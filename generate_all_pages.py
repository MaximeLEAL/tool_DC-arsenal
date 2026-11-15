#!/usr/bin/env python3
# language: Python 3, file: generate_all_pages.py, target: macOS
# Pages web des tools : 26 kits, 1 fiche explicative par tool (rôle + fonctionnement +
# utilisation) avec redirection GitHub. Lance : python3 generate_all_pages.py
import os, re, json, html as H

ROOT = os.path.dirname(os.path.abspath(__file__))
GITHUB = "https://github.com/MaximeLEAL/tool_DC-arsenal"
MD = os.path.join(ROOT, "liste_tool.md")
OUT = os.path.join(ROOT, "arsenal_web_pages")
DATA = os.path.join(ROOT, "arsenal_pages_data")

# n° kit → dossier, nom affiché, couleur, emoji, visage (UNIQUE par kit)
KITS = [
    (1,  "RickPortal",        "RICKPORTAL",       "#00e676", "🟢", "rick_face.jpg"),
    (2,  "FlashToolSuper",    "FLASH TOOL_SUPER", "#ffd60a", "⚡", "flash_face.jpg"),
    (3,  "BatCave",           "BATCAVE",          "#ffd60a", "🦇", "batman_face.jpg"),
    (4,  "JokerChaos",        "JOKER CHAOS",      "#9b30ff", "🃏", "joker_face.jpg"),
    (5,  "TridentAquaman",    "TRIDENT AQUAMAN",  "#40e0d0", "🔱", "aquaman_face.jpg"),
    (6,  "SupermanVision",    "SUPERMAN",         "#ff4628", "🦸", "superman_face.jpg"),
    (7,  "ConstantineDark",   "CONSTANTINE",      "#90ff78", "🕯️", "constantine_face.jpg"),
    (8,  "LassoVerite",       "LASSO VÉRITÉ",     "#ffdc50", "🪢", "wonder_woman_face.jpg"),
    (9,  "CyborgTech",        "CYBORG TECH",      "#00c8ff", "🤖", "cyborg_face.jpg"),
    (10, "LexCorpIndustries", "LEXCORP",          "#39ff14", "🏢", "lex_luthor_face.jpg"),
    (11, "STARLabs",          "S.T.A.R. LABS",    "#00c8ff", "🔬", "starlabs_face.jpg"),
    (12, "TaskForceX",        "TASK FORCE X",     "#ff6a00", "🎯", "taskforce_face.jpg"),
    (13, "NeoMatrix",         "NEO / LA MATRICE", "#00ff70", "💊", "matrix_face.jpg"),
    (14, "ForceGalaxy",       "LA FORCE",         "#ffd60a", "🌟", "force_face.jpg"),
    (15, "CatwomanVoleuse",   "CATWOMAN",         "#ffdc50", "🐱", "catwoman_face.jpg"),
    (16, "HiveMining",        "H.I.V.E.",         "#ffc800", "🍯", "hive_face.jpg"),
    (17, "ScarecrowPhish",    "SCARECROW",        "#ff8c30", "🎃", "scarecrow_face.jpg"),
    (18, "WarWorld",          "WARWORLD",         "#ff4628", "⚔️", "warworld_face.jpg"),
    (19, "LeagueOfShadows",   "LIGNE ROUGE",      "#c9a600", "🥷", "league_face.jpg"),
    (20, "KryptoniteSuite",   "KRYPTONITE SUITE", "#39ff14", "🟩", "kryptonite_face.jpg"),
    (21, "WOPR",              "W.O.P.R.",         "#7fff00", "🎮", "wopr_face.jpg"),
    (22, "TheCalculator",     "THE CALCULATOR",   "#00c8ff", "📊", "calculator_face.jpg"),
    (23, "RavenEvasion",      "RAVEN",            "#8899ff", "🐦‍⬛", "raven_face.jpg"),
    (24, "TheThinker",        "THE THINKER",      "#9b30ff", "🧠", "thinker_face.jpg"),
    (25, "JokerCard",         "JOKER CARD",       "#ff6a00", "🂡", "jokercard_face.jpg"),
    (26, "DailyPlanet",       "DAILY PLANET",     "#64a0ff", "📰", "dailyplanet_face.jpg"),
    (27, "BatWeb",            "BATWEB",           "#4ad66d", "🕸️", None),
]
FACES_REL = "../../gotham_static/faces/"

