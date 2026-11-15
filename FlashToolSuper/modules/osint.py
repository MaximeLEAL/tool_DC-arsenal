# modules/osint.py - 15 outils OSINT reels (APIs publiques + commandes macOS)
import os, subprocess, json, urllib.request, urllib.parse

def ask(label):
    return input(f"  {label} : ").strip()

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "FlashToolSuper/1.0"})
    return urllib.request.urlopen(req, timeout=12).read().decode(errors="ignore")

def username_hunt():
    import concurrent.futures
    u = ask("pseudo").replace(" ", "")
    sites = [
        ("GitHub", "https://github.com/{}"), ("Twitter/X", "https://x.com/{}"),
        ("Instagram", "https://instagram.com/{}"), ("Reddit", "https://reddit.com/user/{}"),
        ("TikTok", "https://tiktok.com/@{}"), ("Twitch", "https://twitch.tv/{}"),
        ("YouTube", "https://youtube.com/@{}"), ("Steam", "https://steamcommunity.com/id/{}"),
        ("Pinterest", "https://pinterest.com/{}"), ("Medium", "https://medium.com/@{}"),
        ("Spotify", "https://open.spotify.com/user/{}"), ("SoundCloud", "https://soundcloud.com/{}"),
        ("Behance", "https://behance.net/{}"), ("GitLab", "https://gitlab.com/{}"),
        ("Dev.to", "https://dev.to/{}"), ("Keybase", "https://keybase.io/{}"),
        ("Telegram", "https://t.me/{}"), ("Bluesky", "https://bsky.app/profile/{}"),
        ("Flickr", "https://flickr.com/people/{}"), ("Vimeo", "https://vimeo.com/{}"),
    ]
    print(f"\n  recherche du pseudo : {u}\n")
    def check(site_url):
        name, url = site_url
        full = url.format(urllib.parse.quote(u))
        try:
            req = urllib.request.Request(full, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            return name, full, urllib.request.urlopen(req, timeout=6).status == 200
        except Exception as e:
            return name, full, getattr(e, "code", 0) == 200
    with concurrent.futures.ThreadPoolExecutor(20) as ex:
        for name, full, found in ex.map(check, sites):
            print(f"  {'[TROUVE]' if found else '[-----]'} {name:<12} {full}")

def whois():
    d = ask("domaine")
    subprocess.run(["whois", d])

def dns_enum():
    d = ask("domaine")
    for t in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        subprocess.run(["dig", "+short", d, t])

def subdomains():
    d = ask("domaine")
    data = fetch(f"https://crt.sh/?q=%.{d}&output=json")
    subs = sorted({e["name_value"] for e in json.loads(data) if d in e["name_value"]})
    print(f"\n  {len(subs)} sous-domaines trouves :\n")
    for s in subs[:60]:
        print("   ", s)

def geoloc():
    ip = ask("IP")
    print("  " + fetch(f"https://ipinfo.io/{ip}/json"))

def reverse_ip():
    ip = ask("IP")
    try:
        print("  " + fetch(f"https://api.hackertarget.com/reverseiplookup/?q={ip}"))
    except Exception as e:
        print(f"  [!] {e} (limite API gratuite atteinte ?)")

def headers():
    u = ask("URL (http://...)")
    subprocess.run(["curl", "-sI", u])

def exif():
    f = ask("chemin de la photo")
    subprocess.run(["mdls", f])
    subprocess.run(["sips", "-g", "all", f])

def wayback():
    d = ask("domaine")
    print("  " + fetch(f"http://web.archive.org/cdx/search/cdx?url={d}&output=text&fl=timestamp,original,statuscode&limit=25"))

def pastes():
    q = ask("mots-cles")
    try:
        data = fetch(f"https://psbdmp.ws/api/search/{urllib.parse.quote(q)}")
        hits = json.loads(data).get("data", [])[:15]
        for h in hits:
            print(f"   {h.get('id','?')}  {h.get('text','')[:80]}")
    except Exception as e:
        print(f"  [!] {e}")

def permutator():
    p, n, d = ask("prenom").lower(), ask("nom").lower(), ask("domaine")
    fmts = [f"{p}.{n}", f"{p}{n}", f"{n}{p}", f"{p[0]}{n}", f"{p}{n[0]}", f"{n}.{p}", f"{p}-{n}", f"{n[0]}{p}"]
    print()
    for f in fmts:
        print(f"   {f}@{d}")

def dorks():
    d = ask("domaine")
    for q in [f"site:{d} filetype:pdf", f"site:{d} filetype:xlsx", f"site:{d} inurl:admin",
              f"site:{d} intitle:login", f"site:{d} inurl:confidential", f"intext:@{d}"]:
        print(f"   https://www.google.com/search?q={urllib.parse.quote(q)}")

def tls_info():
    h = ask("host")
    r = subprocess.run(["openssl", "s_client", "-connect", f"{h}:443", "-servername", h],
                       input=b"", capture_output=True, timeout=15)
    import re
    cert = r.stdout.decode(errors="ignore")
    for line in cert.splitlines():
        if "subject=" in line or "issuer=" in line:
            print("  ", line.strip())

def social():
    n = ask("nom ou pseudo")
    for q in [f'"{n}" site:linkedin.com', f'"{n}" site:facebook.com', f'"{n}" site:x.com']:
        print(f"   https://www.google.com/search?q={urllib.parse.quote(q)}")

def breach():
    e = ask("email")
    # check public via les services sans cle : paste engines + mot de passe clue
    print(f"  verifie manuellement ces sources pour {e} :")
    print(f"   https://haveibeenpwned.com/unifiedsearch/{urllib.parse.quote(e)}  (via navigateur)")
    print(f"   https://psbdmp.ws/api/search/{urllib.parse.quote(e.split('@')[0])}")
    try:
        data = fetch(f"https://psbdmp.ws/api/search/{urllib.parse.quote(e.split('@')[0])}")
        for h in json.loads(data).get("data", [])[:10]:
            print(f"   paste {h.get('id')}")
    except Exception:
        pass
