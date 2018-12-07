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

# This file allows for explicit testing of stuff.

import logging
import time
import pprint
import json
import testCases

from KIRAIO import SendToKIRA
from deviceDB import DEVICE_DB
from AWSlambda import lambda_handler

# Logger boilerplate
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kira.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
























# Some user-specific test primitives here

PORT = 65432
REPEAT = 1
DELAY = 0.04




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

turnontv = {
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
      "endpointId": "TV",
      "cookie": {}
    },
    "payload": {}
  }
}
response = lambda_handler(turnontv, "")
print(json.dumps(response))

turnofftv = {
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
      "endpointId": "TV",
      "cookie": {}
    },
    "payload": {}
  }
}

pause = {
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
      "endpointId": "TV",
      "cookie": {}
    },
    "payload": {}
  }
}

voldown5 = {
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
      "endpointId": "TV",
      "cookie": {}
    },
    "payload": { 'volumeSteps': -5 }
  }
}

changechannel = {
    "directive": {
        "header": {
          "namespace": "Alexa.ChannelController",
          "name": "ChangeChannel",
          "payloadVersion": "3",
          "messageId": "1bd5d003-31b9-476f-ad03-71d471922820",
          "correlationToken": "dFMb0z+PgpgdDmluhJ1LddFvSqZ/jCc8ptlAKulUj90jSqg=="
        },
        "endpoint": {
          "scope": {
            "type": "BearerToken",
            "token": "access-token-from-skill"
          },
          "endpointId": "TV",
          "cookie": {}
        },
        "payload": {
           "channel": {
                "number": "1",
                "callSign": "KSTATION1",
                "affiliateCallSign": "KSTATION2",
                "uri": "someUrl"
            },
        }
    }
}

#response = lambda_handler(turnontv, "")

TARGET = "cloudon7281.ddns.net:65433"
#TARGET = "hbradburn7281.ddns.net"

bluray = DEVICE_DB['Panasonic']['DMP-BDT110EB']['IRcodes']
tv = DEVICE_DB['Pioneer']['PDP-LX508D']['IRcodes']
arcam = DEVICE_DB['Arcam']['AVR360']['IRcodes']
humax = DEVICE_DB['Humax']['DTR-T2100']['IRcodes']
htv = DEVICE_DB['Panasonic']['TX-L32X10AB']['IRcodes']

#for n in range(0,1000):
#SendToKIRA(TARGET, tv['PowerToggle'], 6, 0.04)
#  time.sleep(2.5)
#SendToKIRA(TARGET, PORT, tv['PowerOn'], 2, 0.04)
#SendToKIRA(TARGET, PORT, tv['PowerOn'], 2, 0.04)
#SendToKIRA(TARGET, PORT, tv['PowerOn'], 2, 0.04)
#SendToKIRA(TARGET, PORT, tv['PowerOn'], 2, 0.04)


