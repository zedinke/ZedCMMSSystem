; Inno Setup Script for Zed CMMS System
; This script creates a Windows installer for the CMMS application

#define AppName "Zed CMMS System"
#define AppPublisher "Zed"
#define AppURL "https://www.zed.com"
#define AppExeName "CMMS.exe"

; Version will be set by build script via /DVersion parameter
; Default version if not provided
#ifndef VersionString
  #define VersionString "1.0.0"
#endif

[Setup]
; Application information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#VersionString}
AppVerName={#AppName} {#VersionString}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
DisableDirPage=no
AllowRootDirectory=no
LicenseFile=installer\terms_of_service.txt
InfoBeforeFile=installer\gdpr_agreement.txt
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=ZedCMMS_Setup_v{#VersionString}
SetupIconFile=icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
VersionInfoVersion={#VersionString}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} - Computerized Maintenance Management System
VersionInfoCopyright=Copyright (C) 2025 {#AppPublisher}

[Languages]
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Updater executable
Source: "dist\Updater.exe"; DestDir: "{app}"; Flags: ignoreversion
; Templates directory
Source: "templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
; Localization files
Source: "localization\translations\*"; DestDir: "{app}\localization\translations"; Flags: ignoreversion recursesubdirs createallsubdirs
; Database migrations
Source: "migrations\versions\*"; DestDir: "{app}\migrations\versions"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "migrations\env.py"; DestDir: "{app}\migrations"; Flags: ignoreversion
Source: "migrations\script.py.mako"; DestDir: "{app}\migrations"; Flags: ignoreversion
Source: "alembic.ini"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure InitializeWizard;
begin
  // Create runtime data directories after installation
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  AppDataPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create runtime data directories in %LOCALAPPDATA%
    AppDataPath := ExpandConstant('{localappdata}\ZedCMMS');
    CreateDir(AppDataPath);
    CreateDir(AppDataPath + '\data');
    CreateDir(AppDataPath + '\data\logs');
    CreateDir(AppDataPath + '\data\files');
    CreateDir(AppDataPath + '\data\files\equipment_manuals');
    CreateDir(AppDataPath + '\data\files\maintenance_photos');
    CreateDir(AppDataPath + '\data\reports');
    CreateDir(AppDataPath + '\data\reports\generated');
    CreateDir(AppDataPath + '\data\system_backups');
    CreateDir(AppDataPath + '\generated_pdfs');
  end;
end;

