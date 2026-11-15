#!/usr/bin/env python3
# language: Python 3, file: recrop_faces.py, target: macOS
# Cadrage serré centré sur le visage — valeurs mesurées et vérifiées visuellement
import os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
FACES = os.path.join(HERE, "faces")
os.makedirs(FACES, exist_ok=True)

def dims(p):
    w = h = 0
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        if "pixelWidth" in line: w = int(line.split()[-1])
        if "pixelHeight" in line: h = int(line.split()[-1])
    return w, h

def crop(src, out_name, top_frac, height_frac, cx_frac, out_size=500):
    src = src if os.path.isabs(src) else os.path.join(IMG, src)
    if not os.path.exists(src):
        print(f"  ✗ {out_name} — source manquante"); return False
    w, h = dims(src)
    if w == 0 or h == 0:
        print(f"  ✗ {out_name} — dims illisibles"); return False
    ch = max(1, int(h * height_frac))
    cw = min(w, max(1, int(ch * 0.95)))
    off_y = max(0, int(h * top_frac))
    off_x = max(0, min(w - cw, int(w * cx_frac - cw / 2)))
    out = os.path.join(FACES, out_name)
    tmp = out + ".tmp"
    subprocess.run(["sips", "-c", str(ch), str(cw), "--cropOffset", str(off_y), str(off_x),
                    src, "--out", tmp], capture_output=True, text=True)
    subprocess.run(["sips", "-z", str(out_size), str(out_size), tmp, "--out", out],
                   capture_output=True, text=True)
    os.remove(tmp)
    print(f"  ✓ {out_name}  y={off_y}+{ch} x={off_x}+{cw}")
    return True

# (source, sortie, top, hauteur, centre_x) — cadrage serré sur la tête
JOBS = [
    ("batman_wiki.png",       "batman_face.png",       0.20, 0.18, 0.47),
    ("flash_wiki.png",        "flash_face.png",        0.12, 0.22, 0.54),
    ("superman_wiki.png",     "superman_face.png",     0.015, 0.16, 0.55),
    ("aquaman_wiki.png",      "aquaman_face.png",      0.07, 0.22, 0.44),
    ("wonder_woman_real.png", "wonder_woman_face.png", 0.44, 0.20, 0.50),
    ("cyborg_wiki.png",       "cyborg_face.png",       0.09, 0.22, 0.63),
    ("lex_luthor_wiki.png",   "lex_luthor_face.png",   0.07, 0.18, 0.44),
    ("raven_wiki.png",        "raven_face.png",        0.18, 0.20, 0.50),
    ("joker_wiki.png",        "joker_face.png",        0.37, 0.20, 0.58),
    ("catwoman.png",          "catwoman_face.png",     0.16, 0.22, 0.37),
    ("scarecrow_face.png",    "scarecrow_face.png",    0.13, 0.22, 0.62),
    ("league_shadows.png",    "league_face.png",       0.30, 0.20, 0.47),
    ("kryptonite_dc.png",     "kryptonite_face.png",   0.12, 0.75, 0.50),
    ("wargames_movie.png",    "wopr_face.png",         0.02, 0.40, 0.50),
    ("the_matrix_face.png",   "matrix_face.png",       0.13, 0.20, 0.51),
    (os.path.join(IMG, "images", "forcegalaxy_face.png"),
                              "force_face.png",        0.14, 0.26, 0.53),
]

print("=== RECROP SERRÉ ===")
ok = sum(1 for s, o, t, hh, cx in JOBS if crop(s, o, t, hh, cx))
print(f"{ok}/{len(JOBS)} OK")
