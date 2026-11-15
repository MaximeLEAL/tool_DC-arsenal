#!/usr/bin/env python3
# language: Python 3, file: veille_notifs.py, target: macOS
# DAILY PLANET · NOTIFICATIONS MACOS — prévient dès qu'une actu cyber arrive
# Usage:  python3 veille_notifs.py start [minutes]   → veille en boucle (défaut 5 min)
#         python3 veille_notifs.py once              → un seul check
#         python3 veille_notifs.py test              → notif de test
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "veille_cache.json")
STATE = os.path.join(ROOT, "notifs_state.json")

def refresh_cache():
    """rafraîchit le cache via veille.py (fetch_all) — import silencieux"""
    global VEILLE
    try:
        sys.path.insert(0, ROOT)
        import veille
        VEILLE = veille
        veille.fetch_all(force=True)
        return True
    except Exception as e:
        print(f"[!] refresh: {e}")
        return False

def load(p, default):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default

def save(p, d):
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False)

def notify(title, message):
    """notification macOS (Centre de notifications)"""
    title = title.replace('"', "'")[:60]
    message = message.replace('"', "'")[:180]
    script = f'display notification "{message}" with title "{title}" subtitle "DAILY PLANET"'
    subprocess.run(["osascript", "-e", script], capture_output=True)

def check(quiet_first=True):
    cache = load(CACHE, {})
    items = cache.get("items", [])
    state = load(STATE, {"seen": [], "last_seen": 0})
    seen = set(state.get("seen", []))
    # premier lancement : on marque tout comme vu (pas de spam)
    if not seen:
        state["seen"] = [i.get("lien", "") for i in items]
        save(STATE, state)
        print(f"[*] {len(items)} actus marquées comme lues — les prochaines déclencheront une notif")
        return 0
    fresh = [i for i in items if i.get("lien") and i["lien"] not in seen]
    if not fresh:
        return 0
    # max 5 notifs d'un coup, les plus récentes en premier
    for item in fresh[:5]:
        source = item.get("source", "News")
        titre = item.get("titre", "")[:120]
        notify(f"📰 {source}", titre)
        time.sleep(1.2)
    if len(fresh) > 5:
        notify(f"📰 Daily Planet", f"+ {len(fresh) - 5} autres actus sur le site")
    # garde les 300 derniers liens vus
    all_seen = list(seen) + [i.get("lien", "") for i in fresh]
    state["seen"] = all_seen[-300:]
    state["last_seen"] = time.time()
    save(STATE, state)
    return len(fresh)

def digest(hour=8):
    """DIGEST QUOTIDIEN — une seule notif le matin avec les 3 actus majeures de la nuit"""
    refresh_cache()
    cache = load(CACHE, {})
    items = cache.get("items", [])
    state = load(STATE, {"seen": [], "last_digest": 0})
    since = state.get("last_digest", 0)
    # actus de la nuit (depuis le dernier digest, sinon 24 h)
    from email.utils import parsedate_to_datetime
    recent = []
    for it in items:
        try:
            ts = parsedate_to_datetime(it.get("date", "")).timestamp()
        except Exception:
            continue
        if ts > since and ts > time.time() - 86400:
            recent.append((ts, it))
    if not recent:
        notify("📰 DIGEST DU MATIN", "Aucune actu majeure cette nuit — le journal est à jour.")
        state["last_digest"] = time.time() - 23 * 3600  # retente demain à 8h
        save(STATE, state)
        return
    # score de "majeure" : mots chauds + source de référence + catégorie
    HOT_KW = getattr(globals().get("VEILLE"), "HOT", None) or \
        ["ransomware", "0-day", "zero-day", "cve-", "exploit", "vulnérabilité", "vulnerability"]
    TOP_SOURCES = {"The Hacker News", "KrebsOnSecurity", "CISA Alertes", "CERT-FR",
                   "BleepingComputer", "Dark Reading", "SecurityWeek", "WeLiveSecurity"}
    def score(it):
        s = 0
        t = it.get("titre", "").lower()
        if any(k in t for k in HOT_KW): s += 3
        if it.get("cat") == "alertes": s += 3
        if it.get("cat") == "cyber": s += 2
        if it.get("source") in TOP_SOURCES: s += 2
        return -s  # tri croissant
    ranked = sorted(recent, key=lambda x: score(x[1]))
    top3 = [it for _, it in ranked[:3]]
    lines = []
    for n, it in enumerate(top3, 1):
        titre = it.get("titre", "")[:58]
        src = it.get("source", "")[:14]
        lines.append(f"{n}. {titre} — {src}")
    msg = "\n".join(lines)
    extra = len(recent) - len(top3)
    if extra > 0:
        msg += f"\n+ {extra} autres sur le journal"
    notify("📰 DIGEST DU MATIN", msg)
    print(f"[✓] digest envoyé : {len(top3)} actus majeures ({len(recent)} nouvelles au total)")
    # marque tout comme vu pour ne pas re-notifier
    state["seen"] = list(set(state.get("seen", [])) | {i.get("lien", "") for i in items})[-400:]
    state["last_digest"] = time.time()
    save(STATE, state)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "test":
        notify("📰 Daily Planet", "Notifs opérationnelles — tu seras prévenu à chaque actu cyber.")
        print("[✓] notif de test envoyée")
    elif cmd == "digest":
        digest()
    elif cmd == "once":
        n = check(quiet_first=False)
        print(f"[✓] {n} nouvelle(s) actu(s) notifiée(s)")
    elif cmd == "start":
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        check(quiet_first=True)
        print(f"[*] DAILY PLANET NOTIFS — vérification toutes les {minutes} min · Ctrl+C pour arrêter")
        while True:
            time.sleep(minutes * 60)
            try:
                refresh_cache()
                n = check(quiet_first=False)
                if n: print(f"[{time.strftime('%H:%M')}] {n} notif(s) envoyée(s)")
            except Exception as e:
                print(f"[!] {e}")
    else:
        print(__doc__)
        print("MODES : start (flux en continu) · digest (récap quotidien à heure fixe) · once · test")

if __name__ == "__main__":
    main()
