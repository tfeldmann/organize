#!/bin/sh
# Builds the Organize menu bar app and installs it to ~/Applications.
#
#   macos/build-app.sh [config]     (config: the organize config to show, default: downloads)
#
# The app runs the Python engine of this project folder, so build it again if
# you move the project.
set -eu

CONFIG="${1:-downloads}"
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT="$(cd "$HERE/.." && pwd)"
APP="$HOME/Applications/Organize.app"

xml_escape() {
    printf '%s' "$1" | sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'
}

cd "$HERE/OrganizeBar"
swift build -c release
BIN="$(swift build -c release --show-bin-path)/OrganizeBar"

# quit a running copy before replacing it
osascript -e 'quit app "Organize"' 2>/dev/null || true

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$BIN" "$APP/Contents/MacOS/Organize"
cat >"$APP/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Organize</string>
    <key>CFBundleDisplayName</key>
    <string>Organize</string>
    <key>CFBundleIdentifier</key>
    <string>local.organize.bar</string>
    <key>CFBundleExecutable</key>
    <string>Organize</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>LSUIElement</key>
    <true/>
    <key>OrganizeProjectPath</key>
    <string>$(xml_escape "$PROJECT")</string>
    <key>OrganizeConfig</key>
    <string>$(xml_escape "$CONFIG")</string>
</dict>
</plist>
EOF
codesign --force --sign - "$APP"
echo "Installed $APP"
open "$APP"
