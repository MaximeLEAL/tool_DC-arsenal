# H.I.V.E. — LA RUCHE · powered by Maxime Leal

6 tools de minage crypto (ta machine, ton wallet, tes labos). Lancement : `RUCHE.command`
Touches : `1`–`6`, `s` (l'essaim), `q`.

## 1 — POW MINER · minage PoW RÉEL : recherche de nonce SHA-256 sous difficulté réglable (`python3 ruche_pow.py 20`). Ta machine fait ~1 955 000 h/s vérifié. Difficulté 16-20 = blocs trouvés en quelques secondes.
## 2 — XMRIG RÉEL · **vrai miner Monero** : installe xmrig (brew), configure pool+wallet (`./ruche_xmrig.sh <wallet>`), 50% CPU, Ctrl+C pour stopper. Ton wallet, ton pool, ta machine.
## 3 — CRYPTOJACKER · génère le payload-ruche : mineur discret à X% CPU + persistance LaunchAgent (Nice 10). Arrêt : `launchctl unload ~/Library/LaunchAgents/com.apple.hivesync.plist`
## 4 — WALLET WATCH · soldes/transactions d'adresses BTC surveillées (API blockchain.info)
## 5 — MINER HUNTER · détecte les mineurs étrangers sur une machine (signatures + CPU>80%)
## 6 — PROFIT CALC · hashrate → part du réseau → revenu BTC/EUR estimé


## V2 — LA FABRIQUE D'ESSAIM · powered by Maxime Leal

### 7 — BOT FACTORY (`ruche_bots.py`)
Génère les scripts de déploiement des bots mineurs pour ta flotte (TES machines) :
```
python3 ruche_bots.py <wallet_xmr> 127.0.0.1:8096 macbook-air vm-windows serveur-lab
```
→ `sorties/bots/bot_<nom>.sh` par machine : install xmrig, config (pool auto-switch
MoneroOcean, 60% CPU, priorité basse), **beacon de statut** vers le coordonnateur toutes les 60 s.
Déploiement : `scp bot_<nom>.sh cible: && zsh bot_<nom>.sh`.

### 8 — COORDONNATEUR (`ruche_coordo.py`, port 8096)
Le cerveau de la ruche : reçoit les beacons (bot/host/état/uptime), dashboard web live :
```
python3 ruche_coordo.py 8096
open http://127.0.0.1:8096/dashboard
```
Table : bot · host · état (EN LIGNE / silence) · hashrate estimé · uptime · dernier rapport.
Bandeau : bots en ligne, hashrate de flotte, revenu XMR/j + $ (prix coingecko live).
Vérifié réel : 3 bots simulés → « 3 en ligne / 3 », flotte 7 500 h/s ✓.

### LA VÉRITÉ DES CHIFFRES (calculé en réel ce jour)
| Grandeur | Valeur |
|---|---|
| Ton MacBook (RandomX réel) | ~2 500 h/s |
| Réseau Monero | ~2,8 GH/s |
| Ta part | 0,00009 % |
| Revenu | **0,000386 XMR/j ≈ $0,18/j ≈ $5,44/mois** |
| Conso | ~0,5 kWh/jour |

Lecture honnête : un laptop ne fait pas d'argent en minant — ça couvre à peine
l'électricité. Les leviers : matériel dédié (ASIC/GPU), machines dont tu ne paies
pas le courant (et pour le reste, tu connais la frontière du lab), ou le pool
auto-switch MoneroOcean qui mine la monnaie la plus rentable.