# ─────────────────────────────────────────────────────────────────────────────
# EXPLICATIONS PAR TYPE DE TOOL — le RÔLE de chaque famille
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "keylogger": {"role": "Un keylogger enregistre chaque frappe au clavier de la machine cible.",
        "how": ["Hook clavier global : chaque touche est interceptée à la source.",
                "Horodatage + nom de la fenêtre active : on sait QUI a tapé quoi et OÙ.",
                "Stockage local dans un fichier log discret, relu plus tard à distance."]},
    "reverse shell": {"role": "Un reverse shell fait que la machine cible appelle l'attaquant et lui donne un shell complet.",
        "how": ["La cible ouvre une connexion sortante (plus facile à filtrer qu'entrante).",
                "L'attaquant écoute sur son port et reçoit le shell interactif.",
                "Reconnexion automatique : si le lien tombe, la cible revient toute seule."]},
    "ransomware": {"role": "Un ransomware chiffre les fichiers de la victime et demande une rançon pour la clé.",
        "how": ["Dérivation d'une clé AES-256 depuis le secret de la session.",
                "Chiffrement des fichiers ciblés par extension, renommés .morty.",
                "Mode decrypt inclus : la même clé rend tout, à des fins de test/pédagogie."]},
    "clipboard": {"role": "Un clip hijacker surveille le presse-papiers et remplace ce qui y passe.",
        "how": ["Poll en boucle du contenu du presse-papiers.",
                "Détection d'adresses crypto (BTC/XMR) copiées.",
                "Remplacement silencieux par l'adresse de l'attaquant avant le collage."]},
    "worm usb": {"role": "Un worm USB se propage de clé USB en clé USB dès qu'une clé est branchée.",
        "how": ["Détection des volumes amovibles insérés.",
                "Copie de lui-même + autorun sur la clé, fichiers cachés.",
                "Exécution auto au branchement suivant : la clé devient le vecteur."]},
    "worm lan": {"role": "Un worm LAN se propage de machine en machine sur le réseau local.",
        "how": ["Scan du /24 pour trouver les hôtes vivants.",
                "Tentative de partage admin (C$, creds faibles) et dépôt du binaire.",
                "Exécution à distance : la machine devient un nouveau point de propagation."]},
    "screenspy": {"role": "Un screen spy prend des captures d'écran périodiques de la victime.",
        "how": ["Capture GDI de l'écran entier en BMP.",
                "Toutes les N secondes, horodatées.",
                "Reliées au C2 pour consultation à distance."]},
    "webcam": {"role": "Un module webcam prend des snapshots silencieux de la caméra.",
        "how": ["Capture VFW (Video For Windows) sans allumer la LED.",
                "Snapshots périodiques JPEG.",
                "Remontés au poste de contrôle."]},
    "micro": {"role": "Un module micro enregistre l'audio ambiant de la machine.",
        "how": ["Enregistrement WAV de 60 secondes en boucle.",
                "Fichiers horodatés, stockés localement.",
                "Récupérables via le canal C2."]},
    "dropper": {"role": "Un dropper est un petit programme dont le seul job est de déposer et lancer la vraie charge utile.",
        "how": ["URL XOR-obfusquée dans le binaire (pas de chaîne en clair).",
                "Download + exécution cachée de la charge.",
                "Installation de la persistance (Run key / LaunchAgent)."]},
    "build": {"role": "Un builder compile tout le kit en un coup, pour macOS ou Windows.",
        "how": ["Compile chaque tool avec les bons flags.",
                "Cross-compile les exes PE Windows depuis le Mac (mingw).",
                "Sort un dossier bin/ prêt à déployer."]},
    "animation": {"role": "Une animation d'ambiance : l'identité visuelle du kit dans le terminal.",
        "how": ["Animation ASCII qui prend toute la fenêtre du terminal.",
                "S'adapte à la taille de la fenêtre en direct.",
                "Purement décoratif — aucune action système."]},
    "osint": {"role": "L'OSINT (renseignement en source ouverte) récolte des infos publiques sur une cible.",
        "how": ["Interrogation de sources publiques (réseaux, whois, APIs geo).",
                "Aucune interaction avec la cible : tout est déjà public.",
                "Résultats consolidés dans un rapport lisible."]},
    "réseau": {"role": "Les tools réseau cartographient et mesurent le réseau autour de la machine.",
        "how": ["Découverte des hôtes vivants (ping sweep / ARP).",
                "Scan des ports ouverts et services exposés.",
                "Mesure du trafic en direct pour les graphiques."]},
    "crypto": {"role": "Les tools crypto chiffrent, hachent ou vérifient des données.",
        "how": ["Chiffrement AES ou hachage md5/sha1 selon le tool.",
                "Attaque dictionnaire pour casser des hash faibles.",
                "Sortie claire : hash, clé, ou fichier chiffré."]},
    "stégano": {"role": "La stéganographie cache un message secret DANS une image, sans trace visible.",
        "how": ["Écriture octet par octet dans les LSB des pixels du PNG.",
                "L'image reste visuellement identique.",
                "L'extraction relit les LSB et restitue le message."]},
    "forensics": {"role": "La forensic analyse un artefact (email, image, fichier) pour en extraire toute la vérité.",
        "how": ["Analyse des headers : IP source, relais, SPF.",
                "Hash + métadonnées + recherche inverse d'image.",
                "Conclusion : authentique, falsifié, ou suspect."]},
    "sniffer": {"role": "Un sniffer capture le trafic réseau qui passe sur la machine, en direct.",
        "how": ["tcpdump en mode live sur l'interface active.",
                "Filtre appliqué pour ne garder que l'utile.",
                "Affichage paquet par paquet, coloré."]},
    "alertes": {"role": "Un watcher surveille une ressource et prévient quand elle change.",
        "how": ["Polling périodique de la ressource (site, port, fichier).",
                "Comparaison avec l'état précédent.",
                "Notification (bat-signal web) au moindre changement."]},
    "système": {"role": "Les tools système radiographient la machine elle-même : disque, CPU, process.",
        "how": ["Scan des plus gros fichiers, cachés, récents.",
                "CPU par process en direct (vision thermique).",
                "Détection d'IOCs connus de l'arsenal."]},
    "détection": {"role": "La défense : détecter les traces des kits de l'arsenal sur une machine.",
        "how": ["Comparaison de la machine contre la base d'IOCs.",
                "Génération de règles Sigma (SIEM) et YARA.",
                "Rapport : ce qui est propre, ce qui est infecté."]},
    "wake-on-lan": {"role": "Wake-on-LAN allume une machine éteinte du réseau via un magic packet.",
        "how": ["Construction du magic packet (6×FF + 16×MAC).",
                "Envoi en broadcast UDP sur le port 9.",
                "La carte mère de la cible réveille la machine."]},
    "intégration": {"role": "Les tools d'intégration connectent l'arsenal à des APIs et services externes.",
        "how": ["Requêtes REST authentifiées vers l'endpoint.",
                "Validation et extraction du JSON de réponse.",
                "Sortie formatée pour la suite du workflow."]},
    "automatisation": {"role": "L'automatisation déclenche des actions quand une condition est remplie.",
        "how": ["Veille en boucle sur l'état surveillé (port, fichier, process).",
                "Déclenchement de l'action configurée.",
                "Log de tout ce qui s'est passé."]},
    "injection": {"role": "L'injection DLL fait exécuter son code par un processus légitime d'une autre application.",
        "how": ["OpenProcess + VirtualAllocEx dans la cible.",
                "Écriture du chemin de la DLL.",
                "CreateRemoteThread : la cible charge et exécute la DLL."]},
    "hollowing": {"role": "Le process hollowing vide un processus légitime pour y mettre un autre programme.",
        "how": ["Création du processus légitime en SUSPENDU.",
                "Unmapping de son image mémoire (NtUnmapViewOfSection).",
                "Écriture du PE malveillant à la place, puis reprise."]},
    "crypter": {"role": "Un crypter emballe un binaire pour le rendre indéchiffrable par l'antivirus au repos.",
        "how": ["Packing RC4 du payload original.",
                "Génération d'un loader stub qui déchiffre en mémoire.",
                "Exécution directe en RAM : jamais écrit déchiffré sur disque."]},
    "télémétrie": {"role": "Ce module coupe les capteurs de télémétrie que l'EDR utilise pour voir.",
        "how": ["Patch de EtwEventWrite : ret immédiat → plus d'événements ETW.",
                "Patch de AmsiScanBuffer → contenu marqué CLEAN.",
                "L'EDR devient aveugle aux actions suivantes."]},
    "mémoire": {"role": "L'obfuscation mémoire chiffre le code au repos pour échapper aux scans.",
        "how": ["Pendant le sleep, les pages de code sont chiffrées.",
                "Un timer les déchiffre juste avant l'exécution.",
                "Un scan mémoire au mauvais moment ne voit que du bruit."]},
    "call stack": {"role": "Le stack spoofing maquille la pile d'appels pour cacher l'origine du code.",
        "how": ["Remplacement de la chaîne de retour par un frame légitime.",
                "Le debugger/EDR croit que CreateFileA a tout appelé.",
                "L'attribution du code malveillant devient fausse."]},
    "dark web": {"role": "Les tools dark web passent par Tor pour consulter des services .onion.",
        "how": ["Vérification/contrôle du daemon Tor (SOCKS 9050).",
                "Fetch de la page .onion via le proxy.",
                "Crawler pour suivre les liens internes."]},
    "phishing": {"role": "Le phishing héberge une fausse page de login pour capturer les identifiants.",
        "how": ["Miroir pixel-perfect de la vraie page (Microsoft, etc.).",
                "Chaque frappe est capturée au vol (JS).",
                "La victime est renvoyée vers le vrai site : elle ne voit rien."]},
    "viewer": {"role": "Le viewer est la salle de contrôle : tout ce qui est capturé s'affiche ici en live.",
        "how": ["Relecture du fichier de captures JSON.",
                "Vue temps réel, dernières entrées en haut.",
                "Sert de preuve et de suivi pendant l'exercice."]},
    "secrets": {"role": "Ces tools extraient les secrets stockés par la machine : mots de passe wifi, navigateurs, clés API.",
        "how": ["Trousseau macOS / DPAPI Windows pour les clés wifi.",
                "Bases SQLite des navigateurs (logins, cookies, historique).",
                "Scan regex des fichiers pour les clés API oubliées."]},
    "minage": {"role": "Le minage exploite la puissance de calcul pour générer de la cryptomonnaie (lab : preuve de concept).",
        "how": ["Minage PoW SHA-256 réel : cherche le nonce sous la cible.",
                "Ou xmrig Monero configuré avec le wallet de test.",
                "Coordonnateur : dashboard de la flotte en direct."]},
    "arsenal": {"role": "L'arsenal est une bibliothèque d'outils prêts à l'emploi, classée par thème.",
        "how": ["Interface plein écran (terminal ou web) avec recherche.",
                "Chaque arme a sa fiche : usage + commande.",
                "Sélection directe = lancement immédiat."]},
    "orchestration": {"role": "L'orchestrateur planifie et enchaîne une campagne complète, tool par tool.",
        "how": ["Génération du plan en étapes (phishing → dropper → C2).",
                "Exécution séquentielle avec vérification de chaque étape.",
                "Rapport final horodaté avec captures."]},
    "exécution": {"role": "L'exécution de campagne lance tout le plan préparé, dans l'ordre.",
        "how": ["Lecture du plan généré.",
                "Lancement de chaque module avec ses arguments.",
                "Arrêt propre et rapport si une étape échoue."]},
    "documentation": {"role": "La génération de rapport documente tout l'exercice pour en garder la preuve.",
        "how": ["Collecte des sorties et captures de chaque étape.",
                "Écriture d'un RAPPORT.md structuré.",
                "Utile pour le debrief après le CTF."]},
    "lab": {"role": "Le builder de lab crée une cible vulnérable isolée pour s'entraîner en CTF.",
        "how": ["Serveur local :8090 avec failles plantées (SQLi, traversal, RCE).",
                "4 flags cachés à trouver.",
                "Tout tourne en local : aucun risque extérieur."]},
    "ctf": {"role": "Le scoreboard CTF suit les scores et les flags trouvés pendant l'exercice.",
        "how": ["Enregistrement des soumissions de flags.",
                "Classement en direct des participants.",
                "Validation des flags côté serveur."]},
    "nettoyage": {"role": "Le nettoyage désinstalle tout ce que le kit a installé, proprement.",
        "how": ["Suppression des agents, LaunchAgents, processus.",
                "Effacement des fichiers installés et logs.",
                "Vérification finale : 0 agent, 0 process."]},
    "analyse": {"role": "L'analyse statique radiographie un binaire sans l'exécuter.",
        "how": ["Type de fichier, headers, sections, imports.",
                "Extraction des strings : URLs, IPs, mots chauds.",
                "Conclusion sur la nature du binaire."]},
    "strings": {"role": "L'extraction de strings révèle les données lisibles cachées dans un binaire.",
        "how": ["Parcours des sections de données.",
                "Filtrage des URLs, IPs, chemins, mots suspects.",
                "Souvent la première indice de ce que fait un malware."]},
    "imports": {"role": "La liste des imports trahit ce qu'un binaire est capable de faire.",
        "how": ["Lecture de la table d'imports (DLL + fonctions).",
                "VirtualAlloc + WriteProcessMemory → injection probable.",
                "WinExec / URLDownloadToFile → dropper probable."]},
    "dépack": {"role": "Le dépackage déballe un binaire packé (UPX) pour l'analyser.",
        "how": ["Détection du signature du packer.",
                "Décompression UPX → binaire lisible.",
                "Analyse reprise sur le binaire dépacké."]},
    "radare2": {"role": "Radare2 est le couteau suisse du reverse engineering en terminal.",
        "how": ["aaa : analyse complète (fonctions, xrefs).",
                "pdf : désassemblage d'une fonction.",
                "Passthrough : tu tapes r2, le tool te l'affiche."]},
    "dynamique": {"role": "L'analyse dynamique observe un binaire PENDANT qu'il tourne.",
        "how": ["Surveillance des fichiers ouverts en live.",
                "Ce qu'il écrit, ce qu'il lit, où.",
                "Complète l'analyse statique avec la vérité du terrain."]},
    "versioning": {"role": "Le diff de versions compare deux échantillons pour voir ce qui a changé.",
        "how": ["Diff des strings des deux binaires.",
                "Nouvelles URLs, IPs ou mots ajoutés ressortent.",
                "Utile pour suivre l'évolution d'une campagne."]},
    "référence": {"role": "La référence liste les outils pro du domaine et comment les utiliser.",
        "how": ["Ghidra, radare2, x64dbg, Wireshark…",
                "Pour chaque outil : à quoi ça sert, quand l'utiliser.",
                "Le point de départ pour aller plus loin."]},
    "veille": {"role": "La veille agrège les actus cybersé de 25 sources en un seul flux.",
        "how": ["Fetch périodique des flux RSS.",
                "Déduplication et tri chronologique.",
                "Interface web filtrable + sortie terminal."]},
    "terminal": {"role": "La sortie terminal affiche le flux de données directement dans le shell.",
        "how": ["Lecture du cache des dernières entrées.",
                "Affichage coloré, N lignes.",
                "Pour une consultation rapide sans browser."]},
    "archive": {"role": "L'archive totale capture l'état complet de la machine à un instant T.",
        "how": ["Inventaire : process, réseau, users, apps installées.",
                "Snapshot horodaté stocké en JSON.",
                "Comparable à un snapshot ultérieur pour voir les changements."]},
    "propagation": {"role": "Le SSH worm se propage de machine en machine via les clés SSH connues.",
        "how": ["Lecture de known_hosts pour la liste des cibles.",
                "Résolution ARP du réseau local.",
                "Injection de la clé dans authorized_keys des cibles."]},
    "apk": {"role": "Le module Android installe un agent sur un téléphone pour le piloter à distance.",
        "how": ["Service START_STICKY : redémarre même après kill.",
                "Check-in périodique vers le C2.",
                "Nécessite le SDK Android pour builder l'APK."]},
    "payloads": {"role": "Le forgeron de payloads cuit des charges BadUSB prêtes à flasher sur une carte.",
        "how": ["5 payloads préécrits avec TON adresse de C2.",
                "Compilation pour la cible SGP Card.",
                "Flash de la carte : elle exécute le payload à l'insertion."]},
    "ducky-lite": {"role": "Le firmware ducky-lite transforme la carte en clavier malveillant autonome.",
        "how": ["Interpréteur de script type DuckyScript embarqué.",
                "LED + buzzer pour le feedback.",
                "Fonctionne sans ordinateur hôte : la carte agit seule."]},
    "gestionnaire": {"role": "Le gestionnaire web permet d'éditer et lancer les payloads depuis le browser.",
        "how": ["Éditeur de payload dans la page web.",
                "Save en LittleFS (mémoire de la carte).",
                "Run direct en HID : la carte tape le script."]},
    "audit": {"role": "Le rapport d'audit documente l'architecture et les capacités du hardware.",
        "how": ["Analyse du composant (ESP32, SGP Card).",
                "Schéma des vecteurs d'attaque possibles.",
                "RAPPORT_SGP_JOKER.md : la base de travail."]},
    "breach analytics": {"role": "L'analytics de breach analyse les grandes fuites de données publiques.",
        "how": ["Dataset des 23 plus grosses breaches.",
                "Stats par secteur et par année.",
                "Visualisation : barres + timeline web."]},
    "vérification": {"role": "La vérification prouve si une donnée est authentique ou falsifiée.",
        "how": ["Hash de référence vs hash calculé.",
                "Certificat TLS : émetteur, chaîne, validité.",
                "Métadonnées d'image : GPS, appareil, retouche."]},
    "c2": {"role": "Le C2 (Command & Control) est le poste de commande qui pilote les agents déployés.",
        "how": ["Les agents font un check-in périodique.",
                "Les tâches sont poussées, les résultats remontent.",
                "Console web + canal DNS pour passer les filtres."]},
    "forensics web": {"role": "L'analyse d'headers détermine si un email est authentique ou usurpé, sans l'ouvrir.",
        "how": ["SPF vérifie que le serveur émetteur est autorisé pour le domaine.",
                "DKIM prouve la signature du message, DMARC aligne le domaine affiché.",
                "La chaîne Received retrace chaque relais depuis l'expéditeur."]},
    "stégano studio": {"role": "Le studio stégano cache un message dans une image directement depuis le navigateur.",
        "how": ["Le message est écrit dans le bit de poids faible de chaque canal RGB.",
                "L'image résultante est visuellement identique à l'originale.",
                "Un mot de passe dérive un flux SHA-256 qui chiffre le payload."]},
    "carte réseau": {"role": "La carte réseau révèle en temps réel les appareils connectés à ton wifi.",
        "how": ["La table ARP (ou un ping sweep) découvre les hôtes vivants.",
                "Le graphe se rafraîchit toutes les 10 secondes.",
                "Tout nouvel appareil apparaît en orange avec une alerte."]},
    "prank": {"role": "Un prank est une farce visuelle inoffensive, sans aucune action système.",
        "how": ["Animation plein écran ou notification.",
                "Aucun fichier écrit, aucune persistance.",
                "Sortie toujours possible (touche secrète ou Ctrl+C)."]},
    "unhooking": {"role": "L'unhooking restaure les DLL système dans leur état d'origine pour retirer les hooks de l'EDR.",
        "how": ["Copie propre de ntdll depuis le disque (non hookée).",
                "Remappage de la section .text sur la ntdll en mémoire.",
                "Les fonctions redeviennent des syscalls directs, invisibles."]},
    "syscalls": {"role": "Les syscalls directs appellent le noyau directement, sans passer par les API hookées.",
        "how": ["Lecture des numéros de syscall (SSN) depuis ntdll sur disque.",
                "Construction des stubs en mémoire (Hell's Gate).",
                "Les appels critiques n'apparaissent jamais dans les API surveillées."]},
    "wargames": {"role": "Le lab W.O.P.R. recrée l'ordinateur de WarGames pour jouer un CTF guidé.",
        "how": ["Intro + morpion comme dans le film.",
                "Cible vulnérable construite puis attaquée.",
                "Destroy : efface tout le lab après usage."]},
    "veille web": {"role": "L'interface web de veille affiche le flux d'actus dans un dashboard filtrable.",
        "how": ["Serveur local avec le cache des actus.",
                "Filtres par source et par mot-clé.",
                "Lien direct vers chaque article."]},
}
GENERIC = {"role": "Ce tool est une brique de l'arsenal : il accomplit une action précise dans son kit.",
    "how": ["Lancé depuis le menu du kit avec son numéro.",
            "Il travaille en local sur ta machine ou ta VM de lab.",
            "Sa sortie est affichée directement dans le terminal."]}

