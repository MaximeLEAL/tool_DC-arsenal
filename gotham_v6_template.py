<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GOTHAM CITY — L'ARSENAL DC</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{background:#030308;color:#c8c8d0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;overflow-x:hidden}

/* HEADER CINÉMATIQUE */
.hero{position:relative;height:45vh;min-height:350px;background:#000;overflow:hidden;display:flex;align-items:center;justify-content:center}
.hero::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 50% at 50% 40%,rgba(255,214,10,.08),transparent 70%);z-index:1}
.hero::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent 40%,#030308 100%);z-index:2}
.bat-signal{position:absolute;top:8%;left:50%;transform:translateX(-50%);width:300px;height:200px;
background:radial-gradient(ellipse at center,rgba(255,214,10,.12),transparent 70%);animation:signal 4s ease-in-out infinite}
@keyframes signal{0%,100%{opacity:.4;transform:translateX(-50%) scale(1)}50%{opacity:.9;transform:translateX(-50%) scale(1.1)}}
.hero-content{position:relative;z-index:5;text-align:center}
.hero-content h1{font-family:'Orbitron',sans-serif;font-size:clamp(2.2em,6vw,4.5em);color:#fff;
letter-spacing:4px;text-shadow:0 0 40px rgba(255,214,10,.4),0 2px 0 #000}
.hero-content h1 b{color:#ff4628}
.hero-content .sub{color:#666;letter-spacing:8px;font-size:.85em;margin-top:12px;text-transform:uppercase}
.hero-content .sub b{color:#ff4628;font-style:italic}
.hero-stats{display:flex;gap:14px;justify-content:center;margin-top:24px;flex-wrap:wrap}
.hs{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:12px 28px;text-align:center;backdrop-filter:blur(8px)}
.hs b{color:#ffd60a;font-size:1.6em;display:block}
.hs span{color:#666;font-size:.72em;text-transform:uppercase;letter-spacing:2px}
/* scanline */
.scanline{position:fixed;top:0;left:0;right:0;height:2px;z-index:999;pointer-events:none;
background:linear-gradient(90deg,transparent,rgba(255,214,10,.15),transparent);animation:scanmove 5s linear infinite}
@keyframes scanmove{from{transform:translateY(0)}to{transform:translateY(100vh)}}

/* GRID PROFESSIONNELLE */
#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:22px;
max-width:1450px;margin:30px auto;padding:0 20px}
.kit-card{background:#0a0a14;border:1px solid rgba(255,255,255,.06);border-radius:16px;overflow:hidden;
cursor:pointer;transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;display:flex;flex-direction:column}
.kit-card:hover{transform:translateY(-8px) scale(1.02);border-color:var(--c);z-index:10;
box-shadow:0 20px 60px -10px var(--c)33,0 0 0 1px var(--c)}
.kit-card:active{transform:translateY(-4px) scale(1.01)}

/* image area — ratio fixe, cadre propre */
.kit-visual{width:100%;height:180px;position:relative;overflow:hidden;background:var(--d)}
.kit-visual img{width:100%;height:100%;object-fit:cover;transition:transform .4s cubic-bezier(.4,0,.2,1)}
.kit-card:hover .kit-visual img{transform:scale(1.08)}
.kit-visual .icon{position:absolute;inset:0;display:grid;place-items:center;font-size:4em;
background:linear-gradient(135deg,var(--c)15,var(--c)05)}
/* overlay gradient pour lisibilité */
.kit-visual::after{content:'';position:absolute;bottom:0;left:0;right:0;height:50%;
background:linear-gradient(0deg,#0a0a14 20%,transparent)}

/* info area */
.kit-info{padding:16px 18px 18px;flex:1;display:flex;flex-direction:column}
.kit-name{font-family:'Orbitron',sans-serif;font-size:1em;font-weight:700;color:var(--c);letter-spacing:1px}
.kit-desc{color:#888;font-size:.82em;margin:6px 0 8px;line-height:1.4;flex:1}
.kit-footer{display:flex;justify-content:space-between;align-items:center}
.kit-tools{background:var(--c);color:#000;border-radius:12px;padding:2px 14px;font-size:.72em;font-weight:700}
.kit-link{color:var(--c);font-size:.72em;opacity:.6}

/* SECTION FILTRES */
.filters{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;padding:20px;position:sticky;top:0;z-index:50;
background:rgba(3,3,8,.92);backdrop-filter:blur(12px);border-bottom:1px solid rgba(255,255,255,.05)}
.chip{padding:8px 22px;border-radius:20px;font-size:.82em;cursor:pointer;border:1px solid #2a2a3a;
background:#0a0a14;color:#c9a600;transition:all .2s;font-family:inherit}
.chip:hover{border-color:#ffd60a}
.chip.active{background:#ffd60a;color:#000;font-weight:bold}
.search-box{display:flex;justify-content:center;margin:16px auto;max-width:600px}
.search-box input{width:100%;background:#0a0a14;border:1px solid #2a2a3a;color:#ddd;
padding:14px 24px;border-radius:24px;font-size:1em;font-family:monospace;text-align:center}
.search-box input:focus{outline:none;border-color:#ffd60a;box-shadow:0 0 20px rgba(255,214,10,.15)}

/* footer */
footer{text-align:center;color:#1a1a2a;padding:50px;font-size:.7em;letter-spacing:3px}
</style>
</head>
<body>
<div class="scanline"></div>

<div class="hero">
  <div class="bat-signal"></div>
  <div class="hero-content">
    <h1>GOTHAM <b>CITY</b></h1>
    <div class="sub">L'ARSENAL DC COMPLET · POWERED BY <b>MAXIME LEAL</b></div>
    <div class="hero-stats">
      <div class="hs"><b id="stKits">26</b><span>KITS</span></div>
      <div class="hs"><b id="stTools">~240</b><span>TOOLS</span></div>
      <div class="hs"><b id="stSessions">0</b><span>SESSIONS C2</span></div>
      <div class="hs"><b id="stCaptures">0</b><span>CAPTURES</span></div>
      <div class="hs"><b id="stIOCs">0</b><span>IOCs</span></div>
    </div>
  </div>
</div>

<div class="search-box"><input id="q" placeholder="🔍 Rechercher un tool, un thème, une capacité…"></div>
<div class="filters" id="filters"></div>
<div id="grid"></div>
<footer>GOTHAM CITY · L'ARSENAL DC COMPLET · POWERED BY MAXIME LEAL</footer>

<script>
const KITS = __KITS_DATA__;
const esc = s => (s||'').toString().replace(/</g,'&lt;');
let activeFilter = "";

function build(){
  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  KITS.forEach(kit => {
    const c = kit.color;
    const card = document.createElement('div');
    card.className = 'kit-card';
    card.style.setProperty('--c', c);
    card.style.setProperty('--d', kit.dark);
    // image
    let visual;
    if (kit.face_img) {
      visual = `<img src="/img/${kit.face_img}" alt="${esc(kit.name)}" loading="lazy">`;
    } else {
      visual = `<div class="icon">${kit.icon}</div>`;
    }
    card.innerHTML = visual + `
      <div class="kit-info">
        <div class="kit-name">${esc(kit.name)}</div>
        <div class="kit-desc">${esc(kit.desc)}</div>
        <div class="kit-footer">
          <span class="kit-tools">${kit.tools} tools</span>
          <span class="kit-link">Ouvrir →</span>
        </div>
      </div>`;
    card.onclick = () => { window.location.href = `/kit/${kit.id}`; };
    grid.appendChild(card);
  });
  applyFilters();
}

function applyFilters(){
  const q = document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('.kit-card').forEach(card => {
    const name = card.querySelector('.kit-name').textContent.toLowerCase();
    const desc = card.querySelector('.kit-desc').textContent.toLowerCase();
    const match = name.includes(q) || desc.includes(q);
    if (activeFilter) {
      const theme = card.querySelector('.kit-name').textContent.toLowerCase();
      card.style.display = match && activeFilter === 'all' ? '' :
        (match && theme.includes(activeFilter) ? '' : 'none');
    } else {
      card.style.display = match ? '' : 'none';
    }
  });
}

/* les images par kit */
const FACE_MAP = __FACE_MAP__;

/* charge les données et les images */
async function load(){
  const d = await (await fetch('/api/status')).json();
  document.getElementById('stSessions').textContent = Object.keys(d.sessions||{}).length;
  document.getElementById('stCaptures').textContent = (d.captures||[]).length;
  document.getElementById('stIOCs').textContent = (d.scan||[]).length;
  // injecte les images Wikipedia dans les cartes
  document.querySelectorAll('.kit-card').forEach(card => {
    const name = card.querySelector('.kit-name').textContent;
    const img = FACE_MAP[name];
    if (img) {
      const visual = card.querySelector('.kit-visual');
      if (visual && !visual.querySelector('img')) {
        visual.innerHTML = `<img src="/img/${img}" style="width:100%;height:100%;object-fit:cover;object-position:center 20%" alt="${esc(name)}">`;
      }
    }
  });
}
</script>
</body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path.startswith("/img/"):
            fname = os.path.basename(u.path)
            img = os.path.join(TOOL_DC, "gotham_static", "images", fname)
            if os.path.exists(img):
                with open(img, "rb") as f: data = f.read()
                ct = "image/png" if fname.endswith(".png") else "image/jpeg"
                self.send_response(200); self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data))); self.end_headers(); self.wfile.write(data)
            else: self.send_response(404); self.end_headers()
            return
        if u.path == "/api/status":
            self._json({"news": get_news(), "captures": get_captures(),
                        "sessions": get_sessions(), "fleet": get_fleet(), "scan": get_scan()})
            return
        if u.path == "/api/launch":
            q = urllib.parse.parse_qs(u.query)
            kid = q.get("kit", [""])[0]
            kit = next((k for k in KITS if k["id"] == kid), None)
            if kit:
                subprocess.Popen(kit["cmd"], shell=True, cwd=os.path.join(TOOL_DC, kit["id"]),
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self._json({"ok": True, "name": kit["name"]})
            else: self._json({"ok": False})
            return
        if u.path.startswith("/kit/"):
            kid = u.path.split("/kit/")[1].split("?")[0]
            kit = next((k for k in KITS if k["id"] == kid), None)
            if kit: self._html(build_kit_page(kit)); return
        self._html(build_page())
    def _json(self, d):
        b = json.dumps(d, ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def _html(self, h):
        b = h.encode()
        self.send_response(200); self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

# les données pour le JS (générées par Python)
def build_face_map():
    fm = {}
    for kit in KITS:
        face = kit.get("face")
        if face and os.path.exists(os.path.join(IMG_DIR, face)):
            fm[kit["name"]] = face
    return fm

def build_kits_json():
    return json.dumps([{**k, "face_img": k.get("face") if os.path.exists(os.path.join(IMG_DIR, k.get("face",""))) else None} for k in KITS], ensure_ascii=False)
