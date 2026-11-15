#!/usr/bin/env python3
# language: Python 3, file: generate_all_pages.py v2, target: macOS
# Génère les pages web pour TOUS les tools de TOUS les kits
# Parse directement liste_tool.md (qui contient déjà tout) — pas besoin de redéfinir les données
# Usage: python3 generate_all_pages.py [github_username]
import os, sys, re, json, html as html_mod

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
GITHUB_USER = sys.argv[1] if len(sys.argv) > 1 else "MaximeLeal"
GITHUB_BASE = f"https://github.com/{GITHUB_USER}/tool_DC"
OUT = os.path.join(ROOT, "arsenal_web_pages")
os.makedirs(OUT, exist_ok=True)

MD_FILE = os.path.join(ROOT, "liste_tool.md")
if not os.path.exists(MD_FILE):
    print("[X] liste_tool.md introuvable"); sys.exit(1)

raw_md = open(MD_FILE, encoding="utf-8").read()

# ─── parse les kits et tools depuis le markdown ───
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

def parse_md():
    sections = re.split(r'(?=## KIT \d+)', raw_md)
    kits = []
    for sec in sections:
        if not sec.startswith("## KIT"): continue
        header = re.match(r'## KIT (\d+) — ([^(\n]+)', sec)
        if not header: continue
        kit_num = header.group(1)
        kit_name = header.group(2).strip()
        # trouve le kit_id par matching des noms connus
        kit_id = ""
        for k in DC_COLORS:
            if k.lower() in kit_name.lower(): kit_id = k; break
        if not kit_id:
            for k, ic in DC_ICONS.items():
                if ic in sec[:300]: kit_id = k; break
        if not kit_id: kit_id = kit_name.replace(" ", "")
        color = DC_COLORS.get(kit_id, "#ffd60a")
        icon = DC_ICONS.get(kit_id, "⭐")

        # extrait la commande
        cmd_match = re.search(r'```\n(cd ~/Desktop/tool_DC/[^\n]+)\n```', sec)
        cmd = cmd_match.group(1).strip() if cmd_match else f"cd ~/Desktop/tool_DC/{kit_id}"

        # extrait les tools depuis les tableaux pipe
        tools = []
        for line in sec.splitlines():
            m = re.match(r'\|\s*(\d+|\'?\w+\'?)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', line)
            if m:
                num = m.group(1).strip()
                name = m.group(2).strip()
                theme = m.group(3).strip()
                desc = m.group(4).strip()
                if name and name not in ("Tool", "Name", "Commande", "Module"):
                    tools.append({"num": num, "name": name, "theme": theme, "desc": desc})

        # fallback : lignes simples "| # | Tool | Thème |"
        if not tools:
            for line in sec.splitlines():
                m = re.match(r'\|\s*(\d+|\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*$', line)
                if m and m.group(2).strip() not in ("Tool", "Name", "Commande", "Thème"):
                    tools.append({"num": m.group(1).strip(), "name": m.group(2).strip(),
                                  "theme": m.group(3).strip(), "desc": ""})

        # fallback 2 : lignes non-table comme "1 TOOL_NAME | theme | desc"
        if not tools:
            for line in sec.splitlines():
                m = re.match(r'\|\s*(\d+)\s*\|\s*(\S[\S ]+)\s*\|', line)
                if m and m.group(2).strip() not in ("Tool", "Name"):
                    tools.append({"num": m.group(1), "name": m.group(2).strip(),
                                  "theme": "", "desc": ""})

        kits.append({"num": kit_num, "name": kit_name, "id": kit_id,
                     "color": color, "icon": icon, "cmd": cmd, "tools": tools})
    return kits

