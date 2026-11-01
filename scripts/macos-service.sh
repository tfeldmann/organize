#!/bin/sh
# Runs `organize watch <config>` in the background on macOS, started at login.
#
#   scripts/macos-service.sh install [config]   install and start (config: downloads)
#   scripts/macos-service.sh uninstall          stop and remove
#   scripts/macos-service.sh stop               pause until `start` or the next login
#   scripts/macos-service.sh start              resume after `stop`
#   scripts/macos-service.sh status             show whether it is running
#   scripts/macos-service.sh logs               follow the log
#
# API keys are read from the `.env` file in the project folder.
set -eu

LABEL="local.organize.watch"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs/organize"
LOG="$LOG_DIR/watch.log"
PROJECT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$PROJECT/.venv/bin/python"
DOMAIN="gui/$(id -u)"

xml_escape() {
    printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'
}

install() {
    config="${1:-downloads}"
    if [ ! -x "$PYTHON" ]; then
        echo "No virtualenv found. Run 'uv sync' in $PROJECT first." >&2
        exit 1
    fi
    "$PYTHON" -m organize check "$config" >/dev/null
    mkdir -p "$LOG_DIR" "$(dirname "$PLIST")"
    cat >"$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(xml_escape "$PYTHON")</string>
        <string>-m</string>
        <string>organize</string>
        <string>watch</string>
        <string>$(xml_escape "$config")</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(xml_escape "$PROJECT")</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>PYTHONUNBUFFERED</key>
        <string>1</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>
    <key>ThrottleInterval</key>
    <integer>30</integer>
    <key>ProcessType</key>
    <string>Background</string>
    <key>StandardOutPath</key>
    <string>$(xml_escape "$LOG")</string>
    <key>StandardErrorPath</key>
    <string>$(xml_escape "$LOG")</string>
</dict>
</plist>
EOF
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    launchctl bootstrap "$DOMAIN" "$PLIST"
    echo "Installed. Watching with config \"$config\", log: $LOG"
}

uninstall() {
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "Uninstalled."
}

start() {
    if [ ! -f "$PLIST" ]; then
        echo "Not installed. Use: $0 install [config]" >&2
        exit 1
    fi
    launchctl bootstrap "$DOMAIN" "$PLIST" 2>/dev/null || launchctl kickstart "$DOMAIN/$LABEL"
    echo "Started."
}

stop() {
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    echo "Stopped."
}

status() {
    if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
        launchctl print "$DOMAIN/$LABEL" | grep -E '^\s+(state|pid|last exit code) ='
    elif [ -f "$PLIST" ]; then
        echo "Stopped."
    else
        echo "Not installed."
    fi
}

case "${1:-}" in
install) install "${2:-}" ;;
uninstall) uninstall ;;
start) start ;;
stop) stop ;;
status) status ;;
logs) tail -f "$LOG" ;;
*)
    sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
