'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pEditor.h
** Date      : 2008-01-14T00:37:06
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
#ifndef PEDITOR_H
#define PEDITOR_H

#include <objects/MonkeyExport.h>
#include <qsciscintilla.h>

class Q_MONKEY_EXPORT pEditor : public QsciScintilla
    Q_OBJECT

public:
    enum MarkerDefineType
        # bookmarks
        mdBookmark = 0,


    pEditor( QWidget* = 0 )

    virtual bool findFirst(  QString& expr, re, cs, wo, wrap, forward = True, line = -1, index = -1, show = True )
    virtual bool findNext()
    virtual void replace(  QString& replaceStr )

    bool lineNumbersMarginEnabled()
    int lineNumbersMarginWidth()
    bool lineNumbersMarginAutoWidth()
    bool copyAvailable()
    bool canPaste()
    QPoint cursorPosition()

    #return the text of the current line
    QString currentLineText()

    bool markerAtLine( int line, markerId )
    int markerFindPrevious( int line, markerId )
    int markerFindNext( int line, markerId )

    # Set for self indentation according with actual in the file
    void autoDetectIndent()

    # Set for self EOL mode according with actual in the file
    void autoDetectEol()

protected:
    struct SearchState
        SearchState() : inProgress(0)
        bool inProgress
        QString expr
        bool wrap
        bool forward
        int flags
        long startpos
        long endpos
        bool show
        QRegExp rx


    bool mCopyAvailable
    static bool mPasteAvailableInit
    static bool mPasteAvailable
    QPoint mCursorPosition
    pEditor.SearchState mSearchState

    virtual void keyPressEvent( QKeyEvent* )

    int simpleSearch()
    bool search()

protected slots:
    void linesChanged()
    void setCopyAvailable( bool )
    void cursorPositionChanged( int, int )
    void textChanged()
    void clipboardDataChanged()

public slots:
    void setLineNumbersMarginEnabled( bool )
    void setLineNumbersMarginWidth( int )
    void setLineNumbersMarginAutoWidth( bool )
    bool openFile(  QString& fileName, codec )
    bool saveFile(  QString& = QString() )
    bool saveBackup(  QString& )
    void closeFile()
    void print( bool = False )
    void quickPrint()
    void selectNone()
    void invokeGoToLine()
    void convertTabs()
    void makeBackup()

signals:
    void cursorPositionChanged(  QPoint& )
    void undoAvailable( bool )
    void redoAvailable( bool )
    void pasteAvailable( bool )


#endif # PEDITOR_H
