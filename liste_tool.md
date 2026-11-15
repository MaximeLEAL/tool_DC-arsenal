# L'ARSENAL DC — LE GUIDE DE LANCEMENT · powered by Maxime Leal
# 26 kits · ~240 tools · tout se lance depuis ~/Desktop/tool_DC/
# Interface unique : double-clique DC.command OU http://127.0.0.1:9000

═══════════════════════════════════════════════════════════════
  FORMULE UNIVERSELLE : cd ~/Desktop/tool_DC/<Dossier> && <Commande>
  Puis : numéro + Entrée = lance le tool · q = quit · Ctrl+C = stop
═══════════════════════════════════════════════════════════════

---

## KIT 01 — RICKPORTAL (portail vert · kit malware complet)
```
cd ~/Desktop/tool_DC/RickPortal && ./RickPortal.command
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | MEESEEKS KEYLOGGER | keylogger | capture des frappes clavier, horodaté + fenêtre active |
| 2 | PORTAL SHELL | reverse shell | contrôle total à distance, reconnexion auto 20 s |
| 3 | SCHWIFTYCRYPT | ransomware | AES-256-CBC, fichiers .morty, mode decrypt inclus |
| 4 | CLIP HIJACK | clipboard | espionne le presse-papiers, remplace adresses crypto |
| 5 | PLUMBUS WORM | worm USB | propagation sur clés USB, autorun, fichiers cachés |
| 6 | CITADEL WORM | worm LAN | propagation réseau /24 via C$, creds faibles |
| 7 | INTERDIM SCREENS | screenspy | captures d'écran GDI périodiques en BMP |
| 8 | BLIPS & CHITZ CAM | webcam | snapshots webcam VFW périodiques |
| 9 | PORTAL DROPPER | dropper | URL XOR-obfusquée, download+exec caché+persistance |
| 0 | POOPYBUTTHOLE MIC | micro | enregistrement micro WAV 60 s en boucle |
| c | compile tout | build | compile les 10 tools mac en un coup |
| p | replay portail | animation | rejoue l'animation du portail vert |

---

## KIT 02 — FLASH TOOL_SUPER (éclair · 55 tools)
```
cd ~/Desktop/tool_DC/FlashToolSuper && python3 flash_tool.py
```
Touches : `1-9` tools · `n`/`p` pages · `l` foudre · `q` quit

### Page 1 — MALWARE
| # | Tool | Thème |
|---|---|---|
| 1 | COMPILE KIT MAC | build des 10 tools macOS |
| 2 | COMPILE KIT WINDOWS | cross-compile les 10 exes PE |
| 3 | DROPPER MAC | génère le .command auto-extractant |
| 4 | DROPPER WINDOWS | génère le vbs silencieux + zip |
| 5 | KEYLOGGER test | capteur de frappes local |
| 6 | REVERSE SHELL test | shell sortant vers 127.0.0.1:4444 |
| 7 | SCHWIFTYCRYPT demo | AES chiffre/déchiffre dossier leurre |
| 8 | USB WORM test | propagation sur volumes montés |
| 9 | SCREENSPY 5s | captures rapides pour test |
| 0 | NETTOYER MACHINE | uninstall complet des agents |

### Page 2 — OSINT
| # | Tool | Thème |
|---|---|---|
| 1 | USERNAME HUNT | pseudo sur 20 réseaux |
| 2 | WHOIS DOMAINE | registre + dates |
| 3 | DNS ENUM | A/AAAA/MX/NS/TXT |
| 4 | SOUS-DOMAINES | certificats TLS → sous-domaines |
| 5 | GEOLOC IP | ville, ASN, orga d'une IP |
| 6 | REVERSE IP | sites co-hébergés |
| 7 | HTTP HEADERS | technos exposées |
| 8 | EXIF METADATA | GPS, appareil, dates |
| 9 | WAYBACK | historique d'archive |
| 0 | PASTES/LEAKS | recherche sur sites de paste |
| 1bis | EMAIL PERMUTATOR | formats d'email possibles |
| 2bis | GOOGLE DORKS | dorks pré-montés |
| 3bis | CERTIFICATS TLS | SAN et émetteur |
| 4bis | SOCIAL SCAN | profils publics d'un nom |
| 5bis | BREACH CHECK | email dans les fuites |

### Page 3 — RECON-RÉSEAU
| # | Tool | Thème |
|---|---|---|
| 1 | PING SWEEP /24 | hôtes vivants du sous-réseau |
| 2 | PORT SCAN | scan TCP via nc |
| 3 | ARP TABLE | voisins réseau et MAC |
| 4 | CONNEXIONS ACTIVES | netstat complet |
| 5 | TRACEROUTE | chemin vers une cible |
| 6 | WIFI AUTOUR | réseaux visibles, force, canal |
| 7 | MA TABLE WIFI | réseaux mémorisés |
| 8 | IP PUBLIQUE | ton IP vue de l'extérieur |
| 9 | ROUTE TABLE | passerelles et routes |
| 0 | DNS LEAK TEST | qui résout tes requêtes |

### Page 4 — BADUSB
| # | Tool | Thème |
|---|---|---|
| 1 | PRANK PLEIN ÉCRAN | message invincible, combo secret pour sortir |
| 2 | FAKE BSOD | écran bleu factice plein écran |
| 3 | DROPPER MAC USB | installe le kit via terminal tapé |
| 4 | DROPPER WINDOWS | installe via powershell tapé |
| 5 | WIFI GRAB WIN | exporte les clés wifi sur clé USB |
| 6 | WALLPAPER SWAP | change le fond d'écran (prank) |
| 7 | MESSAGE SPAMMER | popups en boucle |
| 8 | HISTORIQUE NAV | exfiltration des navigations |

### Page 5 — PHISHING
| # | Tool | Thème |
|---|---|---|
| 1 | PAGE LOGIN DEMO | page de capture (lab autorisé) |
| 2 | TRACKER DE CLICS | serveur qui logge IP/UA des clics |
| 3 | PRETEXTES EMAIL | 3 modèles d'emails d'ingénierie |
| 4 | PRETEXTES SMS | modèles smishing pour le lab |
| 5 | DORK GENERATOR | dorks ciblés sur un domaine |

### Page 6 — SYSTÈME
| # | Tool | Thème |
|---|---|---|
| 1 | CLÉS WIFI MÉMORISÉES | passphrase des réseaux connus |
| 2 | PROCESSUS | arbre des processus en cours |
| 3 | LAUNCHAGENTS | persistance présente |
| 4 | PORTES OUVERTES | ports en écoute locale |
| 5 | DISQUE | usage des volumes |
| 6 | HISTORIQUE TERMINAL | dernières commandes |
| 7 | MATÉRIEL | modèle, CPU, RAM, macOS |

---

## KIT 03 — BATCAVE (chauve-souris · 31 tools)
```
cd ~/Desktop/tool_DC/BatCave && python3 bat_tool.py
```
### Page DETECTIVE
| # | Tool | Thème |
|---|---|---|
| 1 | ANALYSE EMAIL | headers : IP source, relais, SPF |
| 2 | IMAGE FORENSIQUE | hash, infos, recherche inverse |
| 3 | STÉGANO CACHER | message secret dans un PNG |
| 4 | STÉGANO RÉVÉLER | extraire le secret d'un PNG |
| 5 | DOSSIER DOMAINE | whois + DNS + MX en rapport |
| 6 | IDENTIFIER UN HASH | type + essais dictionnaire |

### Page CRYPTO
| # | Tool | Thème |
|---|---|---|
| 1 | COUTEAU SUISSE ENC | base64 / hex / rot13 |
| 2 | AES FICHIER | chiffre/déchiffre via openssl |
| 3 | CASSE-MD5 | attaque dictionnaire md5/sha1 |
| 4 | GÉNÉRATEUR MDP | mot de passe fort sur mesure |
| 5 | CHIFFRE CESAR | rot-N interactif |
| 6 | EMPREINTES | checksums sha256 |

### Page SNIFFER
| # | Tool | Thème |
|---|---|---|
| 1 | TCPDUMP LIVE | paquets en direct (sudo) |
| 2 | HTTP URIS | URLs en clair sur port 80 |
| 3 | REJOUER UN PCAP | analyse d'une capture |
| 4 | VOISINS ARP | qui est sur le réseau |
| 5 | GROS PARLEURS | qui consomme le réseau |

### Page DARK WEB
| # | Tool | Thème |
|---|---|---|
| 1 | STATUS TOR | tor actif ? IP de sortie ? |
| 2 | INSTALLER TOR | brew install + service |
| 3 | FETCH ONION | récupérer une page .onion |
| 4 | MOTEURS D'OMBRE | liens de recherche leaks/ombres |

### Page GADGETS
| # | Tool | Thème |
|---|---|---|
| 1 | BATARANG KNOCK | port knocking sur une cible |
| 2 | SONAR RÉSEAU | balayage complet vivants + MAC |
| 3 | FUMIGÈNE MAC | usurper une adresse MAC |
| 4 | GRAPIN SSH | connexion ssh configurée |
| 5 | BATMOBILE SPEED | test de débit réseau |
| 6 | BATSUIT | rapport machine complet |

### Page ALERTES
| # | Tool | Thème |
|---|---|---|
| 1 | BAT-SIGNAL WEB | surveille un site, alerte au changement |
| 2 | PÉRIMÈTRE RÉSEAU | alerte aux nouveaux appareils |
| 3 | VEILLE PORTS | alerte si un port s'ouvre |
| 4 | JOURNAL D'ALERTES | relecture du journal |

---

## KIT 04 — JOKER (chaos · 8 pranks)
```
cd ~/Desktop/tool_DC/JokerChaos && python3 joker_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | TEMPÊTE HAHA | écran envahi de rires (Ctrl+C) |
| 2 | RIRE DU JOKER | la machine rit à voix haute (say) |
| 3 | POPUP ORAGE | dialogues en rafale |
| 4 | NOTIFICATIONS | bombardement de notifications |
| 5 | PRANK PLEIN ÉCRAN | page invincible, sortie: JOKER |
| 6 | FAKE UPDATE | fausse mise à jour infinie |
| 7 | VOLUME MAX | volume à fond en boucle |
| 8 | WALLPAPER JOKE | fond d'écran violet posé |

