/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Compiler Plugins
** FileName  : GccParser.cpp
** Date      : 2008-01-14T00:53:26
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
/*!
	\file GccParser.cpp
	\date 2008-01-14T00:53:21
	\author Andrei Kopats
	\brief Implementation for GccParser plugin class
*/

#include "GccParser.h"
#include "Parser.h"

void GccParser::fillPluginInfos()
{
	mPluginInfos.Caption = tr( "GccParser" );
	mPluginInfos.Description = tr( "Plugin for parsing output of GNU Copiler Collection" );
	mPluginInfos.Author = "Kopats Andrei aka hlamer <hlamer@tut.by>";
	mPluginInfos.Type = BasePlugin::iBase;
	mPluginInfos.Name = PLUGIN_NAME;
	mPluginInfos.Version = "0.1.0";
#ifdef Q_CC_GNU
	mPluginInfos.FirstStartEnabled = true;
#else
	mPluginInfos.FirstStartEnabled = false;
#endif
}

/*!
	Install plugin to the system
	\return Status of process 
	\retval true Successfully enabled
	\retval false Some error ocurred
*/
bool GccParser::install()
{
	MonkeyCore::consoleManager()->addParser( new Parser( this ) );
	return true;
}

/*!
	Uninstall plugin to the system
	\return Status of process 
	\retval true Successfully enabled
	\retval false Some error ocurred
*/
bool GccParser::uninstall()
{
	MonkeyCore::consoleManager()->removeParser( PLUGIN_NAME );
	return true;
}

Q_EXPORT_PLUGIN2( BaseGccParser, GccParser )