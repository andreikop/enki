'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UISettings.h
** Date      : 2008-01-14T00:36:54
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
#ifndef UISETTINGS_H
#define UISETTINGS_H

#include <objects/MonkeyExport.h>
#include <objects/QSingleton.h>

#include "ui_UISettings.h"

class QsciLexer

class Q_MONKEY_EXPORT UISettings : public QDialog, Ui.UISettings, QSingleton<UISettings>
    Q_OBJECT
    friend class QSingleton<UISettings>

private:
    UISettings( QWidget* = 0 )
    void loadSettings()
    void saveSettings()
    QButtonGroup* bgAutoCompletionSource
    QButtonGroup* bgCallTipsStyle
    QButtonGroup* bgBraceMatch
    QButtonGroup* bgEdgeMode
    QButtonGroup* bgFoldStyle
    QButtonGroup* bgEolMode
    QButtonGroup* bgWhitespaceVisibility
    QButtonGroup* bgWrapMode
    QButtonGroup* bgStartWrapVisualFlag
    QButtonGroup* bgEndWrapVisualFlag
    QHash<QString, mLexers

public slots:
    void reject()
    void accept()
    void apply()

private slots:
    void on_twMenu_itemSelectionChanged()
    void on_pbDefaultDocumentFont_clicked()
    void on_gbAutoCompletionEnabled_clicked( bool checked )
    void tbFonts_clicked()
    void cbSourceAPIsLanguages_beforeChanged( int )
    void on_cbSourceAPIsLanguages_currentIndexChanged( int )
    void on_pbSourceAPIsDelete_clicked()
    void on_pbSourceAPIsAdd_clicked()
    void on_pbSourceAPIsBrowse_clicked()
    void on_twLexersAssociations_itemSelectionChanged()
    void on_pbLexersAssociationsAddChange_clicked()
    void on_pbLexersAssociationsDelete_clicked()
    void on_cbLexersHighlightingLanguages_currentIndexChanged(  QString& )
    void on_lwLexersHighlightingElements_itemSelectionChanged()
    void lexersHighlightingColour_clicked()
    void lexersHighlightingFont_clicked()
    void on_cbLexersHighlightingFillEol_clicked( bool )
    void cbLexersHighlightingProperties_clicked( bool )
    void on_cbLexersHighlightingIndentationWarning_currentIndexChanged( int )
    void on_pbLexersHighlightingReset_clicked()
    void on_pbLexersApplyDefaultFont_clicked()
    void on_twAbbreviations_itemSelectionChanged()
    void on_pbAbbreviationsAdd_clicked()
    void on_pbAbbreviationsRemove_clicked()
    void on_teAbbreviationsCode_textChanged()


#endif # UISETTINGS_H
