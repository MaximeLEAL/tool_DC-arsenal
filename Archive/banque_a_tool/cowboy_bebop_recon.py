# lang: Python 3.10+ | file: cowboy_bebop_recon.py
# deps: flask (pip install flask) — "whatever happens, happens."

import argparse, socket, subprocess, platform, os, sys, json, threading
from pathlib import Path

# ─── BANNER ───────────────────────────────────────────────────────────────────
BANNER = r"""
  ██████╗ ███████╗██████╗  ██████╗ ██████╗     ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
  ██╔══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
  ██████╔╝█████╗  ██████╔╝██║   ██║██████╔╝    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
  ██╔══██╗██╔══╝  ██╔══██╗██║   ██║██╔═══╝     ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
  ██████╔╝███████╗██████╔╝╚██████╔╝██║         ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝         ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
  "Whatever happens, happens." — Spike Spiegel  |  RECON SUITE v2
"""

README = """
╔══════════════════════════════════════════════════════════════╗
║           COWBOY BEBOP RECON — README                       ║
╠══════════════════════════════════════════════════════════════╣
║  USAGE CMD  : python cowboy_bebop_recon.py                  ║
║  USAGE WEB  : python cowboy_bebop_recon.py --web [--port N] ║
╠══════════════════════════════════════════════════════════════╣
║  TOOLS (10)                                                 ║
║  1.  portscan        — TCP connect scan, range configurable ║
║  2.  udpscan         — UDP probe top services               ║
║  3.  banner_grab     — raw TCP banner on any port           ║
║  4.  traceroute      — hop-by-hop path to target            ║
║  5.  ping_sweep      — ICMP sweep over /24 CIDR             ║
║  6.  os_detect       — TTL + banner OS fingerprint          ║
║  7.  whois_resolve   — reverse DNS + hostname chain         ║
║  8.  ssl_inspect     — TLS cert details (SAN, expiry, CN)   ║
║  9.  http_probe      — HTTP/S headers + status codes        ║
║  10. subnet_map      — enumerate live hosts in a subnet     ║
╠══════════════════════════════════════════════════════════════╣
║  DEPS : pip install flask                                   ║
║  NOTE : portscan large ranges → drop timeout to 0.1 on LAN ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─── TOOLS ────────────────────────────────────────────────────────────────────

def portscan(host, start=1, end=1024, timeout=0.4):
    results = []
    for port in range(int(start), int(end)+1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(float(timeout))
            if s.connect_ex((host, int(port))) == 0:
                results.append(port)
    return results

def udpscan(host, timeout=1.0):
    top_udp = {53:"DNS",67:"DHCP",69:"TFTP",123:"NTP",137:"NetBIOS",
               161:"SNMP",500:"IKE",514:"Syslog",1900:"SSDP",4500:"NAT-T"}
    results = {}
    for port, svc in top_udp.items():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(float(timeout))
            try:
                s.sendto(b"\x00", (host, port))
                s.recvfrom(128)
                results[port] = f"{svc} — open|filtered"
            except socket.timeout:
                results[port] = f"{svc} — open|filtered (no response)"
            except Exception:
                results[port] = f"{svc} — closed"
    return results

def banner_grab(host, port, timeout=3.0):
    try:
        with socket.socket() as s:
            s.settimeout(float(timeout))
            s.connect((host, int(port)))
            s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            return s.recv(2048).decode(errors="replace")
    except Exception as e:
        return f"error: {e}"

def traceroute(host, max_hops=20):
    system = platform.system()
    if system == "Windows":
        cmd = ["tracert", "-d", "-h", str(max_hops), host]
    else:
        cmd = ["traceroute", "-n", "-m", str(max_hops), host]
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=30).decode(errors="replace")
        return out
    except Exception as e:
        return f"error: {e}"

def ping_sweep(subnet_base):
    # subnet_base like "192.168.1" → sweeps .1–.254
    alive = []
    def ping_one(ip):
        param = "-n" if platform.system()=="Windows" else "-c"
        r = subprocess.run(["ping", param, "1", "-W", "1", ip],
                           capture_output=True, timeout=3)
        if r.returncode == 0:
            alive.append(ip)
    threads = []
    for i in range(1, 255):
        ip = f"{subnet_base}.{i}"
        t = threading.Thread(target=ping_one, args=(ip,), daemon=True)
        threads.append(t); t.start()
    for t in threads:
        t.join(timeout=4)
    return sorted(alive, key=lambda x: int(x.split(".")[-1]))

def os_detect(host, port=80):
    try:
        with socket.socket() as s:
            s.settimeout(2)
            s.connect((host, int(port)))
            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(512).decode(errors="replace")
    except Exception:
        banner = ""
    try:
        pkt = subprocess.check_output(
            ["ping", "-c" if platform.system()!="Windows" else "-n", "1", host],
            stderr=subprocess.DEVNULL).decode(errors="replace")
        ttl_line = [l for l in pkt.split("\n") if "ttl" in l.lower() or "TTL" in l]
        ttl = int([x for x in (ttl_line[0] if ttl_line else "").split() if "ttl" in x.lower()][0].split("=")[-1]) if ttl_line else 0
    except Exception:
        ttl = 0
    guess = "unknown"
    if ttl:
        if ttl <= 64: guess = "Linux / macOS"
        elif ttl <= 128: guess = "Windows"
        else: guess = "Network device (Cisco/Juniper)"
    return {"ttl": ttl, "os_guess": guess, "banner_snippet": banner[:200]}

def whois_resolve(host):
    try:
        ip = socket.gethostbyname(host)
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception as e:
        return {"error": str(e)}
    return {"input": host, "resolved_ip": ip, "reverse_hostname": hostname}

def ssl_inspect(host, port=443):
    import ssl, datetime
    ctx = ssl.create_default_context()
    try:
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, int(port)))
            cert = s.getpeercert()
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer  = dict(x[0] for x in cert.get("issuer", []))
        san     = [v for _, v in cert.get("subjectAltName", [])]
        expiry  = cert.get("notAfter", "unknown")
        return {"CN": subject.get("commonName"), "issuer": issuer.get("organizationName"),
                "SAN": san, "expires": expiry}
    except Exception as e:
        return {"error": str(e)}

def http_probe(host, paths=None):
    import urllib.request
    paths = paths or ["/", "/robots.txt", "/sitemap.xml", "/.well-known/security.txt"]
    results = {}
    for path in paths:
        for scheme in ["https", "http"]:
            url = f"{scheme}://{host}{path}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent":"BebopRecon/2.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    results[url] = {"status": r.status, "server": r.headers.get("Server","?"),
                                    "content_type": r.headers.get("Content-Type","?")}
                break
            except urllib.request.HTTPError as e:
                results[url] = {"status": e.code}; break
            except Exception:
                results[url] = {"status": "error"}
    return results

def subnet_map(subnet_base, port=80, timeout=0.3):
    alive = []
    def probe(ip):
        with socket.socket() as s:
            s.settimeout(float(timeout))
            if s.connect_ex((ip, int(port))) == 0:
                alive.append(ip)
    threads = [threading.Thread(target=probe, args=(f"{subnet_base}.{i}",), daemon=True) for i in range(1,255)]
    for t in threads: t.start()
    for t in threads: t.join(timeout=2)
    return sorted(alive, key=lambda x: int(x.split(".")[-1]))

# ─── CMD MENU ─────────────────────────────────────────────────────────────────

TOOLS = {
    "1":  ("portscan",      "TCP port scan",           lambda: (lambda h,s,e,t: print(f"\n[OPEN] {portscan(h,s,e,t)}"))(
                                input("host: "), input("start[1]: ") or 1, input("end[1024]: ") or 1024, input("timeout[0.4]: ") or 0.4)),
    "2":  ("udpscan",       "UDP top-10 probe",        lambda: print(json.dumps(udpscan(input("host: ")), indent=2))),
    "3":  ("banner_grab",   "TCP banner grab",         lambda: print(banner_grab(input("host: "), input("port: ")))),
    "4":  ("traceroute",    "hop-by-hop trace",        lambda: print(traceroute(input("host: ")))),
    "5":  ("ping_sweep",    "ICMP /24 sweep",          lambda: print(ping_sweep(input("subnet base (e.g. 192.168.1): ")))),
    "6":  ("os_detect",     "TTL OS fingerprint",      lambda: print(json.dumps(os_detect(input("host: ")), indent=2))),
    "7":  ("whois_resolve", "reverse DNS",             lambda: print(json.dumps(whois_resolve(input("host/ip: ")), indent=2))),
    "8":  ("ssl_inspect",   "TLS cert details",        lambda: print(json.dumps(ssl_inspect(input("host: ")), indent=2))),
    "9":  ("http_probe",    "HTTP header probe",       lambda: print(json.dumps(http_probe(input("host: ")), indent=2))),
    "10": ("subnet_map",    "live hosts in subnet",    lambda: print(subnet_map(input("subnet base: "), input("port[80]: ") or 80))),
}

def cmd_menu():
    print(BANNER)
    print(README)
    while True:
        print("\n  TOOLS:")
        for k,(name,desc,_) in TOOLS.items():
            print(f"    [{k:>2}] {name:<18} — {desc}")
        print("    [ q] quit")
        c = input("\n  >> ").strip()
        if c == "q": break
        if c in TOOLS:
            try: TOOLS[c][2]()
            except Exception as e: print(f"  [!] {e}")

# ─── WEB SERVER ───────────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Cowboy Bebop Recon</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0a0f;color:#e0e0e0;font-family:'Courier New',monospace;min-height:100vh}}
.header{{background:linear-gradient(135deg,#1a0a2e,#0d1b2a);border-bottom:2px solid #f4a01a;padding:20px 40px}}
.header h1{{color:#f4a01a;font-size:1.8em;text-shadow:0 0 20px #f4a01a88}}
.header p{{color:#8899aa;margin-top:5px}}
.container{{display:flex;min-height:calc(100vh - 100px)}}
.sidebar{{width:260px;background:#0d1117;border-right:1px solid #1f2d3d;padding:20px}}
.sidebar h3{{color:#f4a01a;margin-bottom:15px;font-size:.9em;letter-spacing:2px}}
.tool-btn{{display:block;width:100%;padding:10px 15px;margin:4px 0;background:#111827;border:1px solid #1f3a5f;
           color:#7dd3fc;cursor:pointer;text-align:left;font-family:inherit;font-size:.85em;
           border-radius:4px;transition:all .2s}}
.tool-btn:hover,.tool-btn.active{{background:#1e3a5f;border-color:#f4a01a;color:#f4a01a}}
.main{{flex:1;padding:30px}}
.card{{background:#0d1117;border:1px solid #1f2d3d;border-radius:8px;padding:25px;margin-bottom:20px}}
.card h2{{color:#f4a01a;margin-bottom:15px;font-size:1.1em}}
.form-row{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px}}
input[type=text],input[type=number]{{background:#111827;border:1px solid #374151;color:#e0e0e0;
  padding:8px 12px;border-radius:4px;font-family:inherit;font-size:.9em;min-width:180px}}
input:focus{{outline:none;border-color:#f4a01a}}
.btn{{background:#f4a01a;color:#0a0a0f;border:none;padding:9px 20px;border-radius:4px;
      cursor:pointer;font-family:inherit;font-weight:bold;font-size:.9em}}
.btn:hover{{background:#fbbf24}}
.output{{background:#050a0f;border:1px solid #0f2a3f;border-radius:4px;padding:20px;
         min-height:120px;white-space:pre-wrap;font-size:.85em;color:#7dd3fc;
         max-height:500px;overflow-y:auto;margin-top:15px}}
.loading{{color:#f4a01a;animation:blink 1s infinite}}
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.tag{{display:inline-block;background:#1e3a5f;color:#7dd3fc;padding:2px 8px;border-radius:3px;
      font-size:.75em;margin:2px}}
#readme-box{{color:#8899aa;font-size:.82em;line-height:1.6}}
</style>
</head>
<body>
<div class="header">
  <h1>🚀 COWBOY BEBOP — RECON SUITE</h1>
  <p>"Whatever happens, happens." — 10 tools, one bench, no hesitation.</p>
</div>
<div class="container">
  <div class="sidebar">
    <h3>// TOOLS</h3>
    <button class="tool-btn active" onclick="showTool('portscan')">01 · portscan</button>
    <button class="tool-btn" onclick="showTool('udpscan')">02 · udpscan</button>
    <button class="tool-btn" onclick="showTool('banner_grab')">03 · banner grab</button>
    <button class="tool-btn" onclick="showTool('traceroute')">04 · traceroute</button>
    <button class="tool-btn" onclick="showTool('ping_sweep')">05 · ping sweep</button>
    <button class="tool-btn" onclick="showTool('os_detect')">06 · os detect</button>
    <button class="tool-btn" onclick="showTool('whois_resolve')">07 · whois resolve</button>
    <button class="tool-btn" onclick="showTool('ssl_inspect')">08 · ssl inspect</button>
    <button class="tool-btn" onclick="showTool('http_probe')">09 · http probe</button>
    <button class="tool-btn" onclick="showTool('subnet_map')">10 · subnet map</button>
    <button class="tool-btn" onclick="showTool('readme')" style="margin-top:20px;border-color:#374151;color:#6b7280">README</button>
  </div>
  <div class="main">
    <div id="readme" class="card" style="display:none">
      <h2>// README</h2>
      <pre id="readme-box"></pre>
    </div>
    <div id="tool-panel" class="card">
      <h2 id="tool-title">// 01 · PORTSCAN</h2>
      <div id="tool-form"></div>
      <div id="output" class="output">— ready, name the target —</div>
    </div>
  </div>
</div>
<script>
const tools = {
  portscan:     {title:"01 · PORTSCAN",     fields:[{n:"host",p:"e.g. 192.168.1.1"},{n:"start",p:"1"},{n:"end",p:"1024"},{n:"timeout",p:"0.4"}]},
  udpscan:      {title:"02 · UDP SCAN",     fields:[{n:"host",p:"target IP/host"}]},
  banner_grab:  {title:"03 · BANNER GRAB",  fields:[{n:"host",p:"target"},{n:"port",p:"80"}]},
  traceroute:   {title:"04 · TRACEROUTE",   fields:[{n:"host",p:"target"}]},
  ping_sweep:   {title:"05 · PING SWEEP",   fields:[{n:"subnet_base",p:"e.g. 192.168.1"}]},
  os_detect:    {title:"06 · OS DETECT",    fields:[{n:"host",p:"target"},{n:"port",p:"80"}]},
  whois_resolve:{title:"07 · WHOIS RESOLVE",fields:[{n:"host",p:"domain or IP"}]},
  ssl_inspect:  {title:"08 · SSL INSPECT",  fields:[{n:"host",p:"domain"},{n:"port",p:"443"}]},
  http_probe:   {title:"09 · HTTP PROBE",   fields:[{n:"host",p:"domain or IP"}]},
  subnet_map:   {title:"10 · SUBNET MAP",   fields:[{n:"subnet_base",p:"192.168.1"},{n:"port",p:"80"}]},
};
let currentTool = "portscan";
function showTool(name) {
  document.querySelectorAll(".tool-btn").forEach(b=>b.classList.remove("active"));
  event.target.classList.add("active");
  if(name==="readme"){
    document.getElementById("tool-panel").style.display="none";
    document.getElementById("readme").style.display="block";
    fetch("/readme").then(r=>r.text()).then(t=>{document.getElementById("readme-box").textContent=t});
    return;
  }
  document.getElementById("readme").style.display="none";
  document.getElementById("tool-panel").style.display="block";
  currentTool=name;
  const t=tools[name];
  document.getElementById("tool-title").textContent="// "+t.title;
  const form=document.getElementById("tool-form");
  form.innerHTML=`<div class="form-row">${t.fields.map(f=>`<input type="text" id="f_${f.n}" placeholder="${f.n}: ${f.p}">`).join("")}<button class="btn" onclick="runTool()">▶ RUN</button></div>`;
  document.getElementById("output").textContent="— ready —";
}
async function runTool(){
  const t=tools[currentTool];
  const params={};
  t.fields.forEach(f=>{params[f.n]=document.getElementById("f_"+f.n).value});
  const out=document.getElementById("output");
  out.innerHTML='<span class="loading">[ running... ]</span>';
  try{
    const r=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tool:currentTool,params})});
    const d=await r.json();
    out.textContent=JSON.stringify(d.result,null,2)||d.error||"done.";
  }catch(e){out.textContent="error: "+e}
}
document.addEventListener("keydown",e=>{if(e.key==="Enter")runTool()});
</script>
</body>
</html>"""

