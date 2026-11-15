#!/usr/bin/env python3
# batman_osint.py | Python 3.10+ | deps: requests, colorama, shodan, holehe, discord.py, hashlib, itertools

import os, sys, time, json, hashlib, itertools, threading, socket
import requests
from colorama import Fore, Style, init

init(autoreset=True)

# ─────────────────────────────────────────────
#  CONFIG — fill before running
# ─────────────────────────────────────────────
SHODAN_API_KEY   = "FILL_YOUR_SHODAN_KEY"       # shodan.io free tier works
IPAPI_KEY        = ""                            # optional — ip-api.com (free, no key needed for basic)
HIBP_API_KEY     = "FILL_YOUR_HIBP_KEY"         # haveibeenpwned.com
DISCORD_TOKEN    = "FILL_BOT_TOKEN"             # discord bot token with guilds.members intent

# ─────────────────────────────────────────────
#  BATMAN ASCII BANNER
# ─────────────────────────────────────────────
BANNER = f"""
{Fore.YELLOW}
        .=.,
       ';'..|
      /   .'|
     .  _  .'
    / .'/  :
   / /  |  |
  / /   |  |   {Fore.WHITE}██████╗  █████╗ ████████╗ ██████╗ ███████╗██╗███╗   ██╗████████╗
 / /    '  |   {Fore.WHITE}██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝
/_/____  .'     {Fore.WHITE}██████╔╝███████║   ██║   ██║   ██║███████╗██║██╔██╗ ██║   ██║
|      \/        {Fore.WHITE}██╔══██╗██╔══██║   ██║   ██║   ██║╚════██║██║██║╚██╗██║   ██║
|      |          {Fore.WHITE}██████╔╝██║  ██║   ██║   ╚██████╔╝███████║██║██║ ╚████║   ██║
 \     /           {Fore.WHITE}╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝
  \___/
{Fore.YELLOW}          [ OSINT & CSINT MULTITOOL — GOTHAM EDITION ]
{Fore.CYAN}          [ coded for the shadows, not the spotlight  ]
{Style.RESET_ALL}"""

# ─────────────────────────────────────────────
#  UTILS
# ─────────────────────────────────────────────
def banner(): print(BANNER)

def section(title):
    print(f"\n{Fore.YELLOW}{'═'*60}")
    print(f"{Fore.YELLOW}  ⚡  {Fore.WHITE}{title.upper()}")
    print(f"{Fore.YELLOW}{'═'*60}{Style.RESET_ALL}")

def result(label, value, color=Fore.CYAN):
    print(f"  {Fore.YELLOW}[+]{Style.RESET_ALL} {Fore.WHITE}{label:<25}{color}{value}{Style.RESET_ALL}")

def error(msg):
    print(f"  {Fore.RED}[!]{Style.RESET_ALL} {Fore.RED}{msg}{Style.RESET_ALL}")

def info(msg):
    print(f"  {Fore.CYAN}[*]{Style.RESET_ALL} {msg}")

def pause():
    input(f"\n{Fore.YELLOW}  [ENTER] back to Batcave...{Style.RESET_ALL}")

# ─────────────────────────────────────────────
#  MODULE 1 — IP GEOLOCATION
# ─────────────────────────────────────────────
def ip_lookup():
    section("IP Geolocation & Intelligence")
    ip = input(f"  {Fore.YELLOW}Target IP > {Style.RESET_ALL}").strip()
    if not ip:
        error("No IP provided.")
        return

    # ip-api.com (free, no key, 45 req/min)
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query", timeout=8)
        d = r.json()
        if d.get("status") == "success":
            result("IP",          d.get("query","?"))
            result("Country",     d.get("country","?"))
            result("Region",      d.get("regionName","?"))
            result("City",        d.get("city","?"))
            result("ZIP",         d.get("zip","?"))
            result("Latitude",    str(d.get("lat","?")))
            result("Longitude",   str(d.get("lon","?")))
            result("ISP",         d.get("isp","?"))
            result("Organisation",d.get("org","?"))
            result("AS",         d.get("as","?"))
            # Google Maps link
            lat, lon = d.get("lat"), d.get("lon")
            if lat and lon:
                result("Maps Link", f"https://maps.google.com/?q={lat},{lon}", Fore.GREEN)
        else:
            error(d.get("message","ip-api returned failure"))
    except Exception as e:
        error(f"ip-api failed: {e}")

    # Shodan host lookup
    if SHODAN_API_KEY and SHODAN_API_KEY != "FILL_YOUR_SHODAN_KEY":
        try:
            import shodan
            api = shodan.Shodan(SHODAN_API_KEY)
            host = api.host(ip)
            info("─── Shodan ───")
            result("OS",          host.get("os","unknown"))
            result("Open Ports",  str([p["port"] for p in host.get("data",[])]))
            for item in host.get("data", [])[:3]:
                result(f"Port {item['port']}",item.get("product","") + " " + item.get("version",""))
            result("Hostnames",   str(host.get("hostnames",[])))
            result("Vulns",       str(list(host.get("vulns",{}).keys())[:5]))
        except Exception as e:
            error(f"Shodan: {e}")
    else:
        info("Shodan key not set — skipping port/vuln scan.")

    pause()

