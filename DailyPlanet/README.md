# DAILY PLANET — LA VEILLE TECH & CYBER · powered by Maxime Leal

L'agrégateur de presse : **10 sources tech & cybersécurité** (FR + EN) collectées en direct,
dédoublonnées, classées (CYBER / TECH FR / TECH / CVE & ALERTES), servies dans un **journal
web** au look Daily Planet, avec recherche, filtres et badges HOT.

## LANCEMENT
```
cd ~/Desktop/tool_DC/DailyPlanet
python3 veille.py serve 8088        # page web → http://127.0.0.1:8088
python3 veille.py top 15            # les 15 dernières dans le terminal (couleurs)
```
La page web : masthead DAILY PLANET, chips de filtres (TOUTES · CYBER · TECH FR · TECH ·
CVE & ALERTES), champ de recherche, cartes avec source + ancienneté + résumé + lien vers
l'article original. Rafraîchi automatiquement (cache 15 min + re-collecte en tâche de fond).

## LES SOURCES — 25, panel élargi (vérifiées vivantes)
| Catégorie | Sources |
|---|---|
| **CYBER** (377 art.) | The Hacker News · BleepingComputer · KrebsOnSecurity · Dark Reading · SecurityWeek · Malwarebytes Labs · Unit42 PaloAlto · WeLiveSecurity (ESET) · ZATAZ · GitHub Security |
| **CVE & ALERTES** (9) | CISA · CERT-FR |
| **JURIDIQUE** (10) | CNIL — privacy, RGPD, sanctions |
| **TECH** (128) | Ars Technica · TechCrunch · The Verge · Wired · Engadget · HN frontpage · MIT Tech Review |
| **TECH FR** (120) | Korben · NextINpact · IT-Connect · LeMondeInformatique · Frandroid |

Ajouter une source : une ligne dans `FEEDS` :
```python
"Nom": ("https://site.example/feed", "categorie"),
```

## VÉRIFIÉ RÉEL (ce jour)
- **175 actualités agrégées, 10 sources** ✓
- filtres par catégorie 200 ✓ · recherche (ex `ransomware`) 200 ✓
- mode terminal `top` : titres colorés par catégorie ✓
- badges HOT automatiques (ransomware, 0-day, CVE, exploit, breach…)

## AJOUTER UNE SOURCE
Dans `veille.py`, dictionnaire `FEEDS` :
```python
"Nom Source": ("https://site.example/feed", "cyber"),
```
Les catégories de base : `cyber`, `tech-fr`, `tech`, `alertes` — le classement auto
reclasse en `cyber` si le titre contient des mots chauds (ransomware, CVE, exploit…).

## DONNÉES
Cache : `veille_cache.json` (15 min TTL) — la page se rafraîchit toutes les 5 min,
la re-collecte complète tourne en tâche de fond, aucune source n'est martelée.
