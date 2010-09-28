/****************************************************************************
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
****************************************************************************/
#ifndef QTDESIGNERCHILD_H
#define QTDESIGNERCHILD_H

#include <workspace/pAbstractChild.h>

namespace SharedTools {
    class WidgetHost;
};

class QToolBar;
class QtDesignerManager;
class QDesignerFormWindowInterface;

class QtDesignerChild : public pAbstractChild
{
    Q_OBJECT

public:
    QtDesignerChild( QtDesignerManager* manager );

protected:
    QtDesignerManager* mDesignerManager;
    SharedTools::WidgetHost* mHostWidget;

    void showEvent( QShowEvent* event );
    void printFormHelper( QDesignerFormWindowInterface* form, bool quick );

protected slots:
    void formChanged();
    void formSelectionChanged();
    void formGeometryChanged();
    void formMainContainerChanged( QWidget* widget );

public:
    virtual QString fileBuffer() const;
    virtual QString context() const;
    virtual void initializeContext( QToolBar* tb );
    virtual QPoint cursorPosition() const;
    inline virtual pEditor* editor() const { return 0; }
    virtual bool isModified() const;
    virtual bool isUndoAvailable() const;
    virtual bool isRedoAvailable() const;
    virtual bool isCopyAvailable() const;
    virtual bool isPasteAvailable() const;
    virtual bool isGoToAvailable() const;
    virtual bool isPrintAvailable() const;

public slots:
    virtual void undo();
    virtual void redo();
    virtual void cut();
    virtual void copy();
    virtual void paste();
    virtual void goTo();
    virtual void goTo( const QPoint& position, int selectionLength = -1 );
    virtual void searchReplace();
    virtual bool isSearchReplaceAvailable() const;
    virtual void saveFile();
    virtual void backupFileAs( const QString& fileName );
    virtual bool openFile( const QString& fileName, const QString& codec );
    virtual void closeFile();
    virtual void reload();
    virtual void printFile();
    virtual void quickPrintFile();
};

#endif // QTDESIGNERCHILD_H
