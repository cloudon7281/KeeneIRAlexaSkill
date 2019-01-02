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

import pprint

from logutilities import log_info, log_debug
from alexaSchema import CAPABILITY_DISCOVERY_RESPONSES, CAPABILITY_DIRECTIVES_TO_COMMANDS
from utilities import verify_devices, find_target, get_connected_device, get_repeats, find_user_device_in_DB, find_device_from_friendly_name
from endpoint import new_endpoint

pp = pprint.PrettyPrinter(indent=2, width = 200)


def construct_command_sequence(device_chain, capability, generic_commands):
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

	log_debug("Converting generic primitives %s to specific commands for capability %s for device chain %s", pp.pformat(generic_commands), capability, pp.pformat(device_chain))

	for primitive in generic_commands:
		log_debug("This primitive is %s", primitive)

		for link in device_chain:
			device = link['friendly_name']
			device_details = link['details']
			target = link['target']
			
			log_debug("Check device %s", device)

			if primitive == 'SingleIRCommand' or primitive == 'StepIRCommands' or primitive == 'DigitsIRCommands':
				# We need to loop through the chain of devices, and
				# for each one that supports the capability, search 
				# for the appropriate commands and add them.
				log_debug("Search for IR commands primitive %s", primitive)

				# Cope with the 'fake' DevicePowerController capability
				if capability == "DevicePowerController":
					cap_to_check = "PowerController"
				else:
					cap_to_check = capability

				if cap_to_check in device_details['supports']:
					log_debug("Device %s supports the %s capability", device, capability)

					output_cmd = {}
					output_cmd[primitive]	= {}

					# IRCommands are a flat list of synonyms.  StepIRCommands are two flat lists,
					# one for +ve and one for -ve.  Loop accordingly.
					if primitive == 'SingleIRCommand':
						index = [ 'single' ]
					elif primitive == 'StepIRCommands':
						index = [ '+ve', '-ve' ]
						log_debug("StepIRCommmands should check for key %s", generic_commands[primitive]['key'])
						output_cmd[primitive]['key'] = generic_commands[primitive]['key']
					else:
						index = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]

						if 'UseNameMap' in generic_commands[primitive]:
							map = generic_commands[primitive]['UseNameMap']
							log_debug("This primitive for this directive can accept name map %s", map)
							if map in device_details:
								log_debug("Map present")
								output_cmd[primitive]['NameMap'] = device_details[map].copy()

					for i in index:	
						if i == 'single':
							command_list = generic_commands[primitive]
						else:
							command_list = generic_commands[primitive][i]

						found = False

						for command in command_list:
							if not found:
								log_debug("Look for command %s", command)

								if command in device_details['IRcodes']:
									log_debug("Device %s supports command %s", device, command)

									# Only want to find one command e.g. PowerOn or PowerToggle
									# We include the device name as we will need that when
									# later figuring out what to turn on/off
									output_cmd[primitive][i] = { 
										'KIRA': device_details['IRcodes'][command], 
										'target': target,
										'repeats': get_repeats(device_details),
										'device': device
										}
									found = True
					commands.append(output_cmd)		
				else:
					log_debug("...doesn't support this capability")			

			elif primitive == 'InputChoice':
				# At this point we have to add commands to set all
				# the devices in the chain to the correct input
				# values.
				if 'required_input' in link:
					log_debug("Need to set %s to input %s", device, link['required_input'])
					log_debug("device_details: %s", pp.pformat(device_details['IRcodes']))

					command = {
						'SingleIRCommand': {
							'single': {
								'KIRA': device_details['IRcodes'][link['required_input']], 
								'target': target,
								'repeats': get_repeats(device_details),
								'device': device
							}
						}
					}

					commands.append(command)

			elif primitive == 'Pause':
				# This is an additional pause, typically to wait
				# for kit to switch on
				pause = generic_commands[primitive]
				log_debug("Add an additional pause of %d", pause)
				commands.append({'Pause': pause})

	log_debug("Commands for this directive:\n%s", pp.pformat(commands))		
	return commands		


def find_endpoint_chain_and_caps(user_details, root_device, global_database):
	# Identify the chain of devices included in an endpoint chain plus the set of
	# capabilities it supports.
	# This is the union of all capabilities supported by the devices we are 
	# aggregating to form this endpoint.

	log_debug("Find the set of capabilities for the activity rooted in %s", root_device['friendly_name'])
	
	user_targets = user_details['targets']
	user_devices = user_details['devices']

	capabilities = {}
	chain = []
	
	device = root_device
	device_details = find_user_device_in_DB(device, global_database)
	is_audio = ('A_source' in device_details['roles'])
	log_debug("Is the activity audio only? %d", is_audio)

	reached_end = False
	required_input = None

	while not reached_end:
		for capability in device_details['supports']:
			log_debug("Activity supports %s capability via device %s", capability, device['friendly_name'])
			capabilities[capability] = 'supported'

		this_link = {
						"friendly_name": device['friendly_name'],
						"details": device_details,
						"target": find_target(device, user_targets)
					}

		if required_input != None:
			this_link['required_input'] = required_input	

		if 'connected_to' in device:
			old_device = device
			device_friendly_name, device, device_details = get_connected_device(user_devices, global_database, device)
			if is_audio and ('display' in device_details['roles']):
				log_debug("Connected to a display, but audio only source - end of chain")
				reached_end = True
			else:
				required_input = old_device['connected_to']['input']
		else:
			reached_end = True
			log_debug("Reached end of activity chain")

		chain.append(this_link)

	log_debug("List of capabilities for this activity:\n%s", pp.pformat(capabilities))
	log_debug("Device chain involved in this activity:\n%s", pp.pformat(chain))
	return capabilities, chain


