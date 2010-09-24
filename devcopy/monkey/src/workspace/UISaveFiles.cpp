'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UISaveFiles.cpp
** Date      : 2008-01-14T00:37:18
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
#include "UISaveFiles.h"
#include "pAbstractChild.h"

#include <QCloseEvent>
#include <QVBoxLayout>
#include <QLabel>
#include <QListWidget>
#include <QDialogButtonBox>
#include <QAbstractButton>
#include <QPushButton>
#include <QFileInfo>

UISaveFiles.UISaveFiles( QWidget* w, b )
        : QDialog( w )
    # set no child modified
    setProperty( "ChildsModified", False )
    # set undefined button state
    setProperty( "ClickedButton", UISaveFiles.bDiscardAll )
    # set window title
    setWindowTitle( tr( "Save File(s) ?" ) )
    # resize window
    resize( 400, 300 )

    # create dialog layout
    vl = QVBoxLayout( self )
    vl.setMargin( 5 )
    vl.setSpacing( 3 )

    # create label
    l = QLabel
    l.setText( tr( "Check the files you want to save :" ) )
    vl.addWidget( l )

    # create listwidget
    lwFiles = QListWidget
    vl.addWidget( lwFiles )

    # create buttons
    dbbButtons = QDialogButtonBox
    dbbButtons.setStandardButtons( QDialogButtonBox.Save | QDialogButtonBox.Discard )
    dbbButtons.button( QDialogButtonBox.Save ).setText( tr( "Save Selected" ) )
    dbbButtons.button( QDialogButtonBox.Discard ).setText( tr( "Discard All" ) )

    # if not forced, cancel button
    if  not b:
        dbbButtons.addButton( QDialogButtonBox.Cancel )
        dbbButtons.button( QDialogButtonBox.Cancel ).setText( tr( "Cancel Close" ) )


    # add button to dialog
    vl.addWidget( dbbButtons )

    # connections
    dbbButtons.clicked.connect(self.clicked)

    # set focus on discard button
    dbbButtons.button( QDialogButtonBox.Discard ).setFocus()


def addFile(self, c ):
    # create file item
    i = QListWidgetItem( c.fileName(), lwFiles )
    i.setToolTip( c.filePath() )
    i.setData( Qt.UserRole, QVariant.fromValue( c ) )
    i.setCheckState( Qt.Checked )

    # change dialog window modified if needed
    if  not property( "ChildsModified" ).toBool() :
        setProperty( "ChildsModified", True )


def clicked(self, ab ):
    # if button was save
    if  ab  == dbbButtons.button( QDialogButtonBox.Save ) :
        setProperty( "ClickedButton", UISaveFiles.bSaveSelected )
        for ( i = 0; i < lwFiles.count(); i++ )
            if  lwFiles.item( i ).checkState() != Qt.Unchecked :
                lwFiles.item( i ).data( Qt.UserRole ).value<pAbstractChild*>().saveFile()

    # else cancel changing child event
    elif  ab == dbbButtons.button( QDialogButtonBox.Cancel ) :
        setProperty( "ClickedButton", UISaveFiles.bCancelClose )

    # close dialog
    close()


def saveDocuments(self, w, l, b ):
    # create dialog
    UISaveFiles d( w, b )

    # add files
    for c in l:
    if  c.isModified() :
        d.addFile( c )

    # if at least one file is modified, is True, it if needed
    if  d.property( "ChildsModified" ).toBool() :
        d.exec()

    # return clicked button
    return static_cast<UISaveFiles.Buttons>( d.property( "ClickedButton" ).toInt() )


def saveDocument(self, w, c, b ):
    return saveDocuments( w, QList<pAbstractChild*>() << c, b )

