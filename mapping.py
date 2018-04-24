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

from alexaSchema import CAPABILITY_DISCOVERY_RESPONSES, CAPABILITY_DIRECTIVES
from utilities import verify_devices, find_target, get_connected_device, get_repeats, find_user_device_in_DB, find_device_from_friendly_name
from endpoint import new_endpoint

logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=2, width = 200)


def find_capabilities(user_devices, root_device, global_database, is_audio):
	# Identify the set of capabilities supported for a particular activity
	logger.debug("Find the set of capabilities for the activity rooted in %s", root_device['friendly_name'])
	logger.debug("Is the activity audio only? %d", is_audio)
	capabilities = {}
	device = root_device
	device_details = find_user_device_in_DB(device, global_database)

	while True:
		for capability in device_details['supports']:
			logger.debug("Activity supports %s capability via device %s", capability, device['friendly_name'])
			capabilities[capability] = 'supported'

		if 'connected_to' in device:
			_, device, device_details = get_connected_device(user_devices, global_database, device)
			if is_audio and ('display' in device_details['roles']):
				logger.debug("Connected to a display, but audio only source")
				break
		else:
			logger.debug("Reached end of activity chain")
			break			

	logger.debug("List of capabilities for this activity:\n%s", pp.pformat(capabilities))
	return capabilities


def construct_command_sequence(user_devices, root_device, global_database, capability, directive, instructions, targets, is_audio):
	# Construct the sequence of commands for an entire activity corresponding to
	# particular directive of a particular capability.
	# The instructions are a dictionary of commands to be interpreted when a
	# directive is received, as follows.
	#
	#  SingleIRCommands	- Send a single IR command.  Instruction has a list of 
	#                     command names to search for in each device; use the 
	#					  first match found	for each relevant device
	#  
	#  StepIRCommands   - Directive is of form increase/decrease by N.
	#					  Instruction is a dict with +ve and -ve command lists,
	#                     interpreted as above.
	#
	#  DigitsIRComamnds - Directive is a number to be converted to a sequence
	#                     of IR commands for each deimal digit.  Instructions
	#                     is a dict with list of possible commands for each 
	#					  digit.
	#
	#  InputChoice      - Send IRCommands to set all the devices in the
	#					  activity to the correct input setting.  Typically
	#					  used in "power on".
	#
	#  Pause            - Pause before sending anything further.  Typically
	#  					  used to wait for kit to switch on.  Instruction is
	# 					  length of pause in seconds.
	#
	# The output commands are a list of dicts of the same form as above.
	#
	# Note that we rely on dictionary ordering - not true for Python 2, true 
	# for Python 3.6 onwards.
	#
	# We do this by looping through all the devices in the activity, and for
	# those which support this capability, looking for matches for the set of
	# instructions.
	commands = []

	logger.debug("Finding set of commands for capability %s, directive %s for all relevant devices", capability, directive)
	logger.debug("Is the activity audio only? %d", is_audio)

	for instruction in instructions:
		logger.debug("This instruction is %s", instruction)
		device = root_device
		device_details = find_user_device_in_DB(device, global_database)

		if instruction == 'SingleIRCommand' or instruction == 'StepIRCommands' or instruction == 'DigitsIRCommands':
			# We need to loop through the chain of devices, and
			# for each one that supports the capability, search 
			# for the appropriate commands and add them.
			logger.debug("Search for IR commands for this directive; type = %s", instruction)

			while True:
				logger.debug("Check device %s", device['friendly_name'])

				if capability in device_details['supports']:
					logger.debug("Device %s supports the %s capability", device['friendly_name'], capability)

					# IRCommands are a flat list of synonyms.  StepIRCommands are two flat lists,
					# one for +ve and one for -ve.  Loop accordingly.
					if instruction == 'SingleIRCommand':
						index = [ 'single' ]
					elif instruction == 'StepIRCommands':
						index = [ '+ve', '-ve' ]
					else:
						index = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]

					output_cmd = {}
					output_cmd[instruction]	= {}

					for i in index:	
						if i == 'single':
							command_list = instructions[instruction]
						else:
							command_list = instructions[instruction][i]

						found = False

						for command in command_list:
							if not found:
								logger.debug("Look for command %s", command)

								if command in device_details['IRcodes']:
									logger.debug("Device %s supports command %s", device['friendly_name'], command)

									# Only want to find one command e.g. PowerOn or PowerToggle
									output_cmd[instruction][i] = { 
										'KIRA': device_details['IRcodes'][command], 
										'target': find_target(device, targets),
										'repeats': get_repeats(device_details)
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

		elif instruction == 'InputChoice':
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

		elif instruction == 'Pause':
			# This is an additional pause, typically to wait
			# for kit to switch on
			pause = instructions[instruction]
			logger.debug("Add an additional pause of %d", pause)
			commands.append({'Pause': pause})

	logger.debug("Commands for this directive:\n%s", pp.pformat(commands))		
	return commands		

def map_user_devices(user_devices, global_database):
	# We construct both the definition of the endpoints (= activities)
	# auto-generated from the list of user devices and how they are connected
	# to each other, plus the instruction of commands to send for each primitive
	# on each supported .
	logger.info("Auto-generating list of endpoints and acitvity responses")
	verify_devices(user_devices['devices'], global_database)

	endpoints = []
	directive_responses = {}

	# Get the list of targets associated with this user
	targets = user_devices['targets']
	devices = user_devices['devices']

	for device in devices:
		logger.debug("User has device %s", device['friendly_name'])	

		device_details = find_user_device_in_DB(device, global_database)

		is_video_source = ('AV_source' in device_details['roles'])
		is_audio_source = ('A_source' in device_details['roles'])
		is_source = (is_video_source or is_audio_source)

		if is_source:
			logger.debug("It's a source; map it to an endpoint")
			
			# XXX endpoint id should be unique
			endpoint_id = device['friendly_name']
			manufacturer = device['manufacturer']
			endpoint = new_endpoint(endpoint_id, manufacturer)

			# We now need to add the set of capabilities this activity 
			# support, which is the union of all those supported by
			# the chain of connected devices.
			capabilities = find_capabilities(devices, device, global_database, is_audio_source)
			
			# Now go through the capabilities, and as well as constructing the
			# appropriate discovery response construct the set of commands for
			# each primitive.
			directive_responses[endpoint_id] = {}

			for capability in capabilities:
				logger.debug("Add capability %s to endpoint response", capability)

				endpoint['capabilities'].append(CAPABILITY_DISCOVERY_RESPONSES[capability])
				directive_responses[endpoint_id][capability] = {}

				# For each capability we look at the primitives it supports and 
				# construct them from each device.
				directives = CAPABILITY_DIRECTIVES[capability]

				for directive in directives:
					commands = construct_command_sequence(devices, device, global_database, capability, directive, directives[directive], targets, is_audio_source)
					directive_responses[endpoint_id][capability][directive] = commands

			# Add the constructed endpoint info to what we return
			endpoints.append(endpoint)

	return endpoints, directive_responses


