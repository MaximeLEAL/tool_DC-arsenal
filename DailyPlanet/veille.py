#!/usr/bin/env python3
# language: Python 3, file: veille.py, target: macOS
# DAILY PLANET - LA VEILLE TECH & CYBER · powered by Maxime Leal
# Agrège les grands flux RSS (FR + EN), dédoublonne, classe, et sert une page web journal.
# Usage: python3 veille.py serve [port]   |   python3 veille.py top [n]
import http.server, urllib.request, urllib.parse, xml.etree.ElementTree as ET, json, time, os, sys, re, html, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dc_fullscreen as dfs

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "veille_cache.json")
CACHE_TTL = 900  # 15 min

FEEDS = {
    "The Hacker News":   ("https://feeds.feedburner.com/TheHackersNews", "cyber"),
    "BleepingComputer":  ("https://www.bleepingcomputer.com/feed/", "cyber"),
    "KrebsOnSecurity":   ("https://krebsonsecurity.com/feed/", "cyber"),
    "Dark Reading":      ("https://www.darkreading.com/rss.xml", "cyber"),
    "SecurityWeek":      ("https://www.securityweek.com/feed/", "cyber"),
    "Malwarebytes Labs": ("https://www.malwarebytes.com/blog/feed/index.xml", "cyber"),
    "Unit42 PaloAlto":   ("https://unit42.paloaltonetworks.com/feed/", "cyber"),
    "WeLiveSecurity":    ("https://www.welivesecurity.com/feed/", "cyber"),
    "CISA Alertes":      ("https://www.cisa.gov/cybersecurity-advisories/all.xml", "alertes"),
    "CERT-FR":           ("https://www.cert.ssi.gouv.fr/feed/", "alertes"),
    "CNIL":              ("https://www.cnil.fr/fr/rss", "juridique"),
    "Ars Technica":      ("https://feeds.arstechnica.com/arstechnica/technology-lab", "tech"),
    "TechCrunch":        ("https://techcrunch.com/feed/", "tech"),
    "The Verge":         ("https://www.theverge.com/rss/index.xml", "tech"),
    "Wired":             ("https://www.wired.com/feed/rss", "tech"),
    "Engadget":          ("https://www.engadget.com/rss.xml", "tech"),
    "HN frontpage":      ("https://hnrss.org/frontpage", "tech"),
    "MIT Tech Review":   ("https://www.technologyreview.com/feed/", "tech"),
    "Korben":            ("https://korben.info/feed", "tech-fr"),
    "NextINpact":        ("https://www.nextinpact.com/rss", "tech-fr"),
    "IT-Connect":        ("https://www.it-connect.fr/feed/", "tech-fr"),
    "ZATAZ":             ("https://www.zataz.com/feed/", "cyber"),
    "GitHub Security":   ("https://github.blog/security/feed/", "cyber"),
    "LeMondeInformatique": ("https://www.lemondeinformatique.fr/rss/rss_actualites.xml", "tech-fr"),
    "Frandroid":         ("https://www.frandroid.com/feed", "tech-fr"),
}

HOT = ["ransomware", "0-day", "zero-day", "cve-", "exploit", "vulnérabilité", "vulnerability",
       "breach", "fuite", "phishing", "backdoor", "malware", "apt", "rootkit", "déploiement"]

def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return html.unescape(re.sub(r"\s+", " ", s)).strip()

def entry_category(title, desc, base):
    text = (title + " " + desc).lower()
    if any(k in text for k in ["cve-", "ransomware", "0-day", "zero-day", "exploit", "backdoor",
                                "malware", "breach", "violation de données", "attaqu", "hacker"]):
        return "cyber"
    return base

def fetch_feed(name, url):
    req = urllib.request.Request(url, headers={"User-Agent": "DailyPlanet/1.0 (veille)"})
    try:
        raw = urllib.request.urlopen(req, timeout=15).read()
        root = ET.fromstring(raw)
    except Exception as e:
        return {"error": str(e), "items": []}
    items = []
    # RSS 2.0
    for it in root.iter("item"):
        title = strip_html(it.findtext("title") or "")
        link = (it.findtext("link") or "").strip()
        desc = strip_html(it.findtext("description") or "")[:280]
        date = it.findtext("pubDate") or ""
        items.append({"titre": title, "lien": link, "resume": desc, "date": date, "source": name})
    # Atom
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for it in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = strip_html(it.findtext("a:title") or "")
        link_el = it.find("a:link", ns)
        link = link_el.get("href") if link_el is not None else ""
        desc = strip_html(it.findtext("a:summary") or "")[:280]
        date = it.findtext("a:updated") or ""
        items.append({"titre": title, "lien": link, "resume": desc, "date": date, "source": name})
    return {"error": None, "items": items}

def fetch_all(force=False):
    if not force and os.path.exists(CACHE):
        age = time.time() - os.path.getmtime(CACHE)
        if age < CACHE_TTL:
            return json.load(open(CACHE))
    all_items, errors = [], []
    for name, (url, base) in FEEDS.items():
        r = fetch_feed(name, url)
        if r["error"]:
            errors.append(f"{name}: {r['error'][:60]}")
            continue
        for it in r["items"]:
            it["cat"] = entry_category(it["titre"], it["resume"], base)
            if it["titre"] and it["lien"]:
                all_items.append(it)
    # dedup par lien, tri par source-date inconnue -> stable
    seen, uniq = set(), []
    for it in all_items:
        if it["lien"] not in seen:
            seen.add(it["lien"]); uniq.append(it)
    data = {"fetched": time.strftime("%Y-%m-%d %H:%M:%S"), "n": len(uniq),
            "items": uniq, "errors": errors}
    json.dump(data, open(CACHE, "w"), ensure_ascii=False)
    return data

