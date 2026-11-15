# LEXCORP INDUSTRIES — powered by Maxime Leal

L'arsenal Windows offensif de Luthor : injection, hollowing, APC, ransomware v2,
worm SMB, crypter. Tout cross-compilé x64 (`build/`), runtime à valider en VM Windows.

Compilation : `zsh verify_lex.zsh` (inclus) — `x86_64-w64-mingw32-g++` requis.

---

## 1 — LEX_INJECT_DLL
**Quoi** : injecte une DLL dans un processus vivant (VirtualAllocEx + CreateRemoteThread → LoadLibraryW).
**Usage** : `lex_inject_dll.exe <pid> <dll>` — ex `lex_inject_dll.exe 1234 C:\Users\Public\lex_test_dll.dll`.
**Preuve** : injecte `lex_test_dll.dll` → MessageBox « LexCorp was here » dans la cible.
**Détection** : WriteRemoteMemory + remote thread sont les IOCs classiques d'EDR.

## 2 — LEX_HOLLOW
**Quoi** : process hollowing — crée un processus légitime en suspend, démappe son image, écrit ton PE à la place, reprend l'exécution. Le process porte l'apparence de svchost, l'âme de ton payload.
**Usage** : `lex_hollow.exe C:\Windows\System32\notepad.exe C:\Users\Public\payload.exe`.

## 3 — LEX_APC
**Quoi** : APC injection — le shellcode (stub LoadLibrary) est mis en file d'APC d'un thread suspendu ; exécuté au ResumeThread.
**Usage** : `lex_apc.exe <legitime> <dll>`.

## 4 — LEX_RANSOM2
**Quoi** : ransomware v2 — supprime les shadow copies (`vssadmin delete shadows /all`), chiffre AES-256-CBC **partiel** (1er Mo de chaque fichier : quasi instantané), note localisée, extension `.lexcor`.
**Modes** : lancer = chiffrer · `lex_ransom2.exe decrypt` = restaurer (clé dans `%USERPROFILE%\lex_key.bin`, démo réversible).
**Test** : dossier leurre sur le Desktop de la VM, snapshot avant.

## 5 — LEX_SMB_WORM
**Quoi** : sweep /24 en 24 threads, montages `C$` avec liste de creds faibles, drop de lui-même dans `Users\Public`, puis **tâche planifiée à distance** (`schtasks /s \\host /tn LexSvc`) — l'exécution est déclenchée sur la cible le lendemain 3h13.
**Usage** : `lex_smb_worm.exe [password]`. Code retour = nombre d'infections.

## 6 — LEX_CRYPTER (lex_crypter_win.cpp + lex_crypter.py)
**Quoi** : crypter — le payload est RC4-chiffré, la clé noyée dans le binaire, strings xorées ; exécution cachée puis effacement de la trace.
**Usage** : `python3 lex_crypter.py payload.exe` → génère `lex_loader_gen.cpp` → compile → `lex_loader.exe`. Le payload n'apparaît jamais en clair dans le binaire final.
**Note** : l'exécution passe par un drop chiffré→décrypté sur disque ; la version in-memory (manual mapping) est l'étage suivant.

## 7 — LEX_TEST_DLL
**Quoi** : DLL de démonstration (MessageBox à l'attach) — la preuve visuelle des trois méthodes d'injection.
