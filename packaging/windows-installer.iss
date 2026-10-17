#ifndef AppSource
  #define AppSource "..\dist\portable-1.0.1"
#endif
[Setup]
AppId={{781F7313-7FF8-434C-A4CA-CF71D1141F5B}
AppName=ST VidÃ©o
AppVersion=1.0.1
AppPublisher=David Ascenso
DefaultDirName={localappdata}\Programs\STVideo
DefaultGroupName=ST VidÃ©o
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\dist
OutputBaseFilename=STVideo-1.0.1-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\STVideo.exe
CloseApplications=yes
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
[CustomMessages]
english.DesktopIcon=Create a desktop shortcut
french.DesktopIcon=Créer un raccourci sur le Bureau
english.LaunchProgram=Launch ST Vidéo
french.LaunchProgram=Lancer ST Vidéo
[Tasks]
Name: "desktopicon"; Description: "CrÃ©er un raccourci sur le Bureau"; Flags: unchecked
[Files]
Source: "{#AppSource}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{autoprograms}\ST VidÃ©o"; Filename: "{app}\STVideo.exe"
Name: "{autodesktop}\ST VidÃ©o"; Filename: "{app}\STVideo.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\STVideo.exe"; Description: "Lancer ST VidÃ©o"; Flags: nowait postinstall skipifsilent
