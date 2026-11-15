#!/usr/bin/env python3
# language: Python 3, file: warworld_cmd.py v2, target: macOS Terminal/iTerm2
# WARWORLD v2 — CMD anime : fiches d'armes completes, recherche, budget d'acquisition
import os, sys, time, random, math

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
from arsenal_data import ARSENAL, DETAILS

R, O, Y, W, DIM, G, RST, CLR, HOME = ("\033[38;2;255;106;0m", "\033[38;2;255;140;0m",
    "\033[38;2;255;215;0m", "\033[1;97m", "\033[2m", "\033[38;2;57;255;20m", "\033[0m",
    "\033[2J", "\033[H")

LOGO = r"""
    ▄████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓
   ██▒ ▀█▒▓██░ ██▒▒██    ▒ ▒██    ▒ ▓  ██▒ ▓░
  ▒██░▄▄▄░▒██ ██▒░░ ▓██▄   ░ ▓██▄   ▒██░░▒█
  ░▓█  ██▓░ ▚█░█░   ▒   ▒▒   ▒   ██▒▓█   ▓▒░
  ░▒▓███▀▒░ ░▒ ▒  ░▒██████   ▒██████▒▒ ▒▒▒▒░
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def gears(ms=1.2):
    chars = "▚▞▙▟▛▜"
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for row in range(6):
            for col in range(10):
                if random.random() < 0.8:
                    c = random.choice(chars)
                    print(f"\x1b[{2 + row * 3};{6 + col * 7}H"
                          + (R if random.random() < 0.6 else O) + c * 3 + RST, end="")
        print(f"\x1b[{21};{28}H{W}WARWORLD - L'ARSENAL{RST}", end="", flush=True)
        time.sleep(0.12)
    print(CLR + HOME, end="", flush=True)

def target_lock(ms=0.9):
    cx, cy = 40, 12
    for r in range(20, 2, -2):
        print(CLR + HOME, end="")
        for a in range(0, 360, 15):
            x = int(cx + r * math.cos(a * math.pi / 180))
            y = int(cy + r * math.sin(a * math.pi / 180) * 0.5)
            if 0 < x < 80 and 0 < y < 25: print(f"\x1b[{y};{x}H{O}·{RST}", end="")
        print(f"\x1b[{cy};{cx - r}H{R}+{RST}\x1b[{cy};{cx + r}H{R}+{RST}", end="")
        print(f"\x1b[{cy};{cx}H{W}⚠{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def alert(ms=0.8):
    for _ in range(int(ms / 0.09)):
        print(CLR + HOME + "\x1b[48;2;140;20;10m" + " " * 3000 + RST, end="", flush=True)
        time.sleep(0.09); print(CLR + HOME, end="", flush=True); time.sleep(0.06)

def boot():
    hid(); gears(1.6); alert(0.7); target_lock(1.0)
    n = sum(len(v) for v in ARSENAL.values())
    print(CLR + HOME + f"\033[1;91m{LOGO}{RST}", flush=True)
    print(f"{O}   L'ARSENAL CYBER — 12 themes, {n} armes · 21 [LAB] · 31 [REF] · 15 [ACHAT]{RST}", flush=True)
    time.sleep(0.8); print(CLR + HOME, end="")

C = "\033[38;2;136;153;255m"
def badge(s):
    return {"LAB": f"{G}[LAB]", "REF": "\033[38;2;100;160;255m[REF]",
            "ACHAT": f"{O}[ACHAT]", "FERME": f"{C}[FERMÉ]"}[s] + RST

def detail(name, typ, desc, statut, theme):
    target_lock(0.8)
    d = DETAILS.get(name, {})
    print(CLR + HOME)
    print(f"{R}  ╔{'═' * 58}╗{RST}")
    print(f"  ║ {W}{name.upper():<56}{R}║")
    print(f"  ║ {DIM}{theme} · {typ}{R}", " " * max(1, 57 - len(theme) - len(typ) - 11), f"║{RST}")
    print(f"{R}  ╚{'═' * 58}╝{RST}\n")
    print(f"  {badge(statut)}\n")
    print(f"  {DIM}{desc}{RST}\n")
    if d.get("usage"):
        print(f"  {Y}USAGE :{RST} {d['usage']}")
    if d.get("kit"):
        print(f"  {G}KIT   :{RST} ~/Desktop/{d['kit']}")
    if d.get("prix"):
        print(f"  {O}PRIX  :{RST} ~{d['prix']} EUR (approx)")
    if d.get("buy"):
        print(f"  {Y}MAGASIN :{RST} {d['buy']}")
    if d.get("link"):
        print(f"  {C}DÉPÔT   :{RST} {d['link']}")
    print(f"\n  {DIM}[entree] retour au theme{RST}")
    input()

def budget():
    print(CLR + HOME)
    total = 0
    print(f"{O}  === BUDGET D'ACQUISITION (hardware a acquerir) ===\n{RST}")
    for theme, ws in ARSENAL.items():
        for name, typ, desc, s in ws:
            if s == "ACHAT":
                prix = DETAILS.get(name, {}).get("prix", 0)
                total += prix
                buy = DETAILS.get(name, {}).get("buy", "")
                print(f"   {Y}{name:<30}{RST} {DIM}{prix:>5} EUR — {desc[:40]}{RST}")
                if buy: print(f"   {'':30} {DIM}↳ {buy}{RST}")
    print(f"\n   {R}TOTAL ARSENAL HARDWARE COMPLET : {total} EUR{RST}")
    print(f"   {DIM}(sans compteur, ni VM Windows, ni serveur distant){RST}")
    print(f"\n  {DIM}[entree] retour{RST}")
    input()

def search():
    q = input(f"\n  {Y}chasse :{RST} ").strip().lower()
    if not q: return
    print(CLR + HOME)
    print(f"{W}  RESULTATS POUR '{q.upper()}'{RST}\n")
    n = 0
    for theme, ws in ARSENAL.items():
        for name, typ, desc, s in ws:
            if q in (name + desc + theme).lower():
                n += 1
                print(f"   {R}[{theme[:12]:<12}]{RST} {badge(s)} {W}{name:<28}{RST} {DIM}{typ}{RST}")
    print(f"\n   {DIM}{n} resultat(s) — entree pour retour{RST}")
    input()

def draw_theme(ti):
    theme = list(ARSENAL.keys())[ti]
    weapons = ARSENAL[theme]
    print(CLR + HOME)
    print(f"{R}  ╔{'═' * 58}╗{RST}")
    print(f"  ║{W}  THEME {ti+1}/12 : {theme.upper():<42}{R}║")
    print(f"{R}  ╚{'═' * 58}╝{RST}\n")
    for i, (name, typ, desc, statut) in enumerate(weapons):
        print(f"  {R}[{i+1}]{RST} {W}{name:<30}{RST} {DIM}{typ:<9}{RST} {badge(statut)}")
    print(f"\n  {O}[1-9]{RST} fiche arme   {Y}[f]{RST} chasse   {Y}[b]{RST} budget hardware")
    print(f"  {O}[n]{RST} suivant  {O}[p]{RST} precedent  {O}[g]{RST} rouages  {O}[t]{RST} verrou  {O}[q]{RST} quitter")

def main():
    boot()
    ti = 0
    while True:
        draw_theme(ti)
        c = input(f"\n  {R}warworld>{RST} ").strip().lower()
        weapons = ARSENAL[list(ARSENAL.keys())[ti]]
        if c == "q":
            gears(1.0)
            print(CLR + HOME + f"\n{R}l'arsenal se scelle. la guerre attend son heure.{RST}\n\n")
            show(); return
        elif c == "n": ti = (ti + 1) % 12; gears(0.5)
        elif c == "p": ti = (ti - 1) % 12; gears(0.5)
        elif c == "g": gears(2.0)
        elif c == "t": target_lock(1.5)
        elif c == "b": budget()
        elif c == "f": search()
        elif c.isdigit() and 1 <= int(c) <= 9:
            idx = int(c) - 1
            if idx < len(weapons):
                name, typ, desc, statut = weapons[idx]
                theme = list(ARSENAL.keys())[ti]
                detail(name, typ, desc, statut, theme)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
