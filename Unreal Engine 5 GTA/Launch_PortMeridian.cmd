@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Tools\Launch_Windows.ps1" -Mode Play
if errorlevel 1 pause
