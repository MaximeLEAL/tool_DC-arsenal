#!/usr/bin/env python3
# language: Python 3, file: render_md.py, target: macOS
# Rend liste_tool.md en page HTML full design DC (pas du texte brut)
import http.server, os, sys, re, json

ROOT = os.path.dirname(os.path.abspath(__file__))
MD = os.path.join(ROOT, "liste_tool.md")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8097

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
ICONS = {
    "RickPortal": "🟢", "FlashToolSuper": "⚡", "BatCave": "🦇", "JokerChaos": "🃏",
    "TridentAquaman": "🔱", "SupermanVision": "🦸", "ConstantineDark": "🕯️",
    "LassoVerite": "🪢", "CyborgTech": "🤖", "LexCorpIndustries": "🏢",
    "STARLabs": "🔬", "TaskForceX": "🎯", "NeoMatrix": "💊", "ForceGalaxy": "🌟",
    "CatwomanVoleuse": "🐱", "HiveMining": "🍯", "ScarecrowPhish": "🎃",
    "WarWorld": "⚔️", "LeagueOfShadows": "🥷", "KryptoniteSuite": "🟩",
    "WOPR": "🎮", "TheCalculator": "📊", "RavenEvasion": "🐦‍⬛",
    "TheThinker": "🧠", "JokerCard": "🂡", "DailyPlanet": "📰",
}

