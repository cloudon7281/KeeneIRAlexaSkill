# -*- coding: utf-8 -*-

# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Amazon Software License (the "License"). You may not use this file except in
# compliance with the License. A copy of the License is located at
#
#    http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific
# language governing permissions and limitations under the License.

"""CL hacked about version of sample Alexa Smart Home Lambda Function.

Removes all the v2 to v3 guff, and just deals with a simple discovery request returning a single
TV object
"""

import logging
import time
import json
import uuid
import socket

# Imports for v3 validation
#from validation import validate_message

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Some KIRA IR codes
KIRA_IR_codes = { 'BluRay':
                            { 'Eject': 'K 2627 1123 11DD 019D 0244 019D 0244 019E 0243 019E 0243 019E 0243 019E 062A 019D 0244 019D 0246 019D 0244 019D 0243 019D 0244 019D 0244 0183 025E 0182 025E 0182 0244 019D 0244 019D 11F7 0184 062A 019E 062A 019E 062A 019E 0243 019E 062A 019D 0246 019C 0246 019D 0243 019E 0243 019E 0244 019D 0243 019E 0244 019D 0244 019D 062A 0183 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 062A 019E 2000'},
                  'YouView':
                            { '0': 'K 2602 22E4 08D5 021D 2000',
                              '1': 'K 2602 22DE 08DA 0221 2000',
                              '2': 'K 2602 22E3 08D6 0220 2000',
                              '3': 'K 2602 22DE 08DB 0201 2000',
                              '4': 'K 2602 22F9 08DA 0220 2000',
                              '5': 'K 2602 22E3 08D6 021E 2000',
                              '6': 'K 2602 22F8 08DB 0206 2000',
                              '7': 'K 2602 22DF 08BF 021F 2000',
                              '8': 'K 2602 22F9 08DA 021D 2000',
                              '9': 'K 2602 22E1 08D8 021D 2000',
                              'PowerToggle': 'K 2602 22DF 08D9 021E 2000',
                              'Up': 'K 2602 22E3 08D6 021F 2000',
                              'Down': 'K 2602 22F9 08DA 021D 2000',
                              'Left': 'K 2602 22DE 08DB 0220 2000',
                              'Right': 'K 2602 22DE 08DB 0220 2000',
                              'OK': 'K 2602 22DE 08DA 021D 2000',
                              'Guide': 'K 2602 22F8 08DB 0201 2000',
                              'Menu': 'K 2602 22DE 08DB 0220 2000',
                              'Info': 'K 2602 22FD 08D7 0202 2000',
                              'Exit': 'K 2602 22DE 08DB 021B 2000',
                              'Delete': 'K 2602 22F9 08DA 0205 2000',
                              'MyView': 'K 2602 22E4 08D5 0221 2000',
                              'ChannelDown': 'K 2622 22E0 11AC 021D 0249 021C 0249 021E 0246 0206 0244 021E 0247 021E 0247 0205 025E 0205 0246 021C 0248 021D 0248 0203 0248 021E 0246 021D 0697 021D 0248 021D 0248 0205 0244 021E 0696 021D 0696 021E 0696 021F 0695 021D 0249 021D 0247 0205 025F 0203 0247 021C 0249 021D 0247 0205 0246 021D 0248 021C 0697 021E 0696 021D 0697 021D 0696 021D 2000'
                            }         
                }

target = "cloudon7281.ddns.net"

# Define a single v3 appliance - a TV providing simple Power capabilities
SAMPLE_APPLIANCES = [
    {
        "endpointId": "Pioneer-PDP-LX50",
        "friendlyName": "Calum's living room TV",
        "Description": "Calum's living room TV",
        "manufacturerName": "Pioneer",
        "displayCategories": [
            "TV"
        ],
        "cookie": { "key":"value"},
        "capabilities": [
            {
                "type": "AlexaInterface",
                "interface": "Alexa.PowerController",
                "version": "1.0",
                "properties": {
                    "supported": [
                        { "name": "powerState" }
                    ],
                "proactivelyReported": False,
                "retrievable": False
                },
            }
        ]
    }
]


def Send(host, port, mesg, repeat, repeatDelay):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    for i in range(repeat+1):
        logger.info("Sending event to target %s on port %d; event = %s", host, port, mesg)
        sock.sendto(mesg.encode('utf-8'), (host, port))
        if i == repeat:
            time.sleep(repeatDelay)
    sock.close()

def lambda_handler(request, context):
    """Main Lambda handler.
    """

    try:
        logger.info("Directive:")
        logger.info(json.dumps(request, indent=4, sort_keys=True))

        if request["directive"]["header"]["name"] == "Discover":
            response = handle_discovery(request)
        else:
            response = handle_non_discovery(request)

        logger.info("Response:")
        logger.info(json.dumps(response, indent=4, sort_keys=True))

        #logger.info("Validate v3 response")
        #validate_message(request, response)

        return response
    except ValueError as error:
        logger.error(error)
        raise

# utility functions
def get_appliance_by_appliance_id(appliance_id):
    for appliance in SAMPLE_APPLIANCES:
        if appliance["applianceId"] == appliance_id:
            return appliance
    return None

def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))

def get_uuid():
    return str(uuid.uuid4())

# v3 handlers
def handle_discovery(request):
    endpoints = []
    for appliance in SAMPLE_APPLIANCES:
        endpoints.append(appliance)

    response = {
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

def handle_non_discovery(request):
    request_namespace = request["directive"]["header"]["namespace"]
    request_name = request["directive"]["header"]["name"]

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