def theme_info(theme, name=""):
    t = (theme or "").lower().strip()
    if t and t in THEMES: return THEMES[t]
    if t:
        for k, v in THEMES.items():
            if k in t or t in k: return v
    # thème absent → essaie avec le NOM du tool
    n = (name or "").lower()
    ALIAS = {
        "phishing": "phishing", "pixel-perfect": "phishing", "tunnel": "phishing",
        "harvest": "phishing", "domaines": "phishing", "miroir": "phishing",
        "unhook": "unhooking", "ntdll": "unhooking", "syscall": "syscalls",
        "apc": "injection", "hollow": "hollowing", "smb": "worm lan", "worm": "worm usb",
        "shell": "reverse shell", "miner": "minage", "xmrig": "minage", "wallet": "minage",
        "coord": "minage", "flotte": "minage", "pow": "minage", "hasrate": "minage",
        "rayons": "système", "thermique": "système", "detector": "détection",
        "marées": "réseau", "wol": "wake-on-lan", "abyss": "réseau", "reef": "réseau",
        "port": "automatisation", "api": "intégration", "webhook": "intégration",
        "json": "intégration", "vérité": "vérification", "tls": "vérification",
        "email": "forensics", "image": "forensics", "tempête": "prank", "prank": "prank",
        "update": "prank", "wallpaper": "prank", "tor": "dark web", "onion": "dark web",
        "dark": "dark web", "crawl": "dark web", "btc": "crypto", "fuite": "osint",
        "arsenal": "arsenal", "holocron": "archive", "sith": "reverse shell",
        "droid": "réseau", "kyber": "crypto", "wifi": "secrets", "browser": "secrets",
        "dpapi": "secrets", "secret": "secrets", "vault": "secrets", "keylog": "keylogger",
        "clipboard": "clipboard", "webcam": "webcam", "micro": "micro",
        "screen": "screenspy", "écran": "screenspy", "dropper": "dropper",
        "persistance": "dropper", "compile": "build", "dns": "c2", "c2": "c2",
        "agent": "c2", "anti-analysis": "télémétrie", "infostealer": "secrets",
        "fiche": "référence", "journal": "veille", "veille": "veille", "stats": "breach analytics",
        "plan": "orchestration", "run": "exécution", "report": "documentation",
        "rapport": "documentation", "play": "wargames", "destroy": "nettoyage",
        "unpack": "dépack", "upx": "dépack", "strings": "strings", "import": "imports",
        "watch": "dynamique", "diff": "versioning", "analyze": "analyse",
        "stégano": "stégano", "hash": "crypto", "md5": "crypto", "aes": "crypto",
        "cesar": "crypto", "mot de passe": "crypto", "whois": "osint", "domaine": "osint",
        "geoloc": "osint", "osint": "osint", "ping": "réseau", "arp": "réseau",
        "débit": "réseau", "knock": "réseau", "tcpdump": "sniffer", "pcap": "sniffer",
        "paquet": "sniffer", "yara": "détection", "sigma": "détection", "ioc": "détection",
        "payload": "payloads", "forge": "payloads", "firmware": "ducky-lite",
        "ducky": "ducky-lite", "manager": "gestionnaire", "apk": "apk", "android": "apk",
        "ssh": "propagation", "haha": "prank", "notif": "prank", "popup": "prank",
        "foudre": "animation", "replay": "animation", "portail": "animation",
        "top": "terminal", "sweep": "réseau", "infiltrator": "reverse shell",
        "archive": "archive", "wopr": "wargames", "matrix": "prank", "joker": "prank",
    }
    if t:
        for a, target in ALIAS.items():
            if a in t: return THEMES.get(target, GENERIC)
    for a, target in ALIAS.items():
        if a in n: return THEMES.get(target, GENERIC)
    for k, v in THEMES.items():
        if k in n: return v
    return GENERIC

