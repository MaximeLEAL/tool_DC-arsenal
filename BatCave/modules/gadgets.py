# modules/gadgets.py - l'arsenal
import subprocess, random, os

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def batarang():
    host = ask("host cible")
    seq = ask("ports a frapper (ex 1337,7000,9001)") or "1337,7000,9001"
    for p in seq.split(","):
        subprocess.run(f"nc -z -G 1 -w 1 {host} {p.strip()}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [FRAPPE] {host}:{p.strip()}")

def sonar():
    prefix = ask("prefixe (ex 192.168.1.)")
    import concurrent.futures
    def ping(i):
        rc = subprocess.run(f"ping -c 1 -W 400 {prefix}{i}", shell=True, stdout=subprocess.DEVNULL).returncode
        return prefix + str(i) if rc == 0 else None
    with concurrent.futures.ThreadPoolExecutor(50) as ex:
        alive = [h for h in ex.map(ping, range(1, 255)) if h]
    arp = subprocess.run("arp -a", shell=True, capture_output=True).stdout.decode()
    print(f"  {len(alive)} appareils vivants :\n")
    for h in alive:
        ip = h
        line = [l for l in arp.splitlines() if l.startswith(f"{ip} ")]
        print(f"   {ip:<16} {line[0].split('at ')[1].split(' ')[0] if line else 'mac:?' }")

def smoke_mac():
    iface = ask("interface (en0)")
    mac = ":".join(f"{random.randint(0,255):02x}" for _ in range(6))
    mac = "02" + mac[2:]  # prefixe local admin
    print(f"  MAC genere : {mac}")
    print(f"  commande a lancer (sudo requis) :")
    print(f"    sudo ifconfig {iface} ether {mac}")
    if ask("lancer maintenant ? (o/n)").lower() == "o":
        r(f"sudo ifconfig {iface} ether {mac}")
        r(f"ifconfig {iface} | grep ether")

def grapple():
    host = ask("host")
    user = ask("user")
    r(f"ssh -o StrictHostKeyChecking=accept-new {user}@{host}")

def speed():
    print("  test de debit (fichier de test Cloudflare 10 Mo) :")
    r("curl -o /dev/null -w '  vitesse : %{speed_download} octets/s\\n' https://speed.cloudflare.com/__down?bytes=10000000")

def suit():
    r("system_profiler SPHardwareDataType | grep -E 'Model|Memory|Serial'")
    r("sw_vers")
    r("ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1")
    r("df -h / | tail -1")
