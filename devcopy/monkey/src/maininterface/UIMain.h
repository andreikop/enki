'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIMain.h
** Date      : 2008-01-14T00:36:57
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
#ifndef UIMAIN_H
#define UIMAIN_H

#include <objects/MonkeyExport.h>
#include <widgets/pMainWindow.h>

#include <QUrl>

class pStylesActionGroup

class Q_MONKEY_EXPORT UIMain : public pMainWindow
    Q_OBJECT
    friend class MonkeyCore

public:
    QMenu* createPopupMenu()
    bool updateMenuVisibility( QMenu* menu )

protected:
    pStylesActionGroup* agStyles

    UIMain( QWidget* = 0 )
    
    virtual void dragEnterEvent( QDragEnterEvent* event )
    virtual void dropEvent( QDropEvent* event )
    
    void initGui()
    void closeEvent( QCloseEvent* )
    void initMenuBar()
    void initToolBar()
    void initConnections()
    void finalyzeGuiInit()

public slots:
    void menu_Docks_aboutToShow()
    void menu_CustomAction_aboutToShow()
    void changeStyle(  QString& style )

signals:
    void aboutToClose()
    void urlsDropped(  QList<QUrl>& urls )


#endif # UIMAIN_H
