/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIPluginsSettings.h
** Date      : 2008-01-14T00:37:00
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
#ifndef UIPLUGINSSETTINGS_H
#define UIPLUGINSSETTINGS_H

#include <objects/MonkeyExport.h>

#include "ui_UIPluginsSettings.h"

#include <QApplication>

class Q_MONKEY_EXPORT UIPluginsSettings : public QDialog, public Ui::UIPluginsSettings
{
    Q_OBJECT

public:
    UIPluginsSettings( QWidget* = QApplication::activeWindow() );
    
protected:
    void updateList();
    
protected slots:
    void on_cbPluginType_currentIndexChanged( int );
};

#endif // UIPLUGINSSETTINGS_H
