#!/usr/bin/env python3
# language: Python 3, file: generate_all_pages_v2.py, target: macOS
# Génère les pages web pour TOUS les tools de TOUS les 26 kits
# Chaque page a : le SVG du personnage, les animations CSS, les liens GitHub réels
import os, sys, re, html as html_mod

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
GITHUB_USER = "MaximeLEAL"
GITHUB_BASE = f"https://github.com/{GITHUB_USER}/tool_DC-arsenal"
OUT = os.path.join(ROOT, "arsenal_web_pages")
os.makedirs(OUT, exist_ok=True)

MD = os.path.join(ROOT, "liste_tool.md")

DC_ICONS = {
    "RickPortal": "🟢", "FlashToolSuper": "⚡", "BatCave": "🦇", "JokerChaos": "🃏",
    "TridentAquaman": "🔱", "SupermanVision": "🦸", "ConstantineDark": "🕯️",
    "LassoVerite": "🪢", "CyborgTech": "🤖", "LexCorpIndustries": "🏢",
    "STARLabs": "🔬", "TaskForceX": "🎯", "NeoMatrix": "💊", "ForceGalaxy": "🌟",
    "CatwomanVoleuse": "🐱", "HiveMining": "🍯", "ScarecrowPhish": "🎃",
    "WarWorld": "⚔️", "LeagueOfShadows": "🥷", "KryptoniteSuite": "🟩",
    "WOPR": "🎮", "TheCalculator": "📊", "RavenEvasion": "🐦‍⬛",
    "TheThinker": "🧠", "JokerCard": "🂡", "DailyPlanet": "📰",
}
DC_COLORS = {
    "RickPortal": "#00ff70", "FlashToolSuper": "#ffd60a", "BatCave": "#ffd60a",
    "JokerChaos": "#9b30ff", "TridentAquaman": "#40e0d0", "SupermanVision": "#ff4628",
    "ConstantineDark": "#90ff78", "LassoVerite": "#ffdc50", "CyborgTech": "#00c8ff",
    "LexCorpIndustries": "#39ff14", "STARLabs": "#00c8ff", "TaskForceX": "#ff6a00",
    "NeoMatrix": "#00ff70", "ForceGalaxy": "#ffd60a", "CatwomanVoleuse": "#ffdc50",
    "HiveMining": "#ffc800", "ScarecrowPhish": "#ff8c30", "WarWorld": "#ff4628",
    "LeagueOfShadows": "#c9a600", "KryptoniteSuite": "#39ff14", "WOPR": "#7fff00",
    "TheCalculator": "#00c8ff", "RavenEvasion": "#8899ff", "TheThinker": "#9b30ff",
    "JokerCard": "#ff6a00", "DailyPlanet": "#64a0ff",
}


