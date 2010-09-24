'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pAbstractChild.h
** Date      : 2008-01-14T00:37:19
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
#ifndef PABSTRACTCHILD_H
#define PABSTRACTCHILD_H

#include <QMdiSubWindow>
#include <QFileInfo>
#include <QTextCodec>
#include <QShortcut>
#include <QMenu>
#include <QDebug>

#include <objects/MonkeyExport.h>

#include "pMonkeyStudio.h"

class pEditor

class Q_MONKEY_EXPORT pAbstractChild : public QMdiSubWindow
    Q_OBJECT
    Q_ENUMS( DocumentMode LayoutMode )

public:
    enum DocumentMode { mNone = 0, mNa, mInsert, mOverwrite, mReadOnly } mDocument
    enum LayoutMode { lNone = 0, lNormal, lVertical, lHorizontal } mLayout

    # constructor
    pAbstractChild( parent = 0 )
            : QMdiSubWindow( parent )
        mCodec = 0
        setAttribute( Qt.WA_DeleteOnClose )
        mDocument = mNone
        mLayout = lNone

        # clear Close shortcut that conflict with menu one on some platform
        menu = systemMenu()
         QKeySequence closeSequence( QKeySequence.Close )

        for action in menu.actions():
            if  action.shortcut() == closeSequence :
                action.setShortcut( QKeySequence() )




    # return defaultsize for child
    virtual QSize sizeHint()
        return QSize( 640, 480 )


    # return child document mode
    virtual pAbstractChild.DocumentMode documentMode()
        return mDocument


    # return the child layout mode
    virtual pAbstractChild.LayoutMode layoutMode()
        return mLayout


    # return child language
    virtual QString language()
        return QString.null


    # set the file path of the document
    void setFilePath(  QString& filePath )
        if  filePath.isEmpty() :
            setWindowFilePath( QString.null )
            setWindowTitle( QString.null )

        else:
            setWindowFilePath( filePath )
            setWindowTitle( fileName().append( "[*]" ) )



    # return the document file path
    QString filePath()
        return windowFilePath()


    # return the filename of the document
    QString fileName()
         wfp = windowFilePath()
        return wfp.isEmpty() ? QString.null : QFileInfo( wfp ).fileName()


    # return the absolute path of the document
    QString path()
         wfp = windowFilePath()
        return wfp.isEmpty() ? QString.null : QFileInfo( wfp ).absolutePath()


    # return the current buffer of filename
    virtual QString fileBuffer()
        return QString.null


    # return the child context
    virtual QString context()  = 0
    # the context initialization
    virtual void initializeContext( QToolBar* tb ) = 0
    # return cursor position if available
    virtual QPoint cursorPosition()  = 0
    # the current visible editor
    virtual pEditor* editor()  = 0
    # return the current file modified flag
    virtual bool isModified()  = 0
    # return the current file undo flag
    virtual bool isUndoAvailable()  = 0
    # return the current file redo flag
    virtual bool isRedoAvailable()  = 0
    # return the current file copy available
    virtual bool isCopyAvailable()  = 0
    # return the current file paste available
    virtual bool isPasteAvailable()  = 0
    # return is goto is available
    virtual bool isGoToAvailable()  = 0
    # return if print is available
    virtual bool isPrintAvailable()  = 0

public slots:
    # set the child document mode
    virtual void setDocumentMode( pAbstractChild.DocumentMode m )
        if  mDocument == m :
            return
        mDocument = m
        documentModeChanged.emit( mDocument )


    # set the child layout mode
    virtual void setLayoutMode( pAbstractChild.LayoutMode m )
        if  mLayout == m :
            return
        mLayout = m
        layoutModeChanged.emit( mLayout )


    virtual QString textCodec()
        return mCodec ? mCodec.name() : pMonkeyStudio.defaultCodec()


    virtual QTextCodec* codec()
        return mCodec ? mCodec : QTextCodec.codecForName( pMonkeyStudio.defaultCodec().toLocal8Bit().constData() )


    # undo
    virtual void undo() = 0
    # redo
    virtual void redo() = 0
    # cut
    virtual void cut() = 0
    # copy
    virtual void copy() = 0
    # paste
    virtual void paste() = 0
    # go to in the current child
    virtual void goTo() = 0
    # go to position and select by selection length from position
    virtual void goTo(  QPoint& position, selectionLength = -1 ) = 0
    # search in the file
    virtual void invokeSearch()    # ask to save file
    virtual void saveFile() = 0
    # ask to backup current file
    virtual void backupFileAs(  QString& fileName ) = 0
    # ask to load file
    virtual bool openFile(  QString& fileName, codec ) = 0
    # ask to close file
    virtual void closeFile() = 0
    # ask to reload the current file
    virtual void reload() = 0
    # ask to print self file
    virtual void printFile() = 0
    # ask to quick print self file
    virtual void quickPrintFile() = 0

protected:
    # the codec the document was open with
    QTextCodec* mCodec

signals:
    # when.emit a file is opened
    void fileOpened(); # ok
    # when.emit a file is closed
    void fileClosed(); # ok
    # when.emit a file is reloaded
    void fileReloaded()
    # when.emit the content changed
    void contentChanged()
    # when.emit the child layout mode has changed
    void layoutModeChanged( pAbstractChild.LayoutMode )
    # when.emit the child document mode has changed
    void documentModeChanged( pAbstractChild.DocumentMode )
    # when.emit cursor position changed
    void cursorPositionChanged(  QPoint& ); # ok
    # when.emit a file is modified
    void modifiedChanged( bool ); # ok
    # when.emit undo has changed
    void undoAvailableChanged( bool ); # ok
    # when.emit undo has changed
    void redoAvailableChanged( bool ); # ok
    # when.emit a file paste available change
    void pasteAvailableChanged( bool ); # ok
    # when.emit a file copy available change
    void copyAvailableChanged( bool ); # ok
    # when.emit search/replace is available
    #void searchReplaceAvailableChanged( bool )
    # when.emit goto is available
    #void goToAvailableChanged( bool )
    # when.emit requesting search in editor
    #void requestSearchReplace()
    # when.emit request go to line
    #void requestGoTo()
    # when.emit a child require to update workspace
    #void updateWorkspaceRequested()



Q_DECLARE_METATYPE( pAbstractChild* )

#endif # PABSTRACTCHILD_H
