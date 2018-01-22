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

# This file talks to Amazon LWA (the AWS OAuth2 service) to extract the user
# corresponding to an access token.

import os
import logging
import json
import pprint
import requests
import urllib

logger = logging.getLogger()

LWA_PROFILE_URL = 'https://api.amazon.com/user/profile?'

def get_user_from_token(token):
    logger.debug("Token is %s", token)

    url = LWA_PROFILE_URL + urllib.parse.urlencode({ 'access_token' : token })
    r = requests.get(url=url)

    if r.status_code == 200:
        logger.debug("Amazon profile returned is:")
        logger.debug(json.dumps(r.json(), indent=4))

        body = r.json()
        user = body['user_id']
    else:
        logger.error("Amazon look up returned an error %d", r.status_code)
        logger.error(json.dumps(r.json(), indent=4))

        user = "<unknown>"

    return user
