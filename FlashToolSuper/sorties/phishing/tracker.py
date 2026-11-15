
import http.server, datetime
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        line = f"{datetime.datetime.now()} CLIC IP={self.client_address[0]} UA={self.headers.get('User-Agent','')} ref={self.headers.get('Referer','-')}"
        open("clics.log","a").write(line + "\n"); print(line)
        self.send_response(302); self.send_header("Location","https://example.com"); self.end_headers()
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8082), H).serve_forever()