---

## KIT 05 — AQUAMAN (réseau · 8 tools)
```
cd ~/Desktop/tool_DC/TridentAquaman && python3 aquaman_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | MARÉES | débit réseau graphique live RX/TX |
| 2 | PROFONDEURS | latence ping en graphique |
| 3 | TRIDENT WOL | wake-on-lan réel (magic packet) |
| 4 | COURANTS DNS | requêtes DNS en direct |
| 5 | REEF PORTS | ports d'écoute par application |
| 6 | MARÉES ARP | voisinage réseau |
| 7 | ABYSS SCAN | scan profond de ports (threads) |
| 8 | MÉMOIRE DE MER | usage données par interface |

---

## KIT 06 — SUPERMAN (vision · 8 tools)
```
cd ~/Desktop/tool_DC/SupermanVision && python3 superman_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | RAYONS-X DISQUE | plus gros / cachés / récents fichiers |
| 2 | VISION THERMIQUE | CPU par process en direct |
| 3 | SOUFFLE GIVRANT | geler un processus (réversible) |
| 4 | SUPER-OUÏE | carte audio de la machine |
| 5 | KRYPTONITE DETECTOR | détecte les IOCs des 20 kits |
| 6 | FORTERESSE | coffre chiffré AES d'un dossier |
| 7 | CHARGE SOLAIRE | batterie et thermique |
| 8 | SUPER-VITESSE | recherche instantanée de fichiers |

