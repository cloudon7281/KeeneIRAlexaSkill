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

# This file maintains state for a user and devices.  It exposes:
# - public methods to set and get user and device details (used by the CLI to
#   provision users)
# - public methods to trigger model creation (used by the discovery handler)
#   and read the model (used by the request handler)
# - public methods to get and set device status for a user (used by the request
#   handler)
#
# It implements a write-through cache i.e. all sets of user and device details
# plus device status and the model are secured to S3 (unless using static
# files for offline test purposes, in which case they are secured to global
# vars).
#
# The set of S3 objects used is as follows.
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
# This schema (key structure plus object data) are versioned using semver.
# The S3 values are simply Python objects serialised via pickle.

import pickle
import pprint
import os
import copy

from AWSS3storage import write_object, read_object
from logutilities import log_info, log_debug, log_error
from deviceDB import DEVICE_DB
from userDetails import USER_DETAILS
from utilities import verify_devices
from mapping import model_user

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


# Global vars for the non-S3 case
G_MODEL = {}
G_DEVICE_STATUS = {}

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

	def __init__(self, manufacturer, device, use_S3):
		self.manufacturer = manufacturer
		self.device = device
		self.device_details = {} 
		self.use_S3 = use_S3
		log_debug("Creating Device object for manufacturer %s/device %s", manufacturer, device)
		log_debug("Using S3 rather than static files? %s", self.use_S3)

	def set(self, details):
		if self.use_S3:
			write_state(BUCKET_GLOBALDB, self.manufacturer + "-" + self.device, details)
		else: 
			log_error("Called to write device details but using static files")

	def get(self):
		if self.use_S3:
			self.device_details = read_state(BUCKET_GLOBALDB, self.manufacturer + "-" + self.device)
		else:
			try:
				self.device_details = DEVICE_DB[self.manufacturer][self.device]
			except KeyError:
				log_error("Could not find device %s from manufacturer %s in static files", self.device, self.manufacturer)
		return self.device_details
	
class User:
	# This class models the details uploaded by a user about their own setup.

	def __init__(self, user_id):
		self.use_S3 = ('USE_STATIC_FILES' not in os.environ)
		self.user_id = user_id
		self.user_details = {}
		self.model = {}
		self.device_status = {}
		self.devicesDB = {}
		log_debug("Create a User object for user %s", user_id)
		log_debug("Using S3 for storage? %s", self.use_S3)

	def set_details(self, details):
		log_debug("Set user details for user %s to be %s", self.user_id, pp.pformat(details))
		self.user_details = details
		if self.use_S3:
			write_state(BUCKET_USERDB, self.user_id + KEY_USER_DETAILS, details)

	def get_details(self):
		if self.use_S3:
			if not self.user_details:
				self.user_details = read_state(BUCKET_USERDB, self.user_id + KEY_USER_DETAILS)
		else:
			try:
				self.user_details = USER_DETAILS[self.user_id]
			except KeyError:
				log_error("Could not find user %s in static files", self.user_id)
	
	def create_model(self):
		# Create a model for this user, plus initialise the device status to
		# 'all devices off'
		log_debug("Create model for user %s", self.user_id)
		self.get_details()
		user_devices = self.user_details['devices']
		device_state = {}

		for user_device in user_devices:
			manufacturer = user_device['manufacturer']
			model = user_device['model']
			d = Device(manufacturer, model, self.use_S3)
			if manufacturer not in self.devicesDB:
				self.devicesDB[manufacturer] = {}
			self.devicesDB[manufacturer][model] = d.get()
			device_state[user_device['friendly_name']] = False

		log_debug("Device DB for user's devices: %s", pp.pformat(self.devicesDB))
		self.model = model_user(self.user_details, self.devicesDB)
		if self.use_S3:
			log_debug("Secure model to S3")
			write_state(BUCKET_USERDB, self.user_id + KEY_USER_MODEL, self.model)
		else:
			global G_MODEL
			G_MODEL = copy.deepcopy(self.model)
			log_debug("Secured model to memory: %s", pp.pformat(G_MODEL))
		self.set_device_status(device_state)

	def get_model(self):
		if not self.model:
			if self.use_S3:
				log_debug("Retrieve model from S3")
				self.model = read_state(BUCKET_USERDB, self.user_id + KEY_USER_MODEL)
			else:
				global G_MODEL
				log_debug("Retrieve model from memory: %s", pp.pformat(G_MODEL))
				self.model = copy.deepcopy(G_MODEL)
		return self.model

	def set_device_status(self, device_status):
		log_debug("Set device status for user %s to be %s", self.user_id, pp.pformat(device_status))
		self.device_status = device_status
		if self.use_S3:
			log_debug("Secure model to S3")
			write_state(BUCKET_USERDB, self.user_id + KEY_USER_DEVICE_STATUS, device_status)
		else:
			log_debug("Secure model to memory")
			global G_DEVICE_STATUS
			G_DEVICE_STATUS = copy.deepcopy(device_status)

	def get_device_status(self):
		if not self.device_status:
			if self.use_S3:
				log_debug("Retrieve model from S3")
				self.device_status = read_state(BUCKET_USERDB, self.user_id + KEY_USER_DEVICE_STATUS)
			else:
				log_debug("Retrieve model from memory")
				global G_DEVICE_STATUS
				self.device_status = copy.deepcopy(G_DEVICE_STATUS)
		return self.device_status