def parse_md():
    if not os.path.exists(MD): return []
    raw = open(MD, encoding="utf-8").read()
    sections = re.split(r'(?=## KIT \d+)', raw)
    out = []
    for sec in sections:
        if not sec.startswith("## KIT"): continue
        header = re.match(r'## KIT (\d+) — ([^(]+)\(([^)]+)\)', sec)
        if not header: continue
        kit_num = header.group(1)
        kit_name = header.group(2).strip()
        kit_desc = header.group(3).strip().rstrip("—").strip()
        cmd_match = re.search(r'```\n(.*?)\n```', sec, re.S)
        cmd = cmd_match.group(1).strip() if cmd_match else ""
        rows = re.findall(r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', sec)
        tools = [{"num": r[0], "name": r[1].strip(), "theme": r[2].strip(), "desc": r[3].strip()} for r in rows]
        # aussi les lignes simples sans numéro (tableaux texte)
        simple = re.findall(r'\|\s*(\d+)\s*\|\s*(\w[\w\s]+?)\s*\|\s*(\w[\w\s]*?)\s*\|', sec)
        if simple and not tools:
            tools = [{"num": s[0], "name": s[1].strip(), "theme": s[2].strip(), "desc": ""} for s in simple]
        # détermine le kit ID depuis le nom
        kit_id = ""
        for k in DC_COLORS:
            if k.lower() in kit_name.lower() or k.lower() in sec.lower()[:200]:
                kit_id = k; break
        if not kit_id:
            for k, ic in ICONS.items():
                if ic in sec[:300]: kit_id = k; break
        out.append({"num": kit_num, "name": kit_name, "desc": kit_desc,
                    "cmd": cmd, "tools": tools, "id": kit_id or kit_name.replace(" ", "")})
    return out

def build_html():
    data = parse_md()
    total_tools = sum(len(d["tools"]) for d in data)
    kits_html = ""
    for d in data:
        color = DC_COLORS.get(d["id"], "#ffd60a")
        icon = ICONS.get(d["id"], "⭐")
        tools_html = ""
        for t in d["tools"]:
            tools_html += f"""<div class="tool" data-q="{t['name']} {t['theme']} {t['desc']}".toLowerCase()>
              <span class="tnum">{t['num']}</span>
              <span class="tname">{t['name']}</span>
              <span class="ttheme">{t['theme']}</span>
              <span class="tdesc">{t['desc']}</span>
            </div>"""
        if not tools_html:
            # fallback : extrait les lignes simples du bloc
            lines = re.findall(r'^\s+(\d+|\'?\w+?\')\s+[A-Z].*', d.get("cmd", ""), re.M)
            if d.get("cmd"):
                for line in d["cmd"].splitlines():
                    m = re.match(r'^\s*\|?\s*(\d+)\s+\|?\s*(\w[\w\s]+)\s*\|?\s*(\w+)?\s*\|?\s*(.*)', line)
                    if m:
                        tools_html += f"""<div class="tool">
                          <span class="tnum">{m.group(1)}</span>
                          <span class="tname">{m.group(2)}</span>
                          <span class="ttheme">{m.group(3) or ''}</span>
                          <span class="tdesc">{m.group(4) or ''}</span></div>"""
        kits_html += f"""
        <div class="kit" id="kit{d['num']}" style="--c:{color}">
          <div class="kit-header">
            <span class="kit-icon">{icon}</span>
            <div>
              <span class="kit-name">{d['name']}</span>
              <span class="kit-desc">{d['desc']}</span>
            </div>
            <span class="kit-count">{len(d['tools'])} tools</span>
          </div>
          <div class="kit-cmd"><code>{d['cmd']}</code></div>
          <div class="kit-tools">{tools_html}</div>
        </div>"""

    html = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>L'ARSENAL DC — {len(data)} KITS · {total_tools} TOOLS</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
*{{box-sizing:border-box;margin:0}}
body{{background:#020208;color:#ccc;font-family:monospace;min-height:100vh}}
.hero{{background:linear-gradient(180deg,#000,#0a0a14);text-align:center;padding:60px 20px 30px;
border-bottom:3px solid #ffd60a;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;
background:radial-gradient(ellipse at 50% 20%,rgba(255,214,10,.08),transparent 70%);animation:flicker 5s infinite}}
@keyframes flicker{{0%,100%{{opacity:1}}97%{{opacity:1}}98%{{opacity:.5}}99%{{opacity:1}}}}
.hero h1{{font-family:'Orbitron',monospace;font-size:3.2em;color:#ffd60a;letter-spacing:4px;
text-shadow:0 0 30px rgba(255,214,10,.4)}}
.hero h1 b{{color:#ff4628}}
.hero .sub{{color:#666;font-size:.9em;letter-spacing:6px;margin-top:8px}}
.hero .stats{{display:flex;gap:12px;justify-content:center;margin-top:16px;flex-wrap:wrap}}
.hero .stat{{background:#0a0a14;border:1px solid #2a2a3a;padding:8px 20px;border-radius:8px}}
.hero .stat b{{color:#ffd60a;font-size:1.3em}}
.search-bar{{text-align:center;padding:16px;position:sticky;top:0;z-index:100;
background:#020208ee;backdrop-filter:blur(8px);border-bottom:1px solid #1a1a2a}}
.search-bar input{{background:#0a0a14;border:1px solid #333;color:#ddd;padding:12px 24px;
border-radius:24px;width:min(500px,90%);font-size:1em;font-family:monospace}}
#container{{max-width:1200px;margin:0 auto;padding:20px}}
.kit{{background:#0a0a14;border:1px solid #1a1a2a;border-radius:12px;margin:16px 0;
border-left:4px solid var(--c);overflow:hidden}}
.kit-header{{display:flex;align-items:center;gap:12px;padding:16px 20px;
background:linear-gradient(90deg,{chr(34)}var(--c)11{chr(34)},transparent);cursor:pointer}}
.kit-header:hover{{background:rgba(255,255,255,.03)}}
.kit-icon{{font-size:2em}}
.kit-name{{font-family:'Orbitron',monospace;font-size:1.15em;color:var(--c);font-weight:700}}
.kit-desc{{display:block;color:#666;font-size:.8em;margin-top:2px}}
.kit-count{{margin-left:auto;background:var(--c);color:#000;border-radius:12px;
padding:3px 12px;font-size:.8em;font-weight:bold}}
.kit-cmd{{padding:8px 20px;background:#000;border-top:1px solid #111}}
.kit-cmd code{{color:#39ff14;font-size:.82em;background:none}}
.kit-tools{{padding:8px 20px 16px}}
.tool{{display:grid;grid-template-columns:36px 1fr 140px 1fr;gap:12px;padding:7px 10px;
border-bottom:1px solid #111;border-radius:4px;align-items:center}}
.tool:hover{{background:#0d0d1a;border-bottom-color:#222}}
.tnum{{color:var(--c);font-weight:bold;text-align:center}}
.tname{{color:#e7e9ea;font-weight:600;font-size:.92em}}
.ttheme{{color:#6495ff;font-size:.82em}}
.tdesc{{color:#777;font-size:.82em}}
@media(max-width:700px){{.tool{{grid-template-columns:36px 1fr}}.ttheme,.tdesc{{display:none}}}}
</style></head><body>
<div class="hero">
  <h1>L'ARSENAL <b>DC</b></h1>
  <div class="sub">{len(data)} KITS · {total_tools} TOOLS · POWERED BY MAXIME LEAL</div>
  <div class="stats">
    <div class="stat"><b>{len(data)}</b><span>KITS</span></div>
    <div class="stat"><b>{total_tools}</b><span>TOOLS</span></div>
    <div class="stat"><b>16</b><span>PERSONNAGES DC</span></div>
    <div class="stat"><b>~240</b><span>COMMANDS</span></div>
  </div>
</div>
<div class="search-bar">
  <input id="q" placeholder="🔍 rechercher un tool, un thème, une arme…" autocomplete="off">
</div>
<div id="container">{kits_html}</div>
<script>
document.getElementById('q').addEventListener('input', function() {{
  const q = this.value.toLowerCase();
  document.querySelectorAll('.kit').forEach(function(kit) {{
    let visible = false;
    kit.querySelectorAll('.tool').forEach(function(tool) {{
      const match = tool.dataset.q.includes(q);
      tool.style.display = match ? '' : 'none';
      if (match) visible = true;
    }});
    kit.style.display = visible || !q ? '' : 'none';
  }});
}});
document.querySelectorAll('.kit-header').forEach(function(h) {{
  h.onclick = function() {{
    const tools = h.parentElement.querySelector('.kit-tools');
    const cmd = h.parentElement.querySelector('.kit-cmd');
    const open = tools.style.display !== 'none';
    tools.style.display = open ? 'none' : '';
    cmd.style.display = open ? 'none' : '';
  }};
}});
</script></body></html>"""
    return html

if __name__ == "__main__":
    out = os.path.join(ROOT, "arsenal_dc.html")
    open(out, "w", encoding="utf-8").write(build_html())
    print(f"[OK] {out} — {os.path.getsize(out)//1024} Ko")
    import webbrowser; webbrowser.open(f"file://{out}")
