# README — banque_a_tool

## Structure

| Fichier | Univers | Port web | Focus |
|---|---|---|---|
| `cowboy_bebop_recon.py` | Cowboy Bebop 🚀 | 5000 | Recon réseau |
| `akatsuki_dox.py` | Akatsuki 🔴 | 5001 | Dox / OSINT IP |
| `homura_pentest.py` | Homura 🌸 | 5002 | Pentest web |
| `quirk_osint.py` | My Hero 🦸 | 5003 | OSINT domaine |
| `venom_forge.py` | Venom 🕷️ | 5004 | Malware forge |

## Lancement

### CMD (menu interactif)
```bash
python cowboy_bebop_recon.py
python akatsuki_dox.py
python homura_pentest.py
python quirk_osint.py
python venom_forge.py
```

### Web (UI dans le navigateur)
```bash
python cowboy_bebop_recon.py --web --port 5000
python akatsuki_dox.py       --web --port 5001
python homura_pentest.py     --web --port 5002
python quirk_osint.py        --web --port 5003
python venom_forge.py        --web --port 5004
```

Ouvre `http://localhost:<port>` dans le navigateur.

## Dépendances

```bash
pip install flask pillow
# keylogger uniquement :
pip install pynput
```

## Tools par fichier

### cowboy_bebop_recon (10)
1. portscan — TCP scan range
2. udpscan — probe UDP top services
3. banner_grab — grab raw TCP banner
4. traceroute — hop-by-hop path
5. ping_sweep — sweep /24
6. os_detect — TTL fingerprint
7. whois_resolve — reverse DNS
8. ssl_inspect — TLS cert details
9. http_probe — HTTP headers
10. subnet_map — live hosts subnet

### akatsuki_dox (10)
1. ip_dox — geo + ASN + ports
2. domain_dox — domain chain
3. email_validate — MX + VRFY
4. phone_format — ITU E.164 parse
5. username_hunt — 15 platforms
6. breach_check — HIBP k-anon
7. social_links — generate URLs
8. google_dork — dork builder
9. metadata_strip — EXIF read/strip
10. timeline_build — findings log

### homura_pentest (10)
1. toolkit_audit — check tools installed
2. banner_grab — raw TCP banner
3. dir_bruteforce — HTTP path brute
4. sqli_probe — SQLi error detect
5. xss_probe — reflected XSS
6. lfi_probe — LFI path test
7. header_audit — missing sec headers
8. cookie_audit — cookie flags check
9. ssl_weak_check — TLS 1.0/1.1 detect
10. fuzz_params — URL param fuzzer

### quirk_osint (10)
1. dns_full — A/MX/NS/TXT/CNAME/SOA
2. subdomain_enum — brute subdomains
3. cert_transparency — crt.sh lookup
4. shodan_dork — Shodan queries
5. wayback_check — Wayback Machine
6. github_recon — user/org intel
7. pastebin_hunt — Google dork paste
8. tech_detect — CMS/framework detect
9. ip_range_owner — ARIN/RIPE ASN
10. org_intel — combined sweep

### venom_forge (10)
1. reverse_shell_py — TCP reverse Python
2. reverse_shell_ps1 — PowerShell reverse
3. bind_shell_py — Python bind shell
4. keylogger_py — pynput keylogger
5. persistence_win — registry Run key
6. persistence_linux — crontab entry
7. dropper_py — download & exec
8. xor_encoder — XOR encode + stub
9. rat_skeleton_py — async RAT skeleton
10. payload_b64_wrapper — b64 wrap

## Notes
- venom reverse shells → listener : `nc -lvnp <LPORT>`
- rat_skeleton écoute côté serveur, `nc <host> <port>` pour s'y connecter
- breach_check envoie seulement les 5 premiers chars du SHA1 (k-anonymat HIBP)
- metadata_strip crée un fichier `_clean` à côté de l'original
- web UI pilotable depuis mobile, responsive