# les SVG de chaque personnage DC
SVGS = {
    "RickPortal": '<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="28" fill="none" stroke="#00ff70" stroke-width="2"/><circle cx="30" cy="30" r="20" fill="none" stroke="#00ff70" stroke-width="1" opacity=".5"/><circle cx="30" cy="30" r="10" fill="#00ff70" opacity=".3"/></svg>',
    "FlashToolSuper": '<svg viewBox="0 0 100 100"><path d="M50 5 L35 45 L50 45 L30 95 L70 40 L55 40 L65 5 Z" fill="#ffd60a" stroke="#fff" stroke-width="1.5"/></svg>',
    "BatCave": '<svg viewBox="0 0 100 60"><path d="M5 55 Q30 5 50 30 Q70 5 95 55 Q75 40 50 40 Q25 40 5 55Z" fill="#ffd60a" stroke="#fff"/></svg>',
    "JokerChaos": '<svg viewBox="0 0 60 60"><text x="30" y="30" text-anchor="middle" fill="#9b30ff" font-size="24" font-weight="bold">HA</text><text x="30" y="48" text-anchor="middle" fill="#57ff14" font-size="14">HA HA</text></svg>',
    "TridentAquaman": '<svg viewBox="0 0 60 60"><path d="M30 5 L30 55 M30 5 L20 15 M30 5 L40 15 M30 25 L15 35 M30 25 L45 35" stroke="#40e0d0" stroke-width="3" fill="none"/></svg>',
    "SupermanVision": '<svg viewBox="0 0 60 60"><path d="M30 5 L55 30 L30 55 L5 30 Z" fill="none" stroke="#ff4628" stroke-width="3"/><text x="30" y="38" text-anchor="middle" fill="#ffd60a" font-size="20" font-weight="bold">S</text></svg>',
    "ConstantineDark": '<svg viewBox="0 0 60 60"><rect x="25" y="35" width="10" height="20" fill="#c96100"/><path d="M30 25 Q28 15 32 10 Q30 20 30 25Z" fill="#ff8c30"/><circle cx="30" cy="30" r="25" fill="none" stroke="#333" stroke-dasharray="4 3"/></svg>',
    "LassoVerite": '<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="25" fill="none" stroke="#ffdc50" stroke-width="2" stroke-dasharray="6 4"/><text x="30" y="35" text-anchor="middle" fill="#fff" font-size="10">V</text></svg>',
    "CyborgTech": '<svg viewBox="0 0 60 60"><rect x="15" y="15" width="30" height="30" rx="5" fill="none" stroke="#00c8ff" stroke-width="2"/><path d="M25 15 L25 45 M35 15 L35 45 M15 25 L45 25 M15 35 L45 35" stroke="#00c8ff" stroke-width="1"/><circle cx="30" cy="30" r="5" fill="#00c8ff"/></svg>',
    "LexCorpIndustries": '<svg viewBox="0 0 60 60"><rect x="10" y="10" width="40" height="40" fill="none" stroke="#39ff14" stroke-width="2"/><text x="30" y="38" text-anchor="middle" fill="#39ff14" font-size="22" font-weight="bold">LX</text></svg>',
    "STARLabs": '<svg viewBox="0 0 60 60"><path d="M15 15 L45 15 L45 45 L15 45 Z" fill="none" stroke="#00c8ff" stroke-width="2"/><path d="M15 30 L45 30" stroke="#00c8ff"/><path d="M30 15 L30 45" stroke="#00c8ff"/><circle cx="30" cy="30" r="4" fill="#00c8ff"/></svg>',
    "TaskForceX": '<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="25" fill="none" stroke="#ff6a00" stroke-width="2"/><path d="M30 10 L30 50 M20 20 L40 40 M40 20 L20 40" stroke="#ff6a00"/></svg>',
    "NeoMatrix": '<svg viewBox="0 0 60 60"><text x="15" y="20" fill="#00ff70" font-size="12">ｱ</text><text x="35" y="35" fill="#00ff70" font-size="12">ｲ</text><text x="10" y="50" fill="#00ff70" font-size="12">ｳ</text><text x="40" y="15" fill="#00ff70" font-size="12">ｴ</text><text x="25" y="55" fill="#0f0" font-size="12">ｵ</text></svg>',
    "ForceGalaxy": '<svg viewBox="0 0 60 60"><path d="M30 5 L30 55" stroke="#ffd60a" stroke-width="2"/><path d="M10 30 L50 30" stroke="#ffd60a" stroke-width="2"/><circle cx="30" cy="30" r="8" fill="none" stroke="#ffd60a" stroke-width="2"/></svg>',
    "CatwomanVoleuse": '<svg viewBox="0 0 60 60"><path d="M15 15 L25 30 L15 45 M45 15 L35 30 L45 45" stroke="#ffdc50" stroke-width="2" fill="none"/><circle cx="30" cy="30" r="6" fill="#ffdc50"/></svg>',
    "HiveMining": '<svg viewBox="0 0 60 60"><path d="M30 10 L45 20 L45 40 L30 50 L15 40 L15 20 Z" fill="none" stroke="#ffc800" stroke-width="2"/><path d="M30 10 L30 50 M15 20 L45 40 M45 20 L15 40" stroke="#ffc800" stroke-width="1"/></svg>',
    "ScarecrowPhish": '<svg viewBox="0 0 60 60"><circle cx="30" cy="20" r="8" fill="none" stroke="#ff8c30" stroke-width="2"/><path d="M30 28 L30 50 M20 35 L40 35 M25 42 L35 42" stroke="#ff8c30" stroke-width="2" fill="none"/></svg>',
    "WarWorld": '<svg viewBox="0 0 60 60"><path d="M30 5 L55 20 L55 40 L30 55 L5 40 L5 20 Z" fill="none" stroke="#ff4628" stroke-width="2"/><path d="M15 20 L45 40 M45 20 L15 40" stroke="#ff4628"/><circle cx="30" cy="30" r="6" fill="#ff4628"/></svg>',
    "LeagueOfShadows": '<svg viewBox="0 0 60 60"><path d="M10 10 L50 50 M50 10 L10 50" stroke="#c9a600" stroke-width="2"/><circle cx="30" cy="30" r="10" fill="none" stroke="#c9a600"/></svg>',
    "KryptoniteSuite": '<svg viewBox="0 0 60 60"><path d="M30 10 L40 30 L30 50 L20 30 Z" fill="#39ff14" opacity=".5"/><path d="M30 10 L40 30 L30 50 L20 30 Z" fill="none" stroke="#39ff14" stroke-width="2"/></svg>',
    "WOPR": '<svg viewBox="0 0 60 60"><path d="M15 15 L45 15 L45 45 L15 45 Z" fill="none" stroke="#7fff00" stroke-width="2"/><path d="M15 25 L45 25 M15 35 L45 35" stroke="#7fff00"/><path d="M25 15 L25 45 M35 15 L35 45" stroke="#7fff00"/></svg>',
    "TheCalculator": '<svg viewBox="0 0 60 60"><rect x="15" y="10" width="30" height="40" rx="3" fill="none" stroke="#00c8ff" stroke-width="2"/><path d="M20 20 L40 20 M20 30 L40 30 M20 40 L40 40" stroke="#00c8ff"/></svg>',
    "RavenEvasion": '<svg viewBox="0 0 60 60"><path d="M30 10 Q45 25 30 40 Q15 55 30 40 Q45 25 30 10Z" fill="none" stroke="#8899ff" stroke-width="2"/><circle cx="30" cy="30" r="20" fill="none" stroke="#8899ff" stroke-dasharray="3 3"/></svg>',
    "TheThinker": '<svg viewBox="0 0 60 60"><circle cx="30" cy="20" r="12" fill="none" stroke="#9b30ff" stroke-width="2"/><path d="M30 32 L30 50 M20 40 L40 40" stroke="#9b30ff" stroke-width="2" fill="none"/></svg>',
    "JokerCard": '<svg viewBox="0 0 60 60"><rect x="15" y="10" width="30" height="40" rx="5" fill="none" stroke="#ff6a00" stroke-width="2"/><text x="30" y="35" text-anchor="middle" fill="#ff6a00" font-size="16">J</text></svg>',
    "DailyPlanet": '<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="20" fill="none" stroke="#64a0ff" stroke-width="2"/><path d="M10 30 L50 30 M30 10 Q20 30 30 50 M30 10 Q40 30 30 50" stroke="#64a0ff" fill="none"/></svg>',
}

