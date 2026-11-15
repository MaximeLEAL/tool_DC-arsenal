# KRYPTONITE SUITE · powered by Maxime Leal
Le renversement defensif : ton arsenal devient ta blue team.
## scan
`python3 kryptonite.py scan` — la machine vs les IOCs des 20 kits : chemins (RickCache, ArkhamLab…), fichiers, processus, LaunchAgents, crontab, ports (4444/5050/8090/8096/8085-8089…). Sortie : scan.json. TESTE : a detecte Daily Planet + WarWorld actifs ✓
## sigma
`python3 kryptonite.py sigma` — 8 regles Sigma par kit (sysmon process_creation/file_event/persistence) → `sorties/sigma/` → importables dans Elastic/Splunk via sigma-cli.
## yara
`python3 kryptonite.py yara` — 5 regles YARA sur les strings des agents → `sorties/yara/`.
## catalog
`python3 kryptonite.py catalog` — le JSON des IOCs complets.
## clean (lab)
Pour chaque kit : voir les README d'origine (RickPortal delivery/uninstall.sh, Arkham reg/schtasks…).
