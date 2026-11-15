# modules/darkweb_kit.py - CONSTANTINE : 10 tools dark web (lab/recherche autorisee)
# Tor requis pour les tools onion - le kit l'installe pour toi (tool 02)
import os, subprocess, re, json, socket, urllib.request, hashlib

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)
SOCKS = "--socks5-hostname localhost:9050"

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def tor_ok():
    return subprocess.run("pgrep -x tor", shell=True, stdout=subprocess.DEVNULL).returncode == 0

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode(errors="ignore")

def tor_fetch(url, timeout=40):
    return subprocess.run(f"curl -s {SOCKS} --max-time {timeout} '{url}'", shell=True,
                          capture_output=True, timeout=timeout + 5).stdout.decode(errors="ignore")

# 01 ------------------------------------------------------------------
def status():
    print("  tor :", "ACTIF" if tor_ok() else "INACTIF")
    if tor_ok():
        try:
            ip = fetch("https://check.torproject.org/api/ip")
            print("  sortie tor :", ip)
        except Exception as e:
            print(f"  [!] test de sortie : {e}")
    else:
        print("  lance le tool 02 pour l'installer")
    print("\n  ton IP en clair :")
    r("curl -s https://ipinfo.io/json | head -12")

# 02 ------------------------------------------------------------------
def install():
    if tor_ok():
        print("  tor tourne deja."); return
    r("brew install tor && brew services start tor")
    time.sleep(3)
    print("  tor", "ACTIF" if tor_ok() else "en demarrage (reessaie dans 10 s)")

# 03 ------------------------------------------------------------------
def onion_fetch():
    if not tor_ok(): print("  [!] tor inactif - tool 02"); return
    url = ask("URL .onion")
    page = tor_fetch(url)
    if page:
        open(os.path.join(OUT, "onion_page.html"), "w").write(page)
        text = re.sub(r"<[^>]+>", " ", page)
        print("  ", " ".join(text.split())[:600])
        print(f"\n  [OK] page sauvee -> sorties/onion_page.html")
    else:
        print("  page vide ou onion morte")

# 04 ------------------------------------------------------------------
def crawler():
    if not tor_ok(): print("  [!] tor inactif - tool 02"); return
    url = ask("onion de depart")
    depth = 1
    seen = set()
    log = open(os.path.join(OUT, "crawl.log"), "w")
    def crawl(u, d):
        if d > depth or u in seen or len(seen) > 30: return
        seen.add(u)
        page = tor_fetch(u)
        links = re.findall(r'href="(http://[a-z2-7]{16,56}\.onion[^"\']*)"', page)
        title = re.search(r"<title>(.*?)</title>", page, re.I | re.S)
        line = f"{u}  |  {title.group(1).strip()[:60] if title else '?'}"
        log.write(line + "\n"); print("  ", line)
        for l in links:
            crawl(l, d + 1)
    crawl(url, 0)
    log.close()
    print(f"\n  [OK] {len(seen)} pages -> sorties/crawl.log")

# 05 ------------------------------------------------------------------
def dark_search():
    q = ask("mots-cles")
    try:
        data = fetch("https://ahmia.fi/search/?q=" + __import__("urllib.parse", fromlist=["quote"]).quote(q))
        results = re.findall(r'href="(http[s]?://[a-z2-7]+\.onion[^"]*)"[^>]*>([^<]{5,80})', data)
        if not results:
            print("  aucun resultat direct - ouvre dans le navigateur :")
            print(f"   https://ahmia.fi/search/?q={__import__('urllib.parse', fromlist=['quote']).quote(q)}")
        for url, title in results[:15]:
            print(f"   {url[:70]}\n     {title.strip()[:70]}")
    except Exception as e:
        print(f"  [!] {e}")

# 06 ------------------------------------------------------------------
def wiki():
    print("  les annuaires survivent, les URLs meurent. fontaines actives :")
    for name, url in [
        ("Ahmia index", "https://ahmia.fi/onions/"),
        ("The Hidden Wiki (miroirs variables)", "https://thehiddenwiki.org/"),
        ("Torch", "http://torchdeedp3iwrjigufjxyvw5uhwt7hsgeykhvemizfa3wj43lzlf5aid.onion"),
    ]:
        print(f"   {name:<36} {url}")
    u = ask("onion d'annuaire a ouvrir (vide = passer)")
    if u and tor_ok():
        page = tor_fetch(u)
        links = re.findall(r'href="(http://[a-z2-7]{16,56}\.onion[^"]*)"', page)
        for l in links[:25]: print("   ", l)

