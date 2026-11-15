# LIGNE ROUGE — LEAGUE OF SHADOWS · powered by Maxime Leal
L'orchestrateur : la campagne complete en une commande.
## plan
`python3 league.py plan <nom> [site]` — cree campagnes/<nom>/campagne.json : 4 steps (PHISHING → DROPPER → C2 → SURVEILLANCE)
## run
`python3 league.py run <nom> [minutes]` — l'ordre d'execution optimal :
1. C2 d'abord (Arkham :4444 + console :5050)  2. page de capture Scarecrow + tunnel public
3. forge de l'installateur-leurre  4. monitoring live : captures + sessions affichees toutes les 10 s
## report
`python3 league.py report <nom>` — RAPPORT.md : parametres, captures (IP + creds + heure), sessions C2, recommandations blue team.
Perimetre : lab autorise.