# ─── génération des pages ───
def tool_page(kit, tool):
    color = kit["color"]
    icon = kit["icon"]
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{kit['name']} — {tool['name']}</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#050505;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:30px 40px 20px;
border-bottom:3px solid {color};display:flex;align-items:center;gap:20px;position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;
background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);animation:scan 3s infinite}}
@keyframes scan{{to{{left:100%}}}}
.icon{{font-size:3em;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.1)}}}}
h1{{font-family:'Orbitron',sans-serif;font-size:1.6em;color:{color};margin:0}}
h1 small{{color:#555;font-size:.5em;display:block;margin-top:2px}}
.github{{margin-left:auto}}
.github a{{background:{color};color:#000;padding:8px 20px;border-radius:6px;
text-decoration:none;font-weight:bold;font-size:.85em}}
main{{max-width:900px;margin:30px auto;padding:0 20px}}
.card{{background:#0d0d0d;border:1px solid {color}22;border-radius:10px;padding:24px;
margin-bottom:18px;border-left:4px solid {color}}}
.card h2{{color:{color};font-size:1.1em;margin-bottom:12px}}
.card p{{color:#99a;font-size:.9em;line-height:1.6}}
.code{{background:#000;border:1px solid {color}33;border-radius:8px;padding:14px 18px;
font-size:.85em;color:#7fff7f;margin:10px 0;overflow-x:auto;white-space:pre-wrap}}
.theme-tag{{background:{color}22;color:{color};padding:3px 14px;border-radius:12px;font-size:.8em;display:inline-block}}
.back{{color:{color};text-decoration:none;font-size:.85em;margin-bottom:16px;display:inline-block}}
.features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:14px 0}}
.feature{{background:#111;border-radius:8px;padding:12px 16px;font-size:.85em}}
.feature b{{color:{color}}}
.demo{{background:#000;border-radius:8px;padding:30px;margin:14px 0;text-align:center;
border:1px solid {color}22}}
.demo .icon{{font-size:4em;animation:pulse 3s infinite}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px}}
</style></head><body>
<header>
  <div class="icon">{icon}</div>
  <div><h1>{tool['name']}<small>{kit['name']} · {tool['theme']}</small></h1></div>
  <div class="github"><a href="{GITHUB_BASE}" target="_blank">⬇ GitHub ↗</a></div>
</header>
<main>
  <a class="back" href="../index.html">← Gotham City</a>
  <a class="back" href="index_{kit['name'].replace(' ','_')}.html" style="margin-left:16px">← {kit['name']}</a>
  <div class="card"><h2>📝 DESCRIPTION</h2><p>{html_mod.escape(tool['desc'])}</p></div>
  <div class="card"><h2>⚙️ LANCEMENT</h2>
    <div class="code">{html_mod.escape(kit['cmd'])}</div>
    <p style="margin-top:8px">Tape le numéro <b style="color:{color}">{tool['num']}</b> dans le menu du kit pour lancer ce tool.</p>
  </div>
  <div class="card"><h2>🏷️ INFORMATIONS</h2>
    <div class="features">
      <div class="feature"><b style="color:{color}">Thème</b><br>{html_mod.escape(tool['theme'])}</div>
      <div class="feature"><b style="color:{color}">Kit</b><br>{html_mod.escape(kit['name'])}</div>
      <div class="feature"><b style="color:{color}">Numéro</b><br>{tool['num']}</div>
      <div class="feature"><b style="color:{color}">Source</b><br>{html_mod.escape(GITHUB_BASE)}</div>
    </div>
  </div>
  <div class="card"><h2>🎬 DÉMONSTRATION</h2>
    <div class="demo">
      <div class="icon">{icon}</div>
      <p style="color:#666;font-size:.85em;margin-top:12px">
        Lance le tool dans le terminal pour voir la démonstration animée complète.<br>
        Les animations fullscreen sont générées en temps réel par dc_fullscreen.py.
      </p>
    </div>
  </div>
</main>
<footer>{kit['name']} · {tool['name']} · powered by Maxime Leal</footer>
</body></html>"""

def kit_index(kit):
    color = kit["color"]; icon = kit["icon"]
    tools_html = ""
    for t in kit["tools"]:
        safe_name = re.sub(r'[^\w\-]', '_', f"{t['num']}_{t['name']}")[:80]
        fname = f"{safe_name}.html"
        tools_html += f"""<a class="tool-card" href="{fname}" style="border-left-color:{color}">
          <div style="font-size:1.8em">{icon}</div>
          <div><b style="color:{color}">{html_mod.escape(t['name'])}</b>
          <span style="color:#6495ff;font-size:.78em;display:block">{html_mod.escape(t['theme'])}</span>
          <p style="color:#777;font-size:.82em;margin:4px 0 0">{html_mod.escape(t['desc'][:70])}</p></div>
          <span style="margin-left:auto;color:{color};font-size:1.3em">→</span></a>"""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{kit['name']} — Tous les Tools</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#050505;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:40px;text-align:center;
border-bottom:3px solid {color};position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;inset:0;
background:radial-gradient(ellipse at 50% 0%,{color}11,transparent 60%)}}
.icon{{font-size:4em;margin-bottom:10px}}
h1{{font-size:2em;color:{color};letter-spacing:3px}}
main{{max-width:800px;margin:30px auto;padding:0 20px}}
.tool-card{{display:flex;gap:16px;align-items:center;background:#0d0d0d;
border:1px solid #1a1a2a;border-left:4px solid {color};border-radius:10px;
padding:18px 20px;margin-bottom:12px;text-decoration:none;transition:all .2s}}
.tool-card:hover{{background:#1a1a1a;transform:translateX(6px)}}
.back{{color:{color};text-decoration:none;font-size:.9em;display:block;margin-bottom:20px}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px}}
</style></head><body>
<header><div class="icon">{icon}</div><h1>{kit['name']}</h1></header>
<main>
  <a class="back" href="../index.html">← Gotham City</a>
  <div class="github-link" style="text-align:center;margin:20px 0">
    <a href="{GITHUB_BASE}" target="_blank" style="background:{color};color:#000;padding:10px 30px;border-radius:8px;text-decoration:none;font-weight:bold">⬇ Dépôt GitHub</a>
  </div>
  {tools_html}
</main>
<footer>{kit['name']} · powered by Maxime Leal</footer>
</body></html>"""

def main_index(kits):
    cards = ""
    for kit in kits:
        fname = f"{kit['id']}/index_{kit['name'].replace(' ','_')}.html"
        cards += f"""<a href="{fname}" style="border-color:{kit['color']}44;text-decoration:none;
          display:flex;flex-direction:column;gap:8px;align-items:center;background:#0a0a14;
          border:1px solid #1a1a2a;border-radius:12px;padding:20px;transition:all .2s">
          <div style="font-size:2.5em">{kit['icon']}</div>
          <div><b style="color:{kit['color']}">{kit['name']}</b>
          <span style="color:#555;font-size:.78em;display:block">{len(kit['tools'])} tools</span></div>
        </a>"""
    total_tools = sum(len(k["tools"]) for k in kits)
    return f"""<!doctype html><html><head><meta charset=utf8><title>GOTHAM CITY — Arsenal DC</title>
<style>body{{background:#000;color:#ccc;font-family:monospace;padding:40px;text-align:center}}
h1{{color:#ffd60a;font-size:2.5em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;max-width:1200px;margin:30px auto}}
footer{{color:#333;padding:30px;letter-spacing:2px;font-size:.75em}}</style></head><body>
<h1>GOTHAM CITY</h1><p style="color:#555">L'ARSENAL DC · POWERED BY MAXIME LEAL</p>
<div class="grid">{cards}</div>
<footer>{len(kits)} KITS · {total_tools} TOOLS · ARSENAL DC COMPLET</footer>
</body></html>"""

def generate():
    kits = parse_md()
    total_pages = 0
    total_tools = 0
    for kit in kits:
        kit_dir = os.path.join(OUT, re.sub(r'[^\w\-]', '_', kit["id"]).strip("_"))
        os.makedirs(kit_dir, exist_ok=True)
        # index du kit
        kit_fname = re.sub(r'[^\w\-]', '_', kit["name"]) + ".html"
        open(os.path.join(kit_dir, f"index_{kit_fname}"), "w").write(kit_index(kit))
        total_pages += 1
        # une page par tool
        for t in kit["tools"]:
            safe_name = re.sub(r'[^\w\-]', '_', f"{t['num']}_{t['name']}")[:80]
            fname = os.path.join(kit_dir, f"{safe_name}.html")
            open(fname, "w", encoding="utf-8").write(tool_page(kit, t))
            total_pages += 1
        total_tools += len(kit["tools"])
    # index global
    open(os.path.join(OUT, "index.html"), "w").write(main_index(kits))
    total_pages += 1
    print(f"[OK] {total_pages} pages web générées dans {OUT}")
    print(f"     {len(kits)} kits · {total_tools} tools documentés")
    print(f"     index : {OUT}/index.html")

if __name__ == "__main__":
    generate()
