# KeeneIRAlexaSkill

Overview
========

This project implements an Alexa skill to control home entertainment systems via [Keene KIRA IR modules](https://www.keene.co.uk/keene-ir-anywhere-ir-over-ip-modules-pair.html).

Specifically, it provides a lambda function implementing the Smart Home Skill API.

In time, the intent is to implement a publishable skill which 
- reads the IR codes from a [public IR database](https://github.com/probonopd/irdb)
- provides a GUI to let users define their devices and activities (see below).

For now, both are hard-coded, with the IR codes manually captured.

Devices vs. activities
======================

The [Smart Home Skills (SHS) API](https://developer.amazon.com/docs/smarthome/build-smart-home-skills-for-entertainment-devices.html) is based on devices being controlled individually.  (There is a concept of a group of devices, but those are identical devices such as a set of lights in the same room.)  This is fine if you literally just have a TV, but if you have multiple components linked together and you want to control them all together, it is bad.  For example, if you have a set-top box (STB) linked to a TV, you would have to separately tell Alexa to first turn on the TV, then set the TV to the appropriate input, then turn on the STB, and you have to remember to tell Alexa to change the volume on the TV but the channel on the STB.  Not very user friendly.

While this skill does expose individual devices in this way, it also
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

The current implementation is stateless.  That is only a problem for those annoying devices that only implement power toggle commands, not power on/power off: we do not remember what state the devices are in.  As a workaround, users can ask Alexa to turn on the individual devices if they've been turned off, or just repeat the command (though the latter doesn't work if it has to turn on multiple devices which just support a power toggle and have got out of sequence).

Authentication
==============

TBD - ideally use OAuth2 with LWA to distinguish users and read target configuration.