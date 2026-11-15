#!/usr/bin/env python3
# language: Python 3, file: catwoman_tool.py, target: macOS
# CATWOMAN - LA VOLEUSE - powered by Maxime Leal - 8 tools de secrets (lab autorise)
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
B, G, W, DIM, RST, CLR, HOME = ("\033[38;2;60;60;70m", "\033[38;2;255;220;0m",
    "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
      ______   ______   _____   ___    ___
     /      | /      | / ____| / __|  / __|
    |  o    ||  o    || |     | |     | |
    |  _    ||  _    || |___  | |__   | |__
     \_| |__| \_| |__| \____|  \___|  \___|
      LA VOLEUSE - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def jewels(ms=1.0):
    """bijoux qui brillent dans le noir"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(10, 16)):
            x, y = random.randint(1, 74), random.randint(1, 24)
            g = random.choice("◆◇✦✧◇◆")
            print(f"\x1b[{y};{x}H{G}{g}{RST}", end="")
        print(f"\x1b[{12};{30}H{W}seule la nuit protege{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

def claw(ms=0.6):
    """les griffes raient l'ecran"""
    print(CLR + HOME, flush=True)
    for i in range(4):
        x = 12 + i * 14
        for d in range(9):
            print(f"\x1b[{2 + d};{x + d // 2}H{W}/{RST}", end="", flush=True)
            time.sleep(0.02)
        time.sleep(0.1)
    time.sleep(0.4)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.catwoman_fullscreen(2.0)
    jewels(1.0)
    claw()
    print(CLR + HOME + f"\033[1;93m{LOGO}{RST}", flush=True)
    time.sleep(0.5)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================ CATWOMAN ================{RST}")
    print(f"{G}   powered by Maxime Leal{DIM}   |   8 tools de secrets (lab){RST}")
    print(f"{B}  {'◇◆◇' * 14}{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {G}[{i+1}]{RST} {W}{name:<26}{RST} {DIM}{desc}{RST}")
    print(f"\n  {G}[j]{RST} bijoux   {G}[c]{RST} griffes   {G}[q]{RST} disparaitre")

def run(fn):
    claw()
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

cat = importlib.import_module("catwoman")

def main():
    boot()
    tools = cat.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {G}chatte>{RST} ").strip().lower()
        if c == "q":
            jewels(0.8)
            print(CLR + HOME + f"\n{G}la nuit m'appartient. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "j": jewels(2.0)
        elif c == "c": claw()
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