def slugify(num, name):
    s = re.sub(r"[^a-z0-9]+", "-", f"{num}-{name}".lower()).strip("-")
    return s[:60]

def parse_md():
    raw = open(MD, encoding="utf-8").read()
    sections = re.split(r"(?=^## KIT \d+)", raw, flags=re.M)
    kits = {}
    for sec in sections:
        m = re.match(r"## KIT (\d+) — ([^(\n]+)", sec)
        if not m: continue
        num = int(m.group(1))
        cmd = ""
        cb = re.search(r"```\n(.*?)```", sec, re.S)
        if cb:
            cmd = cb.group(1).strip().splitlines()[0].strip()
        tools = []
        for line in sec.splitlines():
            if not line.startswith("|"): continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 3: continue
            if cells[0] in ("#", "---", "") or set(cells[0]) <= {"-", " "}: continue
            numc = cells[0]
            if not re.match(r"^[0-9a-z]{1,2}$", numc, re.I): continue
            if len(cells) >= 4:
                name, theme, desc = cells[1], cells[2], cells[3]
            else:
                name, theme, desc = cells[1], "", cells[2]
            if name.lower() in ("tool",): continue
            tools.append({"num": numc, "name": name, "theme": theme, "desc": desc,
                          "slug": slugify(numc, name)})
        kits[num] = {"cmd": cmd, "tools": tools}
    return kits

