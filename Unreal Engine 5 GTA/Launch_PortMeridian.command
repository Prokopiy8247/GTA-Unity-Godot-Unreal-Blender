#!/bin/bash
cd "$(dirname "$0")" || exit 1
/bin/bash Tools/launch_macos.sh "${1:-play}"
result=$?
if [[ $result -ne 0 ]]; then
    printf '\nPress Return to close this window.\n'
    read -r _
fi
exit "$result"
