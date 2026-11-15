#!/usr/bin/env python3
# language: Python 3, file: thinker.py, target: macOS
# THE THINKER — LE LABO DE REVERSE ENGINEERING · powered by Maxime Leal
# radare2 + otool + strings + upx + watch dynamique — le tout en commandes simples.
# Usage: thinker.py analyze <binaire> | strings <binaire> | imports <binaire> |
#        unpack <binaire> | r2 <binaire> "cmd" | watch <pid> | diff a b | arsenal
import os, sys, subprocess, re, time
sys.path.insert(0, os.path.expanduser('~/Desktop/tool_DC'))
import dc_fullscreen as dfs

def exists(path):
    if not os.path.exists(path):
        print(f"[X] {path} introuvable"); sys.exit(1)

def r2cmd(path, cmd):
    return subprocess.run(f'r2 -q -c "{cmd}" "{path}" 2>/dev/null',
                          shell=True, capture_output=True, timeout=60).stdout.decode(errors="ignore")

def info(path):
    print("\033[38;2;155;48;255m=== FICHE TECHNIQUE ===\033[0m")
    subprocess.run(f"file '{path}'", shell=True)
    subprocess.run(f"ls -lh '{path}'", shell=True)

def analyze(path):
    exists(path)
    print(f"\033[38;2;155;48;255m=== ANALYSE COMPLÈTE : {os.path.basename(path)} ===\033[0m\n")
    info(path)
    print("\n\033[1;97m--- EN-TÊTES (r2 iI) ---\033[0m")
    out = subprocess.run(f'r2 -q -c "iI" "{path}" 2>/dev/null | head -20', shell=True, capture_output=True).stdout.decode()
    for line in out.splitlines()[:14]: print("  ", line)
    print("\n--- SECTIONS ---")
    out = r2cmd(path, "iS")
    for line in out.splitlines()[:12]: print("  ", line)
    print("\n--- LIBRAIRIES/IMPORTS ---")
    for tool in (["otool -L"] if not path.endswith(".exe") else ["x86_64-w64-mingw32-objdump -p"]):
        out = subprocess.run(f"{tool} '{path}' 2>/dev/null", shell=True, capture_output=True).stdout.decode()
        if out.strip():
            for line in out.splitlines()[:10]: print("  ", line.strip())
            break
    print("\n--- ENTROPIE / PROTECTION (upx test) ---")
    out = subprocess.run(f"upx -t '{path}' 2>&1", shell=True, capture_output=True).stdout.decode()
    print("  " + (out.strip()[:200] or "  pas de signature UPX"))
    print("\n[OK] analyse → utilise thinker.py strings/imports/r2 pour creuser")

INTERESTING = [
    (r"https?://[^\s\"']+", "URLs"),
    (r"\b\d{1,3}(\.\d{1,3}){3}\b", "IPs"),
    (r"[A-Za-z]:\\[^\s\"']+", "chemins Windows"),
    (r"(/Users/|/Library/|/tmp/|/etc/)[^\s\"']+", "chemins mac"),
    (r"(key|pass|token|secret|flag|c2|shell|hook|mutex|inject)", "mots chauds"),
]

def strings(path):
    exists(path)
    print(f"\033[38;2;155;48;255m=== STRINGS FILTRÉS : {os.path.basename(path)} ===\033[0m\n")
    raw = subprocess.run(f"strings -n 6 '{path}' 2>/dev/null", shell=True, capture_output=True).stdout.decode(errors="ignore")
    total = len(raw.splitlines())
    print(f"  {total} strings bruts — filtrage des intéressants :\n")
    for pat, label in INTERESTING:
        found = sorted(set(re.findall(pat, raw, re.I)))[:14]
        if found:
            print(f"  \033[38;2;255;215;0m[{label}]\033[0m")
            for s in found: print(f"    {s[:90]}")
            print()

def imports(path):
    exists(path)
    print(f"\033[38;2;155;48;255m=== IMPORTS/SYMBOLS ===\033[0m\n")
    if path.endswith(".exe") or ".dll" in path:
        out = subprocess.run(f"x86_64-w64-mingw32-objdump -p '{path}' 2>/dev/null | grep -A200 'DLL Name'",
                             shell=True, capture_output=True).stdout.decode()
        dlls = sorted(set(re.findall(r"\b(\w+\.dll)\b", out, re.I)))
        print("  DLL importées :", ", ".join(dlls) or "aucune")
        funcs = subprocess.run(f"x86_64-w64-mingw32-objdump -p '{path}' 2>/dev/null | grep -E '^[[:space:]]+[0-9]+[[:space:]]+[0-9]+' | awk '{{print $NF}}' | sort -u | head -40",
                               shell=True, capture_output=True).stdout.decode()
        print("\n  fonctions :")
        for f in funcs.splitlines(): print("   ", f)
    else:
        r("nm -gU " + path)
        r("otool -L " + path)

def unpack(path):
    exists(path)
    print(f"\033[38;2;155;48;255m=== UNPACK UPX ===\033[0m\n")
    out = subprocess.run(f"upx -d '{path}' -o '{path}.unpacked' 2>&1", shell=True, capture_output=True).stdout.decode()
    print(out[:400])
    if os.path.exists(path + ".unpacked"):
        print(f"  [OK] dépacké → {path}.unpacked — relance strings/analyze dessus")

