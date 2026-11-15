#!/usr/bin/env python3
# language: Python 3, file: dc_web_engine.py, target: macOS
# DC WEB ENGINE — le générateur de pages web pour chaque tool de l'arsenal
# Génère une page web par tool : design DC, animation, description, usage, dépôt GitHub
# Usage: python3 dc_web_engine.py  →  génère tool_DC/arsenal_web_pages/ (26 kits × N tools)
import os, sys, json, time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "arsenal_web_pages")
os.makedirs(OUT, exist_ok=True)

GITHUB_BASE = "https://github.com/MaximeLeal/tool_DC"

# ─── les données de tous les tools de tous les kits ───
# format : {kit_id: {"name","color","icon","char","desc","github_path","tools": [{"num","name","theme","desc","usage","cmd"}]}}
ARSENAL = json.load(open(os.path.join(ROOT, "arsenal_data.py".replace(".py", "_data.py")))) if os.path.exists(os.path.join(ROOT, "arsenal_data.py")) else {}

def tool_page(kit_name, kit_color, kit_icon, tool_name, tool_theme, tool_desc, tool_usage, tool_cmd, github_url):
    color_dark = "#0a0a0a"
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{kit_name} — {tool_name}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
*{{box-sizing:border-box;margin:0}}
body{{background:{color_dark};color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:30px 40px 20px;border-bottom:3px solid {kit_color};
display:flex;align-items:center;gap:20px;position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;top:0;left:-100%;width:100%;height:100%;
background:linear-gradient(90deg,transparent,rgba(255,255,255,.03),transparent);animation:scan 3s infinite}}
@keyframes scan{{to{{left:100%}}}}
.icon{{font-size:3em;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.1)}}}}
h1{{font-family:'Orbitron',monospace;font-size:1.6em;color:{kit_color};margin:0}}
h1 small{{color:#555;font-size:.5em;display:block;margin-top:2px}}
.github{{margin-left:auto}}
.github a{{background:{kit_color};color:#000;padding:8px 20px;border-radius:6px;
text-decoration:none;font-weight:bold;font-size:.85em}}
.github a:hover{{background:#fff;transform:scale(1.05)}}
main{{max-width:900px;margin:30px auto;padding:0 20px}}
.card{{background:#0d0d0d;border:1px solid {kit_color}22;border-radius:10px;padding:24px;margin-bottom:18px;
border-left:4px solid {kit_color}}}
.card h2{{color:{kit_color};font-size:1.1em;margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.card h2::before{{content:'';width:5px;height:5px;background:{kit_color};border-radius:50%;animation:pulse 2s infinite}}
.card p{{color:#99a;font-size:.9em;line-height:1.6}}
.code{{background:#000;border:1px solid {kit_color}33;border-radius:8px;padding:14px 18px;
font-size:.85em;color:#7fff7f;margin:10px 0;overflow-x:auto;white-space:pre-wrap}}
.code::before{{content:'$ ';color:{kit_color}}}
.theme-tag{{background:{kit_color}22;color:{kit_color};padding:3px 14px;border-radius:12px;font-size:.8em;display:inline-block}}
.back{{color:{kit_color};text-decoration:none;font-size:.85em;margin-bottom:16px;display:inline-block}}
.back:hover{{text-decoration:underline}}
.features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:14px 0}}
.feature{{background:#111;border-radius:8px;padding:12px 16px;font-size:.85em}}
.feature b{{color:{kit_color}}}
.demo{{background:#000;border-radius:8px;padding:20px;margin:14px 0;text-align:center;
border:1px solid {kit_color}22;min-height:120px;display:grid;place-items:center}}
.demo .icon{{font-size:4em;animation:pulse 3s infinite}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px;letter-spacing:2px}}
</style></head><body>
<header>
  <div class="icon">{kit_icon}</div>
  <div>
    <h1>{tool_name}<small>{kit_name} · {tool_theme}</small></h1>
  </div>
  <div class="github"><a href="{github_url}" target="_blank">⬇ GitHub ↗</a></div>
</header>
<main>
  <a class="back" href="index_{kit_name.replace(' ','_')}.html">← retour aux tools de {kit_name}</a>

  <div class="card">
    <h2>DESCRIPTION</h2>
    <p>{tool_desc}</p>
  </div>

  <div class="card">
    <h2>USAGE</h2>
    <div class="code">{tool_cmd}</div>
    <p>{tool_usage}</p>
  </div>

  <div class="card">
    <h2>FONCTIONNEMENT</h2>
    <div class="features">
      <div class="feature"><b>Thème</b><br>{tool_theme}</div>
      <div class="feature"><b>Kit</b><br>{kit_name}</div>
      <div class="feature"><b>Langage</b><br>Python 3 / C++</div>
      <div class="feature"><b>Plateforme</b><br>macOS · Windows</div>
    </div>
  </div>

  <div class="card">
    <h2>DÉMONSTRATION VISUELLE</h2>
    <div class="demo">
      <div class="icon">{kit_icon}</div>
      <p style="color:#666;font-size:.85em;margin-top:10px">
        Lance le tool dans le terminal pour voir la démonstration animée complète.<br>
        Les animations sont générées en temps réel par le code du tool.
      </p>
    </div>
  </div>
</main>
<footer>{kit_name} · {tool_name} · powered by Maxime Leal</footer>
</body></html>"""

def kit_index(kit_name, kit_color, kit_icon, tools, github_url):
    tools_html = ""
    for t in tools:
        num, tname, theme, desc = t[0], t[1], t[2], t[3] if len(t) > 3 else ""
        fname = f"{num}_{tname.replace(' ','_').replace('/','_')}.html"
        tools_html += f"""<a class="tool-card" href="{fname}" style="border-left-color:{kit_color}">
          <div class="tool-icon">{kit_icon}</div>
          <div class="tool-info">
            <b style="color:{kit_color}">{tname}</b>
            <span class="theme">{theme}</span>
            <p>{desc[:80]}</p>
          </div>
          <span class="arrow">→</span>
        </a>"""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{kit_name} — Tous les Tools</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
*{{box-sizing:border-box;margin:0}}
body{{background:#050505;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:40px;text-align:center;
border-bottom:3px solid {kit_color};position:relative;overflow:hidden}}
header::before{{content:'';position:absolute;inset:0;
background:radial-gradient(ellipse at 50% 0%,{kit_color}11,transparent 60%)}}
.icon{{font-size:4em;margin-bottom:10px}}
h1{{font-family:'Orbitron',monospace;font-size:2em;color:{kit_color};letter-spacing:3px}}
h1 small{{color:#555;font-size:.4em;display:block;letter-spacing:6px}}
main{{max-width:800px;margin:30px auto;padding:0 20px}}
.tool-card{{display:flex;gap:16px;align-items:center;background:#0d0d0d;
border:1px solid #1a1a2a;border-left:4px solid {kit_color};border-radius:10px;
padding:18px 20px;margin-bottom:12px;text-decoration:none;transition:all .2s}}
.tool-card:hover{{background:#1a1a1a;transform:translateX(6px);border-left-width:6px}}
.tool-icon{{font-size:2.2em}}
.tool-info b{{color:{kit_color};font-size:1.05em;display:block}}
.tool-info .theme{{color:#6495ff;font-size:.78em;display:block;margin:2px 0}}
.tool-info p{{color:#777;font-size:.82em;margin:4px 0 0}}
.arrow{{margin-left:auto;color:{kit_color};font-size:1.3em}}
.back{{color:{kit_color};text-decoration:none;font-size:.9em;display:block;margin-bottom:20px}}
.github-link{{margin:20px 0;text-align:center}}
.github-link a{{background:{kit_color};color:#000;padding:10px 30px;border-radius:8px;
text-decoration:none;font-weight:bold}}
footer{{text-align:center;color:#333;font-size:.75em;padding:30px;letter-spacing:2px}}
</style></head><body>
<header>
  <div class="icon">{kit_icon}</div>
  <h1>{kit_name}<small>TOUS LES TOOLS · SELECT POUR LA FICHE DÉTAILLÉE</small></h1>
</header>
<main>
  <a class="back" href="index.html">← retour à Gotham City</a>
  <div class="github-link"><a href="{github_url}" target="_blank">⬇ Dépôt GitHub complet</a></div>
  {tools_html}
</main>
<footer>{kit_name} · powered by Maxime Leal</footer>
</body></html>"""

def main_index():
    kits_data = json.load(open(os.path.join(ROOT, "kits_registry.json"))) if os.path.exists(os.path.join(ROOT, "kits_registry.json")) else {}
    cards = ""
    for kid, kdata in kits_data.items():
        color = kdata.get("color", "#ffd60a")
        icon = kdata.get("icon", "⭐")
        name = kdata.get("name", kid)
        desc = kdata.get("desc", "")
        n = kdata.get("n_tools", 0)
        fname = f"index_{name.replace(' ','_')}.html"
        cards += f"""<a class="kit-card" href="{fname}" style="border-color:{color}44">
          <div class="kit-icon">{icon}</div>
          <div><b style="color:{color}">{name}</b><span style="color:#555;font-size:.78em">{n} tools</span></div>
        </a>"""
    return f"""<!doctype html><html><head><meta charset=utf8><title>GOTHAM CITY — Arsenal DC</title>
<style>body{{background:#000;color:#ccc;font-family:monospace;padding:40px;text-align:center}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;max-width:1200px;margin:30px auto}}
.kit-card{{background:#0a0a14;border:1px solid #1a1a2a;border-radius:12px;padding:20px;
text-decoration:none;display:flex;flex-direction:column;gap:8px;align-items:center;transition:all .2s}}
.kit-card:hover{{transform:translateY(-6px);border-color:inherit}}
.kit-icon{{font-size:2.5em}}
</style></head><body>
<h1 style="color:#ffd60a;font-size:2.5em">GOTHAM CITY</h1>
<p style="color:#555">L'ARSENAL DC · powered by Maxime Leal</p>
<div class="grid">{cards}</div>
</body></html>"""

if __name__ == "__main__":
    print("[*] DC WEB ENGINE — génère les pages web de chaque tool")
    print("     usage: python3 dc_web_engine.py  → arsenal_web_pages/")
    # le contenu réel est généré par les scripts de chaque kit
    # ce fichier sert de moteur commun