BG_HTML = '<div class="bg"><div class="beam"></div><div class="dots"></div><div class="grid"></div><div class="vig"></div></div>'
FONTS_LINK = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Anton&family=Oswald:wght@400;500;600;700&family=Archivo:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">'
NAV_HTML = ('<nav class="nav"><div class="brand"><span class="dot"></span>Gotham <em>City</em></div>'
            '<div class="nav-right"><span class="status">System Online</span>'
            '<a class="ghbtn" href="' + GITHUB + '" target="_blank">&#8599; GITHUB</a></div></nav>')

def banner(folder, color, emoji, face, inner):
    if face and os.path.exists(os.path.join(ROOT, "gotham_static", "faces", face)):
        av = (f'<img src="{FACES_REL}{face}" alt="" '
              f'style="width:110px;height:110px;object-fit:cover;border-radius:10px;'
              f'border:1px solid {color}66;flex-shrink:0">')
    else:
        av = (f'<div style="width:110px;height:110px;border-radius:10px;display:grid;'
              f'place-items:center;font-size:3.2em;background:radial-gradient(70% 70% at 50% 35%,{color}40,transparent 75%),'
              f'linear-gradient(160deg,{color}14,var(--panel2));border:1px solid {color}44;flex-shrink:0">{emoji}</div>')
    return (f'<div class="banner" style="--c:{color}">{av}<div class="info">{inner}</div></div>')

