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

# This file contains a number of utilities related to the Alexa interface.

import logging
import time
import uuid

logger = logging.getLogger()

def extract_token_from_request(request):
    # Find the OAuth2 token from either a discovery or directive request.
    locations = [ 'endpoint', 'payload' ]
    token = None

    for l in locations:
        if l in request['directive']:
            if 'scope' in request['directive'][l]:
                token = request['directive'][l]['scope']['token']

    logger.debug("Token passed in request = %s", token)
    return token

def unpack_request(request):
    # Extract the interface, directive and enpoint ID from a request
    alexa_interface = request["directive"]["header"]["namespace"]

    # Strip off the 'Alexa.' at start of the string
    interface=alexa_interface[6:]
    directive = request["directive"]["header"]["name"]
    payload = request["directive"]["payload"]
    endpoint_id = request["directive"]["endpoint"]["endpointId"]

    return interface, directive, payload, endpoint_id

