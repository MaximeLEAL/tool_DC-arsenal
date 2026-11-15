# modules/aquaman.py - 8 tools des courants (reseau, tout reels)
import os, subprocess, socket, struct, time

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def marees():
    """debit reseau en graphique terminal, delta toutes les 2 s"""
    print("  Ctrl+C pour stopper. Chaque barre = 2 s de trafic.\n")
    try:
        def counters():
            out = subprocess.run("netstat -ib", shell=True, capture_output=True).stdout.decode()
            rx = tx = 0
            for line in out.splitlines():
                p = line.split()
                if p and (p[0].startswith("en") or p[0] == "lo0") and len(p) > 9:
                    try:
                        rx += int(p[6]); tx += int(p[9])
                    except (ValueError, IndexError):
                        pass
            return rx, tx
        prx, ptx = counters()
        while True:
            time.sleep(2)
            rx, tx = counters()
            dr, dt = rx - prx, tx - ptx
            prx, ptx = rx, tx
            scale = lambda v: min(60, v // 10000)
            print(f"  RX {'█' * scale(dr):<60} {dr/1000:>8.0f} ko/s")
            print(f"  TX {'▓' * scale(dt):<60} {dt/1000:>8.0f} ko/s")
    except KeyboardInterrupt:
        print("\n  la maree se retire.")

def profondeurs():
    """latence en graphique, chaque ligne = un ping"""
    host = ask("host (1.1.1.1)") or "1.1.1.1"
    print("  Ctrl+C pour stopper\n")
    try:
        while True:
            out = subprocess.run(f"ping -c 1 -t 2 {host}", shell=True, capture_output=True).stdout.decode()
            if "time=" in out:
                ms = float(out.split("time=")[1].split()[0])
                depth = min(50, int(ms * 2))
                print(f"  {host:<15} {'·' * depth}▮ {ms:>6.1f} ms")
            else:
                print(f"  {host:<15} PERDU")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()

def trident_wol():
    """wake-on-lan reel : magic packet UDP broadcast"""
    mac = ask("MAC cible (ex a1:b2:c3:d4:e5:f6)").strip()
    mac_clean = mac.replace(":", "").replace("-", "")
    if len(mac_clean) != 12:
        print("  MAC invalide"); return
    pkt = bytes.fromhex("FF" * 6 + mac_clean * 16)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    for _ in range(3):
        s.sendto(pkt, ("255.255.255.255", 9))
        s.sendto(pkt, ("255.255.255.255", 7))
    print(f"  [TRIDENT] 3 magic packets envoyes a {mac} (ports 7 et 9)")

def courants_dns():
    iface = ask("interface (en0)") or "en0"
    print("  requetes DNS en direct (sudo, Ctrl+C) :\n")
    r(f"sudo tcpdump -i {iface} -nn port 53 -c 40")

def reef_ports():
    """ports d'ecoute groupes par application"""
    out = subprocess.run("lsof -nP -iTCP -sTCP:LISTEN", shell=True, capture_output=True).stdout.decode()
    apps = {}
    for line in out.splitlines()[1:]:
        p = line.split()
        if len(p) > 8:
            apps.setdefault(p[0], []).append(p[8])
    print("  ports d'ecoute par application :\n")
    for a, ports in sorted(apps.items(), key=lambda x: -len(x[1])):
        print(f"   {a:<18} {len(ports):>3} ports   {', '.join(ports[:5])}")

def tides_arp():
    print("  voisinage actuel :\n")
    out = subprocess.run("arp -a", shell=True, capture_output=True).stdout.decode()
    print(out)
    print(f"  total : {len(out.splitlines())} appareils connus")

def abyss_scan():
    host = ask("host")
    start = int(ask("port debut (1)"))
    end = int(ask("port fin (1024)"))
    import concurrent.futures
    def probe(p):
        s = socket.socket()
        s.settimeout(0.6)
        try:
            s.connect((host, p)); s.close(); return p
        except Exception:
            return None
    print(f"  plongee sur {end - start} ports...\n")
    with concurrent.futures.ThreadPoolExecutor(200) as ex:
        for p in ex.map(probe, range(start, end)):
            if p: print(f"  OUVERT : {p}")
    print("  remonte.")

def memoire_mer():
    r("netstat -ib")
