#!/usr/bin/env python3
"""
download_ctf_images.py
Lance : python3 download_ctf_images.py
Crée  : images/ avec les 23 fichiers
"""
import urllib.request, pathlib, time, sys

OUT = pathlib.Path("images")
OUT.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")

IMAGES = [
    # 1 Rick Portal
    ("rickportal_face.png",
     "https://upload.wikimedia.org/wikipedia/en/b/b0/Rick_and_Morty_season_1.jpg"),
    # 2 Batman
    ("batcave_face.png",
     "https://upload.wikimedia.org/wikipedia/en/8/87/Batman_DC_Comics.png"),
    # 3 Aquaman
    ("tridentaquaman_face.png",
     "https://upload.wikimedia.org/wikipedia/en/5/50/Aquaman_2018_film_poster.jpg"),
    # 4 Superman
    ("supermanvision_face.png",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Superman_Shield.svg/440px-Superman_Shield.svg.png"),
    # 5 Constantine
    ("constantinedark_face.png",
     "https://upload.wikimedia.org/wikipedia/en/8/8d/Constantine2005.jpg"),
    # 6 Wonder Woman
    ("lassoverite_face.png",
     "https://upload.wikimedia.org/wikipedia/en/8/80/Wonder_Woman_2017_film_poster.jpg"),
    # 7 Lex Luthor / LexCorp
    ("lexcorpindustries_face.png",
     "https://upload.wikimedia.org/wikipedia/en/7/7f/Batman_v_Superman_Dawn_of_Justice_theatrical_poster.jpg"),
    # 8 STAR Labs
    ("starlabs_face.png",
     "https://upload.wikimedia.org/wikipedia/en/c/c2/The_Flash_season_1_poster.jpg"),
    # 9 Raven
    ("ravenevasion_face.png",
     "https://upload.wikimedia.org/wikipedia/en/5/55/Titans_TV_series_poster.jpg"),
    # 10 The Thinker (Rodin, domaine public)
    ("thethinker_face.png",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Rodin_TheThinker.jpg/440px-Rodin_TheThinker.jpg"),
    # 11 Scarecrow
    ("scarecrowphish_face.png",
     "https://upload.wikimedia.org/wikipedia/en/1/1f/Batman_Begins_Teaser_Poster.jpg"),
    # 12 Catwoman
    ("catwomanvoleuse_face.png",
     "https://upload.wikimedia.org/wikipedia/en/5/5c/Catwoman_2004_film_poster.jpg"),
    # 13 Hive / abeilles
    ("hivemining_face.png",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Apis_mellifera_flying2.jpg/440px-Apis_mellifera_flying2.jpg"),
    # 14 Deathstroke / WarWorld
    ("warworld_face.png",
     "https://upload.wikimedia.org/wikipedia/en/a/a9/Suicide_Squad_2016_film_poster.jpg"),
    # 15 League of Shadows
    ("leagueofshadows_face.png",
     "https://upload.wikimedia.org/wikipedia/en/5/5e/The_Dark_Knight_Rises_Theatrical_Poster.jpg"),
    # 16 Kryptonite
    ("kryptonitesuite_face.png",
     "https://upload.wikimedia.org/wikipedia/en/e/e0/Superman_Returns_poster.jpg"),
    # 17 WOPR WarGames
    ("wopr_face.png",
     "https://upload.wikimedia.org/wikipedia/en/5/5e/WarGames.jpg"),
    # 18 The Calculator / cyber
    ("thecalculator_face.png",
     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/HAL9000.svg/440px-HAL9000.svg.png"),
    # 19 Task Force X / Suicide Squad
    ("taskforcex_face.png",
     "https://upload.wikimedia.org/wikipedia/en/a/a9/Suicide_Squad_2016_film_poster.jpg"),
    # 20 Joker Card
    ("jokercard_face.png",
     "https://upload.wikimedia.org/wikipedia/en/a/a2/Joker_2019_film_poster.jpg"),
    # 21 Daily Planet
    ("dailyplanet_face.png",
     "https://upload.wikimedia.org/wikipedia/en/0/0c/Man_of_Steel_theatrical_poster.jpg"),
    # 22 Force Galaxy / Star Wars
    ("forcegalaxy_face.png",
     "https://upload.wikimedia.org/wikipedia/en/a/a2/Star_Wars_The_Force_Awakens_Theatrical_Poster.jpg"),
    # 23 Neo Matrix
    ("neomatrix_face.png",
     "https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg"),
]

ok = 0
err = 0
failed = []

print(f"\n{'='*55}")
print(f"  CTF Images — {len(IMAGES)} fichiers → images/")
print(f"{'='*55}\n")

for fname, url in IMAGES:
    dest = OUT / fname
    sys.stdout.write(f"  {fname:<40} ")
    sys.stdout.flush()
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = r.read()
        dest.write_bytes(data)
        kb = len(data) // 1024
        print(f"✓ {kb} KB")
        ok += 1
    except Exception as e:
        print(f"✗ {e}")
        err += 1
        failed.append((fname, url))
    time.sleep(0.3)

print(f"\n{'='*55}")
print(f"  ✓ {ok}/{len(IMAGES)} téléchargés")
if err:
    print(f"  ✗ {err} erreurs\n")
    print("  Fichiers manquants — URLs de secours :")
    FALLBACK = {
        "batcave_face.png":
            "https://m.media-amazon.com/images/I/71niXI3lxoL._AC_SX679_.jpg",
        "supermanvision_face.png":
            "https://m.media-amazon.com/images/I/71Qn8t5WPLL._AC_SX679_.jpg",
        "starlabs_face.png":
            "https://m.media-amazon.com/images/I/81QpkIctqPL._AC_SX679_.jpg",
        "ravenevasion_face.png":
            "https://m.media-amazon.com/images/I/91vdWJlQtLL._AC_SX679_.jpg",
        "thecalculator_face.png":
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Social_Network_Analysis_Visualization.png/440px-Social_Network_Analysis_Visualization.png",
    }
    for fname, url in failed:
        fallback = FALLBACK.get(fname, url)
        print(f"  {fname}")
        print(f"    {fallback}")
        dest = OUT / fname
        try:
            req = urllib.request.Request(
                fallback, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            dest.write_bytes(data)
            print(f"    ✓ fallback OK")
            ok += 1
            err -= 1
        except Exception as e:
            print(f"    ✗ {e}")
    print()

print(f"  Dossier : {OUT.resolve()}")
print(f"{'='*55}\n")
