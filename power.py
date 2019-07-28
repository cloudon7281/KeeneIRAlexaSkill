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
from alexaSchema import CAPABILITY_DIRECTIVES_TO_COMMANDS
from utilities import find_target, find_user_device_in_DB
from command_sequences import construct_command_sequence

pp = pprint.PrettyPrinter(indent=2, width = 200)


def construct_power_map(user_details, global_database):
	# We need to understand (a) which devices are active in which endpoints and
	# (b) whether they have sensible PowerOn/Off commands or just support the 
	# useless PowerToggle (why?) which can result in us getting out of sync.
	# We will later combine this with the current device status to ensure that
	# we (a) turn off now-unused devices when switching between endpoints and
	# (b) get the power polarity correct.
	# device_power_map is a dict with form
	# { 'device': {
	#      'room': <room>, 					# which room this device is
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
		friendly_name = this_device['friendly_name']
		log_debug("Examine device %s", friendly_name)	

		device_power_map[friendly_name] = {}
		this_device_map = device_power_map[friendly_name]
		this_device_map['room'] = this_device['room']
		this_device_map['endpoints'] = {}

		device_details = find_user_device_in_DB(this_device, global_database)

		# Does it use PowerToggle?
		if 'PowerToggle' in device_details['IRcodes']:
			log_debug("Uses PowerToggle")
			this_device_map['toggle'] = True
		else:
			log_debug("Does not use PowerToggle")
			this_device_map['toggle'] = False

		# Store the set of commands corresponding to the power directives.
		this_device_map['commands'] = {}
		chain = [
					{
						"friendly_name": this_device['friendly_name'],
						"log_name": this_device['manufacturer'] + " " + this_device['model'],
						"details": device_details,
						"target": find_target(this_device, user_targets)
					}
				]

		power_directives = CAPABILITY_DIRECTIVES_TO_COMMANDS['DevicePowerController']

		for directive in power_directives:
			log_debug("Find specific commands corresponding to %s", directive)
			specific_commands = construct_command_sequence(chain,
														   "DevicePowerController",
														   power_directives[directive])
			this_device_map['commands'][directive] = specific_commands

	return device_power_map