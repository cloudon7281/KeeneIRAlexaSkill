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

# This file contains definitions of various parts of the Alexa skills schema.

DISCOVERY_RESPONSE = {
    "event": {
        "header": {
            "namespace": "Alexa.Discovery",
            "name": "Discover.Response",
            "payloadVersion": "3",
        },
	    "payload": {}
    }
}

DIRECTIVE_RESPONSE = {
    "context": {
    },
    "event": {
        "header": {
            "namespace": "Alexa",
            "name": "Response",
            "payloadVersion": "3",
    	},
        "payload": {}
    }
}

CAPABILITY_DISCOVERY_RESPONSES = {

	'PowerController':	{
        "type": "AlexaInterface",
        "interface": "Alexa.PowerController",
        "version": "1.0",
        "properties":
        {
            "supported":
            [
                { "name": "powerState" }
            ],
        },
	},
	'PlaybackController':  {
        "type": "AlexaInterface",
        "interface": "Alexa.PlaybackController",
        "version": "3",
        "supportedOperations": [ "Play", "Pause", "Stop" ]
    },
    'ChannelController': {
        "type": "AlexaInterface",
        "interface": "Alexa.ChannelController",
        "version": "3"
    },
	'StepSpeaker': {
        "type": "AlexaInterface",
        "interface": "Alexa.StepSpeaker",
        "version": "3",
        "properties": {},
	},
} 	   

CAPABILITY_DIRECTIVE_PROPERTIES_RESPONSES = {

	'PowerController': {
        "namespace": "Alexa.PowerController",
        "name": "powerState",
        "value": "ON",
        "uncertaintyInMilliseconds": 200,
    },
	'ChannelController':	{
        "namespace": "Alexa.ChannelController",
        "name": "channel",
        "uncertaintyInMilliseconds": 200,
    },
   	'StepSpeaker':	{
    },
   	'PlaybackController':	{
    },
} 	   

CAPABILITY_DIRECTIVES = {
	
	'PowerController': {
		'TurnOn' : {
			'SingleIRCommand': [ 'PowerOn', 'PowerToggle' ],
			'Pause': 4,
			'InputChoice': True
		},
		'TurnOff' : {
			'SingleIRCommand': [ 'PowerOff', 'PowerToggle' ],
		},
	},
	'PlaybackController': {
		'Play': { 'SingleIRCommand': ['Play'] },
		'Pause': { 'SingleIRCommand': ['Pause'] },
		'Stop': { 'SingleIRCommand': ['Stop'] },
	},
	'ChannelController': {
		'ChangeChannel': { 
			'DigitsIRCommands': {
				'0': ['0'],
				'1': ['1'],
				'2': ['2'],
				'3': ['3'],
				'4': ['4'],
				'5': ['5'],
				'6': ['6'],
				'7': ['7'],
				'8': ['8'],
				'9': ['9'],
			},
		},
	},
	'StepSpeaker': { 
		'AdjustVolume': { 
			'StepIRCommands': {
				'+ve': [ 'VolumeUp' ],
				'-ve': [ 'VolumeDown' ]
			}
		},
		'SetMute': { 'SingleIRCommand': ['Mute'] }
	},
}
