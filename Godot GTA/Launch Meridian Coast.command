#!/bin/bash
set -e
cd "$(dirname "$0")"
engine="${GODOT_EXECUTABLE:-}"
if [ -z "$engine" ]; then
  for candidate in "./Godot.app/Contents/MacOS/Godot" "/Applications/Godot.app/Contents/MacOS/Godot" "$HOME/Applications/Godot.app/Contents/MacOS/Godot"; do
    if [ -x "$candidate" ]; then engine="$candidate"; break; fi
  done
fi
if [ -z "$engine" ]; then engine="$(command -v godot || command -v godot4 || true)"; fi
if [ -n "$engine" ] && [ -x "$engine" ]; then
  exec "$engine" --path "$PWD" "$@"
fi
printf '%s\n' "Godot was not found." "For the ready-to-play Mac app, download a release:" "https://github.com/Prokopiy8247/GTA-Unity-Godot-Unreal-Blender/releases/tag/godot-v0.1.0" "For source code, install Godot 4.7.2 Standard and import project.godot." "See PLAY_GUIDE.md."
read -r -p "Press Return to close..."
