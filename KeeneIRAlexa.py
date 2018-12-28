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

# This file provides the CLI to read and write user and device details.

import sys
import argparse
import json
import pprint
import os

from logutilities import log_info, log_debug
from stateStorage import Device, User

pp = pprint.PrettyPrinter(indent=2, width = 200)

def parse_command_line(argv):
	parser = argparse.ArgumentParser(description='Manage user and device details for Keene IR Alexa skill')
	parser.add_argument("command", choices = ['get', 'set'], help='One of get or set')
	parser.add_argument('-f','--file', type=str, help='File to read/write object from')
	parser.add_argument('-u','--user', action='store_true', help='Amazon account name of user')
	parser.add_argument('-l','--details', action='store_true', help='Set if wanting to get/set user details')
	parser.add_argument('-o','--model', action='store_true', help='Set if wanting to get/set user model')
	parser.add_argument('-s','--status', action='store_true', help='Set if wanting to get/set user device status')
	parser.add_argument('-m','--manufacturer', action='store_true', help='Manufacturer name')
	parser.add_argument('-d','--device', action='store_true', help='Device name')
	parser.add_argument('-b','--bulk', action='store_true', help='Bulk load')

	args = vars(parser.parse_args())
	return args

def print_user_details(user_details):
	user_devices = user_details['devices']
	user_targets = user_details['targets']

	print("KIRA target addresses:")
	for t in user_targets:
		print("\t%s @ %s" % (t, user_targets[t]))
	print("Devices:")
	for d in user_devices:
		print("\t%s" % (d['friendly_name']))
		print("\t\t%s/%s" % (d['manufacturer'], d['model']))
		if 'target' in d:
			print("\t\ttarget %s" % (d['target']))
		if 'connected_to' in d:
			print("\t\tconnected to %s on %s" % (d['connected_to']['next_device'], d['connected_to']['input']))
	
def print_device_status(device_status):
	for device in device_status:
		print("%s is %s" % (device, "on" if status[device] else "off"))

def print_device(device):
	roles = device['roles']
	supports = device['supports']
	IRcodes = device['IRcodes']

	print("Roles:")
	for r in roles:
		print("\t%s" % (r))
	print("Supports Alexa interfaces:")
	for i in supports:
		print("\t%s" % (i))
	print("IR codes:")
	for c in IRcodes:
		print("\t%<20s: %s" % (c, IRcodes[c]))


def main(argv):
	# Start by parsing the command-line options.
	args_dict = parse_command_line(argv)
	
	get = (args_dict['command'] == "get")
	user = False

	if not get:
		if not args_dict['file']:
			print("Error: if setting an object must specify JSON file")
			return
		else:
			json_file = args_dict['file']

	if args_dict['user']:
		user_id = args_dict['user']
		user = True
	elif args_dict['manufacturer']:
		manufacturer = args_dict['manufacturer']
		device = args_dict['device']
	elif not args_dict['bulk']:
		print("Error: must specify one of user or manufacturer")
		return

	if user:
		if get:
			u = User(user_id)
			if args_dict['details']:
				print_user_details(u.read_details())
			elif args_dict['model']:
				print(pp.pformat(u.read_model()))
			elif args_dict['status']:
				print_device_status(u.read_device_status())
		else:
			input_dict = json.loads(open(json_file).read())

			if not args_dict['bulk']:
				this_dict = { user_id: input_dict }
			else:
				this_dict = input_dict

			for this_user in this_dict:
				u = User(this_user)
				if args_dict['details']:
					print("Uploading details for user %s" % (this_user))
					u.write_details(this_dict[this_user])
				elif args_dict['model']:
					print("Error - models are auto-generated and cannot be uploaded")
				elif args_dict['device']:
					print("Error - device status cannot be directly uploaded; re-run discovery to reset status to 'all off'")
	else:
		if get:
			d = Device(manufacturer, device)
			print_device(d.read())
		else:
			input_dict = json.loads(open(json_file).read())

			if not args_dict['bulk']:
				this_dict = { manufacturer: { device: input_dict } }
			else:
				this_dict = input_dict

			for this_manufacturer in this_dict:
				for this_device in this_dict[this_manufacturer]:
					print("Uploading details for device %s from manufacturer %s" % (this_device, this_manufacturer))
					d = Device(this_manufacturer, this_device)
					d.write(this_dict[this_manufacturer][this_device])


if __name__ == "__main__":
    main(sys.argv[1:])
