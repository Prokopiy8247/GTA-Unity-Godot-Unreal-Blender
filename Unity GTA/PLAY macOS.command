#!/bin/bash
set -e
project_dir="$(cd "$(dirname "$0")" && pwd)"
game="$project_dir/Builds/macOS/Meridian Coast.app"
if [[ -d "$game" ]]; then
  open "$game"
else
  open "https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/unity-v1.0.0"
fi