---

## KIT 07 — CONSTANTINE (dark web · 10 tools)
```
cd ~/Desktop/tool_DC/ConstantineDark && python3 constantine_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | STATUS TOR | tor actif ? IP de sortie ? |
| 2 | INSTALLER TOR | brew install + service |
| 3 | FETCH ONION | récupérer une page .onion |
| 4 | DARK CRAWLER | explorer 1 niveau depuis une onion |
| 5 | RECHERCHE OMBRE | moteur Ahmia → onions |
| 6 | ANNUAIRES | hidden wiki et fontaines |
| 7 | SIGNATURE OMBRE | signer un message (RSA) |
| 8 | BTC LOOKUP | solde et transactions d'une adresse |
| 9 | MOTEUR DE FUITE | email/pseudo sur 4 sources |
| 0 | TRACE BRÛLÉE | ce que ta machine fuit en clair |

---

## KIT 08 — LASSO VÉRITÉ (vérification · 8 tools)
```
cd ~/Desktop/tool_DC/LassoVerite && python3 lasso_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | VÉRITÉ FICHIER | hash + comparaison de référence |
| 2 | VÉRITÉ TLS | certificat : émetteur, validité |
| 3 | VÉRITÉ EMAIL | SPF/DKIM/DMARC d'un header |
| 4 | VÉRITÉ IMAGE | GPS, appareil, empreinte |
| 5 | VÉRITÉ SITE | HSTS/CSP : protections |
| 6 | VÉRITÉ URL | démêler les redirections |
| 7 | VÉRITÉ PERSONNE | consistance d'un pseudo |
| 8 | VÉRITÉ RÉSEAU | DNSSEC : la zone signe-t-elle ? |

