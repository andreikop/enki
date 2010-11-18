'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pChild.h
** Date      : 2008-01-14T00:37:20
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
#ifndef PCHILD_H
#define PCHILD_H

#include <objects/MonkeyExport.h>

#include "pAbstractChild.h"

class pEditor

class Q_MONKEY_EXPORT pChild : public pAbstractChild
    Q_OBJECT

public:
    pChild()
    virtual ~pChild()

    # return child language
    virtual QString language()
    
    virtual QString fileBuffer()

    # return child context
    virtual QString context()
    
    # the context initialization
    virtual void initializeContext( QToolBar* tb )
    
    # return cursor position if available
    virtual QPoint cursorPosition()

    # the current visible editor
    virtual pEditor* editor()

    # return the current file modified flag
    virtual bool isModified()

    # return the current file undo flag
    virtual bool isUndoAvailable()

    # undo
    virtual void undo()

    # return the current file redo flag
    virtual bool isRedoAvailable()

    # redo
    virtual void redo()

    # cut
    virtual void cut()

    # copy
    virtual void copy()

    # paste
    virtual void paste()

    # go to in the current child
    virtual void goTo()

    # go to position and select by selection length from position
    virtual void goTo(  QPoint& position, selectionLength = -1 )

    # return the current file copy available
    virtual bool isCopyAvailable()

    # return the current file paste available
    virtual bool isPasteAvailable()

    # return is goto is available
    virtual bool isGoToAvailable()

    # return if print is available
    virtual bool isPrintAvailable()

    # ask to save file
    virtual void saveFile()
    
    # ask to backup the current file
    void backupFileAs(  QString& fileName )

    # ask to load file
    virtual bool openFile(  QString& fileName, codec )

    # ask to close file
    virtual void closeFile()
    
    # ask to reload the document
    virtual void reload()

    # ask to print self file
    virtual void printFile()

    # ask to quick print self file
    virtual void quickPrintFile()

protected:
    pEditor* mEditor

protected slots:
    void cursorPositionChanged()

public slots:
    void invokeSearch()


#endif # PCHILD_H
