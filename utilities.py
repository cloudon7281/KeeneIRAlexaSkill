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

# This file contains a number of utilities.

import logging
import time
import uuid
from deviceDB import DEVICE_DB
from userDevices import DEVICES

logger = logging.getLogger()

def get_utc_timestamp(seconds=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S.00Z", time.gmtime(seconds))

def get_uuid():
    return str(uuid.uuid4())

def verify_user(user):
	# Check we know about this user
	if user in DEVICES:
		logger.info("Recognise user %s", user)
	else:
		logger.error("Don't recognise user %s", user)

def verify_request(responses, endpoint, interface, directive):
	# Check we know about this endpoint
	if endpoint in responses:
		logger.info("Recognise endpoint %s", endpoint)

		if interface in responses[endpoint]:
			logger.info("Recognise interface %s", interface)

			if directive in responses[endpoint][interface]:
				logger.info("Recognise directive %s", directive)
			else:
				logger.error("Don't recognise directive %s", directive)
		else:
			logger.error("Don't recognise interface %s", interface)
	else:
		logger.error("Don't recognise endpoint %s", endpoint)

def verify_devices(devices):
	# Check we recognise the list of devices the user has.  As we'er running
	# as a lambda, don't worry too much about raising and catching exceptions;
	# the important thing is to log it.
	logger.info("Validate user devices exist in DB")
	bad_device = False
	for device in devices:
		logger.info("User has device %s", device['friendly_name'])	
		manu = device['manufacturer']
		model = device['model']
		if manu in DEVICE_DB:
			if model in DEVICE_DB[manu]:
				logger.info("Manu %s, model %s found OK", manu, model)
			else:
				logger.error("Device %s with manu %s has incorrect model %s", device['friendly_name'], manu, model)
				bad_device = True
		else:
			logger.error("Device %s has incorrect manu %s", device['friendly_name'], manu)
			bad_device = True

def find_user_device_in_DB(user_device):
	# Given a user device, return the details in the device DB
	manu = user_device['manufacturer']
	model = user_device['model']
	return DEVICE_DB[manu][model]

def find_device_from_friendly_name(devices, friendly_name):
	# Given a device friendly name, find it in the list of user devices
	for d in devices:
		if d['friendly_name'] == friendly_name:
			return d