# ─────────────────────────────────────────────
#  MODULE 2 — USERNAME OSINT (Sherlock-style)
# ─────────────────────────────────────────────
PLATFORMS = {
    "GitHub":       "https://github.com/{}",
    "Twitter/X":    "https://twitter.com/{}",
    "Instagram":    "https://www.instagram.com/{}/",
    "Reddit":       "https://www.reddit.com/user/{}",
    "TikTok":       "https://www.tiktok.com/@{}",
    "Twitch":       "https://www.twitch.tv/{}",
    "YouTube":      "https://www.youtube.com/@{}",
    "Pinterest":    "https://www.pinterest.com/{}/",
    "Telegram":     "https://t.me/{}",
    "Steam":        "https://steamcommunity.com/id/{}",
    "Pastebin":     "https://pastebin.com/u/{}",
    "Replit":       "https://replit.com/@{}",
    "Gitlab":       "https://gitlab.com/{}",
    "Keybase":      "https://keybase.io/{}",
    "Medium":       "https://medium.com/@{}",
    "Dev.to":       "https://dev.to/{}",
    "Linktree":     "https://linktr.ee/{}",
    "Spotify":      "https://open.spotify.com/user/{}",
    "SoundCloud":   "https://soundcloud.com/{}",
    "HackerNews":   "https://news.ycombinator.com/user?id={}",
    "ProductHunt":  "https://www.producthunt.com/@{}",
    "Gravatar":     "https://en.gravatar.com/{}",
    "Tryhackme":    "https://tryhackme.com/p/{}",
    "HackTheBox":   "https://app.hackthebox.com/users/search?term={}",
}

def _check_platform(username, name, url, found):
    target = url.format(username)
    try:
        r = requests.get(target, timeout=6, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True)
        if r.status_code == 200 and username.lower() in r.text.lower():
            found.append((name, target))
    except:
        pass

def username_lookup():
    section("Username OSINT — Cross-Platform")
    username = input(f"  {Fore.YELLOW}Username > {Style.RESET_ALL}").strip()
    if not username:
        error("No username provided.")
        return

    info(f"Scanning {len(PLATFORMS)} platforms for '{username}' — threads running...")
    found = []
    threads = []
    for name, url in PLATFORMS.items():
        t = threading.Thread(target=_check_platform, args=(username, name, url, found))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    if found:
        for name, url in found:
            result(name, url, Fore.GREEN)
    else:
        info("No confirmed accounts found.")

    # holehe — email-based username check
    info("Tip: install holehe (pip install holehe) for email-based platform check.")
    pause()

