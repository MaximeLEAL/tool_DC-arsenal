#!/usr/bin/env python3
# language: Python 3, file: build_catalog.py, target: macOS
# Génère arsenal_dc.html — LE CATALOGUE de l'arsenal, style Gotham, données à jour
# (27 kits, 249 tools, recherche live, fiches liées)
import os, sys, json, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from generate_all_pages import KITS, GITHUB

DATA = os.path.join(ROOT, "arsenal_pages_data")
OUT = os.path.join(ROOT, "arsenal_dc.html")
FACES = os.path.join(ROOT, "gotham_static", "faces")

total_tools = 0
sections = ""
for num, folder, name, color, emoji, face in KITS:
    jpath = os.path.join(DATA, f"{folder}.json")
    if not os.path.exists(jpath): continue
    d = json.load(open(jpath, encoding="utf-8"))
    tools = d.get("tools", [])
    total_tools += len(tools)
    cmd = d.get("cmd", "")
    if face and os.path.exists(os.path.join(FACES, face)):
        av = (f'<img src="gotham_static/faces/{face}" alt="" loading="lazy" '
              f'style="width:64px;height:64px;object-fit:cover;border-radius:10px;border:1px solid {color}66">')
    else:
        av = (f'<div style="width:64px;height:64px;border-radius:10px;display:grid;place-items:center;'
              f'font-size:1.9em;background:radial-gradient(70% 70% at 50% 35%,{color}40,transparent 75%),'
              f'var(--panel2);border:1px solid {color}44">{emoji}</div>')
    rows = "".join(
        f'<a class="t" href="{folder}/{t["slug"]}.html" data-k="{H.escape((t["name"] + " " + t["theme"] + " " + t["desc"]).lower())}">'
        f'<span class="n">{H.escape(t["num"])}</span>'
        f'<span class="nm">{H.escape(t["name"])}</span>'
        f'<span class="th">{H.escape(t["theme"])}</span>'
        f'<span class="ds">{H.escape(t["desc"])}</span></a>'
        for t in tools)
    cmd_html = f'<code>{H.escape(cmd)}</code>' if cmd else ""
    sections += f"""
    <section class="kit" id="{folder}" style="--c:{color}" data-kit="{H.escape(name.lower() + ' ' + folder.lower())}">
      <div class="khead">{av}
        <div class="kinfo">
          <h2>{H.escape(name)}</h2>
          <span class="kcount">{len(tools)} tools</span>
        </div>
        <button class="kfold" onclick="toggleKit('{folder}')">▾</button>
      </div>
      {cmd_html and f'<div class="kcmd">{cmd_html}</div>' or ''}
      <div class="kbody" id="body-{folder}">{rows}</div>
    </section>"""

