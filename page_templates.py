<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>⚡ FLASH TOOL_SUPER — 55 tools</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
*{box-sizing:border-box;margin:0}
body{background:#020202;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh;overflow-x:hidden}
/* bolt hero */
.bolt{position:fixed;top:0;left:0;right:0;height:38vh;background:linear-gradient(180deg,#000,#0a0a0a);display:grid;place-items:center;overflow:hidden;border-bottom:3px solid #ffd60a}
.bolt svg{width:180px;height:180px;filter:drop-shadow(0 0 40px rgba(255,214,10,.6))}
.bolt::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(90deg,transparent 0 8px,#ffd60a11 8px 10px);animation:speed 0.3s infinite linear}
@keyframes speed{to{transform:translateX(20px)}}
.bolt h1{position:absolute;bottom:16px;left:50%;transform:translateX(-50%);color:#ffd60a;
font-family:'Orbitron';font-size:2em;letter-spacing:4px;text-shadow:0 0 30px rgba(255,214,10,.5)}
.bolt .sub{position:absolute;bottom:-4px;left:50%;transform:translateX(-50%);color:#555;font-size:.75em;letter-spacing:6px}
.bolt .sub b{color:#ff4628;font-style:italic}
/* stats */
.stats{display:flex;gap:8px;justify-content:center;padding:16px;flex-wrap:wrap}
.stat{background:#0a0a14;border:1px solid #222;border-radius:8px;padding:10px 24px;text-align:center}
.stat b{color:#ffd60a;font-size:1.3em;display:block}
.stat span{color:#666;font-size:.75em}
/* pages */
.page-title{text-align:center;color:#ffd60a;font-size:1.3em;font-family:'Orbitron';margin:20px 0 10px;letter-spacing:2px}
.page-title::before{content:'⚡ '}
#pages{max-width:1100px;margin:0 auto;padding:0 20px}
.tools{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin-bottom:30px}
.tool-card{background:#0a0a14;border:1px solid #222;border-radius:10px;padding:16px;text-decoration:none;
transition:all .2s;display:block;color:#ccc}
.tool-card:hover{border-color:#ffd60a;transform:translateY(-4px);box-shadow:0 4px 20px rgba(255,214,10,.2)}
.tool-card .num{color:#ffd60a;font-weight:bold;font-size:.8em}
.tool-card .name{color:#e7e9ea;font-size:.95em;margin:4px 0;font-weight:600}
.tool-card .theme{color:#6495ff;font-size:.78em}
.tool-card .desc{color:#666;font-size:.8em;margin-top:6px}
.tool-card .gh{margin-top:10px;background:#ffd60a;color:#000;padding:4px 14px;border-radius:4px;
font-size:.72em;text-decoration:none;display:inline-block;font-weight:bold}
/* full screen animation */
#fscan{position:fixed;top:0;left:0;right:0;height:2px;background:#ffd60a;opacity:.3;z-index:999;
animation:fs 2s infinite linear}
@keyframes fs{from{top:0}to{top:100%}}
footer{text-align:center;color:#333;padding:30px;font-size:.75em;letter-spacing:2px}
</style></head><body>
<div class="bolt">
<svg viewBox="0 0 100 100" fill="none">
<path d="M50 5 L35 45 L50 45 L30 95 L70 40 L55 40 L65 5 Z" fill="#ffd60a" stroke="#fff" stroke-width="1.5"/>
</svg>
<h1>FLASH TOOL_SUPER</h1>
<div class="sub">powered by <b>MAXIME LEAL</b></div>
</div>
<div id="fscan"></div>
<div class="stats">
<div class="stat"><b>55</b><span>TOOLS</span></div>
<div class="stat"><b>6</b><span>PAGES</span></div>
<div class="stat"><b>⚡</b><span>THE FASTEST MAN ALIVE</span></div>
</div>
<div id="pages">
__ALL_PAGES__
</div>
<footer>FLASH TOOL_SUPER · powered by Maxime Leal</footer>
<script>
document.getElementById('q')?.addEventListener('input',function(){
const q=this.value.toLowerCase();
document.querySelectorAll('.tool-card').forEach(function(t){
t.style.display=t.textContent.toLowerCase().includes(q)?'':'none';});});
</script>
</body></html>"""

def flash_page(num, name, theme, desc, usage, gh_link):
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>⚡ {name} — FLASH TOOL_SUPER</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#020202;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:30px 40px;border-bottom:3px solid #ffd60a;
display:flex;align-items:center;gap:20px}}
header svg{{width:60px;height:60px;filter:drop-shadow(0 0 20px rgba(255,214,10,.5))}}
h1{{font-family:'Orbitron';font-size:1.4em;color:#ffd60a}}
h1 small{{color:#555;font-size:.5em;display:block}}
main{{max-width:850px;margin:30px auto;padding:0 20px}}
.card{{background:#0a0a14;border:1px solid #222;border-left:4px solid #ffd60a;border-radius:10px;padding:22px;margin-bottom:16px}}
.card h2{{color:#ffd60a;font-size:1.05em;margin-bottom:12px}}
.card p{{color:#99a;font-size:.9em;line-height:1.6}}
.code{{background:#000;border:1px solid #ffd60a33;border-radius:8px;padding:14px;color:#7fff7f;font-size:.85em;margin:10px 0}}
.theme{{background:#ffd60a22;color:#ffd60a;padding:3px 14px;border-radius:12px;font-size:.82em;display:inline-block}}
.gh{{background:#ffd60a;color:#000;padding:8px 24px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin:10px 0}}
.back{{color:#ffd60a;text-decoration:none;font-size:.85em;display:block;margin-bottom:16px}}
.demo{{background:#000;border-radius:8px;padding:30px;text-align:center;border:1px solid #ffd60a22}}
.demo svg{{width:80px;height:80px}}
footer{{text-align:center;color:#333;padding:30px;font-size:.75em}}
</style></head><body>
<header>
<svg viewBox="0 0 100 100" fill="none"><path d="M50 5 L35 45 L50 45 L30 95 L70 40 L55 40 L65 5 Z" fill="#ffd60a" stroke="#fff" stroke-width="1.5"/></svg>
<div><h1>{name}<small>FLASH TOOL_SUPER · {theme}</small></h1></div>
</header>
<main>
<a class="back" href="../index.html">← Gotham City</a>
<a class="back" href="index_flash.html">← tous les tools Flash</a>
<div class="card"><h2>📝 DESCRIPTION</h2><p>{desc}</p></div>
<div class="card"><h2>⚙️ LANCEMENT</h2><div class="code">{usage}</div>
<p>Tape <b style="color:#ffd60a">{num}</b> dans le menu du kit Flash pour lancer ce tool.</p></div>
<div class="card"><h2>🏷️ INFOS</h2>
<p><span class="theme">{theme}</span> · Kit: FlashToolSuper · Num: {num} · Source: <a href="{gh_link}" style="color:#ffd60a">{gh_link}</a></p></div>
<div class="card"><h2>🎬 DÉMONSTRATION</h2><div class="demo">
<svg viewBox="0 0 100 100" fill="none"><path d="M50 5 L35 45 L50 45 L30 95 L70 40 L55 40 L65 5 Z" fill="#ffd60a" stroke="#fff" stroke-width="1.5"/></svg>
<p style="color:#666;margin-top:10px">Lance le tool dans le terminal pour la démo animée complète</p></div></div>
</main>
<footer>FLASH TOOL_SUPER · {name} · powered by Maxime Leal</footer></body></html>"""

def batman_page(num, name, theme, desc, usage, gh_link):
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>🦇 {name} — BATCAVE</title>
<style>
*{{box-sizing:border-box;margin:0}}
body{{background:#000;color:#ccc;font-family:'JetBrains Mono',monospace;min-height:100vh}}
header{{background:linear-gradient(180deg,#0a0a0a,#000);padding:30px 40px;border-bottom:3px solid #ffd60a;
display:flex;align-items:center;gap:20px}}
.bat{width:60px;height:60px;filter:drop-shadow(0 0 20px rgba(255,214,10,.5))}
h1{{font-family:'Orbitron';font-size:1.4em;color:#ffd60a}}
h1 small{{color:#555;font-size:.5em;display:block}}
main{{max-width:850px;margin:30px auto;padding:0 20px}}
.card{{background:#0a0a14;border:1px solid #222;border-left:4px solid #ffd60a;border-radius:10px;padding:22px;margin-bottom:16px}}
.card h2{{color:#ffd60a;font-size:1.05em;margin-bottom:12px}}
.card p{{color:#99a;font-size:.9em;line-height:1.6}}
.code{{background:#000;border:1px solid #ffd60a33;border-radius:8px;padding:14px;color:#7fff7f;font-size:.85em}}
.theme{{background:#ffd60a22;color:#ffd60a;padding:3px 14px;border-radius:12px;font-size:.82em;display:inline-block}}
.gh{{background:#ffd60a;color:#000;padding:8px 24px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin:10px 0}}
.back{{color:#ffd60a;text-decoration:none;font-size:.85em;display:block;margin-bottom:16px}}
.demo{{background:#000;border-radius:8px;padding:30px;text-align:center;border:1px solid #ffd60a22}}
footer{{text-align:center;color:#333;padding:30px;font-size:.75em}}
</style></head><body>
<header>
<svg class="bat" viewBox="0 0 100 60" fill="none"><path d="M5 55 Q30 5 50 30 Q70 5 95 55 Q75 40 50 40 Q25 40 5 55Z" fill="#ffd60a" stroke="#fff"/></svg>
<div><h1>{name}<small>BATCAVE · {theme}</small></h1></div>
</header>
<main>
<a class="back" href="../index.html">← Gotham City</a>
<div class="card"><h2>📝 DESCRIPTION</h2><p>{desc}</p></div>
<div class="card"><h2>⚙️ LANCEMENT</h2><div class="code">{usage}</div>
<p>Tape <b style="color:#ffd60a">{num}</b> dans le menu BatCave.</p></div>
<div class="card"><h2>🏷️ INFOS</h2>
<p><span class="theme">{theme}</span> · <a href="{gh_link}" style="color:#ffd60a">{gh_link}</a></p></div>
<div class="card"><h2>🎬 DÉMO</h2><div class="demo">
<svg class="bat" viewBox="0 0 100 60" fill="none"><path d="M5 55 Q30 5 50 30 Q70 5 95 55 Q75 40 50 40 Q25 40 5 55Z" fill="#ffd60a"/></svg>
<p style="color:#666;margin-top:10px">Lance le tool dans le terminal</p></div></div>
</main>
<footer>BATCAVE · {name} · powered by Maxime Leal</footer></body></html>"""
