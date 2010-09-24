'''***************************************************************************
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
***************************************************************************'''
'''!
    \file main.cpp
    \date 2008-01-14T00:37:22
    \author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
    \brief The main file of Monkey Studio IDE application
'''
#include <QApplication>
#include <QMessageBox>

#include "main.h"
#include "coremanager/MonkeyCore.h"
#include "pluginsmanager/PluginsManager.h"
#include "settingsmanager/Settings.h"
#include "commandlinemanager/CommandLineManager.h"

##include "properties/Properties.h"

def main(self, argc, argv ):
    # check qt version
    QT_REQUIRE_VERSION( argc, argv, "4.5.0" )
    # create application
    QApplication a( argc, argv )
    a.setApplicationName( PACKAGE_NAME )
    a.setOrganizationName( PACKAGE_NAME )
    a.setOrganizationDomain( PACKAGE_DOMAIN )
    QObject.connect( &a, SIGNAL( lastWindowClosed() ), &a, SLOT( quit() ) )

    # init pSettings
    pSettings.setIniInformations()

    # parse command line arguments
    CommandLineManager clm
    clm.parse()

    '''Properties p
    p.writeToFile( "properties.xml" );'''

     arguments = clm.arguments().keys()

    if  arguments.contains( "-v" ) or arguments.contains( "--version" ) :
        clm.showVersion()


    if  arguments.contains( "-h" ) or arguments.contains( "--help" ) :
        clm.showHelp()


    if  arguments.contains( "-v" ) or arguments.contains( "--version" ) or arguments.contains( "-h" ) or arguments.contains( "--help" ) :
        return 0


    # init monkey studio core
    MonkeyCore.init()
    # handle command line arguments
    clm.process()
    # execute application
     result = a.exec()
    # some cleanup
    MonkeyCore.pluginsManager().clearPlugins()
    delete MonkeyCore.settings()
    # exit code
    return result

