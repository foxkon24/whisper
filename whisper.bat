@echo off

rem @if not "%~0"=="%~dp0.\%~nx0" start /min cmd /c,"%~dp0.\%~nx0" %* & goto :eof

cd C:\root\utlity\apps\whisper

cd %~dp0

python main.py

pause