def parse_md():
    raw = open(MD, encoding="utf-8").read()
    sections = re.split(r'(?=## KIT \d+)', raw)
    kits = []
    for sec in sections:
        if not sec.startswith("## KIT"): continue
        hm = re.match(r'## KIT (\d+) — ([^(\n]+)', sec)
        if not hm: continue
        num = hm.group(1)
        name = hm.group(2).strip()
        kit_id = ""
        for k in DC_COLORS:
            if k.lower() in name.lower(): kit_id = k; break
        if not kit_id:
            for k, ic in DC_ICONS.items():
                if ic in sec[:300]: kit_id = k; break
        if not kit_id: kit_id = re.sub(r'[^a-zA-Z]', '', name)
        color = DC_COLORS.get(kit_id, "#ffd60a")
        icon = DC_ICONS.get(kit_id, "⭐")
        svg = SVGS.get(kit_id, f'<svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="25" fill="none" stroke="{color}" stroke-width="2"/></svg>')
        cm = re.search(r'```\n(cd ~/Desktop/tool_DC/[^\n]+)\n```', sec)
        cmd = cm.group(1).strip() if cm else f"cd ~/Desktop/tool_DC/{kit_id}"
        tools = []
        for line in sec.splitlines():
            m = re.match(r'\|\s*(\d+|\'?\w+\'?)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', line)
            if m:
                n = m.group(1).strip()
                nm = m.group(2).strip()
                th = m.group(3).strip()
                ds = m.group(4).strip()
                if nm and nm not in ("Tool", "Name", "Commande", "Module", "Tool | Thème"):
                    tools.append({"num": n, "name": nm, "theme": th, "desc": ds})
        if not tools:
            for line in sec.splitlines():
                m = re.match(r'\|\s*(\d+|\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', line)
                if m and m.group(2).strip() not in ("Tool", "Name", "Commande", "Thème", ""):
                    tools.append({"num": m.group(1), "name": m.group(2).strip(),
                                  "theme": m.group(3).strip(), "desc": ""})
        kits.append({"num": num, "name": name, "id": kit_id,
                     "color": color, "icon": icon, "svg": svg, "cmd": cmd, "tools": tools})
    return kits

