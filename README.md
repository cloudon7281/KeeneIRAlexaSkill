# KeeneIRAlexaSkill

Overview
========

This project implements an Alexa skill to control home entertainment systems via [Keene KIRA IR modules](https://www.keene.co.uk/keene-ir-anywhere-ir-over-ip-modules-pair.html).

Specifically, it provides:
- a lambda function implementing the Smart Home Skill API
- a CLI to allow users to
    - upload details of their set up
    - upload IR codes for their devices captured using the [Keene utilities](https://www.keene.co.uk/pages/downloads/dnl_files/IRAnywhere.zip)
    - send test commands to their devices.

User and device details are stored in S3.

Devices vs. activities
======================

The [Smart Home Skills (SHS) API](https://developer.amazon.com/docs/smarthome/build-smart-home-skills-for-entertainment-devices.html) is based on devices being controlled individually.  (There is a concept of a group of devices, but those are identical devices such as a set of lights in the same room.)  This is fine if you literally just have a TV, but if you have multiple components linked together and you want to control them all together, it is bad.  For example, if you have a set-top box (STB) linked to a TV, you would have to separately tell Alexa to first turn on the TV, then set the TV to the appropriate input, then turn on the STB, and you have to remember to tell Alexa to change the volume on the TV but the channel on the STB.  Not very user friendly.

Instead, this skill
- aggregates devices together into activities ("Watch a Blu Ray")
- exposes those activities *as individual devices* across the SHS API
- maps directives on those activities to a series of individual commands on the underlying devices.

So for example, "Alexa, turn on the Blu Ray" would trigger a TurnOn directive to the skill, which might map that to individual IR commands to
- turn on the TV
- select the appropriate input channel on the TV
- turn on a Blu Ray player
- turn on an amp
- set the amp to the appropriate channel.

Outputs
=======

The lambda responds to incoming directives by sending a sequence of KIRA commands over UDP to a configured target address for a given user.  The target address should typically be a dynamic DNS name, with the user's home router or firewall configured to forward UDP packets on the appropriate port (usually 65432) to the appropriate KIRA target device, which should be configured to have a static/permanently allocated IP address on the home network.

A possible future is to implement support for BearerTokenWithPartition to allow for multiple rooms in the same house.

Reporting
=========

TBD - currently all devices/activities have proactivelyReported and retrievable set to False.

State
=====

All user and device state is held in S3.
- Global information about devices (their capabilities and IR codes) are stored in one bucket with key names based on manufacturer and device.
- For users, we store 3 types of information.
    - Information on which devices they have and how they are connected (e.g. a CD player is connected to a receiver on input 'CD').
    - Current device state i.e. whether a user's devices are currently switched on or off.
    - The "model" for that user i.e. a lookup table for how the lambda should respond to any incoming directive.  The model is generated whenever a user "discovers" their devices via the Alexa app.  (It also resets the stored device state to "all off".)

 Storing current device state is required for two reasons.
 - Some devices only implement power toggle commands, not power on/power off.  So we need to avoid successive commands to "turn on X" sending PowerToggle twice and and turning off X.
 - If a user issues "turn on X" then "turn on Y" then to handle the latter we should turn off any devices involved in X but not Y - so we need to know the current state.

Authentication
==============

Commands are authenticated via OAuth2 with LWA.

Usage
=====

Installing the lambda
---------------------

TBD.

The CLI
-------

A CLI is provided to allow users to upload (and check) details of both their set up and details of devices, such as the IR codes, and to test send IR commands to particular addresses.

Run keenealexair for more details.

xxx to flesh out