/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UISettingsAStyle.cpp
** Date      : 2008-01-14T00:39:48
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
#include "UISettingsAStyle.h"

#include <coremanager/MonkeyCore.h>
#include <settingsmanager/Settings.h>

UISettingsAStyle::UISettingsAStyle( QWidget* p )
    : QWidget( p )
{
    setupUi( this );
    setAttribute( Qt::WA_DeleteOnClose );
    // connect radio button
    QList<QRadioButton*> l = gbStyles->findChildren<QRadioButton*>();
    foreach ( QRadioButton* rb, l )
        connect( rb, SIGNAL( clicked() ), SLOT( onStyleChange() ) );
    // load settings
    loadSettings();
}

void UISettingsAStyle::setStyle( AStylePredefinedStyle s )
{
    QString sample;
    switch ( s )
    {
    case aspsAnsi:
        sample = "namespace foospace\n{\n    int Foo()\n    {\n        if (isBar)\n        {\n            bar();\n            return 1;\n        }\n        else\n            return 0;\n    }\n}";
        rbANSI->setChecked( true );
        break;
    case aspsKr:
        sample = "namespace foospace {\n    int Foo() {\n        if (isBar) {\n            bar();\n            return 1;\n         } else\n            return 0;\n    }\n}";
        rbKR->setChecked( true );
        break;
    case aspsLinux:
        sample = "namespace foospace\n{\n        int Foo()\n        {\n                if (isBar) {\n                        bar();\n                        return 1;\n                 }\n                 else\n                        return 0;\n        }\n}";
        rbLinux->setChecked( true );
        break;
    case aspsGnu:
        sample = "namespace foospace\n  {\n  int Foo()\n  {\n    if (isBar)\n      {\n        bar();\n        return 1;\n      }\n    else\n      return 0;\n  }\n}";
        rbGNU->setChecked( true );
        break;
    case aspsJava:
        sample = "namespace foospace {\n    int Foo() {\n        if (isBar) {\n            bar();\n            return 1;\n         }\n         else\n            return 0;\n    }\n}";
        rbJava->setChecked( true );
        break;
    default:
        rbCustom->setChecked( true );
        break;
    }
    
    bool en = s != aspsCustom;
    teSample->setText( sample );
    teSample->setEnabled( en );
    // disable/enable checkboxes based on style
    spnIndentation->setEnabled( !en );
    chkUseTab->setEnabled( !en );
    chkForceUseTabs->setEnabled( !en );
    chkConvertTabs->setEnabled( !en );
    chkFillEmptyLines->setEnabled( !en );
    chkIndentClasses->setEnabled( !en );
    chkIndentSwitches->setEnabled( !en );
    chkIndentCase->setEnabled( !en );
    chkIndentBrackets->setEnabled( !en );
    chkIndentBlocks->setEnabled( !en );
    chkIndentNamespaces->setEnabled( !en );
    chkIndentLabels->setEnabled( !en );
    chkIndentPreprocessor->setEnabled( !en );
    cmbBreakType->setEnabled( !en );
    chkBreakBlocks->setEnabled( !en );
    chkBreakElseIfs->setEnabled( !en );
    chkPadOperators->setEnabled( !en );
    chkPadParens->setEnabled( !en );
    chkKeepComplex->setEnabled( !en );
    chkKeepBlocks->setEnabled( !en );
}

void UISettingsAStyle::onStyleChange()
{
    QRadioButton* rb = qobject_cast<QRadioButton*>( sender() );
    if ( rb == rbANSI )
        setStyle( aspsAnsi );
    else if ( rb == rbKR )
        setStyle( aspsKr );
    else if ( rb == rbLinux )
        setStyle( aspsLinux );
    else if ( rb == rbGNU )
        setStyle( aspsGnu );
    else if ( rb == rbJava )
        setStyle( aspsJava );
    else if ( rb == rbCustom )
        setStyle( aspsCustom );
}

