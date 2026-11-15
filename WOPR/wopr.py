#!/usr/bin/env python3
# language: Python 3, file: wopr.py, target: macOS
# W.O.P.R. — SHALL WE PLAY A GAME? · powered by Maxime Leal
# L'auto-lab : une commande qui construit, demarre et note un CTF complet (hors Docker).
# Usage: wopr.py play | serve | destroy
import os, sys, json, time, subprocess, threading, http.server, sqlite3, random

LAB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WOPR_Lab")
FLAG_IDS = ["ALPHA", "BRAVO", "CHARLIE", "DELTA"]

def build():
    os.makedirs(os.path.join(LAB, "flags"), exist_ok=True)
    flags = {}
    for fid in FLAG_IDS:
        f = f"FLAG{{{fid}-{random.randint(1000,9999)}}}"
        flags[fid] = f
        open(os.path.join(LAB, "flags", f"{fid}.txt"), "w").write(f)
    json.dump(flags, open(os.path.join(LAB, "scoreboard.json"), "w"), indent=1)

    # serveur vulnerable : SQLi, path traversal, upload arbitraire, RCE shell
    vuln = '''#!/usr/bin/env python3
# WOPR target - serveur volontairement vulnérable (LAB, localhost:8090)
import http.server, sqlite3, os, urllib.parse, subprocess
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs
FLAG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flags")
con = sqlite3.connect(":memory:")
con.execute("create table users (id integer, name text, pass text)")
con.execute("insert into users values (1, 'admin', 'im_a_teapot')")
con.execute("insert into users values (2, 'wopr', 'shall_we_play')")

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlparse(self.path); q = urllib.parse.parse_qs(u.query)
        p = u.path
        if p == "/":
            self.send_response(200); self.end_headers()
            self.wfile.write("<h1>WOPR CTF TARGET</h1><p>/login?u=&p= (SQLi) · /files?f= (traversal) · /cmd?c= (RCE)</p>".encode())
        elif p == "/login":
            uname = q.get("u", [""])[0]
            rows = con.execute(f"select name, pass from users where name = '{uname}'").fetchall()
            if rows:
                self.send_response(200); self.end_headers()
                self.wfile.write(f"[SQL OK] {rows}".encode())
            else:
                flag = open(os.path.join(FLAG_PATH, "ALPHA.txt")).read()
                self.send_response(200); self.end_headers()
                self.wfile.write(f"[SQL ERROR] mais le flag de la base est : {flag}".encode())
        elif p == "/files":
            f = q.get("f", [""])[0]
            full = os.path.join(FLAG_PATH, f)
            if os.path.exists(full):
                self.send_response(200); self.end_headers()
                self.wfile.write(open(full).read().encode())
            else:
                self.send_response(200); self.end_headers()
                self.wfile.write("[TRAVERSAL] path inconnu — essaie la marche arriere".encode())
        elif p == "/cmd":
            c = q.get("c", [""])[0]
            out = subprocess.run(c, shell=True, capture_output=True).stdout.decode()
            self.send_response(200); self.end_headers()
            self.wfile.write(f"[RCE] {out}".encode())
        else:
            self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

http.server.HTTPServer(("0.0.0.0", 8090), H).serve_forever()
'''
    open(os.path.join(LAB, "vuln_target.py"), "w").write(vuln)

    missions = {
        "ALPHA": "Injection SQL sur /login — la base lache son flag quand l'injection reussit",
        "BRAVO": "Path traversal sur /files — les 4 fichiers de flags/ se debloquent avec ../",
        "CHARLIE": "RCE sur /cmd?c= — execute n'importe quelle commande, lis les flags",
        "DELTA": "Upload + exploitation — les autres cibles de ton arsenal",
    }
    json.dump(missions, open(os.path.join(LAB, "missions.json"), "w"), indent=1)
    print(f"[OK] lab construit -> {LAB}")
    print("     cible vuln : vuln_target.py :8090 (SQLi / traversal / RCE)")
    print("     missions   : 4 flags cachés — scoreboard intégré")
    print("     lancement  : python3 wopr.py serve")

