#!/bin/zsh
# verify_build.zsh - cross-compile check (macOS host -> mingw-w64 PE)
cd "/Users/mleal/Documents/Projet par défaut/RickPortal"
CC=x86_64-w64-mingw32-g++
build() {
    local src="src/tools/$1.cpp" out="build/$1.exe"; shift
    "$CC" -O2 -std=c++17 "$src" -o "$out" "$@" 2>&1
    if [ $? -eq 0 ]; then echo "OK   $1"; else echo "FAIL $1"; fi
}
build 01_keylogger  -luser32
build 02_reverse_shell -lws2_32
build 03_ransomware -lbcrypt
build 04_clipboard  -ladvapi32
build 05_usb_worm
build 06_lan_worm   -lws2_32 -lmpr
build 07_screenspy  -lgdi32
build 08_webcam     -lavicap32
build 09_dropper    -lurlmon -ladvapi32
build 10_mic_rec    -lwinmm
"$CC" -O2 -std=c++17 src/rick_lab.cpp -o build/rick_lab.exe -luser32 2>&1 && echo "OK   rick_lab"
