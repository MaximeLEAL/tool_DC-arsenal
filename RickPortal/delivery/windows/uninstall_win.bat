@echo off
REM RickPortal Windows - nettoyage complet de la machine de lab
schtasks /delete /f /tn RickKey    >nul 2>&1
schtasks /delete /f /tn RickScreen >nul 2>&1
schtasks /delete /f /tn RickCam    >nul 2>&1
schtasks /delete /f /tn RickMic    >nul 2>&1
schtasks /delete /f /tn RickUsb    >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v RickShell /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v RickClip /f >nul 2>&1
taskkill /f /im 01_keylogger.exe     >nul 2>&1
taskkill /f /im 02_reverse_shell.exe >nul 2>&1
taskkill /f /im 04_clipboard.exe     >nul 2>&1
taskkill /f /im 05_usb_worm.exe      >nul 2>&1
taskkill /f /im 07_screenspy.exe     >nul 2>&1
taskkill /f /im 08_webcam.exe        >nul 2>&1
taskkill /f /im 09_dropper.exe       >nul 2>&1
taskkill /f /im 10_mic_rec.exe       >nul 2>&1
rmdir /s /q "%APPDATA%\RickPortal" >nul 2>&1
del "%USERPROFILE%\rick_key.bin" >nul 2>&1
echo [OK] machine propre
