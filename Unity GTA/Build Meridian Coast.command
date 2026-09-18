#!/bin/bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")" && pwd)"
version="$(sed -n 's/^m_EditorVersion: //p' "$project_dir/ProjectSettings/ProjectVersion.txt" | tr -d '\r')"
editor="${UNITY_EDITOR:-/Applications/Unity/Hub/Editor/$version/Unity.app/Contents/MacOS/Unity}"
if [[ ! -x "$editor" ]]; then
  printf 'Install Unity %s and macOS Build Support in Unity Hub.\n' "$version"
  read -r -p 'Press Enter to close.'
  exit 1
fi
mkdir -p "$project_dir/.astra-run"
printf 'Building macOS Universal. Close Unity Editor before running this script.\n'
"$editor" -batchmode -quit -buildTarget OSXUniversal -projectPath "$project_dir" -executeMethod Meridian.Editor.ReleaseBuilder.MacOS -logFile "$project_dir/.astra-run/build-macOS.log"
open "$project_dir/Builds/macOS"
