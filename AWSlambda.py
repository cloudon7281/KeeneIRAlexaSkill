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

# This file implements a lambda to implement the skill.  It supports the SHS
# API, both discvoery and subsequent defines a set of commands and associated
# Keene KIRA IR commands for a range of devices.

import os
import logging
import time
import json
import pprint
import requests

from userDevices import DEVICES
from alexaSchema import DISCOVERY_RESPONSE, DIRECTIVE_RESPONSE, CAPABILITY_DIRECTIVE_PROPERTIES_RESPONSES
from deviceDB import DEVICE_DB

from utilities import verify_static_user, verify_request, get_uuid, get_utc_timestamp, extract_token_from_request
from LWAauth import get_user_from_token
from mapping import map_user_devices
from KIRAIO import SendToKIRA

# Logger boilerplate
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
pp = pprint.PrettyPrinter(indent=2, width = 200)

PORT = 65432
REPEAT = 1
DELAY = 0.04
PAUSE_BETWEEN_COMMANDS = 0.2

def lambda_handler(request, context):
    # Main lambda handler.  We simply switch on the directive type.

    # XXX We should have something at this point that looks at the token in the
    # context and figures out what user it is for.  But I don't know how to do
    # that just yet, so ignore it for now and just assume it's me.
    logger.info("Received request")
    logger.info(json.dumps(request, indent=4))

    if 'TEST_USER' in os.environ:
        # Currently we are testing with a hard-coded user name
        user = os.environ['TEST_USER']
        logger.debug("User name passed as env var = %s", user)
    else:
        # User name must be retrieved from a token, either passed in as an env
        # var or extracted from the real request.
        if 'TEST_TOKEN' in os.environ:
            OAuth2_token = os.environ['TEST_TOKEN']
            logger.debug("Token passed as env var = %s", OAuth2_token)
        else:
            # Real request.  Extract token.
            OAuth2_token = extract_token_from_request(request)
        
        user = get_user_from_token(OAuth2_token)

    logger.info("Request is for user %s", user)
    if request["directive"]["header"]["name"] == "Discover":
        req_is_discovery = True
    else:
        req_is_discovery = False

    # We now need the details of the user's devices (for a discovery request)
    # or their auto-generated activities (for a directive).  
    #
    # If we're using static files, we do this mapping on every request.
    #
    # If we're using S3, then
    # - the user's details (list of devices) is in S3
    # - on discovery, we retrieve this, auto-generate the endpoint list and
    #   set of mappings from directives -> commands, return the endpoint list
    #   to Alexa, and store the mapped activities back into S3 for use on
    #   directives
    # - for directives, we read the mapped activiites from S3.
    if 'USE_STATIC_FILES' in os.environ:
        logger.debug("Using static files - map the user -> endpoints/activities")

        # Check this user is in the static input file.
        verify_static_user(user)

        # Map the user devices to endpoint and discovery information using
        # static files.
        user_activities = map_user_devices(DEVICES[user]['devices'], DEVICE_DB)
        user_activities['directive_responses']['target'] = DEVICES[user]['target']
        user_activities['directive_responses']['port'] = DEVICES[user]['port']

        endpoints = user_activities['endpoints']
        activity_responses = user_activities['directive_responses']
    else:
        # If this is a discovery, we need to read the user's devices object 
        # plus the global device DB from S3, and then write the mapped activity
        # responses back to S3.
        # If this is a directive, we read the activity responses.
        logger.debug("Reading from S3")

    if req_is_discovery:
        response = reply_to_discovery(endpoints)
    else:
        response = handle_non_discovery(request, activity_responses)

    logger.info("Response:")
    logger.info(json.dumps(response, indent=4, sort_keys=True))

    return response

def reply_to_discovery(endpoints):
    # Handle discovery requests.  This is straightforward: we have already 
    # mapped the users set of devices to an auto-generated list of activities
    # (endpoints), so just return them.
    logger.info("Reply to discovery")

    response = DISCOVERY_RESPONSE
    response['event']['payload']['endpoints'] = endpoints
    response['event']['header']['messageId'] = get_uuid()
                    
    return response

