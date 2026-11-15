#!/usr/bin/env python3
# language: Python 3, file: download_hd.py, target: macOS
# Télécharge des images HAUTE RÉSOLUTION (portraits HD) pour chaque perso du site
# Sources : DC Database (Fandom, API) pour les comics · Wikipedia pour les films
import json, os, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "images_hd")
os.makedirs(OUT, exist_ok=True)

UA = ("ArsenalDC/1.0 (personnel; contact: local) python-urllib")
WIKI = "https://en.wikipedia.org/w/api.php"
FANDOM = "https://dc.fandom.com/api.php"

def api_thumb(api, title, size=2400):
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "redirects": "1",
        "titles": title, "prop": "pageimages", "pithumbsize": str(size)})
    req = urllib.request.Request(f"{api}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.load(r)
    pages = data.get("query", {}).get("pages", {})
    for p in pages.values():
        t = p.get("thumbnail", {})
        if t.get("source"):
            return t["source"], t.get("width", 0), t.get("height", 0)
    return None, 0, 0

def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://dc.fandom.com/"})
    with urllib.request.urlopen(req, timeout=40) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)

# (nom du fichier final, wiki, titre de page, fallback titre)
JOBS = [
    ("batman.png",       FANDOM, "Batman (Bruce Wayne)",  "Batman"),
    ("flash.png",        FANDOM, "Barry Allen",           "Flash"),
    ("superman.png",     FANDOM, "Superman (Clark Kent)", "Superman"),
    ("aquaman.png",      FANDOM, "Aquaman (Arthur Curry)","Aquaman"),
    ("wonder_woman.png", FANDOM, "Wonder Woman",          "Wonder Woman (Diana Prince)"),
    ("cyborg.png",       FANDOM, "Victor Stone",          "Cyborg"),
    ("lex_luthor.png",   FANDOM, "Alexander Luthor",      "Lex Luthor"),
    ("raven.png",        FANDOM, "Rachel Roth",           "Raven"),
    ("joker.png",        FANDOM, "Joker",                 "Joker (Prime Earth)"),
    ("catwoman.png",     FANDOM, "Selina Kyle",           "Catwoman"),
    ("scarecrow.png",    FANDOM, "Jonathan Crane",        "Scarecrow"),
    ("league.png",       FANDOM, "Ra's al Ghul",          "Ra's al Ghul (New Earth)"),
    ("kryptonite.png",   FANDOM, "Kryptonite",            None),
    ("wopr.png",         WIKI,   "WarGames",              None),
    ("matrix.png",       WIKI,   "The Matrix",            None),
    ("force.png",        WIKI,   "Star Wars: The Force Awakens", None),
]

print(f"=== TÉLÉCHARGEMENT HD → {OUT} ===")
ok = fail = 0
for fname, api, title, fb in JOBS:
    dest = os.path.join(OUT, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        print(f"  ✓ {fname} déjà présent ({os.path.getsize(dest)//1024} KB)")
        ok += 1
        continue
    url = w = h = None
    for t in filter(None, (title, fb)):
        try:
            url, w, h = api_thumb(api, t)
            if url: break
        except Exception as e:
            print(f"    api '{t}' : {e}")
        time.sleep(1.2)
    if not url:
        print(f"  ✗ {fname} — pas de thumb"); fail += 1; continue
    try:
        n = download(url, dest)
        print(f"  ✓ {fname} {w}×{h} ({n//1024} KB)")
        ok += 1
    except Exception as e:
        print(f"  ✗ {fname} — download : {e}")
        fail += 1
    time.sleep(1.5)
print(f"\n{ok} OK · {fail} échecs")
