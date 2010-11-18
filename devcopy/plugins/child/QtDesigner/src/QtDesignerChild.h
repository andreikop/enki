'''***************************************************************************
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
***************************************************************************'''
#ifndef QTDESIGNERCHILD_H
#define QTDESIGNERCHILD_H

#include <workspace/pAbstractChild.h>

namespace SharedTools    class WidgetHost


class QToolBar
class QtDesignerManager
class QDesignerFormWindowInterface

class QtDesignerChild : public pAbstractChild
    Q_OBJECT

public:
    QtDesignerChild( QtDesignerManager* manager )

protected:
    QtDesignerManager* mDesignerManager
    SharedTools.WidgetHost* mHostWidget

    void showEvent( QShowEvent* event )
    void printFormHelper( QDesignerFormWindowInterface* form, quick )

protected slots:
    void formChanged()
    void formSelectionChanged()
    void formGeometryChanged()
    void formMainContainerChanged( QWidget* widget )

public:
    virtual QString fileBuffer()
    virtual QString context()
    virtual void initializeContext( QToolBar* tb )
    virtual QPoint cursorPosition()
    inline virtual pEditor* editor()  { return 0;
    virtual bool isModified()
    virtual bool isUndoAvailable()
    virtual bool isRedoAvailable()
    virtual bool isCopyAvailable()
    virtual bool isPasteAvailable()
    virtual bool isGoToAvailable()
    virtual bool isPrintAvailable()

public slots:
    virtual void undo()
    virtual void redo()
    virtual void cut()
    virtual void copy()
    virtual void paste()
    virtual void goTo()
    virtual void goTo(  QPoint& position, selectionLength = -1 )
    virtual void searchReplace()
    virtual bool isSearchReplaceAvailable()
    virtual void saveFile()
    virtual void backupFileAs(  QString& fileName )
    virtual bool openFile(  QString& fileName, codec )
    virtual void closeFile()
    virtual void reload()
    virtual void printFile()
    virtual void quickPrintFile()


#endif # QTDESIGNERCHILD_H
