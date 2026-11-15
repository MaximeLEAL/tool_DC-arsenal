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
    total_all = data["n"]
    shown = len(items)
    # comptes par catégorie
    counts = {}
    for i in data["items"]:
        counts[i["cat"]] = counts.get(i["cat"], 0) + 1
    chips = [("toutes", "TOUTES"), ("cyber", "CYBER"), ("alertes", "CVE & ALERTES"),
             ("juridique", "JURIDIQUE"), ("tech-fr", "TECH FR"), ("tech", "TECH")]
    chips_html = "".join(
        f'<a class="chip{" on" if c == cat else ""}" href="/?cat={c}&q={urllib.parse.quote(query)}">{label}'
        f'<b>{counts.get(c, total_all if c == "toutes" else 0)}</b></a>'
        for c, label in chips)

    CAT_COLOR = {"cyber": "#ff4628", "alertes": "#ff8c30", "juridique": "#64a0ff",
                 "tech": "#4ad66d", "tech-fr": "#f5c518"}
    cards = []
    for it in items[:250]:
        cc = CAT_COLOR.get(it["cat"], "#64a0ff")
        resume = html.escape((it.get("resume") or "")[:220])
        titre = html.escape(it.get("titre", ""))
        cards.append(f"""
        <a class="news" href="{html.escape(it.get('lien',''))}" target="_blank" rel="noopener" style="--cc:{cc}">
          <div class="nhead">
            <span class="src" style="color:{cc};border-color:{cc}55">{html.escape(it['source'])}</span>
            <span class="ago">{time_ago(it.get('date',''))}</span>
            {hot_badge(html.escape(it['titre']))}
            <span class="cat">{it['cat'].upper()}</span>
          </div>
          <h3>{titre}</h3>
          <p>{resume}…</p>
          <div class="go">LIRE L'ARTICLE <span class="arr">→</span></div>
        </a>""")

    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
    <title>DAILY PLANET — La veille tech &amp; cyber</title>
    <meta http-equiv="refresh" content="300">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;500;600;700&family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
    :root{{--bg:#06070c; --panel:#0c0e17; --panel2:#070810; --line:#1a1c2e;
      --txt:#c4c6d6; --muted:#6a6d86; --dim:#45485e; --red:#e63022; --gold:#f5c518;
      --c:#64a0ff;
      --disp:"Anton",Impact,sans-serif; --cond:"Oswald",sans-serif;
      --sans:"Archivo",-apple-system,sans-serif; --mono:"JetBrains Mono",monospace}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{background:var(--bg);color:var(--txt);font-family:var(--sans);min-height:100vh;position:relative;-webkit-font-smoothing:antialiased}}
    ::selection{{background:var(--red);color:#fff}}
    ::-webkit-scrollbar{{width:11px}}::-webkit-scrollbar-track{{background:var(--bg)}}
    ::-webkit-scrollbar-thumb{{background:#1c1e30;border-radius:6px;border:2px solid var(--bg)}}
    ::-webkit-scrollbar-thumb:hover{{background:var(--red)}}
    .bg{{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}}
    .bg .beam{{position:absolute;inset:0;background:
      radial-gradient(44% 70% at 50% 108%,rgba(100,160,255,.10),transparent 60%),
      radial-gradient(60% 80% at 50% -10%,rgba(230,48,34,.12),transparent 62%)}}
    .bg .dots{{position:absolute;inset:0;opacity:.12;background-image:radial-gradient(rgba(255,255,255,.5) 1px,transparent 1.4px);background-size:16px 16px;mask-image:radial-gradient(ellipse 70% 55% at 50% 20%,#000 10%,transparent 72%)}}
    .bg .grid{{position:absolute;inset:0;opacity:.5;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:52px 52px;mask-image:radial-gradient(ellipse 85% 70% at 50% 30%,#000 35%,transparent 88%)}}
    .bg .vig{{position:absolute;inset:0;background:radial-gradient(ellipse 100% 80% at 50% 30%,transparent 55%,rgba(0,0,0,.55))}}
    .wrap{{position:relative;z-index:1}}
    .nav{{display:flex;justify-content:space-between;align-items:center;padding:14px clamp(18px,4vw,40px);
      position:sticky;top:0;z-index:30;background:rgba(6,7,12,.55);backdrop-filter:blur(16px) saturate(140%);border-bottom:1px solid var(--line)}}
    .brand{{font-family:var(--cond);font-weight:700;letter-spacing:5px;font-size:.95rem;color:#fff;
      display:flex;align-items:center;gap:11px;text-transform:uppercase;text-decoration:none}}
    .brand .dot{{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 14px var(--red);animation:pulse 2s infinite}}
    .brand em{{color:var(--red);font-style:normal}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
    .nav-right{{display:flex;align-items:center;gap:14px}}
    .status{{font-family:var(--mono);font-size:.64rem;letter-spacing:1.6px;color:#4ad66d;display:flex;align-items:center;gap:7px;text-transform:uppercase}}
    .status::before{{content:"";width:6px;height:6px;border-radius:50%;background:#4ad66d;box-shadow:0 0 10px #4ad66d;animation:pulse 1.6s infinite}}
    .ghbtn{{font-family:var(--mono);color:#9fb4ff;font-size:.7rem;letter-spacing:.6px;text-decoration:none;
      border:1px solid var(--line);padding:8px 15px;border-radius:10px;transition:.25s;background:rgba(255,255,255,.02)}}
    .ghbtn:hover{{border-color:#6495ff;color:#cdd9ff;box-shadow:0 0 22px rgba(100,149,255,.22)}}
    header.hero{{text-align:center;padding:clamp(40px,7vw,80px) 20px 30px;position:relative}}
    .eyebrow{{font-family:var(--mono);font-size:.7rem;letter-spacing:6px;color:var(--muted);display:inline-flex;
      align-items:center;gap:14px;margin-bottom:22px;text-transform:uppercase}}
    .eyebrow::before,.eyebrow::after{{content:"";width:40px;height:1px;background:linear-gradient(90deg,transparent,var(--dim),transparent)}}
    h1{{font-family:var(--disp);font-size:clamp(3rem,10vw,6.4rem);line-height:.9;color:#fff;letter-spacing:2px;
      text-transform:uppercase;text-shadow:0 3px 0 rgba(0,0,0,.55),0 0 70px rgba(100,160,255,.25)}}
    h1 b{{background:linear-gradient(120deg,var(--gold) 0%,#ff6a3d 50%,var(--red) 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}
    .sous{{margin-top:14px;font-family:var(--mono);color:var(--muted);letter-spacing:3px;font-size:.72rem;text-transform:uppercase}}
    .stats{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:34px}}
    .stat{{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.008));border:1px solid var(--line);
      border-radius:12px;padding:15px 26px;min-width:110px;transition:.3s}}
    .stat:hover{{border-color:rgba(100,160,255,.4);transform:translateY(-3px)}}
    .stat b{{display:block;font-family:var(--disp);font-size:2rem;color:#fff;line-height:1}}
    .stat span{{font-family:var(--mono);font-size:.6rem;letter-spacing:2px;color:var(--muted);margin-top:7px;display:block;text-transform:uppercase}}
    .toolbar{{position:sticky;top:49px;z-index:20;background:rgba(6,7,12,.72);backdrop-filter:blur(14px);
      border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:16px clamp(18px,4vw,40px);
      display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;margin-top:30px}}
    .chip{{font-family:var(--mono);font-size:.66rem;letter-spacing:1.2px;text-decoration:none;color:var(--muted);
      border:1px solid var(--line);background:rgba(255,255,255,.02);padding:8px 14px;border-radius:999px;transition:.25s;display:inline-flex;gap:8px;align-items:center}}
    .chip b{{color:var(--dim);font-weight:500}}
    .chip:hover{{border-color:var(--c);color:#cdd9ff}}
    .chip.on{{background:var(--gold);border-color:var(--gold);color:#111;font-weight:700}}
    .chip.on b{{color:rgba(0,0,0,.55)}}
    form.search{{position:relative}}
    .search input{{font-family:var(--mono);font-size:.78rem;color:#fff;background:rgba(255,255,255,.03);
      border:1px solid var(--line);border-radius:10px;padding:10px 14px 10px 38px;width:min(320px,70vw);outline:none;transition:.25s}}
    .search input::placeholder{{color:var(--dim);letter-spacing:1.5px;text-transform:uppercase;font-size:.68rem}}
    .search input:focus{{border-color:var(--c);box-shadow:0 0 24px rgba(100,160,255,.18);background:rgba(255,255,255,.05)}}
    .search svg{{position:absolute;left:12px;top:50%;transform:translateY(-50%);stroke:var(--muted)}}
    main{{max-width:880px;margin:26px auto 0;padding:0 24px 44px;position:relative;z-index:1}}
    .info{{font-family:var(--mono);color:var(--dim);font-size:.64rem;letter-spacing:1.5px;text-align:center;
      text-transform:uppercase;margin-bottom:22px}}
    .news{{display:block;background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
      border-radius:4px;padding:16px 20px 14px;margin-bottom:11px;text-decoration:none;position:relative;overflow:hidden;
      transition:border-color .25s,transform .25s,box-shadow .25s}}
    .news:hover{{border-color:color-mix(in srgb,var(--cc) 55%,var(--line));transform:translateX(5px);
      box-shadow:0 10px 34px color-mix(in srgb,var(--cc) 14%,transparent)}}
    .news::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--cc);opacity:.85}}
    .nhead{{display:flex;gap:10px;align-items:center;font-family:var(--mono);font-size:.64rem;letter-spacing:.8px;margin-bottom:8px}}
    .src{{border:1px solid;border-radius:5px;padding:2px 8px;font-weight:700}}
    .ago{{color:var(--muted)}}
    .cat{{margin-left:auto;color:var(--dim)}}
    .hot{{background:#7a1010;color:#fff;border-radius:4px;padding:2px 8px;letter-spacing:1.5px}}
    .news h3{{font-family:var(--cond);color:#fff;font-size:1.06rem;font-weight:600;line-height:1.35;letter-spacing:.2px}}
    .news p{{color:var(--muted);font-size:.85em;margin:7px 0 0;line-height:1.55}}
    .go{{font-family:var(--mono);font-size:.6rem;letter-spacing:1.6px;color:var(--cc);margin-top:10px;opacity:.85}}
    .go .arr{{display:inline-block;transition:transform .25s}}
    .news:hover .go .arr{{transform:translateX(6px)}}
    .more{{display:block;margin:26px auto 0;font-family:var(--mono);font-size:.7rem;letter-spacing:2px;
      color:#cdd9ff;background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:10px;
      padding:13px 30px;cursor:pointer;transition:.25s;text-transform:uppercase}}
    .more:hover{{border-color:var(--c);box-shadow:0 0 22px rgba(100,160,255,.2)}}
    footer{{text-align:center;color:var(--muted);padding:40px 20px 56px;font-family:var(--mono);font-size:.66rem;
      letter-spacing:2.2px;border-top:1px solid var(--line);margin-top:44px;text-transform:uppercase}}
    footer a{{color:#9fb4ff;text-decoration:none}}
    @media (max-width:560px){{.status{{display:none}}}}
    </style></head><body>
    <div class="bg"><div class="beam"></div><div class="dots"></div><div class="grid"></div><div class="vig"></div></div>
    <div class="wrap">
    <nav class="nav">
      <a class="brand" href="https://maximeleal.github.io/tool_DC-arsenal/"><span class="dot"></span>Gotham <em>City</em></a>
      <div class="nav-right"><span class="status">Live · {len(FEEDS)} sources</span>
        <a class="ghbtn" href="https://github.com/MaximeLEAL/tool_DC-arsenal" target="_blank">&#8599; GITHUB</a></div>
    </nav>
    <header class="hero">
      <div class="eyebrow">Veille technologie &amp; cybersécurité</div>
      <h1>DAILY <b>PLANET</b></h1>
      <div class="sous">L'ACTUALITÉ MONDIALE · POWERED BY MAXIME LEAL</div>
      <div class="stats">
        <div class="stat"><b>{total_all}</b><span>Actualités</span></div>
        <div class="stat"><b>{len(FEEDS)}</b><span>Sources</span></div>
        <div class="stat"><b>{counts.get('cyber', 0)}</b><span>Cyber</span></div>
        <div class="stat"><b>{counts.get('alertes', 0)}</b><span>CVE &amp; Alertes</span></div>
      </div>
    </header>
    <div class="toolbar">{chips_html}
      <form class="search" method="get"><input name="q" placeholder="Rechercher une actu…" value="{html.escape(query)}" spellcheck="false">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg></form>
    </div>
    <main>
    <div class="info">{shown} résultat{'s' if shown != 1 else ''} affiché{'s' if shown != 1 else ''} · dernière collecte {data['fetched']} · auto-refresh 5 min</div>
    <div id="list">{''.join(cards)}</div>
    <button class="more" id="more" onclick="showMore()" style="display:{'block' if shown > 60 else 'none'}">Charger plus d'actus ▾</button>
    </main>
    <footer>DAILY PLANET · UNE DE L'ARSENAL DC · <a href="https://github.com/MaximeLEAL/tool_DC-arsenal">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
    </div>
    <script>
    const all = document.querySelectorAll('#list .news'), step = 60;
    let shownN = Math.min(step, all.length);
    for (let i = shownN; i < all.length; i++) all[i].style.display = 'none';
    function showMore() {{
      const next = Math.min(shownN + step, all.length);
      for (let i = shownN; i < next; i++) all[i].style.display = '';
      shownN = next;
      if (shownN >= all.length) document.getElementById('more').style.display = 'none';
    }}
    </script>
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
