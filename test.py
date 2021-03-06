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

import os
import time
import pprint
import json
import testCases

from testip import testip
from AWSlambda import lambda_handler
from testCases import testCases


pp = pprint.PrettyPrinter(indent=2, width = 200)

def set_test_env():
	os.environ['TEST_USER'] = 'testuser'
	os.environ['TEST_TOKEN'] = 'token'
	os.environ['LOG_LEVEL'] = 'DEBUG'


def run_test(test, sinkudp, sinktcp):
	print("\nRunning test case:", test["title"])
	pass_test = True

	response = lambda_handler(test["directive"], "")

	if test["expect_kira_commands"]:
		kira_commands = []
		if test["expect_udp"]:
			kira_commands = kira_commands + sinkudp.get_messages()
		if test["expect_tcp"]:
			kira_commands = kira_commands + sinktcp.get_messages()
		print("Received KIRA commands:", pp.pformat(kira_commands))
		print("Expected KIRA commands:", pp.pformat(test["expected_kira_commands"]))

		pass_test = (kira_commands == test["expected_kira_commands"])

	if pass_test:
		print("Test passed")
	else:
		print("TEST FAILED")


def run_tests():
	set_test_env()
	sinkudp = testip(60000, "udp")
	sinktcp = testip(60000, "tcp")
	sinkudp.spawn()
	sinktcp.spawn()

	try:
		for test in testCases:
			run_test(test, sinkudp, sinktcp)

	except KeyboardInterrupt:
		print("Interrupted")

	sinkudp.terminate()
	sinktcp.terminate()


if __name__ == '__main__':
	run_tests()



