# modules/sniff.py - les capteurs du reseau de Gotham
import subprocess

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def live():
    iface = ask("interface (vide = en0)") or "en0"
    n = ask("nombre de paquets (50)") or "50"
    r(f"sudo tcpdump -i {iface} -c {n} -nn")

def http_uris():
    iface = ask("interface (vide = en0)") or "en0"
    r(f"sudo tcpdump -i {iface} -A -s 0 'tcp port 80' -c 200 | grep -E 'GET|POST|Host:' | head -40")

def replay():
    f = ask("fichier pcap")
    r(f"tcpdump -nn -r '{f}' 2>/dev/null | head -40")

def neighbors():
    r("arp -a")

def talkers():
    r("nettop -P -L 1 -k state -t tcp | head -25")
