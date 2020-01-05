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

# This file implements IO to the Keene IR devices, sending a given message
# to a given target and port.

# XXX We should check for a return of 'OK'.

import socket
import time

from logutilities import log_info, log_debug, log_error

def SendUDP(target, mesg, repeat, repeatDelay):
    log_info("Send UDP to %s with repeat %d, delay %.3f; message %s", target, repeat, repeatDelay, mesg)

    host, port = target.split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', int(port)))
    for i in range(repeat+1):
        log_debug("Sending %s", mesg.encode('utf-8'))
        sock.sendto(mesg.encode('utf-8'), (host, int(port)))
        if i < repeat:
            time.sleep(repeatDelay)
    sock.close()


def SendTCP(target, mesg, repeat, repeatDelay):
    log_info("Send TCP to %s with repeat %d, delay %.3f; message %s", target, repeat, repeatDelay, mesg)

    host, port = target.split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    log_debug("Connecting to remote socket on %s:%s", host, port)
    sock.connect((host, int(port)))
    log_debug("Connected")

    for i in range(repeat+1):
        log_debug("Sending %s", mesg.encode('utf-8'))

        totalsent = 0
        while totalsent < len(mesg):
            sent = sock.send(mesg[totalsent:].encode('utf-8'))
            log_debug("Sent %d bytes", sent)
            if sent == 0:
                log_error("Couldn't send TCP data to %s", target)
            totalsent = totalsent + sent

        if i < repeat:
            time.sleep(repeatDelay)

    sock.shutdown(socket.SHUT_WR)
    sock.close()
    log_debug("Closed socket")
