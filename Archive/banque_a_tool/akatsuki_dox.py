# lang: Python 3.10+ | file: akatsuki_dox.py
# deps: pip install flask requests

import argparse, socket, json, sys, urllib.request, re, subprocess, platform, threading

BANNER = r"""
  █████╗ ██╗  ██╗ █████╗ ████████╗███████╗██╗   ██╗██╗  ██╗██╗
 ██╔══██╗██║ ██╔╝██╔══██╗╚══██╔══╝██╔════╝██║   ██║██║ ██╔╝██║
 ███████║█████╔╝ ███████║   ██║   ███████╗██║   ██║█████╔╝ ██║
 ██╔══██║██╔═██╗ ██╔══██║   ██║   ╚════██║██║   ██║██╔═██╗ ██║
 ██║  ██║██║  ██╗██║  ██║   ██║   ███████║╚██████╔╝██║  ██╗██║
 ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝
  DOX ENGINE v2  — "Pain knows everything about you."
"""

README = """
╔══════════════════════════════════════════════════════════════╗
║              AKATSUKI DOX — README                          ║
╠══════════════════════════════════════════════════════════════╣
║  USAGE CMD  : python akatsuki_dox.py                        ║
║  USAGE WEB  : python akatsuki_dox.py --web [--port N]       ║
╠══════════════════════════════════════════════════════════════╣
║  TOOLS (10)                                                 ║
║  1.  ip_dox          — full IP intel (geo, ASN, DNS, ports) ║
║  2.  domain_dox      — domain → IP chain + registrar hints  ║
║  3.  email_validate  — MX check + SMTP VRFY probe           ║
║  4.  phone_format    — parse + format intl phone numbers    ║
║  5.  username_hunt   — check username across 15 platforms   ║
║  6.  breach_check    — HIBP v3 k-anon password hash check   ║
║  7.  social_links    — build likely social URLs from name   ║
║  8.  google_dork     — generate targeted dork queries       ║
║  9.  metadata_strip  — show / strip EXIF from images        ║
║  10. timeline_build  — assemble findings into JSON timeline ║
╠══════════════════════════════════════════════════════════════╣
║  DEPS : pip install flask pillow requests                   ║
║  NOTE : HIBP check is k-anon (SHA1 prefix) — no PII sent   ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─── TOOLS ────────────────────────────────────────────────────────────────────

def ip_dox(ip):
    out = {"ip": ip}
    try: out["reverse_dns"] = socket.gethostbyaddr(ip)[0]
    except: out["reverse_dns"] = "none"
    try:
        with urllib.request.urlopen(f"http://ip-api.com/json/{ip}?fields=status,country,regionName,city,zip,lat,lon,isp,org,as,asname,query", timeout=6) as r:
            d = json.loads(r.read().decode())
        out.update({k: d.get(k) for k in ["country","regionName","city","zip","lat","lon","isp","org","as","asname"]})
    except Exception as e:
        out["geo_error"] = str(e)
    top20 = [21,22,23,25,53,80,110,135,139,143,443,445,3306,3389,5900,6379,8080,8443,27017,6443]
    open_p = []
    def chk(p):
        with socket.socket() as s:
            s.settimeout(0.4)
            if s.connect_ex((ip, p)) == 0: open_p.append(p)
    ts = [threading.Thread(target=chk, args=(p,), daemon=True) for p in top20]
    for t in ts: t.start()
    for t in ts: t.join(timeout=2)
    out["open_ports_top20"] = sorted(open_p)
    return out

def domain_dox(domain):
    out = {"domain": domain}
    try: out["ip"] = socket.gethostbyname(domain)
    except Exception as e: out["ip_error"] = str(e); return out
    out["ip_intel"] = ip_dox(out["ip"])
    for rec in ["MX","NS","TXT"]:
        try:
            if platform.system() == "Windows":
                cmd = ["nslookup", f"-type={rec}", domain]
            else:
                cmd = ["dig", "+short", rec, domain]
            r = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace").strip()
            out[rec] = r[:300] if r else "none"
        except: out[rec] = "error"
    return out

def email_validate(email):
    out = {"email": email}
    try:
        domain = email.split("@")[1]
        mx_cmd = ["nslookup","-type=MX",domain] if platform.system()=="Windows" else ["dig","+short","MX",domain]
        mx = subprocess.check_output(mx_cmd, stderr=subprocess.DEVNULL, timeout=5).decode(errors="replace").strip()
        out["MX"] = mx[:200] if mx else "none"
        if mx and mx != "none":
            mx_host = mx.split()[-1].rstrip(".")
            with socket.socket() as s:
                s.settimeout(5)
                s.connect((mx_host, 25))
                banner = s.recv(512).decode(errors="replace")
                out["smtp_banner"] = banner[:200]
                s.sendall(b"VRFY " + email.encode() + b"\r\n")
                vrfy = s.recv(512).decode(errors="replace")
                out["vrfy_response"] = vrfy[:200]
    except Exception as e:
        out["error"] = str(e)
    return out

def phone_format(number):
    # basic ITU E.164 parser — no phonenumbers lib needed
    cleaned = re.sub(r"[^\d+]", "", number)
    out = {"raw": number, "cleaned": cleaned, "length": len(cleaned.lstrip("+"))}
    cc_map = {"1":"US/CA","33":"FR","44":"UK","49":"DE","81":"JP","86":"CN","7":"RU","55":"BR","91":"IN","34":"ES"}
    if cleaned.startswith("+"):
        for cc, name in cc_map.items():
            if cleaned[1:].startswith(cc):
                out["country_code"] = f"+{cc}"; out["country"] = name
                out["local"] = cleaned[1+len(cc):]
                break
    return out

def username_hunt(username):
    platforms = {
        "GitHub":    f"https://github.com/{username}",
        "Twitter":   f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}",
        "Reddit":    f"https://www.reddit.com/user/{username}",
        "TikTok":    f"https://www.tiktok.com/@{username}",
        "Twitch":    f"https://www.twitch.tv/{username}",
        "YouTube":   f"https://www.youtube.com/@{username}",
        "LinkedIn":  f"https://www.linkedin.com/in/{username}",
        "Steam":     f"https://steamcommunity.com/id/{username}",
        "Replit":    f"https://replit.com/@{username}",
        "HackerNews":f"https://news.ycombinator.com/user?id={username}",
        "GitLab":    f"https://gitlab.com/{username}",
        "Medium":    f"https://medium.com/@{username}",
        "DevTo":     f"https://dev.to/{username}",
        "Pinterest": f"https://www.pinterest.com/{username}",
    }
    results = {}
    def check(name, url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                results[name] = {"url": url, "status": r.status, "found": r.status == 200}
        except urllib.request.HTTPError as e:
            results[name] = {"url": url, "status": e.code, "found": False}
        except Exception as e:
            results[name] = {"url": url, "status": "error", "found": False, "err": str(e)}
    ts = [threading.Thread(target=check, args=(n,u), daemon=True) for n,u in platforms.items()]
    for t in ts: t.start()
    for t in ts: t.join(timeout=8)
    return results

def breach_check(password):
    import hashlib
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    try:
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={"Add-Padding":"true"})
        with urllib.request.urlopen(req, timeout=6) as r:
            lines = r.read().decode().split("\r\n")
        for line in lines:
            if ":" in line:
                h, count = line.split(":")
                if h.strip() == suffix:
                    return {"pwned": True, "count": int(count), "note": "found in HIBP breach db"}
        return {"pwned": False, "count": 0}
    except Exception as e:
        return {"error": str(e)}

def social_links(name, year_hint=""):
    slug = name.lower().replace(" ","")
    slug2 = name.lower().replace(" ",".")
    slug3 = name.lower().replace(" ","_")
    bases = [slug, slug2, slug3]
    links = []
    for s in bases:
        links += [
            f"https://github.com/{s}",
            f"https://twitter.com/{s}",
            f"https://www.instagram.com/{s}",
            f"https://www.linkedin.com/in/{s}",
            f"https://www.reddit.com/user/{s}",
        ]
    if year_hint:
        links += [f"https://github.com/{slug}{year_hint}", f"https://twitter.com/{slug}{year_hint}"]
    return {"name": name, "generated_links": links}

def google_dork(target, dork_type="general"):
    templates = {
        "general":  [f'site:{target}', f'"{target}" filetype:pdf', f'"{target}" password', f'inurl:{target} admin'],
        "email":    [f'site:{target} "@{target}"', f'"{target}" email contact', f'inurl:mailto "{target}"'],
        "files":    [f'site:{target} filetype:sql', f'site:{target} filetype:env', f'site:{target} filetype:log', f'site:{target} filetype:bak'],
        "subdomains":[f'site:*.{target}', f'site:{target} -www'],
        "login":    [f'site:{target} inurl:login', f'site:{target} inurl:admin', f'site:{target} inurl:panel'],
    }
    dorks = templates.get(dork_type, templates["general"])
    return {
        "target": target,
        "type": dork_type,
        "dorks": dorks,
        "google_urls": [f"https://www.google.com/search?q={urllib.request.pathname2url(d)}" for d in dorks]
    }

def metadata_strip(filepath):
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(filepath)
        exif_data = img._getexif()
        if not exif_data:
            return {"file": filepath, "exif": "none found"}
        readable = {TAGS.get(k, k): str(v)[:100] for k, v in exif_data.items()}
        # strip
        clean = Image.new(img.mode, img.size)
        clean.putdata(list(img.getdata()))
        out_path = filepath.rsplit(".",1)[0] + "_clean." + filepath.rsplit(".",1)[-1]
        clean.save(out_path)
        return {"file": filepath, "exif": readable, "stripped_to": out_path}
    except ImportError:
        return {"error": "pip install pillow"}
    except Exception as e:
        return {"error": str(e)}

_timeline = []
def timeline_build(entry_type, value, note=""):
    import datetime
    _timeline.append({"ts": datetime.datetime.utcnow().isoformat()+"Z", "type": entry_type, "value": value, "note": note})
    return {"timeline": _timeline, "count": len(_timeline)}

# ─── CMD MENU ─────────────────────────────────────────────────────────────────

TOOLS_DOX = {
    "1":  ("ip_dox",          lambda: print(json.dumps(ip_dox(input("IP: ")), indent=2))),
    "2":  ("domain_dox",      lambda: print(json.dumps(domain_dox(input("domain: ")), indent=2))),
    "3":  ("email_validate",  lambda: print(json.dumps(email_validate(input("email: ")), indent=2))),
    "4":  ("phone_format",    lambda: print(json.dumps(phone_format(input("number: ")), indent=2))),
    "5":  ("username_hunt",   lambda: print(json.dumps(username_hunt(input("username: ")), indent=2))),
    "6":  ("breach_check",    lambda: print(json.dumps(breach_check(input("password: ")), indent=2))),
    "7":  ("social_links",    lambda: print(json.dumps(social_links(input("full name: "), input("year hint (blank=skip): ")), indent=2))),
    "8":  ("google_dork",     lambda: print(json.dumps(google_dork(input("target domain: "), input("type[general/email/files/subdomains/login]: ") or "general"), indent=2))),
    "9":  ("metadata_strip",  lambda: print(json.dumps(metadata_strip(input("image path: ")), indent=2))),
    "10": ("timeline_build",  lambda: print(json.dumps(timeline_build(input("type: "), input("value: "), input("note: ")), indent=2))),
}

def cmd_menu():
    print(BANNER); print(README)
    while True:
        print("\n  TOOLS:")
        for k,(name,_) in TOOLS_DOX.items():
            print(f"    [{k:>2}] {name}")
        print("    [ q] quit")
        c = input("\n  >> ").strip()
        if c == "q": break
        if c in TOOLS_DOX:
            try: TOOLS_DOX[c][1]()
            except Exception as e: print(f"  [!] {e}")

# ─── WEB ──────────────────────────────────────────────────────────────────────

DOX_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Akatsuki Dox</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d0010;color:#e0d0f0;font-family:'Courier New',monospace;min-height:100vh}
.header{background:linear-gradient(135deg,#1a0028,#2d0040);border-bottom:2px solid #c026d3;padding:20px 40px}
.header h1{color:#e879f9;font-size:1.8em;text-shadow:0 0 20px #c026d388}
.header p{color:#9d6aaa;margin-top:5px}
.container{display:flex;min-height:calc(100vh - 100px)}
.sidebar{width:260px;background:#0a000f;border-right:1px solid #3b0054;padding:20px}
.sidebar h3{color:#c026d3;margin-bottom:15px;font-size:.9em;letter-spacing:2px}
.tool-btn{display:block;width:100%;padding:10px 15px;margin:4px 0;background:#12001a;border:1px solid #3b0054;
          color:#d8b4fe;cursor:pointer;text-align:left;font-family:inherit;font-size:.85em;border-radius:4px;transition:all .2s}
.tool-btn:hover,.tool-btn.active{background:#3b0054;border-color:#c026d3;color:#e879f9}
.main{flex:1;padding:30px}
.card{background:#0a000f;border:1px solid #3b0054;border-radius:8px;padding:25px;margin-bottom:20px}
.card h2{color:#c026d3;margin-bottom:15px;font-size:1.1em}
.form-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px}
input[type=text]{background:#12001a;border:1px solid #4a0066;color:#e0d0f0;padding:8px 12px;border-radius:4px;font-family:inherit;font-size:.9em;min-width:180px}
input:focus{outline:none;border-color:#c026d3}
.btn{background:#c026d3;color:#0d0010;border:none;padding:9px 20px;border-radius:4px;cursor:pointer;font-family:inherit;font-weight:bold;font-size:.9em}
.btn:hover{background:#e879f9}
.output{background:#050008;border:1px solid #2d0040;border-radius:4px;padding:20px;min-height:120px;white-space:pre-wrap;font-size:.85em;color:#d8b4fe;max-height:500px;overflow-y:auto;margin-top:15px}
.loading{color:#c026d3;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
</style></head><body>
<div class="header">
  <h1>🔴 AKATSUKI — DOX ENGINE</h1>
  <p>"Pain knows everything about you." — 10 tools, full intel gathering.</p>
</div>
<div class="container">
<div class="sidebar">
  <h3>// TOOLS</h3>
  <button class="tool-btn active" onclick="showTool('ip_dox')">01 · ip dox</button>
  <button class="tool-btn" onclick="showTool('domain_dox')">02 · domain dox</button>
  <button class="tool-btn" onclick="showTool('email_validate')">03 · email validate</button>
  <button class="tool-btn" onclick="showTool('phone_format')">04 · phone format</button>
  <button class="tool-btn" onclick="showTool('username_hunt')">05 · username hunt</button>
  <button class="tool-btn" onclick="showTool('breach_check')">06 · breach check</button>
  <button class="tool-btn" onclick="showTool('social_links')">07 · social links</button>
  <button class="tool-btn" onclick="showTool('google_dork')">08 · google dork</button>
  <button class="tool-btn" onclick="showTool('metadata_strip')">09 · metadata strip</button>
  <button class="tool-btn" onclick="showTool('timeline_build')">10 · timeline build</button>
  <button class="tool-btn" onclick="showTool('readme')" style="margin-top:20px;border-color:#3b0054;color:#6b7280">README</button>
</div>
<div class="main">
  <div id="readme" class="card" style="display:none"><h2>// README</h2><pre id="readme-box" style="color:#9d6aaa;font-size:.82em;line-height:1.6"></pre></div>
  <div id="tool-panel" class="card">
    <h2 id="tool-title">// 01 · IP DOX</h2>
    <div id="tool-form"></div>
    <div id="output" class="output">— ready, enter target —</div>
  </div>
</div>
</div>
<script>
const tools={
  ip_dox:{title:"01 · IP DOX",fields:[{n:"ip",p:"e.g. 8.8.8.8"}]},
  domain_dox:{title:"02 · DOMAIN DOX",fields:[{n:"domain",p:"e.g. example.com"}]},
  email_validate:{title:"03 · EMAIL VALIDATE",fields:[{n:"email",p:"user@domain.com"}]},
  phone_format:{title:"04 · PHONE FORMAT",fields:[{n:"number",p:"+33612345678"}]},
  username_hunt:{title:"05 · USERNAME HUNT",fields:[{n:"username",p:"handle to search"}]},
  breach_check:{title:"06 · BREACH CHECK",fields:[{n:"password",p:"password to check"}]},
  social_links:{title:"07 · SOCIAL LINKS",fields:[{n:"name",p:"Full Name"},{n:"year_hint",p:"e.g. 99 (optional)"}]},
  google_dork:{title:"08 · GOOGLE DORK",fields:[{n:"target",p:"domain.com"},{n:"dork_type",p:"general/email/files/subdomains/login"}]},
  metadata_strip:{title:"09 · METADATA STRIP",fields:[{n:"filepath",p:"/path/to/image.jpg"}]},
  timeline_build:{title:"10 · TIMELINE BUILD",fields:[{n:"entry_type",p:"ip/domain/email"},{n:"value",p:"the value"},{n:"note",p:"optional note"}]},
};
let cur="ip_dox";
function showTool(name){
  document.querySelectorAll(".tool-btn").forEach(b=>b.classList.remove("active"));
  event.target.classList.add("active");
  if(name==="readme"){
    document.getElementById("tool-panel").style.display="none";
    document.getElementById("readme").style.display="block";
    fetch("/readme").then(r=>r.text()).then(t=>document.getElementById("readme-box").textContent=t);
    return;
  }
  document.getElementById("readme").style.display="none";
  document.getElementById("tool-panel").style.display="block";
  cur=name;const t=tools[name];
  document.getElementById("tool-title").textContent="// "+t.title;
  document.getElementById("tool-form").innerHTML=`<div class="form-row">${t.fields.map(f=>`<input type="text" id="f_${f.n}" placeholder="${f.n}: ${f.p}">`).join("")}<button class="btn" onclick="runTool()">▶ RUN</button></div>`;
  document.getElementById("output").textContent="— ready —";
}
async function runTool(){
  const t=tools[cur];const params={};
  t.fields.forEach(f=>{params[f.n]=document.getElementById("f_"+f.n).value});
  const out=document.getElementById("output");
  out.innerHTML='<span class="loading">[ gathering intel... ]</span>';
  try{
    const r=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tool:cur,params})});
    const d=await r.json();
    out.textContent=JSON.stringify(d.result,null,2)||d.error;
  }catch(e){out.textContent="error: "+e}
}
</script></body></html>"""

