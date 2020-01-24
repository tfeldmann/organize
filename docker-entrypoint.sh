#!/bin/sh

set -e
. /app/bin/activate

if [ -n "$DELAY" ] && [ "$DELAY" -eq "$DELAY" ] 2>/dev/null; then
    while [ 1 ]
    do
        organize --config-file=/app/config.yaml "$@"
        sleep $DELAY
    done
else
    exec organize --config-file=/app/config.yaml "$@"
fi
