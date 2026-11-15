# lang: Python 3.10+ | file: quirk_osint.py
# deps: pip install flask

import argparse, socket, subprocess, platform, urllib.request, urllib.parse, json, re, sys, threading

BANNER = r"""
   ██████╗ ██╗   ██╗██╗██████╗ ██╗  ██╗     ██████╗ ███████╗██╗███╗   ██╗████████╗
  ██╔═══██╗██║   ██║██║██╔══██╗██║ ██╔╝    ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
  ██║   ██║██║   ██║██║██████╔╝█████╔╝     ██║   ██║███████╗██║██╔██╗ ██║   ██║
  ██║▄▄ ██║██║   ██║██║██╔══██╗██╔═██╗     ██║   ██║╚════██║██║██║╚██╗██║   ██║
  ╚██████╔╝╚██████╔╝██║██║  ██║██║  ██╗    ╚██████╔╝███████║██║██║ ╚████║   ██║
   ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝
  "Plus Ultra — right into your data."  OSINT SUITE v2
"""

README = """
╔══════════════════════════════════════════════════════════════╗
║              QUIRK OSINT — README                           ║
╠══════════════════════════════════════════════════════════════╣
║  USAGE CMD  : python quirk_osint.py                         ║
║  USAGE WEB  : python quirk_osint.py --web [--port N]        ║
╠══════════════════════════════════════════════════════════════╣
║  TOOLS (10)                                                 ║
║  1.  dns_full        — A/MX/NS/TXT/CNAME/SOA records        ║
║  2.  subdomain_enum  — brute subdomain enumeration          ║
║  3.  cert_transparency — crt.sh cert log search             ║
║  4.  shodan_dork     — build Shodan search queries          ║
║  5.  wayback_check   — check Wayback Machine snapshots      ║
║  6.  github_recon    — public github user/org intel         ║
║  7.  pastebin_hunt   — search Pastebin via Google dork      ║
║  8.  tech_detect     — detect CMS/framework from headers    ║
║  9.  ip_range_owner  — ARIN/RIPE ASN whois lookup           ║
║  10. org_intel       — combine DNS + cert + tech in one     ║
╠══════════════════════════════════════════════════════════════╣
║  DEPS : pip install flask                                   ║
╚══════════════════════════════════════════════════════════════╝
"""

SUBDOMAINS = ["www","mail","remote","blog","webmail","server","ns1","ns2","smtp","secure",
              "vpn","m","shop","ftp","api","dev","staging","test","portal","admin","cdn","static"]

def dns_full(domain):
    out = {"domain": domain}
    try: out["A"] = socket.gethostbyname(domain)
    except Exception as e: out["A"] = f"error: {e}"
    for rec in ["MX","NS","TXT","CNAME","SOA"]:
        try:
            if platform.system()=="Windows":
                cmd=["nslookup",f"-type={rec}",domain]
            else:
                cmd=["dig","+short",rec,domain]
            r=subprocess.check_output(cmd,stderr=subprocess.DEVNULL,timeout=5).decode(errors="replace").strip()
            out[rec]=r[:300] if r else "none"
        except Exception as e: out[rec]=f"error: {e}"
    return out

def subdomain_enum(domain):
    found = []
    def probe(sub):
        fqdn = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(fqdn)
            found.append({"subdomain": fqdn, "ip": ip})
        except: pass
    ts=[threading.Thread(target=probe,args=(s,),daemon=True) for s in SUBDOMAINS]
    for t in ts: t.start()
    for t in ts: t.join(timeout=5)
    return sorted(found, key=lambda x: x["subdomain"])

def cert_transparency(domain):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"QuirkOSINT/2.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        seen = set()
        results = []
        for entry in data[:50]:
            name = entry.get("name_value","").strip()
            for n in name.split("\n"):
                n = n.strip()
                if n and n not in seen:
                    seen.add(n)
                    results.append({"name": n, "issuer": entry.get("issuer_name","")[:60], "logged": entry.get("entry_timestamp","")})
        return results
    except Exception as e: return {"error": str(e)}

def shodan_dork(target, category="general"):
    dorks = {
        "general": [f"hostname:{target}",f'org:"{target}"',f'ssl.cert.subject.cn:"{target}"'],
        "iot":     [f"hostname:{target} port:23",f"hostname:{target} port:21",f'hostname:{target} "default password"'],
        "web":     [f"hostname:{target} http.title:admin",f"hostname:{target} http.status:200",f"hostname:{target} port:8080"],
        "vuln":    [f"hostname:{target} vuln:CVE-2021-44228",f"hostname:{target} vuln:CVE-2017-0144"],
    }
    selected = dorks.get(category, dorks["general"])
    return {"target":target,"category":category,"queries":selected,
            "shodan_urls":[f"https://www.shodan.io/search?query={urllib.parse.quote(q)}" for q in selected]}