# ─────────────────────────────────────────────
#  MODULE 3 — NAME / PERSON LOOKUP
# ─────────────────────────────────────────────
def name_lookup():
    section("Person OSINT — Name Search")
    fname = input(f"  {Fore.YELLOW}First name > {Style.RESET_ALL}").strip()
    lname = input(f"  {Fore.YELLOW}Last name  > {Style.RESET_ALL}").strip()
    full  = f"{fname} {lname}".strip()

    info(f"Generating search vectors for: {full}")

    dorks = [
        f'https://www.google.com/search?q="{full}"',
        f'https://www.google.com/search?q="{full}"+site:linkedin.com',
        f'https://www.google.com/search?q="{full}"+site:facebook.com',
        f'https://www.google.com/search?q="{full}"+email+OR+contact',
        f'https://www.google.com/search?q="{full}"+phone+OR+adresse',
        f'https://www.google.com/search?q="{full}"+instagram+OR+twitter',
        f'https://www.google.com/search?q="{full}"+filetype:pdf',
        f'https://www.google.com/search?q="{full}"+resume+OR+CV',
        f'https://www.bing.com/search?q="{full}"',
        f'https://duckduckgo.com/?q="{full}"',
    ]

    # direct checks
    result("LinkedIn",     f"https://www.linkedin.com/search/results/people/?keywords={full.replace(' ','+')}",   Fore.GREEN)
    result("Facebook",     f"https://www.facebook.com/search/people/?q={full.replace(' ','+')}",                 Fore.GREEN)
    result("Twitter/X",    f"https://twitter.com/search?q={full.replace(' ','+')}&f=user",                       Fore.GREEN)
    result("TruthFinder",  f"https://www.truthfinder.com/results/?firstName={fname}&lastName={lname}",           Fore.GREEN)
    result("Spokeo",       f"https://www.spokeo.com/{fname}-{lname}",                                            Fore.GREEN)
    result("PeekYou",      f"https://www.peekyou.com/{fname}_{lname}",                                           Fore.GREEN)

    info("─── Google Dorks (open in browser) ───")
    for d in dorks:
        print(f"  {Fore.CYAN}{d}{Style.RESET_ALL}")

    pause()

# ─────────────────────────────────────────────
#  MODULE 4 — DISCORD ID LOOKUP
# ─────────────────────────────────────────────
def discord_lookup():
    section("Discord User Lookup by ID")
    user_id = input(f"  {Fore.YELLOW}Discord User ID > {Style.RESET_ALL}").strip()
    if not user_id:
        error("No ID provided.")
        return

    if not DISCORD_TOKEN or DISCORD_TOKEN == "FILL_BOT_TOKEN":
        error("DISCORD_TOKEN not set — set your bot token in config.")
        pause()
        return

    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}
    try:
        r = requests.get(f"https://discord.com/api/v10/users/{user_id}", headers=headers, timeout=8)
        if r.status_code == 200:
            d = r.json()
            result("Username",    d.get("username","?") + "#" + d.get("discriminator","0"))
            result("Global Name", d.get("global_name") or "none")
            result("ID",          d.get("id","?"))
            result("Bot",         str(d.get("bot", False)))
            avatar = d.get("avatar")
            if avatar:
                ext = "gif" if avatar.startswith("a_") else "png"
                result("Avatar", f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.{ext}?size=1024", Fore.GREEN)
            banner_hash = d.get("banner")
            if banner_hash:
                ext = "gif" if banner_hash.startswith("a_") else "png"
                result("Banner", f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=1024", Fore.GREEN)
            result("Accent Color", str(d.get("accent_color","none")))
            # created_at from snowflake
            snowflake_ms = (int(user_id) >> 22) + 1420070400000
            created = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(snowflake_ms / 1000))
            result("Account Created", created)
        elif r.status_code == 404:
            error("User not found — invalid ID or account deleted.")
        elif r.status_code == 401:
            error("Bot token invalid or expired.")
        else:
            error(f"Discord API returned {r.status_code}: {r.text}")
    except Exception as e:
        error(f"Request failed: {e}")

    pause()

# ─────────────────────────────────────────────
#  MODULE 5 — EMAIL BREACH CHECK (HIBP)
# ─────────────────────────────────────────────
def email_breach():
    section("Email Breach Check — HaveIBeenPwned")
    email = input(f"  {Fore.YELLOW}Email > {Style.RESET_ALL}").strip()
    if not email:
        error("No email provided.")
        return

    if not HIBP_API_KEY or HIBP_API_KEY == "FILL_YOUR_HIBP_KEY":
        error("HIBP_API_KEY not set.")
        pause()
        return

    headers = {
        "hibp-api-key": HIBP_API_KEY,
        "user-agent":   "BatOSINT/1.0"
    }
    try:
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers=headers,
            params={"truncateResponse": "false"},
            timeout=10
        )
        if r.status_code == 200:
            breaches = r.json()
            result("Breaches found", str(len(breaches)), Fore.RED)
            for b in breaches:
                print(f"\n  {Fore.RED}[BREACH]{Style.RESET_ALL} {Fore.WHITE}{b['Name']}")
                result("  Date",        b.get("BreachDate","?"))
                result("  Accounts",    f"{b.get('PwnCount',0):,}")
                result("  Data classes",str(b.get("DataClasses",[])))
        elif r.status_code == 404:
            result("Status", "No breaches found ✓", Fore.GREEN)
        elif r.status_code == 401:
            error("HIBP API key invalid.")
        else:
            error(f"HIBP returned {r.status_code}")
    except Exception as e:
        error(f"Request failed: {e}")

    pause()

