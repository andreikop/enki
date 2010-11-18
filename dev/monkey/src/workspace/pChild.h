/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pChild.h
** Date      : 2008-01-14T00:37:20
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
#ifndef PCHILD_H
#define PCHILD_H

#include <objects/MonkeyExport.h>

#include "pAbstractChild.h"

class pEditor;

class Q_MONKEY_EXPORT pChild : public pAbstractChild
{
	Q_OBJECT

public:
	pChild();
	virtual ~pChild();

	// return child language
	virtual QString language() const;
	
	virtual QString fileBuffer() const;

	// return child context
	virtual QString context() const;
	
	// the context initialization
	virtual void initializeContext( QToolBar* tb );
	
	// return cursor position if available
	virtual QPoint cursorPosition() const;

	// the current visible editor
	virtual pEditor* editor() const;

	// return the current file modified flag
	virtual bool isModified() const;

	// return the current file undo flag
	virtual bool isUndoAvailable() const;

	// undo
	virtual void undo();

	// return the current file redo flag
	virtual bool isRedoAvailable() const;

	// redo
	virtual void redo();

	// cut
	virtual void cut();

	// copy
	virtual void copy();

	// paste
	virtual void paste();

	// go to in the current child
	virtual void goTo();

	// go to position and select by selection length from position
	virtual void goTo( const QPoint& position, int selectionLength = -1 );

	// return the current file copy available
	virtual bool isCopyAvailable() const;

	// return the current file paste available
	virtual bool isPasteAvailable() const;

	// return is goto is available
	virtual bool isGoToAvailable() const;

	// return if print is available
	virtual bool isPrintAvailable() const;

	// ask to save file
	virtual void saveFile();
	
	// ask to backup the current file
	void backupFileAs( const QString& fileName );

	// ask to load file
	virtual bool openFile( const QString& fileName, const QString& codec );

	// ask to close file
	virtual void closeFile();
	
	// ask to reload the document
	virtual void reload();

	// ask to print this file
	virtual void printFile();

	// ask to quick print this file
	virtual void quickPrintFile();

protected:
	pEditor* mEditor;

protected slots:
	void cursorPositionChanged();

public slots:
	void invokeSearch();
};

#endif // PCHILD_H
