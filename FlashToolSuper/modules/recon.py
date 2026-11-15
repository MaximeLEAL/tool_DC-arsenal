# modules/recon.py - 10 outils de reconnaissance reseau (commandes macOS reelles)
import os, subprocess, concurrent.futures

def ask(label): return input(f"  {label} : ").strip()

def r(cmd): subprocess.run(cmd, shell=True)

def ping_sweep():
    prefix = ask("prefixe (ex 192.168.1.)").strip()
    def ping(i):
        rc = subprocess.run(f"ping -c 1 -W 500 {prefix}{i}", shell=True,
                            stdout=subprocess.DEVNULL).returncode
        return (i, rc == 0)
    with concurrent.futures.ThreadPoolExecutor(50) as ex:
        for i, ok in ex.map(ping, range(1, 255)):
            if ok: print(f"  [VIVANT] {prefix}{i}")

def port_scan():
    host = ask("host"); ports = ask("ports (ex 21,22,80,443,445,3389)")
    for p in [x for x in ports.split(",") if x.strip()]:
        rc = subprocess.run(f"nc -z -G 2 {host} {p}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        print(f"  {host}:{p:<6} {'OUVERT' if rc == 0 else 'ferme'}")

def arp():
    r("arp -a")

def netstat():
    r("netstat -anv | head -60")

def trace():
    r(f"traceroute {ask('host')}")

def wifi_scan():
    # airport (masque sur les macOS recents) ou wdutil ; fallback system_profiler
    airport = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
    if os.path.exists(airport):
        r(f"{airport} -s")
    else:
        r("wdutil info 2>/dev/null || system_profiler SPAirPortsDataType | head -40")

def wifi_mine():
    r("networksetup -listpreferredwirelessnetworks en0 2>/dev/null || networksetup -listpreferredwirelessnetworks en1")

def pubip():
    r("curl -s https://ipinfo.io/json")

def routes():
    r("netstat -rn | head -30")

def dns_leak():
    print("  resolver actifs :")
    r("scutil --dns | grep nameserver | sort -u | head -10")
    print("  test d'echappement DNS :")
    r("curl -s https://ipleak.net/json/dns.json 2>/dev/null | head -20")