# ─────────────────────────────────────────────
#  MODULE 6 — PHONE LOOKUP
# ─────────────────────────────────────────────
def phone_lookup():
    section("Phone Number OSINT")
    phone = input(f"  {Fore.YELLOW}Phone (intl format +33...) > {Style.RESET_ALL}").strip()
    if not phone:
        error("No phone provided.")
        return

    # numverify free — basic validation & carrier
    try:
        r = requests.get(
            f"http://apilayer.net/api/validate",
            params={"access_key":"free","number": phone},
            timeout=8
        )
        d = r.json()
        result("Valid",        str(d.get("valid","?")))
        result("Number",       d.get("international_format","?"))
        result("Local format", d.get("local_format","?"))
        result("Country",      d.get("country_name","?"))
        result("Location",     d.get("location","?"))
        result("Carrier",      d.get("carrier","?"))
        result("Line type",    d.get("line_type","?"))
    except Exception as e:
        error(f"numverify: {e}")

    # search links
    info("─── OSINT search links ───")
    result("TrueCaller",  f"https://www.truecaller.com/search/fr/{phone.replace('+','')}", Fore.GREEN)
    result("Google",      f"https://www.google.com/search?q={phone}", Fore.GREEN)
    result("WhatsApp",    f"https://wa.me/{phone.replace('+','')}", Fore.GREEN)

    pause()

# ─────────────────────────────────────────────
#  MODULE 7 — DOMAIN / EMAIL INTEL
# ─────────────────────────────────────────────
def domain_lookup():
    section("Domain & Email Intel")
    domain = input(f"  {Fore.YELLOW}Domain (ex: example.com) > {Style.RESET_ALL}").strip()
    if not domain:
        error("No domain provided.")
        return

    # WHOIS via whois.arin.net basic
    try:
        r = requests.get(f"https://rdap.org/domain/{domain}", timeout=8)
        d = r.json()
        result("Name",        d.get("ldhName","?"))
        result("Status",      str(d.get("status",[])))
        events = {e["eventAction"]: e["eventDate"] for e in d.get("events",[])}
        result("Registered",  events.get("registration","?"))
        result("Expiration",  events.get("expiration","?"))
        result("Last changed",events.get("last changed","?"))
        for ns in d.get("nameservers",[])[:4]:
            result("NS", ns.get("ldhName","?"))
    except Exception as e:
        error(f"RDAP: {e}")

    # DNS
    try:
        ip = socket.gethostbyname(domain)
        result("Resolved IP", ip)
    except:
        pass

    # Hunter.io — email finder (free tier 25 req/month, no key needed for basic)
    result("Hunter.io",   f"https://hunter.io/search/{domain}", Fore.GREEN)
    result("crt.sh",      f"https://crt.sh/?q=%.{domain}", Fore.GREEN)
    result("Shodan",      f"https://www.shodan.io/search?query=hostname%3A{domain}", Fore.GREEN)
    result("VirusTotal",  f"https://www.virustotal.com/gui/domain/{domain}", Fore.GREEN)
    result("Wayback",     f"https://web.archive.org/web/*/{domain}", Fore.GREEN)

    pause()

# ─────────────────────────────────────────────
#  MODULE 8 — PASSWORD CRACKER
#  Supports: MD5, SHA1, SHA256, SHA512, bcrypt*
#  *bcrypt requires pip install bcrypt
# ─────────────────────────────────────────────
HASH_FUNCS = {
    "md5":    lambda p: hashlib.md5(p.encode()).hexdigest(),
    "sha1":   lambda p: hashlib.sha1(p.encode()).hexdigest(),
    "sha256": lambda p: hashlib.sha256(p.encode()).hexdigest(),
    "sha512": lambda p: hashlib.sha512(p.encode()).hexdigest(),
}

