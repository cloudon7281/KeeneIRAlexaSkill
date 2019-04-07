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

# This file defines a set of commands and associated Keene KIRA IR commands for
# a range of devices.
#
# Ideally these would be auto-derived from an open source DB such as
# https://github.com/probonopd/irdb but for now hard code those devices we
# care about, based on capturing IR via a Keene receiver.
#
# Structure is [<manufacturer>][<model>] then
#     roles = any N of (AV_source|AV_switch|speaker|display)
#     supports = any N pf (PowerController|ChannelController|InputController|PlaybackController|StepSpeaker|Speaker)


DEVICE_DB = {
                'Test': {
                    'TestAVSource': {
                        'roles': { 'AV_source' },
                        'supports': { 'PowerController', 
                                      'PlaybackController' },
                        'IRcodes': {
                            'PowerToggle': 'TestAVSource: power toggle',
                            'Pause': 'TestAVSource: pause',
                            'Play': 'TestAVSource: play',
                            'Stop': 'TestAVSource: stop',
                            'Rewind': 'TestAVSource: rewind',
                            'FastForward': 'TestAVSource: fast forward',
                        },
                    },
                    'TestASource': {
                        'roles': { 'A_source' },
                        'supports': { 'PowerController', 
                                      'PlaybackController' },
                        'IRcodes': {
                            'PowerOn': 'TestASource: power on',
                            'PowerOff': 'TestASource: power off',
                            'Pause': 'TestASource: pause',
                            'Play': 'TestASource: play',
                            'Stop': 'TestASource: stop',
                            'Rewind': 'TestASource: rewind',
                            'FastForward': 'TestASource: fast forward',
                        },
                    },
                    'TestReceiver': {
                        'roles': { 'AV_switch', 'speaker' },
                        'supports': { 'PowerController', 
                                      'StepSpeaker' },
                        'IRcodes': {  
                            'PowerOn': 'TestReceiver: power on',
                            'PowerOff': 'TestReceiver: power off',
                            'InputA': 'TestReceiver: input A',
                            'InputAV': 'TestReceiver: input AV',
                            'InputHDMI1': 'TestReceiver: input HDMI1',
                            'VolumeUp': 'TestReceiver: volume up',
                            'VolumeDown': 'TestReceiver: volume down',
                            'Mute': 'TestReceiver: mute',
                        },
                    },
                    'TestMonitor': {
                        'roles': { 'display' },
                        'supports': { 'PowerController' },
                        'IRcodes': {  
                            'PowerToggle': 'TestMonitor: power toggle',
                            'InputHDMI1': 'TestMonitor: input HDMI1',
                        },
                    }
                },
            }
