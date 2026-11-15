#!/usr/bin/env python3
# language: Python 3, file: sentinelle.py, target: macOS
# SENTINELLE — le gardien de ta machine · tourne en LaunchAgent (toutes les 5 min)
# Surveille : nouveaux appareils wifi · nouveaux ports en écoute · LaunchAgents
# modifiés · sessions ouvertes · disque. Chaque anomalie → notif macOS + push ntfy.
import json, os, subprocess, time, urllib.request, hashlib, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "sentinelle_state.json")
EVENTS = os.path.join(ROOT, "events.json")
CFG = os.path.expanduser("~/.gotham/runtime/DailyPlanet/notifs_config.json")

def load(p, d): 
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return d

def save(p, d): json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)

def cfg():
    return load(CFG, {})

def push(title, message, tags="shield"):
    topic = cfg().get("ntfy_topic")
    if topic:
        try:
            req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=message.encode(),
                headers={"Title": title.encode(), "Tags": tags, "Priority": "high"})
            urllib.request.urlopen(req, timeout=10)
        except Exception: pass

def notify(title, message, sev):
    title = title[:60]; message = message[:160]
    subprocess.run(["osascript", "-e",
        f'display notification "{message}" with title "{title}" subtitle "🛡️ SENTINELLE"'],
        capture_output=True)
    push(title, message)
    events = load(EVENTS, [])
    events.insert(0, {"ts": time.strftime("%d/%m %H:%M"), "type": title, "detail": message, "sev": sev})
    save(EVENTS, events[:50])

def local_ips():
    out = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True).stdout.strip()
    return out or subprocess.run(["ipconfig", "getifaddr", "en1"], capture_output=True, text=True).stdout.strip()

def router_ip():
    rn = subprocess.run(["netstat", "-rn"], capture_output=True, text=True).stdout
    m = re.search(r"^default\s+([\d.]+)", rn, re.M) if (re := __import__("re")) else None
    return m.group(1) if m else ""

import re  # noqa: E402

def scan_lan(state):
    """nouveaux appareils sur le wifi"""
    me = local_ips()
    if not me: return
    base = ".".join(me.split(".")[:3])
    def ping(ip):
        return ip if subprocess.run(["ping", "-c", "1", "-W", "1", ip],
                                    capture_output=True).returncode == 0 else None
    ips = [f"{base}.{i}" for i in range(1, 255) if f"{base}.{i}" != me]
    alive = []
    with __import__("concurrent.futures", fromlist=["futures"]).ThreadPoolExecutor(32) as ex:
        alive = [x for x in ex.map(ping, ips) if x]
    known = set(state.get("lan", []))
    new = [ip for ip in alive if ip not in known and ip != router_ip()]
    if new and known:  # pas d'alerte au tout premier scan (baseline)
        notify("🚨 APPAREIL(S) INCONNU(S) SUR LE WIFI",
               ", ".join(new[:4]) + f" ({len(new)} au total)", "alerte")
    state["lan"] = alive

def scan_ports(state):
    """nouveaux ports en écoute"""
    out = subprocess.run(["lsof", "-iTCP", "-sTCP:LISTEN", "-n", "-P"],
                         capture_output=True, text=True).stdout
    ports = sorted({m.group(1) for m in (re.finditer(r":(\d+)\s+\(LISTEN\)", out))})
    known = state.get("ports", [])
    if known:
        new = [p for p in ports if p not in known]
        if new:
            notify("🔓 NOUVEAU(X) PORT(S) EN ÉCOUTE", ", ".join(new[:6]), "alerte")
    state["ports"] = ports

def scan_agents(state):
    """LaunchAgents modifiés ou ajoutés"""
    la = os.path.expanduser("~/Library/LaunchAgents")
    try:
        entries = sorted(os.listdir(la))
        digest = hashlib.md5("|".join(entries).encode()).hexdigest()[:12]
        if "agents_hash" in state and digest != state["agents_hash"]:
            added = [e for e in entries if e not in state.get("agents_list", [])]
            detail = ", ".join(added[:3]) if added else "liste modifiée"
            notify("⚙️ LAUNCHAGENTS MODIFIÉS", detail, "alerte")
        state["agents_hash"] = digest
        state["agents_list"] = entries
    except Exception:
        pass  # TCC peut bloquer selon le contexte

def scan_sessions(state):
    """nouvelles sessions ouvertes (who)"""
    out = subprocess.run(["who"], capture_output=True, text=True).stdout.strip()
    h = hashlib.md5(out.encode()).hexdigest()[:12]
    if state.get("who_hash") and h != state["who_hash"]:
        notify("👥 SESSION(S) OUVERTE(S) — CHANGEMENT", out.replace("\n", " · ")[:100], "alerte")
    state["who_hash"] = h

def scan_disk(state):
    """disque presque plein"""
    out = subprocess.run(["df", "-H", "/"], capture_output=True, text=True).stdout
    try:
        pct = int(out.splitlines()[1].split()[4].rstrip("%"))
        if pct >= 90 and not state.get("disk_alerted"):
            notify("💾 DISQUE PRESQUE PLEIN", f"volume racine à {pct}%", "info")
            state["disk_alerted"] = True
        elif pct < 85:
            state["disk_alerted"] = False
    except Exception:
        pass

def run_checks():
    state = load(STATE, {})
    for fn in (scan_lan, scan_ports, scan_agents, scan_sessions, scan_disk):
        try: fn(state)
        except Exception as e: print(f"[!] {fn.__name__}: {e}")
    save(STATE, state)

if __name__ == "__main__":
    minutes = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 5
    print(f"[*] SENTINELLE active — vérification toutes les {minutes} min · Ctrl+C pour arrêter")
    while True:
        run_checks()
        time.sleep(minutes * 60)
