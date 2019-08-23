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

import multiprocessing
import socket
import pprint

from logutilities import log_info, log_debug

pp = pprint.PrettyPrinter(indent=2, width = 200)

class testip:
	# This class implements a background process simulating a KIRA endpoint.

	def __init__(self, port, protocol):
		self.port = port
		self.protocol = protocol
		self.q = multiprocessing.Queue()
		self.jobs = []

	def spawn(self):
		p = multiprocessing.Process(target=listener, args = (self.q, self.port, self.protocol))
		self.jobs.append(p)
		p.daemon = True
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


def listener(q, port, protocol):
	# Signal that we have spawned then loop until terminated, pulling messages
	# of the UDP port and putting them back onto the queue.

	q.put("Started")
	
	log_debug("Listen on port %d, protocol %s", port, protocol)

	if protocol == "udp":
		sock_type = socket.SOCK_DGRAM
	else:
		sock_type = socket.SOCK_STREAM

	sock = socket.socket(socket.AF_INET, sock_type)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('127.0.0.1', int(port)))

	if protocol == "tcp":
		log_debug("Set socket to listen")
		sock.listen(1)
		(sock, address) = sock.accept()
		log_debug("Accepted incoming connection from address %s on protocol %s", pp.pformat(address), protocol)

	while(True):
		log_debug("Waiting for data on protocol %s", protocol)
		(message, address) = sock.recvfrom(1024)
		log_debug("Received data %s from address %s on protocol %s", message, pp.pformat(address), protocol)
		q.put(message)


