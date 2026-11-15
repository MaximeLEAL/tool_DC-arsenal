# modules/crypto.py - la cryo-chambre de la cave
import os, subprocess, hashlib, secrets, string

def ask(label): return input(f"  {label} : ").strip()
def r(cmd): subprocess.run(cmd, shell=True)

def swiss():
    t = ask("encode(e64/hex/rot13) ou decode(base64/hex)").lower()
    v = ask("valeur")
    if t.startswith("e64"): print("  base64 :", v.encode().hex() and __import__("base64").b64encode(v.encode()).decode())
    elif t.startswith("d64"):
        import base64
        print("  texte  :", base64.b64decode(v).decode(errors="ignore"))
    elif t == "ehex": print("  hex :", v.encode().hex())
    elif t == "dhex": print("  texte :", bytes.fromhex(v).decode(errors="ignore"))
    elif t == "rot13":
        import codecs
        print("  rot13 :", codecs.encode(v, "rot13"))

def aes_file():
    f = ask("fichier")
    mode = ask("encrypt ou decrypt").lower()
    pw = ask("mot de passe")
    if mode == "encrypt":
        r(f'openssl enc -aes-256-cbc -pbkdf2 -salt -in "{f}" -out "{f}.bat" -pass pass:"{pw}"')
        print(f"  [OK] {f}.bat")
    else:
        r(f'openssl enc -d -aes-256-cbc -pbkdf2 -in "{f}" -out "{f}.clair" -pass pass:"{pw}"')
        print(f"  [OK] {f}.clair")

def crack_md5():
    h = ask("hash md5/sha1").strip().lower()
    wl = ask("wordlist (vide = dictionnaire systeme)") or "/usr/share/dict/words"
    if not os.path.exists(wl):
        print("  wordlist absente"); return
    n = 0
    for w in open(wl, errors="ignore"):
        w = w.strip()
        if not w: continue
        n += 1
        if hashlib.md5(w.encode()).hexdigest() == h:
            print(f"  [CRACK MD5] '{w}' ({n} essais)"); return
        if hashlib.sha1(w.encode()).hexdigest() == h:
            print(f"  [CRACK SHA1] '{w}' ({n} essais)"); return
    print(f"  echec ({n} essais) - ajoute des regles ou une meilleure wordlist")

def pwgen():
    n = int(ask("longueur") or 20)
    pool = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    print("  " + "".join(secrets.choice(pool) for _ in range(n)))

def caesar():
    v = ask("texte")
    for s in range(1, 26):
        out = "".join(chr((ord(c) - 97 + s) % 26 + 97) if c.islower() else c for c in v)
        print(f"  rot{str(s).zfill(2)} : {out}")

def checksums():
    f = ask("fichier")
    data = open(f, "rb").read()
    print(f"  md5    {hashlib.md5(data).hexdigest()}")
    print(f"  sha1   {hashlib.sha1(data).hexdigest()}")
    print(f"  sha256 {hashlib.sha256(data).hexdigest()}")
