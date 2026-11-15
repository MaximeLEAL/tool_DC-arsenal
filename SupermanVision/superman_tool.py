#!/usr/bin/env python3
# language: Python 3, file: superman_tool.py, target: macOS Terminal
# SUPERMAN TOOLKIT - powered by Maxime Leal - 8 tools de vision
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
R, B, Y, W, DIM, RST, CLR, HOME = ("\033[38;2;255;60;60m", "\033[38;2;80;140;255m",
    "\033[38;2;255;215;0m", "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
      ____   ___   _    _   ___   _     ___    ___
     / ___| / __| | |  | | / __| | |   / _ \  | _ \
    | (__  | (__  | |__| | \__ \ | |__| (_) | |   /
     \___|  \___| |____| | |___/ |____|\___/  |_|_\\
         SUPERMAN TOOLKIT - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def fly(ms=1.0):
    """le S traverse l'ecran en trace rouge"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        x = random.randint(5, 60)
        print(f"\x1b[{random.randint(3, 20)};{x}H{R}" + "‣" + W + "S" + R + "‣" + RST, end="")
        for _ in range(random.randint(8, 16)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H{B}·{RST}", end="")
        print(f"\x1b[{1};{30}H{Y}★{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def heat(ms=0.8):
    """vision thermique : rougeoie l'ecran"""
    for i in range(int(ms / 0.06)):
        alpha = int(70 + 60 * (i % 2))
        print(CLR + HOME + f"\x1b[48;2;{alpha};20;10m" + " " * 3000 + RST, end="", flush=True)
        time.sleep(0.06)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.superman_fullscreen(2.5)
    fly(0.8)
    heat(0.7)
    fly(0.5)
    print(CLR + HOME + f"\033[1;94m{LOGO}{RST}", flush=True)
    time.sleep(0.4)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================= SUPERMAN ================={RST}")
    print(f"{B}   powered by Maxime Leal{DIM}   |   8 tools de vision{RST}")
    print(f"{R}  {'S' * 1}{Y} ★ {R}{B}" + "-" * 38 + RST + "\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {R}[{i+1}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[f]{RST} vol   {Y}[v]{RST} vision thermique   {Y}[q]{RST} quitter")

def run(fn):
    heat(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

sm = importlib.import_module("superman")

def main():
    boot()
    tools = sm.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {R}sup>{RST} ").strip().lower()
        if c == "q":
            fly(0.8)
            print(CLR + HOME + f"\n{B}la nuit ne fait que commencer.  - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "f": fly(2.0)
        elif c == "v": heat(1.5)
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