def watch(pid):
    print(f"\033[38;2;155;48;255m=== WATCH PID {pid} — fichiers ouverts en direct (Ctrl+C) ===\033[0m\n")
    try:
        while True:
            os.system("clear")
            print(f"  watch pid {pid} — {time.strftime('%H:%M:%S')}\n")
            subprocess.run(f"lsof -p {pid} 2>/dev/null | grep -vE 'REG.*[.]dylib|txt|PIPE|unix|KQUEUE' | head -25", shell=True)
            time.sleep(2)
    except KeyboardInterrupt:
        print()

def diff(a, b):
    exists(a); exists(b)
    print(f"\033[38;2;155;48;255m=== DIFF {os.path.basename(a)} vs {os.path.basename(b)} ===\033[0m\n")
    sa = set(subprocess.run(f"strings -n 8 '{a}'", shell=True, capture_output=True).stdout.decode().splitlines())
    sb = set(subprocess.run(f"strings -n 8 '{b}'", shell=True, capture_output=True).stdout.decode().splitlines())
    only_a, only_b = sa - sb, sb - sa
    print(f"  strings uniquement dans {os.path.basename(a)} : {len(only_a)}")
    for s in sorted(only_a)[:12]: print("   <", s[:90])
    print(f"  strings uniquement dans {os.path.basename(b)} : {len(only_b)}")
    for s in sorted(only_b)[:12]: print("   >", s[:90])

ARSENAL_RE = [
    ("Ghidra (NSA)", "REF", "https://github.com/NationalSecurityAgency/ghidra",
     "le décompileur open-source de l'agence — headless pour automatiser"),
    ("radare2 / rizin", "REF", "https://github.com/radareorg/radare2",
     "le framework CLI — installé chez toi (r2 6.2.6)"),
    ("Cutter", "REF", "https://github.com/rizinorg/cutter", "l'interface graphique de rizin"),
    ("x64dbg", "REF", "https://github.com/x64dbg/x64dbg", "LE debugger Windows (VM requise)"),
    ("IDA Free / Pro", "FERMÉ", "https://hex-rays.com/", "le standard commercial — Free pour usage léger"),
    ("Binary Ninja", "FERMÉ", "https://binary.ninja/", "décompilateur commercial moderne"),
    ("Hopper", "FERMÉ", "https://www.hopperapp.com/", "le disassembler mac"),
    ("FLARE-VM", "REF", "https://github.com/mandiant/flare-vm", "la VM complète de reverse Mandiant"),
    ("Capstone", "REF", "https://github.com/capstone-engine/capstone", "le moteur de désassembly embarquable"),
    ("Unicorn Engine", "REF", "https://github.com/unicorn-engine/unicorn", "l'émulateur CPU universel"),
    ("de4dot / dnSpy", "REF", "https://github.com/dnSpyEx/dnSpy", "le reverse .NET"),
    ("Detect It Easy", "REF", "https://github.com/horsicq/DIE-engine", "identification de packer/compilateur"),
    ("PE-bear", "REF", "https://github.com/hasherezade/pe-bear-research", "l'explorateur de headers PE"),
    ("YARA", "REF", "https://github.com/VirusTotal/yara", "les signatures (ton Kryptonite les génère)"),
    ("Frida", "REF", "https://github.com/frida/frida", "le hooking dynamique — déjà dans ton arsenal Mobile"),
    ("upx", "REF", "https://github.com/upx/upx", "pack/unpack — installé chez toi"),
]

def arsenal():
    print("\033[38;2;155;48;255m=== L'ARSENAL REVERSE — les forteresses du domaine ===\033[0m\n")
    for name, st, link, desc in ARSENAL_RE:
        color = "\033[38;2;57;255;20m" if st == "REF" else "\033[38;2;136;153;255m"
        print(f"  {color}[{st}]\033[0m {name}")
        print(f"      {link}")
        print(f"      {desc}\n")
    print("  [\033[38;2;57;255;20mREF\033[0m] = open-source/public · [\033[38;2;136;153;255mFERMÉ\033[0m] = commercial/accès restreint")

def r(path, cmd=None):
    if cmd:
        print(r2cmd(path, cmd) or "")
    else:
        subprocess.run(f"r2 -q -c '{cmd or 'aaa; afl; pdf main'}' '{path}'", shell=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: thinker.py analyze|strings|imports|unpack|r2|watch|diff|arsenal <args>")
        print("ex: thinker.py analyze lexagent.exe · thinker.py strings binaire · thinker.py arsenal")
        sys.exit(0)
    cmd = sys.argv[1]
    if cmd == "arsenal": arsenal()
    elif cmd == "watch": watch(sys.argv[2])
    elif cmd == "diff": diff(sys.argv[2], sys.argv[3])
    elif cmd == "r2": r2cmd(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "aaa;afl")
    else:
        fn = {"analyze": analyze, "strings": strings, "imports": imports, "unpack": unpack}.get(cmd)
        if fn and len(sys.argv) > 2: fn(sys.argv[2])
        else: print("commande inconnue")
