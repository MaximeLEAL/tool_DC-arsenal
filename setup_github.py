#!/usr/bin/env python3
# language: Python 3, file: setup_github.py, target: macOS
# GITHUB SETUP — initialise le dépôt git, crée le repo GitHub, push tout l'arsenal
# Usage: python3 setup_github.py <github_username> [nom_du_repo]
import os, sys, subprocess, json

TOOL_DC = os.path.expanduser("~/Desktop/tool_DC")
GITHUB_USER = sys.argv[1] if len(sys.argv) > 1 else ""
REPO_NAME = sys.argv[2] if len(sys.argv) > 2 else "tool_DC-arsenal"

if not GITHUB_USER:
    print("usage: python3 setup_github.py <github_username> [repo_name]")
    print("       ex: python3 setup_github.py MaximeLeal")
    sys.exit(1)

GITHUB_URL = f"https://github.com/{GITHUB_USER}/{REPO_NAME}"

def run(cmd, show=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=TOOL_DC)
    if show and r.stdout: print(r.stdout[:500])
    if show and r.stderr: print(r.stderr[:300])
    return r

# 1. .gitignore — exclut les gros binaires et fichiers temporaires
gitignore = """__pycache__/
*.pyc
*.o
*.exe
*.dll
*.bin
*.wav
*.bmp
*.png
*.jpg
.DS_Store
node_modules/
WOPR_Lab/
sorties/bots/
arsenal_web_pages/
Reception/
RickCTF.command
RickPortal_win.zip
*.unpacked
"""
gi = os.path.join(TOOL_DC, ".gitignore")
open(gi, "w").write(gitignore)
print("[OK] .gitignore écrit")

# 2. README principal pour le repo
readme = f"""# ⚡ TOOL DC ARSENAL — powered by Maxime Leal

**26 kits · ~240 tools · l'arsenal cyber complet dans un seul dépôt**

---

## L'ARSENAL

| # | Kit | Tools | Description |
|---|---|---|---|
| 1 | 🟢 RickPortal | 10 | Kit malware complet (keylogger, RAT, ransomware, worms) |
| 2 | ⚡ FlashToolSuper | 55 | OSINT, malware, phishing, réseau, badusb, système |
| 3 | 🦇 BatCave | 31 | Investigation, crypto, sniffing, alertes |
| 4 | 🃏 JokerChaos | 8 | Chaos-prank |
| 5 | 🔱 TridentAquaman | 8 | Réseau graphique |
| 6 | 🦸 SupermanVision | 8 | Vision système |
| 7 | 🕯️ ConstantineDark | 10 | Dark web |
| 8 | 🪢 LassoVerite | 8 | Vérification |
| 9 | 🤖 CyborgTech | 8 | Intégration |
| 10 | 🏢 LexCorpIndustries | 7 | Arsenal Windows (injection, ransomware, crypter) |
| 11 | 🔬 STARLabs | 5 | C2 DNS + HTTP framework |
| 12 | 🎯 TaskForceX | 2 | SSH worm + APK Android |
| 13 | 💊 NeoMatrix | 10 | La matrice |
| 14 | 🌟 ForceGalaxy | 8 | La galaxie |
| 15 | 🐱 CatwomanVoleuse | 8 | Secrets (wifi, browser, SSH, DPAPI) |
| 16 | 🍯 HiveMining | 8 | Minage crypto |
| 17 | 🎃 ScarecrowPhish | 6 | Phishing (12 sites + miroir MS) |
| 18 | ⚔️ WarWorld | 110 | Arsenal (16 thèmes, registre complet) |
| 19 | 🥷 LeagueOfShadows | 3 | Orchestrateur de campagnes |
| 20 | 🟩 KryptoniteSuite | 4 | Défense (scan IOCs → Sigma/YARA) |
| 21 | 🎮 WOPR | 4 | Auto-lab CTF WarGames |
| 22 | 📊 TheCalculator | 2 | Breach analytics |
| 23 | 🐦‍⬛ RavenEvasion | 5 | Évasion EDR (syscalls, unhook, ETW, AMSI) |
| 24 | 🧠 TheThinker | 8 | Reverse engineering lab |
| 25 | 🂡 JokerCard | 4 | SGP Card Joker (ESP32-S3 BadUSB) |
| 26 | 📰 DailyPlanet | 2 | Veille tech & cyber (25 sources) |

---

## LANCEMENT RAPIDE

```bash
cd ~/Desktop/tool_DC
# Le Batcomputer Suprême (interface web — 26 kits en un écran)
python3 batcomputer_supreme.py 9000

# Ou un kit spécifique
cd FlashToolSuper && python3 flash_tool.py
cd BatCave && python3 bat_tool.py
cd ScarecrowPhish && python3 epouvanteur.py
```

## CHAQUE TOOL A SA PAGE WEB

Les pages sont générées dans `arsenal_web_pages/` :
```
python3 generate_all_pages.py
open arsenal_web_pages/index.html
```

---

## COMPILATION

### macOS
```bash
cd RickPortal && ./build_mac.sh
cd FlashToolSuper && python3 flash_tool.py  # page MALWARE, tool 1
```

### Windows (cross-compile)
```bash
cd LexCorpIndustries && zsh verify_lex.zsh
cd RickPortal && zsh verify_build.zsh
```

---

## SÉCURITÉ

Cet arsenal est conçu pour:
- La formation en cybersécurité
- Les CTF (Capture The Flag)
- Les tests d'intrusion autorisés
- La recherche en sécurité offensive

**Utilise-le uniquement sur des machines que tu possèdes ou as l'autorisation de tester.**

---

*Powered by Maxime Leal*
"""
open(os.path.join(TOOL_DC, "README.md"), "w").write(readme)
print("[OK] README.md écrit")

# 3. init git
run("git init", show=False)
print("[OK] git init")

# 4. git config si nécessaire
run('git config user.name "Maxime Leal"')
run('git config user.email "maxime.leal@users.noreply.github.com"')

# 5. git add + commit
run("git add -A")
r = run('git commit -m "⚡ ARSENAL DC COMPLET — 26 kits · ~240 tools · powered by Maxime Leal"', show=True)

# 6. branche main
run("git branch -M main")

# 7. crée le repo GitHub avec gh
r = run(f'gh repo create {REPO_NAME} --public --source=. --push --description "⚡ Arsenal DC — 26 kits · 240 tools · powered by Maxime Leal"')
if r.returncode == 0:
    print(f"\n{'=' * 60}")
    print(f"  ✓ DÉPÔT GITHUB CRÉÉ : {GITHUB_URL}")
    print(f"  ✓ TOUT L'ARSENAL EST EN LIGNE")
    print(f"{'=' * 60}")
    print(f"\n  Le lien GitHub de chaque tool dans les pages web pointe maintenant")
    print(f"  vers https://github.com/{GITHUB_USER}/{REPO_NAME}/tree/main/<Kit>")
else:
    print("\n[!] le repo n'a pas pu être créé automatiquement.")
    print("    1. connecte-toi : gh auth login")
    print("    2. relance : python3 setup_github.py " + GITHUB_USER)
    print(f"    3. ou crée le repo manuellement sur github.com/new puis :")
    print(f"       git remote add origin https://github.com/{GITHUB_USER}/{REPO_NAME}.git")
    print(f"       git push -u origin main")
