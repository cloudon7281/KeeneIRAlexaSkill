# Copyright 2018 Calum Loudon
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not 
# use this file except in compliance with the License. A copy of the License
# is located at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
# CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

# This file takes a definition of a user's devices and from them constructs a
# set of activities.

import logging, pprint

from alexaSchema import CAPABILITY_DISCOVERY_RESPONSES, CAPABILITY_DIRECTIVES_TO_COMMANDS
from deviceDB import DEVICE_DB
from utilities import verify_devices, find_target, get_connected_device, get_repeats, find_user_device_in_DB, find_device_from_friendly_name
from endpoint import new_endpoint

logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=2, width = 200)


def skip_command(verb, command_tuple, device_map, device_state):
	# Determine whether to skip sending a command.
    # We do so if:
    # - the device has toggle rather than on/off      and
    # - this is a TurnOn and the current state is on  or
    skip = False

    if verb == 'SingleIRCommand':
	    device = command_tuple['single']['device']
	    if device_map['toggle']:
	        logger.debug("This is a single command for a device supporting power toggle")
	        if (directive == 'Turn' and DEVICE_STATE[device] == True) or (directive == 'TurnOff' and DEVICE_STATE[device] == False):
	            logger.debug("Already in correct state: skipping")   


def construct_command_sequence(user_devices, root_device, global_database, capability, generic_commands, targets):
	# Construct the sequence of commands for an entire activity corresponding to
	# particular directive of a particular capability.
	# The generic_commands is a dictionary of commands to be interpreted when a
	# directive is received, each consisting of a primitive plus parameters as
	# follows.
	#
	#  SingleIRCommands	- Send a single IR command.  Primitive has a list of 
	#                     command names to search for in each device; use the 
	#					  first match found	for each relevant device
	#  
	#  StepIRCommands   - Directive is of form increase/decrease by N.
	#					  Primitive is a dict with +ve and -ve command lists,
	#                     interpreted as above.
	#
	#  DigitsIRComamnds - Directive is a number to be converted to a sequence
	#                     of IR commands for each decimal digit.  Primitives
	#                     is a dict with list of possible commands for each 
	#					  digit.
	#
	#  InputChoice      - Send IRCommands to set all the devices in the
	#					  activity to the correct input setting.  Typically
	#					  used in "power on".
	#
	#  Pause            - Pause before sending anything further.  Typically
	#  					  used to wait for kit to switch on.  Primitive is
	# 					  length of pause in seconds.
	#
	# We map this to the specific sequence of commands for this users devices
	# by substituting from the global database of devices.
	#
	# Note that we rely on dictionary ordering - not true for Python 2, true 
	# for Python 3.6 onwards.
	#
	# We do this by looping through all the devices in the activity, and for
	# those which support this capability, looking for matches for the set of
	# instructions.
	commands = []

	logger.debug("Converting generic primitives %s to specific commands for capability %s for user chain starting with device %s", pp.pformat(generic_commands), capability, root_device)

	for primitive in generic_commands:
		logger.debug("This primitive is %s", primitive)
		device = root_device
		device_details = find_user_device_in_DB(device, global_database)
		is_audio = ('A_source' in device_details['roles'])
		logger.debug("Is the activity audio only? %d", is_audio)

		if primitive == 'SingleIRCommand' or primitive == 'StepIRCommands' or primitive == 'DigitsIRCommands':
			# We need to loop through the chain of devices, and
			# for each one that supports the capability, search 
			# for the appropriate commands and add them.
			logger.debug("Search for IR commands for this directive; type = %s", primitive)

			while True:
				logger.debug("Check device %s", device['friendly_name'])

				if capability in device_details['supports']:
					logger.debug("Device %s supports the %s capability", device['friendly_name'], capability)

					output_cmd = {}
					output_cmd[primitive]	= {}

					# IRCommands are a flat list of synonyms.  StepIRCommands are two flat lists,
					# one for +ve and one for -ve.  Loop accordingly.
					if primitive == 'SingleIRCommand':
						index = [ 'single' ]
					elif primitive == 'StepIRCommands':
						index = [ '+ve', '-ve' ]
						logger.debug("INSTRUCTION IS %s", primitive)
						logger.debug("StepIRCommmands should check for key %s", generic_commands[primitive]['key'])
						output_cmd[primitive]['key'] = generic_commands[primitive]['key']
					else:
						index = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]

						if 'UseNameMap' in generic_commands[primitive]:
							map = generic_commands[primitive]['UseNameMap']
							logger.debug("This primitive for this directive can accept name map %s", map)
							if map in device_details:
								logger.debug("Map present")
								output_cmd[primitive]['NameMap'] = device_details[map].copy()

					for i in index:	
						if i == 'single':
							command_list = generic_commands[primitive]
						else:
							command_list = generic_commands[primitive][i]

						found = False

						for command in command_list:
							if not found:
								logger.debug("Look for command %s", command)

								if command in device_details['IRcodes']:
									logger.debug("Device %s supports command %s", device['friendly_name'], command)

									# Only want to find one command e.g. PowerOn or PowerToggle
									# We include the device name as we will need that when
									# later figuring out what to turn on/off
									output_cmd[primitive][i] = { 
										'KIRA': device_details['IRcodes'][command], 
										'target': find_target(device, targets),
										'repeats': get_repeats(device_details),
										'device': device['friendly_name']
										}
									found = True
					commands.append(output_cmd)		
				else:
					logger.debug("...doesn't support this capability")			

				if 'connected_to' in device:
					_, device, device_details = get_connected_device(user_devices, global_database, device)
					if is_audio and ('display' in device_details['roles']):
						logger.debug("Connected to a display, but audio only source")
						break
				else:
					break

		elif primitive == 'InputChoice':
			# At this point we have to add commands to set all
			# the devices in the chain to the correct input
			# values.
			logger.debug("Need to add commands to set up inputs appropriately")
			while True:
				if 'connected_to' in device:
					next_input = device['connected_to']['input']
					next_device_name, device, device_details = get_connected_device(user_devices, global_database, device)
					if is_audio and ('display' in device_details['roles']):
						logger.debug("Connected to a display, but audio only source")
						break

					logger.debug("Need to set %s to input %s", next_device_name, next_input)

					command = {
						'SingleIRCommand': {
							'single': {
								'KIRA': device_details['IRcodes'][next_input], 
								'target': find_target(device, targets),
								'repeats': get_repeats(device_details)
							}
						}
					}

					commands.append(command)
				else:
					break

		elif primitive == 'Pause':
			# This is an additional pause, typically to wait
			# for kit to switch on
			pause = generic_commands[primitive]
			logger.debug("Add an additional pause of %d", pause)
			commands.append({'Pause': pause})

	logger.debug("Commands for this directive:\n%s", pp.pformat(commands))		
	return commands		


