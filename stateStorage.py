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

# This file stores and retrieves details from the global device DB and user's 
# details.  
#
# It maps them as follows.
#
# - bucket = <BUCKET_ROOT><BUCKET_GLOBALDB>
#       + key = <KEY_ROOT><manufacturer name>-<device name>
#         value = serialised dict of device details
#
# - bucket = <BUCKET_ROOT><BUCKET_USERDB>
#       + key = <KEY_ROOT><Amazon user account name>-<KEY_USER_DETAILS>
#         value = serialised dict of user's details, containing both devices
#                 and targets
#       + key = <KEY_ROOT><Amazon user account name>-<KEY_USER_MODEL>
#         value = serialised dict of user's modelled devices
#       + key = <KEY_ROOT><Amazon user account name>-<KEY_USER_STATUS>
#         value = serialised dict of user's device status
#

import pickle
import pprint

from AWSS3storage import write_object, read_object
from logutilities import log_info, log_debug

pp = pprint.PrettyPrinter(indent=2, width = 200)


# Semver schema version
S3_SCHEMA_VERSION="V0.1.0"

BUCKET_ROOT = "keeneiralexaskill-"
BUCKET_GLOBALDB = "globaldevicedb"
BUCKET_USERDB = "users"
KEY_ROOT = "keeneiralexaskill-"
KEY_USER_DETAILS = "-details"
KEY_USER_MODEL = "-model"
KEY_USER_DEVICE_STATUS = "-device-status"


def write_state(bucket, key, state):
	blob = pickle.dumps(state)
	write_object(BUCKET_ROOT + bucket, KEY_ROOT + key, blob, S3_SCHEMA_VERSION)
	log_debug("Wrote %s/%s state: %s", bucket, key, pp.pformat(state))


def read_state(bucket, key):
	state = {}

	blob, version = read_object(BUCKET_ROOT + bucket, KEY_ROOT + key)

	if version != S3_SCHEMA_VERSION:
		log_error("Schema mismatch: read %s, code at %s", version, S3_SCHEMA_VERSION)
	else:
		state = pickle.loads(blob)
		log_debug("Read %s/%s state: %s", bucket, key, pp.pformat(state))

	return state

class Device:
	# This class models a device in the global DB

	def __init__(self, manufacturer, device):
		self.manufacturer = manufacturer
		self.device = device

	def write(self, details):
		write_state(BUCKET_GLOBALDB, self.manufacturer + "-" + self.device, details)

	def read(self):
		return read_state(BUCKET_GLOBALDB, self.manufacturer + "-" + self.device)
	
class User:
	# This class models the details uploaded by a user about their own setup.

	def __init__(self, user_id):
		self.user_id = user_id

	def write_details(self, details):
		write_state(BUCKET_USERDB, self.user_id + KEY_USER_DETAILS, details)

	def read_details(self):
		return read_state(BUCKET_USERDB, self.user_id + KEY_USER_DETAILS)
	
	def write_model(self, model):
		write_state(BUCKET_USERDB, self.user_id + KEY_USER_MODEL, model)

	def read_model(self):
		return read_state(BUCKET_USERDB, self.user_id + KEY_USER_MODEL)
	
	def write_device_status(self, device_status):
		write_state(BUCKET_USERDB, self.user_id + KEY_USER_DEVICE_STATUS, device_status)

	def read_device_status(self):
		return read_state(BUCKET_USERDB, self.user_id + KEY_USER_DEVICE_STATUS)
	