void UISettingsAStyle::loadSettings()
{
    Settings* s = MonkeyCore::settings();
    s->beginGroup( QString( "Plugins/%1" ).arg( PLUGIN_NAME ) );
    int style = s->value( "style", 0 ).toInt();
    spnIndentation->setValue( s->value( "indentation", 4 ).toInt() );
    chkUseTab->setChecked( s->value( "use_tabs", false ).toBool() );
    chkForceUseTabs->setChecked( s->value( "force_tabs", false ).toBool() );
    chkConvertTabs->setChecked( s->value( "convert_tabs", false ).toBool() );
    chkFillEmptyLines->setChecked( s->value( "fill_empty_lines", false ).toBool() );
    chkIndentClasses->setChecked( s->value( "indent_classes", false ).toBool() );
    chkIndentSwitches->setChecked( s->value( "indent_switches", false ).toBool() );
    chkIndentCase->setChecked( s->value( "indent_case", false ).toBool() );
    chkIndentBrackets->setChecked( s->value( "indent_brackets", false ).toBool() );
    chkIndentBlocks->setChecked( s->value( "indent_blocks", false ).toBool() );
    chkIndentNamespaces->setChecked( s->value( "indent_namespaces", false ).toBool() );
    chkIndentLabels->setChecked( s->value( "indent_labels", false ).toBool() );
    chkIndentPreprocessor->setChecked( s->value( "indent_preprocessor", false ).toBool() );
    cmbBreakType->setCurrentIndex( s->value( "break_type", 0 ).toInt() );
    chkBreakBlocks->setChecked( s->value( "break_blocks", false ).toBool() );
    chkBreakElseIfs->setChecked( s->value( "break_elseifs", false ).toBool() );
    chkPadOperators->setChecked( s->value( "pad_operators", false ).toBool() );
    chkPadParens->setChecked( s->value( "pad_parentheses", false ).toBool() );
    chkKeepComplex->setChecked( s->value( "keep_complex", false ).toBool() );
    chkKeepBlocks->setChecked( s->value( "keep_blocks", false ).toBool() );
    s->endGroup();
    setStyle( ( AStylePredefinedStyle )style );
}

void UISettingsAStyle::saveSettings()
{
    int style = 0;
    if ( rbANSI->isChecked() )
        style = 0;
    else if ( rbKR->isChecked() )
        style = 1;
    else if ( rbLinux->isChecked() )
        style = 2;
    else if ( rbGNU->isChecked() )
        style = 3;
    else if ( rbJava->isChecked() )
        style = 4;
    else if ( rbCustom->isChecked() )
        style = 5;
    Settings* s = MonkeyCore::settings();
    s->beginGroup( QString( "Plugins/%1" ).arg( PLUGIN_NAME ) );
    s->setValue( "style", style );
    s->setValue( "indentation", spnIndentation->value() );
    s->setValue( "use_tabs", chkUseTab->isChecked() );
    s->setValue( "force_tabs", chkForceUseTabs->isChecked() );
    s->setValue( "convert_tabs", chkConvertTabs->isChecked() );
    s->setValue( "fill_empty_lines", chkFillEmptyLines->isChecked() );
    s->setValue( "indent_classes", chkIndentClasses->isChecked() );
    s->setValue( "indent_switches", chkIndentSwitches->isChecked() );
    s->setValue( "indent_case", chkIndentCase->isChecked() );
    s->setValue( "indent_brackets", chkIndentBrackets->isChecked() );
    s->setValue( "indent_blocks", chkIndentBlocks->isChecked() );
    s->setValue( "indent_namespaces", chkIndentNamespaces->isChecked() );
    s->setValue( "indent_labels", chkIndentLabels->isChecked() );
    s->setValue( "indent_preprocessor", chkIndentPreprocessor->isChecked() );
    s->setValue( "break_type",  cmbBreakType->currentIndex () );
    s->setValue( "break_blocks", chkBreakBlocks->isChecked() );
    s->setValue( "break_elseifs", chkBreakElseIfs->isChecked() );
    s->setValue( "pad_operators", chkPadOperators->isChecked() );
    s->setValue( "pad_parentheses", chkPadParens->isChecked() );
    s->setValue( "keep_complex", chkKeepComplex->isChecked() );
    s->setValue( "keep_blocks", chkKeepBlocks->isChecked() );
    s->endGroup();
}

void UISettingsAStyle::on_pbApply_clicked()
{ saveSettings(); }
