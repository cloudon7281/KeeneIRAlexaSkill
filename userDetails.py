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

USER_DETAILS =  {
                    'amzn1.account.AGY6FJTLLYJH6EYDMHWXLQSUJQZQ': {
                        'targets': {
                            'targeta': 'cloudon7281.ddns.net:65432',
                            'targetb': 'cloudon7281.ddns.net:65433',
                            'targetc': 'cloudon7281.ddns.net:65434'
                        },
                        'devices': [
                            {
                                'friendly_name': 'Blu-ray', 
                                'manufacturer': 'Oppo',
                                'model': 'BDP-83',
                                'target': 'targeta',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputBR'
                                }
                            },
                            {
                                'friendly_name': 'Compact Disc', 
                                'manufacturer': 'Oppo',
                                'model': 'BDP-83-CD',
                                'target': 'targeta',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputCD'
                                }
                            },
                            {
                                'friendly_name': 'TV', 
                                'manufacturer': 'Virgin',
                                'model': 'Hub-3',
                                'target': 'targetb',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputSAT'
                                }
                            },
                            {
                                'friendly_name': 'Firestick', 
                                'manufacturer': 'Amazon',
                                'model': 'Firestick',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputVCR'
                                }
                            },
                            {
                                'friendly_name': 'Dot', 
                                'manufacturer': 'Amazon',
                                'model': 'Echo Dot',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputPVR'
                                }
                            },
                            {
                                'friendly_name': 'Wii', 
                                'manufacturer': 'Nintendo',
                                'model': 'Wii U',
                                'connected_to': 
                                {
                                    'next_device': 'Receiver',
                                    'input': 'InputAV'
                                }
                            },
                            {
                                'friendly_name': 'Receiver', 
                                'manufacturer': 'Arcam',
                                'model': 'AVR360',
                                'target': 'targetc',
                                'connected_to': 
                                {
                                    'next_device': 'Monitor',
                                    'input': 'InputHDMI1'
                                }
                            },
                            {
                                'friendly_name': 'Monitor', 
                                'manufacturer': 'Pioneer',
                                'model': 'PDP-LX508D',
                                'target': 'targetb'
                            }
                        ]
                    },
                    'amzn1.account.AEH3ZOZHYIZQA3VB75UPFMTQAMPQ': {
                        'targets': {
                            'primary': 'hbradburn7281.ddns.net:65432',
                        },
                        'devices': [
                            {
                                'friendly_name': 'TV',
                                'manufacturer': 'Humax',
                                'model': 'DTR-T2100',
                                'connected_to':
                                {
                                    'next_device': 'Monitor',
                                    'input': 'Input2'
                                }
                            },
                            {
                                'friendly_name': 'Firestick', 
                                'manufacturer': 'Amazon',
                                'model': 'Firestick',
                                'connected_to': 
                                {
                                    'next_device': 'Monitor',
                                    'input': 'Input3'
                                }
                            },
                            {
                                'friendly_name': 'Monitor', 
                                'manufacturer': 'Panasonic',
                                'model': 'TX-L32X10AB',
                            }
                        ]
                    }
                }