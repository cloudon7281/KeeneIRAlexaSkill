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

import logging, pprint

from AWSutilities import unpack_request
from alexaSchema import DIRECTIVE_RESPONSE, CAPABILITY_DIRECTIVE_PROPERTIES_RESPONSES
from utilities import get_uuid, get_utc_timestamp

logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=2, width = 200)

def construct_response(request):
	# Construct the appropriate response to the received request.
	#
    # This should be data driven, but for now do in code, because frankly
    # the API is all over the place here.
    interface, directive, endpoint_id = unpack_request(request)

    response = DIRECTIVE_RESPONSE

    prop = CAPABILITY_DIRECTIVE_PROPERTIES_RESPONSES[interface]
    prop['timeOfSample'] = get_utc_timestamp()

    # Depending on the interface/directive, need to construct an appropriate
    # value field. 
    if interface == 'PowerController':
        if directive == 'TurnOn':
            prop['value'] = "ON"
        else:
            prop['value'] = "OFF"
    elif interface == 'ChannelController':
        if directive == 'ChangeChannel':
            prop['value'] = request['directive']['payload']['channel']
    elif interface == 'StepSpeaker':
        prop = {}
    elif interface == 'PlaybackController':
        prop = {}

    if prop == {}:
        response['context']['properties'] = [ ]
    else:
        response['context']['properties'] = [ prop ]
    
    response['event']['header']['messageId'] = get_uuid()
    response['event']['header']['correlationToken'] = request['directive']['header']['correlationToken']
    response['event']['endpoint'] = request['directive']['endpoint']

    return response