def find_capabilities(user_devices, root_device, global_database):
	# Identify the set of capabilities supported for a particular activity. 
	# This is the union of all capabilities supported by the devices we are 
	# aggregating to form this endpoint.

	logger.debug("Find the set of capabilities for the activity rooted in %s", root_device['friendly_name'])
	
	capabilities = {}
	device_list = []
	
	device = root_device
	device_details = find_user_device_in_DB(device, global_database)
	is_audio = ('A_source' in device_details['roles'])
	logger.debug("Is the activity audio only? %d", is_audio)

	device_list.append(root_device['friendly_name'])
		
	while True:
		device_list
		for capability in device_details['supports']:
			logger.debug("Activity supports %s capability via device %s", capability, device['friendly_name'])
			capabilities[capability] = 'supported'

		if 'connected_to' in device:
			device_friendly_name, device, device_details = get_connected_device(user_devices, global_database, device)


			if is_audio and ('display' in device_details['roles']):
				logger.debug("Connected to a display, but audio only source")
				break
			else:
				device_list.append(device_friendly_name)
		else:
			logger.debug("Reached end of activity chain")
			break			

	logger.debug("List of capabilities for this activity:\n%s", pp.pformat(capabilities))
	logger.debug("Devices invovled in this activity:\n%s", pp.pformat(device_list))
	return capabilities, device_list