---

## KIT 09 — CYBORG (intégration · 8 tools)
```
cd ~/Desktop/tool_DC/CyborgTech && python3 cyborg_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | API STRIKE | tester un endpoint REST |
| 2 | WEBHOOK FORGE | serveur qui reçoit les webhooks |
| 3 | JSON X-RAY | valider + extraire du JSON |
| 4 | CRON FORGE | planifier des tâches (crontab) |
| 5 | PORT GUARD | veille : action quand un port s'ouvre |
| 6 | TECH SCAN | robots/sitemap/headers d'un site |
| 7 | AUTOMATON | surveille un dossier, agit au changement |
| 8 | NANO-REPAIR | santé du volume et du FS |

---

## KIT 10 — LEXCORP (arsenal Windows · 7 modules)
```
cd ~/Desktop/tool_DC/LexCorpIndustries && zsh verify_lex.zsh
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | LEX_INJECT_DLL | injection | VirtualAllocEx + CreateRemoteThread → LoadLibrary |
| 2 | LEX_HOLLOW | process hollowing | créer suspendu, démapper, écrire son PE |
| 3 | LEX_APC | APC injection | shellcode dans un thread suspendu |
| 4 | LEX_RANSOM2 | ransomware | shadow copies supprimées + AES partiel + decrypt |
| 5 | LEX_SMB_WORM | worm SMB | sweep /24 + drop + tâche distante |
| 6 | LEX_CRYPTER | crypter | packer RC4 → loader généré, strings xorées |
| 7 | LEX_TEST_DLL | preuve | DLL MessageBox à l'attach |


