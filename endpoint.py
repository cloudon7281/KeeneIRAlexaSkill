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

pp = pprint.PrettyPrinter(indent=2, width = 200)

class Endpoint:
	# This class models an Alexa endpoint

	def __init__(self, endpoint_id, manufacturer):
		self.endpointId = endpoint_id
		self.friendlyName = endpoint_id
		self.Description = "Some blurb"
		self.displayCategories = [ "TV" ]
		self.manufacturerName = manufacturer
		self.capabilities = []

	def add_capability_response(self, capability_response):
		self.capabilities.append(capability_response)
			

def new_endpoint(endpoint_id, manufacturer):	
	endpoint = {}		
	endpoint['endpointId'] = endpoint_id
	endpoint['friendlyName'] = endpoint_id
	endpoint['Description'] = "some blurb"
	endpoint['displayCategories'] = [ "TV" ]
	endpoint['manufacturerName'] = manufacturer
	endpoint['capabilities'] = []

	return endpoint