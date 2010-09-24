'''***************************************************************************
**
**         Created using Monkey Studio
** Authors   : Andrei KOPATS aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio Beaver integration
** FileName  : BeaverDebuggerSettings.cpp
** Date      : 2009-09-23T19:02:00
** License   : GPL
** Comment   : Settings widget of BeaverDebugger plugin
** Home Page : http:#www.monkeystudio.org
**
    Copyright (C) 2005 - 2008  Andrei KOPATS & The Monkey Studio Team

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
'''!
    \file BeaverDebuggerSettings.cpp
    \date 2009-09-23T19:02:00
    \author Andrei KOPATS
    \brief Settings widget of BeaverDebugger plugin
'''
#ifndef BEAVERDEBUGGERSETTINGS_H
#define BEAVERDEBUGGERSETTINGS_H

#include <QDialog>

class BeaverDebugger

class QLineEdit
'''!
    Settigs widget of BeaverDebugger plugin
'''
class BeaverDebuggerSettings : public QDialog
    Q_OBJECT

public:
    BeaverDebuggerSettings( BeaverDebugger* plugin)

protected:
    BeaverDebugger* mPlugin
    QLineEdit* mPath

protected slots:
    void applySettings()
    void openPathDialog()


#endif # BEAVERDEBUGGERSETTINGS_H
