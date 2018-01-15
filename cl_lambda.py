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

import logging
import time
import json
import uuid
import socket

from userDevices import DEVICES
from KIRAIO import SendToKIRA
from mapping import map_user_devices

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#fh.setLevel(logging.DEBUG)
## create console handler with a higher log level
#ch = logging.StreamHandler()
#ch.setLevel(logging.ERROR)
## create formatter and add it to the handlers
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
#ch.setFormatter(formatter)
## add the handlers to the logger
#logger.addHandler(fh)
#logger.addHandler(ch)

target = "cloudon7281.ddns.net"

def lambda_handler(request, context):
    # Main lambda handler.  We simply switch on the directive type.

    # XXX We should have something at this point that looks at the token in the
    # context and figures out what user it is for.  But I don't know how to do
    # that just yet, so ignore it for now and just assume it's me.
    user = "user1"
    logger.info("Request is for user %s", user)

    # For now, map the user devices to endpoint and discovery information
    # on every request
    user_activities = map_user_devices(DEVICES[user]['devices'])

    try:
        logger.info("Directive:")
        logger.info(json.dumps(request, indent=4, sort_keys=True))

        if request["directive"]["header"]["name"] == "Discover":
            response = handle_discovery(user_activities['endpoints'])
        else:
            response = handle_non_discovery(request, endpoints)

        logger.info("Response:")
        logger.info(json.dumps(response, indent=4, sort_keys=True))

        return response

    except ValueError as error:
        logger.error(error)
        raise

# utility functions
def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))

def get_uuid():
    return str(uuid.uuid4())

# Now main handlers
def handle_discovery(endpoints):
    # We want to return both the individual devices and the aggregated 
    # activities for the given user.
    # XXX for now just do activties.
    # XXX We can find the appropriate definition to return in the SHS definition 
    # XXX field
    logger.info("It's a discovery")

    response =  {
                    "event": {
                        "header": {
                            "namespace": "Alexa.Discovery",
                            "name": "Discover.Response",
                            "payloadVersion": "3",
                            "messageId": get_uuid()
                        },
                        "payload": {
                            "endpoints": endpoints
                        }
                    }
                }
    return response

def handle_non_discovery(request, user):
    # Some action directive.  We find the appropriate sequence of events in the
    # user activity definition and send them all to KIRA in sequence.
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]
    endpoint_id = request["endpoint"]["endpointId"]

    logger.info("It's an action directive: %s, %s for endpoint ", request_namespace, request_name, endpoint_id)

    if user in ACTIVITIES:
            logger.info("Found user in activities list")
            for a in ACTIVITIES[user]:
                logger.info("Found activity:")
                logger.info(a)

                if a['activityname'] == endpoint_id:
                    logger.info("Directive aimed at this activity")

                    for d in a['directives']:
                        if request_namespace in d:
                            logger.info("Directive aimed at this namespace")

                            if request_name in d:
                                logger.info("And we support this directive")

                                for message in d[request_name]:
                                    logger.info("Send %s", message)
                                    SendToKIRA(message)






    if request_namespace == "Alexa.PowerController":
        if request_name == "TurnOn":
            value = "ON"
            Send(target, 65432, KIRA_IR_codes['BluRay']['Eject'], 2, 0.2)
        else:
            value = "OFF"

        response = {
            "context": {
                "properties": [
                    {
                        "namespace": "Alexa.PowerController",
                        "name": "powerState",
                        "value": value,
                        "timeOfSample": get_utc_timestamp(),
                        "uncertaintyInMilliseconds": 500
                    }
                ]
            },
            "event": {
                "header": {
                    "namespace": "Alexa",
                    "name": "Response",
                    "payloadVersion": "3",
                    "messageId": get_uuid(),
                    "correlationToken": request["directive"]["header"]["correlationToken"]
                },
                "endpoint": {
                    "scope": {
                        "type": "BearerToken",
                        "token": "access-token-from-Amazon"
                    },
                    "endpointId": request["directive"]["endpoint"]["endpointId"]
                },
                "payload": {}
            }
        }
        return response

    elif request_namespace == "Alexa.Authorization":
        if request_name == "AcceptGrant":
            response = {
                "event": {
                    "header": {
                        "namespace": "Alexa.Authorization",
                        "name": "AcceptGrant.Response",
                        "payloadVersion": "3",
                        "messageId": "5f8a426e-01e4-4cc9-8b79-65f8bd0fd8a4"
                    },
                    "payload": {}
                }
            }
            return response

    # other handlers omitted in this example


discover = {
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover",
      "payloadVersion": "3",
      "messageId": "1bd5d003-31b9-476f-ad03-71d471922820"
    },
    "payload": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-skill"
      }
    }
  }
}
#response = lambda_handler(discover, "")