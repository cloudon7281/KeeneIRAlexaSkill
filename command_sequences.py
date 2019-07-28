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
from utilities import get_repeats

pp = pprint.PrettyPrinter(indent=2, width = 200)


def which_capability(capability):
	# Cope with the 'fake' DevicePowerController capability
	if capability == "DevicePowerController":
		cap_to_check = "PowerController"
	else:
		cap_to_check = capability

	return cap_to_check


def construct_specific_IR_command(device_details, command, target, device_name, device_logname):
	output_cmd = { 
		'KIRA': device_details['IRcodes'][command], 
		'target': target,
		'repeats': get_repeats(device_details),
		'device': device_name,
		'log': "Send " + command + " to " + device_logname + " (" + device_name + ")"
		}

	return output_cmd


def SingleIRCommand(device, capability, command_list):
	log_debug("Have list of single IR commands to check: %s", pp.pformat(command_list))
	cap_to_check = which_capability(capability)
	log_debug("Checking for capability %s", capability)

	device_name = device['friendly_name']
	device_logname = device['log_name']
	device_details = device['details']
	target = device['target']

	output_cmd = {}

	log_debug("Checking device details: %s", pp.pformat(device_details))

	if cap_to_check in device_details['supports']:
		log_debug("Device %s supports the %s capability", device_name, capability)

		output_cmd['SingleIRCommand'] = {}

		found = False

		for command in command_list:
			if not found:
				log_debug("Look for command %s", command)

				if command in device_details['IRcodes']:
					log_debug("Device %s supports command %s", device_name, command)

					# Only want to find one command e.g. PowerOn or PowerToggle
					# We include the device name as we will need that when
					# later figuring out what to turn on/off
					output_cmd['SingleIRCommand']['single'] = construct_specific_IR_command(device_details, command, target, device_name, device_logname)
					found = True
				else:
					log_debug("...doesn't support this capability")			

	return output_cmd

def StepIRCommands(device, capability, command_list):
	cap_to_check = which_capability(capability)

	device_name = device['friendly_name']
	device_logname = device['log_name']
	device_details = device['details']
	target = device['target']

	output_cmd = {}

	if cap_to_check in device_details['supports']:
		log_debug("Device %s supports the %s capability", device_name, capability)

		output_cmd['StepIRCommands'] = {}

		found = False

		log_debug("StepIRCommands should check for key %s", command_list['key'])
		output_cmd['StepIRCommands']['key'] = command_list['key']

		for i in [ '+ve', '-ve' ]:	
			found = False

			for command in command_list[i]:
				if not found:
					log_debug("Look for command %s", command)

					if command in device_details['IRcodes']:
						log_debug("Device %s supports command %s", device_name, command)

						# Only want to find one command e.g. PowerOn or PowerToggle
						# We include the device name as we will need that when
						# later figuring out what to turn on/off
						output_cmd['StepIRCommands'][i] = construct_specific_IR_command(device_details, command, target, device_name, device_logname)
						found = True
				else:
					log_debug("...doesn't support this capability")			

	return output_cmd

def DigitsIRCommands(device, capability, command_list):
	cap_to_check = which_capability(capability)

	device_name = device['friendly_name']
	device_logname = device['log_name']
	device_details = device['details']
	target = device['target']

	output_cmd = {}

	if cap_to_check in device_details['supports']:
		log_debug("Device %s supports the %s capability", device_name, capability)

		output_cmd['DigitsIRCommands'] = {}

		if 'UseNameMap' in command_list:
			map = command_list['UseNameMap']
			log_debug("DigitsIRCommand for this directive can accept name map %s", map)
			if map in device_details:
				log_debug("Map present")
				output_cmd['DigitsIRCommands']['NameMap'] = device_details[map].copy()

		for i in [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]:	
			found = False

			for command in command_list[i]:
				if not found:
					log_debug("Look for command %s", command)

					if command in device_details['IRcodes']:
						log_debug("Device %s supports command %s", device_name, command)

						# Only want to find one command e.g. PowerOn or PowerToggle
						# We include the device name as we will need that when
						# later figuring out what to turn on/off
						output_cmd['DigitsIRCommands'][i] = construct_specific_IR_command(device_details, command, target, device_name, device_logname)
						found = True
				else:
					log_debug("...doesn't support this capability")			

	return output_cmd


def InputChoice(device, capability, command_list):
	device_name = device['friendly_name']
	device_logname = device['log_name']
	device_details = device['details']
	target = device['target']

	output_cmd = {}
	
	# Add commands to set all the devices in the chain to the correct input
	# values.
	if 'required_input' in device:
		log_debug("Need to set %s to input %s", device_name, device['required_input'])
		log_debug("device_details: %s", pp.pformat(device_details['IRcodes']))

		output_cmd['SingleIRCommand'] = {}
		output_cmd['SingleIRCommand']['single'] = construct_specific_IR_command(device_details, device['required_input'], target, device_name, device_logname)

	return output_cmd


def Pause(device, capability, pause):
	# This is an additional pause, typically to wait for kit to switch on
	output_cmd = { 'Pause': pause }

	return output_cmd


def construct_command_sequence(device_chain, capability, generic_commands):
	# Construct the sequence of commands corresponding to a particular
	# directive of a particular capability, for example "Play" for a 
	# "PlaybackController".
	#
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
			device_logname = link['log_name']
			device_details = link['details']
			target = link['target']
			
			log_debug("Check device %s", device)

			commands.append(globals()[primitive](link, capability, generic_commands[primitive]))

	log_debug("Commands for this directive:\n%s", pp.pformat(commands))		

	return commands		
