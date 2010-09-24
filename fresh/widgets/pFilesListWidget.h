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
/*!
	\file pFilesListWidget.h
	\date 2008-01-14T00:27:45
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A QListWidget dock for pExtendedWorkspace
*/
#ifndef PFILESLISTWIDGET_H
#define PFILESLISTWIDGET_H

#include "objects/MonkeyExport.h"
#include "pDockWidget.h"

#include <QUrl>
#include <QIcon>

class pExtendedWorkspace;
class QComboBox;
class QListWidget;
class QDragEnterEvent;
class QDropEvent;

/*!
	\brief A QListWidget dock for pExtendedWorkspace
	\details The list is showing all workspace document windowTitle,
	\details you can activated a document by clicking its corresponding item in the list.
*/
class Q_MONKEY_EXPORT pFilesListWidget : public pDockWidget
{
	Q_OBJECT
	friend class FilesComboAction;
	
public:
	pFilesListWidget( const QString& title, pExtendedWorkspace* workspace );
	
	QAction* filesComboAction() const;

public slots:
	void setItemToolTip( int id, const QString& toolTip );

protected:
	QAction* aFilesCombo;
	QListWidget* mList;
	pExtendedWorkspace* mWorkspace;
	QIcon mModifiedIcon;
	QIcon mNonModifiedIcon;

	bool eventFilter( QObject* object, QEvent* event );

protected slots:
	void modifiedChanged( int id, bool modified );
	void docTitleChanged( int id, const QString& title );
	void documentInserted( int id, const QString& title, const QIcon& icon );
	void documentAboutToClose( int id );
	void setCurrentRow( int id );
};

#endif // PFILESLISTWIDGET_H
