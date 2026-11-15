#!/usr/bin/env python3
# language: Python 3, file: batweb.py, target: macOS
# BATWEB — les 3 apps web de l'arsenal (servies par gotham_full sur /app/)
#   /app/forensics  → Forensics Email : verdict authentique/spoofé/suspect + carte des relais
#   /app/stegano    → Stégano Studio : cacher/révéler un message dans une image (glisser-déposer)
#   /app/netmap     → Carte réseau vivante : les hôtes du wifi en graphe, auto-refresh
import json, os, re, subprocess, concurrent.futures

GITHUB = "https://github.com/MaximeLEAL/tool_DC-arsenal"

CSS = """:root{--bg:#06070c; --panel:#0c0e17; --panel2:#070810; --line:#1a1c2e;
  --txt:#c4c6d6; --muted:#6a6d86; --dim:#45485e; --red:#e63022; --gold:#f5c518;
  --disp:"Anton",Impact,sans-serif; --cond:"Oswald",sans-serif;
  --sans:"Archivo",-apple-system,sans-serif; --mono:"JetBrains Mono",monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:var(--sans);min-height:100vh;position:relative}
::selection{background:var(--red);color:#fff}
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.bg .beam{position:absolute;inset:0;background:
  radial-gradient(44% 70% at 50% 108%,color-mix(in srgb,var(--c) 10%,transparent),transparent 60%),
  radial-gradient(60% 80% at 50% -10%,rgba(230,48,34,.12),transparent 62%)}
.bg .dots{position:absolute;inset:0;opacity:.12;background-image:radial-gradient(rgba(255,255,255,.5) 1px,transparent 1.4px);background-size:16px 16px;mask-image:radial-gradient(ellipse 70% 55% at 50% 20%,#000 10%,transparent 72%)}
.bg .grid{position:absolute;inset:0;opacity:.5;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:52px 52px;mask-image:radial-gradient(ellipse 85% 70% at 50% 30%,#000 35%,transparent 88%)}
.bg .vig{position:absolute;inset:0;background:radial-gradient(ellipse 100% 80% at 50% 30%,transparent 55%,rgba(0,0,0,.55))}
.wrap{position:relative;z-index:1}
.nav{display:flex;justify-content:space-between;align-items:center;padding:14px clamp(18px,4vw,40px);position:sticky;top:0;z-index:30;background:rgba(6,7,12,.55);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.brand{font-family:var(--cond);font-weight:700;letter-spacing:5px;font-size:.95rem;color:#fff;display:flex;align-items:center;gap:11px;text-transform:uppercase;text-decoration:none}
.brand .dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 14px var(--red)}
.brand em{color:var(--red);font-style:normal}
.tabs{display:flex;gap:10px}
.tabs a{font-family:var(--mono);font-size:.66rem;letter-spacing:1px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:7px 13px;border-radius:9px;transition:.2s}
.tabs a:hover{color:#cdd9ff;border-color:#6495ff}
.tabs a.on{color:var(--c);border-color:var(--c);background:color-mix(in srgb,var(--c) 12%,transparent)}
main{max-width:860px;margin:26px auto 0;padding:0 24px 44px;position:relative;z-index:1}
.crumb{font-family:var(--mono);font-size:.68rem;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:14px}
.crumb a{color:var(--c);text-decoration:none}
h1{font-family:var(--disp);color:#fff;font-size:clamp(1.9rem,5vw,2.7rem);margin:6px 0 4px;letter-spacing:1px;text-transform:uppercase;text-shadow:0 2px 0 rgba(0,0,0,.55)}
.sub{font-family:var(--mono);color:var(--muted);font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:22px}
.card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:4px;padding:18px 20px;margin-bottom:14px;position:relative}
.card::before{content:"";position:absolute;inset:auto 0 0 0;height:3px;background:linear-gradient(90deg,transparent,var(--c),transparent)}
textarea,input[type=text],input[type=password]{width:100%;background:var(--panel2);border:1px solid var(--line);color:#fff;
  font-family:var(--mono);font-size:.8rem;padding:12px 14px;border-radius:8px;outline:none;transition:.25s}
textarea{min-height:190px;line-height:1.6;resize:vertical}
textarea:focus,input:focus{border-color:var(--c);box-shadow:0 0 20px color-mix(in srgb,var(--c) 18%,transparent)}
.btn{display:inline-block;font-family:var(--mono);font-size:.72rem;letter-spacing:2px;font-weight:700;color:#fff;
  background:linear-gradient(135deg,var(--c),color-mix(in srgb,var(--c) 60%,#000));border:none;border-radius:10px;
  padding:13px 26px;cursor:pointer;text-transform:uppercase;transition:.2s;text-decoration:none}
.btn:hover{transform:translateY(-2px);box-shadow:0 8px 26px color-mix(in srgb,var(--c) 35%,transparent)}
.btn.ghost{background:transparent;border:1px solid var(--line);color:var(--muted)}
.btn.ghost:hover{color:#fff;border-color:var(--c)}
.verdict{border-radius:8px;padding:18px 22px;margin:16px 0;display:none;border:1px solid}
.verdict.ok{display:block;background:rgba(74,214,109,.08);border-color:#4ad66d66}
.verdict.bad{display:block;background:rgba(230,48,34,.08);border-color:#e6302266}
.verdict.mid{display:block;background:rgba(245,197,24,.08);border-color:#f5c51866}
.verdict .big{font-family:var(--disp);font-size:1.7rem;letter-spacing:2px}
.verdict.ok .big{color:#4ad66d}.verdict.bad .big{color:#e63022}.verdict.mid .big{color:#f5c518}
.verdict ul{margin:10px 0 0;padding:0;list-style:none}
.verdict li{font-family:var(--mono);font-size:.74rem;padding:3px 0;color:var(--txt)}
.checks li b.ok{color:#4ad66d}.checks li b.ko{color:#e63022}.checks li b.mid{color:#f5c518}
.hop{display:flex;gap:12px;align-items:flex-start;padding:11px 0;border-left:2px solid var(--c);margin-left:10px;padding-left:18px;position:relative}
.hop::before{content:"";position:absolute;left:-6px;top:16px;width:10px;height:10px;border-radius:50%;background:var(--c);box-shadow:0 0 10px var(--c)}
.hop .ip{font-family:var(--mono);color:var(--c);font-size:.78rem}
.hop .lbl{color:var(--txt);font-size:.86em}
.hop .dt{font-family:var(--mono);color:var(--dim);font-size:.66rem}
.drop{border:2px dashed var(--line);border-radius:12px;padding:34px;text-align:center;color:var(--muted);
  font-family:var(--mono);font-size:.75rem;letter-spacing:1px;transition:.25s;cursor:pointer;background:var(--panel2)}
.drop.hover{border-color:var(--c);background:color-mix(in srgb,var(--c) 8%,transparent);color:#fff}
.preview{max-width:100%;border-radius:8px;border:1px solid var(--line);margin:14px 0;display:none}
#netmap{width:100%;height:520px;border:1px solid var(--line);border-radius:8px;background:var(--panel2)}
.legend{display:flex;gap:18px;font-family:var(--mono);font-size:.64rem;color:var(--muted);margin:12px 0;flex-wrap:wrap}
.legend span::before{content:"●";margin-right:6px}
footer{text-align:center;color:var(--muted);padding:34px 20px 50px;font-family:var(--mono);font-size:.66rem;letter-spacing:2.2px;border-top:1px solid var(--line);text-transform:uppercase}
footer a{color:#9fb4ff;text-decoration:none}"""

