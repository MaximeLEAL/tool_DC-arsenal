# modules/joker.py - 8 tools de chaos (pranks locaux, Ctrl+C partout, lab uniquement)
import os, subprocess, time

OUT = os.path.dirname(os.path.abspath(__file__))

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def tempete_haha():
    print("  Ctrl+C pour stopper la tempete\n")
    while True:
        os.system('clear')
        for _ in range(15):
            x, y = __import__("random").randint(1, 70), __import__("random").randint(1, 24)
            print(f"\033[{y};{x}H\033[38;2;155;48;255mHA HA HA HA\033[0m", end="")
        print(f"\033[12;30HWHY SO SERIOUS ?", end="", flush=True)
        time.sleep(0.12)

def rire():
    lignes = ["ha ha ha ha ha ha", "pourquoi si serieux ?", "c'est un rat, morty... euh, un rire",
              "one bad day, voila tout"]
    for l in lignes:
        r(f'say -v Thomas "{l}"')
    print("  la machine a ri.")

def popup_orage():
    n = int(ask("nombre de popups (10)") or 10)
    for i in range(n):
        r(f'''osascript -e 'display dialog "HA HA HA - {i+1}/{n}" with title "JOKER" buttons {{"HA"}}' ''' )
    print("  orage termine.")

def notif_spam():
    n = int(ask("nombre de notifications (10)") or 10)
    for i in range(n):
        r(f'''osascript -e 'display notification "HA HA ({i+1})" with title "JOKER" subtitle "why so serious ?"’ ''')
        time.sleep(0.6)
    print("  notifications envoyees.")

def prank_page():
    """genere la page kiosque joker : plein ecran, sortie = taper JOKER"""
    html = """<!doctype html><html><head><meta charset=utf8><title>HAHA</title>
<style>html,body{margin:0;height:100%;background:#120024;overflow:hidden}
#c{display:grid;place-items:center;height:100vh;text-align:center}
h1{color:#57ff14;font-size:4em;font-family:monospace;text-shadow:0 0 20px #57ff14}
p{color:#b48cff;font-size:1.5em}</style></head>
<body onkeydown="guard(event)" oncontextmenu="return false">
<div id=c><h1>HA HA HA HA</h1><p id=m>Systeme compromis par le Clown.<br>Aucune echappatoire.</p></div>
<script>
document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
var buf="",COMBO="JOKER";
function guard(e){if(e.key==="F11")e.preventDefault();
if(e.key.length===1){buf=(buf+e.key.toUpperCase()).slice(-8);
if(buf.endsWith(COMBO)){document.getElementById("m").innerHTML="Une mauvaise journee, voila tout.";setTimeout(function(){document.exitFullscreen&&document.exitFullscreen()},1200);}}}
window.onbeforeunload=function(){return "Vraiment ?";};
</script></body></html>"""
    p = os.path.join(OUT, "..", "sorties", "prank_joker.html")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(html)
    print(f"  [OK] {p} - sert-la (python3 -m http.server) et combo de sortie = JOKER")
    r(f"open '{p}'")

def fake_update():
    html = """<!doctype html><html><head><meta charset=utf8><title>Mise a jour</title>
<style>html,body{margin:0;height:100%;background:#0a1a2a;color:#dff;font-family:sans-serif;display:grid;place-items:center}
.bar{width:420px;height:26px;border:2px solid #4af;border-radius:13px;overflow:hidden}
.fill{height:100%;width:0;background:#4af;animation:f 600s linear forwards}
@keyframes f{to{width:99%}}</style></head>
<body onkeydown="guard(event)"><div style="text-align:center">
<h2>Mise a jour du systeme en cours</h2><div class="bar"><div class="fill"></div></div>
<p id="pc">0%</p><p style="color:#678">N'eteignez pas votre ordinateur</p></div>
<script>
var t=setInterval(function(){document.getElementById("pc").textContent=Math.min(99,Math.floor(Math.random()*3)+parseInt(document.getElementById("pc").textContent)+1)+"%"},900);
document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen();
var buf="";function guard(e){if(e.key.length===1){buf=(buf+e.key.toUpperCase()).slice(-8);
if(buf.endsWith("JOKER")){clearInterval(t);document.exitFullscreen&&document.exitFullscreen();}}}
</script></body></html>"""
    p = os.path.join(OUT, "..", "sorties", "fake_update.html")
    open(p, "w").write(html)
    print(f"  [OK] {p} - sortie = taper JOKER")
    r(f"open '{p}'")

def volume_max():
    print("  volume a fond (les dialogues restaient muets, pas le volume) - Ctrl+C")
    try:
        while True:
            r('osascript -e "set volume output volume 10"')
            time.sleep(2)
    except KeyboardInterrupt:
        r('osascript -e "set volume output volume 4"')
        print("  volume rendu a 40%.")

def wallpaper_joke():
    # PNG violet genere a la main, pose en fond d'ecran
    import struct, zlib
    w, h = 64, 36
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    raw = b""
    for y in range(h):
        row = b"\x00"
        for x in range(w):
            purple = (60, 10, 90) if (x // 4 + y // 4) % 2 == 0 else (20, 4, 35)
            row += bytes(purple)
        raw += row
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    p = os.path.expanduser("~/Desktop/JokerChaos/sorties/wallpaper_joke.png")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(png)
    r(f'''osascript -e 'tell application "System Events" to tell every desktop to set picture to "{p}"' ''')
    print(f"  [OK] fond d'ecran pose : {p}")
    r(f"open '{p}'")

TOOLS = [
    ("TEMPETE HAHA",      "l'ecran envahi de rires (Ctrl+C)",        tempete_haha),
    ("RIRE DU JOKER",     "la machine rit a voix haute (say)",       rire),
    ("POPUP ORAGE",       "dialogues en rafale",                     popup_orage),
    ("NOTIFICATIONS",     "bombardement de notifications",           notif_spam),
    ("PRANK PLEIN ECRAN", "page invincible - sortie: taper JOKER",   prank_page),
    ("FAKE UPDATE",       "fausse mise a jour infinie - JOKER",      fake_update),
    ("VOLUME MAX",        "volume a fond en boucle (Ctrl+C)",        volume_max),
    ("WALLPAPER JOKE",    "fond d'ecran violet pose",                wallpaper_joke),
]
