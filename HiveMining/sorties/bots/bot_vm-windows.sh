#!/bin/zsh
# bot vm-windows - mineur xmrig + rapport a la ruche (machine autorisee : vm-windows)
# Install une seule fois, puis tourne en daemon basse priorite.
WALLET="44AFFq5kKiGBohNU1FsFKNncbhK6SLGq6GkBoheFgsiiWqYKZ8b34ENuPT88FnSswYbn33s1YvD5mZgMoFo4JLPB4pCoV8b"
POOL="pool.moneroocean.stream:10128"
COORD="127.0.0.1:8096"
NAME="vm-windows"

command -v xmrig >/dev/null || brew install xmrig
mkdir -p ~/ruche
cat > ~/ruche/config.json <<CFG
{
  "autosave": true,
  "cpu": { "max-threads-hint": 60, "yield": true, "priority": 1 },
  "pools": [ { "url": "pool.moneroocean.stream:10128", "user": "$WALLET", "pass": "vm-windows", "keepalive": true } ]
}
CFG

# rapport de statut vers le coordonnateur toutes les 60 s
cat > ~/ruche/beacon.py <<BCN
#!/usr/bin/env python3
import urllib.request, time, os
N = "vm-windows"; C = "http://127.0.0.1:8096/beacon"
t0 = time.time()
while True:
    try:
        running = os.system("pgrep -x xmrig >/dev/null") == 0
        body = (f"bot={N}&alive={'1' if running else '0'}&"
                f"uptime={int(time.time()-t0)}&host={os.uname().nodename}").encode()
        urllib.request.urlopen(urllib.request.Request(C, data=body), timeout=10)
    except Exception:
        pass
    time.sleep(60)
BCN
chmod +x ~/ruche/beacon.py
nohup python3 ~/ruche/beacon.py >/dev/null 2>&1 &

# lancement du minage en daemon basse priorite
nohup xmrig --config ~/ruche/config.json --daemon >/dev/null 2>&1
echo "[OK] bot vm-windows deploye : minage en cours + beacon vers 127.0.0.1:8096"
