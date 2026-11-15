# modules/darkweb.py - la face cachee du reseau
import subprocess

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def status():
    print("  tor tourne ?", end=" ")
    rc = subprocess.run("pgrep -x tor", shell=True, stdout=subprocess.DEVNULL).returncode
    print("OUI" if rc == 0 else "NON (installe-le avec le tool suivant)")
    if rc == 0:
        r("curl -s --socks5-hostname localhost:9050 https://check.torproject.org/api/ip | head -5")

def install():
    r("brew install tor && brew services start tor")
    print("  tor demarre sur le port socks 9050")

def onion_fetch():
    url = ask("URL .onion")
    r(f"curl -s --socks5-hostname localhost:9050 '{url}' | head -40")

def shadow_engines():
    for name, url in [
        ("Ahmia (onion search)", "https://ahmia.fi/search/?q="),
        ("HaveIBeenPwned", "https://haveibeenpwned.com/"),
        ("DeHashed", "https://www.dehashed.com/search?query="),
        ("IntelTechniques", "https://inteltechniques.com/tools/"),
        ("Shodan", "https://www.shodan.io/search?query="),
        ("Censys", "https://search.censys.io/search?q="),
    ]:
        print(f"   {name:<22} {url}")
