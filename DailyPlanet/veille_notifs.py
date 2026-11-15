#!/usr/bin/env python3
# language: Python 3, file: veille_notifs.py, target: macOS
# DAILY PLANET · NOTIFICATIONS MACOS — prévient dès qu'une actu cyber arrive
# Usage:  python3 veille_notifs.py start [minutes]   → veille en boucle (défaut 5 min)
#         python3 veille_notifs.py once              → un seul check
#         python3 veille_notifs.py test              → notif de test
import json, os, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "veille_cache.json")
STATE = os.path.join(ROOT, "notifs_state.json")
CFG = os.path.join(ROOT, "notifs_config.json")

def cfg():
    return load(CFG, {})

def push_ntfy(title, message, link=None, tags="newspaper", image_data=None):
    """publie sur ntfy.sh → reçue sur le téléphone. image_data = octets (attachment)"""
    topic = cfg().get("ntfy_topic")
    if not topic: return
    try:
        headers = {"Title": title.encode("utf-8"), "Tags": tags, "Priority": "default",
                   **({"Click": link} if link else {}),
                   **({"Message": message.encode("utf-8")} if image_data else {})}
        if image_data:
            headers["Filename"] = "actus.jpg"
            req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=image_data, headers=headers)
        else:
            req = urllib.request.Request(f"https://ntfy.sh/{topic}", data=message.encode("utf-8"), headers=headers)
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"[!] ntfy: {e}")

def thumb_for(article_url):
    """octets de la vignette en cache (pré-téléchargée), ou None"""
    try:
        sys.path.insert(0, ROOT)
        import veille
        return veille.fetch_og_image(article_url)
    except Exception:
        return None

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

def notify(title, message, link=None):
    """notification macOS + push téléphone (ntfy si configuré)"""
    title = title.replace('"', "'")[:60]
    message = message.replace('"', "'")[:180]
    script = f'display notification "{message}" with title "{title}" subtitle "DAILY PLANET"'
    subprocess.run(["osascript", "-e", script], capture_output=True)
    push_ntfy(title, message, link)

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
        notify(f"📰 {source}", titre, link=item.get("lien"))
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
    notify("📰 DIGEST DU MATIN", msg,
           link="https://maximeleal.github.io/tool_DC-arsenal/DailyPlanet/")
    # téléphone : 3 notifs enrichies avec les vignettes, cliquables vers les articles
    for n, it in enumerate(top3, 1):
        img = thumb_for(it.get("lien", ""))
        push_ntfy(f"📰 DIGEST {n}/3 · {it.get('source','')[:20]}", it.get("titre", "")[:180],
                  link=it.get("lien"), tags="newspaper", image_data=img)
        time.sleep(1)
    print("[📱] 3 notifs enrichies envoyées sur le téléphone")
    print(f"[✓] digest envoyé : {len(top3)} actus majeures ({len(recent)} nouvelles au total)")
    # marque tout comme vu pour ne pas re-notifier
    state["seen"] = list(set(state.get("seen", [])) | {i.get("lien", "") for i in items})[-400:]
    state["last_digest"] = time.time()
    save(STATE, state)

def check_keywords():
    """ALERTES IMMÉDIATES : notifie (Mac + téléphone, avec image) si une nouvelle actu
    contient un des mots-clés du fichier notifs_config.json"""
    kws = [k.lower() for k in cfg().get("keywords", []) if k.strip()]
    if not kws: return 0
    cache = load(CACHE, {})
    items = cache.get("items", [])
    state = load(STATE, {"seen": [], "last_digest": 0})
    seen = set(state.get("seen", []))
    hits = 0
    for it in items:
        lien = it.get("lien", "")
        if not lien or lien in seen: continue
        blob = (it.get("titre", "") + " " + it.get("resume", "")).lower()
        match = [k for k in kws if k in blob]
        if not match: continue
        title = f"🎯 {', '.join(match[:2]).upper()} — {it.get('source', '')[:24]}"
        notify(title, it.get("titre", "")[:140], link=lien)
        # push téléphone avec la vignette si dispo
        img = thumb_for(lien)
        push_ntfy(title, it.get("titre", "")[:180], link=lien,
                  tags="rotating_light", image_data=img)
        seen.add(lien)
        hits += 1
        if hits >= 5:
            print("[!] limite de 5 alertes mots-clés par cycle (anti-spam)")
            break
    # marque tout comme vu (pour que les non-matching ne reviennent pas en boucle)
    state["seen"] = (list(seen) + [i.get("lien", "") for i in items])[-400:]
    save(STATE, state)
    return hits

def watch(minutes=5):
    """MODE PERSISTANT : alertes mots-clés immédiates + digest quotidien à 8h"""
    kws = cfg().get("keywords", [])
    print(f"[*] DAILY PLANET WATCH — alertes mots-clés: {kws or 'aucun (à configurer)'} · digest à {cfg().get('digest_hour', 8)}h · toutes les {minutes} min")
    while True:
        try:
            refresh_cache()
            h = check_keywords()
            if h: print(f"[{time.strftime('%H:%M')}] {h} alerte(s) mot(s)-clé(s) envoyée(s)")
            now = time.localtime()
            today = time.strftime("%Y-%m-%d")
            state = load(STATE, {})
            if now.tm_hour == int(cfg().get("digest_hour", 8)) and state.get("digest_day") != today:
                state["digest_day"] = today
                save(STATE, state)
                digest()
        except Exception as e:
            print(f"[!] watch: {e}")
        time.sleep(minutes * 60)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    if cmd == "test":
        notify("📰 Daily Planet", "Notifs opérationnelles — tu seras prévenu à chaque actu cyber.")
        print("[✓] notif de test envoyée")
    elif cmd == "digest":
        digest()
    elif cmd == "watch":
        watch(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    elif cmd == "keywords":
        for k in cfg().get("keywords", []): print(" -", k)
        print(f"→ édite {CFG} pour changer (json: \"keywords\": [...])")
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
