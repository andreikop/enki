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
#include "BeaverDebuggerSettings.h"
#include "BeaverDebugger.h"

#include <QVBoxLayout>
#include <QDialogButtonBox>
#include <QPushButton>
#include <QLabel>
#include <QFileDialog>
#include <QCompleter>
#include <QDirModel>
#include <QLineEdit>
#include <QToolButton>

'''!
    Creates settings widget
    \param plugin Pointer to BeaverDebugger plugin
    \param parent Parent widget of settings widget
'''
BeaverDebuggerSettings.BeaverDebuggerSettings(BeaverDebugger* plugin):
        QDialog(),
        mPlugin(plugin)
    label = QLabel(tr("Beaver executable\n"
                                  "It may be only executable file name, name with path\n"
#ifdef Q_OS_WIN
                                  "Example: C:\\Programm Files\\Beaver Debugger\\beaverdbg.exe"
#else:
                                  "Example: /usr/local/bin/beaverdbg"
#endif
                                 ))

    mPath = QLineEdit(mPlugin.beaverPath(), NULL)
    mPath.setCompleter(new QCompleter(new QDirModel(mPath)))
    open = QToolButton(self)
    open.setIcon(QIcon(":/icons/open.png")); # FIXME use system icon?

    hbox = QHBoxLayout()
    hbox.addWidget(mPath)
    hbox.addWidget(open)

    # apply button
    dbbApply = QDialogButtonBox( self )
    dbbApply.addButton( QDialogButtonBox.Apply )

    # global layout
    vbox = QVBoxLayout( self )
    vbox.addWidget( label )
    vbox.addLayout( hbox )
    vbox.addWidget( dbbApply )

    # connections
    connect( dbbApply.button( QDialogButtonBox.Apply ), SIGNAL( clicked() ), self, SLOT( applySettings() ) )
    open.clicked.connect(self.openPathDialog)


'''!
    Handler of clicking Apply button. Applying settings
'''
def applySettings(self):
    mPlugin.setBeaverPath(mPath.text())


'''!
    Handler of clicking button with folder. Opens dialog for choose Beaver Path
'''
def openPathDialog(self):
    QString newPath =
        QFileDialog.getOpenFileName (    self,
                                       tr("Beaver Debugger executable"),
                                       QFileInfo(mPath.text()).absolutePath()); # default dir path
    if not newPath.isNull():
        mPath.setText(newPath)


