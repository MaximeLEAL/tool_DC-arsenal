# modules/lasso.py - WONDER WOMAN : 8 tools de verification (le lasso ne ment pas)
import os, subprocess, hashlib, re

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def fichier():
    f = ask("fichier a soumettre au lasso")
    if not os.path.exists(f): print("  introuvable"); return
    d = open(f, "rb").read()
    print(f"  md5     {hashlib.md5(d).hexdigest()}")
    print(f"  sha256  {hashlib.sha256(d).hexdigest()}")
    r(f'sips -g pixelWidth -g pixelHeight -g format "{f}" 2>/dev/null')
    ref = ask("hash de reference (vide = passer)")
    if ref and hashlib.sha256(d).hexdigest() == ref.strip().lower():
        print("  [VERITE] le fichier est exactement celui annonce")
    elif ref:
        print("  [MENTI] le hash ne correspond pas — fichier alterne")

def tls():
    h = ask("host")
    out = subprocess.run(f"openssl s_client -connect {h}:443 -servername {h} < /dev/null 2>/dev/null",
                         shell=True, capture_output=True).stdout.decode()
    for l in out.splitlines():
        if "subject=" in l or "issuer=" in l or "Verify return code" in l:
            print("  ", l.strip())
    # dates de validite
    dates = subprocess.run(
        f'openssl s_client -connect {h}:443 -servername {h} < /dev/null 2>/dev/null | openssl x509 -noout -dates',
        shell=True, capture_output=True).stdout.decode()
    print("  ", dates.strip())

def email():
    print("  colle les headers de l'email (ligne vide = fin)")
    lines = []
    while True:
        l = input()
        if not l.strip(): break
        lines.append(l)
    text = "\n".join(lines).lower()
    verdicts = []
    for mech in ["spf", "dkim", "dmarc"]:
        m = re.search(mech + r"=([a-z]+)", text)
        if m:
            verdicts.append(f"{mech.upper()}={m.group(1).upper()}")
    print("  verdict du lasso :", ", ".join(verdicts) if verdicts else "aucune authentification visible")
    if any("fail" in v or "softfail" in v for v in verdicts):
        print("  [MENTI] l'authentification echoue — email suspect")
    ips = re.findall(r"\[([\d.]+)\]", text)
    if ips: print("  IP relais a geolocaliser :", ips[-1])

def image():
    f = ask("image a interroger")
    if not os.path.exists(f): print("  introuvable"); return
    r(f"mdls -name kMDItemGPSLatitude -name kMDItemGPSLongitude -name kMDItemAcquisitionModel -name kMDItemContentCreationDate '{f}'")
    import struct, zlib
    # pHash approximatif : miniatures normalisees -> hash comparable
    tmp = "/tmp/lasso_thumb.png"
    subprocess.run(["sips", "-s", "format", "png", "--resampleWidth", "16", f, "--out", tmp],
                   capture_output=True)
    d = open(tmp, "rb").read()
    print(f"  empreinte perceptuelle : {hashlib.md5(d).hexdigest()}")
    print("  compare-la avec une seconde image (tool 01) pour detecter un doublon re-publie")

def site():
    h = ask("site (https://...)")
    r(f'curl -sIL "{h}" | grep -iE "^(HTTP|strict-transport|x-frame|content-security|x-content)" | head -12')
    print("\n  verdict : absence de HSTS/CSP = site qui ne protege pas ses visiteurs")

def url():
    u = ask("URL a demeler")
    r(f'curl -sIL "{u}" | grep -i "^location" ')
    print("  la chaine complete des redirections ci-dessus — les raccourcisseurs mentent, le lasso demele")

def personne():
    u = ask("pseudo a suivre avec le lasso")
    for net in ["github.com", "reddit.com/user", "x.com", "instagram.com", "keybase.io"]:
        url = f"https://{net}/{u}" if "user" in net or net == "github.com" else f"https://{net}/{u}"
        print(f"   {url}")

def reseau():
    d = ask("domaine")
    r(f"dig +dnssec +short {d} | head -8")
    print("  presence d'enregistrements DNSSEC = la zone signe ses reponses (pas de mensonge possible sur son IP)")

TOOLS = [
    ("VERITE FICHIER",   "hash + comparaison de reference",          fichier),
    ("VERITE TLS",       "certificat : emetteur, validite, chaine",  tls),
    ("VERITE EMAIL",     "SPF/DKIM/DMARC d'un header",               email),
    ("VERITE IMAGE",     "GPS, appareil, empreinte perceptuelle",    image),
    ("VERITE SITE",      "HSTS/CSP : securite annoncee",             site),
    ("VERITE URL",       "demelage des redirections",                url),
    ("VERITE PERSONNE",  "consistance d'un pseudo multi-plateforme", personne),
    ("VERITE RESEAU",    "DNSSEC : la zone signe-t-elle ?",          reseau),
]
