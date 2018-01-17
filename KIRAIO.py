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

def SendToKIRA(host, port, mesg, repeat, repeatDelay):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    for i in range(repeat+1):
        logger.info("Sending event to target %s on port %d; event = %s", host, port, mesg)
        sock.sendto(mesg.encode('utf-8'), (host, port))
        if i == repeat:
            time.sleep(repeatDelay)
    sock.close()

