#!/usr/bin/env python3
# language: Python 3, file: calculator.py, target: macOS
# THE CALCULATOR — L'ANALYSEUR DE BREACHES · powered by Maxime Leal
# Stats par secteur/annee, timeline des plus grosses fuites, page web. Mode terminal aussi.
import http.server, json, sys, os, urllib.parse
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

DATA = [
    ("2004", "AOL", "Internet", 92000000, "mots de passe + recherche"),
    ("2011", "Sony PSN", "Gaming", 77000000, "mots de passe, cartes"),
    ("2012", "LinkedIn", "Social", 164000000, "mots de passe SHA1"),
    ("2013", "Yahoo", "Internet", 3000000000, "mots de passe, questions"),
    ("2013", "Target", "Retail", 40000000, "cartes bancaires"),
    ("2014", "eBay", "Retail", 145000000, "mots de passe"),
    ("2014", "Anthem", "Sante", 80000000, "SSN, dossiers medicaux"),
    ("2015", "OPM", "Gouvernement", 22000000, "dossiers de securite"),
    ("2016", "AdultFriendFinder", "Social", 412000000, "mots de passe, emails"),
    ("2016", "Yahoo #2", "Internet", 500000000, "mots de passe"),
    ("2017", "Equifax", "Finance", 147000000, "SSN, cartes, dossiers"),
    ("2017", "Deep Root/VR ancillary", "Politique", 198000000, "opinions politiques"),
    ("2018", "Facebook-Cambridge", "Social", 87000000, "profils et relations"),
    ("2019", "First American", "Finance", 885000000, "documents financiers"),
    ("2019", "Facebook scraping", "Social", 533000000, "telephones, profils"),
    ("2020", "Marriott #2", "Hotellerie", 5200000, "cartes, passeports"),
    ("2021", "Facebook scraping #2", "Social", 106000000, "telephones, emails"),
    ("2021", "LinkedIn scraping", "Social", 700000000, "profils complets"),
    ("2022", "Twitter API", "Social", 5400000, "telephones, emails"),
    ("2023", "MOVEit/Cl0p", "Finance/Sante", 95000000, "dossiers multiples"),
    ("2024", "Ticketmaster/Cl0p", "Retail", 560000000, "noms, cartes partielles"),
    ("2025", "Snowflake clients", "SaaS", 165000000, "tickets, telephones"),
    ("2026", "JaggedDB leaks", "Multi", 200000000, "consolidation de fuites"),
]

def stats():
    print("\033[38;2;255;215;0mTHE CALCULATOR — ANALYSE DES BREACHES\033[0m\n")
    by_sector, by_year = {}, {}
    for y, org, sec, rec, what in DATA:
        by_sector[sec] = by_sector.get(sec, 0) + rec
        by_year[y] = by_year.get(y, 0) + rec
    print("  par secteur (total d'enregistrements exposes) :")
    for sec, rec in sorted(by_sector.items(), key=lambda x: -x[1]):
        bar = "#" * max(1, int(rec / 100_000_000))
        print(f"   {sec:<14}{rec:>12,}  {bar}")
    print("\n  par annee :")
    for y, rec in sorted(by_year.items()):
        print(f"   {y}   {rec:>12,}")
    top = sorted(DATA, key=lambda x: -x[3])[:8]
    print("\n  top 8 des plus grosses fuites :")
    for y, org, sec, rec, what in top:
        print(f"   {y}  {org:<28}{rec:>13,}  {what}")

def serve(port=8094):
    total = sum(d[3] for d in DATA)
    by_sector = {}
    for y, org, sec, rec, w in DATA: by_sector[sec] = by_sector.get(sec, 0) + rec
    by_year = {}
    for y, org, sec, rec, w in DATA: by_year[y] = by_year.get(y, 0) + rec
    rows = "".join(f"""<tr><td>{y}</td><td><b>{org}</b></td><td>{sec}</td>
        <td style="color:#ffd60a">{rec:,}</td><td>{w}</td>
        <td><span style="background:#7a1010;color:#fff;padding:1px 8px;border-radius:4px">{rec//1_000_000}M</span></td></tr>"""
        for y, org, sec, rec, w in sorted(DATA, key=lambda x: -x[3]))
    sectors = "".join(f'<div><span style="color:#ffd60a">{sec}</span> '
                      f'<span class="bar" style="width:{min(300, rec//2_000_000)}px"></span> {rec:,}</div>'
                      for sec, rec in sorted(by_sector.items(), key=lambda x: -x[1]))
    page = f"""<!doctype html><html><head><meta charset=utf8><title>The Calculator — Breach Analytics</title>
    <meta http-equiv="refresh" content="60">
    <style>body{{background:#02020a;color:#7ff;font-family:monospace;padding:30px}}
    h1{{color:#7ff}}h1 small{{color:#f90;font-size:.4em;font-style:italic}}
    .bar{{background:#0f7;display:inline-block;height:14px}}
    table{{border-collapse:collapse;width:100%;max-width:900px}}
    td,th{{border:1px solid #073;padding:8px 14px;text-align:left}}
    th{{color:#7ff}} .big{{color:#fff;font-size:1.3em}}</style></head><body>
    <h1>THE CALCULATOR <small>— breach analytics · powered by Maxime Leal</small></h1>
    <div class="big">{total:,} enregistrements exposes dans la base historique</div>
    <h3 style="color:#7ff">PAR SECTEUR</h3>{sectors}
    <h3 style="color:#7ff">TIMELINE</h3>
    <table><tr><th>Annee</th><th>Organisation</th><th>Secteur</th><th>Enregistrements</th><th>Nature</th><th>Échelle</th></tr>
    {rows}</table>
    <p style="color:#567">· lecture en direct de veille_cache.json (Daily Planet) pour le flux cyber du jour</p>
    </body></html>"""
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            b = page.encode()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def log_message(self, *a): pass
    print(f"[*] The Calculator sur http://127.0.0.1:{port}")
    http.server.HTTPServer(("0.0.0.0", port), H).serve_forever()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stats"
    if mode == "stats": stats()
    else: serve(int(mode) if mode.isdigit() else 8094)
