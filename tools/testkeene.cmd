@echo off
set TARGET=%1
if [%TARGET%]==[A] echo Testing A & call tools\keeneiralexa.cmd -m Oppo -d BDP-83 -i Eject -r 0 send -t targeta:65432 
if [%TARGET%]==[B] echo Testing B & call tools\keeneiralexa.cmd -m Virgin -d Hub-3 -i Info -r 2 send -t targetb:65432 
if [%TARGET%]==[C] echo Testing C & call tools\keeneiralexa.cmd -m Arcam -d AVR360 -i Mute -r 0 send -t targetc:65432 
