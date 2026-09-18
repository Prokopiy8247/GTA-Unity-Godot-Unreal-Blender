#!/bin/bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_FILE="$PROJECT_ROOT/Unreal_GTA.uproject"
MODE="${1:-play}"

fail() { printf '\n%s\nRead START_HERE.md for setup and troubleshooting.\n' "$*" >&2; exit 1; }
find_app() {
    if [[ -d "$PROJECT_ROOT/Packaged/Mac" ]]; then
        /usr/bin/find "$PROJECT_ROOT/Packaged/Mac" -type d -name 'Unreal_GTA*.app' -prune -print | /usr/bin/head -n 1
    fi
}
if [[ "$MODE" != play && "$MODE" != build && "$MODE" != editor && "$MODE" != check ]]; then fail "Unknown mode: $MODE"; fi
GAME_APP="$(find_app)"
if [[ "$MODE" == play && -n "$GAME_APP" ]]; then
    /usr/bin/open "$GAME_APP" --args -windowed -ResX=1600 -ResY=900
    exit 0
fi
ENGINE=""
for candidate in "${UE_ROOT:-}" "/Users/Shared/Epic Games/UE_5.8" "/Users/Shared/UnrealEngine/UE_5.8" "/Applications/Epic Games/UE_5.8"; do
    [[ -n "$candidate" ]] || continue
    version="$candidate/Engine/Build/Build.version"
    if [[ -f "$version" && -f "$candidate/Engine/Build/BatchFiles/RunUAT.sh" ]] &&
       /usr/bin/grep -Eq '"MajorVersion"[[:space:]]*:[[:space:]]*5[[:space:]]*,' "$version" &&
       /usr/bin/grep -Eq '"MinorVersion"[[:space:]]*:[[:space:]]*8[[:space:]]*,' "$version"; then
        ENGINE="$candidate"; break
    fi
done
[[ -n "$ENGINE" ]] || fail "Unreal Engine 5.8 was not found. Install UE 5.8.2 using Epic Games Launcher, or set UE_ROOT for a custom installation."
[[ "$(/usr/bin/uname -m)" == arm64 ]] || fail "This launch script targets Apple Silicon Macs. Intel Macs have not been validated."
/usr/bin/xcodebuild -version >/dev/null 2>&1 || fail "Install full Xcode, launch it once and complete its setup."
/usr/bin/xcrun --find clang >/dev/null 2>&1 || fail "Xcode command-line tools are not configured."
if /usr/bin/xcodebuild -version | /usr/bin/grep -q '^Xcode 26\.4'; then
    fail "Epic lists Xcode 26.4 as incompatible with UE 5.8. Use a compatible version (recommended: 26.1.1)."
fi
if [[ "$MODE" == check ]]; then printf 'UE 5.8 and Xcode found. Native Mac execution still requires a build.\n'; exit 0; fi
if [[ "$MODE" == editor ]]; then
    /bin/bash "$ENGINE/Engine/Build/BatchFiles/Mac/Build.sh" Unreal_GTAEditor Mac Development "-Project=$PROJECT_FILE" -WaitMutex
    /usr/bin/open "$ENGINE/Engine/Binaries/Mac/UnrealEditor.app" --args "$PROJECT_FILE"
    exit 0
fi
printf 'Building Port Meridian for this Mac. The first build can take a long time.\n'
/bin/bash "$ENGINE/Engine/Build/BatchFiles/RunUAT.sh" BuildCookRun "-project=$PROJECT_FILE" -noP4 -platform=Mac -architecture=arm64 -clientconfig=Shipping -build -cook -cookall -stage -pak -compressed -nodebuginfo -archive "-archivedirectory=$PROJECT_ROOT/Packaged" -unattended -utf8output
GAME_APP="$(find_app)"
[[ -n "$GAME_APP" ]] || fail "Build finished but Unreal_GTA.app was not found in Packaged/Mac."
printf 'Ready: %s\n' "$GAME_APP"
if [[ "$MODE" == play ]]; then /usr/bin/open "$GAME_APP" --args -windowed -ResX=1600 -ResY=900; fi
