#!/bin/zsh
# 3-VOIR-BUTIN.command - double-clique : le butin s'ouvre et se synchronise
# Lance le collecteur (RickCache cache -> Reception visible, toutes les 5 s)
cd "$(dirname "$0")"
nohup zsh delivery/collecteur.sh >/dev/null 2>&1 &
open "Reception"
exit 0
