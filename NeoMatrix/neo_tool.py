#!/usr/bin/env python3
# language: Python 3, file: neo_tool.py, target: macOS Terminal/iTerm2
# NEO - LA MATRICE - powered by Maxime Leal - 10 tools, pluie de code + intro culte
import os, sys, time, random, string, importlib
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE, "modules"))
G, DG, W, DIM, RST, CLR, HOME = ("\033[38;2;0;255;70m", "\033[38;2;0;120;30m",
    "\033[1;97m", "\033[2m", "\033[0m", "\033[2J", "\033[H")
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾈﾊﾋﾌﾍﾎﾏﾐﾑﾓﾔﾕﾗﾘﾜ0123456789"

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def rain(ms=3.0, density=0.6):
    """LA pluie de code - colonnes qui tombent, tete blanche, trainee verte"""
    cols, rows = 80, 24
    heads = [random.randint(-rows, rows) for _ in range(cols)]
    speeds = [random.choice((1, 1, 1, 2)) for _ in range(cols)]
    end = time.time() + ms
    buf = []
    while time.time() < end:
        screen = [[" " for _ in range(cols)] for _ in range(rows)]
        color = [[None] * cols for _ in range(rows)]
        for x in range(cols):
            if random.random() < density:
                heads[x] += speeds[x]
            if heads[x] > rows + 6:
                heads[x] = random.randint(-8, 0)
            for d in range(8):
                y = heads[x] - d
                if 0 <= y < rows:
                    screen[y][x] = random.choice(GLYPHS)
                    color[y][x] = W if d == 0 else (G if d < 4 else DG)
        print(CLR + HOME, end="")
        for y in range(rows):
            for x in range(cols):
                if screen[y][x] != " ":
                    print(f"\x1b[{y+1};{x+1}H{color[y][x]}{screen[y][x]}", end="")
        print(RST, end="", flush=True)
        time.sleep(0.07)

def typewriter(txt, ms=0.05):
    for c in txt:
        print(c, end="", flush=True)
        time.sleep(ms)

def intro():
    """la sequence d'ouverture : pluie -> reveil -> la matrice t'a"""
    print(CLR + HOME)
    rain(3.2)
    print(CLR + HOME)
    print("\n\n\n")
    typewriter("      Wake up, Maxime...", 0.07)
    time.sleep(0.8)
    print("\n\n")
    typewriter("      La Matrice t'a.", 0.07)
    time.sleep(0.8)
    print("\n\n")
    typewriter("      Suis le lapin blanc.", 0.06)
    time.sleep(1.2)
    print(CLR + HOME)

def glitch(ms=0.8):
    """l'ecran qui se corrompt"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME)
        for _ in range(random.randint(4, 10)):
            y = random.randint(1, 24)
            x = random.randint(1, 40)
            print(f"\x1b[{y};{x}H{G}" + "".join(random.choice(GLYPHS) for _ in range(random.randint(3, 12))) + RST, end="")
        print(f"\x1b[{12};{32}H{W}DEJA VU{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def redpill():
    print(f"\n  {R}  ___  {G}  ___  {RST}")
    print(f"  {R} (red) {G} (blue){RST}")
    c = input("\n  la pilule rouge (offensif) ou bleue (defense) ? [r/b] : ").strip().lower()
    glitch(0.6)
    return "rouge" if c == "r" else "bleue"

def draw(tools):
    print(CLR + HOME)
    print(f"{W}  ================ N E O ================={RST}")
    print(f"{G}   powered by Maxime Leal{DIM}   |   10 tools de la source{RST}")
    print(f"{DG}  " + "".join(random.choice(GLYPHS) for _ in range(40)) + RST + "\n")
    for i, (name, desc, fn) in enumerate(tools):
        print(f"  {G}[{i+1:>2}]{RST} {W}{name:<26}{RST} {DIM}{desc}{RST}")
    print(f"\n  {G}[r]{RST} pluie de code   {G}[d]{RST} deja-vu (glitch)   {G}[q]{RST} sortir de la matrice")

def run(fn):
    rain(0.8, 0.3)
    try:
        fn()
    except Exception as e:
        print(f"\033[38;2;255;60;60m[X] {e}{RST}")
    print(f"\n{DIM}[entree] retour{RST}")
    input()

neo = importlib.import_module("neo")

def main():
    dfs.hid()
    dfs.matrix_rain_fullscreen(3.5)
    dfs.show()

    hid()
    intro()
    tools = neo.TOOLS
    while True:
        draw(tools)
        c = input(f"\n  {G}matrice>{RST} ").strip().lower()
        if c == "q":
            rain(1.2)
            print(CLR + HOME + f"\n{G}Free your mind. - powered by Maxime Leal{RST}\n\n")
            show(); return
        elif c == "r": rain(3.0)
        elif c == "d": glitch(1.5)
        elif c.isdigit() and 1 <= int(c) <= 10:
            idx = int(c) - 1
            if idx < len(tools): run(tools[idx][2])

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: show(); print()