def shell(app_id, color, title, crumb, body, extra_js=""):
    nav_tabs = f"""
      <div class="tabs">
        <a href="/app/forensics" class="{'on' if app_id=='forensics' else ''}">FORENSICS</a>
        <a href="/app/stegano" class="{'on' if app_id=='stegano' else ''}">STÉGANO</a>
        <a href="/app/netmap" class="{'on' if app_id=='netmap' else ''}">RÉSEAU</a>
      </div>"""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — BATWEB · Gotham City</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;500;600;700&family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body style="--c:{color}">
<div class="bg"><div class="beam"></div><div class="dots"></div><div class="grid"></div><div class="vig"></div></div>
<div class="wrap">
<nav class="nav"><a class="brand" href="/"><span class="dot"></span>Gotham <em>City</em></a>{nav_tabs}</nav>
<main>
<div class="crumb">{crumb}</div>
{body}
</main>
<footer>BATWEB · APPS DE L'ARSENAL DC · <a href="{GITHUB}">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
</div>
<script>{extra_js}</script>
</body></html>"""

# ─────────────────────────── 1. FORENSICS EMAIL ───────────────────────────
FORENSICS_JS = r"""
function splitHeaders(txt){
  const lines = txt.replace(/\r/g,'').split('\n');
  const heads = []; let cur = null;
  for (const l of lines){
    if (/^[A-Za-z-]+:\s/.test(l)){ if(cur) heads.push(cur); cur = [l]; }
    else if (cur && (l.startsWith(' ') || l.startsWith('\t'))) cur.push(l);
    else if (cur && l.trim()==='') { heads.push(cur); cur = null; }
  }
  if (cur) heads.push(cur);
  return heads.map(h => { const parts = h.join(' '); const i = parts.indexOf(':');
    return [parts.slice(0,i).trim(), parts.slice(i+1).trim()]; });
}
const PRIVATE = ip => /^(10\.|127\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|169\.254\.)/.test(ip);
function domainOf(addr){
  const m = (addr||'').match(/@([\w.-]+)/); return m ? m[1].toLowerCase() : '';
}
function analyze(){
  const txt = document.getElementById('hdr').value;
  const heads = splitHeaders(txt);
  const get = n => (heads.find(h => h[0].toLowerCase() === n) || ['', ''])[1];
  const all = Object.fromEntries(heads.map(h => [h[0].toLowerCase(), h[1]]));
  // auth
  const ar = (all['authentication-results']||'') + ' ' + (all['received-spf']||'');
  const spf = /spf\s*=\s*(\w+)/i.exec(ar); const dkim = /dkim\s*=\s*(\w+)/i.exec(ar);
  const dmarc = /dmarc\s*=\s*(\w+)/i.exec(ar);
  const from = get('from'), rp = get('return-path');
  const dFrom = domainOf(from), dRp = domainOf(rp);
  const val = r => r ? r[1].toLowerCase() : 'absent';
  const vSpf = val(spf), vDkim = val(dkim), vDmarc = val(dmarc);
  const domMatch = dFrom && dRp ? dFrom === dRp || dRp.endsWith(dFrom) || dFrom.endsWith(dRp) : false;
  // verdict
  let bad = 0;
  const rows = [];
  const row = (name, state, note) => rows.push(`<li>${name} <b class="${state}">${note}</b></li>`);
  const good = v => v === 'pass';
  const spfState = good(vSpf) ? 'ok' : (vSpf === 'softfail' || vSpf === 'none' || vSpf === 'absent') ? 'mid' : 'ko';
  if (spfState === 'ko') bad++;
  row('SPF', spfState, vSpf);
  const dkState = vDkim === 'pass' ? 'ok' : vDkim === 'absent' ? 'mid' : 'ko';
  if (dkState === 'ko') bad++;
  row('DKIM', dkState, vDkim);
  const dmState = vDmarc === 'pass' ? 'ok' : vDmarc === 'absent' ? 'mid' : 'ko';
  if (dmState === 'ko') bad++;
  row('DMARC', dmState, vDmarc);
  const domState = domMatch ? 'ok' : (dRp ? 'ko' : 'mid');
  if (domState === 'ko') bad++;
  row('Domaine From ↔ Return-Path', domState, domMatch ? (dFrom + ' ✓') : (dRp ? dFrom + ' ≠ ' + dRp : 'Return-Path absent'));
  let cls, big, sub;
  if (bad === 0 && vSpf === 'pass'){ cls='ok'; big='AUTHENTIQUE'; sub='Tous les contrôles passent — l\'email est conforme.'; }
  else if (spfState === 'ko' || domState === 'ko'){ cls='bad'; big='SPOOFÉ'; sub='Signaux d\'usurpation d\'identité — n\'ouvre pas les pièces jointes.'; }
  else { cls='mid'; big='SUSPECT'; sub='Signaux mixtes — vérifie l\'expédieur avant toute action.'; }
  const v = document.getElementById('verdict');
  v.className = 'verdict ' + cls;
  v.innerHTML = `<div class="big">${big}</div><div style="color:var(--muted);font-size:.85em;margin-top:4px">${sub}</div>
    <ul class="checks">${rows.join('')}</ul>`;
  // relais
  const hops = [];
  for (const [name, val_] of heads){
    if (name.toLowerCase() !== 'received') continue;
    const fm = /from\s+([^\s(]+)/i.exec(val_);
    const bm = /by\s+([^\s;]+)/i.exec(val_);
    const ipm = val_.match(/\b\d{1,3}(\.\d{1,3}){3}\b/);
    const dm = /\w{3},\s*\d{1,2}\s+\w{3}\s+\d{4}[^;]*/.exec(val_);
    const ip = ipm ? ipm[0] : '';
    hops.push({from: fm ? fm[1] : '?', by: bm ? bm[1] : '?', ip, date: dm ? dm[0] : '', priv: ip ? PRIVATE(ip) : true});
  }
  const chain = hops.map((h,i) => `<div class="hop">
    <div><div class="lbl">Hop ${i+1} — depuis <b>${h.from.replace(/[<>]/g,'')}</b> vers <b>${h.by.replace(/[<>]/g,'')}</b></div>
    ${h.ip ? `<div class="ip">${h.ip} ${h.priv ? '· réseau privé' : '· IP publique'}</div>` : ''}
    ${h.date ? `<div class="dt">${h.date}</div>` : ''}</div></div>`).join('');
  document.getElementById('chain').innerHTML = chain || '<div style="color:var(--muted)">Aucun header Received — colle les headers complets.</div>';
  document.getElementById('chainwrap').style.display = 'block';
  document.getElementById('vwrap').style.display = 'block';
  v.scrollIntoView({behavior:'smooth', block:'start'});
}
function sample(){
  document.getElementById('hdr').value = `Received: from mail-out.example.com (mail-out.example.com [93.184.216.34])\n\tby mx.google.com with ESMTPS id abc123\n\tfor <maxime@gmail.com>; Sat, 14 Nov 2026 08:12:01 +0100\nReceived: from [192.168.1.55] (unknown [192.168.1.55])\n\tby mail.example.com (Postfix) with ESMTPSA id DEF456\n\tfor <contact@example.com>; Sat, 14 Nov 2026 08:11:55 +0100\nAuthentication-Results: mx.google.com; spf=fail (google.com: domain of info@paypa1-secure.com does not designate 93.184.216.34 as permitted sender) smtp.mailfrom=info@paypa1-secure.com; dkim=none; dmarc=fail (p=NONE)\nFrom: PayPa1 Securite <service@paypa1-secure.com>\nReturn-Path: <bounce@spam-relay.ru>\nSubject: URGENT : votre compte sera suspendu\nTo: <maxime@gmail.com>` + "\n";
}
"""

def page_forensics():
    body = f"""
    <h1>Forensics Email</h1>
    <div class="sub">Colle les headers d'un email · verdict visuel + carte des relais · analyse 100% locale</div>
    <div class="card">
      <textarea id="hdr" placeholder="Colle ici les headers bruts (Received, Authentication-Results, From, Return-Path…)"></textarea>
      <div style="display:flex;gap:12px;margin-top:14px;flex-wrap:wrap">
        <button class="btn" onclick="analyze()">🔍 Analyser</button>
        <button class="btn ghost" onclick="sample()">Charger un exemple spoofé</button>
      </div>
    </div>
    <div id="vwrap" style="display:none">
      <div id="verdict" class="verdict"></div>
    </div>
    <div id="chainwrap" style="display:none">
      <div class="card"><h3 style="font-family:var(--cond);color:#fff;letter-spacing:1px;margin-bottom:12px">🗺️ CARTE DES RELAIS</h3>
      <div id="chain"></div></div>
    </div>
    <div class="card"><p style="color:var(--muted);font-size:.85em;line-height:1.6">Comment lire : <b>SPF</b> vérifie que le serveur émetteur est autorisé pour le domaine · <b>DKIM</b> que le message est signé · <b>DMARC</b> aligne le domaine affiché. Un <b>Return-Path</b> différent du <b>From</b> est le signal n°1 d'usurpation. L'analyse se fait entièrement dans ton navigateur — rien n'est envoyé.</p></div>
    """
    return shell("forensics", "#64a0ff", "Forensics Email",
                 '<a href="/">← Gotham City</a> · APP WEB · BATCAVE ANALYSE EMAIL', body, FORENSICS_JS)

# ─────────────────────────── 2. STÉGANO STUDIO ───────────────────────────
STEGANO_JS = r"""
const MAGIC = [0x44,0x43,0x53,0x54,0x47,0x31]; // "DCSTG1"
let img = null, mode = 'hide';
async function keyStream(password, length){
  if (!password) return null;
  const out = new Uint8Array(length);
  let block = 0;
  for (let off = 0; off < length; off += 32){
    const data = new TextEncoder().encode(password + ':' + block++);
    const h = await crypto.subtle.digest('SHA-256', data);
    out.set(new Uint8Array(h).slice(0, Math.min(32, length - off)), off);
  }
  return out;
}
function setupDrop(id, cb){
  const el = document.getElementById(id);
  el.addEventListener('dragover', e => { e.preventDefault(); el.classList.add('hover'); });
  el.addEventListener('dragleave', () => el.classList.remove('hover'));
  el.addEventListener('drop', e => { e.preventDefault(); el.classList.remove('hover');
    const f = e.dataTransfer.files[0]; if (f) cb(f); });
  el.addEventListener('click', () => { const i = document.createElement('input');
    i.type = 'file'; i.accept = 'image/*'; i.onchange = () => cb(i.files[0]); i.click(); });
}
function loadImage(file, canvas, cb){
  const img = new Image();
  img.onload = () => { canvas.width = img.width; canvas.height = img.height;
    canvas.getContext('2d').drawImage(img, 0, 0); cb(canvas); };
  img.src = URL.createObjectURL(file);
}
function bitsOf(bytes){ const bits = []; for (const b of bytes) for (let i = 7; i >= 0; i--) bits.push((b >> i) & 1); return bits; }
function bytesOf(bits){ const out = []; for (let i = 0; i + 8 <= bits.length; i += 8){
  let b = 0; for (let j = 0; j < 8; j++) b = (b << 1) | bits[i + j]; out.push(b); } return new Uint8Array(out); }
setupDrop('dropHide', f => loadImage(f, document.getElementById('cvHide'), cv => {
  img = cv; document.getElementById('pvHide').src = cv.toDataURL('image/png');
  document.getElementById('pvHide').style.display = 'block';
  document.getElementById('dropHide').innerHTML = '✅ ' + f.name + ' (' + cv.width + '×' + cv.height + ') — prête à cacher un message';
}));
async function hide(){
  if (!img){ alert('Dépose d\'abord une image'); return; }
  const msg = new TextEncoder().encode(document.getElementById('msg').value);
  if (!msg.length){ alert('Écris un message à cacher'); return; }
  const pw = document.getElementById('pwHide').value;
  let payload = msg;
  if (pw){ const ks = await keyStream(pw, msg.length);
    payload = msg.map((b, i) => b ^ ks[i]); }
  const head = [...MAGIC, (payload.length >> 24) & 255, (payload.length >> 16) & 255,
                (payload.length >> 8) & 255, payload.length & 255];
  const all = bitsOf(new Uint8Array([...head, ...payload]));
  const ctx = img.getContext('2d');
  const data = ctx.getImageData(0, 0, img.width, img.height);
  const px = data.data;
  if (all.length > px.length / 4 * 3){ alert('Message trop long pour cette image (capacité : ' +
    Math.floor(px.length / 4 * 3 / 8 - 11) + ' octets)'); return; }
  let bit = 0;
  for (let i = 0; i < px.length && bit < all.length; i++){
    if (i % 4 === 3) continue; // jamais l'alpha
    px[i] = (px[i] & 0xFE) | all[bit++];
  }
  ctx.putImageData(data, 0, 0);
  const url = img.toDataURL('image/png');
  const pv = document.getElementById('pvOut'); pv.src = url; pv.style.display = 'block';
  const a = document.getElementById('dl'); a.href = url; a.download = 'stego.png'; a.style.display = 'inline-block';
  document.getElementById('done').style.display = 'block';
}
setupDrop('dropRev', f => loadImage(f, document.getElementById('cvRev'), async cv => {
  const ctx = cv.getContext('2d');
  const data = ctx.getImageData(0, 0, cv.width, cv.height).data;
  const bits = []; for (let i = 0; i < data.length && bits.length < 8 * 560; i++){
    if (i % 4 === 3) continue; bits.push(data[i] & 1); }
  const head = bytesOf(bits.slice(0, 8 * 9));
  for (let i = 0; i < 6; i++) if (head[i] !== MAGIC[i]){
    document.getElementById('res').innerHTML = '<div class="verdict mid" style="display:block"><div class="big">RIEN DÉTECTÉ</div><div style="color:var(--muted);font-size:.85em">Aucun message de l\'arsenal dans cette image (l\'image a peut-être été réencodée en JPEG — ça détruit le message caché).</div></div>'; return; }
  const len = (head[6] << 24) | (head[7] << 16) | (head[8] << 8) | head[9];
  const need = 8 * 9 + 8 * len;
  const bits2 = []; const d2 = ctx.getImageData(0, 0, cv.width, cv.height).data;
  for (let i = 0; i < d2.length && bits2.length < need; i++){ if (i % 4 === 3) continue; bits2.push(d2[i] & 1); }
  let payload = bytesOf(bits2.slice(8 * 9));
  const pw = document.getElementById('pwRev').value;
  if (pw){ const ks = await keyStream(pw, payload.length); payload = payload.map((b, i) => b ^ ks[i]); }
  document.getElementById('res').innerHTML = '<div class="verdict ok" style="display:block"><div class="big">MESSAGE RÉVÉLÉ</div>' +
    '<pre style="margin-top:10px;color:var(--txt);white-space:pre-wrap;font-family:var(--mono);font-size:.85em">' +
    new TextDecoder().decode(payload).replace(/[<&]/g, '') + '</pre></div>';
}));
"""

def page_stegano():
    body = f"""
    <h1>Stégano Studio</h1>
    <div class="sub">Cache un message dans une image · glisser-déposer · LSB sur PNG · 100% local</div>
    <div class="card">
      <div class="drop" id="dropHide">🖼️ Dépose une image PNG ici (ou clique)</div>
      <canvas id="cvHide" style="display:none"></canvas>
      <img id="pvHide" class="preview" alt="">
      <div style="margin-top:14px">
        <textarea id="msg" placeholder="Ton message secret…" style="min-height:90px"></textarea>
        <input type="password" id="pwHide" placeholder="Mot de passe (optionnel — chiffre le message)" style="margin-top:10px">
        <div style="margin-top:14px"><button class="btn" onclick="hide()">🔒 Cacher le message</button></div>
      </div>
      <img id="pvOut" class="preview" alt="">
      <a class="btn ghost" id="dl" style="display:none" download="stego.png">⬇️ Télécharger l'image stego (PNG)</a>
      <div id="done" style="display:none;color:#4ad66d;font-family:var(--mono);font-size:.72rem;margin-top:10px">✓ Message caché — l'image est visuellement identique. Envoie-la à la cible du CTF.</div>
    </div>
    <div class="card">
      <div class="drop" id="dropRev">🔓 Dépose une image stego ici pour révéler son message</div>
      <canvas id="cvRev" style="display:none"></canvas>
      <input type="password" id="pwRev" placeholder="Mot de passe (si le message en avait un)" style="margin-top:12px">
      <div id="res"></div>
    </div>
    <div class="card"><p style="color:var(--muted);font-size:.85em;line-height:1.6">Comment ça marche : le message est écrit octet par octet dans le <b>bit de poids faible</b> de chaque canal RGB — l'œil ne voit aucune différence. Un mot de passe dérive un flux de chiffrement (SHA-256) qui masque le payload. ⚠️ Utilise le <b>PNG</b> : le JPEG réencode et détruit le message.</p></div>
    """
    return shell("stegano", "#9b30ff", "Stégano Studio",
                 '<a href="/">← Gotham City</a> · APP WEB · BATCAVE STÉGANO', body, STEGANO_JS)

# ─────────────────────────── 3. CARTE RÉSEAU VIVANTE ───────────────────────────
_seen = {}

def api_netmap_scan(deep=False):
    me_ip = me_mac = router = ""
    try:
        me_ip = subprocess.run(["ipconfig", "getifaddr", "en0"], capture_output=True, text=True).stdout.strip() \
             or subprocess.run(["ipconfig", "getifaddr", "en1"], capture_output=True, text=True).stdout.strip()
        rn = subprocess.run(["netstat", "-rn"], capture_output=True, text=True).stdout
        m = re.search(r"^default\s+([\d.]+)", rn, re.M)
        router = m.group(1) if m else ""
    except Exception:
        pass
    hosts = []
    # 1) table ARP si disponible (IP + MAC + nom)
    try:
        arp = subprocess.run(["arp", "-a"], capture_output=True, text=True).stdout
        for line in arp.splitlines():
            m = re.search(r"\(?([\d.]+)\)?\s+at\s+([\w:]+)", line)
            if not m: continue
            ip, mac = m.group(1), m.group(2)
            nm = re.match(r"([\w.-]+)\s+\(", line.strip())
            name = nm.group(1) if nm and not nm.group(1).startswith(("?",)) else ""
            hosts.append({"ip": ip, "mac": mac, "name": name or ("routeur" if ip == router else ""),
                          "router": ip == router, "me": ip == me_ip, "new": False})
    except Exception:
        pass
    # 2) fallback : ping sweep du /24 (ARP bloqué dans certains contextes launchd)
    if not hosts and (me_ip or router):
        base = ".".join((me_ip or router).split(".")[:3])
        def ping(ip):
            r = subprocess.run(["ping", "-c", "1", "-W", "1", ip], capture_output=True)
            return ip if r.returncode == 0 else None
        ips = [f"{base}.{i}" for i in range(1, 255) if f"{base}.{i}" != me_ip]
        with concurrent.futures.ThreadPoolExecutor(32) as ex:
            alive = [x for x in ex.map(ping, ips) if x]
        for ip in alive:
            hosts.append({"ip": ip, "mac": "", "name": "routeur" if ip == router else "",
                          "router": ip == router, "me": False, "new": False})
    # marque "new" pour les hôtes jamais vus
    for h in hosts:
        key = h["mac"] or h["ip"]
        if h["me"]: continue
        if key not in _seen: h["new"] = True
        _seen[key] = True
    return {"me": {"ip": me_ip, "mac": me_mac}, "router": router, "hosts": hosts,
            "count": len(hosts)}

NETMAP_JS = r"""
const cv = document.getElementById('netmap');
const ctx = cv.getContext('2d');
let nodes = [], t0 = Date.now();
function resize(){ cv.width = cv.clientWidth * devicePixelRatio; cv.height = cv.clientHeight * devicePixelRatio; }
window.addEventListener('resize', resize); resize();
function layout(hs){
  const W = cv.width, H = cv.height;
  nodes = hs.map((h, i) => ({
    ...h,
    x: h.me ? W/2 : (h.router ? W/2 : W/2 + Math.cos(i * 6.28 / Math.max(hs.length - 2, 1)) * W * 0.36),
    y: h.me ? H/2 : (h.router ? H*0.28 : H*0.28 + Math.sin(i * 6.28 / Math.max(hs.length - 2, 1)) * H * 0.3),
    vx: 0, vy: 0, r: h.me ? 26 : h.router ? 22 : 15,
    a: 0
  }));
}
async function scan(deep){
  const r = await fetch('/app/netmap/scan' + (deep ? '?deep=1' : ''));
  const d = await r.json();
  layout(d.hosts);
  document.getElementById('info').textContent =
    d.count + ' hôtes · toi : ' + (d.me.ip || '?') + ' · routeur : ' + (d.router || '?') +
    ' · rafraîchi ' + new Date().toLocaleTimeString();
  const nn = d.hosts.filter(h => h.new).length;
  document.getElementById('newdev').style.display = nn ? 'block' : 'none';
  document.getElementById('newdev').textContent = '🚨 ' + nn + ' NOUVEAU(x) APPAREIL(S) DÉTECTÉ(S) !';
}
function draw(){
  const W = cv.width, H = cv.height;
  ctx.clearRect(0, 0, W, H);
  ctx.strokeStyle = 'rgba(100,149,255,.25)'; ctx.lineWidth = 1;
  for (const n of nodes) for (const m of nodes){
    if (n === m) continue;
    if (n.router || m.router || n.me || m.me){
      ctx.beginPath(); ctx.moveTo(n.x, n.y); ctx.lineTo(m.x, m.y); ctx.stroke();
    }
  }
  for (const n of nodes){
    n.a = Math.min(1, n.a + .05);
    const col = n.me ? '#e63022' : n.router ? '#f5c518' : n.new ? '#ff8c30' : '#4ad66d';
    ctx.globalAlpha = n.a;
    ctx.beginPath(); ctx.arc(n.x, n.y, n.r + Math.sin(Date.now()/300) * (n.new ? 3 : 0), 0, 7);
    ctx.fillStyle = col; ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.fill(); ctx.shadowBlur = 0;
    ctx.fillStyle = '#fff'; ctx.font = '600 ' + (11 * devicePixelRatio) + 'px Archivo';
    ctx.textAlign = 'center';
    ctx.fillText((n.name || n.ip).slice(0, 22), n.x, n.y + n.r + 16 * devicePixelRatio);
    ctx.fillStyle = 'rgba(255,255,255,.55)'; ctx.font = (9 * devicePixelRatio) + 'px JetBrains Mono';
    ctx.fillText(n.mac.slice(0, 17), n.x, n.y + n.r + 30 * devicePixelRatio);
    ctx.globalAlpha = 1;
  }
  requestAnimationFrame(draw);
}
scan(); draw();
setInterval(() => scan(false), 10000);
document.getElementById('deep').addEventListener('click', () => { scan(true); });
"""

def page_netmap():
    body = f"""
    <h1>Carte réseau vivante</h1>
    <div class="sub">Les hôtes de ton wifi en temps réel · ARP + ping sweep · alerte nouvel appareil</div>
    <div id="newdev" style="display:none;background:rgba(255,140,48,.12);border:1px solid #ff8c3066;color:#ff8c30;
      font-family:var(--mono);font-size:.8rem;letter-spacing:1px;padding:12px 18px;border-radius:8px;margin-bottom:14px"></div>
    <canvas id="netmap"></canvas>
    <div class="legend">
      <span style="color:#e63022">toi</span><span style="color:#f5c518">routeur</span>
      <span style="color:#4ad66d">appareil connu</span><span style="color:#ff8c30">nouveau détecté</span>
    </div>
    <div class="card" style="display:flex;gap:14px;align-items:center;flex-wrap:wrap">
      <button class="btn" id="deep">⚡ Scan profond (/24 complet)</button>
      <span style="font-family:var(--mono);color:var(--muted);font-size:.7rem" id="info">scan en cours…</span>
    </div>
    <div class="card"><p style="color:var(--muted);font-size:.85em;line-height:1.6">La carte rafraîchit la table ARP toutes les <b>10 s</b> — tout appareil qui rejoint le wifi apparaît en orange pulsant. Le scan profond ping les 254 adresses du /24 pour découvrir même les appareils silencieux. 100% local.</p></div>
    """
    return shell("netmap", "#4ad66d", "Carte réseau vivante",
                 '<a href="/">← Gotham City</a> · APP WEB · RÉSEAU', body, NETMAP_JS)
