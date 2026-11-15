#!/usr/bin/env python3
# language: Python 3, file: ruche_bots.py, target: macOS
# LA FABRIQUE DE BOTS MINIERS : genere les scripts de deploiement pour ta flotte
# Chaque bot = xmrig configure (wallet/pool/threads) + rapport de statut au coordonnateur.
# Usage: python3 ruche_bots.py <wallet_xmr> [coordonnateur_ip:port]
# Sortie: sorties/bots/bot_<nom>.sh + bot_<nom>.py (a poser sur CHACUNE de TES machines)
import os, sys, json

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "sorties", "bots")
os.makedirs(OUT, exist_ok=True)

wallet = sys.argv[1] if len(sys.argv) > 1 else "44AFFq5kKiGBohNU1FsFKNncbhK6SLGq6GkBoheFgsiiWqYKZ8b34ENuPT88FnSswYbn33s1YvD5mZgMoFo4JLPB4pCoV8b"
coord = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1:8096"
POOL = "pool.moneroocean.stream:10128"   # pool auto-switchant : choisit la monnaie la plus rentable

BOT_SH = '''#!/bin/zsh
# bot {name} - mineur xmrig + rapport a la ruche (machine autorisee : {name})
# Install une seule fois, puis tourne en daemon basse priorite.
WALLET="{wallet}"
POOL="{pool}"
COORD="{coord}"
NAME="{name}"

command -v xmrig >/dev/null || brew install xmrig
mkdir -p ~/ruche
cat > ~/ruche/config.json <<CFG
{{
  "autosave": true,
  "cpu": {{ "max-threads-hint": 60, "yield": true, "priority": 1 }},
  "pools": [ {{ "url": "{pool}", "user": "$WALLET", "pass": "{name}", "keepalive": true }} ]
}}
CFG

# rapport de statut vers le coordonnateur toutes les 60 s
cat > ~/ruche/beacon.py <<BCN
#!/usr/bin/env python3
import urllib.request, time, os
N = "{name}"; C = "http://{coord}/beacon"
t0 = time.time()
while True:
    try:
        running = os.system("pgrep -x xmrig >/dev/null") == 0
        body = (f"bot={{N}}&alive={{'1' if running else '0'}}&"
                f"uptime={{int(time.time()-t0)}}&host={{os.uname().nodename}}").encode()
        urllib.request.urlopen(urllib.request.Request(C, data=body), timeout=10)
    except Exception:
        pass
    time.sleep(60)
BCN
chmod +x ~/ruche/beacon.py
nohup python3 ~/ruche/beacon.py >/dev/null 2>&1 &

# lancement du minage en daemon basse priorite
nohup xmrig --config ~/ruche/config.json --daemon >/dev/null 2>&1
echo "[OK] bot {name} deploye : minage en cours + beacon vers {coord}"
'''

BOT_PY = None  # la beacon est embarquee dans le .sh

names = sys.argv[3:] if len(sys.argv) > 3 else ["macbook-air", "vm-windows", "serveur-lab"]
for i, name in enumerate(names):
    n = name.replace(" ", "-").lower()
    p = os.path.join(OUT, f"bot_{n}.sh")
    open(p, "w").write(BOT_SH.format(name=n, wallet=wallet, pool=POOL, coord=coord))
    os.chmod(p, 0o755)
    print(f"[OK] bot_{n}.sh  -> a copier et lancer sur la machine '{n}'")

print(f"\n[*] wallet : {wallet[:24]}...")
print(f"[*] pool   : {POOL} (auto-switch rentabilite)")
print(f"[*] coordonnateur : http://{coord}/dashboard")
print("[*] deployment : scp bot_<nom>.sh cible: && zsh bot_<nom>.sh")
