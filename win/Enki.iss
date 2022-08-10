; *************************************************************************************************
; Enki.iss - `Inno Setup <http://www.jrsoftware.org/isinfo.php>`_ Script to package the Enki binary
; *************************************************************************************************
; This produces a setup .exe to install Enki. It was created
; from ``Example1.iss`` which comes with Inno setup plus
; info from
; http://opencandy.com/2011/06/09/installer-platform-comparison-making-the-right-choice/.
;
; Provide a few handy definitions to avoid repetition.
#define PRODUCT_NAME 'Enki'
#define PRODUCT_VERSION '22.08.0'

[Setup]
AppName={#PRODUCT_NAME}
AppVersion={#PRODUCT_VERSION}
DefaultDirName={pf}\{#PRODUCT_NAME}
DefaultGroupName={#PRODUCT_NAME}
LicenseFile=..\LICENSE.GPL2.rtf
UninstallDisplayIcon={app}\bin\Enki.exe
Compression=lzma2
SolidCompression=yes
OutputBaseFilename="Install_{#PRODUCT_NAME}"
OutputDir=.
WizardImageFile=portrait-logo.bmp

[Files]
Source: "..\dist\all\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\{#PRODUCT_NAME}"; Filename: "{app}\bin\Enki.exe"
