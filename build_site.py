#!/usr/bin/env python3
# language: Python 3, file: build_site.py, target: macOS
# Construit la version STATIQUE du site (index Gotham + 26 kits + 245 fiches tools + visages)
# pour publication GitHub Pages → docs/
import os, shutil, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "docs")
TPL = os.path.join(ROOT, "design_preview", "page_principale.html")
PAGES = os.path.join(ROOT, "arsenal_web_pages")
FACES = os.path.join(ROOT, "gotham_static", "faces")

# 1. repart de zéro
if os.path.isdir(SITE):
    shutil.rmtree(SITE)
os.makedirs(SITE)

# 2. pages des kits + fiches tools
shutil.copytree(PAGES, SITE, dirs_exist_ok=True)

# 3. visages
shutil.copytree(FACES, os.path.join(SITE, "faces"))

# 4. arsenal_dc.html (catalogue)
shutil.copy(os.path.join(ROOT, "arsenal_dc.html"), SITE)

# 5. index : le template Gotham + cartes générées dynamiquement (comme le serveur)
import sys
sys.path.insert(0, ROOT)
import gotham_full as G
index = G.build_index()
index = index.replace('src="/face/', 'src="faces/')
index = re.sub(r'href="/kit/([A-Za-z]+)"', r'href="\1/"', index)
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(index)

# 6. corrige les chemins des visages dans les pages kits/tools
n = 0
for dirpath, _, files in os.walk(SITE):
    for f in files:
        if not f.endswith(".html") or f == "index.html": continue
        p = os.path.join(dirpath, f)
        s = open(p, encoding="utf-8").read()
        s2 = s.replace("../../gotham_static/faces/", "../faces/")
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            n += 1
print(f"{n} pages corrigées")

# 7. snapshot du journal Daily Planet (statique, fraîchit à chaque build)
os.system(f"python3 {os.path.join(ROOT, 'build_news_snapshot.py')}")

# 7. stats
kits = [d for d in os.listdir(SITE) if os.path.isdir(os.path.join(SITE, d)) and d != "faces"]
tools = sum(len([f for f in os.listdir(os.path.join(SITE, k)) if f.endswith(".html") and f != "index.html"]) for k in kits)
print(f"site/docs : 1 index · {len(kits)} kits · {tools} fiches tools · {len(os.listdir(os.path.join(SITE, 'faces')))} visages")