def detect_hash_type(h):
    lengths = {32:"md5", 40:"sha1", 64:"sha256", 128:"sha512"}
    return lengths.get(len(h), "unknown")

def crack_wordlist(target_hash, hash_type, wordlist_path):
    func = HASH_FUNCS.get(hash_type)
    if not func:
        error(f"Unsupported hash type: {hash_type}")
        return None
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                word = line.strip()
                if func(word) == target_hash:
                    return word
                if i % 100000 == 0 and i > 0:
                    info(f"  Tested {i:,} candidates...")
    except FileNotFoundError:
        error(f"Wordlist not found: {wordlist_path}")
    return None

def crack_bruteforce(target_hash, hash_type, charset, max_len):
    func = HASH_FUNCS.get(hash_type)
    if not func:
        error(f"Unsupported: {hash_type}")
        return None
    count = 0
    for length in range(1, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            word = "".join(combo)
            count += 1
            if func(word) == target_hash:
                return word
            if count % 500000 == 0:
                info(f"  Tested {count:,} candidates ({word})...")
    return None

def password_cracker():
    section("Password Cracker — Hash Attack")
    target = input(f"  {Fore.YELLOW}Hash > {Style.RESET_ALL}").strip()
    if not target:
        error("No hash provided.")
        return

    detected = detect_hash_type(target)
    info(f"Detected: {detected}")
    hash_type = input(f"  {Fore.YELLOW}Hash type [{detected}] > {Style.RESET_ALL}").strip().lower() or detected

    print(f"\n  {Fore.YELLOW}[1]{Style.RESET_ALL} Wordlist attack")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} Brute-force attack")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} Online lookup (MD5/SHA1 only)")
    mode = input(f"  {Fore.YELLOW}Mode > {Style.RESET_ALL}").strip()

    result_pw = None

    if mode == "1":
        wl = input(f"  {Fore.YELLOW}Wordlist path (default: rockyou.txt) > {Style.RESET_ALL}").strip() or "rockyou.txt"
        info(f"Running wordlist attack with {wl}...")
        result_pw = crack_wordlist(target, hash_type, wl)

    elif mode == "2":
        charset_choice = input(f"  {Fore.YELLOW}Charset [1=alpha 2=alphanum 3=alphanum+symbols] > {Style.RESET_ALL}").strip()
        charsets = {
            "1": "abcdefghijklmnopqrstuvwxyz",
            "2": "abcdefghijklmnopqrstuvwxyz0123456789",
            "3": "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()",
        }
        charset = charsets.get(charset_choice, charsets["2"])
        max_len = int(input(f"  {Fore.YELLOW}Max length (warning: >5 is slow) > {Style.RESET_ALL}").strip() or "4")
        info(f"Brute-forcing up to length {max_len} — this may take a while...")
        result_pw = crack_bruteforce(target, hash_type, charset, max_len)

    elif mode == "3":
        # online MD5/SHA1 lookup
        try:
            if hash_type == "md5":
                r = requests.get(f"https://md5decrypt.net/Api/api.php?hash={target}&hash_type=md5&email=dummy@dummy.com&code=dummy", timeout=8)
                result_pw = r.text.strip() if r.text.strip() and "ERROR" not in r.text else None
            elif hash_type == "sha1":
                r = requests.get(f"https://sha1.gromweb.com/?sha1={target}", timeout=8)
                import re
                m = re.search(r'<em class="long-content">(.*?)</em>', r.text)
                result_pw = m.group(1) if m else None
            else:
                error("Online lookup supports MD5 and SHA1 only.")
        except Exception as e:
            error(f"Online lookup failed: {e}")

    if result_pw:
        result("CRACKED", result_pw, Fore.GREEN)
    else:
        error("Password not found.")

    pause()

