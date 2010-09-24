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
	\date 2008-01-14T00:27:48
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief a pStringListEditor that handle files name.
*/
#ifndef PPATHLISTEDITOR_H
#define PPATHLISTEDITOR_H

#include "objects/MonkeyExport.h"
#include "pFileListEditor.h"

/*!
	\brief a pPathListEditor that handle paths name.
	\details 
*/
class Q_MONKEY_EXPORT pPathListEditor : public pFileListEditor
{
	Q_OBJECT
	
public:
	pPathListEditor( QWidget* parent = 0, const QString& title = QString(), const QString& path = QString() );

protected slots:
	virtual void onAddItem();
	virtual void onEditItem();
};

#endif // PPATHLISTEDITOR_H
