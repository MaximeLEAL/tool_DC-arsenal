#!/usr/bin/env python3
# language: Python 3, file: dc_fullscreen.py, target: macOS Terminal/iTerm2 (FULLSCREEN ADAPTIVE)
# LA BIBLIOTHÈQUE VISUELLE FULLSCREEN — s'adapte à la taille réelle du terminal
# Chaque animation remplit TOUTE la fenêtre, peu importe la taille (80x24 ou 300x80)
import os, sys, time, random, math, shutil

# ─── DIMENSIONS DYNAMIQUES (s'adaptent au fullscreen) ───
def term_size():
    try:
        cols, rows = os.get_terminal_size()
        return cols, rows
    except Exception:
        return shutil.get_terminal_size((80, 24))

COLS, ROWS = term_size()
CLR, HOME = "\033[2J", "\033[H"
RST = "\033[0m"

def hid(): print("\033[?25l", end="")
def show(): print("\033[?25h", end="")

def refresh_size():
    global COLS, ROWS
    COLS, ROWS = term_size()

# ─── HELPERS FULLSCREEN ───
def fill_bg(rgb, alpha=1.0):
    """remplit tout l'écran avec une couleur de fond"""
    print(CLR + HOME + f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m" + " " * (COLS * ROWS) + RST, end="", flush=True)

def clear():
    print(CLR + HOME, end="", flush=True)

def px(y, x, char, color="", bg=""):
    """dessine UN pixel à la position donnée"""
    if 0 < y < ROWS and 0 < x < COLS:
        print(f"\x1b[{y};{x}H{color}{bg}{char}", end="")

def rect(y, x, h, w, char, color="", fill=False):
    """dessine un rectangle plein ou bordure"""
    if fill:
        for r in range(h):
            print(f"\x1b[{y + r};{x}H{color}{char * w}{RST}", end="")
    else:
        print(f"\x1b[{y};{x}H{color}{'─' * w}{RST}", end="")
        for r in range(1, h):
            print(f"\x1b[{y + r};{x}H{color}│{' ' * (w - 1)}│{RST}", end="")
        print(f"\x1b[{y + h};{x}H{color}{'─' * w}{RST}", end="")

def center_text(txt, y, color="", bg=""):
    """centre du texte sur la largeur de l'écran"""
    x = max(1, (COLS - len(txt)) // 2)
    print(f"\x1b[{y};{x}H{color}{bg}{txt}{RST}", end="")

# ═══════════════════════════════════════════════════════════════════
# BATMAN — bat-signal FULLSCREEN + chauve-souris géante
# ═══════════════════════════════════════════════════════════════════
def batman_intro(duration=4.0):
    refresh_size()
    cx, cy = COLS // 2, ROWS // 2
    end = time.time() + duration * 0.5
    # phase 1 : bat-signal qui balaie tout le ciel
    while time.time() < end:
        clear()
        beam_x = random.randint(COLS // 6, COLS * 5 // 6)
        for y in range(1, ROWS - 4):
            w = min(y * 2, COLS // 2)
            color = "\033[38;2;40;40;60m"
            if y > ROWS // 2: color = "\033[38;2;30;30;45m"
            print(f"\x1b[{y};{max(1, beam_x - w // 2)}H{color}" + "░" * max(1, w) + RST, end="")
        # la chauve-souris apparaît dans le faisceau
        bat_y = random.randint(3, ROWS // 2)
        print(f"\x1b[{bat_y};{beam_x - 2}H\033[1;93m{'.^.':^7}{RST}", end="", flush=True)
        time.sleep(0.09)
    # phase 2 : la chauve-souris GÉANTE se déploie (proportionnelle à l'écran)
    clear()
    bat_size = min(ROWS - 6, 20)
    bat_art = [
        "                _         _                ",
        "               / \\       / \\              ",
        "              {   '.   .'   }              ",
        "           ^~^~^~^~^~^~^~^~^~^           ",
        "          {     BATMAN      }             ",
        "           ^~^~^~^~^~^~^~^~^~^           ",
        "              {   .'   '.   }              ",
        "               \\  /     \\  /              ",
    ]
    start_y = max(1, (ROWS - len(bat_art)) // 2)
    start_x = max(1, (COLS - len(bat_art[0])) // 2)
    for i, line in enumerate(bat_art):
        print(f"\x1b[{start_y + i};{start_x}H\033[1;93m{line}{RST}", end="")
    print(flush=True)
    typewriter_fs("I AM THE NIGHT.", ROWS - 4)
    time.sleep(duration * 0.25)
    clear()

def typewriter_fs(txt, y, color="\033[1;97m"):
    """typewriter centré sur l'écran complet"""
    x = max(1, (COLS - len(txt)) // 2)
    for i, c in enumerate(txt):
        print(f"\x1b[{y};{x + i}H{color}{c}", end="", flush=True)
        time.sleep(0.05)

# ═══════════════════════════════════════════════════════════════════
# FLASH — éclair qui traverse TOUT l'écran, lignes de vitesse
# ═══════════════════════════════════════════════════════════════════
def flash_intro(duration=3.5):
    refresh_size()
    end = time.time() + duration * 0.4
    # phase 1 : lignes de vitesse FULLSCREEN
    while time.time() < end:
        clear()
        for _ in range(random.randint(25, 40)):
            x = random.randint(1, max(1, COLS - 30))
            y = random.randint(1, ROWS)
            c = random.choice(["\033[1;93m", "\033[38;2;255;60;60m", "\033[38;2;255;140;0m"])
            length = random.randint(15, min(COLS - x, 60))
            print(f"\x1b[{y};{x}H{c}" + "-" * length + RST, end="")
        center_text("⚡", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.04)
    # phase 2 : l'éclair qui descend FULLSCREEN
    clear()
    x = COLS // 2
    for y in range(1, ROWS - 2, 2):
        x += random.randint(-4, 4)
        x = max(2, min(COLS - 2, x))
        print(f"\x1b[{y};{x}H\033[1;93m/{RST}", end="")
        print(f"\x1b[{y+1};{x+1}H\033[1;97m/{RST}", end="", flush=True)
        time.sleep(0.03)
    time.sleep(0.3)
    # phase 3 : FLASH TOOL_SUPER en plein centre
    clear()
    title_big = "FLASH TOOL SUPER"
    fs = max(1, (COLS - len(title_big)) // 2)
    print(f"\x1b[{ROWS // 2 - 2};{fs}H\033[1;97m{title_big}{RST}")
    sub = "powered by Maxime Leal"
    print(f"\x1b[{ROWS // 2};{max(1, (COLS - len(sub)) // 2)}H\033[38;2;255;60;60m{sub}{RST}", end="", flush=True)
    time.sleep(0.8)
    clear()

def speed_lines_fullscreen(ms=0.6):
    refresh_size()
    end = time.time() + ms
    while time.time() < end:
        clear()
        for _ in range(random.randint(8, 14)):
            y = random.randint(1, ROWS)
            x = random.randint(1, max(1, COLS - 40))
            c = random.choice(["\033[1;93m", "\033[38;2;255;60;60m", "\033[38;2;255;140;0m"])
            length = random.randint(20, COLS - x)
            print(f"\x1b[{y};{x}H{c}" + "-" * length + RST, end="")
        center_text("⚡", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.05)
    clear()

# ═══════════════════════════════════════════════════════════════════
# JOKER — HAHA HA FULLSCREEN + carte géante
# ═══════════════════════════════════════════════════════════════════
def joker_intro(duration=3.5):
    refresh_size()
    end = time.time() + duration * 0.55
    # phase 1 : HAHA envahit TOUT l'écran
    while time.time() < end:
        clear()
        for _ in range(random.randint(30, 50)):
            x = random.randint(1, COLS - 12)
            y = random.randint(1, ROWS)
            c = random.choice(["\033[1;95m", "\033[1;92m", "\033[1;97m"])
            text = random.choice(["HA", "HA HA", "HA HA HA", "HAH", "AH"])
            print(f"\x1b[{y};{x}H{c}{text}{RST}", end="")
        print(f"\x1b[{ROWS // 2};{COLS // 2 - 9}H\033[1;97mWHY SO SERIOUS?{RST}", end="", flush=True)
        time.sleep(0.08)
    # phase 2 : la carte JOKER au centre
    clear()
    card_y = ROWS // 2 - 4
    card_x = COLS // 2 - 12
    card = [
        "┌────────────┐",
        "│            │",
        "│   J O K    │",
        "│   E  R    │",
        "│   ♠ ♥ ♦   │",
        "│   CLUBS   │",
        "│            │",
        "└────────────┘",
    ]
    for i, line in enumerate(card):
        print(f"\x1b[{card_y + i};{card_x}H\033[1;95m{line}{RST}")
    print(f"\x1b[{card_y + 9};{card_x}H\033[1;92mWHY SO SERIOUS?{RST}", flush=True)
    time.sleep(duration * 0.25)
    clear()

# ═══════════════════════════════════════════════════════════════════
# MATRIX — LA pluie de code FULLSCREEN (remplit TOUTE la fenêtre)
# ═══════════════════════════════════════════════════════════════════
GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾈﾊﾋﾌﾍﾎﾏﾐﾑﾓﾔﾕﾗﾘﾜ0123456789"

def matrix_rain_fullscreen(duration=4.0, density=0.65):
    refresh_size()
    heads = [random.randint(-ROWS, ROWS) for _ in range(COLS)]
    speeds = [random.choice((1, 1, 1, 2)) for _ in range(COLS)]
    trail = min(ROWS // 2, 10)
    end = time.time() + duration
    while time.time() < end:
        clear()
        for x in range(COLS):
            if random.random() < density:
                heads[x] += speeds[x]
            if heads[x] > ROWS + trail:
                heads[x] = random.randint(-10, 0)
            for d in range(trail):
                y = heads[x] - d
                if 0 <= y < ROWS:
                    if d == 0:
                        print(f"\x1b[{y + 1};{x + 1}H\033[1;97m{random.choice(GLYPHS)}{RST}", end="")
                    elif d < trail // 2:
                        print(f"\x1b[{y + 1};{x + 1}H\033[38;2;0;255;70m{random.choice(GLYPHS)}{RST}", end="")
                    else:
                        print(f"\x1b[{y + 1};{x + 1}H\033[38;2;0;100;30m{random.choice(GLYPHS)}{RST}", end="")
        print(end="", flush=True)
        time.sleep(0.06)
    clear()

# ═══════════════════════════════════════════════════════════════════
# STAR LABS — scanlines FULLSCREEN bleu holographique
# ═══════════════════════════════════════════════════════════════════
def star_scanlines(duration=2.0):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        scan_y = random.randint(2, ROWS - 2)
        print(f"\x1b[{scan_y};1H\033[38;2;0;200;255m" + "═" * COLS + RST, end="")
        for _ in range(random.randint(15, 25)):
            x = random.randint(1, COLS)
            y = random.randint(1, ROWS)
            print(f"\x1b[{y};{x}H\033[38;2;180;255;120m▪{RST}", end="")
        center_text("S.T.A.R. LABS — SYSTEMS ONLINE", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.09)
    clear()

# ═══════════════════════════════════════════════════════════════════
# LEX LUTHOR — vagues vertes corporate FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def lex_boot_fullscreen(duration=2.0):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        t = time.time() * 3
        for y in range(1, ROWS):
            wave = int(math.sin(y * 0.4 + t) * 10)
            width = COLS // 3 + abs(wave) * 2
            x = max(1, COLS // 2 - width // 2 + wave)
            color = "\033[38;2;57;255;20m" if y % 3 == 0 else "\033[38;2;30;120;10m"
            line = "█" * max(1, width // 3)
            print(f"\x1b[{y};{x}H{color}{line}{RST}", end="")
        center_text("L E X C O R P", ROWS // 2, "\033[1;92m")
        print(end="", flush=True)
        time.sleep(0.08)
    clear()

# ═══════════════════════════════════════════════════════════════════
# WONDER WOMAN — lasso tournoyant FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def lasso_fullscreen(duration=2.5):
    refresh_size()
    cx, cy = COLS // 2, ROWS // 2
    r_max = min(COLS // 3, ROWS // 2 - 2)
    end = time.time() + duration
    while time.time() < end:
        clear()
        r = r_max
        for k in range(0, 360, 12):
            a = k + time.time() * 300
            x = int(cx + r * math.cos(a * math.pi / 180))
            y = int(cy + r * math.sin(a * math.pi / 180) * 0.5)
            if 0 < x < COLS and 0 < y < ROWS:
                print(f"\x1b[{y};{x}H\033[1;93m*{RST}", end="")
        # cercles concentriques
        for rr in range(3, r_max, 3):
            for k in range(0, 360, 30):
                a = k + time.time() * 200
                x = int(cx + rr * math.cos(a * math.pi / 180))
                y = int(cy + rr * math.sin(a * math.pi / 180) * 0.5)
                if 0 < x < COLS and 0 < y < ROWS:
                    print(f"\x1b[{y};{x}H\033[38;2;200;170;0m·{RST}", end="")
        center_text("LA VÉRITÉ", cy, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.05)
    clear()

# ═══════════════════════════════════════════════════════════════════
# AQUAMAN — vagues FULLSCREEN + bulles qui montent
# ═══════════════════════════════════════════════════════════════════
def waves_fullscreen(duration=2.5):
    refresh_size()
    bubbles = [(random.randint(1, COLS), random.randint(ROWS, ROWS * 2)) for _ in range(30)]
    end = time.time() + duration
    while time.time() < end:
        clear()
        # vagues par vagues
        for y in range(1, ROWS):
            t = time.time() * 3
            for x in range(1, COLS, 2):
                if (x + int(t * 4) + y * 2) % 8 < 3:
                    color = "\033[38;2;64;224;208m" if y < ROWS // 2 else "\033[38;2;0;150;150m"
                    print(f"\x1b[{y};{x}H{color}~{RST}", end="")
        # bulles qui montent
        for i, (bx, by) in enumerate(bubbles):
            by -= 1
            if by < 1: by = ROWS; bx = random.randint(1, COLS)
            print(f"\x1b[{by};{bx}H\033[38;2;100;255;200m○{RST}", end="")
            bubbles[i] = (bx, by)
        center_text("T R I D E N T", ROWS // 2, "\033[1;96m")
        print(end="", flush=True)
        time.sleep(0.1)
    clear()

# ═══════════════════════════════════════════════════════════════════
# CONSTANTINE — bougie + fumée FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def candle_fullscreen(duration=2.5):
    refresh_size()
    cx = COLS // 2
    end = time.time() + duration
    while time.time() < end:
        clear()
        # fumée qui monte dans tout l'écran
        for _ in range(random.randint(30, 50)):
            x = random.randint(1, COLS)
            y = random.randint(1, ROWS - 4)
            color = random.choice(["\033[38;2;50;50;50m", "\033[38;2;70;70;70m", "\033[38;2;90;90;90m"])
            print(f"\x1b[{y};{x}H{color}{'░▒▓'[:random.randint(1,3)]}{RST}", end="")
        # la bougie
        h = random.randint(3, 8)
        print(f"\x1b[{ROWS - 4};{cx - 1}H\033[1;93m██{RST}", end="")
        for i in range(h):
            print(f"\x1b[{ROWS - 4 - i};{cx}H\033[38;2;255;170;60m█{RST}", end="")
        print(f"\x1b[{ROWS - 4 - h};{cx}H\033[1;93m▲{RST}", end="")
        center_text("l'ombre t'appelle", ROWS - 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.1)
    clear()

# ═══════════════════════════════════════════════════════════════════
# RAVEN — fumée violette FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def raven_fullscreen(duration=2.0):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        for _ in range(random.randint(40, 60)):
            x = random.randint(1, COLS - 3)
            y = random.randint(1, ROWS)
            color = random.choice(["\033[38;2;80;0;120m", "\033[38;2;40;0;60m", "\033[38;2;120;50;180m"])
            print(f"\x1b[{y};{x}H{color}{'░▒▓'[:random.randint(1,3)]}{RST}", end="")
        center_text("RAVEN — L'OMBRE", ROWS // 2, "\033[1;95m")
        print(end="", flush=True)
        time.sleep(0.08)
    clear()

# ═══════════════════════════════════════════════════════════════════
# WARWORLD — rouages FULLSCREEN + alerte
# ═══════════════════════════════════════════════════════════════════
def war_gears_fullscreen(duration=2.0):
    refresh_size()
    chars = "▚▞▙▟▛▜"
    end = time.time() + duration
    while time.time() < end:
        clear()
        for _ in range(random.randint(60, 90)):
            x = random.randint(1, COLS - 3)
            y = random.randint(1, ROWS)
            color = random.choice(["\033[38;2;255;70;40m", "\033[38;2;255;140;0m", "\033[38;2;200;80;20m"])
            print(f"\x1b[{y};{x}H{color}{random.choice(chars) * 3}{RST}", end="")
        center_text("W A R W O R L D — L ' A R S E N A L", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.1)
    clear()

def alert_fullscreen(ms=1.0):
    refresh_size()
    for _ in range(int(ms / 0.1)):
        fill_bg((140, 20, 10), 1.0)
        time.sleep(0.08)
        clear()
        time.sleep(0.07)
    clear()

# ═══════════════════════════════════════════════════════════════════
# SUPERMAN — vol FULLSCREEN + vision thermique
# ═══════════════════════════════════════════════════════════════════
def superman_fullscreen(duration=2.5):
    refresh_size()
    end = time.time() + duration
    stars = [(random.randint(1, COLS), random.randint(1, ROWS)) for _ in range(50)]
    while time.time() < end:
        clear()
        for x, y in stars:
            print(f"\x1b[{y};{x}H\033[38;2;100;160;255m·{RST}", end="")
        # le S qui traverse
        t = (time.time() - end + duration) / duration
        sx = int(COLS * t)
        sy = ROWS // 2 + int(math.sin(t * 6) * ROWS // 4)
        if 0 < sx < COLS and 0 < sy < ROWS:
            print(f"\x1b[{sy};{max(1, sx - 3)}H\033[38;2;255;60;60m━━{RST}")
            print(f"\x1b[{sy};{sx}H\033[1;94mS{RST}", end="")
            print(f"\x1b[{sy};{sx + 1}H\033[38;2;255;60;60m━━{RST}", end="")
        print(end="", flush=True)
        time.sleep(0.06)
    clear()

# ═══════════════════════════════════════════════════════════════════
# DAILY PLANET — globe qui tourne FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def globe_fullscreen(duration=2.5):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        t = time.time() * 2
        for y in range(2, ROWS - 2):
            width = int(abs(math.sin(t + y * 0.25)) * (COLS // 3) + 4)
            offset = max(1, COLS // 2 - width // 2)
            color = "\033[38;2;100;160;255m"
            line = "░" * max(1, width)
            print(f"\x1b[{y};{offset}H{color}{line}{RST}", end="")
        for _ in range(random.randint(5, 10)):
            print(f"\x1b[{random.randint(1,ROWS)};{random.randint(1,COLS)}H\033[38;2;255;215;0m✦{RST}", end="")
        center_text("DAILY PLANET — LA VEILLE", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.08)
    clear()

# ═══════════════════════════════════════════════════════════════════
# SCARECROW — épouvantail + fumée orange
# ═══════════════════════════════════════════════════════════════════
def scarecrow_fullscreen(duration=2.5):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        for _ in range(random.randint(30, 45)):
            x = random.randint(1, COLS - 3)
            y = random.randint(1, ROWS)
            color = random.choice(["\033[38;2;255;140;48m", "\033[38;2;200;100;30m", "\033[38;2;255;190;100m"])
            print(f"\x1b[{y};{x}H{color}{'░▒'[:random.randint(1,2)]}{RST}", end="")
        center_text("SCARECROW — LA PEUR EST UN CHOIX", ROWS // 2, "\033[1;93m")
        print(end="", flush=True)
        time.sleep(0.09)
    clear()

# ═══════════════════════════════════════════════════════════════════
# CATWOMAN — bijoux scintillants FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def catwoman_fullscreen(duration=2.0):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        for _ in range(random.randint(25, 40)):
            x = random.randint(1, COLS)
            y = random.randint(1, ROWS)
            g = random.choice("◆◇✦✧◇◆💎")
            print(f"\x1b[{y};{x}H\033[38;2;255;220;0m{g}{RST}", end="")
        center_text("CATWOMAN — LA NUIT M'APPARTIENT", ROWS // 2, "\033[1;93m")
        print(end="", flush=True)
        time.sleep(0.1)
    clear()

# ═══════════════════════════════════════════════════════════════════
# H.I.V.E. — abeilles + or FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def hive_fullscreen(duration=2.0):
    refresh_size()
    end = time.time() + duration
    bees = [(random.randint(1, COLS), random.randint(1, ROWS)) for _ in range(40)]
    while time.time() < end:
        clear()
        cx, cy = COLS // 2, ROWS // 2
        for dy in range(-2, 3):
            print(f"\x1b[{cy+dy};{cx-5}H\033[38;2;255;200;0m{'▓▒░' * 4}{RST}", end="")
        for i, (bx, by) in enumerate(bees):
            dx = (cx - bx) // max(1, abs(cx - bx)) if bx != cx else 0
            dy = (cy - by) // max(1, abs(cy - by)) if by != cy else 0
            nbx, nby = bx + dx, by + dy
            if nbx == cx and nby == cy: nbx, nby = random.randint(1, COLS), random.randint(1, ROWS)
            print(f"\x1b[{nby};{nbx}H\033[38;2;255;140;0m♪{RST}", end="")
            bees[i] = (nbx, nby)
        center_text("H.I.V.E. — LA RUCHE", ROWS // 2 - 4, "\033[1;93m")
        print(end="", flush=True)
        time.sleep(0.1)
    clear()

# ═══════════════════════════════════════════════════════════════════
# CYBORG — scanlines + circuits FULLSCREEN
# ═══════════════════════════════════════════════════════════════════
def cyborg_fullscreen(duration=2.0):
    refresh_size()
    end = time.time() + duration
    while time.time() < end:
        clear()
        y_scan = random.randint(1, ROWS - 1)
        print(f"\x1b[{y_scan};1H\033[38;2;0;200;255m" + "═" * COLS + RST, end="")
        for _ in range(random.randint(20, 30)):
            print(f"\x1b[{random.randint(1,ROWS)};{random.randint(1,COLS-1)}H"
                  + random.choice(["\033[38;2;0;200;255m", "\033[38;2;180;255;120m"])
                  + random.choice(["┌", "┐", "└", "┘", "─", "│", "▪"]) + RST, end="")
        center_text("S Y S T E M S  O N L I N E", ROWS // 2, "\033[1;97m")
        print(end="", flush=True)
        time.sleep(0.08)
    clear()

# ═══════════════════════════════════════════════════════════════════
# menu template FULLSCREEN — s'adapte à la taille du terminal
# ═══════════════════════════════════════════════════════════════════
def fullscreen_menu(title, color, tools, header_char="═"):
    refresh_size()
    clear()
    # header
    print(f"\x1b[1;1H{color}{header_char * COLS}{RST}")
    ty = 2
    t = f"{title} · POWERED BY MAXIME LEAL"
    tx = max(1, (COLS - len(t)) // 2)
    print(f"\x1b[{ty};{tx}H{color}{t}{RST}")
    print(f"\x1b[{ty + 1};1H{color}{header_char * COLS}{RST}")
    # tools
    for i, (name, desc, _) in enumerate(tools):
        ly = ty + 3 + i
        if ly > ROWS - 4: break
        print(f"\x1b[{ly};3H{color}[{i+1:>2}]{RST} {name:<26} {DIM}{desc}{RST}", end="")
    # footer
    print(f"\x1b[{ROWS - 1};3H{DIM}[n] suivant  [p] précédent  [q] quitter{RST}", end="", flush=True)

DIM = "\033[2m"

# ═══════════════════════════════════════════════════════════════════
# export
# ═══════════════════════════════════════════════════════════════════
ALL_ANIMATIONS = {
    "batman": batman_intro, "batman_transition": batman_transition,
    "flash": flash_intro, "speed_lines": speed_lines_fullscreen,
    "joker": joker_intro, "matrix": matrix_rain_fullscreen,
    "star_labs": star_scanlines, "lex_luthor": lex_boot_fullscreen,
    "wonder_woman": lasso_fullscreen, "aquaman": waves_fullscreen,
    "constantine": candle_fullscreen, "raven": raven_fullscreen,
    "warworld": war_gears_fullscreen, "superman": superman_fullscreen,
    "daily_planet": globe_fullscreen, "scarecrow": scarecrow_fullscreen,
    "catwoman": catwoman_fullscreen, "hive": hive_fullscreen,
    "cyborg": cyborg_fullscreen, "alert": alert_fullscreen,
}

if __name__ == "__main__":
    hid()
    refresh_size()
    print(f"terminal: {COLS}x{ROWS}")
    anims = list(ALL_ANIMATIONS.keys())
    for name in anims:
        center_text(f"▶ {name.upper()}", 1, "\033[1;97m")
        ALL_ANIMATIONS[name](2.0)
        clear()
    show()
    print(f"\n{COLS}x{ROWS} — {len(anims)} animations fullscreen testées ✓\n")