# 07 ------------------------------------------------------------------
def pgp_sign():
    """signature/verification de message via openssl (chaque machine peut verifier)"""
    msg = ask("message a signer")
    key = os.path.join(OUT, "ombre_key.pem")
    if not os.path.exists(key):
        subprocess.run(f'openssl genrsa -out "{key}" 2048', shell=True)
        print(f"  [OK] identite creee -> {key}")
    open(os.path.join(OUT, "msg.txt"), "w").write(msg)
    subprocess.run(f'openssl dgst -sha256 -sign "{key}" -out "{OUT}/msg.sig" "{OUT}/msg.txt"', shell=True)
    v = subprocess.run(f'openssl dgst -sha256 -verify "{key}" -signature "{OUT}/msg.sig" "{OUT}/msg.txt"',
                       shell=True, capture_output=True).stdout.decode()
    print("  ", v.strip())
    print("  signature -> sorties/msg.sig (la machine qui verif a besoin de la cle publique)")

# 08 ------------------------------------------------------------------
def btc_lookup():
    addr = ask("adresse BTC")
    try:
        data = json.loads(fetch(f"https://blockchain.info/rawaddr/{addr}"))
        print(f"  adresse   : {data.get('address')}")
        print(f"  total recu: {data.get('total_received', 0)/1e8} BTC")
        print(f"  solde     : {data.get('final_balance', 0)/1e8} BTC")
        print(f"  tx        : {data.get('n_tx')} transactions")
        for tx in (data.get("txs") or [])[:5]:
            print(f"   {tx.get('time', 0)}  hash {tx.get('hash','')[:40]}")
    except Exception as e:
        print(f"  [!] {e}")

# 09 ------------------------------------------------------------------
def leak_engine():
    e = ask("email ou pseudo")
    q = __import__("urllib.parse", fromlist=["quote"]).quote(e)
    print("  sondage multi-source :\n")
    for name, url in [
        ("haveibeenpwned (navigateur)", f"https://haveibeenpwned.com/account/{q}"),
        ("psbdmp (pastes)", f"https://psbdmp.ws/api/search/{q}"),
        ("dehashed (navigateur)", f"https://www.dehashed.com/search?query={q}"),
        ("intelx (navigateur)", f"https://intelx.io/?s={q}"),
    ]:
        print(f"   {name:<30} {url}")
    try:
        hits = json.loads(fetch(f"https://psbdmp.ws/api/search/{q}")).get("data", [])[:10]
        for h in hits:
            print(f"   paste {h.get('id')}  {h.get('text','')[:60]}")
    except Exception:
        pass

# 10 ------------------------------------------------------------------
def burn_trace():
    """ce que ton IP/ta machine fuient dehors, en clair"""
    print("  --- ton IP publique + organisation ---")
    r("curl -s https://ipinfo.io/json | head -12")
    print("\n  --- headers vus par un serveur distant ---")
    r("curl -s https://httpbin.org/headers | head -15")
    print("\n  --- resolver DNS que tu utilises ---")
    r("scutil --dns | grep nameserver | sort -u | head -6")
    print("\n  lecture : tout ce qui sort de ta machine t'identifie.")
    print("  derriere tor, seul le timestamp et le comportement restent.")

TOOLS = [
    ("STATUS TOR",        "tor actif ? quelle IP de sortie ?",          status),
    ("INSTALLER TOR",     "brew install + service automatique",         install),
    ("FETCH ONION",       "recuperer une page .onion",                  onion_fetch),
    ("DARK CRAWLER",      "explorer 1 niveau depuis une onion",         crawler),
    ("RECHERCHE OMBRE",   "moteur ahmia -> resultats .onion",           dark_search),
    ("ANNUAIRES",         "hidden wiki et fontaines d'adresses",        wiki),
    ("SIGNATURE OMBRE",   "signer un message (openssl RSA)",            pgp_sign),
    ("BTC LOOKUP",        "solde et transactions d'une adresse",        btc_lookup),
    ("MOTEUR DE FUITE",   "email/pseudo sur 4 sources de fuite",        leak_engine),
    ("TRACE BRULEE",      "ce que ta machine fuit en clair",            burn_trace),
]
