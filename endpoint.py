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

import pprint

from logutilities import log_info, log_debug
from utilities import find_target, get_connected_device, find_user_device_in_DB

pp = pprint.PrettyPrinter(indent=2, width = 200)

def new_endpoint(endpoint_id, manufacturer):	
	endpoint = {}		
	endpoint['endpointId'] = endpoint_id
	endpoint['friendlyName'] = endpoint_id
	endpoint['description'] = "some blurb"
	endpoint['displayCategories'] = [ "TV" ]
	endpoint['manufacturerName'] = manufacturer
	endpoint['capabilities'] = []
	endpoint['cookie'] = {}

	return endpoint

def construct_endpoint_chain(user_details, root_device, global_database):
	# Identify the chain of devices included in an endpoint chain plus the set of
	# capabilities it supports.
	# This is the union of all capabilities supported by the devices we are 
	# aggregating to form this endpoint.
	user_targets = user_details['targets']
	user_devices = user_details['devices']

	log_debug("Find the set of capabilities for the activity rooted in %s", root_device['friendly_name'])

	endpoint = new_endpoint(root_device['friendly_name'].replace(" ",""), root_device['manufacturer'])

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
						"log_name": device['manufacturer'] + " " + device['model'],
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
	return endpoint, capabilities, chain