css = """:root{--bg:#06070c; --panel:#0c0e17; --panel2:#070810; --line:#1a1c2e;
  --txt:#c4c6d6; --muted:#6a6d86; --dim:#45485e; --red:#e63022; --gold:#f5c518;
  --disp:"Anton",Impact,sans-serif; --cond:"Oswald",sans-serif;
  --sans:"Archivo",-apple-system,sans-serif; --mono:"JetBrains Mono",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:var(--sans);min-height:100vh;position:relative}
::selection{background:var(--red);color:#fff}
::-webkit-scrollbar{width:11px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:#1c1e30;border-radius:6px;border:2px solid var(--bg)}
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.bg .beam{position:absolute;inset:0;background:
  radial-gradient(44% 70% at 50% 108%,rgba(245,197,24,.09),transparent 60%),
  radial-gradient(60% 80% at 50% -10%,rgba(230,48,34,.14),transparent 62%)}
.bg .dots{position:absolute;inset:0;opacity:.12;background-image:radial-gradient(rgba(255,255,255,.5) 1px,transparent 1.4px);background-size:16px 16px;mask-image:radial-gradient(ellipse 70% 55% at 50% 20%,#000 10%,transparent 72%)}
.bg .grid{position:absolute;inset:0;opacity:.5;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:52px 52px;mask-image:radial-gradient(ellipse 85% 70% at 50% 30%,#000 35%,transparent 88%)}
.bg .vig{position:absolute;inset:0;background:radial-gradient(ellipse 100% 80% at 50% 30%,transparent 55%,rgba(0,0,0,.55))}
.wrap{position:relative;z-index:1}
.nav{display:flex;justify-content:space-between;align-items:center;padding:14px clamp(18px,4vw,40px);position:sticky;top:0;z-index:30;background:rgba(6,7,12,.55);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.brand{font-family:var(--cond);font-weight:700;letter-spacing:5px;font-size:.95rem;color:#fff;display:flex;align-items:center;gap:11px;text-transform:uppercase;text-decoration:none}
.brand .dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 14px var(--red);animation:pulse 2s infinite}
.brand em{color:var(--red);font-style:normal}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.nav-right{display:flex;align-items:center;gap:14px}
.status{font-family:var(--mono);font-size:.64rem;letter-spacing:1.6px;color:#4ad66d;display:flex;align-items:center;gap:7px;text-transform:uppercase}
.status::before{content:"";width:6px;height:6px;border-radius:50%;background:#4ad66d;box-shadow:0 0 10px #4ad66d}
.ghbtn{font-family:var(--mono);color:#9fb4ff;font-size:.7rem;letter-spacing:.6px;text-decoration:none;border:1px solid var(--line);padding:8px 15px;border-radius:10px;transition:.25s}
.ghbtn:hover{border-color:#6495ff;color:#cdd9ff}
.hero{text-align:center;padding:clamp(44px,8vw,90px) 20px 36px}
h1{font-family:var(--disp);font-size:clamp(3rem,10vw,6.6rem);line-height:.9;color:#fff;letter-spacing:2px;text-transform:uppercase;text-shadow:0 3px 0 rgba(0,0,0,.55),0 0 70px rgba(245,197,24,.2)}
h1 b{background:linear-gradient(120deg,var(--red) 0%,#ff6a3d 50%,var(--gold) 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
.sous{margin-top:14px;font-family:var(--mono);color:var(--muted);letter-spacing:3px;font-size:.72rem;text-transform:uppercase}
.stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-top:32px}
.stat{background:linear-gradient(180deg,rgba(255,255,255,.045),rgba(255,255,255,.008));border:1px solid var(--line);border-radius:12px;padding:15px 26px;min-width:110px}
.stat b{display:block;font-family:var(--disp);font-size:2rem;color:#fff;line-height:1}
.stat span{font-family:var(--mono);font-size:.6rem;letter-spacing:2px;color:var(--muted);margin-top:7px;display:block;text-transform:uppercase}
.searchbar{position:sticky;top:49px;z-index:20;background:rgba(6,7,12,.72);backdrop-filter:blur(14px);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:16px;display:flex;justify-content:center}
.searchbar input{font-family:var(--mono);font-size:.8rem;color:#fff;background:rgba(255,255,255,.03);border:1px solid var(--line);border-radius:10px;padding:11px 16px 11px 38px;width:min(460px,80vw);outline:none;transition:.25s}
.searchbar input:focus{border-color:var(--gold);box-shadow:0 0 24px rgba(245,197,24,.16)}
.searchbar svg{position:absolute;margin-left:-340px;stroke:var(--muted)}
.searchwrap{position:relative;display:flex;justify-content:center;width:100%}
main{max-width:900px;margin:26px auto 0;padding:0 24px 44px;position:relative;z-index:1}
.kit{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:4px;margin-bottom:16px;overflow:hidden;transition:border-color .3s}
.kit:hover{border-color:color-mix(in srgb,var(--c) 45%,var(--line))}
.kit.hide{display:none}
.khead{display:flex;gap:16px;align-items:center;padding:16px 20px;cursor:pointer}
.khead:hover{background:rgba(255,255,255,.025)}
.kinfo{flex:1;min-width:0}
h2{font-family:var(--cond);color:var(--c);font-size:1.2rem;letter-spacing:.8px;text-transform:uppercase}
.kcount{font-family:var(--mono);font-size:.62rem;letter-spacing:1.5px;color:var(--muted);text-transform:uppercase}
.kfold{font-family:var(--mono);background:none;border:1px solid var(--line);color:var(--muted);border-radius:8px;padding:6px 12px;cursor:pointer;transition:.2s}
.kfold:hover{color:#fff;border-color:var(--c)}
.kcmd{padding:10px 20px;background:#000;border-top:1px solid var(--line)}
.kcmd code{font-family:var(--mono);color:#4ad66d;font-size:.72rem}
.kbody{padding:12px 20px 16px}
.t{display:grid;grid-template-columns:28px minmax(150px,1fr) 120px 1fr;gap:12px;align-items:baseline;
  padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.04);border-radius:4px;text-decoration:none;transition:.2s}
.t:hover{background:color-mix(in srgb,var(--c) 7%,transparent)}
.t .n{font-family:var(--mono);color:var(--c);font-weight:700}
.t .nm{font-family:var(--cond);color:#fff;font-weight:600;font-size:.92rem;letter-spacing:.3px;text-transform:uppercase}
.t .th{font-family:var(--mono);color:var(--muted);font-size:.62rem;letter-spacing:.5px}
.t .ds{color:var(--muted);font-size:.8em}
@media(max-width:700px){.t{grid-template-columns:28px 1fr}.t .th,.t .ds{display:none}}
footer{text-align:center;color:var(--muted);padding:40px 20px 56px;font-family:var(--mono);font-size:.66rem;letter-spacing:2.2px;border-top:1px solid var(--line);text-transform:uppercase}
footer a{color:#9fb4ff;text-decoration:none}
"""

