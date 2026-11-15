#!/usr/bin/env python3
# language: Python 3, file: ruche_tool.py, target: macOS
# H.I.V.E. - LA RUCHE - powered by Maxime Leal - minage et essaim
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
Y, O, W, DIM, RST, CLR, HOME = ("\033[38;2;255;200;0m", "\033[38;2;255;140;0m",
    "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
      _   _  _____ ___  _   _  ___  _   _
     | | | || ____| _ \| \ | |/ _ \| | | |
     | |_| ||  _| | | | |  \| | | | | | | |
     |  _  || |___| |_| | |\  | |_| | |_| |
     |_| |_||_____|____/|_| \_|\___/ \___/
        H.I.V.E. MINING - powered by Maxime Leal
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def swarm(ms=1.2):
    """l'essaim : abeilles qui dansent vers la ruche"""
    end = time.time() + ms
    cx, cy = 40, 12
    bees = [(random.randint(1, 78), random.randint(1, 24)) for _ in range(30)]
    while time.time() < end:
        print(CLR + HOME, end="")
        # la ruche au centre
        for dy in (-1, 0, 1):
            print(f"\x1b[{cy+dy};{cx-3}H{Y}" + ("▓▒░" * 2) + RST, end="")
        for i, (x, y) in enumerate(bees):
            dx = (cx - x) // max(1, abs(cx - x)) if x != cx else 0
            dy = (cy - y) // max(1, abs(cy - y)) if y != cy else 0
            nx, ny = x + dx, y + dy
            if nx == cx and ny == cy: nx, ny = random.randint(1, 78), random.randint(1, 24)
            print(f"\x1b[{ny};{nx}H{O}♪{RST}", end="")
            bees[i] = (nx, ny)
        print(f"\x1b[{24};{2}H{W}la ruche tourne{RST}", end="", flush=True)
        time.sleep(0.09)
    print(CLR + HOME, end="", flush=True)

def gold(ms=0.8):
    """pluie d'or"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(20):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H{Y}{'$' if random.random()<.3 else '¤'}{RST}", end="")
        print(f"\x1b[{12};{34}H{O}H.I.V.E.{RST}", end="", flush=True)
        time.sleep(0.09)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.hive_fullscreen(2.0)
    gold(0.8)
    swarm(1.4)
    print(CLR + HOME + f"\033[1;93m{LOGO}{RST}", flush=True)
    time.sleep(0.5)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================== H.I.V.E. =================={RST}")
    print(f"{Y}   powered by Maxime Leal{DIM}   |   6 tools de la ruche{RST}")
    print(f"{O}  ♪{'-' * 42}♪{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {Y}[{i+1}]{RST} {W}{name:<26}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[s]{RST} l'essaim   {Y}[q]{RST} quitter")

def run(fn):
    gold(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

ru = importlib.import_module("ruche")

def main():
    boot()
    while True:
        draw(ru.TOOLS)
        c = input(f"\n  {Y}ruche>{RST} ").strip().lower()
        if c == "q":
            swarm(1.0)
            print(CLR + HOME + f"\n{Y}le miel est amasse. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "s": swarm(2.5)
        elif c.isdigit() and 1 <= int(c) <= 6:
            idx = int(c) - 1
            if idx < len(ru.TOOLS): run(ru.TOOLS[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
