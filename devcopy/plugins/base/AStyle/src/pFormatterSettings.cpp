'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : pFormatterSettings.cpp
** Date      : 2008-01-14T00:39:48
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
**
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "pFormatterSettings.h"

#include <coremanager/MonkeyCore.h>
#include <settingsmanager/Settings.h>

def applyTo(self, f ):
    s = MonkeyCore.settings()
    s.beginGroup( QString( "Plugins/%1" ).arg( PLUGIN_NAME ) )
    style = s.value( "style", 0 ).toInt()
    switch( style )
    case 0: # ansi
        f.bracketIndent = False
        f.indentLength = 4
        f.indentString = "    "
        f.bracketFormatMode = astyle.BREAK_MODE
        f.classIndent = False
        f.switchIndent = False
        f.namespaceIndent = True
        f.blockIndent = False
        f.breakBlocks = False
        f.breakElseIfs = False
        f.padOperators = False
        f.padParen = False
        f.breakOneLineStatements = True
        f.breakOneLineBlocks = True
        break
    case 1: # K&R
        f.bracketIndent = False
        f.indentLength = 4
        f.indentString = "    "
        f.bracketFormatMode = astyle.ATTACH_MODE
        f.classIndent = False
        f.switchIndent = False
        f.namespaceIndent = True
        f.blockIndent = False
        f.breakBlocks = False
        f.breakElseIfs = False
        f.padOperators = False
        f.padParen = False
        f.breakOneLineStatements = True
        f.breakOneLineBlocks = True
        break
    case 2: # Linux
        f.bracketIndent = False
        f.indentLength = 8
        f.indentString = "        "
        f.bracketFormatMode = astyle.BDAC_MODE
        f.classIndent = False
        f.switchIndent = False
        f.namespaceIndent = True
        f.blockIndent = False
        f.breakBlocks = False
        f.breakElseIfs = False
        f.padOperators = False
        f.padParen = False
        f.breakOneLineStatements = True
        f.breakOneLineBlocks = True
        break
    case 3: # GNU
        f.blockIndent = True
        f.bracketIndent = False
        f.indentLength = 2
        f.indentString = "  "
        f.bracketFormatMode = astyle.BREAK_MODE
        f.classIndent = False
        f.switchIndent = False
        f.namespaceIndent = False
        f.breakBlocks = False
        f.breakElseIfs = False
        f.padOperators = False
        f.padParen = False
        f.breakOneLineStatements = True
        f.breakOneLineBlocks = True
        break
    case 4: # Java
        f.sourceStyle = astyle.STYLE_JAVA
        f.modeSetManually = True
        f.bracketIndent = False
        f.indentLength = 4
        f.indentString = "    "
        f.bracketFormatMode = astyle.ATTACH_MODE
        f.switchIndent = False
        f.blockIndent = False
        f.breakBlocks = False
        f.breakElseIfs = False
        f.padOperators = False
        f.padParen = False
        f.breakOneLineStatements = True
        f.breakOneLineBlocks = True
        break
    case 5: #Runtime
        f.blockIndent = False
        f.bracketIndent = False
        f.indentLength = 4
        f.indentString = '\t'
        f.switchIndent = True
        f.caseIndent = False
        f.bracketFormatMode = astyle.NONE_MODE
        break
    default: # Custom
            spaceNum = s.value( "indentation", 4 ).toInt()
            #
            f.modeSetManually = False
            f.indentLength = spaceNum
            #
            f.indentString = '\t'
            if  not s.value( "use_tabs", False ).toBool() :
                f.indentString = string( spaceNum, ' ' )
            #
            f.forceTabIndent = False
            if  s.value( "force_tabs", False ).toBool() :
                f.indentString = '\t'
                f.forceTabIndent = True

            #
            f.convertTabs2Space = s.value( "convert_tabs", False ).toBool()
            f.emptyLineIndent = s.value( "fill_empty_lines", False ).toBool()
            f.classIndent = s.value( "indent_classes", False ).toBool()
            f.switchIndent = s.value( "indent_switches", False ).toBool()
            f.caseIndent = s.value( "indent_case", False ).toBool()
            f.bracketIndent = s.value( "indent_brackets", False ).toBool()
            f.blockIndent = s.value( "indent_blocks", False ).toBool()
            f.namespaceIndent = s.value( "indent_namespaces", False ).toBool()
            f.labelIndent = s.value( "indent_labels", False ).toBool()
            f.preprocessorIndent = s.value( "indent_preprocessor", False ).toBool()
            #
            breakType = s.value( "break_type", 0 ).toInt()
            switch( breakType )
            case 1: #break
                f.bracketFormatMode = astyle.BREAK_MODE
                break
            case 2: #attach
                f.bracketFormatMode = astyle.ATTACH_MODE
                break
            case 3: #linux
                f.bracketFormatMode = astyle.BDAC_MODE
                break
            default: #none
                f.bracketFormatMode = astyle.NONE_MODE
                break

            #
            f.breakBlocks = s.value( "break_blocks", False ).toBool()
            f.breakElseIfs = s.value( "break_elseifs", False ).toBool()
            f.padOperators = s.value( "pad_operators", False ).toBool()
            f.padParen = s.value( "pad_parentheses", False ).toBool()
            f.breakOneLineStatements = not s.value( "keep_complex", False ).toBool()
            f.breakOneLineBlocks = not s.value( "keep_blocks", False ).toBool()
            break


    s.endGroup()