def wayback_check(url):
    if not url.startswith("http"): url = "http://" + url
    api = f"https://archive.org/wayback/available?url={urllib.parse.quote(url)}"
    try:
        with urllib.request.urlopen(api, timeout=8) as r:
            data = json.loads(r.read().decode())
        snap = data.get("archived_snapshots",{}).get("closest",{})
        return {"url": url, "available": snap.get("available", False),
                "snapshot_url": snap.get("url","none"), "timestamp": snap.get("timestamp","none")}
    except Exception as e: return {"error": str(e)}

def github_recon(username_or_org):
    out = {}
    for endpoint, key in [
        (f"https://api.github.com/users/{username_or_org}", "user"),
        (f"https://api.github.com/users/{username_or_org}/repos?per_page=10&sort=updated", "repos"),
    ]:
        try:
            req = urllib.request.Request(endpoint, headers={"User-Agent":"QuirkOSINT/2.0","Accept":"application/vnd.github.v3+json"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            if key == "user":
                out["user"] = {k: data.get(k) for k in ["login","name","company","blog","location","email","public_repos","followers","created_at"]}
            else:
                out["repos"] = [{"name":d["name"],"stars":d["stargazers_count"],"lang":d["language"],"updated":d["updated_at"]} for d in data]
        except Exception as e: out[key] = {"error": str(e)}
    return out

def pastebin_hunt(query):
    dork = f'site:pastebin.com "{query}"'
    url = f"https://www.google.com/search?q={urllib.parse.quote(dork)}&num=20"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode(errors="replace")
        links = re.findall(r'href="(https://pastebin\.com/[^"&]+)"', html)
        return {"query": query, "dork": dork, "results": list(set(links))[:20]}
    except Exception as e: return {"error": str(e)}

def tech_detect(host):
    if not host.startswith("http"): host = "https://" + host
    sigs = {
        "WordPress":   ["wp-content","wp-includes","wordpress"],
        "Drupal":      ["drupal","sites/default"],
        "Joomla":      ["joomla","com_content"],
        "React":       ["__NEXT_DATA__","react","_next"],
        "Angular":     ["ng-version","angular"],
        "Vue":         ["__vue__","vue.js"],
        "Laravel":     ["laravel_session","laravel"],
        "Django":      ["csrfmiddlewaretoken","django"],
        "ASP.NET":     ["X-Powered-By: ASP","__VIEWSTATE","asp.net"],
        "PHP":         ["X-Powered-By: PHP","PHPSESSID"],
        "Nginx":       ["nginx"],
        "Apache":      ["Apache"],
        "Cloudflare":  ["cf-ray","cloudflare"],
    }
    try:
        req = urllib.request.Request(host, headers={"User-Agent":"QuirkOSINT/2.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            body = r.read(8192).decode(errors="replace")
            headers_str = str(dict(r.headers))
        combined = body + headers_str
        detected = {tech: True for tech, keywords in sigs.items() if any(k.lower() in combined.lower() for k in keywords)}
        return {"host": host, "detected": detected, "server": dict(r.headers).get("Server","unknown")}
    except Exception as e: return {"error": str(e)}

def ip_range_owner(ip_or_asn):
    url = f"https://rdap.arin.net/registry/ip/{ip_or_asn}" if not ip_or_asn.upper().startswith("AS") else f"https://rdap.arin.net/registry/autnum/{ip_or_asn[2:]}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"QuirkOSINT/2.0","Accept":"application/json"})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode())
        return {"name": data.get("name"), "handle": data.get("handle"),
                "type": data.get("type"), "country": data.get("country"),
                "startAddress": data.get("startAddress"), "endAddress": data.get("endAddress")}
    except Exception as e: return {"error": str(e)}

def org_intel(domain):
    return {
        "dns": dns_full(domain),
        "subdomains": subdomain_enum(domain),
        "certs": cert_transparency(domain)[:10],
        "tech": tech_detect(domain),
        "wayback": wayback_check(domain),
    }

TOOLS_OSINT = {
    "1":  ("dns_full",           lambda: print(json.dumps(dns_full(input("domain: ")), indent=2))),
    "2":  ("subdomain_enum",     lambda: print(json.dumps(subdomain_enum(input("domain: ")), indent=2))),
    "3":  ("cert_transparency",  lambda: print(json.dumps(cert_transparency(input("domain: ")), indent=2))),
    "4":  ("shodan_dork",        lambda: print(json.dumps(shodan_dork(input("target: "), input("category[general/iot/web/vuln]: ") or "general"), indent=2))),
    "5":  ("wayback_check",      lambda: print(json.dumps(wayback_check(input("url: ")), indent=2))),
    "6":  ("github_recon",       lambda: print(json.dumps(github_recon(input("github username/org: ")), indent=2))),
    "7":  ("pastebin_hunt",      lambda: print(json.dumps(pastebin_hunt(input("search query: ")), indent=2))),
    "8":  ("tech_detect",        lambda: print(json.dumps(tech_detect(input("host: ")), indent=2))),
    "9":  ("ip_range_owner",     lambda: print(json.dumps(ip_range_owner(input("IP or ASN (e.g. AS15169): ")), indent=2))),
    "10": ("org_intel",          lambda: print(json.dumps(org_intel(input("domain: ")), indent=2))),
}

def cmd_menu():
    print(BANNER); print(README)
    while True:
        print("\n  TOOLS:")
        for k,(name,_) in TOOLS_OSINT.items(): print(f"    [{k:>2}] {name}")
        print("    [ q] quit")
        c = input("\n  >> ").strip()
        if c == "q": break
        if c in TOOLS_OSINT:
            try: TOOLS_OSINT[c][1]()
            except Exception as e: print(f"  [!] {e}")

OSINT_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Quirk OSINT</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#001a0d;color:#d1fae5;font-family:'Courier New',monospace;min-height:100vh}
.header{background:linear-gradient(135deg,#001a0d,#003320);border-bottom:2px solid #10b981;padding:20px 40px}
.header h1{color:#6ee7b7;font-size:1.8em;text-shadow:0 0 20px #10b98188}
.header p{color:#4a8a6a;margin-top:5px}
.container{display:flex;min-height:calc(100vh - 100px)}
.sidebar{width:260px;background:#000f07;border-right:1px solid #0a3d1f;padding:20px}
.sidebar h3{color:#10b981;margin-bottom:15px;font-size:.9em;letter-spacing:2px}
.tool-btn{display:block;width:100%;padding:10px 15px;margin:4px 0;background:#001a0d;border:1px solid #0a3d1f;
          color:#6ee7b7;cursor:pointer;text-align:left;font-family:inherit;font-size:.85em;border-radius:4px;transition:all .2s}
.tool-btn:hover,.tool-btn.active{background:#0a3d1f;border-color:#10b981;color:#a7f3d0}
.main{flex:1;padding:30px}
.card{background:#000f07;border:1px solid #0a3d1f;border-radius:8px;padding:25px;margin-bottom:20px}
.card h2{color:#10b981;margin-bottom:15px;font-size:1.1em}
.form-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px}
input[type=text]{background:#001a0d;border:1px solid #145a32;color:#d1fae5;padding:8px 12px;border-radius:4px;font-family:inherit;font-size:.9em;min-width:200px}
input:focus{outline:none;border-color:#10b981}
.btn{background:#10b981;color:#001a0d;border:none;padding:9px 20px;border-radius:4px;cursor:pointer;font-family:inherit;font-weight:bold;font-size:.9em}
.btn:hover{background:#6ee7b7}
.output{background:#00080a;border:1px solid #0a3d1f;border-radius:4px;padding:20px;min-height:120px;white-space:pre-wrap;font-size:.85em;color:#6ee7b7;max-height:500px;overflow-y:auto;margin-top:15px}
.loading{color:#10b981;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
</style></head><body>
<div class="header">
  <h1>⚡ QUIRK OSINT — PLUS ULTRA</h1>
  <p>"Plus Ultra — right into your data." — 10 tools, full open-source intel.</p>
</div>
<div class="container">
<div class="sidebar"><h3>// TOOLS</h3>
  <button class="tool-btn active" onclick="showTool('dns_full')">01 · dns full</button>
  <button class="tool-btn" onclick="showTool('subdomain_enum')">02 · subdomain enum</button>
  <button class="tool-btn" onclick="showTool('cert_transparency')">03 · cert transparency</button>
  <button class="tool-btn" onclick="showTool('shodan_dork')">04 · shodan dork</button>
  <button class="tool-btn" onclick="showTool('wayback_check')">05 · wayback check</button>
  <button class="tool-btn" onclick="showTool('github_recon')">06 · github recon</button>
  <button class="tool-btn" onclick="showTool('pastebin_hunt')">07 · pastebin hunt</button>
  <button class="tool-btn" onclick="showTool('tech_detect')">08 · tech detect</button>
  <button class="tool-btn" onclick="showTool('ip_range_owner')">09 · ip range owner</button>
  <button class="tool-btn" onclick="showTool('org_intel')">10 · org intel</button>
  <button class="tool-btn" onclick="showTool('readme')" style="margin-top:20px;border-color:#0a3d1f;color:#6b7280">README</button>
</div>
<div class="main">
  <div id="readme" class="card" style="display:none"><h2>// README</h2><pre id="readme-box" style="color:#4a8a6a;font-size:.82em;line-height:1.6"></pre></div>
  <div id="tool-panel" class="card">
    <h2 id="tool-title">// 01 · DNS FULL</h2>
    <div id="tool-form"></div>
    <div id="output" class="output">— ready —</div>
  </div>
</div></div>
<script>
const tools={
  dns_full:{title:"01 · DNS FULL",fields:[{n:"domain",p:"example.com"}]},
  subdomain_enum:{title:"02 · SUBDOMAIN ENUM",fields:[{n:"domain",p:"example.com"}]},
  cert_transparency:{title:"03 · CERT TRANSPARENCY",fields:[{n:"domain",p:"example.com"}]},
  shodan_dork:{title:"04 · SHODAN DORK",fields:[{n:"target",p:"example.com"},{n:"category",p:"general/iot/web/vuln"}]},
  wayback_check:{title:"05 · WAYBACK CHECK",fields:[{n:"url",p:"example.com"}]},
  github_recon:{title:"06 · GITHUB RECON",fields:[{n:"username_or_org",p:"torvalds"}]},
  pastebin_hunt:{title:"07 · PASTEBIN HUNT",fields:[{n:"query",p:"@example.com password"}]},
  tech_detect:{title:"08 · TECH DETECT",fields:[{n:"host",p:"example.com"}]},
  ip_range_owner:{title:"09 · IP RANGE OWNER",fields:[{n:"ip_or_asn",p:"8.8.8.8 or AS15169"}]},
  org_intel:{title:"10 · ORG INTEL",fields:[{n:"domain",p:"example.com"}]},
};
let cur="dns_full";
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
  t.fields.forEach(f=>{params[f.n]=document.getElementById("f_"+f.n)?.value||""});
  const out=document.getElementById("output");
  out.innerHTML='<span class="loading">[ gathering intel... ]</span>';
  try{
    const r=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tool:cur,params})});
    const d=await r.json();
    out.textContent=JSON.stringify(d.result,null,2)||d.error;
  }catch(e){out.textContent="error: "+e}
}
</script></body></html>"""

def run_web(port=5003):
    try: from flask import Flask, request, jsonify
    except ImportError: print("pip install flask"); sys.exit(1)
    app = Flask(__name__)
    @app.route("/") 
    def index(): return OSINT_HTML
    @app.route("/readme")
    def readme(): return README
    @app.route("/run", methods=["POST"])
    def run():
        d=request.json; t=d["tool"]; p=d.get("params",{})
        try:
            dispatch={
                "dns_full":          lambda: dns_full(p["domain"]),
                "subdomain_enum":    lambda: subdomain_enum(p["domain"]),
                "cert_transparency": lambda: cert_transparency(p["domain"]),
                "shodan_dork":       lambda: shodan_dork(p["target"],p.get("category","general")),
                "wayback_check":     lambda: wayback_check(p["url"]),
                "github_recon":      lambda: github_recon(p["username_or_org"]),
                "pastebin_hunt":     lambda: pastebin_hunt(p["query"]),
                "tech_detect":       lambda: tech_detect(p["host"]),
                "ip_range_owner":    lambda: ip_range_owner(p["ip_or_asn"]),
                "org_intel":         lambda: org_intel(p["domain"]),
            }
            return jsonify(result=dispatch[t]())
        except Exception as e: return jsonify(error=str(e))
    print(f"\n  [*] Quirk OSINT — web UI at http://localhost:{port}")
    app.run(host="0.0.0.0", port=int(port), debug=False)

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--web",action="store_true"); ap.add_argument("--port",type=int,default=5003)
    args=ap.parse_args()
    if args.web: run_web(args.port)
    else: cmd_menu()