## KIT 11 — S.T.A.R. LABS (C2 DNS + HTTP · 5 tools)
```
cd ~/Desktop/tool_DC/STARLabs && python3 star_c2_server.py 8090
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | DNS C2 SERVER | DNS tunneling | commandes dans les réponses DNS (testé live ✓) |
| 2 | DNS C2 AGENT | agent DNS | reçoit les commandes par DNS, exécute |
| 3 | C2 FRAMEWORK | HTTP C2 | multi-agents, push par URL, jitter (testé ✓) |
| 4 | INFOSTEALER | infostealer | scan 3 navigateurs, export RC4 chiffré |
| 5 | EVASION | anti-analysis | PT_DENY_ATTACH + strings xor + exec mémoire W^X |


## KIT 12 — TASK FORCE X (déploiement · 2 tools)
```
cd ~/Desktop/tool_DC/TaskForceX && python3 taskforce_ssh_worm.py
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | SSH WORM | propagation | known_hosts + ARP → authorized_keys injection |
| 2 | MODULE ANDROID | APK | LexService : C2 check-in, START_STICKY, boot receiver |


## KIT 13 — NEO / LA MATRICE (10 tools)
```
cd ~/Desktop/tool_DC/NeoMatrix && python3 neo_tool.py
```
Intro : pluie de code → « Wake up, Maxime... » → pilule rouge/bleue
| # | Tool | Thème |
|---|---|---|
| 1 | SOURCE VISION | flux du système en direct |
| 2 | IMAGE RÉSIDUELLE | ta trace actuelle |
| 3 | CONSTRUCT LOADER | payload C2 paramétré généré |
| 4 | AGENT SMITH HUNT | processus anormalement dupliqués |
| 5 | ZION UPLINK | test de liaison avec le C2 |
| 6 | THE KEYMAKER | paire RSA complète |
| 7 | TRACE DESTROY | efface l'historique terminal |
| 8 | WHITE RABBIT | démêler les redirections d'URL |
| 9 | THE ORACLE | un message qui tombe juste |
| 0 | DEFENSIVE PROGRAM | rapport défensif (pilule bleue) |

---

## KIT 14 — LA FORCE (8 tools)
```
cd ~/Desktop/tool_DC/ForceGalaxy && python3 force_tool.py
```
Intro : hyper-espace → défilé jaune → allumage de sabre
| # | Tool | Thème |
|---|---|---|
| 1 | HOLOCRON | archive totale de la machine |
| 2 | SITH INFILTRATOR | reverse shell via RickPortal |
| 3 | FORCE CHOKE | figer/libérer un processus |
| 4 | DROID SWEEP | ping + 5 ports sur chaque vivant |
| 5 | DEATH STAR TARGETING | triple tir sur host:port |
| 6 | JEDI MIND TRICK | 3 prétextes paramétrés |
| 7 | KYBER CRYSTAL | 3 clés AES dérivées (PBKDF2) |
| 8 | BLASTER DEFLECT | lecture + règles firewall pf |

---

## KIT 15 — CATWOMAN (secrets · 8 tools)
```
cd ~/Desktop/tool_DC/CatwomanVoleuse && python3 catwoman_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | WIFI KEYS | clés wifi du trousseau |
| 2 | BROWSER VAULT | historique/logins/cookies 3 navigateurs |
| 3 | KEYCHAIN AUDIT | objets du trousseau système |
| 4 | SSH COLLECTOR | clés privées/publiques SSH |
| 5 | SECRETS SCAN | API keys/tokens dans les fichiers |
| 6 | SESSION THIEF | export cookies reimportable |
| 7 | DPAPI WINDOWS | extracteur réel Chrome (CryptUnprotectData) |
| 8 | CLIP PREMIUM | presse-papiers + détection mots de passe |

---

## KIT 16 — H.I.V.E. (minage · 8 tools)
```
cd ~/Desktop/tool_DC/HiveMining && python3 ruche_tool.py
```
| # | Tool | Thème |
|---|---|---|
| 1 | POW MINER | minage PoW réel SHA-256 (1,95 Mh/s vérifié) |
| 2 | XMRIG RÉEL | vrai miner Monero + config wallet/pool |
| 3 | CRYPTOJACKER | payload discret X% CPU + LaunchAgent |
| 4 | WALLET WATCH | soldes d'adresses BTC surveillées |
| 5 | MINER HUNTER | détecte les mineurs étrangers |
| 6 | PROFIT CALC | hashrate → revenu estimé BTC/EUR |
| 7 | BOT FACTORY | scripts de déploiement par machine |
| 8 | COORDONNATEUR | dashboard flotte live (vérifié 3/3 ✓) |

---

## KIT 17 — SCARECROW (phishing · 12 sites)
```
cd ~/Desktop/tool_DC/ScarecrowPhish && python3 epouvanteur.py
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | MICROSOFT MIROIR | phishing pixel-perfect | le vrai login MS reflété, capture pendant la frappe |
| 2 | TRICK FORGE | 12 sites | gmail, facebook, instagram, twitter, linkedin, netflix, paypal, steam, github, snapchat, tiktok, outlook |
| 3 | LIEN PUBLIC | tunnel cloudflare | lien utilisable de partout |
| 4 | CAPTURES | harvest | identifiants + IP + UA → captures.json (testé ✓) |
| 5 | OEIL | viewer | vue live des captures (rafraîchi 1,5 s) |
| 6 | MIRROR PROXY | multi-domaines | proxy inverse du vrai flux MS multi-étapes (v2) |


