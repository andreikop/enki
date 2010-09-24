/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors   : Andrei Kopats aka hlamer <hlamer at tut by>, Filipe AZEVEDO aka PasNox <pasnox at gmail com>
** Project   : Monkey Studio Base Plugins
** FileName  : UIRegExpEditor.h
** Date      : 2008-01-14T00:40:08
** License   : GPL
** Comment   : Regular expression editor
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
/*!
	\file UIRegExpEditor.h
	\date 2008-01-14T00:40:08
	\author Andrei KOPATS, Filipe AZEVEDO
	\brief Regular expression editor
*/
#ifndef UIREGEXPEDITOR_H
#define UIREGEXPEDITOR_H

#include "ui_UIRegExpEditor.h"

/*!
	Regular expression editor
	
	Tool for quick creation of regular expressions.
	Allows you apply pattern for some text and see matches for pattern
*/
class UIRegExpEditor : public QMainWindow, public Ui::UIRegExpEditor
{
	Q_OBJECT

public:
	UIRegExpEditor( QWidget* parent = 0 );

protected slots:
	void on_tbFind_clicked();
};

Q_DECLARE_METATYPE( QRegExp::PatternSyntax )

#endif // UIREGEXPEDITOR_H
