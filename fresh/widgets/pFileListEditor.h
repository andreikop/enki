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
	\file pFileListEditor.h
	\date 2008-01-14T00:27:44
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief a pStringListEditor that handle files name.
*/
#ifndef PFILELISTEDITOR_H
#define PFILELISTEDITOR_H

#include "objects/MonkeyExport.h"
#include "pStringListEditor.h"

/*!
	\brief a pStringListEditor that handle files name.
	\details 
*/
class Q_MONKEY_EXPORT pFileListEditor : public pStringListEditor
{
	Q_OBJECT
	
public:
	pFileListEditor( QWidget* parent = 0, const QString& title = QString(), const QString& path = QString(), const QString& filter = QString() );
	void setPath( const QString& path );

protected slots:
	virtual void onAddItem();
	virtual void onEditItem();

protected:
	QString mPath;
	QString mFilter;
};

#endif // PFILELISTEDITOR_H
