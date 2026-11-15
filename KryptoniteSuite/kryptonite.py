#!/usr/bin/env python3
# language: Python 3, file: kryptonite.py, target: macOS (et detection windows en regles)
# KRYPTONITE SUITE · powered by Maxime Leal
# Le renversement defensif : scanne une machine contre les IOCs des 20 kits, puis GENERE
# les regles Sigma et YARA correspondantes. Ton arsenal devient ta blue team.
# Usage: kryptonite.py scan | sigma | yara | catalog
import os, sys, json, subprocess, time
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "sorties")
os.makedirs(OUT, exist_ok=True)

# ============ LE CATALOGUE DES IOCs — les 20 kits ============
IOCS = {
    "RickPortal": {
        "chemins": ["~/Library/Application Support/RickCache", "tool_DC/RickPortal"],
        "fichiers": ["sys.log", "clip.log", "portal.command", "rick_key.bin", "README_RICK.txt"],
        "process": ["01_keylogger", "02_reverse_shell", "04_clipboard", "05_usb_worm", "07_screenspy", "08_webcam", "10_mic_rec"],
        "persist": ["com.rick.keylog", "com.rick.clip", "com.rick.screen", "com.rick.cam",
                     "com.rick.mic", "com.rick.usb", "com.rick.shell"],
        "ports": [4444],
    },
    "ArkhamGame (leurre)": {
        "chemins": ["%LOCALAPPDATA%\\ArkhamLab", "%APPDATA%\\Arkham"],
        "fichiers": ["ArkhamUpdate.exe", "msupd.exe", "lexagent.exe", "scr.bmp"],
        "process": ["ArkhamUpdate", "msupd", "lexagent"],
        "persist": ["ArkhamUpdate (Run key)", "ArkhamSvc (tache planifiee)"],
        "mutex": ["ArkhamAgentSingle"],
        "ports": [4444],
    },
    "LexCorpIndustries": {
        "fichiers": ["lexagent.exe", "lex_ransom2.exe", "lex_smb_worm.exe", "lex_loader.exe", ".lexcor"],
        "process": ["lex_ransom2", "lex_smb_worm", "lex_loader"],
        "persist": ["LexSvc (tache distante)"],
    },
    "H.I.V.E. (minage)": {
        "fichiers": ["ruche_worker.py", "config.json (xmrig)"],
        "process": ["xmrig", "ruche_worker"],
        "persist": ["com.apple.hivesync (LaunchAgent)"],
        "ports": [8096],
    },
    "S.T.A.R. Labs (C2)": {
        "process": ["star_dns_c2_server", "star_c2_server", "star_dns_agent"],
        "ports": [5353, 5354, 5355, 5356, 5357, 5358, 5359, 5360, 5361, 5362, 5363, 8090, 8091, 8092, 8093],
    },
    "Daily Planet": {"fichiers": ["veille_cache.json"]},
    "LeagueOfShadows": {"chemins": ["tool_DC/LeagueOfShadows/campagnes"]},
    "Scarecrow Phish": {
        "fichiers": ["captures.json", "mirror_captures.json"],
        "ports": [8085, 8086, 8087],
    },
    "JokerCard": {"chemins": ["/payload.txt (LittleFS carte)"]},
    "TaskForceX APK": {
        "fichiers": ["lex.apk", "LexService.class"],
        "persist": ["com.lexcorp.lexservice (service Android, START_STICKY)"],
    },
}

SIG = {
    "4444": "listener reverse shell standard",
    "5050": "console web Arkham C2",
    "8090": "C2 HTTP S.T.A.R.",
    "8096": "coordonnateur H.I.V.E.",
    "8085": "page phishing Scarecrow",
    "8086": "miroir pixel-perfect",
    "8087": "oeil captures live",
    "8088": "Daily Planet",
    "8089": "WarWorld",
}

def expand(p):
    return os.path.expanduser(p)

