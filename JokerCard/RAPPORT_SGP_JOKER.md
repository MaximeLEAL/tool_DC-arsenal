# RAPPORT TECHNIQUE — SGP CARD JOKER · powered by Maxime Leal
# ESP32-S3-MINI-1-N8 · firmware v1.0 · audit vs documentation officielle

Date : 15 nov 2026 · Sources : doc fournie + page officielle sgpcard.com (lue en direct).
Code source : **non fourni** — `SGP_Card_Joker.ino`, `config.h`, `web_ui.h` ne sont pas sur le banc.
⚠ Sans le repo, aucun élément ne peut recevoir le statut CONFIRMÉ DANS LE CODE.
   Dépose le repo dans `tool_DC/JokerCard/firmware_repo/` et je re-passe le rapport au peigne fin.

────────────────────────────────────────────────────────────────
1. FONCTIONNALITÉS DÉJÀ IMPLÉMENTÉES (selon docs + page officielle)
────────────────────────────────────────────────────────────────
| Fonction | Statut |
|---|---|
| 10 modules (NFC, WiFi Lab, BLE, BadUSB, GPIO, RGB, Buzzer, Storage, Console, Settings) | DOCUMENTÉ MAIS NON VÉRIFIÉ |
| Panel web 192.168.4.1 + AP SGP-JOKER-XXXX | DOCUMENTÉ MAIS NON VÉRIFIÉ |
| WebSocket live logs (Console) | DOCUMENTÉ MAIS NON VÉRIFIÉ |
| Empreinte de compilation officielle : 1.41 MB (42%) flash, 81 KB RAM, core 3.3.8 | DOCUMENTÉ MAIS NON VÉRIFIÉ |
| Interpréteur Ducky-lite (BadUSB) | DOCUMENTÉ MAIS NON VÉRIFIÉ — syntaxe exacte inconnue |

Indice fort (pas une preuve code) : la page officielle publie les commandes arduino-cli
vérifiées « clean » — les 10 modules existent très probablement. Mais probable ≠ confirmé.

────────────────────────────────────────────────────────────────
2. DOCUMENTÉ MAIS ABSENT DE MON ACCÈS (vérification impossible sans repo)
────────────────────────────────────────────────────────────────
- Implémentation exacte des 10 modules (APIs internes, routes web, handlers)
- Syntaxe exacte de l'interpréteur Ducky-lite (écarts possibles vs DuckyScript standard)
- Mécanisme d'upload LittleFS du panel (routes /save etc. — mes snippets sont à brancher)
- Format des captures NFC sauvées
- Gestion d'énergie réelle (deep sleep, jauge — doc dit « non spécifiée »)

────────────────────────────────────────────────────────────────
3. BIBLIOTHÈQUES ET DÉPENDANCES
────────────────────────────────────────────────────────────────
| Lib | Version installée ici | Statut |
|---|---|---|
| arduino-esp32 core | 3.3.12 (doc recommande 3.x) | ✓ installé sur ce banc |
| Adafruit PN532 | 1.3.4 | ✓ installé |
| Adafruit NeoPixel | 1.15.5 | ✓ installé + utilisé par mon sketch |
| ArduinoJson | 7.4.3 | ✓ installé |
| WebSockets | 2.7.2 | ✓ installé |
| USB (Keyboard HID) | incluse core 3.3.12 — API `USBHIDKeyboard` (Keyboard.h 2.x n'existe plus) | CONFIRMÉ SUR CE BANC (compilation) |

Découverte de compilation : le core 3.x a retiré `ledcSetup`/`ledcAttachPin` → API `ledcAttach(pin,freq,res)` / `ledcWriteTone(pin,freq)`. Toute migration de firmware v1.0 vers core 3.x devra corriger ça.

────────────────────────────────────────────────────────────────
4. GPIO RÉELLEMENT DISPONIBLES
────────────────────────────────────────────────────────────────
Occupés (officiels, à ne PAS réassigner) :
GPIO10 RGB · GPIO1 buzzer · GPIO5/6 I²C PN532 (addr 0x24) · GPIO9 bouton user ·
GPIO0 BOOT · GPIO19/20 USB.

Libres (breakout 14 pins) : 48, 34, 33, 47, 26, 35, 36, 37, 38, 39, 40, 8, 7, 3.
Piège confirmé par la doc officielle : la soie PCB « IO27 » = GPIO47 (le S3-MINI ne
bond-out pas GPIO27). Statut : DOCUMENTÉ MAIS NON VÉRIFIÉ au multimètre.

────────────────────────────────────────────────────────────────
5. LIMITATIONS MATÉRIELLES (NON DISPONIBLE — absents du produit)
────────────────────────────────────────────────────────────────
CC1101 sub-GHz · SX1262/SX1278 LoRa · IR · lecteur microSD · microphone dédié ·
jauge de batterie. Aucun code ne doit les présupposer. Capacité/runtimes batterie :
non documentés — je n'invente pas.

Contraintes actives : WiFi = PASSIF uniquement (observation/comptage, pas de
déauth émis, pas de spoof) · NFC limité aux tags compatibles sans auth cryptographique ·
GPIO strictement 3.3 V · PSU mono-cell LiPo + TP4056.

────────────────────────────────────────────────────────────────
6. POSSIBILITÉS D'EXTENSION (compatibles, hors zone interdite)
────────────────────────────────────────────────────────────────
- Payload Manager dans le panel (mon snippet webui/ — à brancher sur les routes réelles)
- Inventaire WiFi/BLE exportable CSV/JSON, stats canaux, détection d'anomalies
- Historique NFC, viewer de tags, export
- Interpréteur Ducky-lite étendu (mon sketch autonome : compilé ✓ 415 889 o (12%) flash,
  55 KB (16%) RAM — CONFIRMÉ SUR CE BANC, non flashé sur hardware)
- Capteurs sur le breakout (I²C/SPI libres), logique-monitor
- Dashboard santé, optimisation LittleFS

────────────────────────────────────────────────────────────────
7. PROBLÈMES DE SÉCURITÉ
────────────────────────────────────────────────────────────────
- Mot de passe AP par défaut `joker12345678` publié — à changer (Settings), sinon
  n'importe qui à portée prend le contrôle du panel
- Le panel est un point d'accès ouvert : ne jamais le bridger vers un réseau routé
- Le BadUSB est un clavier réel : payload = responsabilité de son auteur
- Format LittleFS : destructif — confirmation obligatoire côté UI
- Ma recommandation : secret AP fort + désactivation auto du WiFi quand inutile

────────────────────────────────────────────────────────────────
8. OPTIMISATIONS POSSIBLES
────────────────────────────────────────────────────────────────
- PSRAM désactivé (8 MB flash suffisent) — garder
- Precompiler web_ui.h en gzip PROGMEM (le panel est la plus lourde ressource flash)
- Polling PN532 : dormir entre les scans (batterie), LEDC low-power en veille
- Différer l'init BLE (économie) — scan à la demande seulement
- File d'événements WebSocket bornée (éviter la fuite mémoire sur les logs longs)

────────────────────────────────────────────────────────────────
SYNTHÈSE : 0 CONFIRMÉ DANS LE CODE (pas de repo fourni) · tout le reste
DOCUMENTÉ MAIS NON VÉRIFIÉ ou NON DISPONIBLE. Le seul CONFIRMÉ de ce banc :
mon sketch `JokerPayloadExec` compile (12% flash) contre le core 3.3.12 avec les
libs officielles — pas encore flashé sur la carte.
