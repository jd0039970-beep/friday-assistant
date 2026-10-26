; Inno Setup script — compile with Inno Setup to produce Setup-Friday.exe
; Point it at the PyInstaller dist folder after build_windows.ps1

[Setup]
AppName=F.R.I.D.A.Y
AppVersion=0.6.0
DefaultDirName={autopf}\Friday
DefaultGroupName=F.R.I.D.A.Y
OutputBaseFilename=Setup-Friday
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "..\backend\dist\Friday\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\F.R.I.D.A.Y"; Filename: "{app}\start_friday.bat"
Name: "{group}\Update F.R.I.D.A.Y"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\update_friday.ps1"""
Name: "{userdesktop}\F.R.I.D.A.Y"; Filename: "{app}\start_friday.bat"

[Run]
Filename: "{app}\start_friday.bat"; Description: "Launch F.R.I.D.A.Y"; Flags: nowait postinstall skipifsilent
