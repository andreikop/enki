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
	\file pSettings.h
	\date 2008-01-14T00:27:38
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief A class that handle ini files
*/
#ifndef PSETTINGS_H
#define PSETTINGS_H

#include "MonkeyExport.h"

#include <QSettings>

#ifndef _PACKAGE_NAME
/*!
	\details Default used variable for application name
*/
#define _PACKAGE_NAME "My Application"
#endif

#ifndef _PACKAGE_VERSION_STR
/*!
	\details Default used variable for application version
*/
#define _PACKAGE_VERSION_STR "1.0.0"
#endif

class QMainWindow;

/*!
	\brief A class that handle ini files
	\details This class is used for storing/retreiving datas using ini files
*/
class Q_MONKEY_EXPORT pSettings : public QSettings
{
	Q_OBJECT

public:
	pSettings( QObject* parent = 0, const QString& name = _PACKAGE_NAME, const QString& version = _PACKAGE_VERSION_STR );
	static void setIniInformations( const QString& name = _PACKAGE_NAME, const QString& version = _PACKAGE_VERSION_STR );
	static QString programName();
	static QString programVersion();
	static QString getIniFile( const QString& name, const QString& version );

	virtual void restoreState( QMainWindow* window );
	virtual void saveState( QMainWindow* );
	virtual void setDefaultSettings();
};

#endif // PSETTINGS_H
