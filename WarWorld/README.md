# WARWORLD v3 — LE VISAGE DE DEATHSTROKE · powered by Maxime Leal

**Re-design complet** aux couleurs du mercenaire : orange #ff6a00 / noir, **masque Deathstroke
stylisé en SVG inline** dans le header (moitié or, moitié ombre), sidebar à liseré orange,
cartes à bord orange. Et surtout : **liens d'achat réels** sur le hardware.

## NOUVEAUTÉS v3
1. **Masque Deathstroke SVG** dans le masthead + palette orange/noir partout (web)
2. **8 liens de magasin officiels** intégrés dans les fiches :
   - SGP Card Joker → sgpcard.com/sgp-card-joker/
   - Rubber Ducky, Bash Bunny, WiFi Pineapple → hak5.org / shop.hak5.org
   - Flipper Zero → flipperzero.one · HackRF One → greatscottgadgets.com
   - Proxmark3 → proxmark.com · O.MG Cable → mg.lol · Logic Analyzer → amazon.fr
   - **bouton « 🛒 MAGASIN OFFICIEL ↗ »** sur chaque carte web
3. **4 armes hardware en plus** (67 → 71) : Key Croc (~130€), Alfa AWUS036ACH (~50€),
   RTL-SDR Blog V3 (~40€), Raspberry Pi 4 (~80€) — chacune avec son lien
4. CMD : fiche d'arme affiche le **MAGASIN** ; le budget `[b]` liste les liens sous chaque ligne

## LES DEUX INTERFACES
```
cd ~/Desktop/tool_DC/WarWorld
python3 warworld_cmd.py          # CMD (n/p thèmes · 1-9 fiche · f chasse · b budget)
python3 arsenal_web.py 8089      # page Deathstroke → http://127.0.0.1:8089
```

## V4 — 110 armes · 16 thèmes · 22 dépôts GitHub liés

**Nouveaux thèmes v3 :**
| Thème | Contenu |
|---|---|
| **OPEN-SOURCE & GITHUB** (13) | Villain · HoaxShell · Ligolo-ng · Havoc C2 · Nuclei · Impacket · Rubeus · Mimikatz · BloodHound · Quasar RAT · Xeno-RAT · Certipy · Exploit-DB — **chaque fiche a son dépôt réel** |
| **ESP32 & DIY** (7) | ESP32 Marauder · Spacehuhn Deauther · M5Stack Cardputer (~30€) · ESP32-CAM (~10€) · LilyGO T-Deck (~45€) · Evil Portal · MicroPython payloads |
| **RESSOURCES FERMÉES** (7) | Cobalt Strike · Brute Ratel C4 · Nighthawk · Zerodium/Crowdfense (brokers 0-day) · Genesis/Russian Market (démantelés/surveillés) · Exploit.in, XSS.is · IAB — **les noms de l'écosystème à accès restreint : vetting, invitation, crypto. Les noms pour la connaissance — pas de démarche ici.** |

Statuts : [LAB] 21 · [REF] 57 · [ACHAT] 24 (liens magasin) · [FERMÉ] 9 (accès restreint).

### THÈME EXOTIQUE & RÉSERVE (12) — le non-classique
PoisonTap (Samy Kamkar, ~20€) · Pwnagotchi (l'IA handshake collector, ~35€) · Shark Jack (~100€) ·
StingRay/IMSI catcher (grade flic, FERMÉ) · PRET (imprimantes menteuses) · Rowhammer (bits de RAM retournés) ·
LED-it-GO/Fansmitter (exfil hors air-gap par LED et ventilateur) · Thunderstrike 2 (implant firmware Mac) ·
EternalBlue MS17-010 (le SMB de WannaCry) · **Stuxnet** (la légende industrielle) · USB Killer + usbkill (défense) ·
WiFi profile backdoor (le BadUSB qui fait rejoindre TON hotspot au reboot — LAB)
Ajouter une arme = une ligne dans `arsenal_data.py` (+ `DETAILS["Nom"] = {"prix", "kit", "usage", "buy"}`).


## LES 12 THÈMES · 67 ARMES
| # | Thème | Armes | Joyaux |
|---|---|---|---|
| 1 | RECONNAISSANCE | 6 | Nmap, Shodan, Maltego · **ta page OSINT Flash** |
| 2 | EXPLOITATION WEB | 6 | Burp Suite Pro, sqlmap, Evilginx2 · **ton miroir Scarecrow** |
| 3 | RÉSEAU & INFRA | 6 | Metasploit, Hydra, Responder, Wireshark · **Aquaman + BatCave sniffer** |
| 4 | MALWARE & RANSOMWARE | 7 | Cobalt Strike, Meterpreter · **RickPortal, LexCorp v2, Hydre, Crypter** |
| 5 | INGÉNIERIE SOCIALE | 5 | SET, Gophish · **Scarecrow, ArkhamGame, Jedi Mind Trick** |
| 6 | WIRELESS & RF | 6 | Aircrack-ng · **à acquérir : WiFi Pineapple, HackRF One, Proxmark3, Flipper Zero** |
| 7 | HARDWARE & BADUSB | 6 | Rubber Ducky, Bash Bunny, O.MG Cable · **ta SGP Card Joker + kit** |
| 8 | MOBILE | 5 | Frida, Objection, MobSF, ADB · **TaskForceX APK** |
| 9 | CLOUD | 4 | Pacu, ScoutSuite, kube-hunter · **ton tunnel CloudFlare** |
| 10 | DÉTECTION & DFIR | 6 | Velociraptor, YARA, Sigma · **Kryptonite, Daily Planet** |
| 11 | CRYPTO & CACHAGE | 5 | VeraCrypt, GnuPG · **ta stégano PNG, Kyber Crystal** |
| 12 | POSTURE & C2 | 5 | Sliver, Mythic · **STAR C2 DNS/HTTP, Arkham Console** |

## LECTURE DES STATUTS
- **[LAB — DANS TON ARSENAL]** : déjà construit et fonctionnel chez toi — 21 armes
- **[REF — RÉFÉRENCE MONDIALE]** : les outils dont tout opérateur connaît le nom — 31 armes
- **[ACHAT — HARDWARE À ACQUÉRIR]** : le matériel qui ferait grandir le lab — 15 armes
  (budget indicatif : Flipper Zero ~180€, WiFi Pineapple ~120€, HackRF ~300€, Proxmark3 ~300€)

## EXTENSION
Le registre vit dans `arsenal_data.py` — ajouter une arme = une ligne :
```python
("Nom", "LOGICIEL|HARDWARE|LAB", "description", "LAB|REF|ACHAT"),
```
Les deux interfaces (CMD + web) la ramassent automatiquement.