CSS = """:root{
  --bg:#06070c; --panel:#0c0e17; --panel2:#070810; --line:#1a1c2e;
  --txt:#c4c6d6; --muted:#6a6d86; --dim:#45485e;
  --red:#e63022; --gold:#f5c518;
  --disp:"Anton",Impact,sans-serif; --cond:"Oswald",sans-serif;
  --sans:"Archivo",-apple-system,"Segoe UI",sans-serif;
  --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:var(--sans);min-height:100vh;position:relative;-webkit-font-smoothing:antialiased}
::selection{background:var(--red);color:#fff}
::-webkit-scrollbar{width:11px}::-webkit-scrollbar-track{background:var(--bg)}
::-webkit-scrollbar-thumb{background:#1c1e30;border-radius:6px;border:2px solid var(--bg)}
::-webkit-scrollbar-thumb:hover{background:var(--red)}
.bg{position:fixed;inset:0;z-index:0;pointer-events:none;overflow:hidden}
.bg .beam{position:absolute;inset:0;background:
  radial-gradient(44% 70% at 50% 108%,color-mix(in srgb,var(--c) 10%,transparent),transparent 60%),
  radial-gradient(60% 80% at 50% -10%,rgba(230,48,34,.12),transparent 62%),
  radial-gradient(40% 50% at 82% 20%,rgba(100,149,255,.08),transparent 60%)}
.bg .dots{position:absolute;inset:0;opacity:.12;background-image:radial-gradient(rgba(255,255,255,.5) 1px,transparent 1.4px);background-size:16px 16px;mask-image:radial-gradient(ellipse 70% 55% at 50% 20%,#000 10%,transparent 72%)}
.bg .grid{position:absolute;inset:0;opacity:.5;background-image:linear-gradient(rgba(255,255,255,.02) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.02) 1px,transparent 1px);background-size:52px 52px;mask-image:radial-gradient(ellipse 85% 70% at 50% 30%,#000 35%,transparent 88%)}
.bg .vig{position:absolute;inset:0;background:radial-gradient(ellipse 100% 80% at 50% 30%,transparent 55%,rgba(0,0,0,.55))}
.wrap{position:relative;z-index:1}
.nav{display:flex;justify-content:space-between;align-items:center;padding:14px clamp(18px,4vw,40px);position:sticky;top:0;z-index:30;background:rgba(6,7,12,.55);backdrop-filter:blur(16px) saturate(140%);border-bottom:1px solid var(--line)}
.brand{font-family:var(--cond);font-weight:700;letter-spacing:5px;font-size:.95rem;color:#fff;display:flex;align-items:center;gap:11px;text-transform:uppercase;text-decoration:none}
.brand .dot{width:8px;height:8px;border-radius:50%;background:var(--red);box-shadow:0 0 14px var(--red);animation:pulse 2s infinite}
.brand em{color:var(--red);font-style:normal}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.nav-right{display:flex;align-items:center;gap:14px}
.status{font-family:var(--mono);font-size:.64rem;letter-spacing:1.6px;color:#4ad66d;display:flex;align-items:center;gap:7px;text-transform:uppercase}
.status::before{content:"";width:6px;height:6px;border-radius:50%;background:#4ad66d;box-shadow:0 0 10px #4ad66d;animation:pulse 1.6s infinite}
.ghbtn{font-family:var(--mono);color:#9fb4ff;font-size:.7rem;letter-spacing:.6px;text-decoration:none;border:1px solid var(--line);padding:8px 15px;border-radius:10px;transition:.25s;background:rgba(255,255,255,.02)}
.ghbtn:hover{border-color:#6495ff;color:#cdd9ff;box-shadow:0 0 22px rgba(100,149,255,.22);transform:translateY(-1px)}
.banner{display:flex;gap:20px;align-items:center;max-width:820px;margin:30px auto 0;padding:20px 24px;
background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:4px;position:relative;overflow:hidden}
.banner::before{content:"";position:absolute;inset:auto 0 0 0;height:3px;background:linear-gradient(90deg,transparent,var(--c),transparent)}
.banner .info{flex:1;min-width:0}
.crumb{font-family:var(--mono);font-size:.68rem;letter-spacing:1.2px;text-transform:uppercase}
.crumb a{color:var(--c);text-decoration:none}
.crumb a:hover{text-decoration:underline}
h1{font-family:var(--disp);color:#fff;font-size:clamp(1.7rem,5vw,2.6rem);margin:8px 0 4px;letter-spacing:1px;text-transform:uppercase;line-height:.95;text-shadow:0 2px 0 rgba(0,0,0,.55)}
.sub{font-family:var(--mono);color:var(--muted);font-size:.7rem;letter-spacing:1.5px;text-transform:uppercase}
main{max-width:820px;margin:22px auto 0;padding:0 24px 44px;position:relative;z-index:1}
.theme{display:inline-block;font-family:var(--mono);color:var(--c);border:1px solid color-mix(in srgb,var(--c) 60%,transparent);border-radius:999px;
padding:5px 15px;font-size:.66rem;letter-spacing:1.6px;margin:4px 0 8px;background:color-mix(in srgb,var(--c) 10%,transparent)}
h2{font-family:var(--mono);color:var(--c);font-size:.72rem;letter-spacing:3px;margin:28px 0 10px;text-transform:uppercase;
display:flex;align-items:center;gap:12px}
h2::before{content:"";width:22px;height:1px;background:var(--c);box-shadow:0 0 8px var(--c)}
h2::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line),transparent)}
p.txt{color:var(--txt);font-size:.97em;line-height:1.7}
ul.how{margin:4px 0 2px 2px;padding:0;list-style:none}
ul.how li{color:#a8abbf;font-size:.93em;line-height:1.65;padding:6px 0 6px 24px;position:relative}
ul.how li:before{content:"▸";color:var(--c);position:absolute;left:2px}
.cmd{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:14px 16px;
font-family:var(--mono);font-size:.78em;color:#4ad66d;margin:10px 0 6px;overflow-x:auto}
.cmd small{display:block;color:var(--dim);font-family:var(--sans);margin-bottom:7px;letter-spacing:2px;font-size:.68rem;text-transform:uppercase}
.key{font-family:var(--mono);color:var(--muted);font-size:.74rem;letter-spacing:.5px;margin-bottom:22px}
.key b{color:#fff}
.gh{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none;
background:linear-gradient(135deg,#238636,#2ea043);padding:15px 20px;border-radius:10px;
font-weight:700;font-size:.95em;box-shadow:0 6px 24px #23863644;transition:transform .2s;margin-top:30px}
.gh:hover{transform:translateY(-2px)}
.gh svg{width:24px;height:24px;fill:#fff;flex-shrink:0}
.gh small{display:block;font-weight:400;font-size:.72em;opacity:.85}
.gh .arrow{margin-left:auto;font-size:1.3em}
.list .t{display:flex;gap:14px;align-items:baseline;background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);
border-radius:4px;padding:13px 16px;margin-bottom:9px;text-decoration:none;transition:border-color .25s,transform .25s,box-shadow .25s}
.list .t:hover{border-color:color-mix(in srgb,var(--c) 60%,var(--line));transform:translateX(4px);box-shadow:0 8px 26px color-mix(in srgb,var(--c) 14%,transparent)}
.list .n{font-family:var(--mono);color:var(--c);font-weight:700;min-width:24px}
.list .nm{font-family:var(--cond);color:#fff;font-size:.95em;font-weight:600;letter-spacing:.4px;text-transform:uppercase}
.list .th{margin-left:auto;font-family:var(--mono);color:var(--c);font-size:.66rem;opacity:.85}
footer{text-align:center;color:var(--muted);padding:36px 20px 52px;font-family:var(--mono);font-size:.66rem;letter-spacing:2.2px;border-top:1px solid var(--line);margin-top:40px;text-transform:uppercase}
footer a{color:#9fb4ff;text-decoration:none}
footer a:hover{color:#cdd9ff}
@media (max-width:560px){.status{display:none}}"""

