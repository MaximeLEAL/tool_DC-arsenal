# CYBORG TECHNET — powered by Maxime Leal

8 tools d'intégration : API, webhooks, JSON, automatisation, santé système.
Lancement : double-clic `CYBORG.command`.

## 1 — API STRIKE
**Quoi** : test REST complet : GET/POST/PUT/DELETE avec body JSON.
**Usage** : `[1]` → méthode → URL → body. Réponse brute affichée.

## 2 — WEBHOOK FORGE
**Quoi** : génère et (option) lance un serveur local qui reçoit tout webhook et le logge (IP, path, body).
**Usage** : `[2]` → fichier créé `sorties/webhook_server.py` → `python3 sorties/webhook_server.py` → écoute sur `:8083`, log dans `webhooks.log`.

## 3 — JSON X-RAY
**Quoi** : valide un JSON et extrait un chemin (`a.b.0.c`).
**Usage** : `[3]` → JSON collé ou chemin de fichier → chemin d'extraction optionnel.

## 4 — CRON FORGE
**Quoi** : liste tes crontabs + en crée (`*/5 * * * * commande`).
**Usage** : `[4]` → plan cron → commande. Syntaxe plan : `min heure jour mois jour-semaine`.

## 5 — PORT GUARD
**Quoi** : veille un port local ; dès qu'il s'ouvre, déclenche une commande (defaut : `say 'port ouvert'`).
**Usage** : `[5]` → port → action. Ctrl+C pour arrêter la veille.

## 6 — TECH SCAN
**Quoi** : robots.txt, sitemap.xml et headers d'un site — les plaques d'immatriculation des technos.
**Usage** : `[6]` → URL.

## 7 — AUTOMATON
**Quoi** : surveille un dossier (polling 2 s) et exécute une commande à chaque changement.
**Usage** : `[7]` → dossier → commande. Ctrl+C pour stopper.

## 8 — NANO-REPAIR
**Quoi** : `diskutil verifyVolume` + état du système de fichiers — la santé du corps techno.
**Usage** : `[8]`. Rien à saisir.
