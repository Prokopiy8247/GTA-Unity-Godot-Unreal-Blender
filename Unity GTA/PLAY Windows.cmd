@echo off
if exist "%~dp0Builds\Windows\MeridianCoast.exe" (
  start "" "%~dp0Builds\Windows\MeridianCoast.exe" -screen-fullscreen 1
) else (
  start "" "https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/unity-v1.0.0"
)