def tool_page(kit, tool):
    color = kit["color"]; icon = kit["icon"]; svg = kit["svg"]
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{html_mod.escape(kit['name'])} — {html_mod.escape(tool['name'])}</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#050505;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:30px 40px 20px;
border-bottom:3px solid {color};display:flex;align-items:center;gap:20px;position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;
background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);animation:scan 3s infinite}}
@keyframes scan{{to{{left:100%}}}}
.icon svg{{width:60px;height:60px;filter:drop-shadow(0 0 20px {color}66)}}
h1{{font-family:'Orbitron',sans-serif;font-size:1.4em;color:{color}}}
h1 small{{color:#555;font-size:.5em;display:block}}
.gh{{margin-left:auto}}
.gh a{{background:{color};color:#000;padding:8px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:.85em}}
main{{max-width:850px;margin:30px auto;padding:0 20px}}
.card{{background:#0d0d0d;border:1px solid #1a1a2a;border-left:4px solid {color};border-radius:10px;
padding:22px;margin-bottom:16px}}
.card h2{{color:{color};font-size:1.05em;margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.card h2::before{{content:'';width:5px;height:5px;background:{color};border-radius:50%}}
.card p{{color:#99a;font-size:.9em;line-height:1.6}}
.code{{background:#000;border:1px solid {color}33;border-radius:8px;padding:14px 18px;
font-size:.85em;color:#7fff7f;margin:10px 0;overflow-x:auto;white-space:pre-wrap}}
.theme-tag{{background:{color}22;color:{color};padding:3px 14px;border-radius:12px;font-size:.82em;display:inline-block}}
.back{{color:{color};text-decoration:none;font-size:.85em;margin-bottom:16px;display:inline-block;margin-right:16px}}
.features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:14px 0}}
.feature{{background:#111;border-radius:8px;padding:12px 16px;font-size:.85em}}
.feature b{{color:{color}}}
.demo{{background:#000;border-radius:8px;padding:30px;margin:14px 0;text-align:center;
border:1px solid {color}22;min-height:100px;display:grid;place-items:center}}
.demo .icon svg{{width:80px;height:80px;filter:drop-shadow(0 0 30px {color}44)}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px}}
</style></head><body>
<header>
  <div class="icon">{svg}</div>
  <div><h1>{html_mod.escape(tool['name'])}<small>{html_mod.escape(kit['name'])} · {html_mod.escape(tool['theme'])}</small></h1></div>
  <div class="gh"><a href="{GITHUB_BASE}" target="_blank">⬇ GitHub ↗</a></div>
</header>
<main>
  <a class="back" href="../index.html">← Gotham City</a>
  <a class="back" href="index_{re.sub(r'[^w]','_',kit['name'].replace(' ','_'))}.html">← {kit['name']}</a>
  <div class="card"><h2>📝 DESCRIPTION</h2><p>{html_mod.escape(tool['desc'])}</p></div>
  <div class="card"><h2>⚙️ LANCEMENT</h2>
    <div class="code">{html_mod.escape(kit['cmd'])}</div>
    <p>Tape <b style="color:{color}">{tool['num']}</b> dans le menu du kit pour lancer ce tool.</p>
  </div>
  <div class="card"><h2>🏷️ INFORMATIONS</h2>
    <div class="features">
      <div class="feature"><b>Thème</b><br>{html_mod.escape(tool['theme'])}</div>
      <div class="feature"><b>Kit</b><br>{html_mod.escape(kit['name'])}</div>
      <div class="feature"><b>Numéro</b><br>{tool['num']}</div>
      <div class="feature"><b>GitHub</b><br><a href="{GITHUB_BASE}" style="color:{color}">{GITHUB_BASE.replace('https://','')}</a></div>
    </div>
  </div>
  <div class="card"><h2>🎬 DÉMONSTRATION</h2>
    <div class="demo"><div class="icon">{svg}</div>
    <p style="color:#666;font-size:.85em;margin-top:10px">
      Lance le tool dans le terminal pour la démonstration animée complète<br>
      Les animations fullscreen sont générées par dc_fullscreen.py
    </p></div>
  </div>
</main>
<footer>{kit['name']} · {tool['name']} · powered by Maxime Leal</footer>
</body></html>"""

def kit_index(kit):
    color = kit["color"]; icon = kit["icon"]; svg = kit["svg"]
    tools_html = ""
    for t in kit["tools"]:
        safe = re.sub(r'[^\w\-]', '_', f"{t['num']}_{t['name']}")[:80]
        tools_html += f"""<a class="tool-card" href="{safe}.html" style="border-left-color:{color}">
          <div style="font-size:1.8em">{icon}</div>
          <div style="flex:1"><b style="color:{color}">{html_mod.escape(t['name'])}</b>
          <span style="color:#6495ff;font-size:.78em;display:block">{html_mod.escape(t['theme'])}</span>
          <p style="color:#777;font-size:.82em;margin:4px 0 0">{html_mod.escape(t['desc'][:70])}</p></div>
          <span style="margin-left:auto;color:{color};font-size:1.3em">→</span></a>"""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{html_mod.escape(kit['name'])} — Tous les Tools</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#050505;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:40px;text-align:center;
border-bottom:3px solid {color};position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;inset:0;
background:radial-gradient(ellipse at 50% 0%,{color}11,transparent 60%)}}
.icon svg{{width:80px;height:80px;filter:drop-shadow(0 0 30px {color}44)}}
h1{{font-size:2em;color:{color};letter-spacing:3px}}
main{{max-width:800px;margin:30px auto;padding:0 20px}}
.tool-card{{display:flex;gap:16px;align-items:center;background:#0d0d0d;
border:1px solid #1a1a2a;border-left:4px solid {color};border-radius:10px;
padding:18px 20px;margin-bottom:12px;text-decoration:none;transition:all .2s;color:#ccc}}
.tool-card:hover{{background:#1a1a1a;transform:translateX(6px)}}
.back{{color:{color};text-decoration:none;font-size:.9em;display:block;margin-bottom:20px}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px}}
</style></head><body>
<header><div class="icon">{svg}</div><h1>{html_mod.escape(kit['name'])}</h1></header>
<main>
  <a class="back" href="../index.html">← Gotham City</a>
  <div style="text-align:center;margin:20px 0">
    <a href="{GITHUB_BASE}" target="_blank" style="background:{color};color:#000;padding:10px 30px;border-radius:8px;text-decoration:none;font-weight:bold">⬇ Dépôt GitHub</a>
  </div>
  {tools_html}
</main>
<footer>{html_mod.escape(kit['name'])} · powered by Maxime Leal</footer>
</body></html>"""

def main_index(kits):
    cards = ""
    for kit in kits:
        fname = f"{kit['id']}/index_{re.sub(r'[^w]','_',kit['name'].replace(' ','_'))}.html"
        cards += f"""<a href="{fname}" style="border-color:{kit['color']}44;text-decoration:none;
          display:flex;flex-direction:column;gap:8px;align-items:center;background:#0a0a14;
          border:1px solid #1a1a2a;border-radius:12px;padding:20px;transition:all .2s">
          <div style="width:60px;height:60px">{kit['svg']}</div>
          <div><b style="color:{kit['color']}">{kit['name']}</b>
          <span style="color:#555;font-size:.78em;display:block">{len(kit['tools'])} tools</span></div>
        </a>"""
    total = sum(len(k["tools"]) for k in kits)
    return f"""<!doctype html><html><head><meta charset=utf8><title>GOTHAM CITY — Arsenal DC</title>
<style>body{{background:#000;color:#ccc;font-family:monospace;padding:40px;text-align:center}}
h1{{color:#ffd60a;font-size:2.5em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;max-width:1300px;margin:30px auto}}
a:hover{{transform:translateY(-6px)}}
footer{{color:#333;padding:30px;letter-spacing:2px;font-size:.75em}}</style></head><body>
<h1 style="color:#ffd60a;font-size:2.5em">GOTHAM CITY</h1>
<p style="color:#555;letter-spacing:6px">L'ARSENAL DC · POWERED BY MAXIME LEAL</p>
<div class="grid">{cards}</div>
<footer>{len(kits)} KITS · {total} TOOLS · ARSENAL DC COMPLET</footer>
</body></html>"""

def generate():
    kits = parse_md()
    tp = tt = 0
    for kit in kits:
        kd = os.path.join(OUT, kit["id"])
        os.makedirs(kd, exist_ok=True)
        kf = re.sub(r'[^w]', '_', kit["name"].replace(" ", "_")) + ".html"
        open(os.path.join(kd, f"index_{kf}"), "w", encoding="utf-8").write(kit_index(kit))
        tp += 1
        for t in kit["tools"]:
            safe = re.sub(r'[^\w\-]', '_', f"{t['num']}_{t['name']}")[:80]
            fp = os.path.join(kd, f"{safe}.html")
            open(fp, "w", encoding="utf-8").write(tool_page(kit, t))
            tp += 1
        tt += len(kit["tools"])
    open(os.path.join(OUT, "index.html"), "w").write(main_index(kits))
    tp += 1
    print(f"[OK] {tp} pages web générées dans {OUT}")
    print(f"     {len(kits)} kits · {tt} tools documentés · SVG de chaque personnage")
    print(f"     GitHub : {GITHUB_BASE}")
    print(f"     index : {OUT}/index.html")

if __name__ == "__main__":
    generate()
