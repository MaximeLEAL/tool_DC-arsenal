#!/usr/bin/env python3
# language: Python 3, file: lasso_tool.py, target: macOS Terminal
# LASSO DE LA VERITE - powered by Maxime Leal - 8 tools de verification
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
R, G, Y, W, DIM, RST, CLR, HOME = ("\033[38;2;255;70;90m", "\033[38;2;120;255;140m",
    "\033[38;2;255;215;0m", "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")

LOGO = r"""
    ~~~~~  LASSO DE LA VERITE  ~~~~~
       powered by Maxime Leal
    - THEMISCRACY OBEYS THE TRUTH -
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def lasso_spin(ms=1.0):
    """lasso dore qui tournoie"""
    end = time.time() + ms
    cx, cy = 40, 12
    while time.time() < end:
        print(CLR + HOME)
        r = 14
        for k in range(0, 360, 20):
            a = k + time.time() * 400
            import math
            x = int(cx + r * math.cos(a * 3.14159 / 180))
            y = int(cy + r * math.sin(a * 3.14159 / 180) * 0.5)
            if 0 < x < 80 and 0 < y < 25:
                print(f"\x1b[{y};{x}H{Y}*{RST}", end="")
        print(f"\x1b[{cy};{cx}H{W}LA VERITE{RST}", end="", flush=True)
        time.sleep(0.05)
    print(CLR + HOME, end="", flush=True)

def stars(ms=0.7):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(8, 14)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H{Y}✦{RST}", end="")
        print(f"\x1b[{12};{33}H{R}✧ VERITE ✧{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.lasso_fullscreen(2.5)
    stars(0.7)
    lasso_spin(1.1)
    print(CLR + HOME + f"\033[1;93m{LOGO}{RST}", flush=True)
    time.sleep(0.4)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================= LASSO =================={RST}")
    print(f"{Y}   powered by Maxime Leal{DIM}   |   8 tools de verification{RST}")
    print(f"{R}  ✦{DIM}" + "-" * 44 + f"{R}✦{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {R}[{i+1}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {Y}[s]{RST} tournoi du lasso   {Y}[q]{RST} quitter")

def run(fn):
    stars(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

lasso = importlib.import_module("lasso")

def main():
    boot()
    tools = lasso.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {Y}verite>{RST} ").strip().lower()
        if c == "q":
            lasso_spin(0.8)
            print(CLR + HOME + f"\n{Y}la verite ne negocie pas. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "s": lasso_spin(2.0)
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
