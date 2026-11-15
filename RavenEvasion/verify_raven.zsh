#!/bin/zsh
# RavenEvasion - verify_raven.zsh : compile les 5 modules d'évasion
cd "$(dirname "$0")"
mkdir -p build
CC=x86_64-w64-mingw32-g++
for f in syscalls_direct unhook_ntdll etw_amsi_patch sleep_obf stack_spoof; do
    LIBS=""
    [ "$f" = "stack_spoof" ] && LIBS="-lpsapi"
    "$CC" -O2 -std=c++17 -Wno-narrowing src/$f.cpp -o build/$f.exe $LIBS 2>&1 | head -2
    [ $? -eq 0 ] && echo "OK   $f" || echo "FAIL $f"
done
echo "[*] binaire dans build/ - test face à Defender dans la VM Windows"
