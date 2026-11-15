#!/usr/bin/env python3
# language: Python 3, file: gotham_full.py v8, target: macOS
# GOTHAM CITY v8 — 26 kits, 1 image unique par kit, zéro doublon, pages tools servies
import http.server, urllib.request, urllib.parse, json, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
TOOL_DC = os.path.dirname(os.path.abspath(__file__))
GITHUB = "https://github.com/MaximeLEAL/tool_DC-arsenal"
FACES = os.path.join(TOOL_DC, "gotham_static", "faces")
PAGES = os.path.join(TOOL_DC, "arsenal_web_pages")

# face = fichier UNIQUE dans gotham_static/faces/ (16 kits) — les autres utilisent leur emoji
KITS = [
    {"id": "RickPortal",        "n": "RICKPORTAL",        "c": "#00e676", "f": "rick_face.jpg",                "i": "🟢", "d": "Kit malware · 10 tools"},
    {"id": "FlashToolSuper",    "n": "FLASH TOOL_SUPER",  "c": "#ffd60a", "f": "flash_face.jpg",    "i": "⚡", "d": "55 tools · 6 pages"},
    {"id": "BatCave",           "n": "BATCAVE",           "c": "#ffd60a", "f": "batman_face.jpg",   "i": "🦇", "d": "Investigation · 31 tools"},
    {"id": "JokerChaos",        "n": "JOKER CHAOS",       "c": "#9b30ff", "f": "joker_face.jpg",    "i": "🃏", "d": "Chaos · 8 pranks"},
    {"id": "TridentAquaman",    "n": "TRIDENT AQUAMAN",   "c": "#40e0d0", "f": "aquaman_face.jpg",  "i": "🔱", "d": "Réseau · 8 tools"},
    {"id": "SupermanVision",    "n": "SUPERMAN",          "c": "#ff4628", "f": "superman_face.jpg", "i": "🦸", "d": "Vision · 8 tools"},
    {"id": "ConstantineDark",   "n": "CONSTANTINE",       "c": "#90ff78", "f": "constantine_face.jpg",                "i": "🕯️", "d": "Dark web · 10 tools"},
    {"id": "LassoVerite",       "n": "LASSO VÉRITÉ",      "c": "#ffdc50", "f": "wonder_woman_face.jpg", "i": "🪢", "d": "Vérification · 8 tools"},
    {"id": "CyborgTech",        "n": "CYBORG TECH",       "c": "#00c8ff", "f": "cyborg_face.jpg",   "i": "🤖", "d": "Technet · 8 tools"},
    {"id": "LexCorpIndustries", "n": "LEXCORP",           "c": "#39ff14", "f": "lex_luthor_face.jpg", "i": "🏢", "d": "Arsenal Windows · 7 modules"},
    {"id": "STARLabs",          "n": "S.T.A.R. LABS",     "c": "#00c8ff", "f": "starlabs_face.jpg",                "i": "🔬", "d": "C2 DNS + HTTP · 5 tools"},
    {"id": "TaskForceX",        "n": "TASK FORCE X",      "c": "#ff6a00", "f": "taskforce_face.jpg",                "i": "🎯", "d": "Déploiement · 2 tools"},
    {"id": "NeoMatrix",         "n": "NEO / LA MATRICE",  "c": "#00ff70", "f": "matrix_face.jpg",   "i": "💊", "d": "10 tools"},
    {"id": "ForceGalaxy",       "n": "LA FORCE",          "c": "#ffd60a", "f": "force_face.jpg",    "i": "🌟", "d": "8 tools"},
    {"id": "CatwomanVoleuse",   "n": "CATWOMAN",          "c": "#ffdc50", "f": "catwoman_face.jpg", "i": "🐱", "d": "Secrets · 8 tools"},
    {"id": "HiveMining",        "n": "H.I.V.E.",          "c": "#ffc800", "f": "hive_face.jpg",                "i": "🍯", "d": "Minage · 8 tools"},
    {"id": "ScarecrowPhish",    "n": "SCARECROW",         "c": "#ff8c30", "f": "scarecrow_face.jpg", "i": "🎃", "d": "Phishing · 12 sites"},
    {"id": "WarWorld",          "n": "WARWORLD",          "c": "#ff4628", "f": "warworld_face.jpg",                "i": "⚔️", "d": "Arsenal · 110 armes / 16 thèmes"},
    {"id": "LeagueOfShadows",   "n": "LIGNE ROUGE",       "c": "#c9a600", "f": "league_face.jpg",   "i": "🥷", "d": "Orchestrateur · 3 commands"},
    {"id": "KryptoniteSuite",   "n": "KRYPTONITE SUITE",  "c": "#39ff14", "f": "kryptonite_face.jpg", "i": "🟩", "d": "Défense · 4 tools"},
    {"id": "WOPR",              "n": "W.O.P.R.",          "c": "#7fff00", "f": "wopr_face.jpg",     "i": "🎮", "d": "Auto-lab WarGames · 4 commands"},
    {"id": "TheCalculator",     "n": "THE CALCULATOR",    "c": "#00c8ff", "f": "calculator_face.jpg",                "i": "📊", "d": "Breach analytics · 2 tools"},
    {"id": "RavenEvasion",      "n": "RAVEN",             "c": "#8899ff", "f": "raven_face.jpg",    "i": "🐦‍⬛", "d": "Évasion EDR · 5 modules"},
    {"id": "TheThinker",        "n": "THE THINKER",       "c": "#9b30ff", "f": "thinker_face.jpg",                "i": "🧠", "d": "Reverse engineering · 8 commands"},
    {"id": "JokerCard",         "n": "JOKER CARD",        "c": "#ff6a00", "f": "jokercard_face.jpg",                "i": "🂡", "d": "SGP Card · BadUSB · 4 tools"},
    {"id": "DailyPlanet",       "n": "DAILY PLANET",      "c": "#64a0ff", "f": "dailyplanet_face.jpg",                "i": "📰", "d": "Veille · 25 sources · 3 tools"},
]
KIT_BY_ID = {k["id"]: k for k in KITS}

