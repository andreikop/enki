'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UISettingsAStyle.cpp
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
#include "UISettingsAStyle.h"

#include <coremanager/MonkeyCore.h>
#include <settingsmanager/Settings.h>

UISettingsAStyle.UISettingsAStyle( QWidget* p )
    : QWidget( p )
    setupUi( self )
    setAttribute( Qt.WA_DeleteOnClose )
    # connect radio button
    QList<QRadioButton*> l = gbStyles.findChildren<QRadioButton*>()
    for rb in l:
        connect( rb, SIGNAL( clicked() ), SLOT( onStyleChange() ) )
    # load settings
    loadSettings()


def setStyle(self, s ):
    QString sample
    switch ( s )
    case aspsAnsi:
        sample = "namespace foospace\n{\n    int Foo()\n    {\n        if (isBar)\n        {\n            bar();\n            return 1;\n        }\n        else\n            return 0;\n    }\n}"
        rbANSI.setChecked( True )
        break
    case aspsKr:
        sample = "namespace foospace {\n    int Foo() {\n        if (isBar) {\n            bar();\n            return 1;\n         } else\n            return 0;\n    }\n}"
        rbKR.setChecked( True )
        break
    case aspsLinux:
        sample = "namespace foospace\n{\n        int Foo()\n        {\n                if (isBar) {\n                        bar();\n                        return 1;\n                 }\n                 else\n                        return 0;\n        }\n}"
        rbLinux.setChecked( True )
        break
    case aspsGnu:
        sample = "namespace foospace\n  {\n  int Foo()\n  {\n    if (isBar)\n      {\n        bar();\n        return 1;\n      }\n    else\n      return 0;\n  }\n}"
        rbGNU.setChecked( True )
        break
    case aspsJava:
        sample = "namespace foospace {\n    int Foo() {\n        if (isBar) {\n            bar();\n            return 1;\n         }\n         else\n            return 0;\n    }\n}"
        rbJava.setChecked( True )
        break
    default:
        rbCustom.setChecked( True )
        break

    
    en = s != aspsCustom
    teSample.setText( sample )
    teSample.setEnabled( en )
    # disable/enable checkboxes based on style
    spnIndentation.setEnabled( not en )
    chkUseTab.setEnabled( not en )
    chkForceUseTabs.setEnabled( not en )
    chkConvertTabs.setEnabled( not en )
    chkFillEmptyLines.setEnabled( not en )
    chkIndentClasses.setEnabled( not en )
    chkIndentSwitches.setEnabled( not en )
    chkIndentCase.setEnabled( not en )
    chkIndentBrackets.setEnabled( not en )
    chkIndentBlocks.setEnabled( not en )
    chkIndentNamespaces.setEnabled( not en )
    chkIndentLabels.setEnabled( not en )
    chkIndentPreprocessor.setEnabled( not en )
    cmbBreakType.setEnabled( not en )
    chkBreakBlocks.setEnabled( not en )
    chkBreakElseIfs.setEnabled( not en )
    chkPadOperators.setEnabled( not en )
    chkPadParens.setEnabled( not en )
    chkKeepComplex.setEnabled( not en )
    chkKeepBlocks.setEnabled( not en )


def onStyleChange(self):
    rb = qobject_cast<QRadioButton*>( sender() )
    if  rb == rbANSI :
        setStyle( aspsAnsi )
    elif  rb == rbKR :
        setStyle( aspsKr )
    elif  rb == rbLinux :
        setStyle( aspsLinux )
    elif  rb == rbGNU :
        setStyle( aspsGnu )
    elif  rb == rbJava :
        setStyle( aspsJava )
    elif  rb == rbCustom :
        setStyle( aspsCustom )