def time_ago(date_str):
    # tente les formats RSS communs, sinon renvoie la chaine
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(date_str)
        d = time.time() - dt.timestamp()
        if d < 3600: return f"il y a {int(d//60)} min"
        if d < 86400: return f"il y a {int(d//3600)} h"
        return f"il y a {int(d//86400)} j"
    except Exception:
        return date_str[:16]

def hot_badge(title):
    t = title.lower()
    return '<span style="background:#7a1010;color:#fff;border-radius:4px;padding:1px 8px;font-size:.75em">HOT</span>' \
        if any(k in t for k in HOT) else ""

def render(data, query="", cat="toutes"):
    items = data["items"]
    if cat != "toutes":
        items = [i for i in items if i["cat"] == cat]
    if query:
        q = query.lower()
        items = [i for i in items if q in (i["titre"] + i["resume"]).lower()]
    chips = [("toutes", "TOUTES"), ("cyber", "CYBER"), ("alertes", "CVE & ALERTES"),
             ("juridique", "JURIDIQUE"), ("tech-fr", "TECH FR"), ("tech", "TECH")]
    chips_html = " ".join(
        f'<a href="/?cat={c}" style="text-decoration:none"><span style="background:{"#c9a600" if c==cat else "#14141c"};'
        f'color:{"#111" if c==cat else "#c9a600"};padding:6px 16px;border-radius:20px;font-size:.85em;'
        f'border:1px solid #2a2a3a">{label}</span></a>' for c, label in chips)
    cards = []
    for it in items[:120]:
        cards.append(f"""
        <div style="background:#0c0c16;border:1px solid #1a1a2a;border-radius:10px;padding:16px 20px;margin-bottom:12px">
          <div style="font-size:.75em;color:#889;margin-bottom:6px">
            <span style="background:#14141c;color:#c9a600;border-radius:4px;padding:2px 10px">{it['source']}</span>
            <span style="margin-left:8px">{time_ago(it['date'])}</span> {hot_badge(it['titre'])}
            <span style="float:right;color:#556">{it['cat'].upper()}</span>
          </div>
          <a href="{it['lien']}" target="_blank" style="color:#e7e9ea;text-decoration:none;font-size:1.05em;font-weight:600">
            {it['titre']}</a>
          <p style="color:#99a;font-size:.88em;margin:8px 0 0">{it['resume'][:200]}…</p>
        </div>""")
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
    <title>DAILY PLANET — La veille tech &amp; cyber</title>
    <meta http-equiv="refresh" content="300">
    <style>
    body{{background:#050509;color:#ddd;font-family:'Segoe UI',sans-serif;margin:0;padding:30px 20px}}
    .masthead{{text-align:center;border-bottom:3px double #c9a600;padding-bottom:22px;margin-bottom:8px}}
    h1{{color:#e7e9ea;font-size:2.4em;margin:0;letter-spacing:1px}}
    h1 b{{color:#c9a600}}
    .sous{{color:#889;font-size:.9em}}
    .barre{{display:flex;gap:14px;align-items:center;justify-content:center;margin:20px 0;flex-wrap:wrap}}
    input{{background:#0c0c16;border:1px solid #2a2a3a;color:#ddd;padding:9px 16px;border-radius:20px;width:280px}}
    .info{{text-align:center;color:#665;font-size:.8em;margin-bottom:18px}}
    </style></head><body>
    <div class="masthead">
      <h1>DAILY <b>PLANET</b></h1>
      <div class="sous">LA VEILLE TECHNOLOGIQUE &amp; CYBERSÉCURITÉ — powered by Maxime Leal</div>
    </div>
    <div class="barre">{chips_html}
      <form method="get"><input name="q" placeholder="🔍 rechercher une actualité…" value="{html.escape(query)}"></form>
    </div>
    <div class="info">{data['n']} actualités agrégées · {len(FEEDS)} sources · dernière collecte : {data['fetched']}
    · rafraîchi toutes les 5 min · erreurs : {len(data.get('errors', []))}</div>
    {''.join(cards) or '<div class="info">aucun résultat</div>'}
    </body></html>"""
    return page

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        data = fetch_all()
        if u.path == "/api":
            b = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            page = render(data, q.get("q", [""])[0], q.get("cat", ["toutes"])[0]).encode()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
    def log_message(self, *a): pass

def top(n=15):
    data = fetch_all()
    for it in data["items"][:n]:
        color = "\033[38;2;255;60;60m" if it["cat"] == "cyber" else ("\033[38;2;200;170;0m" if it["cat"] == "tech-fr" else "")
        print(f"{color}[{it['source']}] {it['titre']}\033[0m")
        print(f"   {it['lien'][:100]}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if mode == "top":
        top(int(sys.argv[2]) if len(sys.argv) > 2 else 15)
    else:
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8088
        def refresher():
            while True:
                time.sleep(CACHE_TTL); fetch_all(force=True)
        threading.Thread(target=refresher, daemon=True).start()
        print(f"[*] DAILY PLANET sur http://127.0.0.1:{port} — {len(FEEDS)} sources tech & cyber")
        http.server.ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