def scan():
    print("\033[38;2;57;255;20m" + "KRYPTONITE SCAN — ta machine contre les IOCs des 20 kits\033[0m\n")
    hits = []
    t0 = time.time()
    for kit, iocs in IOCS.items():
        for p in iocs.get("chemins", []):
            full = expand(p)
            if os.path.exists(full):
                hits.append((kit, "CHEMIN", full))
        for f in iocs.get("fichiers", []):
            # cherche dans les zones de capture classiques
            for base in ["~/Library/Application Support", "~", "~/Downloads", "~/Desktop"]:
                full = expand(f"{base}/RickCache/{f}") if "RickCache" in p else None
            # recherche simple dans ~/ et %APPDATA% equivalents mac
            for base in [expand("~/Library/Application Support"), expand("~/Desktop"),
                         expand("~/Downloads"), expand("~/Public")]:
                cand = os.path.join(base, f)
                if os.path.exists(cand):
                    hits.append((kit, "FICHIER", cand))
        for proc in iocs.get("process", []):
            rc = subprocess.run(f"pgrep -f {proc}", shell=True, capture_output=True)
            if rc.returncode == 0:
                hits.append((kit, "PROCESSUS", proc))
        for pers in iocs.get("persist", []):
            agent_dir = expand("~/Library/LaunchAgents")
            if os.path.isdir(agent_dir):
                for f in os.listdir(agent_dir):
                    if any(part in f for part in pers.replace(" (Run key)", "").replace(" (tache planifiee)", "").replace(" (LaunchAgent)", "").split()):
                        hits.append((kit, "PERSISTANCE", f"LaunchAgents/{f}"))
            rc = subprocess.run(f"crontab -l 2>/dev/null | grep -i '{pers[:20]}'", shell=True, capture_output=True)
            if rc.returncode == 0:
                hits.append((kit, "PERSISTANCE", f"crontab: {pers}"))
    # ports
    out = subprocess.run("lsof -nP -iTCP -sTCP:LISTEN", shell=True, capture_output=True).stdout.decode()
    for port, sig in SIG.items():
        for line in out.splitlines():
            if f":{port} " in line:
                hits.append(("PORT", f":{port} — {sig}", line.strip()[:80]))
                break
    print(f"  duree : {time.time()-t0:.1f} s\n")
    if hits:
        print(f"\033[38;2;255;60;60m  ⚠ KRYPTONITE DETECTEE — {len(hits)} IOC(s) :\033[0m")
        cur = None
        for kit, kind, det in hits:
            if kit != cur: print(f"\n  [{kit}]"); cur = kit
            print(f"   {kind:<12} {det}")
    else:
        print("  machine saine — aucune trace kryptonite.")
    json.dump([{"kit": k, "type": t, "detail": d} for k, t, d in hits],
              open(os.path.join(OUT, "scan.json"), "w"), indent=1)
    print(f"\n  [OK] scan -> {OUT}/scan.json")

def sigma():
    rules = []
    for kit, iocs in IOCS.items():
        procs = iocs.get("process", [])
        files = iocs.get("fichiers", [])
        pers = iocs.get("persist", [])
        if not (procs or files or pers): continue
        sels = []
        if procs:
            sels.append(f"""    process_creation:
        Image|endswith:
{''.join('          - ' + chr(39) + p + chr(39) + chr(10) for p in procs)}""")
        if files:
            sels.append(f"""    file_event:
        TargetFilename|contains:
{''.join('          - ' + chr(39) + f + chr(39) + chr(10) for f in files)}""")
        if pers:
            sels.append(f"""    persistence:
        {chr(39)}{pers[0]}{chr(39)}""")
        yaml = f"""title: {kit} — traces d'agent (kit lab Maxime Leal)
status: experimental
description: >
  Detection des traces du kit {kit} (RickPortal/LexCorp/etc lab).
  Generes automatiquement par KryptoniteSuite.
logsource:
    product: windows
    service: sysmon
detection:
{chr(10).join(sels)}
    condition: 1 of them
fields:
    - Image
    - TargetFilename
falsepositives:
    - machines de lab Maxime Leal (autorise)
level: high
tags:
    - attack.execution
    - attack.persistence
"""
        rules.append((kit, yaml))
    os.makedirs(os.path.join(OUT, "sigma"), exist_ok=True)
    for kit, y in rules:
        safe = kit.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(".", "").replace("/", "_")
        open(os.path.join(OUT, "sigma", f"lab_{safe}.yml"), "w").write(y)
        print(f"  [OK] sigma/lab_{safe}.yml")
    print(f"  {len(rules)} regles Sigma generees — importables dans Elastic/Splunk via sigma-cli")

def yara():
    yaras = [
        ("lab_rickportal", ["RickCache", "portal.command", "rick_key.bin"]),
        ("lab_arkham", ["ArkhamUpdate", "lexagent", "ArkhamAgentSingle"]),
        ("lab_lexcorp", ["lex_ransom2", "lex_smb_worm", ".lexcor"]),
        ("lab_star", ["star_dns_c2", "star_c2_server"]),
        ("lab_hive", ["ruche_worker", "hivesync"]),
    ]
    os.makedirs(os.path.join(OUT, "yara"), exist_ok=True)
    for name, strings in yaras:
        y = f"rule {name} {{\n  meta:\n    author = \"Maxime Leal — KryptoniteSuite\"\n    description = \"traces de kit lab\"\n  strings:\n"
        for i, s in enumerate(strings):
            y += f'    $s{i} = "{s}" ascii nocase\n'
        y += "  condition:\n    any of them\n}\n"
        open(os.path.join(OUT, "yara", f"{name}.yar"), "w").write(y)
        print(f"  [OK] yara/{name}.yar")

def catalog():
    print(json.dumps(IOCS, indent=1))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan": scan()
    elif cmd == "sigma": sigma()
    elif cmd == "yara": yara()
    elif cmd == "catalog": catalog()
