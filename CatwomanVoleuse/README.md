# CATWOMAN — LA VOLEUSE · powered by Maxime Leal

8 tools de secrets, sur une machine que tu possèdes (lab). Lancement : `CAT.command`
Touches : `1`–`8`, `j` (bijoux), `c` (griffes), `q`.

## 1 — WIFI KEYS · clés wifi stockées (trousseau) — dialogue de consentement par clé
## 2 — BROWSER VAULT · historique/logins/cookies des 3 navigateurs → `sorties/butin_navigateurs.json`
## 3 — KEYCHAIN AUDIT · objets génériques du trousseau système
## 4 — SSH COLLECTOR · clés privées/publiques → `sorties/butin_ssh.json`
## 5 — SECRETS SCAN · peigne API keys/tokens (AWS, GitHub, Slack, JWT…) dans tes fichiers
## 6 — SESSION THIEF · export cookies horodaté → `sorties/sessions.json`
## 7 — DPAPI WINDOWS · l'extracteur réel Windows (`build/cat_dpapi.exe`, cross-compilé ✓) :
    récupère la clé maître AES de Chrome via CryptUnprotectData (Local State "encrypted_key")
## 8 — CLIP PREMIUM · presse-papiers horodaté + détection de mots de passe collés
