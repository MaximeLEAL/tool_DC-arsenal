#!/usr/bin/env python3
# language: Python 3, file: dc_visual.py, target: macOS Terminal/iTerm2
# DC VISUAL — LA BIBLIOTHÈQUE ANIMÉE PARTAGÉE DE L'ARSENAL · powered by Maxime Leal
# Chaque personnage DC a : sa palette, son intro cinématique, ses transitions, son menu stylé.
# Importé par tous les kits : le design devient cohérent et épique partout.

import time, random, math

# ─── UTILITAIRES COMMUNS ──────────────────────────────────────────
CLR, HOME = "\033[2J", "\033[H"
def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def title(txt, row=2, col=None, color="\033[1;97m", delay=0.02):
    col = col or (40 - len(txt) // 2)
    for i, c in enumerate(txt):
        print(f"\x1b[{row};{col + i}H{color}{c}", end="", flush=True)
        if delay: time.sleep(delay)

def flash_screen(color_rgb, n=2, dur=0.06):
    """flash plein écran de la couleur donnée"""
    for _ in range(n):
        print(CLR + HOME + f"\x1b[48;2;{color_rgb[0]};{color_rgb[1]};{color_rgb[2]}m" + " " * 4000 + RST, end="", flush=True)
        time.sleep(dur)
        print(CLR + HOME + "\x1b[48;2;0;0;0m" + " " * 100 + RST, end="", flush=True)
        time.sleep(dur * 1.2)
    print(CLR + HOME, end="", flush=True)

def particles(ms=1.0, colors=["\033[38;2;255;255;255m"], glyphs=["·", "•", "✦"], count=40):
    """particules qui flottent dans le noir"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for _ in range(count):
            x, y = random.randint(1, 78), random.randint(1, 24)
            c = random.choice(colors)
            print(f"\x1b[{y};{x}H{c}{random.choice(glyphs)}{RST}", end="")
        print(end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

def typewriter(txt, row, col, color="\033[1;97m", ms=0.04):
    for i, c in enumerate(txt):
        print(f"\x1b[{row};{col + i}H{color}{c}", end="", flush=True)
        time.sleep(ms)

RST = "\033[0m"

# ═══════════════════════════════════════════════════════════════════
# BATMAN — noir, or, chauve-souris, bat-signal
# ═══════════════════════════════════════════════════════════════════
BATMAN = {
    "colors": {"primary": "\033[38;2;255;215;0m", "secondary": "\033[38;2;200;200;200m",
               "accent": "\033[38;2;255;60;60m", "bg": "#000000"},
    "logo": ["   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   ", "  █ BATCAVE █  ", "   ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀   "],
}

def batman_intro(ms_total=3.5):
    """bat-signal qui balaie Gotham, chauve-souris apparaît dans le faisceau"""
    end = time.time() + ms_total * 0.5
    cx, cy = 40, 10
    while time.time() < end:
        print(CLR + HOME, end="")
        beam_x = random.randint(20, 55)
        for y in range(1, 18):
            w = y * 2
            print(f"\x1b[{y};{max(1, beam_x - w // 2)}H\033[38;2;60;60;80m" + "░" * max(1, w) + RST, end="")
        print(f"\x1b[{5 + random.randint(0, 5)};{beam_x}H\033[1;93m^.^{RST}", end="")
        print(end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)
    # la chauve-souris se déploie
    bat = r"""
              _         _
             / \       / \
            {   '.   .'   }
           ^~^~^~^~^~^~^~^~^~^
          {    BATCAVE    }
           ^~^~^~^~^~^~^~^~^~^
            {   .'   '.   }
             \  /     \  /
        """
    print(CLR + HOME + f"\033[1;93m{bat}{RST}", flush=True)
    time.sleep(1.0)
    typewriter("I AM THE NIGHT.", 20, 28, "\033[1;93m", 0.06)
    time.sleep(0.8)
    print(CLR + HOME, end="", flush=True)

def batman_transition():
    """transition chauve-souris rapide entre les écrans"""
    print(CLR + HOME, end="")
    for _ in range(3):
        x, y = random.randint(1, 76), random.randint(1, 22)
        print(f"\x1b[{y};{x}H\033[38;2;255;215;0m^{RST}", end="")
        x2, y2 = random.randint(1, 76), random.randint(1, 22)
        print(f"\x1b[{y2};{x2}H\033[38;2;200;200;200m^{RST}", end="")
    print(f"\x1b[{12};{35}H\033[1;93m^.^ BATCAVE{RST}", end="", flush=True)
    time.sleep(0.25)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# THE FLASH — jaune/orange, éclair, vitesse, code rain
# ═══════════════════════════════════════════════════════════════════
FLASH = {
    "colors": {"primary": "\033[38;2;255;215;0m", "secondary": "\033[38;2;255;60;60m",
               "accent": "\033[38;2;255;140;0m"},
}

def flash_intro(ms_total=3.0):
    """l'éclair frappe, la vitesse déchire l'écran"""
    print(CLR + HOME, end="")
    # lignes de vitesse convergentes
    for i in range(30):
        print(CLR + HOME, end="")
        for _ in range(random.randint(15, 25)):
            x = random.randint(1, 70)
            y = random.randint(1, 24)
            c = random.choice(["\033[38;2;255;215;0m", "\033[38;2;255;60;60m", "\033[1;97m"])
            print(f"\x1b[{y};{x}H{c}" + "-" * random.randint(5, 25) + RST, end="")
        print(f"\x1b[{12};{35}H\033[1;97m⚡{RST}", end="", flush=True)
        time.sleep(0.05)
    print(CLR + HOME, end="", flush=True)
    # éclair géant
    for y in range(1, 24, 2):
        print(f"\x1b[{y};{random.randint(30, 50)}H\033[1;93m{'/' if y % 4 else chr(92)}{RST}", end="", flush=True)
        time.sleep(0.03)
    typewriter("⚡ FLASH TOOL_SUPER", 12, 28, "\033[1;97m", 0.04)
    time.sleep(0.5)
    print(CLR + HOME, end="", flush=True)

def speed_lines(ms=0.5):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for _ in range(random.randint(3, 5)):
            line = "".join(random.choice(["\033[38;2;255;215;0m", "\033[38;2;255;60;60m",
                "\033[38;2;255;140;0m"]) + "-" * random.randint(8, 30) + RST for _ in range(2))
            print(CLR + HOME + "\n\n" + line + "\n" * random.randint(2, 4) + line, end="", flush=True)
        time.sleep(0.04)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# JOKER — violet/vert, HA HA HA, chaos
# ═══════════════════════════════════════════════════════════════════
JOKER = {
    "colors": {"primary": "\033[38;2;155;48;255m", "secondary": "\033[38;2;57;255;20m"},
}

def joker_intro(ms_total=3.0):
    """l'écran se remplit de HA HA HA puis une carte apparaît"""
    end = time.time() + ms_total * 0.6
    while time.time() < end:
        print(CLR + HOME, end="")
        for _ in range(random.randint(18, 25)):
            x, y = random.randint(1, 70), random.randint(1, 24)
            c = random.choice(["\033[38;2;155;48;255m", "\033[38;2;57;255;20m"])
            print(f"\x1b[{y};{x}H{c}HA HA{RST}", end="")
        print(f"\x1b[{11};{30}H\033[1;97mWHY SO SERIOUS?{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)
    # carte qui se retourne
    print(f"\x1b[{10};{35}H\033[1;95m┌─────────┐{RST}")
    print(f"\x1b[{11};{35}H\033[1;95m│  JOKER  │{RST}")
    print(f"\x1b[{12};{35}H\033[1;95m│  ♠ ♥ ♦ │{RST}")
    print(f"\x1b[{13};{35}H\033[1;95m│  CLUBS  │{RST}")
    print(f"\x1b[{14};{35}H\033[1;95m└─────────┘{RST}", flush=True)
    time.sleep(0.8)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# SUPERMAN — rouge/bleu, vol, vision thermique
# ═══════════════════════════════════════════════════════════════════
SUPERMAN = {
    "colors": {"primary": "\033[38;2;255;60;60m", "secondary": "\033[38;2;100;160;255m",
               "gold": "\033[38;2;255;215;0m"},
}

def superman_fly(ms=1.0):
    """le S traverse l'écran en trace rouge/bleu"""
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        x = random.randint(10, 60)
        y = random.randint(3, 20)
        print(f"\x1b[{y};{x}H\033[38;2;255;60;60m{'━' * 4}{RST}\x1b[{y};{x + 4}H\033[1;94mS{RST}", end="")
        for _ in range(random.randint(5, 10)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H\033[38;2;100;160;255m·{RST}", end="")
        print(end="", flush=True)
        time.sleep(0.07)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# WONDER WOMAN — rouge/or, lasso tournoyant
# ═══════════════════════════════════════════════════════════════════
def lasso_spin(ms=1.0, cx=40, cy=12, r=14):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for k in range(0, 360, 18):
            a = k + time.time() * 350
            x = int(cx + r * math.cos(a * math.pi / 180))
            y = int(cy + r * math.sin(a * math.pi / 180) * 0.5)
            if 0 < x < 80 and 0 < y < 25:
                print(f"\x1b[{y};{x}H\033[38;2;255;215;0m*{RST}", end="")
        print(f"\x1b[{cy};{cx}H\033[1;97mVÉRITÉ{RST}", end="", flush=True)
        time.sleep(0.04)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# AQUAMAN — turquoise, vagues, bulles
# ═══════════════════════════════════════════════════════════════════
def waves_anim(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for y in range(1, 22):
            t = time.time() * 3
            line = "".join("~" if (x + int(t * 4) + y) % 6 < 2 else " " for x in range(0, 78))
            print(f"\x1b[{y};1H\033[38;2;64;224;208m{line}{RST}", end="")
        print(f"\x1b[{10};{30}H\033[1;96mT R I D E N T{RST}", end="", flush=True)
        time.sleep(0.12)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTINE — bougie, fumée, ombre
# ═══════════════════════════════════════════════════════════════════
def candle(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        h = random.randint(3, 7)
        x = 40
        for i in range(h):
            print(f"\x1b[{20 - i};{x}H\033[38;2;255;170;60m{'█' if i else '▲'}{RST}", end="")
        print(f"\x1b[{20 - h - 1};{x - 1}H\033[38;2;90;255;120m~{RST}", end="")
        print(f"\x1b[{22};{30}H\033[1;97m{'ombre t appelle'.center(30)}{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# RAVEN — ombres, fumée violette
# ═══════════════════════════════════════════════════════════════════
def raven_shadow(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for _ in range(random.randint(12, 18)):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,72)}H"
                  + random.choice(["\033[38;2;80;0;120m", "\033[38;2;40;0;60m"])
                  + "░▒▓"[:random.randint(1, 3)] + RST, end="")
        print(f"\x1b[{12};{36}H\033[1;95mRAVEN{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# MATRICE — pluie de code, déjà-vu
# ═══════════════════════════════════════════════════════════════════
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾈﾊﾋﾌﾍﾎﾏﾐﾑﾓﾔﾕﾗﾘﾜ0123456789"

def matrix_rain(ms=3.0, density=0.6):
    cols, rows = 80, 24
    heads = [random.randint(-rows, rows) for _ in range(cols)]
    speeds = [random.choice((1, 1, 1, 2)) for _ in range(cols)]
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for x in range(cols):
            if random.random() < density: heads[x] += speeds[x]
            if heads[x] > rows + 6: heads[x] = random.randint(-8, 0)
            for d in range(8):
                y = heads[x] - d
                if 0 <= y < rows:
                    c = "\033[1;97m" if d == 0 else ("\033[38;2;0;255;70m" if d < 4 else "\033[38;2;0;120;30m")
                    print(f"\x1b[{y+1};{x+1}H{c}{random.choice(GLYPHS)}", end="")
        print(end="", flush=True)
        time.sleep(0.07)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# WARWORLD — rouages, alerte, verrou
# ═══════════════════════════════════════════════════════════════════
def war_gears(ms=1.2):
    chars = "▚▞▙▟▛▜"
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for _ in range(random.randint(15, 22)):
            x, y = random.randint(1, 74), random.randint(1, 22)
            print(f"\x1b[{y};{x}H" + random.choice(["\033[38;2;255;70;40m", "\033[38;2;255;140;0m"])
                  + random.choice(chars) * 3 + RST, end="")
        print(f"\x1b[{21};{28}H\033[1;97mWARWORLD — L'ARSENAL{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# STAR LABS — scanlines bleu, hologramme
# ═══════════════════════════════════════════════════════════════════
def scanlines(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        y = random.randint(2, 22)
        print(f"\x1b[{y};1H\033[38;2;0;200;255m" + "═" * 78 + RST, end="")
        for _ in range(8):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,72)}H\033[38;2;180;255;120m▪{RST}", end="")
        print(f"\x1b[{12};{30}H\033[1;97mSYSTEMS ONLINE{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# LEX LUTHOR — vert/rouge corporate
# ═══════════════════════════════════════════════════════════════════
def lex_boot(ms=1.0):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for y in range(1, 24):
            width = int(78 * (0.3 + 0.7 * math.sin(y * 0.3 + time.time() * 2)))
            line = "█" * max(1, width // 2)
            print(f"\x1b[{y};{40 - width // 4}H\033[38;2;57;255;20m{line}{RST}", end="")
        print(f"\x1b[{12};{30}H\033[1;92mLEXCORP{RST}", end="", flush=True)
        time.sleep(0.1)
    print(CLR + HOME, end="", flush=True)

# ═══════════════════════════════════════════════════════════════════
# DAILY PLANET — presse, globe qui tourne, étoiles
# ═══════════════════════════════════════════════════════════════════
def globe_spin(ms=1.5):
    end = time.time() + ms
    while time.time() < end:
        print(CLR + HOME, end="")
        for y in range(3, 20):
            width = int(abs(math.sin(time.time() * 2 + y * 0.2)) * 30 + 5)
            offset = int(40 - width // 2)
            line = "░" * max(1, width)
            print(f"\x1b[{y};{offset}H\033[38;2;100;160;255m{line}{RST}", end="")
        for _ in range(5):
            print(f"\x1b[{random.randint(1,24)};{random.randint(1,76)}H\033[38;2;255;215;0m✦{RST}", end="")
        print(f"\x1b[{11};{28}H\033[1;97mDAILY PLANET{RST}", end="", flush=True)
        time.sleep(0.08)
    print(CLR + HOME, end="", flush=True)
