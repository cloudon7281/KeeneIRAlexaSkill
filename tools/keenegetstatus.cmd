@echo off
if exist kira.log del kira.log
python %KIRAPATH%\KeeneIRAlexa.py -u %KIRAUSER% -s get
