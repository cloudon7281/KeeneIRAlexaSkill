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

# This file defines test directives.

Discover = {
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

TurnOnAVSource = {
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOn",
      "payloadVersion": "3",
      "messageId": "1bd5d003-31b9-476f-ad03-71d471922820",
      "correlationToken": "dFMb0z+PgpgdDmluhJ1LddFvSqZ/jCc8ptlAKulUj90jSqg=="
    },
    "endpoint": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-skill"
      },
      "endpointId": "AVsource",
      "cookie": {}
    },
    "payload": {}
  }
}

TurnOffAVSource = {
  "directive": {
    "header": {
      "namespace": "Alexa.PowerController",
      "name": "TurnOff",
      "payloadVersion": "3",
      "messageId": "1bd5d003-31b9-476f-ad03-71d471922820",
      "correlationToken": "dFMb0z+PgpgdDmluhJ1LddFvSqZ/jCc8ptlAKulUj90jSqg=="
    },
    "endpoint": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-skill"
      },
      "endpointId": "AVsource",
      "cookie": {}
    },
    "payload": {}
  }
}

PauseAVSource = {
  "directive": {
    "header": {
      "namespace": "Alexa.PlaybackController",
      "name": "Pause",
      "payloadVersion": "3",
      "messageId": "1bd5d003-31b9-476f-ad03-71d471922820",
      "correlationToken": "dFMb0z+PgpgdDmluhJ1LddFvSqZ/jCc8ptlAKulUj90jSqg=="
    },
    "endpoint": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-skill"
      },
      "endpointId": "AVsource",
      "cookie": {}
    },
    "payload": {}
  }
}

VolDown5AVSource = {
  "directive": {
    "header": {
      "namespace": "Alexa.StepSpeaker",
      "name": "AdjustVolume",
      "payloadVersion": "3",
      "messageId": "1bd5d003-31b9-476f-ad03-71d471922820",
      "correlationToken": "dFMb0z+PgpgdDmluhJ1LddFvSqZ/jCc8ptlAKulUj90jSqg=="
    },
    "endpoint": {
      "scope": {
        "type": "BearerToken",
        "token": "access-token-from-skill"
      },
      "endpointId": "AVsource",
      "cookie": {}
    },
    "payload": { 'volumeSteps': -5 }
  }
}


testCases = [
  { 
    "title": "Discover",
    "expect_kira_commands": False,
    "directive": Discover,
    "expected_commands": None, 
  },
  { 
    "title": "Turn on AV source - all devices start off",
    "expect_kira_commands": True,
    "directive": TurnOnAVSource,
    "expected_kira_commands": [ "TestAVSource: power toggle", "TestMonitor: power toggle", "TestMonitor: input HDMI1" ]
  }
]
