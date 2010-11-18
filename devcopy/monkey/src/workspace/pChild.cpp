'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pChild.cpp
** Date      : 2008-01-14T00:37:20
** License   : GPL
** Comment   : This header has been automatically generated, are the original author, co-author, to replace/append with your informations.
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
    along with self program; if not, the Free Software
    Foundation, Inc., St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "pChild.h"
#include "qscintillamanager/pEditor.h"
#include "coremanager/MonkeyCore.h"

#include <objects/pIconManager.h>
#include <qscilexer.h>

#include <QFileInfo>
#include <QTextStream>
#include <QTextCodec>
#include <QApplication>

pChild.pChild()
    : pAbstractChild()
    # create textedit
    mEditor = pEditor
    mEditor.setAttribute( Qt.WA_MacSmallSize )
    mEditor.setFrameStyle( QFrame.NoFrame | QFrame.Plain )

    setWidget( mEditor )
    setFocusProxy( mEditor )
    #setWindowIcon( pIconManager.icon( "text.png" ) )
    setWindowIcon( QIcon() )

    # connections
    mEditor.cursorPositionChanged.connect(self.cursorPositionChanged)
    mEditor.undoAvailable.connect(self.undoAvailableChanged)
    mEditor.redoAvailable.connect(self.redoAvailableChanged)
    mEditor.copyAvailable.connect(self.copyAvailableChanged)
    mEditor.pasteAvailable.connect(self.pasteAvailableChanged)
    mEditor.modificationChanged.connect(self.setWindowModified)
    mEditor.modificationChanged.connect(self.modifiedChanged)
    mEditor.textChanged.connect(self.contentChanged)


pChild.~pChild()


def cursorPositionChanged(self):
    pAbstractChild.emit.cursorPositionChanged( cursorPosition() )


def language(self):
    # return the editor language
    if  mEditor.lexer() :
        return mEditor.lexer().language()


    # return nothing
    return QString()


def fileBuffer(self):
    return mEditor.text()


def context(self):
    return QLatin1String( "Coding" )


def initializeContext(self, tb ):
    Q_UNUSED( tb )


def cursorPosition(self):
    return mEditor.cursorPosition() +QPoint( 0, 1 )


def editor(self):
    return mEditor


def isModified(self):
    return mEditor.isModified()


def isUndoAvailable(self):
    return mEditor.isUndoAvailable()


void pChild.invokeSearch () 
    '''MonkeyCore.searchWidget().showSearchFile ();'''


def undo(self):
    mEditor.undo()


def isRedoAvailable(self):
    return mEditor.isRedoAvailable()


def redo(self):
    mEditor.redo()


def cut(self):
    mEditor.cut()


def copy(self):
    mEditor.copy()


def paste(self):
    mEditor.paste()


def goTo(self):
    mEditor.invokeGoToLine()


def goTo(self, pos, selectionLength ):
     column = pos.x()
     line = pos.y()
    
    mEditor.setCursorPosition( line, column )
    mEditor.setSelection( line, column, line, column +selectionLength )
    mEditor.ensureLineVisible( line )
    mEditor.setFocus()


def isCopyAvailable(self):
    return mEditor.copyAvailable()


def isPasteAvailable(self):
    return mEditor.canPaste()


def isGoToAvailable(self):
    return True


def isPrintAvailable(self):
    return True


def saveFile(self):
    mEditor.saveFile( filePath() )


def backupFileAs(self, s ):
    mEditor.saveBackup( s )


def openFile(self, fileName, codec ):
    # if already open file, cancel
    '''if  not filePath().isEmpty() :
        return False
    }'''
    
    # set filename of the owned document
    setFilePath( fileName )

    # open file
     locked = blockSignals( True )
     opened = mEditor.openFile( fileName, codec )
    blockSignals( locked )
    
    if  not opened :
        setFilePath( QString.null )
        return False

    
    mCodec = QTextCodec.codecForName( codec.toUtf8() )

    fileOpened.emit()
    return True


def closeFile(self):
    mEditor.closeFile()
    setFilePath( QString.null )

    fileClosed.emit()


def reload(self):
    openFile( mEditor.property( "fileName" ).toString(), mEditor.property( "codec" ).toString() )
    
    fileReloaded.emit()


def printFile(self):
    mEditor.print()


def quickPrintFile(self):
    # print file
    mEditor.quickPrint()

