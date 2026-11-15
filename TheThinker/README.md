# THE THINKER — LE LABO DE REVERSE ENGINEERING · powered by Maxime Leal
radare2 + otool + strings + upx + watch dynamique — le tout en commandes simples.

## COMMANDES (toujours sur un binaire : PE Windows, Mach-O mac, ELF linux)
| Commande | Ce qu'elle fait |
|---|---|
| `analyze <bin>` | fiche complète : type, headers r2, sections, imports, test UPX |
| `strings <bin>` | les strings intéressants filtrés : URLs, IPs, chemins, mots chauds (key/pass/mutex/inject…) |
| `imports <bin>` | DLL + fonctions (PE via objdump mingw) ou nm/otool (Mach-O) |
| `unpack <bin>` | dépacke UPX → `bin.unpacked` |
| `r2 <bin> "cmd"` | passthrough radare2 : `aaa` analyse, `afl` fonctions, `pdf @ main` désassemble, `iz` strings |
| `watch <pid>` | fichiers ouverts d'un process en live (lsof en boucle) |
| `diff a b` | diff de strings entre deux builds — versioning malware |
| `arsenal` | les forteresses RE : Ghidra (NSA), radare2, x64dbg, FLARE-VM, Capstone, Unicorn, dnSpy, DIE, PE-bear, YARA, Frida, upx · FERMÉ: IDA, Binary Ninja, Hopper |

## TESTÉ RÉEL (ce jour)
`analyze lexagent.exe` (ton RAT Hydre) : PE32+ x64, baddr 0x140000000, 10 sections (.text .data
.rdata .tls .reloc…), canary false, compiled 15 nov 02:04 ✓
`strings lexagent.exe` : 3 334 bruts → filtrés IPs/chemins/mots chauds (FLAG, Mutex, Hook…) ✓

## OUTILS INSTALLÉS
radare2 6.2.6 · upx 5.3 (brew) · objdump mingw (cross PE)

## FICHE D'EMPLOI TYPE (recon d'un malware inconnu)
1. `file` + `analyze` — type, arch, packé ?
2. `strings` — URLs, IPs, chemins, mots chauds → le C2 apparaît souvent là
3. `imports` — les APIs révèlent le comportement (WSAStartup = réseau, SetWindowsHookEx = keylogger…)
4. `unpack` si UPX — puis re-analyse
5. `r2 aaa; afl` — les fonctions · `pdf @ sym.main` — le désassemblage du main
6. `watch <pid>` — en dynamique dans la VM
