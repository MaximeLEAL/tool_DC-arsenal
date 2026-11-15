#!/usr/bin/env python3
# language: Python 3, file: bat_tool.py, target: macOS Terminal / iTerm2
# BATCAVE TOOLKIT - powered by Maxime Leal - 31 tools, 6 pages
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))

Y, W, GRAY, RED, DIM, RST = "\033[38;2;255;215;0m", "\033[1;37m", "\033[38;2;160;160;160m", "\033[38;2;255;60;60m", "\033[2m", "\033[0m"
CLR, HOME = "\033[2J", "\033[H"

BANNER = r"""
        _=__        ~~~ BATCAVE TOOLKIT ~~~      =-_
      _==(o)___     powered by Maxime Leal       ___(o)==_
    .'  `.  `-.                                 ,-'  .'  `.
   /  __  \     \                             /     /  __  \
  |  (o) |  ,--. |   GOTHAM  N E T W O R K  | .--,  | (o)  |
   \____/  /    \ \_________________________/ /    \  \____/
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def signal(ms=1.0):
    """bat-signal : faisceau qui balaie le ciel noir, chauve-souris dans le faisceau"""
    end = time.time() + ms
    while time.time() < end:
        x = random.randint(10, 55)
        print(CLR + HOME, end="")
        for y in range(1, 18):
            w = y * 2
            print(f"\x1b[{y};{max(1, x - w//2)}H" + DIM + "." * max(1, w) + RST, end="")
        cx = x
        print(f"\x1b[{3 + random.randint(0, 8)};{cx}H" + Y + "^.^" + RST, end="")
        print(f"\x1b[{20};{30}H" + W + BANNER.splitlines()[1] + RST, end="", flush=True)
        time.sleep(0.09)
    print(CLR + HOME, end="", flush=True)

def bats(ms=0.6):
    """vol de chauves-souris en fond"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(6, 12)):
            x, y = random.randint(1, 76), random.randint(1, 20)
            print(f"\x1b[{y};{x}H" + GRAY + random.choice(["^", "^^", "^.^", "\\^/"]) + RST, end="")
        print(f"\x1b[{22};{2}H" + W + "BATCAVE TOOLKIT" + RST, end="", flush=True)
        time.sleep(0.08)

def bat_flash(n=2):
    """le signal s'allume franchement"""
    for _ in range(n):
        print(CLR + HOME + f"\x1b[48;2;255;225;80m" + " " * 3000 + RST, end="", flush=True)
        time.sleep(0.06)
        print(CLR + HOME + "\x1b[48;2;0;0;0m" + " " * 100 + RST, end="", flush=True)
        time.sleep(0.07)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.batman_intro(3.5)
    bats(0.6)
    signal(1.2)
    print(CLR + HOME + f"\033[1;93m{BANNER}{RST}", flush=True)
    time.sleep(0.6)
    print(CLR + HOME, end="")

def page_banner(p):
    print(CLR + HOME)
    print(f"{W}  =================== BATCAVE ==================={RST}")
    print(f"{Y}   powered by Maxime Leal{DIM}   |   page {p[0]+1}/6 : {p[1]}{RST}")
    print(f"{GRAY}  {random.choice(['^.^', '^  ^', '^.^   ^.^']) * 8}{RST}")
    print()

def draw(p):
    page_banner(p)
    for i, (name, desc, fn) in enumerate(p[2]):
        print(f"  {Y}[{i+1:>2}]{RST} {W}{name:<28}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[n]{RST} page suivante   {Y}[p]{RST} precedente   {Y}[q]{RST} quitter   {Y}[s]{RST} bat-signal")

def run_tool(p, idx):
    name, desc, fn = p[2][idx]
    bat_flash(2)
    print(f"\n{Y}=== {name} ==={RST}\n{DIM}{desc}{RST}\n")
    try:
        fn()
    except Exception as e:
        print(f"{RED}[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour a la cave{RST}")
    input()

detective = importlib.import_module("detective")
crypto    = importlib.import_module("crypto")
sniff     = importlib.import_module("sniff")
darkweb   = importlib.import_module("darkweb")
gadgets   = importlib.import_module("gadgets")
alerts    = importlib.import_module("alerts")

