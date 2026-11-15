# BatOSINT — Gotham Edition 🦇
## README — Everything, explained cold.

---

## Install

```bash
pip install requests colorama shodan holehe
pip install Pillow        # EXIF module
pip install bcrypt        # optional — bcrypt hash support
```

Python 3.10+ required.

---

## Config — fill before launch

Open `batman_osint.py`, top section:

| Variable | Where to get it | Required? |
|---|---|---|
| `SHODAN_API_KEY` | shodan.io → Account → API Key | Optional (port/vuln scan) |
| `HIBP_API_KEY` | haveibeenpwned.com/API | Optional (breach module) |
| `DISCORD_TOKEN` | discord.com/developers → Bot → Token | Required for Discord module |

Leave as `FILL_...` to skip that module — rest still works.

---

## Modules

### [01] IP Geolocation + Shodan
- **What it does:** Takes any IPv4/IPv6 address → pulls country, city, ZIP, lat/lon, ISP, ASN, org.
- **Google Maps link** generated automatically.
- With Shodan key: open ports, running services, CVEs, hostnames.
- **API used:** ip-api.com (free, 45 req/min) + Shodan API.

### [02] Username OSINT
- Checks 25 platforms simultaneously (threaded) — GitHub, Instagram, TikTok, Steam, Telegram, Reddit, Twitch, etc.
- Returns confirmed URLs where the account exists (HTTP 200 + username found in page).
- **No API key needed.**

### [03] Name / Person Lookup
- Generates LinkedIn, Facebook, Twitter people-search links.
- Generates people-search engine links: TruthFinder, Spokeo, PeekYou.
- Generates 10 Google/Bing/DDG dork queries: email, phone, CV, PDF, social.
- **No API key needed.**

### [04] Discord User Lookup by ID
- Uses Discord API v10 with your bot token.
- Returns: username, global name, account creation date (decoded from snowflake), avatar URL (direct CDN link, full res), banner URL, accent color.
- **Requires:** Bot token with no special permissions (public user data only).

### [05] Email Breach Check
- HIBP v3 API — checks all known data breaches for the email.
- Returns per-breach: name, date, number of accounts, data types leaked (passwords, emails, phones, etc).
- **Requires:** HIBP API key ($3.50/month).

### [06] Phone Number OSINT
- Validates format, returns country, carrier, line type (mobile/landline/VOIP), local format.
- Generates TrueCaller, Google, WhatsApp search links.
- **API used:** numverify (free tier).

### [07] Domain / Email Intel
- RDAP lookup: registration date, expiration, nameservers, status.
- DNS resolution → IP.
- Generates links: Hunter.io (email finder), crt.sh (SSL cert history → subdomains), Shodan, VirusTotal, Wayback Machine.
- **No API key needed.**

### [08] Password Cracker
Three attack modes:
1. **Wordlist** — feeds rockyou.txt (or any list) line by line, hashes each, compares. Fast.
2. **Brute-force** — itertools.product over charset, all lengths up to N. Slow past length 5.
3. **Online lookup** — queries free MD5/SHA1 reverse-lookup APIs.

Supports: MD5, SHA1, SHA256, SHA512.
Auto-detects hash type from length.

> Drop rockyou.txt in same folder. Get it: `https://github.com/brannondorsey/naive-hashcat/releases`

### [09] Reverse Image Search
- Takes any image URL → generates one-click search links for:
  Google Images, TinEye, Yandex (best for faces), Bing Visual Search.
- Also links PimEyes and FaceCheck.id (manual upload — best facial recognition OSINT tools).
- **No API key needed.**

### [10] EXIF Metadata + GPS
- Reads EXIF from local image file (JPG/TIFF).
- Extracts: camera model, software, datetime, focal length, all metadata.
- If GPS tags present: converts DMS → decimal degrees → Google Maps link.
- **Requires:** `pip install Pillow`

---

## Failure table

| Module | Common fail | Fix |
|---|---|---|
| IP | `private range` | ip-api doesn't resolve LAN IPs |
| Username | false negatives | some platforms block by UA — open manually |
| Discord | 401 | token expired or wrong; regenerate in dev portal |
| Discord | 404 | user deleted, banned, or ID wrong |
| HIBP | 401 | API key wrong or expired |
| Cracker wordlist | FileNotFoundError | put rockyou.txt in script folder |
| Cracker brute | very slow | keep max_len ≤ 5 for anything other than digits |
| EXIF | no GPS | photo was stripped (WhatsApp, Twitter strip EXIF) |
| EXIF | no EXIF | screenshot or heavily compressed JPEG |

---

## Run

```bash
python batman_osint.py
```

Windows CMD, PowerShell, Linux terminal, Mac terminal — all work.