def run_web(port=5000):
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("  [!] flask not found — pip install flask"); sys.exit(1)
    app = Flask(__name__)

    @app.route("/")
    def index(): return HTML_TEMPLATE

    @app.route("/readme")
    def readme(): return README

    @app.route("/run", methods=["POST"])
    def run():
        data = request.json
        tool = data.get("tool")
        p    = data.get("params", {})
        try:
            if tool == "portscan":
                r = portscan(p["host"], p.get("start",1), p.get("end",1024), p.get("timeout",0.4))
                return jsonify(result=r)
            elif tool == "udpscan":
                return jsonify(result=udpscan(p["host"]))
            elif tool == "banner_grab":
                return jsonify(result=banner_grab(p["host"], p["port"]))
            elif tool == "traceroute":
                return jsonify(result=traceroute(p["host"]))
            elif tool == "ping_sweep":
                return jsonify(result=ping_sweep(p["subnet_base"]))
            elif tool == "os_detect":
                return jsonify(result=os_detect(p["host"], p.get("port",80)))
            elif tool == "whois_resolve":
                return jsonify(result=whois_resolve(p["host"]))
            elif tool == "ssl_inspect":
                return jsonify(result=ssl_inspect(p["host"], p.get("port",443)))
            elif tool == "http_probe":
                return jsonify(result=http_probe(p["host"]))
            elif tool == "subnet_map":
                return jsonify(result=subnet_map(p["subnet_base"], p.get("port",80)))
            else:
                return jsonify(error="unknown tool")
        except Exception as e:
            return jsonify(error=str(e))

    print(f"\n  [*] Cowboy Bebop Recon — web UI at http://localhost:{port}")
    app.run(host="0.0.0.0", port=int(port), debug=False)

# ─── ENTRY ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--web", action="store_true")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()
    if args.web: run_web(args.port)
    else: cmd_menu()