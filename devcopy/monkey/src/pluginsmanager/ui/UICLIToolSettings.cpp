'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UICLIToolSettings.cpp
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
#include "UICLIToolSettings.h"
#include  "consolemanager/pConsoleManager.h"
#include "pMonkeyStudio.h"
#include "pluginsmanager/CLIToolPlugin.h"
#include "coremanager/MonkeyCore.h"

#include <QInputDialog>

using namespace pMonkeyStudio

UICLIToolSettings.UICLIToolSettings( BasePlugin* p, d, c, w )
    : QWidget( w ), mPlugin( p ), mUpdating( False )
    Q_ASSERT( mPlugin )
    setupUi( self )
    # set button icons
    dbbButtons.button( QDialogButtonBox.Help ).setIcon( QIcon( ":/help/icons/help/keyword.png" ) )
    dbbButtons.button( QDialogButtonBox.Reset ).setIcon( QIcon( ":/tools/icons/tools/update.png" ) )
    dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setIcon( QIcon( ":/file/icons/file/backup.png" ) )
    dbbButtons.button( QDialogButtonBox.Save ).setIcon( QIcon( ":/file/icons/file/save.png" ) )
    # delete widget when close
    setAttribute( Qt.WA_DeleteOnClose )
    # memorize defaults and user commands
    mDefaults = d
    mCommands = c
    if  mCommands.isEmpty() :
        mCommands = mDefaults
    mReset = mCommands
    # add parsers
    lwCommandParsers.addItems( MonkeyCore.consoleManager().parsersName() )
    # set uncheck state for parser items
    for ( i = 0; i < lwCommandParsers.count(); i++ )
        lwCommandParsers.item( i ).setCheckState( Qt.Unchecked )
    # load commands
    updateCommands()


def updateCommands(self):
    mUpdating = True
    lwCommands.clear()
    for c in mCommands:
        lwCommands.addItem( c.text() )
    mUpdating = False
    if  lwCommands.count() :
        lwCommands.setCurrentRow( 0 )


def restoreDefaults(self):
    mCommands = mDefaults
    updateCommands()


def reset(self):
    mCommands = mReset
    updateCommands()


def save(self):
    on_lwCommands_currentItemChanged( lwCommands.currentItem(), lwCommands.currentItem() )
    qobject_cast<CLIToolPlugin*>( mPlugin ).setUserCommands( mCommands )


def on_lwCommands_itemSelectionChanged(self):
{ lwCommands.setCurrentItem( lwCommands.selectedItems().value( 0 ) );

def on_lwCommands_currentItemChanged(self, cit, pit ):
    if  pit and not mUpdating :
        c = mCommands[ lwCommands.row( pit ) ]
        c.setText( leCommandText.text() )
        c.setCommand( leCommandCommand.text() )
        c.setArguments( leCommandArguments.text() )
        c.setWorkingDirectory( leCommandWorkingDirectory.text() )
        c.setSkipOnError( cbCommandSkipOnError.isChecked() )
        QStringList l
        for ( i = 0; i < lwCommandParsers.count(); i++ )
            it = lwCommandParsers.item( i )
            if  it.checkState() == Qt.Checked :
                l << it.text()

        c.setParsers( l )
        c.setTryAllParsers( cbCommandTryAll.isChecked() )
        pit.setText( c.text() )

    c = cit ? mCommands.value( lwCommands.row( cit ) ) : pCommand()
    leCommandText.setText( c.text() )
    leCommandCommand.setText( c.command() )
    leCommandArguments.setText( c.arguments() )
    leCommandWorkingDirectory.setText( c.workingDirectory() )
    cbCommandSkipOnError.setChecked( c.skipOnError() )
    for ( i = 0; i < lwCommandParsers.count(); i++ )
        cit = lwCommandParsers.item( i )
        cit.setCheckState( c.parsers().contains( cit.text() ) ? Qt.Checked : Qt.Unchecked )

    cbCommandTryAll.setChecked( c.tryAllParsers() )


def on_pbCommandAdd_clicked(self):
    pCommand c( tr( "New Command" ), "command", "arguments" )
    mCommands << c
    lwCommands.addItem( c.text() )
    lwCommands.setCurrentRow( lwCommands.count() -1 )


def on_pbCommandRemove_clicked(self):
    if  it = lwCommands.currentItem() :
        mUpdating = True
        i = lwCommands.row( it )
        delete it
        mCommands.removeAt( i )
        mUpdating = False



def on_pbCommandUp_clicked(self):
    if  it = lwCommands.currentItem() :
        i = lwCommands.row( it )
        if  i > 0 :
            lwCommands.insertItem( i -1, lwCommands.takeItem( i ) )
            mCommands.swap( i, i -1 )
            lwCommands.setCurrentItem( it )




def on_pbCommandDown_clicked(self):
    if  it = lwCommands.currentItem() :
        i = lwCommands.row( it )
        if  i < lwCommands.count() -1 :
            lwCommands.insertItem( i +1, lwCommands.takeItem( i ) )
            mCommands.swap( i, i +1 )
            lwCommands.setCurrentItem( it )




def on_tbCommandCommand_clicked(self):
    s = getOpenFileName( tr( "Select an executable" ), leCommandCommand.text() )
    if  not s.isNull() :
        leCommandCommand.setText( s )


def on_tbCommandWorkingDirectory_clicked(self):
    s = getExistingDirectory( tr( "Select a folder" ), leCommandWorkingDirectory.text() )
    if  not s.isNull() :
        leCommandWorkingDirectory.setText( s )


def on_dbbButtons_clicked(self, b ):
    if  dbbButtons.standardButton( b ) == QDialogButtonBox.Reset :
        reset()
    elif  dbbButtons.standardButton( b ) == QDialogButtonBox.RestoreDefaults :
        restoreDefaults()
    elif  dbbButtons.standardButton( b ) == QDialogButtonBox.Save :
        save()

