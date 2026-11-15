# W.O.P.R. — SHALL WE PLAY A GAME? · powered by Maxime Leal
L'auto-lab : une commande construit un CTF complet (sans Docker).
## play
`python3 wopr.py play` — l'intro : morpion + SHALL WE PLAY A GAME?
## build
`python3 wopr.py build` — cree WOPR_Lab/ : cible vulnérable (SQLi /login · traversal /files · RCE /cmd) + 4 flags + missions.json
## serve
`python3 wopr.py serve` — cible :8090 + scoreboard :8091. Les missions : injection SQL (le flag de la base), traversal ../flags/, RCE /cmd?c=, et libre. POST /submit?f=FLAG{...} marque le scoreboard. TESTE : SQLi → FLAG{ALPHA-9442} ✓ · traversal ✓ · RCE whoami ✓
## destroy
`python3 wopr.py destroy` — efface tout.
Les cibles avancées (upload, services additionnels) : étages suivants — les kits existants s'y branchent (RickPortal C2, Scarecrow pages).
