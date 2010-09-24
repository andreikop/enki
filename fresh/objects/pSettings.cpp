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
#include "pSettings.h"

#include <QApplication>
#include <QDir>
#include <QFile>
#include <QMainWindow>

static QString mProgramName;
static QString mProgramVersion;

/*!
	\details Construct a new pSettings
	\param parent The object parent
	\param name The settings name
	\param version The settings version.
*/
pSettings::pSettings( QObject* parent,  const QString& name, const QString& version )
	: QSettings( getIniFile( name, version ), QSettings::IniFormat, parent )
{}

/*!
	\details Initialize the default settings name and version
	\param name The settings name
	\param version The settings version
*/
void pSettings::setIniInformations( const QString& name, const QString& version )
{
	mProgramName = name;
	mProgramVersion = version;
}

/*!
	\details Return the default name
*/
QString pSettings::programName()
{ return mProgramName; }

/*!
	\details Return the default version
*/
QString pSettings::programVersion()
{ return mProgramVersion; }

/*!
	\details Return a filePath for storing the ini file according to it's parameters
	\param name The settings name
	\param version The settings version
	\return
*/
QString pSettings::getIniFile( const QString& name, const QString& version )
{
#ifdef Q_OS_MAC
	return QDir::convertSeparators( QString( "%1/../%2 %3.ini" ).arg( QApplication::applicationDirPath() ).arg( name ).arg( version ) );
#elif defined Q_OS_WIN
	return QDir::convertSeparators( QString( "%1/%2 %3.ini" ).arg( QApplication::applicationDirPath() ).arg( name ).arg( version ) );
#else
	return QDir::convertSeparators( QString( "%1/.%2/%3 %4.ini" ).arg( QDir::homePath() ).arg( mProgramName ).arg( name ).arg( version ) );
#endif
}

/*!
	\details Restore a main winow state
	\param window The main window to restore
*/
void pSettings::restoreState( QMainWindow* window )
{
	if ( !window )
		return;
	window->restoreGeometry( value( "MainWindow/Geometry" ).toByteArray() );
	window->restoreState( value( "MainWindow/State" ).toByteArray() );
	if ( value( "MainWindow/Geometry" ).toByteArray().isEmpty() )
		window->showMaximized();
}

/*!
	\details Save a main winow state
	\param window The main window to save
*/
void pSettings::saveState( QMainWindow* window )
{
	if ( !window )
		return;
	setValue( "MainWindow/Geometry", window->saveGeometry() );
	setValue( "MainWindow/State", window->saveState() );
}

/*!
	\details A virtual member that you can reimplement for creating a default settings member
*/
void pSettings::setDefaultSettings()
{}
