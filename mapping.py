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

from deviceDB import DEVICE_DB
from alexaSchema import CAPABILITY_DISCOVERY_RESPONSES, CAPABILITY_DIRECTIVES
from utilities import verify_devices, find_user_device_in_DB, find_device_from_friendly_name

logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=2, width = 200)


def find_capabilities(devices, root_device):
	# Identify the set of capabilities supported for a particular activity
	logger.info("Find the set of capabilities for the activity rooted in %s", root_device['friendly_name'])
	capabilities = {}
	device = root_device

	while True:
		device_details = find_user_device_in_DB(device)
		
		for interface in device_details['supports']:
			logger.info("Activity supports %s interface via device %s", interface, device['friendly_name'])
			capabilities[interface] = 'supported'

		if 'connected_to' in device:
			next_device = device['connected_to']['next_device']
			logger.info("Next device in activity is %s", next_device)

			device = find_device_from_friendly_name(devices, next_device)
		else:
			logger.info("Reached end of activity chain")
			break			

	logger.debug("List of capabilities for this activity:\n%s", pp.pformat(capabilities))
	return capabilities


def construct_command_sequence(devices, root_device, interface, instructions):
	# Construct the sequence of commands for an entire activity corrsponding to
	# particular directive of a particular interface.
	# The instructions are a dictionary of commands to be interpreted when a
	# directive is receivec, as follows.
	#
	#  SingleIRCommands	- Send a single IR command.  Instruction has a list of 
	#                     command names to search for in each device; use the 
	#					  first match found	
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
	# those which support this interface, looking for matches for the set of
	# instructions.
	commands = []

	for instruction in instructions:
		logger.info("This instruction is %s", instruction)
		device = root_device
		device_details = find_user_device_in_DB(device)

		if instruction == 'SingleIRCommand' or instruction == 'StepIRCommands' or instruction == 'DigitsIRCommands':
			# We need to loop through the chain of devices, and
			# for each one that supports the interface, search 
			# for the appropriate commands and add them.
			#
			# The commands are a dict 
			logger.info("Search for IR commands for this directive; type = %s", instruction)

			while True:
				logger.info("Check device %s", device['friendly_name'])
				if interface in device_details['supports']:
					logger.info("Device %s supports the %s interface", device['friendly_name'], interface)

					# IRCommands are a flat list of synonyms.  StepIRCommands are two flat lists,
					# one fore +ve and one for -ve.  Loop accordingly.
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
								logger.info("Look for command %s", command)

								if command in device_details['IRcodes']:
									logger.info("Device %s supports command %s", device['friendly_name'], command)

									# Only want to find one command e.g. PowerOn or PowerToggle
									output_cmd[instruction][i] = device_details['IRcodes'][command]
									found = True

					commands.append(output_cmd)		
				else:
					logger.info("...doesn't support this interface")			

				if 'connected_to' in device:
					next_device_name = device['connected_to']['next_device']
					logger.info("Next connected device is %s", next_device_name)
					device  = find_device_from_friendly_name(devices, next_device_name)
					device_details = find_user_device_in_DB(device)
					logger.info("Now check %s", next_device_name)
				else:
					break

		elif instruction == 'InputChoice':
			# At this point we have to add commands to set all
			# the devices in the chain to the correct input
			# values.
			logger.info("Need to add commands to set up inputs appropriately")
			while True:
				if 'connected_to' in device:
					next_input = device['connected_to']['input']
					next_device_name = device['connected_to']['next_device']
					device = find_device_from_friendly_name(devices, next_device_name)
					device_details = find_user_device_in_DB(device)

					logger.info("Need to set %s to input %s", next_device_name, next_input)

					commands.append({'SingleIRCommand':{'single': device_details['IRcodes'][next_input]}})
				else:
					break

		elif instruction == 'Pause':
			# This is an additional pause, typically to wait
			# for kit to switch on
			pause = instructions[instruction]
			logger.info("Add an additional pause of %d", pause)
			commands.append({'Pause': pause})

	logger.debug("Commands for this directive:\n%s", pp.pformat(commands))		
	return commands		

def map_user_devices(devices):
	# We construct both the definition of the endpoints (= activities)
	# auto-generated from the list of user devices and how they are connected
	# to each other, plus the instruction of commands to send for each primitive
	# on each supported interface.
	verify_devices(devices)

	user_activities = {}
	user_activities['endpoints'] = []
	user_activities['directive_responses'] = {}

	for device in devices:
		logger.info("User has device %s", device['friendly_name'])	
		
		device_details = find_user_device_in_DB(device)

		if 'AV_source' in device_details['roles']:
			logger.info("It's a source; map it to an endpoint")
			
			# XXX endpoint id should be unique
			endpoint_id = device['friendly_name']

			user_activities['directive_responses'][endpoint_id] = {}

			endpoint = {}
			endpoint['endpointId'] = endpoint_id
			endpoint['friendlyName'] = endpoint_id
			endpoint['Description'] = "some blurb"
			endpoint['displayCategories'] = [ "TV" ]
			endpoint['manufacturerName'] = device['manufacturer']
			endpoint['capabilities'] = []

			# We now need to add the set of capabilities this activity 
			# support, which is the union of all those supported by
			# the chain of connected devices.
			capabilities = find_capabilities(devices, device)
			
			# Now go through the capabilities, and as well as constructing the
			# appropriate discovery response construct the set of commands for
			# each primitive.
			for interface in capabilities:
				logger.info("Add interface %s to endpoint response", interface)

				endpoint['capabilities'].append(CAPABILITY_DISCOVERY_RESPONSES[interface])
				user_activities['directive_responses'][endpoint_id][interface] = {}

				# For each interface we look at the primitives it supports and 
				# construct them from each device.
				directives = CAPABILITY_DIRECTIVES[interface]

				for directive in directives:
					commands = construct_command_sequence(devices, device, interface, directives[directive])
					user_activities['directive_responses'][endpoint_id][interface][directive] = commands

			# Add the constructed endpoint info to what we return
			user_activities['endpoints'].append(endpoint)

	return user_activities


