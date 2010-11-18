/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pAbstractChild.h
** Date      : 2008-01-14T00:37:19
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
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
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
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

class pEditor;

class Q_MONKEY_EXPORT pAbstractChild : public QMdiSubWindow
{
	Q_OBJECT
	Q_ENUMS( DocumentMode LayoutMode )

public:
	enum DocumentMode { mNone = 0, mNa, mInsert, mOverwrite, mReadOnly } mDocument;
	enum LayoutMode { lNone = 0, lNormal, lVertical, lHorizontal } mLayout;

	// constructor
	pAbstractChild( QWidget* parent = 0 )
		: QMdiSubWindow( parent )
	{
		mCodec = 0;
		setAttribute( Qt::WA_DeleteOnClose );
		mDocument = mNone;
		mLayout = lNone;
		
		// clear Close shortcut that conflict with menu one on some platform
		QMenu* menu = systemMenu();
		const QKeySequence closeSequence( QKeySequence::Close );
		
		foreach ( QAction* action, menu->actions() )
		{
			if ( action->shortcut() == closeSequence )
			{
				action->setShortcut( QKeySequence() );
			}
		}
	}
	
	// return defaultsize for child
	virtual QSize sizeHint() const
	{ return QSize( 640, 480 ); }

	// return child document mode
	virtual pAbstractChild::DocumentMode documentMode() const
	{ return mDocument; }

	// return the child layout mode
	virtual pAbstractChild::LayoutMode layoutMode() const
	{ return mLayout; }

	// return child language
	virtual QString language() const
	{ return QString::null; }
	
	// set the file path of the document
	void setFilePath( const QString& filePath )
	{
		if ( filePath.isEmpty() )
		{
			setWindowFilePath( QString::null );
			setWindowTitle( QString::null );
		}
		else
		{
			setWindowFilePath( filePath );
			setWindowTitle( fileName().append( "[*]" ) );
		}
	}
	
	// return the document file path
	QString filePath() const
	{ return windowFilePath(); }
	
	// return the filename of the document
	QString fileName() const
	{
		const QString wfp = windowFilePath();
		return wfp.isEmpty() ? QString::null : QFileInfo( wfp ).fileName();
	}
	
	// return the absolute path of the document
	QString path() const
	{
		const QString wfp = windowFilePath();
		return wfp.isEmpty() ? QString::null : QFileInfo( wfp ).absolutePath();
	}
	
	// return the current buffer of filename
	virtual QString fileBuffer() const
	{ return QString::null; }
	
	// return the child context
	virtual QString context() const = 0;
	// the context initialization
	virtual void initializeContext( QToolBar* tb ) = 0;
	// return cursor position if available
	virtual QPoint cursorPosition() const = 0;
	// the current visible editor
	virtual pEditor* editor() const = 0;
	// return the current file modified flag
	virtual bool isModified() const = 0;
	// return the current file undo flag
	virtual bool isUndoAvailable() const = 0;
	// return the current file redo flag
	virtual bool isRedoAvailable() const = 0;
	// return the current file copy available
	virtual bool isCopyAvailable() const = 0;
	// return the current file paste available
	virtual bool isPasteAvailable() const = 0;
	// return is goto is available
	virtual bool isGoToAvailable() const = 0;
	// return if print is available
	virtual bool isPrintAvailable() const = 0;

public slots:
	// set the child document mode
	virtual void setDocumentMode( pAbstractChild::DocumentMode m )
	{
		if ( mDocument == m )
			return;
		mDocument = m;
		emit documentModeChanged( mDocument );
	}

	// set the child layout mode
	virtual void setLayoutMode( pAbstractChild::LayoutMode m )
	{
		if ( mLayout == m )
			return;
		mLayout = m;
		emit layoutModeChanged( mLayout );
	}
	
	virtual QString textCodec() const
	{ return mCodec ? mCodec->name() : pMonkeyStudio::defaultCodec(); }
	
	virtual QTextCodec* codec() const
	{ return mCodec ? mCodec : QTextCodec::codecForName( pMonkeyStudio::defaultCodec().toLocal8Bit().constData() ); }
	
	// undo
	virtual void undo() = 0;
	// redo
	virtual void redo() = 0;
	// cut
	virtual void cut() = 0;
	// copy
	virtual void copy() = 0;
	// paste
	virtual void paste() = 0;
	// go to in the current child
	virtual void goTo() = 0;
	// go to position and select by selection length from position
	virtual void goTo( const QPoint& position, int selectionLength = -1 ) = 0;
	// search in the file
	virtual void invokeSearch() {};
	// ask to save file
	virtual void saveFile() = 0;
	// ask to backup current file
	virtual void backupFileAs( const QString& fileName ) = 0;
	// ask to load file
	virtual bool openFile( const QString& fileName, const QString& codec ) = 0;
	// ask to close file
	virtual void closeFile() = 0;
	// ask to reload the current file
	virtual void reload() = 0;
	// ask to print this file
	virtual void printFile() = 0;
	// ask to quick print this file
	virtual void quickPrintFile() = 0;

protected:
	// the codec the document was open with
	QTextCodec* mCodec;

signals:
	// emit when a file is opened
	void fileOpened(); // ok
	// emit when a file is closed
	void fileClosed(); // ok
	// emit when a file is reloaded
	void fileReloaded();
	// emit when the content changed
	void contentChanged();
	// emit when the child layout mode has changed
	void layoutModeChanged( pAbstractChild::LayoutMode );
	// emit when the child document mode has changed
	void documentModeChanged( pAbstractChild::DocumentMode );
	// emit when cursor position changed
	void cursorPositionChanged( const QPoint& ); // ok
	// emit when a file is modified
	void modifiedChanged( bool ); // ok
	// emit when undo has changed
	void undoAvailableChanged( bool ); // ok
	// emit when undo has changed
	void redoAvailableChanged( bool ); // ok
	// emit when a file paste available change
	void pasteAvailableChanged( bool ); // ok
	// emit when a file copy available change
	void copyAvailableChanged( bool ); // ok
	// emit when search/replace is available
	//void searchReplaceAvailableChanged( bool );
	// emit when goto is available
	//void goToAvailableChanged( bool );
	// emit when requesting search in editor
	//void requestSearchReplace();
	// emit when request go to line
	//void requestGoTo();
	// emit when a child require to update workspace
	//void updateWorkspaceRequested();

};

Q_DECLARE_METATYPE( pAbstractChild* )

#endif // PABSTRACTCHILD_H