GITHUB_SVG = '<svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>'

def tool_page(folder, kit_name, color, emoji, face, cmd, tool, kit_label):
    info = theme_info(tool["theme"], tool["name"])
    how = "".join(f"<li>{H.escape(h)}</li>" for h in info["how"])
    desc = tool["desc"] or "Voir le README du kit sur GitHub."
    cmd_block = ""
    if cmd:
        cmd_block = (f'<div class="cmd"><small>COMMANDE DU KIT</small>'
                     f'{H.escape(cmd)}</div>'
                     f'<p class="key">Puis touche <b>{H.escape(tool["num"].upper())}</b> + Entrée pour lancer ce tool.</p>')
    inner = (f'<div class="crumb"><a href="../index.html">← {H.escape(kit_name)}</a> · '
             f'<a href="../../arsenal_dc.html">Arsenal DC</a></div>'
             f'<h1>{H.escape(tool["name"])}</h1>'
             f'<p class="sub">{H.escape(kit_label)} · powered by Maxime Leal</p>')
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(tool['name'])} · {H.escape(kit_name)} — Arsenal DC</title>
{FONTS_LINK}<style>{CSS}</style></head><body style="--c:{color}">
{BG_HTML}<div class="wrap">
{NAV_HTML}
{banner(folder, color, emoji, face, inner)}
<main>
<span class="theme">{H.escape(tool['theme'].upper()) if tool['theme'] else 'TOOL'}</span>
<h2>Rôle de ce tool</h2>
<p class="txt">{H.escape(info['role'])}</p>
<h2>Comment ça marche</h2>
<ul class="how">{how}</ul>
<h2>Concrètement, ici</h2>
<p class="txt">{H.escape(desc)}</p>
{cmd_block}
<a class="gh" href="{GITHUB}/tree/main/{H.escape(folder)}" target="_blank">
  {GITHUB_SVG}<span>Code source sur GitHub<small>github.com/MaximeLEAL/tool_DC-arsenal → {H.escape(folder)}</small></span><span class="arrow">→</span>