def handle_non_discovery(request, activity_responses):
    # We have received a directive for some capability interface, which we have
    # to now act on.
    # The responses structure is a dict telling us what to do.  It is a nested
    # dict with the following structure:
    #
    # { endpoint:
    #     { interface:
    #         { directive:
    #             [ list of commands ]
    #         }
    #     }
    # }
    #
    # where the list of commands is a list of dicts with the following verbs
    # as keys:
    #
    #   SingleIRCommand     - send a single KIRA command; value is struct with 
    #                         IR sequence as value
    #   StepIRCommands      - send N * up/down KIRA commands; value is a struct
    #                         with +ve & -ve IR commands
    #   DigitsIRCommands    - send sequence of KIRA commands corresponding to 
    #                         digits of number in the payload; value is a struct
    #                         with IR commands for each decimal digit
    #   Pause               - pause for N seconds before sending next command;
    #                         time to wait is the value
    alexa_interface = request["directive"]["header"]["namespace"]
    # Strip off the 'Alexa.' at start of the string
    interface=alexa_interface[6:]
    directive = request["directive"]["header"]["name"]
    endpoint_id = request["directive"]["endpoint"]["endpointId"]

    logger.info("Received directive %s on interface %s for endpoint %s", directive, interface, endpoint_id)

    verify_request(activity_responses, endpoint_id, interface, directive)

    commands_list = activity_responses[endpoint_id][interface][directive]
    target = activity_responses['target']
    port = activity_responses['port']

    logger.info("Target is %s\:%d", target, port)
    print("Target is %s\:%d", target, port)
    logger.info("Commands to execute:\n%s", pp.pformat(commands_list))

    for command_tuple in commands_list:
        for verb in command_tuple:
            logger.debug("Verb to run: %s", verb)

            if verb == 'SingleIRCommand':
                # Send to KIRA the single command specified.
                KIRA_string = command_tuple[verb]['single']['KIRA']
                repeats = command_tuple[verb]['single']['repeats']
                SendToKIRA(target, port, KIRA_string, repeats, DELAY)

            elif verb == 'StepIRCommands':
                # In this case we need to extract the value N in the payload
                # then send either the +ve or -ve command N times.
                # XXX need to generalise payload location from AdjustVolume
                steps = request['directive']['payload']['volumeSteps']
                logger.debug("Adjustment to make: %d", steps)

                if steps > 0:
                    KIRA_string = command_tuple[verb]['+ve']['KIRA']
                    repeats = command_tuple[verb]['+ve']['repeats']
                else:
                    KIRA_string = command_tuple[verb]['-ve']['KIRA']
                    repeats = command_tuple[verb]['+ve']['repeats']

                for n in range(0, abs(steps)):
                    SendToKIRA(target, port, KIRA_string, repeats, DELAY)
                    time.sleep(PAUSE_BETWEEN_COMMANDS)

            elif verb == 'DigitsIRCommands':
                # In this case we need to extract a decimal number in the 
                # payload then send the sequence of IR commands corresponding
                # to its digits.
                # XXX need to generalise payload location from ChangeChannel
                payload = request['directive']['payload']
                number = -1
                for key1 in [ 'channel', 'channelMetadata']:
                    if key1 in payload:
                        for key2 in [ 'number', 'name']:
                            if key2 in payload[key1]:
                                number = payload[key1][key2]

                if number == -1:
                    logger.error("Can't extract channel number from directive!")
                else:
                    logger.debug("Number to send: %s", number)

                    for digit in number:
                        KIRA_string = command_tuple[verb][digit]['KIRA']
                        repeats = command_tuple[verb][digit]['repeats']
                        SendToKIRA(target, port, KIRA_string, repeats, DELAY)
                        time.sleep(PAUSE_BETWEEN_COMMANDS)

            elif verb == 'Pause':
                # Simply pause the appropriate period of time.
                time.sleep(command_tuple[verb])

        time.sleep(PAUSE_BETWEEN_COMMANDS)        
                   
    response = DIRECTIVE_RESPONSE

    prop = CAPABILITY_DIRECTIVE_PROPERTIES_RESPONSES[interface]
    prop['timeOfSample'] = get_utc_timestamp()

    # Depending on the interface/directive, need to construct an appropriate
    # value field. 
    # XXX this should be data driven, but for now do in code, because frankly
    # the API is all over the place here.
    if interface == 'PowerController':
        if directive == 'TurnOn':
            prop['value'] = "ON"
        else:
            prop['value'] = "OFF"
    elif interface == 'ChannelController':
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

