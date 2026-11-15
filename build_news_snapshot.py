#!/usr/bin/env python3
# language: Python 3, file: build_news_snapshot.py, target: macOS
# Génère un snapshot du journal Daily Planet (statique) → docs/DailyPlanet/journal.html
# Utilisé par le cron GitHub Actions pour que le site public affiche les actus du jour.
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "DailyPlanet"))
import veille

DOCS = os.path.join(ROOT, "docs", "DailyPlanet")
os.makedirs(DOCS, exist_ok=True)

data = veille.fetch_all(force=True)
html = veille.render(data)

# sur GitHub Pages les liens relatifs /img, /globe pointent vers le serveur local :
# on les neutralise pour la version statique (les vignettes ne s'affichent pas,
# mais le layout, filtres et titres restent — le journal vivant reste sur :8088)
html = html.replace('src="/img?u=', 'src="" data-u="').replace('src="/globe"', 'src="../faces/dailyplanet_face.jpg"')
path = os.path.join(DOCS, "journal.html")
open(path, "w", encoding="utf-8").write(html)
print(f"journal snapshot : {len(data.get('items', []))} actus → {path}")
