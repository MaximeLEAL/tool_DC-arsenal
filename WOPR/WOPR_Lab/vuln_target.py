#!/usr/bin/env python3
# WOPR target - serveur volontairement vulnérable (LAB, localhost:8090)
import http.server, sqlite3, os, urllib.parse, subprocess
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