page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>L'ARSENAL DC — {len(KITS)} KITS · {total_tools} TOOLS</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;500;600;700&family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<div class="bg"><div class="beam"></div><div class="dots"></div><div class="grid"></div><div class="vig"></div></div>
<div class="wrap">
<nav class="nav"><a class="brand" href="https://maximeleal.github.io/tool_DC-arsenal/"><span class="dot"></span>Gotham <em>City</em></a>
  <div class="nav-right"><span class="status">Catalogue officiel</span>
  <a class="ghbtn" href="{GITHUB}" target="_blank">&#8599; GITHUB</a></div></nav>
<header class="hero">
  <h1>L'ARSENAL <b>DC</b></h1>
  <div class="sous">LE CATALOGUE COMPLET · POWERED BY MAXIME LEAL</div>
  <div class="stats">
    <div class="stat"><b>{len(KITS)}</b><span>Kits</span></div>
    <div class="stat"><b>{total_tools}</b><span>Tools</span></div>
    <div class="stat"><b>26</b><span>Persos</span></div>
    <div class="stat"><b>100%</b><span>Documenté</span></div>
  </div>
</header>
<div class="searchbar"><div class="searchwrap">
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
  <input id="q" placeholder="Rechercher un tool, un kit, un thème…" spellcheck="false">
</div></div>
<main>{sections}</main>
<footer>L'ARSENAL DC · {len(KITS)} KITS · {total_tools} TOOLS · <a href="{GITHUB}">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
</div>
<script>
function toggleKit(id){{
  const b = document.getElementById('body-' + id);
  b.style.display = b.style.display === 'none' ? '' : 'none';
}}
const q = document.getElementById('q');
q.addEventListener('input', () => {{
  const v = q.value.trim().toLowerCase();
  document.querySelectorAll('.kit').forEach(k => {{
    const kitMatch = !v || (k.dataset.k || '').includes(v);
    let tools = 0;
    k.querySelectorAll('.t').forEach(t => {{
      const ok = !v || (t.dataset.k || '').includes(v);
      t.style.display = ok ? '' : 'none';
      if (ok) tools++;
    }});
    k.classList.toggle('hide', !kitMatch && tools === 0);
  }});
}});
</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(page)
print(f"arsenal_dc.html : {len(KITS)} kits · {total_tools} tools ({len(page)//1024} Ko)")
