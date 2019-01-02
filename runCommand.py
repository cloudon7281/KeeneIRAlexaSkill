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


import time
import pprint

from logutilities import log_info, log_debug
from KIRAIO import SendToKIRA

pp = pprint.PrettyPrinter(indent=2, width = 200)

DELAY = 0.02


def set_power_states(directive, endpoint, device_state, device_power_map, pause, payload):
    # Set the power state correctly for all devices, taking into account
    # current state.
    log_debug("Set power state for all devices given directive %s for endpoint %s", directive, endpoint)
    log_debug("Current device states: %s", pp.pformat(device_state))

    for device in device_power_map:
        # The only circumstances in which a device is desired to be on is if
        # it's invovled in the endpoint and we're turning it on; in all other
        # cases (invovled but turning off, or not involved) we want it off.
        this_device_map = device_power_map[device]
        desired_on = (endpoint in this_device_map['endpoints']) and (directive == "TurnOn")
        currently_on = device_state[device]

        log_debug("Device %s: desired on %s; currently on %s", device, pp.pformat(desired_on), pp.pformat(currently_on))

        send_command = None

        if desired_on and not currently_on:
            log_debug("Currently off; should be on")
            send_command = 'TurnOn'

        if not desired_on and currently_on:
            log_debug("Currently on; should be off")
            send_command = 'TurnOff'

        if send_command != None:
            for command_tuple in this_device_map['commands'][send_command]:
                for verb in command_tuple:
                    log_debug("Verb to run: %s", verb)
                    run_command(verb, command_tuple[verb], pause, payload)

        device_state[device] = desired_on
        log_debug("State of device %s now %s", device, desired_on)

    status_changed = (send_command != None)
    
    return device_state, status_changed

def run_command(verb, command_tuple, pause, payload):
	# This function executes a specific command, one of:
	#
	#   SingleIRCommand     - send a single KIRA command; value is struct with 
	#                         IR sequence as value
	#   StepIRCommands      - send N * up/down KIRA commands; value is a struct
	#                         with +ve & -ve IR commands
	#   DigitsIRCommands    - send sequence of KIRA commands corresponding to 
	#                         digits of number in the payload; value is a struct
	#                         with IR commands for each decimal digit
	#   Pause               - pause for N seconds before sending next command;
	#                         time to wait is the value
    if verb == 'SingleIRCommand':
        # Send to KIRA the single command specified.
        KIRA_string = command_tuple['single']['KIRA']
        repeats = command_tuple['single']['repeats']
        target = command_tuple['single']['target']
        SendToKIRA(target, KIRA_string, repeats, DELAY)

    elif verb == 'StepIRCommands':
        # In this case we need to extract the value N in the payload
        # then send either the +ve or -ve command N times.
        # XXX need to generalise payload location from AdjustVolume
        key = command_tuple['key']
        steps = payload[key]
        log_debug("Adjustment to make: %d", steps)

        if steps > 0:
            index = '+ve'
        else:
            index = '-ve'
        
        KIRA_string = command_tuple[index]['KIRA']
        target = command_tuple[index]['target']
        repeats = command_tuple[index]['repeats']
        
        for n in range(0, abs(steps)):
            SendToKIRA(target, KIRA_string, repeats, DELAY)
            time.sleep(pause)

    elif verb == 'DigitsIRCommands':
        # In this case we need to extract a decimal number in the 
        # payload then send the sequence of IR commands corresponding
        # to its digits.
        # XXX need to generalise payload location from ChangeChannel
        number = -1
        for key1 in [ 'channel', 'channelMetadata']:
            if key1 in payload:
                for key2 in [ 'number', 'name']:
                    if key2 in payload[key1]:
                        if key2 == 'number':
                            number = payload[key1][key2]
                        else:
                            name = payload[key1][key2]
                            number = str(command_tuple['NameMap'][name])
                            log_debug("Channel name is %s; number is %s", name, number)

        if number == -1:
            log_error("Can't extract channel number from directive!")
        else:
            log_debug("Number to send: %s", number)

            for digit in number:
                KIRA_string = command_tuple[digit]['KIRA']
                target = command_tuple[digit]['target']
                repeats = command_tuple[digit]['repeats']
                SendToKIRA(target, KIRA_string, repeats, DELAY)
                time.sleep(pause)

    elif verb == 'Pause':
        # Simply pause the appropriate period of time.
        time.sleep(command_tuple)

    return