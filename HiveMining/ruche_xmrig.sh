#!/bin/zsh
# HiveMining/ruche_xmrig.sh - MINER REEL : xmrig (Monero) sur ta machine, ton wallet
# Usage: ./ruche_xmrig.sh <adresse_wallet>  (defaut: pool de test donation-less)
# Prerequis: brew install xmrig  (le script l'installe s'il manque)
set -e
WALLET="${1:-44AFFq5kKiGBohNU1FsFKNncbhK6SLGq6GkBoheFgsiiWqYKZ8b34ENuPT88FnSswYbn33s1YvD5mZgMoFo4JLPB4pCoV8b}"
POOL="pool.moneroocean.stream:10128"
cd "$(dirname "$0")"

command -v xmrig >/dev/null || brew install xmrig
mkdir -p sorties
cat > sorties/config.json <<EOF
{
  "autosave": true,
  "cpu": { "max-threads-hint": 50, "yield": true },
  "pools": [ { "url": "$POOL", "user": "$WALLET", "pass": "x", "keepalive": true } ]
}
EOF
echo "[OK] config : sorties/config.json"
echo "[*] demarrage du minage (Ctrl+C pour stopper) :"
xmrig --config sorties/config.json
