#!/usr/bin/env python3
# language: Python 3, file: aquaman_tool.py, target: macOS Terminal
# TRIDENT TOOLKIT - powered by Maxime Leal - 8 tools courants du reseau
import os, sys, time, random, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
T, W, DIM, RST, CLR, HOME = "\033[38;2;64;224;208m", "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H"

LOGO = r"""
        ~~~~~  ~~~~~~   ~~~~~~~   ~~~~~~~
   ~~~  TRIDENT TOOLKIT - powered by Maxime Leal  ~~~
        ~~~~~   ~~   ~~~~~~~   ~~    ~~~~~~
"""

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def waves(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for y in range(1, 22):
            amp = int(3 * (1 + (y % 4)) * 0.6)
            off = int(10 * (1 + (y % 3)) * 0.8)
            line = "".join("~" if ((x + y * 3 + (x * x) // 11) % 7 == 0) else " " for x in range(0, 78))
            print(f"\x1b[{y};1H{T}{line}{RST}", end="")
        print(f"\x1b[{10};{28}H{W}T R I D E N T{RST}", end="", flush=True)
        time.sleep(0.12)
    print(CLR + HOME, end="", flush=True)

def bubbles(ms=0.6):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(12, 20)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H{T}o{RST}", end="")
        print(f"\x1b[{2};{30}H{W}~ plongee ~{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def boot():
    dfs.hid()
    dfs.waves_fullscreen(2.5)
    bubbles(0.6)
    waves(1.2)
    print(CLR + HOME + f"\033[1;96m{LOGO}{RST}", flush=True)
    time.sleep(0.4)
    print(CLR + HOME, end="")

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================= TRIDENT ================={RST}")
    print(f"{T}   powered by Maxime Leal{DIM}   |   8 tools des courants{RST}")
    print(f"{T}  {'~' * 44}{RST}\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {T}[{i+1}]{RST} {W}{name:<24}{RST} {DIM}{desc}{RST}")
    print(f"\n  {T}[w]{RST} vagues   {T}[q]{RST} remonter")

def run(fn):
    waves(0.5)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

aq = importlib.import_module("aquaman")

def main():
    boot()
    tools = aq.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {T}trident>{RST} ").strip().lower()
        if c == "q":
            waves(0.8)
            print(CLR + HOME + f"\n{T}~~~~~  la maree se retire  ~~~~~{RST}\n\n")
            show(); return
        elif c == "w": waves(2.0)
        elif c.isdigit() and 1 <= int(c) <= 8:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
