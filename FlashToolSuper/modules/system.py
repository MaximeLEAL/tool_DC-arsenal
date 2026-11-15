# modules/system.py - 7 outils d'audit systeme (macOS, reels)
import subprocess

def r(cmd): subprocess.run(cmd, shell=True)

def wifi_keys():
    r("for s in $(networksetup -listpreferredwirelessnetworks en0 2>/dev/null | tail -n +2); do security find-generic-password -wa \"$s\" 2>/dev/null && echo \"  ^^ cle de : $s\"; done")

def procs():
    r("ps aux | head -40")

def agents():
    print("  LaunchAgents utilisateur :")
    r("ls ~/Library/LaunchAgents/ 2>/dev/null")
    print("  LaunchAgents systeme (extraits) :")
    r("ls /Library/LaunchAgents/ 2>/dev/null | head -15")

def ports():
    r("lsof -nP -iTCP -sTCP:LISTEN | head -30")

def disk():
    r("df -h")

def history():
    r("tail -40 ~/.zsh_history 2>/dev/null || tail -40 ~/.bash_history")

def hw():
    r("system_profiler SPHardwareDataType SPSoftwareDataType | head -30")
