'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UICLIToolSettings.h
** Date      : 2008-01-14T00:36:59
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
#ifndef UICLITOOLSETTINGS_H
#define UICLITOOLSETTINGS_H

#include <objects/MonkeyExport.h>

#include "ui_UICLIToolSettings.h"
#include "consolemanager/pCommand.h"

#include <QWidget>

class BasePlugin

class Q_MONKEY_EXPORT UICLIToolSettings : public QWidget, Ui.UICLIToolSettings
    Q_OBJECT

protected:
    pCommandList mDefaults
    pCommandList mReset
    pCommandList mCommands
    BasePlugin* mPlugin
    bool mUpdating

public:
    UICLIToolSettings( BasePlugin*,  pCommandList&,  pCommandList&, QWidget* = 0 )

    void updateCommands()
    void restoreDefaults()
    void reset()
    void save()

protected slots:
    void on_lwCommands_itemSelectionChanged()
    void on_lwCommands_currentItemChanged( QListWidgetItem*, QListWidgetItem* )
    void on_pbCommandAdd_clicked()
    void on_pbCommandRemove_clicked()
    void on_pbCommandUp_clicked()
    void on_pbCommandDown_clicked()
    void on_tbCommandCommand_clicked()
    void on_tbCommandWorkingDirectory_clicked()
    void on_dbbButtons_clicked( QAbstractButton* )



#endif # UICLITOOLSETTINGS_H