def get_power_map(user_details, global_database):
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
	#       },
	#      'commands': {}                   # Set of commands corresponding to
	#                                         power on/off/toggle
	#    }
	# }
	#
	# We fill in the power toggle status here; endpoints are added as we find
	# the capabilities.
	log_debug("Construct device power map")

	user_targets = user_details['targets']
	user_devices = user_details['devices']

	device_power_map = {}

	for this_device in user_devices:
		log_debug("Examine device %s", this_device['friendly_name'])	

		device_power_map[this_device['friendly_name']] = {}
		this_device_map = device_power_map[this_device['friendly_name']]
		this_device_map['endpoints'] = {}

		device_details = find_user_device_in_DB(this_device, global_database)

		# Does it use PowerToggle?
		if 'PowerToggle' in device_details['IRcodes']:
			log_debug("Uses PowerToggle")
			this_device_map['toggle'] = True
		else:
			log_debug("Does not use PowerToggle")
			this_device_map['toggle'] = False

		# Store the set of commands corresponding to the power diorectives.
		this_device_map['commands'] = {}
		chain = [
					{
						"friendly_name": this_device['friendly_name'],
						"details": device_details,
						"target": find_target(this_device, user_targets)
					}
				]

		for directive in CAPABILITY_DIRECTIVES_TO_COMMANDS['DevicePowerController']:
			log_debug("Find specific commands corresponding to %s", directive)
			specific_commands = construct_command_sequence(chain,
														   "DevicePowerController",
														   CAPABILITY_DIRECTIVES_TO_COMMANDS['DevicePowerController'][directive])
			this_device_map['commands'][directive] = specific_commands

	return device_power_map


