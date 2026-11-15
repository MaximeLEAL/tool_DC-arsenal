# modules/superman.py - 8 tools de vision (tout reels)
import os, subprocess, time

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def rayons_x():
    """vision rayons-X du disque : les plus gros, les caches, les recents"""
    print("  --- 15 plus gros fichiers du home ---")
    r("du -ah ~ 2>/dev/null | sort -rh | head -15")
    print("\n  --- fichiers caches recents (48 h) ---")
    r("find ~ -maxdepth 3 -name '.*' -mtime -2 -type f 2>/dev/null | head -15")
    print("\n  --- modifie dans la derniere heure ---")
    r("find ~ -maxdepth 3 -mmin -60 -type f 2>/dev/null | head -15")

def vision_chaleur():
    """CPU par processus en direct, colore"""
    print("  Ctrl+C pour stopper\n")
    try:
        while True:
            os.system("clear")
            print("  VISION THERMIQUE - top CPU\n" + "-" * 50)
            r("ps -arcwwwxo pid,pcpu,comm | head -15")
            time.sleep(2)
    except KeyboardInterrupt:
        print()

def souffle_givrant():
    """geler / degeler un processus - reversible"""
    print("  processus candidats (les plus gourmands) :")
    r("ps -arcwwwxo pid,pcpu,comm | head -8")
    pid = ask("PID a geler (kill -STOP = pause, jamais mort)")
    subprocess.run(f"kill -STOP {pid}", shell=True)
    print(f"  [GEL] {pid} fige. Clique sur entree pour le degeler...")
    input()
    subprocess.run(f"kill -CONT {pid}", shell=True)
    print(f"  [DEGEL] {pid} reprend son vol.")

def super_ouie():
    r("system_profiler SPAudioDataType | head -30")

def kryptonite():
    """detecteur : balaye les process contre les IOCs des kits du lab"""
    import re
    iocs = ["01_keylogger", "02_reverse_shell", "04_clipboard", "05_usb_worm",
            "07_screenspy", "08_webcam", "10_mic", "RickPortal", "RickCache", "sys.log"]
    procs = subprocess.run("ps -axo pid,command", shell=True, capture_output=True).stdout.decode()
    agents = subprocess.run("ls ~/Library/LaunchAgents/", shell=True, capture_output=True).stdout.decode()
    hits = []
    for ioc in iocs:
        if ioc in procs or ioc in agents:
            hits.append(ioc)
    if hits:
        print("  KRYPTONITE DETECTEE — traces de kits dans cette machine :")
        for h in hits: print(f"   * {h}")
        print("\n  purge : zsh ~/Desktop/RickPortal/delivery/uninstall.sh")
    else:
        print("  aucune trace kryptonite — machine saine.")

def forteresse():
    """coffre-fort : dossier chiffre AES via openssl"""
    d = ask("dossier a blinder")
    if not os.path.isdir(d):
        print("  dossier introuvable"); return
    pw = ask("mot de passe de la forteresse")
    out = d.rstrip("/") + ".forteresse"
    r(f'tar czf - -C "{os.path.dirname(d)}" "{os.path.basename(d)}" | openssl enc -aes-256-cbc -pbkdf2 -salt -out "{out}" -pass pass:"{pw}"')
    print(f"  [OK] forteresse : {out}")
    print(f"  pour ouvrir : openssl enc -d -aes-256-cbc -pbkdf2 -in '{out}' -pass pass:'<pw>' | tar xzf -")

def charge_solaire():
    r("pmset -g batt")
    r("pmset -g thermlog 2>/dev/null | head -5 || pmset -g therm 2>/dev/null")

def vite():
    """recherche instantanee de fichiers sur tout le disque"""
    q = ask("nom (ex rapport)")
    r(f"mdfind -name '{q}' | head -25")
    print("\n  par contenu aussi :")
    r(f"mdfind '{q}' | head -10")

TOOLS = [
    ("RAYONS-X DISQUE",     "les plus gros / caches / recents",        rayons_x),
    ("VISION THERMIQUE",    "CPU par process en direct",               vision_chaleur),
    ("SOUFFLE GIVRANT",     "geler un process (reversible)",           souffle_givrant),
    ("SUPER-OUÏE",          "carte audio de la machine",               super_ouie),
    ("KRYPTONITE DETECTOR", "trace de kits suspects sur la machine",   kryptonite),
    ("FORTERESSE",          "coffre chiffre AES d'un dossier",         forteresse),
    ("CHARGE SOLAIRE",      "batterie et thermique",                   charge_solaire),
    ("SUPER-VITESSE",       "recherche instantanee de fichiers",       vite),
]
