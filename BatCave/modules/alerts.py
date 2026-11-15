# modules/alerts.py - le systeme d'alerte de la cave
import os, subprocess, time, hashlib

LOG = os.path.expanduser("~/Desktop/BatCave/sorties/alertes.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    open(LOG, "a").write(line + "\n")
    print("  " + line)

def watch_site():
    url = ask("URL a surveiller")
    iv = int(ask("intervalle secondes (30)") or 30)
    prev = None
    print(f"  surveillance de {url} - Ctrl+C pour stopper\n")
    while True:
        try:
            body = subprocess.run(f"curl -sL '{url}'", shell=True, capture_output=True, timeout=20).stdout
            h = hashlib.sha256(body).hexdigest()
            if prev and h != prev:
                log(f"CHANGEMENT sur {url} (hash {prev[:8]} -> {h[:8]})")
                subprocess.run("say 'bat signal: changement detecte'", shell=True)
            prev = h
        except Exception as e:
            log(f"erreur sur {url} : {e}")
        time.sleep(iv)

def watch_net():
    iv = int(ask("intervalle secondes (15)") or 15)
    known = set()
    print("  perimetre actif - Ctrl+C pour stopper\n")
    while True:
        arp = subprocess.run("arp -a", shell=True, capture_output=True).stdout.decode()
        macs = set(re.findall(r"at ([0-9a-f:]{17})", arp)) if (re := __import__("re")) else set()
        for m in macs - known:
            log(f"NOUVEL APPAREIL sur le reseau : {m}")
            subprocess.run("say 'nouvel appareil detecte'", shell=True)
        known |= macs
        time.sleep(iv)

def watch_ports():
    iv = int(ask("intervalle secondes (10)") or 10)
    prev = None
    print("  veille des ports d'ecoute - Ctrl+C pour stopper\n")
    while True:
        out = subprocess.run("lsof -nP -iTCP -sTCP:LISTEN", shell=True, capture_output=True).stdout.decode()
        s = hashlib.sha256(out.encode()).hexdigest()
        if prev and s != prev:
            log("CHANGEMENT dans les ports d'ecoute")
        prev = s
        time.sleep(iv)

def journal():
    if os.path.exists(LOG):
        subprocess.run(f"tail -40 '{LOG}'", shell=True)
    else:
        print("  journal vide - aucune alerte encore")
