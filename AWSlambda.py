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
import time
import json
import pprint
import requests

from userState import User
from alexaSchema import DISCOVERY_RESPONSE
from utilities import verify_static_user, verify_request, get_uuid, get_utc_timestamp
from AWSutilities import extract_user, unpack_request, is_discovery
from mapping import model_user
from runCommand import run_command, set_power_states
from response import construct_response
from logutilities import log_info, log_debug

# Logger boilerplate
#logger = logging.getLogger()
#log_setLevel(logging.INFO)
pp = pprint.PrettyPrinter(indent=2, width = 200)

PAUSE_BETWEEN_COMMANDS = 0.2

def lambda_handler(request, context):
    # Main lambda handler.  We simply switch on the directive type.

    log_info("Received request")
    log_info(json.dumps(request, indent=4))

    user_id = extract_user(request)
    log_info("Request is for user %s", user_id)

    u = User(user_id)

    if is_discovery(request):
        # On discovery requests we always re-model the user.  This is the 
        # natural point to model, as it is the only mechanism to report to 
        # Alexa any changes in a user's devices.
        # Note that creating the model also resets the device status to
        # 'all off'.
        log_debug("Discovery: model the user")
        u.create_model()
        model = u.get_model()
        response = reply_to_discovery(model['discovery_response'])
    else:
        log_debug("Normal directive: retrieve the model")
        model = u.get_model()
        log_debug("Model is %s", pp.pformat(model))
        device_status = u.get_device_status() 
        response, new_device_status, status_changed = handle_non_discovery(request, model['command_sequences'], model['device_power_map'], device_status)
        if status_changed:
            log_info("Device status changed - updating")
            u.set_device_status(new_device_status)

    log_info("Response:")
    log_info(json.dumps(response, indent=4, sort_keys=True))

    return response

def reply_to_discovery(discovery_response):
    # Handle discovery requests.  This is straightforward: we have already 
    # mapped the users set of devices to an auto-generated list of activities
    # (endpoints), so just return them.
    log_info("Reply to discovery")

    response = DISCOVERY_RESPONSE
    response['event']['payload']['endpoints'] = discovery_response
    response['event']['header']['messageId'] = get_uuid()
                    
    return response

def handle_non_discovery(request, command_sequences, device_power_map, device_state):
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
    # The device_power_map dict tells us which devices are needed for
    # which endpoints, plus for each device whether or not it has separate
    # on/off commands or (evil) a single power toggle.  We use the combo of
    # current state, device involvement and toggle vs. on/off to decide
    # (a) whether to skip any commmands and (b) any additional commands
    # to send for devices that should be switched off.

    # Extract the key fields from the request and check it's one we recognise
    capability, directive, payload, endpoint_id = unpack_request(request)
    verify_request(command_sequences, endpoint_id, capability, directive)

    log_info("Received directive %s on capability %s for endpoint %s", directive, capability, endpoint_id)

    # If this is a PowerController capability we need to figure out
    # what to turn on/off
    if capability == "PowerController":
        log_debug("Turn things on/off")
        new_device_status, status_changed = set_power_states(directive, endpoint_id, device_state, device_power_map, PAUSE_BETWEEN_COMMANDS, payload)
    else:
        new_device_status = {}
        status_changed = False

    # Get the list of commands we need to respond to this directive
    commands_list = command_sequences[endpoint_id][capability][directive]

    for command_tuple in commands_list:
        for verb in command_tuple:
            run_command(verb, command_tuple[verb], PAUSE_BETWEEN_COMMANDS, payload)

    time.sleep(PAUSE_BETWEEN_COMMANDS)        
                   
    response = construct_response(request)

    log_info("Did status change? %s", status_changed)

    return response, new_device_status, status_changed
