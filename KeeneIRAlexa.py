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
from userState import Device, User
from ip import SendTCP, SendUDP

pp = pprint.PrettyPrinter(indent=2, width = 200)

def parse_command_line(argv):
	parser = argparse.ArgumentParser(description='Manage user and device details for Keene IR Alexa skill, and send test commands to devices.')
	parser.add_argument("command", choices = ['get', 'set', 'send'], help='One of get, set or send')
	parser.add_argument('-u','--user', type=str, help='Amazon account name of user')
	parser.add_argument('-m','--manufacturer', type=str, help='Manufacturer name')
	parser.add_argument('-d','--device', type=str, help='Device name')
	parser.add_argument('-f','--file', type=str, help='File to read/write object from')
	parser.add_argument('-b','--bulk', type=str, choices = ['user', 'device'], help='Bulk load')
	parser.add_argument('-l','--details', action='store_true', help='Set if wanting to get/set user details')
	parser.add_argument('-o','--model', action='store_true', help='Set if wanting to get/set user model')
	parser.add_argument('-s','--status', action='store_true', help='Set if wanting to get/set user device status')
	parser.add_argument('-t','--target', type=str, help='Target to send KIRA command to; must be of form <IP address>:<port>')
	parser.add_argument('-i','--IRcommand', type=str, help='Name of IR command to send')
	parser.add_argument('-r','--repeats', type=int, default=0, help='Number of repeats')

	args = vars(parser.parse_args())
	return args

def print_user_details(user_details, device_status):
	user_devices = user_details['devices']
	user_targets = user_details['targets']

	print("KIRA target addresses:")
	for t in user_targets:
		print("-\t%s @ %s" % (t, user_targets[t]))
	print("Devices:")
	for d in user_devices:
		print("-\t%s (%s)" % (d['friendly_name'], "on" if device_status[d['friendly_name']] else "off"))
		print("-\t\t%s/%s" % (d['manufacturer'], d['model']))
		if 'target' in d:
			print("-\t\ttarget %s" % (d['target']))
		if 'room' in d:
			print("-\t\troom %s" % (d['room']))
		if 'connected_to' in d:
			print("-\t\tconnected to %s on %s" % (d['connected_to']['next_device'], d['connected_to']['input']))
	
def print_device_status(device_status):
	for device in device_status:
		print("%-20s%s" % (device, "On" if device_status[device] else "Off"))

def print_device(device):
	roles = device['roles']
	supports = device['supports']
	protocol = device['protocol']
	IRcodes = device['IRcodes']

	print("Roles:")
	for r in roles:
		print("-\t%s" % (r))
	print("Supports Alexa interfaces:")
	for i in supports:
		print("-\t%s" % (i))
	print("Protocol used:\n-\t%s" % protocol)
	print("IR codes:")
	for c in IRcodes:
		print("-\t%-20s %s" % (c, IRcodes[c]))


def main(argv):
	# Start by parsing the command-line options.
	args_dict = parse_command_line(argv)
	
	get_cmd = (args_dict['command'] == "get")
	set_cmd = (args_dict['command'] == "set")
	send_cmd = (args_dict['command'] == "send")

	user = False
	bulk = False

	if set_cmd:
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
	elif args_dict['bulk']:
		bulk = True
		if args_dict['bulk'] == "user":
			user = True
	else:
		print("Error: must specify one of user or device")
		return

	if user:
		if get_cmd:
			u = User(user_id)
			if args_dict['details']:
				print_user_details(u.get_details(), u.get_device_status())
			elif args_dict['model']:
				print(pp.pformat(u.get_model()))
			elif args_dict['status']:
				print_device_status(u.get_device_status())
		elif set_cmd:
			input_dict = json.loads(open(json_file).read())

			if not bulk:
				this_dict = { user_id: input_dict }
			else:
				this_dict = input_dict

			for this_user in this_dict:
				print("Uploading details for user %s" % (this_user))
				u = User(this_user)
				u.set_details(this_dict[this_user])
		else:
			print("Error: cannot send to a user, only a device")
	else:
		if get_cmd:
			d = Device(manufacturer, device, use_S3=True)
			print_device(d.get())
		elif set_cmd:
			input_dict = json.loads(open(json_file).read())

			if not bulk:
				this_dict = { manufacturer: { device: input_dict } }
			else:
				this_dict = input_dict

			for this_manufacturer in this_dict:
				for this_device in this_dict[this_manufacturer]:
					print("Uploading details for device %s from manufacturer %s" % (this_device, this_manufacturer))
					d = Device(this_manufacturer, this_device, use_S3=True)
					d.set(this_dict[this_manufacturer][this_device])
		else:
			if not (args_dict['target'] and args_dict['command']):
				print("Error: must specify both a target and a command to send to that target")
			else:
				d = Device(manufacturer, device, use_S3=True)
				details = d.get()
				IRcommand = args_dict['IRcommand']
				target = args_dict['target']
				repeats = args_dict['repeats']
				protocol = details['protocol']
				try:
					KIRA = details['IRcodes'][IRcommand]
					print("Sending %s to %s/%s at address %s" % (IRcommand, manufacturer, device, target))
					print("IR code string is %s" % (KIRA))
					if protocol == "udp":
						SendUDP(target, KIRA, repeats, 0.02)
					else:
						SendTCP(target, KIRA, repeats, 0.02)
				except KeyError:
					print("Error: could not find command %s for device %s/%s" % (IRcommand, manufacturer, device))


if __name__ == "__main__":
    main(sys.argv[1:])