def serve():
    if not os.path.exists(os.path.join(LAB, "vuln_target.py")):
        print("[X] lab absent — wopr.py play d'abord"); return
    subprocess.Popen(f'python3 "{LAB}/vuln_target.py"', shell=True)
    print("[*] cible vulnerable sur :8090")

    SCORE = json.load(open(os.path.join(LAB, "scoreboard.json")))
    FOUND = []
    PAGE = """<!doctype html><html><head><meta charset=utf8><title>WOPR — Scoreboard</title>
    <meta http-equiv="refresh" content="5">
    <style>body{background:#000;color:#7fff00;font-family:monospace;padding:30px}
    h1{color:#7fff00}table{border-collapse:collapse}td,th{border:1px solid #3f3;padding:8px 16px}
    .big{font-size:1.4em;color:#fff}</style></head><body>
    <h1>W.O.P.R. — GLOBAL THERMONUCLEAR WAR · SCOREBOARD</h1>
    <table><tr><th>FLAG</th><th>MISSION</th><th>ETAT</th></tr>
    <tr><td>ALPHA</td><td>Injection SQL</td><td>__A__</td></tr>
    <tr><td>BRAVO</td><td>Path traversal</td><td>__B__</td></tr>
    <tr><td>CHARLIE</td><td>RCE</td><td>__C__</td></tr>
    <tr><td>DELTA</td><td>Libre</td><td>—</td></tr></table>
    <p class="big">SHALL WE PLAY A GAME?</p>
    <p>formulaire : POST /submit?f=FLAG{...} — le scoreboard s'allume</p></body></html>"""

    import http.server
    import http.server as hs_mod
    class SB(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            import urllib.parse
            u = urllib.parse.urlparse(self.path)
            if u.path == "/":
                page = PAGE
                for fid in ["ALPHA", "BRAVO", "CHARLIE"]:
                    page = page.replace(f"__{fid[:1]}__", "CAPTURÉ" if fid in FOUND else "libre")
                b = page.encode()
                self.send_response(200); self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
            else:
                self.send_response(404); self.end_headers()
    class C2(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            import urllib.parse
            n = int(self.headers.get("Content-Length", 0))
            d = urllib.parse.parse_qs(self.rfile.read(n).decode())
            f = d.get("f", [""])[0]
            for fid, val in SCORE.items():
                if val == f and fid not in FOUND:
                    FOUND.append(fid)
                    print(f"[FLAG] {fid} capture !")
            self.send_response(200); self.end_headers(); self.wfile.write(b"flag received")
        def log_message(self, *a): pass

    class COMBINED(SB, C2):
        pass
    print("[*] scoreboard + capture de flags sur :8091 — GET / = scoreboard, POST /submit?f=... = marquer")
    http.server.ThreadingHTTPServer(("0.0.0.0", 8091), COMBINED).serve_forever()

def destroy():
    import shutil
    subprocess.Popen("pkill -f vuln_target.py", shell=True)
    if os.path.exists(LAB):
        shutil.rmtree(LAB)
    print("[OK] WOPR_Lab détruit. la partie est finie.")

def intro():
    print("\033[38;2;127;255;0m", end="")
    grid = ["+---+---+---+", "| X | O | X |", "+---+---+---+",
            "| O | X | O |", "+---+---+---+", "| X | O | X |", "+---+---+---+"]
    for l in grid:
        print("  " + l)
        time.sleep(0.15)
    print()
    for c in "SHALL WE PLAY A GAME?":
        print(c, end="", flush=True); time.sleep(0.05)
    print("\n\n  LIGNE ROUGE GENERALE... options : build · serve · destroy\n\033[0m")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "play"
    if cmd == "play": intro()
    elif cmd == "build": build()
    elif cmd == "serve": serve()
    elif cmd == "destroy": destroy()
