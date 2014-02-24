; .. Copyright (C) 2012-2013 Bryan A. Jones.
;
;    This file is part of Enki.
;
;    Enki is free software: you can redistribute it and/or
;    modify it under the terms of the GNU General Public
;    License as published by the Free Software Foundation,
;    either version 2 of the License, or (at your option)
;    any later version.
;
;    Enki is distributed in the hope that it will be useful,
;    but WITHOUT ANY WARRANTY; without even the implied 
;    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
;    PURPOSE.  See the GNU General Public License for more
;    details.
;
;    You should have received a copy of the GNU General
;    Public License along with Enki.  If not, see
;    <http://www.gnu.org/licenses/>.
;
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
#define PRODUCT_VERSION GetDateTimeString('ddddd', '', '');

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
