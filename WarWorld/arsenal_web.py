#!/usr/bin/env python3
# language: Python 3, file: arsenal_web.py v3 — LE VISAGE DE DEATHSTROKE, target: macOS
# Re-design : orange/noir du mercenaire, masque SVG, liens d'achat reels, budget, filtres
import http.server, urllib.parse, sys, os, json as _json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arsenal_data import ARSENAL, DETAILS
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8089
TYPE_ICON = {"LOGICIEL": "⌨", "HARDWARE": "🔌", "LAB": "🧪"}

DATA_FLAT = {}
for theme, weapons in ARSENAL.items():
    for name, typ, desc, statut in weapons:
        d = DETAILS.get(name, {})
        DATA_FLAT[f"{theme}|{name}"] = {"theme": theme, "nom": name, "type": typ,
            "desc": desc, "statut": statut, "prix": d.get("prix", 0),
            "kit": d.get("kit", ""), "usage": d.get("usage", ""), "buy": d.get("buy", "")}

def counts():
    c = {"LAB": 0, "REF": 0, "ACHAT": 0, "FERME": 0}
    for w in DATA_FLAT.values(): c[w["statut"]] = c.get(w["statut"], 0) + 1
    return c

HTML = """<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>WARWORLD — l'Arsenal du Mercenaire</title>
<style>
body{background:#060606;color:#d8d8d8;font-family:'Segoe UI',Arial,sans-serif;margin:0}
.mast{display:grid;grid-template-columns:190px 1fr;gap:0;background:#000;border-bottom:3px solid #ff6a00}
.mask{background:#000;text-align:center;padding:10px}
.mast-txt{padding:26px 30px 18px}
h1{color:#ff6a00;font-size:2.4em;margin:0;text-transform:uppercase;letter-spacing:4px;
text-shadow:0 0 24px rgba(255,106,0,.4)}
h1 small{display:block;color:#777;font-size:.36em;letter-spacing:6px;font-style:italic}
.stats{display:flex;gap:12px;margin:16px 0 0;flex-wrap:wrap}
.stat{padding:8px 18px;border-radius:8px;font-weight:bold;font-size:.9em;background:#111}
.layout{display:grid;grid-template-columns:250px 1fr;gap:20px;max-width:1150px;margin:22px auto}
#themes div{padding:11px 16px;border-left:3px solid #333;margin-bottom:6px;cursor:pointer;color:#aaa}
#themes div:hover{color:#ff6a00;border-left-color:#ff6a00}
#themes div.sel{background:#1a0d00;color:#ff6a00;border-left-color:#ff6a00}
#themes div span{float:right;color:#555}
.weapon{background:#0d0d0d;border:1px solid #262626;border-left:3px solid #ff6a00;
border-radius:8px;padding:15px 18px;margin-bottom:11px}
.weapon h3{color:#fff;margin:0 0 4px;font-size:1.05em}
.badge{border-radius:4px;padding:2px 10px;font-size:.72em;font-weight:bold}
.theme-tag{color:#ff6a00;font-size:.78em;margin:4px 0}
.weapon p{color:#9a9a9a;font-size:.88em;margin:6px 0 0}
.buy{display:inline-block;margin-top:10px;background:#ff6a00;color:#000;font-weight:bold;
padding:7px 18px;border-radius:6px;text-decoration:none;font-size:.85em}
.buy:hover{background:#ff8c30}
.search{width:100%;box-sizing:border-box;background:#0d0d0d;border:1px solid #262626;color:#ddd;
padding:11px 16px;border-radius:20px;margin:12px 0;font-size:1em}
.chip{background:#111;color:#ff6a00;padding:6px 16px;border-radius:20px;font-size:.85em;
border:1px solid #262626;cursor:pointer;margin-right:6px}
.chip.sel{background:#ff6a00;color:#000}
details summary{cursor:pointer;color:#ff6a00;font-size:.85em;margin-top:8px}
details p{color:#999;font-size:.88em;margin:8px 0 0}
details .usage{color:#ff8c30}
.priceline{color:#ff6a00;margin-top:8px;font-weight:bold}
</style></head><body>
<div class="mast">
  <div class="mask">
    <svg width="150" height="150" viewBox="0 0 100 100">
      <!-- Deathstroke : le masque du mercenaire, moitie or, moitie ombre -->
      <defs>
        <linearGradient id="or" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#ff8c30"/><stop offset="1" stop-color="#c96100"/>
        </linearGradient>
      </defs>
      <path d="M50 4 L88 14 L88 52 Q88 82 50 96 Q12 82 12 52 L12 14 Z" fill="#0d0d0d" stroke="#333"/>
      <path d="M50 4 L88 14 L88 52 Q88 82 50 96 Z" fill="url(#or)"/>
      <path d="M50 4 L88 14 L88 52 Q88 82 50 96 Z" fill="none" stroke="#111" stroke-width="1"/>
      <path d="M14 20 L40 24 L40 34 L16 32 Z" fill="#e8e8e8"/>
      <path d="M14 20 L40 24 L40 34 L16 32 Z" fill="none" stroke="#111"/>
      <path d="M50 22 L84 30 L84 44 L52 40 Z" fill="#0a0a0a"/>
      <path d="M50 22 L60 40 L48 40 Z" fill="#0a0a0a"/>
      <path d="M50 4 L50 96" stroke="#000" stroke-width="2"/>
      <path d="M30 60 L70 60 L70 66 L30 66 Z" fill="#0a0a0a" opacity=".6"/>
      <path d="M34 70 L66 70" stroke="#555" stroke-width="1.5"/>
      <path d="M36 78 L64 78" stroke="#444" stroke-width="1"/>
    </svg>
  </div>
  <div class="mast-txt">
    <h1>WARWORLD <small>l'arsenal du mercenaire · powered by Maxime Leal</small></h1>
    <div class="stats">
      <div class="stat" style="color:#39ff14">__N__ ARMES REGISTREES</div>
      <div class="stat" style="color:#6495ff">__REF__ RÉFÉRENCES</div>
      <div class="stat" style="color:#39ff14">__LAB__ DANS TON LAB</div>
      <div class="stat" style="color:#ff8c30">__ACHAT__ À ACQUÉRIR</div>
      <div class="stat" style="color:#88a">__FERME__ RESSOURCES FERMÉES</div>
    </div>
  </div>
</div>
<div class="layout">
  <div id="themes">__THEMES__</div>
  <div>
    <input class="search" id="q" placeholder="🔍 chasser une arme (nmap, ransomware, ducky, joker card…)">
    <div style="margin:10px 0" id="filtres">
      <span class="chip sel" data-f="">TOUTES</span>
      <span class="chip" data-f="LAB">DANS TON LAB</span>
      <span class="chip" data-f="REF">RÉFÉRENCES</span>
      <span class="chip" data-f="ACHAT">À ACQUÉRIR</span>
      <span class="chip" data-f="FERME">RESSOURCES FERMÉES</span>
    </div>
    <div id="cards"></div>
  </div>
</div>
<script>
var DATA = __JSON__;
var cur = "__CUR__", filtre = "";
function esc(s){return (s||'').replace(/</g,'&lt;');}
function draw(){
  var q = document.getElementById('q').value.toLowerCase();
  var el = document.getElementById('cards'); el.innerHTML = '';
  var n = 0;
  for (var key in DATA) {
    var w = DATA[key];
    if (cur && w.theme !== cur) continue;
    if (filtre && w.statut !== filtre) continue;
    if (q && !((w.nom + w.desc).toLowerCase().includes(q))) continue;
    var icon = {LOGICIEL:'⌨', HARDWARE:'🔌', LAB:'🧪'}[w.type] || '';
    var b = {LAB:['#0d1a0d','#39ff14','DANS TON ARSENAL'],REF:['#0d0d1a','#6495ff','RÉFÉRENCE'],
             ACHAT:['#1a0d00','#ff6a00','À ACQUÉRIR']}[w.statut];
    var priceLine = w.prix ? `<div class="priceline">💰 ~${w.prix} EUR</div>` : '';
    var buyBtn = '';
    if (w.buy) buyBtn = `<a class="buy" href="${esc(w.buy)}" target="_blank">🛒 MAGASIN OFFICIEL ↗</a>`;
    else if (w.link) buyBtn = `<a class="buy" style="background:#16161a;color:#8899ff" href="${esc(w.link)}" target="_blank">🔗 DÉPÔT ↗</a>`;
    var details = (w.usage || w.kit) ? `<details><summary>fiche d'emploi</summary>
      ${w.usage ? '<p class="usage">USAGE : ' + esc(w.usage) + '</p>' : ''}
      ${w.kit ? '<p>KIT : ~/Desktop/' + esc(w.kit) + '</p>' : ''}</details>` : '';
    var div = document.createElement('div'); div.className = 'weapon';
    div.innerHTML = `<h3>${icon} ${esc(w.nom)}
      <span class="badge" style="background:${b[0]};color:${b[1]}">${b[2]}</span></h3>
      <div class="theme-tag">${esc(w.theme)} · ${esc(w.type)}</div>
      <p>${esc(w.desc)}</p>${priceLine}${buyBtn}${details}`;
    el.appendChild(div); n++;
  }
  if (!n) el.innerHTML = '<div class="weapon"><p>aucune arme ne correspond</p></div>';
}
document.querySelectorAll('#filtres .chip').forEach(function(ch){
  ch.onclick = function(){
    document.querySelectorAll('#filtres .chip').forEach(c=>c.classList.remove('sel'));
    ch.classList.add('sel'); filtre = ch.dataset.f; draw();
  };
});
document.getElementById('q').addEventListener('input', draw);
var th = document.getElementById('themes');
__THEMEHANDLERS__
draw();
</script></body></html>"""

