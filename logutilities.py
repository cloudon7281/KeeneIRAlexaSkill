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
import inspect
import os

logger = logging.getLogger()
if 'LOG_LOCAL' in os.environ:
	fh = logging.FileHandler('kira.log')

log_level = logging.INFO
if 'LOG_LEVEL' in os.environ:
	if os.environ['LOG_LEVEL'] == "DEBUG":
		log_level = logging.DEBUG
logger.setLevel(log_level)

if 'LOG_LOCAL' in os.environ:
	fh.setLevel(log_level)
	formatter = logging.Formatter('%(asctime)s %(levelname)5s %(message)s', "%Y-%m-%d %H:%M:%S")
	fh.setFormatter(formatter)
	logger.addHandler(fh)

def log_info(msg, *arg):
    func = inspect.currentframe().f_back.f_code
    logger.info("%27s %15s %3s " + msg, func.co_name, func.co_filename.split('\\')[-1], func.co_firstlineno, *arg)

def log_debug(msg, *arg):
    func = inspect.currentframe().f_back.f_code
    logger.debug("%27s %15s %3s " + msg, func.co_name, func.co_filename.split('\\')[-1], func.co_firstlineno, *arg)

def log_error(msg, *arg):
    func = inspect.currentframe().f_back.f_code
    logger.error("%27s %15s %3s " + msg, func.co_name, func.co_filename.split('\\')[-1], func.co_firstlineno, *arg)