PAGES = [
    ("DETECTIVE", [
        ("ANALYSE EMAIL",        "headers d'un .eml : IP source, relais",   detective.email_analysis),
        ("IMAGE FORENSIQUE",     "hash, infos, recherche inverse",          detective.image_forensic),
        ("STEGANO - CACHER",     "message secret dans un PNG",              detective.stego_hide),
        ("STEGANO - REVELER",    "extraire le secret d'un PNG",             detective.stego_reveal),
        ("DOSSIER DOMAINE",      "whois + dns + mx en un rapport",          detective.domain_dossier),
        ("IDENTIFIER UN HASH",   "type de hash + essais dictionnaire",      detective.hash_id),
    ]),
    ("CRYPTO", [
        ("COUTEAU SUISSE ENC",   "base64 / hex / rot13 encode-decode",      crypto.swiss),
        ("AES FICHIER",          "chiffre/dechiffre via openssl",           crypto.aes_file),
        ("CASSE-MD5",            "attaque dictionnaire md5/sha1",           crypto.crack_md5),
        ("GENERATEUR MDP",       "mot de passe fort sur mesure",            crypto.pwgen),
        ("CHIFFRE CESAR",        "rot-N interactif",                        crypto.caesar),
        ("EMPREINTES",           "checksums sha256 d'un fichier",           crypto.checksums),
    ]),
    ("SNIFFER", [
        ("TCPDUMP LIVE",         "paquets en direct (sudo demande)",        sniff.live),
        ("HTTP URIS",            "URLs en clair sur le port 80",            sniff.http_uris),
        ("REJOUER UN PCAP",      "analyse d'un fichier de capture",         sniff.replay),
        ("VOISINS ARP",          "qui est sur le reseau maintenant",        sniff.neighbors),
        ("GROS PARLEURS",        "qui consomme le reseau",                  sniff.talkers),
    ]),
    ("DARK WEB", [
        ("STATUS TOR",           "tor tourne ? sortie ok ?",                darkweb.status),
        ("INSTALLER TOR",        "brew install + service",                  darkweb.install),
        ("FETCH ONION",          "recuperer une page .onion via tor",       darkweb.onion_fetch),
        ("MOTEURS D'OMBRE",      "liens de recherche leaks/ombres",         darkweb.shadow_engines),
    ]),
    ("GADGETS", [
        ("BATARANG KNOCK",       "port knocking sur une cible",             gadgets.batarang),
        ("SONAR RESEAU",         "balayage complet : vivants + arp",        gadgets.sonar),
        ("FUMIGENE MAC",         "usurper une adresse MAC",                 gadgets.smoke_mac),
        ("GRAPIN SSH",           "connexion ssh configuree d'un coup",      gadgets.grapple),
        ("BATMOBILE SPEED",      "test de debit reseau",                    gadgets.speed),
        ("BATSUIT",              "rapport machine complet",                 gadgets.suit),
    ]),
    ("ALERTES", [
        ("BAT-SIGNAL WEB",       "surveille un site, alerte au changement", alerts.watch_site),
        ("PERIMETRE RESEAU",     "alerte aux nouveaux appareils",           alerts.watch_net),
        ("VEILLE PORTS",         "alerte si un port s'ouvre",               alerts.watch_ports),
        ("JOURNAL D'ALERTES",    "relecture du journal de la cave",         alerts.journal),
    ]),
]

def main():
    boot()
    pi = 0
    while True:
        p = (pi, PAGES[pi][0], PAGES[pi][1])
        draw(p)
        c = input(f"\n  {Y}bat>{RST} ").strip().lower()
        if c == "q":
            bats(0.8)
            print(CLR + HOME + f"\n{Y}^.^  BATCAVE TOOLKIT - powered by Maxime Leal  ^.^{RST}\n\n")
            show(); return
        elif c == "n": pi = (pi + 1) % 6; bats(0.4)
        elif c == "p": pi = (pi - 1) % 6; bats(0.4)
        elif c == "s": signal(1.5)
        elif c.isdigit() and 1 <= int(c) <= 9:
            idx = int(c) - 1
            if idx < len(p[2]): run_tool(p, idx)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show(); print()