def get_power_toggle(user_devices, global_database):
	# We need to understand (a) which devices are active in which endpoints and
	# (b) whether they have sensible PowerOn/Off commands or just support the 
	# useless PowerToggle (why?) which can result in us getting out of sync.
	# We will later combine this with the current device status to ensure that
	# we (a) turn off now-unused devices when switching between endpoints and
	# (b) get the power polarity correct.
	# device_power_map is a dict with form
	# { 'device': {
	#      'toggle': 'True/False',          # Is PowerToggle used?
	#      'endpoints': {
	#          '<endpoint>' : 'True/False', # Is device used in this endpoint?
	#       }
	#    }
	# }
	#
	# We fill in the power toggle status here; endpoints are added as we find
	# the capabilities.
	device_power_map = {}

	for this_device in user_devices:
		logger.debug("User has device %s", this_device['friendly_name'])	

		device_power_map[this_device['friendly_name']] = {}
		this_device_map = device_power_map[this_device['friendly_name']]
		this_device_map['endpoints'] = {}

		device_details = find_user_device_in_DB(this_device, global_database)

		# Does it use PowerToggle?
		if 'PowerToggle' in device_details['IRcodes']:
			logger.debug("Uses PowerToggle")
			this_device_map['toggle'] = True
		else:
			logger.debug("Does not use PowerToggle")
			this_device_map['toggle'] = False

	return device_power_map

def model_user(user_details):
	# We construct both the definition of the endpoints (= activities)
	# auto-generated from the list of user devices and how they are connected
	# to each other, plus the instruction of commands to send for each primitive
	# on each supported .
	logger.info("Auto-generating list of endpoints and acitvity responses")

	user_targets = user_details['targets']
	user_devices = user_details['devices']

	# xxx in future we may get the global database from S3, but for now use the static file
	global_database = DEVICE_DB

	verify_devices(user_devices, global_database)

	discovery_response = []
	command_sequences = {}
	device_power_map = get_power_toggle(user_devices, global_database)

	for this_device in user_devices:
		logger.debug("User has device %s", this_device['friendly_name'])	

		device_details = find_user_device_in_DB(this_device, global_database)

		is_video_source = ('AV_source' in device_details['roles'])
		is_audio_source = ('A_source' in device_details['roles'])
		is_source = (is_video_source or is_audio_source)

		if is_source:
			logger.debug("It's a source; map it to an endpoint")

			# The Alexa data model looks like this.
			#
			# Endpoints are things like TV or Blu-ray.  In Alexa terms they are
			# usually 1-1 with physical devices, but here we aggregate multiple
			# physical devices into a single endpoint so that they can all be
			# controlled simultaneously.  So our model is that any devices 
			# which the user has which are audio or audio+video sources are
			# mapped to an endpoint.
			#
			# Capabilities are groups of related features such as a 
			# ChannelController or PowerController.  We model each physical
			# device as supporting a set of capabilities; the capabilities we
			# return for an endpoint is the union of all capabilities supported
			# by the devices being aggregated into that endpoint.
			#
			# Directives are the individual commands within each capability e.g.
			# Play or AdjustVolume.
			
			# XXX endpoint id should be unique
			endpoint_id = this_device['friendly_name']
			manufacturer = this_device['manufacturer']
			endpoint = new_endpoint(endpoint_id, manufacturer)

			# We now need to add the set of capabilities this activity 
			# support, which is the union of all those supported by
			# the chain of connected devices.
			capabilities, device_list = find_capabilities(user_devices, this_device, global_database)

			for device in device_list:
				device_power_map[device]['endpoints'][endpoint_id] = True
			
			# Now go through the capabilities, and as well as constructing the
			# appropriate discovery response construct the set of commands for
			# each primitive.
			command_sequences[endpoint_id] = {}

			for capability in capabilities:
				logger.debug("Add capability %s to endpoint response", capability)

				# Append the response we need to return to the discovery, just
				# confirming what directives we support for each capability. 
				# This is taken direct from the Alexa schema.
				endpoint['capabilities'].append(CAPABILITY_DISCOVERY_RESPONSES[capability])

				# More interestingly, for each directive for each capability
				# supported by this endpoint, we want to construct the set of
				# primitives we must generate.  For example, for the TurnOn
				# directive of the PowerController capability, we will likely 
				# to send a 'power on' or 'power toggle' command for every 
				# device in the endpoint chain.
				command_sequences[endpoint_id][capability] = {}
				directives_to_commands = CAPABILITY_DIRECTIVES_TO_COMMANDS[capability]

				for directive in directives_to_commands:
					generic_commands = directives_to_commands[directive]
					specific_commands = construct_command_sequence(user_devices, this_device, global_database, capability, generic_commands, user_targets)
					command_sequences[endpoint_id][capability][directive] = specific_commands

			# Add the constructed endpoint info to what we return
			discovery_response.append(endpoint)

	logger.debug("Device power map = %s", pp.pformat(device_power_map))

	return discovery_response, command_sequences, device_power_map


