# LASSO DE LA VERITE — powered by Maxime Leal

8 tools de vérification : le lasso révèle ce qui est vrai — fichiers, certificats, emails, images, sites, URLs, identités, zones DNS.
Lancement : double-clic `VERITE.command`.

## 1 — VERITE FICHIER
**Quoi** : hash md5/sha256 d'un fichier + comparaison à un hash de référence. Verdict : `[VERITE]` ou `[MENTI]`.
**Usage** : `[1]` → chemin du fichier → hash de référence (ou Entrée pour seulement mesurer).

## 2 — VERITE TLS
**Quoi** : sujet, émetteur, chaîne de vérification et dates de validité du certificat d'un host.
**Usage** : `[2]` → `exemple.com`.

## 3 — VERITE EMAIL
**Quoi** : analyse les mécanismes d'authentification d'un header email (SPF/DKIM/DMARC). Échec = email forgé.
**Usage** : `[3]` → colle les headers complets, ligne vide pour finir.

## 4 — VERITE IMAGE
**Quoi** : GPS, appareil photo, date de l'image + empreinte perceptuelle (miniature 16px hashée) pour détecter les re-publications.
**Usage** : `[4]` → chemin de l'image.

## 5 — VERITE SITE
**Quoi** : HSTS, CSP, X-Frame — les protections que le site annonce. Absence = site qui n'assume pas ses visiteurs.
**Usage** : `[5]` → URL.

## 6 — VERITE URL
**Quoi** : démêle la chaîne complète de redirections d'un lien (raccourcisseurs bit.ly etc.).
**Usage** : `[6]` → URL courte. La destination finale est dans les headers `Location`.

## 7 — VERITE PERSONNE
**Quoi** : génère les URLs des profils d'un pseudo sur 5 plateformes — la cohérence du pseudo est une preuve.
**Usage** : `[7]` → pseudo.

## 8 — VERITE RESEAU
**Quoi** : vérifie DNSSEC — une zone signée ne peut pas mentir sur ses réponses.
**Usage** : `[8]` → domaine.
