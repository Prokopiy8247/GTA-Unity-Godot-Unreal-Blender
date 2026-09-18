@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Tools\Launch_Windows.ps1" -Mode Editor
if errorlevel 1 pause