</a>
</main>
<footer>ARSENAL DC · <a href="{GITHUB}">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
</div></body></html>"""

def kit_index(folder, kit_name, color, emoji, face, cmd, tools):
    rows = "".join(
        f'<a class="t" href="{t["slug"]}.html"><span class="n">{H.escape(t["num"])}</span>'
        f'<span class="nm">{H.escape(t["name"])}</span>'
        f'<span class="th">{H.escape(t["theme"])}</span></a>'
        for t in tools)
    cmd_block = f'<div class="cmd"><small>LANCER LE KIT</small>{H.escape(cmd)}</div>' if cmd else ""
    inner = (f'<div class="crumb"><a href="../../arsenal_dc.html">← Arsenal DC</a></div>'
             f'<h1>{H.escape(kit_name)}</h1>'
             f'<p class="sub">{len(tools)} tools · powered by Maxime Leal</p>')
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(kit_name)} — Arsenal DC</title>
{FONTS_LINK}<style>{CSS}</style></head><body style="--c:{color}">
{BG_HTML}<div class="wrap">
{NAV_HTML}
{banner(folder, color, emoji, face, inner)}
<main>
{cmd_block}
<p class="txt" style="color:var(--muted);font-size:.88em;margin-bottom:14px">Chaque tool a sa fiche : rôle, fonctionnement, utilisation et lien GitHub.</p>
<div class="list">{rows}</div>
<a class="gh" href="{GITHUB}/tree/main/{H.escape(folder)}" target="_blank">
  {GITHUB_SVG}<span>Voir {H.escape(folder)} sur GitHub<small>Code source complet du kit</small></span><span class="arrow">→</span>
</a>
</main>
<footer>ARSENAL DC · <a href="{GITHUB}">GITHUB</a> · POWERED BY MAXIME LEAL</footer>
</div></body></html>"""

def main():
    kits_md = parse_md()
    os.makedirs(DATA, exist_ok=True)
    if os.path.isdir(OUT):
        import shutil; shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)

    total = 0
    for num, folder, name, color, emoji, face in KITS:
        data = kits_md.get(num, {"cmd": "", "tools": []})
        tools = data["tools"]
        d = os.path.join(OUT, folder)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(kit_index(folder, name, color, emoji, face, data["cmd"], tools))
        for t in tools:
            with open(os.path.join(d, f"{t['slug']}.html"), "w", encoding="utf-8") as f:
                f.write(tool_page(folder, name, color, emoji, face, data["cmd"], t, name))
        slim = [{"num": t["num"], "name": t["name"], "theme": t["theme"], "desc": t["desc"], "slug": t["slug"]} for t in tools]
        json.dump({"id": folder, "name": name, "color": color, "emoji": emoji,
                   "cmd": data["cmd"], "tools": slim},
                  open(os.path.join(DATA, f"{folder}.json"), "w", encoding="utf-8"), ensure_ascii=False)
        total += len(tools)
        print(f"  ✓ {folder:<20} {len(tools):>3} tools")
    print(f"\n{total} fiches tools générées dans arsenal_web_pages/ ({len(KITS)} kits, zéro doublon)")

if __name__ == "__main__":
    main()
