#!/usr/bin/env python3
# language: Python 3, file: cyborg_tool.py, target: macOS Terminal
# CYBORG TECHNET - powered by Maxime Leal - 8 tools d'integration
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
C, G, W, DIM, RST, CLR, HOME = ("\033[38;2;0;200;255m", "\033[38;2;180;255;120m",
    "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
     ____ ____  _   _   _____ ____  _____ ____
    / ___|  _ \| \ | | | ____|  _ \| ____|  _ \
   | |   | |_) |  \| | |  _| | |_) |  _| | |_) |
   | |___|  _ <| |\  | | |___|  _ <| |___|  _ <
    \____|_| \_\_| \_| |_____|_| \_\_____|_| \_\
         TECHNET - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def scanlines(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        y = random.randint(2, 22)
        print(f"\x1b[{y};1H{C}" + "═" * 78 + RST, end="")
        for _ in range(8):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,72)}H{G}▪{RST}", end="")
        print(f"\x1b[{12};{30}H{W}SYSTEMS ONLINE{RST}", end="", flush=True)
        time.sleep(0.09)
    print(CLR + HOME, end="", flush=True)

def circuit(ms=0.7):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(14):
            x, y = random.randint(1, 70), random.randint(1, 24)
            print(f"\x1b[{y};{x}H{C}{'─' if y % 2 else '│'}{RST}", end="")
        print(f"\x1b[{12};{34}H{G}◉{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.cyborg_fullscreen(2.0)
    circuit(0.7)
    scanlines(1.1)
    print(CLR + HOME + f"\033[1;96m{LOGO}{RST}", flush=True)
    time.sleep(0.4)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================= CYBORG ================={RST}")
    print(f"{C}   powered by Maxime Leal{DIM}   |   8 tools technet{RST}")
    print(f"{G}  ◉{DIM}{'─' * 44}{G}◉{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {C}[{i+1}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {C}[t]{RST} scanlines   {C}[q]{RST} quitter")

def run(fn):
    scanlines(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

cy = importlib.import_module("cyborg")

def main():
    boot()
    tools = cy.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {C}cyborg>{RST} ").strip().lower()
        if c == "q":
            scanlines(0.8)
            print(CLR + HOME + f"\n{C}les systemes restent en ligne. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "t": scanlines(2.0)
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