def model_user(user_details, device_database):
	# Here we model the user's devices and activities.
	# 
	# It is important to understand:
	# - the inputs to this model
	# - the Alexa data model
	# - how we map user devices -> Alexa objects
	# - why we have to treat power differently
	# - the set of models we return from here.
	#
	# Inputs to this model
	# --------------------
	# 
	# There are two inputs to this modelling exercise.
	#
	# 1. A global database of devices.  This is a dict, structured by
	# manufacturer then device, which for each device contains
	# - what real-world roles it can play (e.g. audio source, or audio + video)
	# - which Alexa capabilities it can support (see below)
	# - a map of IR command names -> IR codes.
	# For now, this is hard-coded in deviceDB.py - in future it will be read
	# from S3.
	#
	# 2. A user's details.  This has two key pieces of info.
	# - The set of KIRA targets to send commands to (IP addresses + ports); we
	# support multiple devices per-user).
	# - A list of the user's devices, including what the user wants to call 
	# them and how they are linked together (e.g. what TV input a Blu-ray 
	# player is connected to.
	# For now, this is hard-coded in userDevices.py - in future it will be 
	# read from S3.
	#
	# Alexa data model
	# ----------------
	# 
	# The key Alexa concepts are endpoints, capabilities and directives.
	#
	# Endpoints are things like TV or Blu-ray.
	# 
	# Capabilities (aka interfaces) are groups of related features such as a 
	# ChannelController or PowerController.  We model each physical
	# device as supporting a set of capabilities; the capabilities we
	# return for an endpoint is the union of all capabilities supported
	# by the devices being aggregated into that endpoint.
	#
	# Directives are the individual commands within each capability e.g.
	# Play or AdjustVolume.
	#
	# Mapping user devices -> Alexa data model
	# ----------------------------------------
	#
	# Alexa "expects" endpoints to be 1-1 with physical devices, but instead
	# we aggregate multiple physical devices into a single endpoint so that 
	# they can all be controlled simultaneously.  So our model is that any 
	# devices which the user has which are audio or audio+video sources are
	# mapped to an endpoint, and we then follow the chain of connectivity
	# from those sources to create a list of each device included in that
	# endpoint.
	#
	# We then model the capabilities supported by the endpoint as being the 
	# union of the capabilities supported by each device included in the 
	# endpoint.
	#
	# For each directive of each capability, we then create a list of the 
	# specific commands we must send to implement that directive on each of
	# the devices supporting that capability (typically, there will only be
	# one device in the chain doing so e.g. only one device supporting 
	# StepSpeaker for volume control).  We do this via a dict representing the
	# Alexa schema; for each directive of each capability it has a list of
	# command names to search for in the device database for the appropriate
	# devices e.g. for the AdjustVolume directive of the StepSpeaker capability
	# we search for commands called VolumeUp and VolumeDown.
	#
	# The commands we extract may be simple unconditional "send this IR seq"
	# commands, or more complex commands that are parameterised by values
	# in the directive e.g. the ChangeChannel directive of the
	# ChannelController capability extracts the IR sequences corresponding to 
	# digits 0-9; the value channel passed in the payload of the directive
	# then determines which IR sequences are sent.
	#
	# Why power is different
	# ----------------------
	#
	# The scheme outlined above works well for everything apart from power
	# commands, for two reasons.
	#
	# - We potentially have to send commands to devices *not* in the endpoint
	# the user command nominally addresses. For example, if the user issues
	# "Turn on TV" then "Turn on CD", then (assuming the CD is being played
	# back through speakers not the TV) we should turn off the TV as part of
	# handling the latter command.  That means we have to have awareness of
	# the power state of all devices.
	#
	# - Some evil device manufacturers just support a "power toggle" IR command
	# rather than separate "power on" and "power off".  This makes awareness
	# of state essential, as the commands are not idempotent e.g. if we simply
	# mapped "Turn on TV" to sending "power toggle" to the TV, then if the user
	# issued successive "Turn on TV" commands, the second one would turn *off*
	# the TV.
	#
	# Models
	# ------
	#
	# Given the above, we model and return the following.
	#
	# discovery_response
	#
	# This is a dict corresponding to the JSON structure to return to Alexa in
	# response to Discovery commands, and includes the full set of endpoints 
	# and their supported capabilities.
	#
	# command_sequence
	#
	# This is a dict indexed by endpoint then capability then directive, 
	# containing a structure corresponding to the set of IR commands to send
	# for that directive of that capability for that endpoint.  The lambda 
	# handler then simply sends that sequence of IR commands, parameterised as
	# necessary by values in the directive payload.
	#
	# device_power_map
	#
	# This is a dict indexed by device which includes info on
	# - which endpoints the device participates in
	# - whether it is a "toggle" or "on/off" device
	# - the set of IR commands corresponding to power toggle/on/off commands.
	# The lambda handler then uses this whenever it receives a directive for
	# the PowerController capability.  In conjunction with the device state,
	# it works out which devices need to be turned off.  Power manipulation
	# (and associated setting of inputs) for devices in the endpoint is handled
	# by the normal command sequence processing.
	log_info("Auto-generating model")

	# Extract the lists of targets and devices from the user details, and check
	# they're not duff.
	user_targets = user_details['targets']
	user_devices = user_details['devices']
	verify_devices(user_devices, device_database)
	
	discovery_response = []
	command_sequences = {}
	
	# We can't construct the full power map until we have the list of endpoints
	# but we can extract whether each device is a toggle or on/off plus the 
	# list of its IR commands.
	device_power_map = get_power_map(user_details, device_database)
	
	# Now construct the list of endpoints, and use to flesh out the discovery
	# response, command sequence and power map.
	for this_device in user_devices:
		log_debug("User has device %s", this_device['friendly_name'])	

		device_details = find_user_device_in_DB(this_device, device_database)

		is_video_source = ('AV_source' in device_details['roles'])
		is_audio_source = ('A_source' in device_details['roles'])
		is_source = (is_video_source or is_audio_source)

		if is_source:
			log_debug("It's a source; map it to an endpoint")

			# The discovery response includes a section on each endpoint.
			# Start building that up.
			# XXX endpoint id should be unique
			endpoint_id = this_device['friendly_name']
			manufacturer = this_device['manufacturer']
			endpoint = new_endpoint(endpoint_id, manufacturer)

			# We now need to find the chain of devices in this endpoint chain, 
			# plus the union of their capabilities.
			capabilities, chain = find_endpoint_chain_and_caps(user_details, this_device, device_database)

			for link in chain:
				device_power_map[link['friendly_name']]['endpoints'][endpoint_id] = True
			
			# Now go through the capabilities, and as well as constructing the
			# appropriate discovery response construct the set of commands for
			# each primitive.
			command_sequences[endpoint_id] = {}

			for capability in capabilities:
				log_debug("Add capability %s to endpoint response", capability)

				# Append the section of the discovery response for this
				# capability for this endpoint.  This is the set of directives
				# we support for this capability, and is taken direct from the
				# Alexa schema.
				endpoint['capabilities'].append(CAPABILITY_DISCOVERY_RESPONSES[capability])

				# Now construct the set of IR commands for each directive of
				# this capability.
				# The schema includes the set of command names to look for,
				# for each directive of each capability.
				command_sequences[endpoint_id][capability] = {}
				directives_to_commands = CAPABILITY_DIRECTIVES_TO_COMMANDS[capability]

				for directive in directives_to_commands:
					specific_commands = construct_command_sequence(chain,
																   capability,
																   directives_to_commands[directive])
					command_sequences[endpoint_id][capability][directive] = specific_commands

			# Add the constructed endpoint info to what we return
			discovery_response.append(endpoint)

	log_debug("Device power map = %s", pp.pformat(device_power_map))

	model = {
				'discovery_response': discovery_response,
				'command_sequences': command_sequences,
				'device_power_map': device_power_map
			}

	return model


