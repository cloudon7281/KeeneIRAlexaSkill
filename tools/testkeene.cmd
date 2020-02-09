@echo off
call keeneiralexa.cmd -m Pioneer -d PDP-LX508D -i PowerToggle -r 4 send -t 192.168.5.229:65432 
timeout 1
call keeneiralexa.cmd -m Virgin -d Hub-3 -i PowerToggle -r 2 send -t 192.168.5.229:65432 
timeout 1
call keeneiralexa.cmd -m Arcam -d AVR360 -i InputSAT -r 2 send -t 192.168.5.164:65432 
