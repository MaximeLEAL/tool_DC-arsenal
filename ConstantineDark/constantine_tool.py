#!/usr/bin/env python3
# language: Python 3, file: constantine_tool.py, target: macOS Terminal
# CONSTANTINE - LA CASE DE L'OMBRE - powered by Maxime Leal - dark web, 10 tools
# usage strictement lab / recherche autorisee - voir README.md section LEGAL
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
G, A, W, DIM, RST, CLR, HOME = ("\033[38;2;90;255;120m", "\033[38;2;255;170;60m",
    "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
      _____ ____  _   _  _____ _    _ _____   ____ _  __     _
     / ____/ ____|| \ | |/ ____| |  | |_   _| / __| |/ /    | |
    | |   | |     |  \| | |    | |__| | | |  | |  | ' /  ___| |__   ___
    | |   | |     | . ` | |    |  __  | | |  | |  |  <  / __| '_ \ / _ \
    | |___| |____ | |\  | |____| |  | |_| |_ | |__| . \ \__ \ | | |  __/
     \_____\_____||_| \_|\_____|_|  |_|_____| |___/_|\_\___/_| |_|\___|
                     LA CASE DE L'OMBRE - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def candle(ms=1.0):
    """flamme de bougie qui vacille dans le noir"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        h = random.randint(3, 7)
        x = 40
        for i in range(h):
            print(f"\x1b[{20 - i};{x}H{A}{'█' if i else '▲'}{RST}", end="")
        print(f"\x1b[{20 - h - 1};{x - 1}H{G}~{RST}", end="")
        for _ in range(6):
            print(f"\x1b[{random.randint(1, 24)};{random.randint(1, 76)}H{DIM}·{RST}", end="")
        print(f"\x1b[{22};{32}H{W}l'ombre t'appelle{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

def smoke(ms=0.8):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(10, 16)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,70)}H{DIM}{G}░▒▓{RST}", end="")
        print(f"\x1b[{12};{34}H{A}✠{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.candle_fullscreen(2.5)
    smoke(0.7)
    candle(1.2)
    print(CLR + HOME + f"\033[1;92m{LOGO}{RST}", flush=True)
    time.sleep(0.5)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  =============== CONSTANTINE ==============={RST}")
    print(f"{G}   powered by Maxime Leal{DIM}   |   10 tools de l'ombre{RST}")
    print(f"{A}  ✠{DIM}{'-' * 44}{A}✠{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {G}[{i+1:>2}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {A}[b]{RST} bougie   {G}[q]{RST} remonter a la surface")

def run(fn):
    candle(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

dk = importlib.import_module("darkweb_kit")

def main():
    boot()
    tools = dk.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {G}ombre>{RST} ").strip().lower()
        if c == "q":
            smoke(0.8)
            print(CLR + HOME + f"\n{A}la surface est juste en haut. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "b": candle(2.0)
        elif c.isdigit() and 1 <= int(c) <= 10:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
