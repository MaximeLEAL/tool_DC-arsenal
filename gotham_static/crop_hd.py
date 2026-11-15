#!/usr/bin/env python3
# language: Python 3, file: crop_hd.py, target: macOS
# Recadre les visages HD → faces/ (800×800) — AVEC MARGE :
# le visage occupe ~55% du cadre, centré → la bande 300×196 de la carte le montre en entier
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "images_hd")
FACES = os.path.join(HERE, "faces")
os.makedirs(FACES, exist_ok=True)

def dims(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                         capture_output=True, text=True).stdout
    w = h = 0
    for line in out.splitlines():
        if "pixelWidth" in line: w = int(line.split()[-1])
        if "pixelHeight" in line: h = int(line.split()[-1])
    return w, h

def crop(src, out_name, top_frac, height_frac, cx_frac, out_size=800):
    src = os.path.join(SRC, src)
    if not os.path.exists(src):
        print(f"  ✗ {out_name}"); return False
    w, h = dims(src)
    ch = max(1, min(h, int(h * height_frac)))
    cw = min(w, max(1, int(ch * 0.98)))
    off_y = max(0, min(h - ch, int(h * top_frac)))
    off_x = max(0, min(w - cw, int(w * cx_frac - cw / 2)))
    out = os.path.join(FACES, out_name)
    tmp = out + ".tmp"
    subprocess.run(["sips", "-c", str(ch), str(cw), "--cropOffset", str(off_y), str(off_x),
                    src, "--out", tmp], capture_output=True, text=True)
    subprocess.run(["sips", "-z", str(out_size), str(out_size), tmp, "--out", out],
                   capture_output=True, text=True)
    os.remove(tmp)
    print(f"  ✓ {out_name}  y{off_y}+{ch} x{off_x}+{cw}")
    return True

# (source, sortie, top, hauteur, centre_x)
# top/hauteur/cx = où se trouve LE VISAGE dans la source ; marge autour → visage ~40% du cadre
JOBS = [
    ("batman.png",       "batman_face.png",       0.0,   0.425, 0.54),
    ("flash.png",        "flash_face.png",        0.05,  0.36,  0.43),
    ("superman.png",     "superman_face.png",     0.06,  0.34,  0.51),
    ("aquaman.png",      "aquaman_face.png",      0.12,  0.33,  0.46),
    ("wwross.png",       "wonder_woman_face.png", 0.27,  0.26,  0.49),
    ("cyborg_hd.png",    "cyborg_face.png",       0.05,  0.36,  0.49),
    ("lex_luthor.png",   "lex_luthor_face.png",   0.0,   0.70,  0.78),
    ("../images/raven_wiki.png", "raven_face.png",0.075, 0.35,  0.49),
    ("joker.png",        "joker_face.png",        0.01,  0.50,  0.36),
    ("catwoman.png",     "catwoman_face.png",     0.06,  0.29,  0.48),
    ("scarecrow.png",    "scarecrow_face.png",    0.01,  0.49,  0.61),
    ("league.png",       "league_face.png",       0.0,   0.80,  0.60),
    ("kryptonite.png",   "kryptonite_face.png",   0.0,   1.0,   0.165),
    ("matrix.png",       "matrix_face.png",       0.19,  0.30,  0.66),
    ("force.png",        "force_face.png",        0.07,  0.29,  0.44),
    ("wopr.png",         "wopr_face.png",         0.0,   0.75,  0.50),
    ("rick.png",         "rick_face.png",         0.0,   1.0,   0.58),
    ("constantine.png",  "constantine_face.png",  0.19,  0.32,  0.36),
    ("starlabs.png",     "starlabs_face.png",     0.05,  0.95,  0.50),
    ("taskforce.png",    "taskforce_face.png",    0.08,  0.60,  0.50),
    ("hive.png",         "hive_face.png",         0.10,  0.33,  0.47),
    ("warworld.png",     "warworld_face.png",     0.49,  0.30,  0.775),
    ("calculator.png",   "calculator_face.png",   0.37,  0.35,  0.495),
    ("thinker.png",      "thinker_face.png",      0.0,   0.48,  0.33),
    ("dailyplanet.png",  "dailyplanet_face.png",  0.0,   1.0,   0.415),
    ("jokercard.png",    "jokercard_face.png",    0.0,   1.0,   0.75),
]

if __name__ == "__main__":
    print("=== CROP HD FINAL → faces/ ===")
    ok = sum(1 for j in JOBS if crop(*j))
    print(f"{ok}/{len(JOBS)} OK")
