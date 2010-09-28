/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, Andrei KOPATS aka hlamer, <hlamer at tut by>
** Project   : Monkey Studio Base Plugins
** FileName  : MessageBox.h
** Date      : 2008-01-14T00:39:59
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
/*!
    \file MessageBox.h
    \date 2008-01-14T00:40:08
    \author Filipe AZEVEDO, Andrei KOPATS
    \brief Header file for MessageBox plugin
*/
#ifndef MESSAGEBOX_H
#define MESSAGEBOX_H

#include <pluginsmanager/BasePlugin.h>

#include <QPointer>

class MessageBoxDocks;

/*!
    Main class of MessageBox plugin

    Plugin displaying console output and build steps of current building project
*/
class MessageBox : public BasePlugin
{
    Q_OBJECT
    Q_INTERFACES( BasePlugin )

public:
    virtual QWidget* settingsWidget();

protected:
    QPointer<MessageBoxDocks> mMessageBoxDocks;
    
    void fillPluginInfos();
    virtual bool install();
    virtual bool uninstall();

protected slots:
    void onConsoleStarted();
};

#endif