# ─────────────────────────────────────────────
#  MODULE 9 — REVERSE IMAGE SEARCH LINKS
# ─────────────────────────────────────────────
def reverse_image():
    section("Reverse Image Search — OSINT Links")
    url = input(f"  {Fore.YELLOW}Image URL > {Style.RESET_ALL}").strip()
    if not url:
        error("No URL provided.")
        return

    import urllib.parse
    enc = urllib.parse.quote(url, safe="")
    result("Google Images",  f"https://www.google.com/searchbyimage?image_url={enc}", Fore.GREEN)
    result("TinEye",         f"https://tineye.com/search?url={enc}", Fore.GREEN)
    result("Yandex",         f"https://yandex.com/images/search?url={enc}&rpt=imageview", Fore.GREEN)
    result("Bing Visual",    f"https://www.bing.com/images/search?view=detailv2&iss=sbi&q=imgurl:{enc}", Fore.GREEN)
    result("PimEyes",        f"https://pimeyes.com/en", Fore.CYAN)   # manual upload required
    result("FaceCheck.id",   f"https://facecheck.id/", Fore.CYAN)    # manual upload required

    pause()

# ─────────────────────────────────────────────
#  MODULE 10 — GEOLOCATION FROM METADATA (EXIF)
# ─────────────────────────────────────────────
def exif_lookup():
    section("EXIF Metadata Extractor")
    info("requires: pip install Pillow")
    path = input(f"  {Fore.YELLOW}Image path > {Style.RESET_ALL}").strip()
    if not path or not os.path.exists(path):
        error("File not found.")
        pause()
        return
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS, GPSTAGS
        img  = Image.open(path)
        raw  = img._getexif()
        if not raw:
            info("No EXIF data found.")
            pause()
            return
        exif = {TAGS.get(k,k): v for k, v in raw.items()}
        gps  = exif.get("GPSInfo")
        for k, v in exif.items():
            if k != "GPSInfo" and not isinstance(v, bytes):
                result(str(k), str(v)[:80])
        if gps:
            gps_data = {GPSTAGS.get(t,t): gps[t] for t in gps}
            def dms_to_dd(vals, ref):
                d = float(vals[0]); m = float(vals[1]); s = float(vals[2])
                dd = d + m/60 + s/3600
                return -dd if ref in ["S","W"] else dd
            try:
                lat = dms_to_dd(gps_data["GPSLatitude"],  gps_data["GPSLatitudeRef"])
                lon = dms_to_dd(gps_data["GPSLongitude"], gps_data["GPSLongitudeRef"])
                result("GPS Latitude",  str(lat), Fore.GREEN)
                result("GPS Longitude", str(lon), Fore.GREEN)
                result("Maps",          f"https://maps.google.com/?q={lat},{lon}", Fore.GREEN)
            except KeyError:
                info("GPS data incomplete.")
    except Exception as e:
        error(f"EXIF read failed: {e}")
    pause()

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
MENU = [
    ("IP Geolocation + Shodan",        ip_lookup),
    ("Username OSINT (25 platforms)",  username_lookup),
    ("Name / Person Lookup + Dorks",   name_lookup),
    ("Discord User Lookup by ID",      discord_lookup),
    ("Email Breach Check (HIBP)",      email_breach),
    ("Phone Number OSINT",             phone_lookup),
    ("Domain / Email Intel",           domain_lookup),
    ("Password Cracker (hash attack)", password_cracker),
    ("Reverse Image Search Links",     reverse_image),
    ("EXIF Metadata + GPS Extract",    exif_lookup),
]

def main():
    os.system("cls" if os.name == "nt" else "clear")
    banner()
    while True:
        print(f"\n{Fore.YELLOW}  ╔══════════════════════════════════╗")
        print(f"  ║       BATCAVE — MAIN MENU        ║")
        print(f"  ╚══════════════════════════════════╝{Style.RESET_ALL}")
        for i, (label, _) in enumerate(MENU, 1):
            print(f"  {Fore.YELLOW}[{i:02d}]{Style.RESET_ALL} {Fore.WHITE}{label}")
        print(f"  {Fore.YELLOW}[00]{Style.RESET_ALL} {Fore.RED}Exit Gotham")
        choice = input(f"\n  {Fore.YELLOW}Batman > {Style.RESET_ALL}").strip()
        if choice == "00":
            print(f"\n{Fore.YELLOW}  The Dark Knight has left the building.{Style.RESET_ALL}\n")
            sys.exit(0)
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(MENU):
                MENU[idx][1]()
            else:
                error("Invalid option.")
        except ValueError:
            error("Enter a number.")

if __name__ == "__main__":
    main()