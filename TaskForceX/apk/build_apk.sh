#!/bin/zsh
# apk/build_apk.sh - construit lex.apk (Android SDK requis)
# Prerequis: brew install --cask android-commandlinetools openjdk
#            puis: sdkmanager "platforms;android-33" "build-tools;33.0.2"
set -e
SDK="${ANDROID_HOME:-$HOME/Library/Android/sdk}"
BT="$SDK/build-tools/33.0.2"
PLAT="$SDK/platforms/android-33/android.jar"
cd "$(dirname "$0")"
mkdir -p build/classes build/dex

# 1. compilation java
javac -source 8 -target 8 -classpath "$PLAT" -d build/classes java/com/lexcorp/lexservice/*.java

# 2. dex
"$BT/d8" --release --lib "$PLAT" --output build/dex $(find build/classes -name '*.class')

# 3. package + align
"$BT/aapt2" link -o build/lex.unsigned.apk -I "$PLAT" --manifest AndroidManifest.xml
cd build/dex && zip -ju ../lex.unsigned.apk classes.dex && cd ../..

# 4. align + sign (cle de debug auto-generee)
[ -f debug.keystore ] || keytool -genkey -keystore debug.keystore -alias lex \
    -storepass lexcorp -keypass lexcorp -keyalg RSA -validity 10000 \
    -dname "CN=LexCorp"
"$BT/zipalign" -f 4 build/lex.unsigned.apk build/lex.aligned.apk
"$BT/apksigner" sign --ks debug.keystore --ks-pass pass:lexcorp --out lex.apk build/lex.aligned.apk
echo "[OK] lex.apk pret - install sur ton appareil lab: adb install lex.apk"
