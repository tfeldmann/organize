#!/bin/sh
# Runs the Swift tests. Works with the Command Line Tools alone (no Xcode needed).
set -eu
cd "$(dirname "$0")/OrganizeBar"
DEV=/Library/Developer/CommandLineTools/Library/Developer
# Xcode finds its test libraries itself, the Command Line Tools need help
case "$(xcode-select -p)" in
*CommandLineTools*) USE_CLT=1 ;;
*) USE_CLT=0 ;;
esac
if [ "$USE_CLT" = 1 ] && [ -d "$DEV/Frameworks/Testing.framework" ]; then
    set -- -Xswiftc -F -Xswiftc "$DEV/Frameworks" \
        -Xlinker -F -Xlinker "$DEV/Frameworks" \
        -Xlinker -rpath -Xlinker "$DEV/Frameworks" \
        -Xlinker -rpath -Xlinker "$DEV/usr/lib"
fi
swift test "$@"
