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
import logging
import time
import pprint
import json
import testCases

from testKIRA import testKIRA
from AWSlambda import lambda_handler
from testCases import testCases

# Logger boilerplate
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('kira.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

pp = pprint.PrettyPrinter(indent=2, width = 200)

def set_test_env():
	os.environ['TEST_USER'] = 'testuser'
	os.environ['TEST_TOKEN'] = 'token'
	os.environ['USE_STATIC_FILES'] = 'Y'


def run_test(test, sink):
	print("\nRunning test case:", test["title"])
	pass_test = True

	response = lambda_handler(test["directive"], "")

	if test["expect_kira_commands"]:
		kira_commands = sink.get_messages()
		print("Received KIRA commands:", pp.pformat(kira_commands))
		print("Expected KIRA commands:", pp.pformat(test["expected_kira_commands"]))

		pass_test = (kira_commands == test["expected_kira_commands"])

	if pass_test:
		print("Test passed")
	else:
		print("TEST FAILED")


def run_tests():
	set_test_env()
	sink = testKIRA(60000)
	sink.spawn()

	for test in testCases:
		run_test(test, sink)

	sink.terminate()


if __name__ == '__main__':
	run_tests()



