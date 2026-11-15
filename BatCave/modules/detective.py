# modules/detective.py - la detects du Batcave
import os, subprocess, hashlib, zlib, struct, re, urllib.parse

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def email_analysis():
    raw = ask("colle les headers (ligne vide pour finir, ou chemin .eml)")
    lines = []
    if os.path.exists(raw):
        lines = open(raw, errors="ignore").read().splitlines()
    else:
        while True:
            l = input()
            if not l.strip(): break
            lines.append(l)
    text = "\n".join(lines)
    ips = re.findall(r"Received:.*?\[([\d.]+)\]", text)
    print("\n  IP de relais (de la plus proche a la plus lointaine) :")
    for ip in ips: print("   ", ip)
    for h in ["From", "Reply-To", "Return-Path", "X-Mailer", "Subject", "Authentication-Results", "SPF"]:
        for line in lines:
            if line.lower().startswith(h.lower()):
                print(f"   {line.strip()}")

def image_forensic():
    f = ask("chemin de l'image")
    if not os.path.exists(f):
        print("  fichier introuvable"); return
    md5 = hashlib.md5(open(f, "rb").read()).hexdigest()
    sha = hashlib.sha256(open(f, "rb").read()).hexdigest()
    print(f"  md5     {md5}\n  sha256  {sha}")
    r(f"mdls -name kMDItemContentCreationDate -name kMDItemGPSLatitude -name kMDItemGPSLongitude -name kMDItemAcquisitionModel '{f}'")
    u = urllib.parse.quote(open(f, "rb").read(0))  # placeholder
    print("\n  recherche inverse (colle le md5 ou uploade l'image) :")
    print("   https://tineye.com/        (upload)")
    print("   https://images.google.com/ (glisser-deposer)")
    print("   https://yandex.com/images/ (glisser-deposer)")

def _png_chunks(data):
    pos = 8
    while pos < len(data) - 8:
        length = struct.unpack(">I", data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+length]
        yield ctype, chunk
        pos += 12 + length

def stego_hide():
    png = ask("PNG de base")
    secret = ask("message secret")
    if not os.path.exists(png):
        print("  fichier introuvable"); return
    data = open(png, "rb").read()
    payload = b"batsecret\x00" + secret.encode()
    chunk = struct.pack(">I", len(payload)) + b"tEXt" + payload
    chunk += struct.pack(">I", zlib.crc32(b"tEXt" + payload) & 0xFFFFFFFF)
    # insertion propre : juste avant le chunk IEND (12 derniers octets du fichier)
    out = data[:-12] + chunk + data[-12:]
    dest = png.replace(".png", "") + "_cache.png"
    open(dest, "wb").write(out)
    print(f"  [OK] secret embarque -> {dest}")

def stego_reveal():
    png = ask("PNG a analyser")
    if not os.path.exists(png):
        print("  fichier introuvable"); return
    data = open(png, "rb").read()
    i = data.find(b"batsecret\x00")
    if i >= 0:
        print("  SECRET REVELÉ :", data[i + 9:].split(b"IEND")[0].decode(errors="ignore"))
        return
    print("  aucun secret de la cave dans ce PNG")

def domain_dossier():
    d = ask("domaine")
    print("\n  --- WHOIS ---")
    r(f"whois {d} | head -25")
    print("\n  --- DNS ---")
    r(f"dig +short {d} A; dig +short {d} MX; dig +short {d} NS")

def hash_id():
    h = ask("hash").strip().lower()
    guess = {32: "MD5", 40: "SHA1", 64: "SHA256", 128: "SHA512"}.get(len(h), "?")
    print(f"  longueur {len(h)} -> probablement {guess}")
    if guess in ("MD5", "SHA1"):
        algo = hashlib.md5 if guess == "MD5" else hashlib.sha1
        wl = "/usr/share/dict/words"
        if os.path.exists(wl):
            n = 0
            for w in open(wl, errors="ignore"):
                w = w.strip()
                n += 1
                if algo(w.encode()).hexdigest() == h:
                    print(f"  [CRACK] trouve : '{w}' ({n} essais)")
                    return
            print(f"  pas dans le dictionnaire ({n} essais)")
        else:
            print("  pas de dictionnaire systeme")
