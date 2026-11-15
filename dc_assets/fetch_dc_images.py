#!/usr/bin/env python3
# language: Python 3, file: fetch_dc_images.py, target: macOS
# Télécharge les VRAIES images DC depuis Wikipedia (API REST)
import urllib.request, urllib.parse, json, os, shutil

OUT = os.path.expanduser("~/Desktop/tool_DC/dc_assets/logos_real")
os.makedirs(OUT, exist_ok=True)

CHARACTERS = [
    ("Batman", "batman"),
    ("Flash (DC Comics)", "flash"),
    ("Superman", "superman"),
    ("Aquaman", "aquaman"),
    ("Wonder Woman", "wonder_woman"),
    ("Cyborg (DC Comics)", "cyborg"),
    ("Lex Luthor", "lex_luthor"),
    ("Deathstroke", "deathstroke"),
    ("Raven (DC Comics)", "raven"),
    ("John Constantine", "constantine"),
    ("Joker (character)", "joker"),
    ("Green Lantern", "green_lantern"),
]

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DailyPlanet/1.0"}

def fetch_wiki_image(title, filename):
    """Récupère l'image principale de l'article Wikipedia"""
    try:
        encoded = urllib.parse.quote(title, safe='')
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        req = urllib.request.Request(api_url, headers=headers)
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())

        # essaie originalimage d'abord (haute résolution)
        img_url = d.get("originalimage", {}).get("source") or d.get("thumbnail", {}).get("source")
        if not img_url:
            return f"pas d'image pour {title}"

        # télécharge l'image
        out_path = os.path.join(OUT, f"{filename}_wiki.png")
        req2 = urllib.request.Request(img_url, headers=headers)
        img_data = urllib.request.urlopen(req2, timeout=15).read()
        open(out_path, "wb").write(img_data)
        return f"OK {len(img_data)} octets — {out_path}"
    except Exception as e:
        return f"ERREUR: {e}"

def fetch_fandom_image(char_name, filename):
    """Récupère depuis le DC Database (Fandom) via leur API"""
    try:
        encoded = urllib.parse.quote(char_name.replace(" ", "_"))
        api_url = f"https://dc.fandom.com/api.php?action=query&titles={encoded}&prop=pageimages&format=json&pithumbsize=500"
        req = urllib.request.Request(api_url, headers=headers)
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        pages = d.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            thumb = page.get("thumbnail", {}).get("source", "")
            if thumb:
                out_path = os.path.join(OUT, f"{filename}_fandom.png")
                req2 = urllib.request.Request(thumb, headers=headers)
                img_data = urllib.request.urlopen(req2, timeout=15).read()
                open(out_path, "wb").write(img_data)
                return f"OK {len(img_data)} octets — {out_path}"
        return f"pas d'image Fandom pour {char_name}"
    except Exception as e:
        return f"ERREUR Fandom: {e}"

print("=== TÉLÉCHARGEMENT DES IMAGES DC ===\n")

for title, filename in CHARACTERS:
    print(f"  {filename}...")
    r1 = fetch_wiki_image(title, filename)
    print(f"    wiki   : {r1}")
    r2 = fetch_fandom_image(title, filename)
    print(f"    fandom : {r2}")

print("\n=== VÉRIFICATION ===")
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    size = os.path.getsize(fp)
    with open(fp, "rb") as fh:
        magic = fh.read(8)
    is_img = magic[:4] == b'\x89PNG' or magic[:2] == b'\xff\xd8'
    fmt = "PNG" if magic[:4] == b'\x89PNG' else ("JPEG" if magic[:2] == b'\xff\xd8' else "HTML/ERROR")
    status = "✓" if is_img else "✗"
    print(f"  {status} {f:<30} {size:>8,} o  [{fmt}]")

print(f"\nTotal images valides: {sum(1 for f in os.listdir(OUT) if open(os.path.join(OUT,f),'rb').read(4)[:4] in (b'\\x89PNG', b'\\xff\\xd8') for f in [f])}")