## KIT 18 — WARWORLD (arsenal · 110 armes / 16 thèmes)
```
cd ~/Desktop/tool_DC/WarWorld && python3 warworld_cmd.py
```
| # | Thème | Armé |
|---|---|---|
| 1 | RECONNAISSANCE | 6 |
| 2 | EXPLOITATION WEB | 6 |
| 3 | RÉSEAU & INFRA | 6 |
| 4 | MALWARE & RANSOMWARE | 7 |
| 5 | INGÉNIERIE SOCIALE | 5 |
| 6 | WIRELESS & RF | 6 |
| 7 | HARDWARE & BADUSB | 10 |
| 8 | MOBILE | 5 |
| 9 | CLOUD | 4 |
| 10 | DÉTECTION & DFIR | 6 |
| 11 | CRYPTO & CACHAGE | 5 |
| 12 | POSTURE & C2 | 5 |
| 13 | OPEN-SOURCE & GITHUB | 13 |
| 14 | ESP32 & DIY | 7 |
| 15 | RESSOURCES FERMÉES | 7 |
| 16 | EXOTIQUE & RÉSERVE | 12 |
**Statuts** : [LAB] 21 · [REF] 57 · [ACHAT] 24 · [FERMÉ] 9 · Web + CMD avec liens magasin

---

## KIT 19 — LIGNE ROUGE (orchestrateur · 3 commands)
```
cd ~/Desktop/tool_DC/LeagueOfShadows && python3 league.py plan <nom> [site]
```
| # | Commande | Thème | Description |
|---|---|---|---|
| 1 | plan | orchestration | planifie la campagne en 4 steps (PHISHING → DROPPER → C2 → SURVEILLANCE) |
| 2 | run | exécution | lance tout : phishing + dropper + C2 + surveillance live (captures/sessions/10s) |
| 3 | report | documentation | RAPPORT.md avec captures (IP+creds), sessions, recommandations |


## KIT 20 — KRYPTONITE SUITE (défense · 4 tools)
```
cd ~/Desktop/tool_DC/KryptoniteSuite && python3 kryptonite.py scan
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | scan | détection | machine vs IOCs des 20 kits (chemins, fichiers, process, ports) |
| 2 | sigma | détection | 8 règles Sigma par kit → import Elastic/Splunk (testé ✓) |
| 3 | yara | détection | 5 règles YARA sur les strings d'agents (testé ✓) |
| 4 | catalog | référence | le JSON des IOCs complets des 20 kits |


## KIT 21 — W.O.P.R. (auto-lab WarGames · 4 commands)
```
cd ~/Desktop/tool_DC/WOPR && python3 wopr.py play
```
| # | Commande | Thème | Description |
|---|---|---|---|
| 1 | play | intro | morpion + SHALL WE PLAY A GAME? tapé lettre par lettre |
| 2 | build | lab | cible vulnérable :8090 (SQLi/traversal/RCE) + 4 flags + missions |
| 3 | serve | CTF | cible + scoreboard :8091 — POST /submit?f=FLAG{...} (testé ✓) |
| 4 | destroy | nettoyage | efface le lab complètement |


## KIT 22 — THE CALCULATOR (breach analytics · 2 tools)
```
cd ~/Desktop/tool_DC/TheCalculator && python3 calculator.py serve 8094
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | stats | analyse | par secteur (Internet 3,59Md · Social 2,0Md), par année, top 8 |
| 2 | serve | web | barres par secteur + timeline des 23 breaches (2004→2026) |


