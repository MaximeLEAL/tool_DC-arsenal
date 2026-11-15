#!/usr/bin/env python3
# language: Python 3, file: fetch_all_faces.py, target: macOS
# Télécharge les VRAIES images (visages/têtes) des personnages DC depuis Wikipedia
# en utilisant les TITRES EXACTS des articles qui contiennent les images
import urllib.request, urllib.parse, json, os, time

OUT = os.path.expanduser("~/Desktop/tool_DC/gotham_static/images")
os.makedirs(OUT, exist_ok=True)
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) DailyPlanet/1.0"}

# TITRES WIKIPEDIA EXACTS qui contiennent les images des personnages
CHARACTERS = [
    # (titre_wikipedia, nom_fichier)
    ("Batman", "batman"),
    ("Batman (Christian Bale)", "batman_bale"),
    ("The Flash (2014 TV series)", "flash"),
    ("The Flash", "flash_comics"),
    ("Superman", "superman"),
    ("Superman (1978 film)", "superman_movie"),
    ("Aquaman", "aquaman"),
    ("Aquaman (film)", "aquaman_movie"),
    ("Wonder Woman", "wonder_woman"),
    ("Wonder Woman (2011 film)", "wonder_woman_movie"),
    ("Cyborg (comics)", "cyborg"),
    ("Lex Luthor", "lex_luthor"),
    ("Deathstroke", "deathstroke"),
    ("Raven (DC Comics)", "raven"),
    ("John Constantine", "constantine"),
    ("John Constantine (Hellblazer)", "constantine_hellblazer"),
    ("Joker (character)", "joker"),
    ("Joker (2019 film)", "joker_2019"),
    ("Green Lantern", "green_lantern"),
    ("Green Lantern (film)", "green_lantern_movie"),
    ("Catwoman", "catwoman"),
    ("Suicide Squad (2016 film)", "suicide_squad"),
    ("Justice League", "justice_league"),
    ("Justice League (film)", "justice_league_movie"),
    ("Harley Quinn", "harley_quinn"),
    ("Watchmen", "watchmen"),
    ("Kryptonite", "kryptonite"),
    ("League of Assassins", "league_of_assassins"),
    ("WarGames", "wargames"),
    ("Rick and Morty", "rick_and_morty"),
    ("The Matrix", "the_matrix"),
    ("Star Wars: The Force Awakens", "star_wars"),
    ("Star Trek", "star_trek"),
    ("Mr. Terrific (comics)", "mr_territific"),
    ("The Riddler", "the_riddler"),
    ("Scarecrow (DC Comics)", "scarecrow"),
    ("Two Face", "two_face"),
    ("Bane (DC Comics)", "bane"),
    ("Nightwing", "nightwing"),
    ("Red Hood", "red_hood"),
    ("Poison Ivy (character)", "poison_ivy"),
    ("Black Canary", "black_canary"),
    ("Martian Manhunter", "martian_manhunter"),
    ("Hawkman", "hawkman"),
    ("Doctor Fate", "doctor_fate"),
    ("Shazam!", "shazam"),
    ("Blue Beetle", "blue_beetle"),
    (" Booster Gold", "booster_gold"),
    ("Firestorm (comics)", "firestorm"),
    ("Zatanna", "zatanna"),
    ("Plastic Man", "plastic_man"),
    ("Atom (comics)", "the_atom"),
    ("Hawkgirl", "hawkgirl"),
    ("Stargirl (TV series)", "stargirl"),
    ("Peacemaker (comics)", "peacemaker"),
]

print("=== TÉLÉCHARGEMENT DES VISAGES DC ===\n")
ok = 0
fail = 0
for title, filename in CHARACTERS:
    try:
        encoded = urllib.parse.quote(title, safe='')
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
        req = urllib.request.Request(api_url, headers=headers)
        d = json.loads(urllib.request.urlopen(req, timeout=10).read())
        img_url = d.get("originalimage", {}).get("source") or d.get("thumbnail", {}).get("source")
        if not img_url:
            print(f"  ✗ {filename} — pas d'image"); fail += 1; continue
        out_path = os.path.join(OUT, f"{filename}_face.png")
        req2 = urllib.request.Request(img_url, headers=headers)
        img_data = urllib.request.urlopen(req2, timeout=15).read()
        magic = img_data[:4]
        valid = magic[:4] == b'\x89PNG' or magic[:2] == b'\xff\xd8'
        if not valid:
            print(f"  ✗ {filename} — pas une image (HTML)"); fail += 1; continue
        open(out_path, "wb").write(img_data)
        fmt = "PNG" if magic[:4] == b'\x89PNG' else "JPEG"
        print(f"  ✓ {filename}_face  [{fmt}] {len(img_data):,} o")
        ok += 1
        time.sleep(1.5)  # anti-429
    except Exception as e:
        print(f"  ✗ {filename} — {e}"); fail += 1

print(f"\n=== RÉSULTAT ===")
print(f"  ✓ téléchargées : {ok}")
print(f"  ✗ échecs       : {fail}")
print(f"\nLes images sont dans {OUT}")
