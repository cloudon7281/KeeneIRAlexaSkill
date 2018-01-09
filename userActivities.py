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

# This file defines on a per-user basis the set of activities that will be 
# mapped to devices across the Smart Home Skills API.
#
# For each activity it defines the capabilities supported by that activity, and
# for each directive thus supported across the Alexa API the set of commands 
# that it is mapped to.
#
# In time there would ideally be some nice GUI to allow users to configure
# these a la Logitech UIs, with the results stored in S3, but for now we hard
# code.

from deviceIRcodes import KIRA_IR_codes

ACTIVITIES = {
                'user1':
                [
                    {
                        'activityname': 'YouView',
                        'SHSdefinition':
                        {
                            "endpointId": "YouView",
                            "friendlyName": "X",
                            "Description": "Y",
                            "manufacturerName": "Z",
                            "displayCategories": [ "TV" ],
                            "capabilities":
                            [
                                {
                                    "type": "AlexaInterface",
                                    "interface": "Alexa.PowerController",
                                    "version": "1.0",
                                    "properties":
                                    {
                                        "supported":
                                        [
                                            { "name": "powerState" }
                                        ],
                                        "proactivelyReported": False,
                                        "retrievable": False
                                    },
                                }
                            ]
                        },
                        'directives':
                        [
                            { 'Alexa.PowerController':
                                { 'TurnOn':
                                    [ 
                                        {   
                                            KIRA_IR_codes['Pioneer']['PDP-LX50D']['PowerOn'],
                                            KIRA_IR_codes['Pioneer']['PDP-LX50D']['InputHDMI1'],
                                            KIRA_IR_codes['Humax']['DTR-T2100']['PowerToggle'],
                                            KIRA_IR_codes['Arcam']['AVR360']['PowerOn'],
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                ]
             }
