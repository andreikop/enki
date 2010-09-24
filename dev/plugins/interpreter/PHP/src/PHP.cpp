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
#include "PHP.h"

#include <QTabWidget>

PHP::PHP ()
{
	// install parsers
	foreach ( QString s, availableParsers() )
	{
		MonkeyCore::consoleManager()->addParser( getParser( s ) );
	}
}

void PHP::fillPluginInfos()
{
	mPluginInfos.Caption = tr( "PHP" );
	mPluginInfos.Description = tr( "This plugin provide PHP interpreter and php parser." );
	mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>";
	mPluginInfos.Type = BasePlugin::iInterpreter;
	mPluginInfos.Name = PLUGIN_NAME;
	mPluginInfos.Version = "0.1.0";
	mPluginInfos.FirstStartEnabled = true;
	mPluginInfos.HaveSettingsWidget = true;
	mPluginInfos.Pixmap = pIconManager::pixmap( "php.png", ":/icons" );
}

PHP::~PHP()
{//TODO move to uninstall
	// uninstall parsers
	foreach ( QString s, availableParsers() )
	{
		MonkeyCore::consoleManager()->removeParser( s );
	}
}

bool PHP::install()
{
	return true;
}

bool PHP::uninstall()
{
	return true;
}

QWidget* PHP::settingsWidget()
{
	QTabWidget* tw = new QTabWidget;
	tw->setAttribute( Qt::WA_DeleteOnClose );
	tw->addTab( interpreterSettingsWidget(), tr( "Interpret Command" ) );
	tw->addTab( cliToolSettingsWidget(), tr( "User Commands" ) );
	return tw;
}

pCommandList PHP::defaultCommands() const
{
	return pCommandList();
}

QStringList PHP::availableParsers() const
{
	return QStringList();
}

pCommand PHP::defaultInterpretCommand() const
{
	const QString mPHP = "php";
	return pCommand( "Interpret", mPHP, QString::null, false, availableParsers(), "$cpp$" );
}

Q_EXPORT_PLUGIN2( InterpreterPHP, PHP )
