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
	\file pStringListEditor.h
	\date 2008-01-14T00:27:49
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A widget that handle QStringList edition.
*/
#ifndef PSTRINGLISTEDITOR_H
#define PSTRINGLISTEDITOR_H

#include "objects/MonkeyExport.h"

#include <QGroupBox>

class QVBoxLayout;
class QListWidget;

/*!
	\brief A widget that handle QStringList edition.
	\details 
*/
class Q_MONKEY_EXPORT pStringListEditor : public QGroupBox
{
	Q_OBJECT
	
public:
	pStringListEditor( QWidget* paret = 0, const QString& title = QString() );
	QVBoxLayout* verticalLayout() const;

	void setValues( const QStringList& values );
	QStringList values() const;

protected:
	QVBoxLayout* mLayout;
	QListWidget* mList;

protected slots:
	virtual void onEdited();
	virtual void onAddItem();
	virtual void onRemoveItem();
	virtual void onClearItem();
	virtual void onMoveUpItem();
	virtual void onMoveDownItem();
	virtual void onEditItem();

signals:
	void edited();
};

#endif // PSTRINGLISTEDITOR_H