def loadSettings(self):
    s = MonkeyCore.settings()
    s.beginGroup( QString( "Plugins/%1" ).arg( PLUGIN_NAME ) )
    style = s.value( "style", 0 ).toInt()
    spnIndentation.setValue( s.value( "indentation", 4 ).toInt() )
    chkUseTab.setChecked( s.value( "use_tabs", False ).toBool() )
    chkForceUseTabs.setChecked( s.value( "force_tabs", False ).toBool() )
    chkConvertTabs.setChecked( s.value( "convert_tabs", False ).toBool() )
    chkFillEmptyLines.setChecked( s.value( "fill_empty_lines", False ).toBool() )
    chkIndentClasses.setChecked( s.value( "indent_classes", False ).toBool() )
    chkIndentSwitches.setChecked( s.value( "indent_switches", False ).toBool() )
    chkIndentCase.setChecked( s.value( "indent_case", False ).toBool() )
    chkIndentBrackets.setChecked( s.value( "indent_brackets", False ).toBool() )
    chkIndentBlocks.setChecked( s.value( "indent_blocks", False ).toBool() )
    chkIndentNamespaces.setChecked( s.value( "indent_namespaces", False ).toBool() )
    chkIndentLabels.setChecked( s.value( "indent_labels", False ).toBool() )
    chkIndentPreprocessor.setChecked( s.value( "indent_preprocessor", False ).toBool() )
    cmbBreakType.setCurrentIndex( s.value( "break_type", 0 ).toInt() )
    chkBreakBlocks.setChecked( s.value( "break_blocks", False ).toBool() )
    chkBreakElseIfs.setChecked( s.value( "break_elseifs", False ).toBool() )
    chkPadOperators.setChecked( s.value( "pad_operators", False ).toBool() )
    chkPadParens.setChecked( s.value( "pad_parentheses", False ).toBool() )
    chkKeepComplex.setChecked( s.value( "keep_complex", False ).toBool() )
    chkKeepBlocks.setChecked( s.value( "keep_blocks", False ).toBool() )
    s.endGroup()
    setStyle( ( AStylePredefinedStyle )style )


def saveSettings(self):
    style = 0
    if  rbANSI.isChecked() :
        style = 0
    elif  rbKR.isChecked() :
        style = 1
    elif  rbLinux.isChecked() :
        style = 2
    elif  rbGNU.isChecked() :
        style = 3
    elif  rbJava.isChecked() :
        style = 4
    elif  rbCustom.isChecked() :
        style = 5
    s = MonkeyCore.settings()
    s.beginGroup( QString( "Plugins/%1" ).arg( PLUGIN_NAME ) )
    s.setValue( "style", style )
    s.setValue( "indentation", spnIndentation.value() )
    s.setValue( "use_tabs", chkUseTab.isChecked() )
    s.setValue( "force_tabs", chkForceUseTabs.isChecked() )
    s.setValue( "convert_tabs", chkConvertTabs.isChecked() )
    s.setValue( "fill_empty_lines", chkFillEmptyLines.isChecked() )
    s.setValue( "indent_classes", chkIndentClasses.isChecked() )
    s.setValue( "indent_switches", chkIndentSwitches.isChecked() )
    s.setValue( "indent_case", chkIndentCase.isChecked() )
    s.setValue( "indent_brackets", chkIndentBrackets.isChecked() )
    s.setValue( "indent_blocks", chkIndentBlocks.isChecked() )
    s.setValue( "indent_namespaces", chkIndentNamespaces.isChecked() )
    s.setValue( "indent_labels", chkIndentLabels.isChecked() )
    s.setValue( "indent_preprocessor", chkIndentPreprocessor.isChecked() )
    s.setValue( "break_type",  cmbBreakType.currentIndex () )
    s.setValue( "break_blocks", chkBreakBlocks.isChecked() )
    s.setValue( "break_elseifs", chkBreakElseIfs.isChecked() )
    s.setValue( "pad_operators", chkPadOperators.isChecked() )
    s.setValue( "pad_parentheses", chkPadParens.isChecked() )
    s.setValue( "keep_complex", chkKeepComplex.isChecked() )
    s.setValue( "keep_blocks", chkKeepBlocks.isChecked() )
    s.endGroup()


def on_pbApply_clicked(self):
{ saveSettings();