def build_page(cur=None):
    cnt = counts()
    themes_html, handlers = "", []
    for i, theme in enumerate(ARSENAL):
        sel = " sel" if theme == cur else ""
        n = len(ARSENAL[theme])
        themes_html += f'<div class="{sel}" data-t="{theme}">{theme}<span>{n}</span></div>'
        handlers.append(f'th.children[{i}].onclick = function(){{cur = "{theme}";'
                        f'document.querySelectorAll("#themes div").forEach(d=>d.classList.remove("sel"));'
                        f'this.classList.add("sel");draw();}};')
    return (HTML.replace("__N__", str(len(DATA_FLAT))).replace("__REF__", str(cnt["REF"]))
            .replace("__LAB__", str(cnt["LAB"])).replace("__ACHAT__", str(cnt["ACHAT"])).replace("__FERME__", str(cnt.get("FERME", 0)))
            .replace("__THEMES__", themes_html).replace("__THEMEHANDLERS__", "\n".join(handlers))
            .replace("__JSON__", _json.dumps(DATA_FLAT, ensure_ascii=False))
            .replace("__CUR__", cur or ""))

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        page = build_page(q.get("theme", [None])[0]).encode()
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[*] WARWORLD v3 (Deathstroke) sur http://127.0.0.1:{PORT} — {len(DATA_FLAT)} armes")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
