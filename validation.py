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

# This file implements schema validation against the schema published at
# https://github.com/alexa/alexa-smarthome/tree/master/validation_schemas

import json

from jsonschema import validate

def validate_message(response):

    path_to_validation_schema = "alexa_smart_home_message_schema.json"

    with open(path_to_validation_schema) as json_file:
        schema = json.load(json_file)
    validate(response, schema)
