#!/usr/bin/env python3
# language: Python 3, file: vader_tool.py, target: macOS Terminal/iTerm2
# LA FORCE - powered by Maxime Leal - 8 tools, hyper-espace + defile culte
import os, sys, time, random, math, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
Y, B, R, W, DIM, RST, CLR, HOME = ("\033[38;2;255;215;0m", "\033[38;2;100;160;255m",
    "\033[38;2;255;60;60m", "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
        ____   ___   _   _   ___    _____ ____    _
       / ___| |_  \ | | | | | _ \  |_   _|  _ \  / \
       \___ \  / /  | |_| | |   /    | | | |_) |/ _ \
        ___) |/ /_  |  _  | | |\ \    | | |  _ </ ___|
       |____/_/  _| |_| |_| |_| \_\   |_| |_| \_/_/  \_\
              LA FORCE - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def hyperspace(ms=2.0):
    """saut en hyper-espace : etoiles en fuite radiale depuis le centre"""
    cx, cy = 40, 12
    stars = [(random.randint(0, 359), random.uniform(1.5, 14)) for _ in range(90)]
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for a, d in stars:
            d2 = d * 1.35
            x1 = int(cx + d * math.cos(a * math.pi / 180) * 1.9)
            y1 = int(cy + d * math.sin(a * math.pi / 180) * 0.55)
            x2 = int(cx + d2 * math.cos(a * math.pi / 180) * 1.9)
            y2 = int(cy + d2 * math.sin(a * math.pi / 180) * 0.55)
            if 0 < x1 < 80 and 0 < y1 < 25 and 0 < x2 < 80 and 0 < y2 < 25:
                dx, dy = x2 - x1, y2 - y1
                ln = max(abs(dx), abs(dy)) or 1
                c = Y if d > 9 else (W if d > 4 else DIM)
                print(f"\x1b[{y2};{min(x1,x2)}H{c}" + ("-" if abs(dx) > abs(dy) else "|") * min(ln, 8) + RST, end="")
            a2 = a; d3 = d * 1.8
            stars[stars.index((a, d))] = (a, min(14, d + 0.35)) if d < 14 else (random.randint(0, 359), 1.2)
        print(f"\x1b[{12};{39}H{W}·{RST}", end="", flush=True)
        time.sleep(0.045)
    print(CLR + HOME, end="", flush=True)

CRAWL_TEXT = [
    "      Episode MAXIME LEAL",
    "",
    "      C'est une epoque de guerre ouverte.",
    "   Les outils de la BATCAVE, du FLASH",
    "   TOOL SUPER et du LEXCORP ont fusionne",
    "   en un seul arsenal.",
    "",
    "   Poursuivis par aucun proces",
    "   fonctionnant sur leur propre machine,",
    "   les outils de LA FORCE balayent",
    "   le reseau local d'un geste de la main...",
    "",
    "   Et vous, Maxime, etes au volant.",
]

def crawl(ms=6.0):
    """le defile jaune culte - le texte monte dans le ciel etoile"""
    stars = [(random.randint(1, 78), random.randint(1, 24)) for _ in range(90)]
    t0 = time.time()
    block = "\n".join(CRAWL_TEXT)
    offset = 26
    while time.time() - t0 < ms:
        print(CLR + HOME, end="")
        for x, y in stars:
            print(f"\x1b[{y};{x}H{W}.{RST}", end="")
        offset -= 1
        if offset < -len(CRAWL_TEXT) - 4: offset = 26
        y_start = offset
        for li, line in enumerate(CRAWL_TEXT):
            y = y_start + li
            if 1 <= y <= 24:
                print(f"\x1b[{y};{max(1, 40 - len(line)//2)}H{Y}{line}{RST}", end="")
        print(flush=True)
        time.sleep(0.22)
    print(CLR + HOME, end="", flush=True)

def saber(color="\033[38;2;60;255;60m", hum=True):
    """allumage du sabre : la lame pousse depuis la poignee"""
    print(CLR + HOME)
    hx, hy = 20, 12
    print(f"\x1b[{hy};{hx}H{W}====={RST}", flush=True)
    for i in range(1, 45):
        print(f"\x1b[{hy};{hx + 5}H{color}" + ("═" * i) + "◄" + RST, end="", flush=True)
        if hum: print("\a", end="")
        time.sleep(0.035)
    time.sleep(0.5)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.superman_fullscreen(2.5)
    hyperspace(2.2)
    crawl(7.0)
    saber("\033[38;2;60;255;60m")
    print(CLR + HOME + f"\033[1;93m{LOGO}{RST}", flush=True)
    time.sleep(0.5)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================= LA FORCE ================={RST}")
    print(f"{Y}   powered by Maxime Leal{DIM}   |   8 tools du systeme{RST}")
    print(f"{B}  {'*' * 44}{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {Y}[{i+1}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[h]{RST} hyper-espace   {Y}[c]{RST} defile   {Y}[s]{RST} sabre   {Y}[q]{RST} quitter")

def run(fn):
    saber("\033[38;2;60;255;60m", hum=False)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

sw = importlib.import_module("force")

def main():
    boot()
    tools = sw.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {Y}force>{RST} ").strip().lower()
        if c == "q":
            hyperspace(1.5)
            print(CLR + HOME + f"\n{Y}Que la Force soit avec toi. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "h": hyperspace(2.5)
        elif c == "c": crawl(7.0)
        elif c == "s": saber(random.choice(["\033[38;2;60;255;60m", "\033[38;2;255;60;60m", "\033[38;2;100;160;255m"]))
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
