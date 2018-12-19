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
import copy

from userDetails import USER_DETAILS
from alexaSchema import DISCOVERY_RESPONSE

from utilities import verify_static_user, verify_request, get_uuid, get_utc_timestamp
from AWSutilities import extract_user, unpack_request, is_discovery
from mapping import model_user, skip_command
from runCommand import run_command
from response import construct_response

# Logger boilerplate
logger = logging.getLogger()
logger.setLevel(logging.INFO)
pp = pprint.PrettyPrinter(indent=2, width = 200)

PAUSE_BETWEEN_COMMANDS = 0.2

DEVICE_STATE = {}

def set_initial_state():
    # Quick hack to set state of all devices to 'off' at start of run
    for d in USER_DETAILS['testuser']['devices']:
        DEVICE_STATE[d['friendly_name']] = False


def lambda_handler(request, context):
    # Main lambda handler.  We simply switch on the directive type.

    logger.info("Received request")
    logger.info(json.dumps(request, indent=4))
    logger.info("Current device state: %s", pp.pformat(DEVICE_STATE))

    user = extract_user(request)
    logger.info("Request is for user %s", user)

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
        discovery_response, command_sequences, endpoint_involvement = model_user(USER_DETAILS[user])
        set_initial_state()
    else:
        # If this is a discovery, we need to read the user's devices object 
        # plus the global device DB from S3, and then write the mapped activity
        # responses back to S3.
        # If this is a directive, we read the activity responses.
        logger.debug("Reading from S3 - not yet implemented")

    if is_discovery(request):
        response = reply_to_discovery(discovery_response)
    else:
        response = handle_non_discovery(request, command_sequences, endpoint_involvement)

    logger.info("Response:")
    logger.info(json.dumps(response, indent=4, sort_keys=True))

    return response

def reply_to_discovery(discovery_response):
    # Handle discovery requests.  This is straightforward: we have already 
    # mapped the users set of devices to an auto-generated list of activities
    # (endpoints), so just return them.
    logger.info("Reply to discovery")

    response = DISCOVERY_RESPONSE
    response['event']['payload']['endpoints'] = discovery_response
    response['event']['header']['messageId'] = get_uuid()
                    
    return response

def handle_non_discovery(request, command_sequences, endpoint_involvement):
    # We have received a directive for some capability interface, which we have
    # to now act on.
    # The command_sequences structure is a dict telling us what to do.  It
    # is a nested dict with the following structure:
    #
    # { endpoint:
    #     { capability:
    #         { directive:
    #             [ list of specific commands ]
    #         }
    #     }
    # }
    #
    # The endpoint_involvement dict tells us which devices are needed for
    # which endpoints, plus for each device whether or not it has separate
    # on/off commands or (evil) a single power toggle.  We use the combo of
    # current state, device involvement and toggle vs. on/off to decide
    # (a) whether to skip any commmands and (b) any additional commands
    # to send for devices that should be switched off.

    # Extract the key fields from the request and check it's one we recognise
    capability, directive, payload, endpoint_id = unpack_request(request)
    verify_request(command_sequences, endpoint_id, capability, directive)

    logger.info("Received directive %s on capability %s for endpoint %s", directive, capability, endpoint_id)

    # Get the list of commands we need to respond to this directive
    commands_list = command_sequences[endpoint_id][capability][directive]

    logger.info("Commands to execute:\n%s", pp.pformat(commands_list))

    for command_tuple in commands_list:
        for verb in command_tuple:
            logger.debug("Verb to run: %s", verb)

            # Before issuing this command, check in case we should skip it.
            if not skip_command(directive, verb, command_tuple[verb], endpoint_involvement, DEVICE_STATE):
                run_command(verb, command_tuple[verb], PAUSE_BETWEEN_COMMANDS, payload)
            else:
                logger.debug("Already in correct state: skipping")  

            # need to turn off stuff on but not involved plus set new state 

        time.sleep(PAUSE_BETWEEN_COMMANDS)        
                   
    response = construct_response(request)

    return response
