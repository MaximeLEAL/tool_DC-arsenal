# modules/cyborg.py - CYBORG : 8 tools technet (integration, API, automatisation)
import os, subprocess, json, time, hashlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def api_strike():
    method = ask("methode (GET/POST/PUT/DELETE)").upper()
    url = ask("URL")
    body = ask("body JSON (vide = aucun)")
    if method == "GET" or not body:
        r(f"curl -s -X {method} '{url}' | head -30")
    else:
        r(f"""curl -s -X {method} '{url}' -H 'Content-Type: application/json' -d '{body}' | head -30""")
    print(f"\n  [OK] frappe {method} loggee")

def webhook_forge():
    """serveur local qui recoit et logge tout webhook"""
    code = """
import http.server, datetime
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n).decode()
        line = f"{datetime.datetime.now()} | {self.client_address[0]} | {self.path} | {body[:300]}"
        open("webhooks.log","a").write(line+"\\n"); print(line)
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"cyborg ready")
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8083), H).serve_forever()
"""
    p = os.path.join(OUT, "webhook_server.py")
    open(p, "w").write(code)
    print(f"  [OK] {p}")
    print("  lance : python3 sorties/webhook_server.py  -> ecoutera sur :8083, log dans webhooks.log")

def json_xray():
    v = ask("JSON colle (ou chemin de fichier)")
    if os.path.exists(v): v = open(v).read()
    try:
        d = json.loads(v)
        print("  JSON valide ✓")
        path = ask("chemin a extraire (ex a.b.c, vide = tout)")
        if path:
            for k in path.split("."):
                d = d[k] if isinstance(d, dict) else d[int(k)]
        print("  extrait :", json.dumps(d, indent=2)[:800])
    except Exception as e:
        print(f"  [MENTI] JSON invalide : {e}")

def cron_forge():
    print("  taches planifiees actuelles :")
    r("crontab -l 2>/dev/null || echo '  (aucune)'")
    sched = ask("plan (ex */5 * * * * = toutes les 5 min, vide = passer)")
    if sched:
        cmd = ask("commande a planifier")
        r(f'(crontab -l 2>/dev/null; echo "{sched} {cmd}") | crontab -')
        r("crontab -l | tail -3")

def port_guard():
    """veille : si un port s'ouvre, une action se declenche"""
    port = ask("port a surveiller")
    action = ask("commande a executer si ouvert") or "say 'port ouvert'"
    print(f"  garde du port {port} active - Ctrl+C pour stopper")
    try:
        while True:
            rc = subprocess.run(f"nc -z -G 1 127.0.0.1 {port}", shell=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            if rc == 0:
                print(f"  [ALERTE] port {port} ouvert !")
                r(action)
                break
            time.sleep(2)
    except KeyboardInterrupt:
        print()

def tech_scan():
    h = ask("site")
    r(f'curl -s "{h}/robots.txt" | head -15')
    print()
    r(f'curl -sIL "{h}" | head -15')
    print()
    r(f'curl -s "{h}/sitemap.xml" | head -10')

def automaton():
    """surveille un dossier et declenche une commande au changement"""
    folder = ask("dossier a surveiller")
    cmd = ask("commande au changement")
    prev = None
    print(f"  automate actif sur {folder} - Ctrl+C pour stopper")
    try:
        while True:
            h = subprocess.run(f"ls -la '{folder}' 2>/dev/null", shell=True, capture_output=True).stdout
            s = hashlib.md5(h).hexdigest()
            if prev and s != prev:
                print(f"  [AUTOMATE] changement detecte -> {cmd}")
                r(cmd)
            prev = s
            time.sleep(2)
    except KeyboardInterrupt:
        print()

def nano_repair():
    """verification sante disque + permissions"""
    r("diskutil verifyVolume / | head -8")
    r("diskutil info / | grep -E 'File System|Mounted|Read-Only'")

TOOLS = [
    ("API STRIKE",       "tester un endpoint REST en 4 methodes",       api_strike),
    ("WEBHOOK FORGE",    "serveur local qui recoit les webhooks",       webhook_forge),
    ("JSON X-RAY",       "valider + extraire du JSON",                  json_xray),
    ("CRON FORGE",       "planifier des taches (crontab)",              cron_forge),
    ("PORT GUARD",       "veille : une action quand un port s'ouvre",   port_guard),
    ("TECH SCAN",        "robots/sitemap/headers d'un site",            tech_scan),
    ("AUTOMATON",        "surveille un dossier, agit au changement",    automaton),
    ("NANO-REPAIR",      "sante du volume et du systeme de fichiers",   nano_repair),
]
