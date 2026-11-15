#!/bin/zsh
# delivery/uninstall.sh - nettoyage complet de la machine de lab
setopt NULL_GLOB
launchctl unload ~/Library/LaunchAgents/com.rick.*.plist 2>/dev/null
launchctl unload ~/Library/LaunchAgents/com.apple.rick*.plist 2>/dev/null
rm -f ~/Library/LaunchAgents/com.rick.*.plist
rm -f ~/Library/LaunchAgents/com.apple.rick*.plist
rm -rf "$HOME/Library/Application Support/RickPortal" "$HOME/Library/Application Support/RickCache"
rm -f ~/.rick_key.bin /tmp/.rick_payload
pkill -f rick 2>/dev/null
echo "[OK] machine propre"