def read_json(path):
    try: return json.load(open(os.path.expanduser(path)))
    except Exception: return {}

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        if p.startswith("/face/"):                      return self._face(p)
        if p == "/api/status":                          return self._api_status()
        if p.startswith("/pages/"):                     return self._static(p[len("/pages/"):], PAGES)
        if p.startswith("/gotham_static/"):             return self._static(p[len("/gotham_static/"):], os.path.join(TOOL_DC, "gotham_static"))
        if p.startswith("/kit/"):
            kid = p.split("/kit/")[1].split("?")[0]
            kit = KIT_BY_ID.get(kid)
            if kit: return self._html(build_kit_page(kit))
        if p == "/arsenal":                             return self._arsenal_dc()
        return self._html(build_index())

    def _face(self, p):
        fname = os.path.basename(p)
        img = os.path.join(FACES, fname)
        if os.path.exists(img) and (fname.endswith(".png") or fname.endswith(".jpg")):
            data = open(img, "rb").read()
            ct = "image/jpeg" if fname.endswith(".jpg") else "image/png"
            self.send_response(200); self.send_header("Content-Type", ct)
            self.send_header("Content-Length", str(len(data))); self.send_header("Cache-Control", "no-cache")
            self.end_headers(); self.wfile.write(data)
        else: self.send_response(404); self.end_headers()

    def _static(self, rel, base):
        rel = urllib.parse.unquote(rel)
        full = os.path.normpath(os.path.join(base, rel))
        if not full.startswith(os.path.normpath(base)) or not os.path.isfile(full):
            self.send_response(404); self.end_headers(); return
        ct = "text/html" if full.endswith(".html") else "text/css" if full.endswith(".css") else "image/png" if full.endswith(".png") else "application/octet-stream"
        data = open(full, "rb").read()
        self.send_response(200); self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _arsenal_dc(self):
        full = os.path.join(TOOL_DC, "arsenal_dc.html")
        if not os.path.isfile(full):
            self.send_response(404); self.end_headers(); return
        data = open(full, "rb").read()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)

    def _api_status(self):
        self._json({"news": read_json(f"{TOOL_DC}/DailyPlanet/veille_cache.json").get("items", [])[:8],
                    "captures": read_json(f"{TOOL_DC}/ScarecrowPhish/sorties/mirror_captures.json")[-3:],
                    "scan": read_json(f"{TOOL_DC}/KryptoniteSuite/sorties/scan.json")})

    def _json(self, d):
        b = json.dumps(d, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _html(self, h):
        b = h.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-cache")
        self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

TPL_PATH = os.path.join(TOOL_DC, "design_preview", "page_principale.html")

def _load_index_template():
    """Charge le template design de l'utilisateur et sépare la zone dynamique des cartes."""
    try:
        tpl = open(TPL_PATH, encoding="utf-8").read()
        head, rest = tpl.split('<main id="grid">', 1)
        _grid_content, tail = rest.split('</main>', 1)
        return head, tail
    except Exception:
        return None, None

def face_visual(kit, height=180):
    c, f = kit["c"], kit["f"]
    if f and os.path.exists(os.path.join(FACES, f)):
        return (f'<img src="/face/{f}" alt="{kit["n"]}">'
                f'<div class="duo"></div>')
    return f'<div class="emoji-tile"><span class="emoji">{kit["i"]}</span></div>'

def build_index():
    head, tail = _load_index_template()
    if head is None:   # fallback si le template n'existe pas
        head, tail = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>GOTHAM CITY — L'ARSENAL DC</title>
<style>body{background:#06070c;color:#ccc;font-family:sans-serif}</style></head><body>
<h1>GOTHAM CITY</h1><main id="grid">""", "</main><footer>placeholder — template manquant</footer></body></html>"
    cards = ""
    for idx, k in enumerate(KITS):
        nn = f"{idx + 1:02d}"
        d_ms = idx * 40
        badge_d = {"FlashToolSuper": 55, "BatCave": 31, "WarWorld": 110}.get(k["id"])
        chip = (f"⚡ {badge_d} TOOLS" if badge_d else k["d"].split("·")[-1].strip())
        data_k = (k["n"] + " " + k["d"]).lower()
        cards += f"""      <a class="kit-card" href="/kit/{k['id']}" style="--c:{k['c']};--d:{d_ms}ms" data-k="{data_k}">
        <span class="ghost">{nn}</span>
        <div class="kit-vis">
          {face_visual(k)}
          <span class="halftone"></span>
          <span class="idx">N<sup>o</sup>&nbsp;{nn}</span>
          <span class="chip">{chip} →</span>
          <div class="sweep"></div>
          <div class="glow"></div>
        </div>
        <div class="kit-body">
          <h3 class="kit-name">{k['n']}</h3>
          <div class="kit-desc">{k['d']}</div>
          <div class="kit-go"><span class="line"></span>ACCÉDER AU KIT <span class="arr">&rarr;</span></div>
        </div>
      </a>
"""
    return head + '<main id="grid">\n' + cards + '      <div class="nores" id="nores">Aucun kit ne correspond.</div>\n</main>' + tail

def build_kit_page(kit):
    dpath = os.path.join(TOOL_DC, "arsenal_pages_data", f"{kit['id']}.json")
    tools = []
    if os.path.exists(dpath):
        try: tools = json.load(open(dpath, encoding="utf-8")).get("tools", [])
        except Exception: tools = []
    rows = ""
    for t in tools:
        link = f"/pages/{kit['id']}/{t['slug']}.html"
        rows += f"""
        <a class="tool" href="{link}" style="--c:{kit['c']}">
          <div class="tool-head"><span class="tool-num">{t['num']}</span><b>{t['name']}</b><span class="tool-theme">{t['theme']}</span></div>
          <p>{t['desc']}</p>
        </a>"""
    if not rows:
        rows = f'<p style="color:#666">La liste détaillée est dans le repo GitHub : <a style="color:{kit["c"]}" href="{GITHUB}">{GITHUB}</a></p>'
    avatar = (f'<img src="/face/{kit["f"]}" alt="" '
              f'style="width:120px;height:120px;object-fit:cover;border-radius:16px;border:2px solid {kit["c"]}55;flex-shrink:0">'
              if kit["f"] and os.path.exists(os.path.join(FACES, kit["f"])) else
              f'<div style="width:120px;height:120px;border-radius:16px;display:grid;place-items:center;'
              f'font-size:3.4em;background:linear-gradient(150deg,{kit["c"]}30,{kit["c"]}08);'
              f'border:2px solid {kit["c"]}55;flex-shrink:0">{kit["i"]}</div>')
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{kit['n']} — GOTHAM CITY</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#04040a;color:#bbb;font-family:-apple-system,sans-serif;min-height:100vh}}
.banner{{display:flex;gap:22px;align-items:center;max-width:860px;margin:28px auto 0;padding:22px 26px;
background:linear-gradient(135deg,{kit['c']}14,transparent 70%);border:1px solid {kit['c']}2e;border-radius:18px}}
.banner .info{{flex:1;min-width:0}}
.back{{color:{kit['c']};text-decoration:none;font-size:.82em}}
h1{{color:#fff;font-size:1.9em;margin:6px 0 3px;letter-spacing:-.5px}}
.sub{{color:#666;font-size:.85em;margin-bottom:12px}}
.gh{{display:inline-block;color:#fff;text-decoration:none;font-size:.8em;font-weight:600;
background:{kit['c']}1e;border:1px solid {kit['c']}55;padding:8px 16px;border-radius:9px}}
.gh:hover{{background:{kit['c']}30}}
main{{max-width:860px;margin:20px auto 0;padding:0 24px 40px}}
.tool{{display:block;background:#0a0a16;border:1px solid #191932;border-left:3px solid var(--c);
border-radius:11px;padding:15px 17px;margin-bottom:11px;text-decoration:none;transition:border-color .2s,transform .2s}}
.tool:hover{{border-color:var(--c);transform:translateX(4px)}}
.tool-head{{display:flex;gap:10px;align-items:baseline}}
.tool-num{{color:var(--c);font-weight:800;min-width:26px;font-size:1.05em}}
.tool b{{color:#fff;font-size:.95em}}
.tool-theme{{margin-left:auto;color:var(--c);font-size:.72em;opacity:.85;letter-spacing:.5px}}
.tool p{{color:#777;font-size:.83em;margin:5px 0 0 36px}}
footer{{text-align:center;color:#333;padding:36px;font-size:.72em;letter-spacing:2px}}
</style></head><body>
<div class="banner">
  {avatar}
  <div class="info">
    <a class="back" href="/">← Gotham City</a>
    <h1>{kit['n']}</h1>
    <p class="sub">{kit['d']}</p>
    <a class="gh" href="{GITHUB}" target="_blank">⭐ Code source sur GitHub → {kit['id']}</a>
  </div>
</div>
<main>
{rows}
</main>
<footer>{kit['n']} · GOTHAM CITY · <a style="color:#555" href="{GITHUB}">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
</body></html>"""

if __name__ == "__main__":
    nf = sum(1 for k in KITS if k["f"] and os.path.exists(os.path.join(FACES, k["f"])))
    print(f"[*] GOTHAM CITY v8 sur http://127.0.0.1:{PORT} — {len(KITS)} kits, {nf} visages, zéro doublon")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
