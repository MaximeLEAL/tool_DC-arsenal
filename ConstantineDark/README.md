# CONSTANTINE — LA CASE DE L'OMBRE · powered by Maxime Leal

Kit dark web — recherche et analyse uniquement, sur des ressources autorisées.
Tor requis pour les tools onion — le kit l'installe tout seul (tool 02).
Lancement : double-clic `CONSTANTINE.command`.

---

## 01 — STATUS TOR
**Quoi** : vérifie si tor tourne, affiche ton IP de sortie tor, puis ton IP réelle en clair pour comparaison.
**Usage** : `[1]` + Entrée. Rien à saisir.
**Sortie** : `sortie tor : {"IP": x.x.x.x}` — si cette IP ≠ ton IP réelle, tu es bien derrière tor.

## 02 — INSTALLER TOR
**Quoi** : `brew install tor` + démarrage du service (port SOCKS 9050).
**Usage** : `[2]`. Tourne une fois, ensuite tor démarre à chaque login.
**Sortie** : `tor ACTIF`.

## 03 — FETCH ONION
**Quoi** : récupère une page `.onion` via tor et la sauvegarde.
**Usage** : `[3]` → colle une URL `.onion` (ex `http://expyuzz4wqqyqhjn.onion`).
**Sortie** : les 600 premiers caractères du texte + `sorties/onion_page.html` (ouvre-le dans un navigateur pour la mise en forme).
**Note** : les onions meurent souvent — page vide = adresse morte.

## 04 — DARK CRAWLER
**Quoi** : crawler 1 niveau : depuis une onion de départ, il suit les liens `.onion` trouvés (max 30 pages).
**Usage** : `[4]` → URL de départ (un annuaire comme la Hidden Wiki marche bien).
**Sortie** : `sorties/crawl.log` — chaque ligne : `url | titre de page`.

## 05 — RECHERCHE OMBRE
**Quoi** : interroge **Ahmia** (moteur d'index onion accessible du web clair).
**Usage** : `[5]` → mots-clés (ex `marketplace`).
**Sortie** : URL + titre des onions correspondantes.

## 06 — ANNUAIRES
**Quoi** : liste des annuaires vivants (Hidden Wiki, Torch…) + extraction des liens d'un annuaire au choix.
**Usage** : `[6]` → colle l'URL d'un annuaire (ou Entrée pour passer).

## 07 — SIGNATURE OMBRE
**Quoi** : crée une identité cryptographique (clé RSA via openssl) et **signe un message** — n'importe qui avec ta clé publique vérifie que c'est toi, sans savoir qui tu es.
**Usage** : `[7]` → ton message. La signature : `sorties/msg.sig`.
**Vérification** : la machine qui reçoit fait
`openssl dgst -sha256 -verify cle_publique.pem -signature msg.sig msg.txt` → `Verified OK`.

## 08 — BTC LOOKUP
**Quoi** : solde, total reçu, nombre de transactions d'une adresse Bitcoin (API blockchain.info, web clair).
**Usage** : `[8]` → adresse BTC.
**Sortie** : solde BTC + les 5 dernières transactions avec leur hash.

## 09 — MOTEUR DE FUITE
**Quoi** : sondage multi-source d'un email/pseudo sur 4 moteurs de fuites (pastes inclus en direct).
**Usage** : `[9]` → email ou pseudo.
**Sortie** : liens des 4 sources + les pastes trouvés automatiquement.

## 10 — TRACE BRÛLÉE
**Quoi** : montre ce que TA machine fuit en clair : IP publique, headers HTTP, resolver DNS.
**Usage** : `[10]`. Rien à saisir.
**Lecture** : derrière tor, seule l'IP change — le reste (empreinte du navigateur, timings) demeure.

---

## LEGAL — LA LIGNE DE CONSTANTINE
Ce kit sonde et lit. Il n'achète rien, ne vend rien, ne touche à personne.
Crawler, chercher, observer : la recherche. Le reste est un autre monde — et ce kit n'en fait pas partie.
