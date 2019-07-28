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

# This file takes a definition of a user's devices and from them constructs a
# set of activities.

import pprint

from logutilities import log_info, log_debug
from alexaSchema import CAPABILITY_DISCOVERY_RESPONSES, CAPABILITY_DIRECTIVES_TO_COMMANDS
from utilities import verify_devices, find_target, get_connected_device, get_repeats, find_user_device_in_DB, find_device_from_friendly_name
from endpoint import construct_endpoint_chain
from power import construct_power_map
from command_sequences import construct_command_sequence

pp = pprint.PrettyPrinter(indent=2, width = 200)


def model_user_and_devices(user_details, device_database):
	# Here we model the user's devices and activities.
	# 
	# It is important to understand:
	# - the inputs to this model
	# - the Alexa data model
	# - how we map user devices -> Alexa objects
	# - why we have to treat power differently
	# - the set of models we return from here.
	#
	# Inputs to this model
	# --------------------
	# 
	# There are two inputs to this modelling exercise.
	#
	# 1. A global database of devices.  This is a dict, structured by
	# manufacturer then device, which for each device contains
	# - what real-world roles it can play (e.g. audio source, or audio + video)
	# - which Alexa capabilities it can support (see below)
	# - a map of IR command names -> IR codes.
	# This database is stored in S3.
	#
	# 2. A user's details.  This has two key pieces of info.
	# - The set of KIRA targets to send commands to (IP addresses + ports); we
	# support multiple devices per-user).
	# - A list of the user's devices, including what the user wants to call 
	# them, how they are linked together (e.g. what TV input a Blu-ray player
	#  is connected to) and how they are grouped into rooms.
	# User details are stored in S3.
	#
	# Alexa data model
	# ----------------
	# 
	# The key Alexa concepts are endpoints, capabilities and directives.
	#
	# Endpoints are things like TV or Blu-ray.
	# 
	# Capabilities (aka interfaces) are groups of related features such as a 
	# ChannelController or PowerController.  We model each physical
	# device as supporting a set of capabilities; the capabilities we
	# return for an endpoint is the union of all capabilities supported
	# by the devices being aggregated into that endpoint.
	#
	# Directives are the individual commands within each capability e.g.
	# Play or AdjustVolume.
	#
	# Mapping user devices -> Alexa data model
	# ----------------------------------------
	#
	# Alexa "expects" endpoints to be 1-1 with physical devices, but instead
	# we aggregate multiple physical devices into a single endpoint so that 
	# they can all be controlled simultaneously.  So our model is that any 
	# devices which the user has which are audio or audio+video sources are
	# mapped to an endpoint, and we then follow the chain of connectivity
	# from those sources to create a list of each device included in that
	# endpoint.
	#
	# We then model the capabilities supported by the endpoint as being the 
	# union of the capabilities supported by each device included in the 
	# endpoint.
	#
	# For each directive of each capability, we then create a list of the 
	# specific commands we must send to implement that directive on each of
	# the devices supporting that capability (typically, there will only be
	# one device in the chain doing so e.g. only one device supporting 
	# StepSpeaker for volume control).  We do this via a dict representing the
	# Alexa schema; for each directive of each capability it has a list of
	# command names to search for in the device database for the appropriate
	# devices e.g. for the AdjustVolume directive of the StepSpeaker capability
	# we search for commands called VolumeUp and VolumeDown.
	#
	# The commands we extract may be simple unconditional "send this IR seq"
	# commands, or more complex commands that are parameterised by values
	# in the directive e.g. the ChangeChannel directive of the
	# ChannelController capability extracts the IR sequences corresponding to 
	# digits 0-9; the value channel passed in the payload of the directive
	# then determines which IR sequences are sent.
	#
	# Why power is different
	# ----------------------
	#
	# The scheme outlined above works well for everything apart from power
	# commands, for two reasons.
	#
	# - We potentially have to send commands to devices *not* in the endpoint
	# the user command nominally addresses. For example, if the user issues
	# "Turn on TV" then "Turn on CD", then (assuming the CD is being played
	# back through speakers not the TV) we should turn off the TV as part of
	# handling the latter command.  That means we have to have awareness of
	# the power state of all devices.
	#
	# - Some evil device manufacturers just support a "power toggle" IR command
	# rather than separate "power on" and "power off".  This makes awareness
	# of state essential, as the commands are not idempotent e.g. if we simply
	# mapped "Turn on TV" to sending "power toggle" to the TV, then if the user
	# issued successive "Turn on TV" commands, the second one would turn *off*
	# the TV.
	#
	# Models
	# ------
	#
	# Given the above, we model and return the following.
	#
	# discovery_response
	#
	# This is a dict corresponding to the JSON structure to return to Alexa in
	# response to Discovery commands, and includes the full set of endpoints 
	# and their supported capabilities.
	#
	# command_sequence
	#
	# This is a dict indexed by endpoint then capability then directive, 
	# containing a structure corresponding to the set of IR commands to send
	# for that directive of that capability for that endpoint.  The lambda 
	# handler then simply sends that sequence of IR commands, parameterised as
	# necessary by values in the directive payload.
	#
	# device_power_map
	#
	# This is a dict indexed by device which includes info on
	# - which endpoints the device participates in
	# - whether it is a "toggle" or "on/off" device
	# - the set of IR commands corresponding to power toggle/on/off commands.
	# The lambda handler then uses this whenever it receives a directive for
	# the PowerController capability.  In conjunction with the device state,
	# it works out which devices need to be turned off.  Power manipulation
	# (and associated setting of inputs) for devices in the endpoint is handled
	# by the normal command sequence processing.
	log_info("Auto-generating model")

	# Extract the lists of targets and devices from the user details, and check
	# they're not duff.
	user_targets = user_details['targets']
	user_devices = user_details['devices']

	verify_devices(user_devices, device_database)
	
	discovery_response = []
	command_sequences = {}
	
	# We can't construct the full power map until we have the list of endpoints
	# but we can extract whether each device is a toggle or on/off plus the 
	# list of its IR commands.
	device_power_map = construct_power_map(user_details, device_database)
	
	# Now construct the list of endpoints, and use to flesh out the discovery
	# response, command sequence and power map.
	for this_device in user_devices:
		log_debug("User has device %s", this_device['friendly_name'])	

		device_details = find_user_device_in_DB(this_device, device_database)

		is_video_source = ('AV_source' in device_details['roles'])
		is_audio_source = ('A_source' in device_details['roles'])
		is_source = (is_video_source or is_audio_source)

		if is_source:
			log_debug("It's a source; map it to an endpoint")

			# We now need to find the chain of devices in this endpoint chain, 
			# plus the union of their capabilities.
			endpoint, capabilities, chain = construct_endpoint_chain(user_details, this_device, device_database)
			endpoint_id = endpoint['endpointId']

			for link in chain:
				log_debug("Marking device %s involved in endpoint %s", link['friendly_name'], endpoint_id)
				device_power_map[link['friendly_name']]['endpoints'][endpoint_id] = True
			
			# Now go through the capabilities, and as well as constructing the
			# appropriate discovery response construct the set of commands for
			# each primitive.
			command_sequences[endpoint_id] = {}

			for capability in capabilities:
				log_debug("Add capability %s to endpoint response", capability)

				# Append the section of the discovery response for this
				# capability for this endpoint.  This is the set of directives
				# we support for this capability, and is taken direct from the
				# Alexa schema.
				endpoint['capabilities'].append(CAPABILITY_DISCOVERY_RESPONSES[capability])

				# Now construct the set of IR commands for each directive of
				# this capability.
				# The schema includes the set of command names to look for,
				# for each directive of each capability.
				command_sequences[endpoint_id][capability] = {}
				directives_to_commands = CAPABILITY_DIRECTIVES_TO_COMMANDS[capability]

				for directive in directives_to_commands:
					specific_commands = construct_command_sequence(chain,
																   capability,
																   directives_to_commands[directive])
					command_sequences[endpoint_id][capability][directive] = specific_commands

			# Add the constructed endpoint info to what we return
			discovery_response.append(endpoint)

	log_debug("Device power map = %s", pp.pformat(device_power_map))

	model = {
				'discovery_response': discovery_response,
				'command_sequences': command_sequences,
				'device_power_map': device_power_map
			}

	return model


