[Setup]
AllowNoIcons=yes
AppName=Textractor
ArchitecturesAllowed=x86 x64
AppVersion={#VERSION}
CloseApplications=no
DefaultDirName={userdesktop}\Textractor
DirExistsWarning=no
DefaultGroupName=Textractor
MinVersion=6.1
OutputBaseFilename=Textractor-{#VERSION}-Setup
OutputDir=Builds
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog
SolidCompression=yes
Uninstallable=no

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "ru"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "tu"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "sc"; MessagesFile: "compiler:Languages\Unofficial\ChineseSimplified.isl"
Name: "id"; MessagesFile: "compiler:Languages\Unofficial\Indonesian.isl"
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "th"; MessagesFile: "compiler:Languages\Unofficial\Thai.isl"
Name: "ko"; MessagesFile: "compiler:Languages\Unofficial\Korean.isl"
Name: "it"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "fr"; MessagesFile: "compiler:Languages\French.isl"


[Files]
Source: "Builds\Runtime\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor--{#VERSION}\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Spanish-{#VERSION}\*"; DestDir: "{app}"; Languages: es; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Russian-{#VERSION}\*"; DestDir: "{app}"; Languages: ru; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Turkish-{#VERSION}\*"; DestDir: "{app}"; Languages: tu; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Simplified-Chinese-{#VERSION}\*"; DestDir: "{app}"; Languages: sc; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Indonesian-{#VERSION}\*"; DestDir: "{app}"; Languages: id; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Portuguese-{#VERSION}\*"; DestDir: "{app}"; Languages: pt; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Thai-{#VERSION}\*"; DestDir: "{app}"; Languages: th; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Korean-{#VERSION}\*"; DestDir: "{app}"; Languages: ko; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-Italian-{#VERSION}\*"; DestDir: "{app}"; Languages: it; Flags: recursesubdirs ignoreversion
Source: "Builds\Textractor-French-{#VERSION}\*"; DestDir: "{app}"; Languages: fr; Flags: recursesubdirs ignoreversion
Source: "INSTALL_THIS_UNICODE_FONT.ttf"; DestDir: "{autofonts}"; DestName: "ARIAL_UNICODE_MS.ttf"; FontInstall: "Arial Unicode MS";