def run_web(port=5001):
    try: from flask import Flask, request, jsonify
    except ImportError: print("pip install flask"); sys.exit(1)
    app = Flask(__name__)

    @app.route("/") 
    def index(): return DOX_HTML

    @app.route("/readme")
    def readme(): return README

    @app.route("/run", methods=["POST"])
    def run():
        d = request.json; t = d["tool"]; p = d.get("params",{})
        try:
            dispatch = {
                "ip_dox":         lambda: ip_dox(p["ip"]),
                "domain_dox":     lambda: domain_dox(p["domain"]),
                "email_validate": lambda: email_validate(p["email"]),
                "phone_format":   lambda: phone_format(p["number"]),
                "username_hunt":  lambda: username_hunt(p["username"]),
                "breach_check":   lambda: breach_check(p["password"]),
                "social_links":   lambda: social_links(p["name"], p.get("year_hint","")),
                "google_dork":    lambda: google_dork(p["target"], p.get("dork_type","general")),
                "metadata_strip": lambda: metadata_strip(p["filepath"]),
                "timeline_build": lambda: timeline_build(p["entry_type"], p["value"], p.get("note","")),
            }
            return jsonify(result=dispatch[t]())
        except Exception as e:
            return jsonify(error=str(e))

    print(f"\n  [*] Akatsuki Dox — web UI at http://localhost:{port}")
    app.run(host="0.0.0.0", port=int(port), debug=False)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", action="store_true")
    ap.add_argument("--port", type=int, default=5001)
    args = ap.parse_args()
    if args.web: run_web(args.port)
    else: cmd_menu()