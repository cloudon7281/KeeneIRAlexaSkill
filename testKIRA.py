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

import logging, pprint
import multiprocessing
import socket

logger = logging.getLogger()
pp = pprint.PrettyPrinter(indent=2, width = 200)

class testKIRA:
	# This class implements a background process simulating a KIRA endpoint.

	def __init__(self, port):
		self.port = port
		self.q = multiprocessing.Queue()
		self.jobs = []

	def spawn(self):
		p = multiprocessing.Process(target=listener, args = (self.q, self.port))
		self.jobs.append(p)
		p.start()

		# Wait till started
		message = self.q.get()
		print(message)

	def terminate(self):
		for p in self.jobs:
			p.terminate()

	def get_messages(self):
		kira_commands = []
		empty = False
		while not empty:
			try:
				kira_command = self.q.get(timeout = 2).decode()
				kira_commands.append(kira_command)
			except:
				empty = True
		return kira_commands


def listener(q, port):
	# Signal that we have spawned then loop until terminated, pulling messages
	# of the UDP port and putting them back onto the queue.

	q.put("Started")
	
	logger.debug("Listen on port %d", port)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('127.0.0.1', int(port)))

	while(True):
		(message, address) = sock.recvfrom(1024)
		q.put(message)
