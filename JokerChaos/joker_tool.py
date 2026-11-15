#!/usr/bin/env python3
# language: Python 3, file: joker_tool.py, target: macOS Terminal
# WHY SO SERIOUS TOOLKIT - powered by Maxime Leal - 8 tools chaos-prank (lab)
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
P, G, W, RST, CLR, HOME = "\033[38;2;155;48;255m", "\033[38;2;57;255;20m", "\033[1;37m", "\033[0m", "\033[2J", "\033[H"

LOGO = r"""
     _   _   ___   _     ___   ___    _     ___
    | | | | / __| | |   |_  | | __|  /_\   | _ \
    | |_| | \__ \ | |__   | | | _|  / _ \  |   /
     \___/  |___/ |____| |___||___|/_/ \_\ |_|_\\
       WHY SO SERIOUS - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def laugh(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(14, 22)):
            c = random.choice([P, G, W])
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,70)}H{c}" + "HA " * random.randint(1, 4) + RST, end="")
        print(f"\x1b[{11};{30}H{W}WHY SO SERIOUS ?{RST}", end="", flush=True)
        time.sleep(0.09)
    print(CLR + HOME, end="", flush=True)

def cards(ms=0.7):
    suits = ["♠", "♥", "♦", "♣"]
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(10, 18)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,74)}H"
                  + random.choice([P, G]) + random.choice(suits) + RST, end="")
        print(f"\x1b[{12};{32}H{W}J O K E R{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

def smoke():
    print(CLR + HOME)
    for i in range(8):
        print(f"\x1b[{24 - i};{10 + i * 6}H{G}" + "░▒▓█" * random.randint(1, 2) + RST, flush=True)
        time.sleep(0.05)
    time.sleep(0.3)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.joker_intro(3.0)
    cards(0.7)
    laugh(1.0)
    smoke()
    print(CLR + HOME + f"\033[1;95m{LOGO}{RST}", flush=True)
    time.sleep(0.5)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================== JOKER =================={RST}")
    print(f"{P}   powered by Maxime Leal{DIM}   |   8 tools de chaos (lab){RST}")
    print(f"{G}  {'♠♥♦♣' * 9}{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {G}[{i+1}]{RST} {P}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {G}[h]{RST} rafale de rires   {G}[c]{RST} pluie de cartes   {G}[q]{RST} quitter")

def run(fn):
    laugh(0.6)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

joker = importlib.import_module("joker")

def main():
    boot()
    tools = joker.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {G}joker>{RST} ").strip().lower()
        if c == "q":
            laugh(0.8)
            print(CLR + HOME + f"\n{G}HA HA HA HA...  WHY SO SERIOUS ?{RST}\n\n")
            show(); return
        elif c == "h": laugh(2.0)
        elif c == "c": cards(1.5)
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
