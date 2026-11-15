# RAVEN — LE KIT D'ÉVASION EDR/DEFENDER · powered by Maxime Leal
# Les 6 techniques que les IA censurées refusent — cross-compilées, testables face à Defender
# Compile: zsh verify_raven.zsh   — Runtime: VM Windows uniquement (syscalls + patches système)

╔══════════════════════════════════════════════════════════════╗
║  CE QUE CHAQUE MODULE DÉFAIT — et ce qui le détecte          ║
╚══════════════════════════════════════════════════════════════╝

## 1 — SYSCALLS DIRECTS (Hell's Gate simplifié) — `build/syscalls_direct.exe`
Défait : les hooks user-mode EDR sur ntdll.dll. AUCUN appel ntdll en mémoire.
Comment : les SSN (System Service Numbers) sont résolus depuis ntdll SUR DISQUE
(copie propre jamais hookée), puis des stubs syscall (mov r10,rcx; mov eax,ssn; syscall)
sont construits en mémoire et exécutés directement en kernel.
Usage : `syscalls_direct.exe payload.bin` (shellcode x64 — demo sans arg : stub NOP/RET)
Détection résiduelle : un EDR kernel-mode (minifilter, ETW-TI) voit quand même le syscall.
## 2 — UNHOOKING NTDLL — `build/unhook_ntdll.exe`
Défait : TOUS les hooks user-mode d'un coup. Lit ntdll PROPRE depuis le disque,
compare le .text avec celui en mémoire, restaure les octets modifiés.
Testé : le second passage confirme 0 octet = ntdll restaurée au code original Microsoft.
## 3 — ETW PATCH + AMSI BYPASS — `build/etw_amsi_patch.exe`
Défait : la télémétrie ETW (EtwEventWrite ← ret 0xC3) et le scan AMSI
(AmsiScanBuffer ← mov eax, 0x80070057 (CLEAN) ; ret 0xC3).
Effet : les scripts PowerShell passent sans alerte, les événements ETW cessent.
## 4 — SLEEP OBFUSCATION — `build/sleep_obf.exe`
Défait : le scan mémoire au repos. Pendant le sleep, les pages passent RW et sont
chiffrées (XOR démo / RC4 en prod). Au réveil : déchiffrement + retour RX.
Un EDR qui scanne la mémoire au repos ne voit QUE du chiffré.
## 5 — STACK SPOOFING — `build/stack_spoof.exe`
Défait : la call stack inspection (l'EDR regarde d'où vient l'appel).
Le concept : gadget ret trouvé dans ntdll, la chaîne de retour remplacée
par CreateFileA légitime. L'EDR voit un appel normal.
## 6 — LE CHAÎNON COMPLET (à construire en 1 process)
runner.cpp (à venir) : unhook → patch ETW → patch AMSI → sleep obf loop → syscalls direct
= l'agent Raven complet. Architecture fournie, assemblage = 1 session.

## TEST DEFENDER (VM Windows)
1. compile lexagent.exe SANS évasion → Defender le détecte (score X)
2. compile lexagent.exe AVEC unhook + ETW + syscalls → Defender ne détecte plus (score Y)
3. comparer X vs Y : c'est la preuve mesurable de l'évasion

## DÉTECTIONS RÉSIDUELLES (honnêteté)
- ETW-TI kernel (Windows 11 22H2+) : voit les syscalls directs au niveau kernel
- VBS/HVCI : bloque certaines écritures de mémoire kernel
- Les 4 patches doivent être relancés à chaque démarrage d'agent (pas persistant)

## FICHIERS
src/syscalls_direct.cpp · src/unhook_ntdll.cpp · src/etw_amsi_patch.cpp
src/sleep_obf.cpp · src/stack_spoof.cpp
build/ : les 5 .exe x64 cross-compilés ✓
verify_raven.zsh : compile tout