## KIT 23 — RAVEN (évasion EDR · 5 modules)
```
cd ~/Desktop/tool_DC/RavenEvasion && zsh verify_raven.zsh
```
| # | Module | Thème | Description |
|---|---|---|---|
| 1 | SYSCALLS DIRECT | Hell's Gate | SSN depuis ntdll disque, stubs syscall en mémoire |
| 2 | UNHOOK NTDLL | unhooking | restaure ntdll au code original Microsoft |
| 3 | ETW + AMSI | télémétrie | EtwEventWrite ← ret · AmsiScanBuffer ← CLEAN |
| 4 | SLEEP OBFUSCATION | mémoire | pages chiffrées pendant le repos, RX à l'exécution |
| 5 | STACK SPOOFING | call stack | chaîne de retour remplacée par CreateFileA |


## KIT 24 — THE THINKER (reverse engineering · 8 commands)
```
cd ~/Desktop/tool_DC/TheThinker && python3 thinker.py arsenal
```
| # | Commande | Thème | Description |
|---|---|---|---|
| 1 | analyze | fiche | type, headers r2, sections, imports, test UPX |
| 2 | strings | strings | URLs, IPs, chemins, mots chauds filtrés |
| 3 | imports | imports | DLL/fonctions (PE via objdump) ou nm/otool (Mach-O) |
| 4 | unpack | dépack | dépacke UPX → .unpacked |
| 5 | r2 | radare2 | passthrough (aaa, afl, pdf main, iz…) |
| 6 | watch | dynamique | fichiers ouverts d'un process en live |
| 7 | diff | versioning | diff de strings entre 2 builds |
| 8 | arsenal | référence | Ghidra (NSA), radare2, x64dbg, FLARE-VM, Capstone, IDA… |


## KIT 25 — JOKER CARD (SGP Card · BadUSB · 4 tools)
```
cd ~/Desktop/tool_DC/JokerCard && python3 joker_forge.py <c2>
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | JOKER FORGE | payloads | cuit les 5 payloads BadUSB avec ton C2 |
| 2 | FIRMWARE | Ducky-lite | interpréteur autonome (LED + buzzer + SW4 relance) |
| 3 | WEB UI | Payload Manager | éditeur + save LittleFS + run HID à distance |
| 4 | RAPPORT | audit | RAPPORT_SGP_JOKER.md (architecture complète) |


## KIT 26 — DAILY PLANET (veille · 25 sources · 3 tools)
```
cd ~/Desktop/tool_DC/DailyPlanet && python3 veille.py serve 8088
```
| # | Tool | Thème | Description |
|---|---|---|---|
| 1 | serve | web journal | 644 actus / 25 sources / filtres CYBER-TECH-JURIDIQUE / recherche |
| 2 | top | terminal | les N dernières colorées par catégorie |
| 3 | notifs | notifications | notif macOS à chaque actu cyber (veille_notifs.py start) |


═══════════════════════════════════════════════════════════════
  TOTAL : 26 KITS · ~240 TOOLS · TOUT DANS ~/Desktop/tool_DC/
  LE COCKPIT : double-clic DC.command OU http://127.0.0.1:9000
═══════════════════════════════════════════════════════════════
