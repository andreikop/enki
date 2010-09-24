'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Andrei Kopats aka hlamer <hlamer at tut by>, AZEVEDO aka PasNox <pasnox at gmail com>
** Project   : Monkey Studio Base Plugins
** FileName  : UIRegExpEditor.cpp
** Date      : 2008-01-14T00:40:08
** License   : GPL
** Comment   : Regular expression editor
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
'''!
    \file UIRegExpEditor.cpp
    \date 2008-01-14T00:40:08
    \author Andrei KOPATS, AZEVEDO
    \brief Regular expression editor
'''
#include "UIRegExpEditor.h"

#include <pMonkeyStudio.h>

#include <QTime>
#include <QMessageBox>
#include <QDebug>

'''!
    Initialise UI
    \param w Parent widget
'''
UIRegExpEditor.UIRegExpEditor( QWidget* w )
        : QMainWindow( w, Qt.Tool )
    # init widget
    setupUi( self )
    # add regexp syntax in combobox
    cbSyntax.addItem( "RegExp", QRegExp.RegExp )
    cbSyntax.addItem( "RegExp2", QRegExp.RegExp2 )
    cbSyntax.addItem( "Wildcard", QRegExp.Wildcard )
    cbSyntax.addItem( "FixedString", QRegExp.FixedString )
    # default configuration
    cbSyntax.setCurrentIndex( cbSyntax.findData( QRegExp.RegExp ) )
    cbCaseSensitive.setChecked( True )
    cbGreedy.setChecked( True )


'''!
    Handler or click on Find button

    Searchs for matching, it's possible and displaying it on UI
    If impossible to search (empty pattern for example) - explains on status
    bar, impossible
'''
def on_tbFind_clicked(self):
    # get pattern and text
     pattern = leRegExp.text().trimmed()
     text = pteTestBuffer.toPlainText().trimmed()
    # create the regexp
    QRegExp regexp( pattern, cbCaseSensitive.isChecked() ? Qt.CaseSensitive : Qt.CaseInsensitive, cbSyntax.itemData( cbSyntax.currentIndex() ).value<QRegExp.PatternSyntax>() )
    regexp.setMinimal( not cbGreedy.isChecked() )
    # check null pattern
    if  pattern.isEmpty() :
        statusBar().showMessage( tr( "Pattern can't be empty not " ) )
        return

    # check null text
    if  text.isEmpty() :
        statusBar().showMessage( tr( "Test text can't be empty not " ) )
        return

    # clear tree
    twResults.clear()
    # tracking time elapsed
    QTime elapsedTime
    elapsedTime.start()
    # searching
    count = 0
    pos = 0
    while ( ( pos = regexp.indexIn( text, pos ) ) != -1 )
        # parent item
        parent = QTreeWidgetItem( twResults )
        parent.setText( 0, regexp.cap( 0 ) )
        parent.setToolTip( 0,QString( "Main capture on iteration %1" ).arg( count ) )
        parent.setExpanded( True )
        # child item
        for ( i = 1; i < regexp.numCaptures(); i++ )
            child = QTreeWidgetItem( parent )
            child.setText( 0,regexp.cap( i ) )
            child.setToolTip( 0, QString( "Capture %1 on iteration %2" ).arg( i ).arg( count ) )
            child.setExpanded( True )

        # continue
        ++count
        pos += regexp.matchedLength()
        # check infinite loop
        if  count %1000 == 0 and QMessageBox.question( window(), tr( "Freeze ?not " ), tr( "The regular expression seem to recurse infinitely, you want to stop searching ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No ) == QMessageBox.Yes :
            break

    # tell about time
    statusBar().showMessage( tr( "Elapsed time: %1" ).arg( (float)elapsedTime.elapsed() /1000.0 ) )

