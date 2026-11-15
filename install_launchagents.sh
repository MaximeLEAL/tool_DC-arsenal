#!/bin/bash
# install_launchagents.sh — lance automatiquement au démarrage de ta session :
#   1. le serveur Gotham City (:9000)          → site accessible en permanence
#   2. le tunnel public                        → URL dans ~/.gotham/tunnel_url
#   3. les notifications Daily Planet          → actu cyber = notif macOS
# Astuce macOS : les agents ne peuvent pas lire ~/Desktop (protection TCC),
# donc un MIROIR du runtime est créé dans ~/.gotham/runtime (sans TCC).
# Usage: bash install_launchagents.sh
set -e
DC="$HOME/Desktop/tool_DC"
RUN="$HOME/.gotham/runtime"
LOGS="$HOME/.gotham"
mkdir -p "$LOGS"

# ── 0. miroir runtime (hors Desktop, accessible aux LaunchAgents) ─
mkdir -p "$RUN/DailyPlanet" "$RUN/gotham_static" "$RUN/arsenal_pages_data"
cp "$DC/gotham_full.py" "$RUN/"
cp "$DC/arsenal_dc.html" "$RUN/" 2>/dev/null || true
cp "$DC/DailyPlanet/veille.py" "$DC/DailyPlanet/veille_notifs.py" "$RUN/DailyPlanet/" 2>/dev/null || true
cp "$DC/dc_fullscreen.py" "$RUN/" 2>/dev/null || true
cp "$DC/gotham_static/faces/"*.jpg "$RUN/gotham_static/faces/" 2>/dev/null || mkdir -p "$RUN/gotham_static/faces" && cp "$DC/gotham_static/faces/"*.jpg "$RUN/gotham_static/faces/" 2>/dev/null || true
cp "$DC/arsenal_pages_data/"*.json "$RUN/arsenal_pages_data/" 2>/dev/null || true
# mets à jour le miroir à chaque login : le plist de sync ci-dessous s'en charge
cat > "$LOGS/gotham_sync.sh" <<EOS
#!/bin/bash
mkdir -p "$RUN/gotham_static" "$RUN/arsenal_pages_data" "$RUN/DailyPlanet"
cp "$DC/gotham_full.py" "$RUN/" 2>/dev/null
cp "$DC/arsenal_dc.html" "$RUN/" 2>/dev/null
cp "$DC/dc_fullscreen.py" "$RUN/" 2>/dev/null
cp "$DC/DailyPlanet/veille.py" "$RUN/DailyPlanet/" 2>/dev/null
cp "$DC/gotham_static/faces/"*.jpg "$RUN/gotham_static/faces/" 2>/dev/null
cp "$DC/arsenal_pages_data/"*.json "$RUN/arsenal_pages_data/" 2>/dev/null
EOS
chmod +x "$LOGS/gotham_sync.sh"

cat > "$HOME/Library/LaunchAgents/com.maxime.gotham-sync.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.maxime.gotham-sync</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>$LOGS/gotham_sync.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
</dict></plist>
EOF

# ── 1. serveur Gotham ─────────────────────────────────────────────
cat > "$HOME/Library/LaunchAgents/com.maxime.gotham.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.maxime.gotham</string>
  <key>ProgramArguments</key><array>
    <string>/opt/homebrew/bin/python3</string>
    <string>$RUN/gotham_full.py</string><string>9000</string>
  </array>
  <key>WorkingDirectory</key><string>$RUN</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOGS/gotham.log</string>
  <key>StandardErrorPath</key><string>$LOGS/gotham.log</string>
</dict></plist>
EOF

# ── 2. tunnel public (URL extraite dans $LOGS/tunnel_url) ─────────
cat > "$LOGS/gotham_tunnel.sh" <<'EOS'
#!/bin/bash
LOG="$HOME/.gotham/cloudflared.log"
/opt/homebrew/bin/cloudflared tunnel --url http://localhost:9000 > "$LOG" 2>&1 &
CPID=$!
sleep 10
URL=$(/usr/bin/grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG" | /usr/bin/head -1)
if [ -n "$URL" ]; then echo "$URL" > "$HOME/.gotham/tunnel_url"; fi
wait $CPID
EOS
chmod +x "$LOGS/gotham_tunnel.sh"

cat > "$HOME/Library/LaunchAgents/com.maxime.gotham-tunnel.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.maxime.gotham-tunnel</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string><string>$LOGS/gotham_tunnel.sh</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict></plist>
EOF

# ── 3. notifications Daily Planet ─────────────────────────────────
cat > "$HOME/Library/LaunchAgents/com.maxime.dailyplanet.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.maxime.dailyplanet</string>
  <key>ProgramArguments</key><array>
    <string>/opt/homebrew/bin/python3</string>
    <string>$RUN/DailyPlanet/veille_notifs.py</string><string>start</string><string>5</string>
  </array>
  <key>WorkingDirectory</key><string>$RUN/DailyPlanet</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOGS/notifs.log</string>
  <key>StandardErrorPath</key><string>$LOGS/notifs.log</string>
</dict></plist>
EOF

# ── installation ──────────────────────────────────────────────────
for svc in gotham gotham-tunnel dailyplanet gotham-sync; do
  launchctl unload "$HOME/Library/LaunchAgents/com.maxime.$svc.plist" 2>/dev/null || true
  launchctl load   "$HOME/Library/LaunchAgents/com.maxime.$svc.plist"
done

echo ""
echo "=== INSTALLÉ — actif maintenant et à chaque démarrage ==="
sleep 12
echo "  Site local    : http://127.0.0.1:9000"
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
[ -n "$IP" ] && echo "  Réseau local  : http://$IP:9000  (téléphone sur le même wifi)"
[ -f "$LOGS/tunnel_url" ] && echo "  Public (monde): $(cat $LOGS/tunnel_url)"
echo "  Notifs        : Daily Planet vérifie les actus toutes les 5 min"
echo "  Miroir runtime: $RUN (sync auto à chaque login)"
echo "  Logs          : $LOGS/"
echo "  Pour tout arrêter : launchctl unload ~/Library/LaunchAgents/com.maxime.gotham{,-tunnel,-sync,-dailyplanet}.plist"
