'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : MonkeyCore.cpp
** Date      : 2008-01-14T00:36:51
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "MonkeyCore.h"
#include "main.h"
#include "pMonkeyStudio.h"
#include "settingsmanager/Settings.h"
#include "pluginsmanager/PluginsManager.h"
#include "maininterface/UIMain.h"
#include "recentsmanager/pRecentsManager.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "workspace/pFileManager.h"
#include "workspace/pWorkspace.h"
#include "consolemanager/pConsoleManager.h"
#include "statusbar/StatusBar.h"
#include "shellmanager/MkSShellInterpreter.h"
#include "abbreviationsmanager/pAbbreviationsManager.h"
#include "maininterface/ui/UISettings.h"

#include <objects/pIconManager.h>
#include <widgets/pMultiToolBar.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <objects/TranslationManager.h>
#include <widgets/TranslationDialog.h>
#include <widgets/pActionsManager.h>
#include <widgets/pMenuBar.h>

#include <QSplashScreen>
#include <QPixmap>
#include <QString>
#include <QDate>
#include <QDebug>

def showMessage(self, s, m ):
    s.showMessage( m, Qt.AlignRight | Qt.AlignBottom, s.property( "isXMas" ).toBool() ? Qt.red : Qt.white )


QHash< QMetaObject*, MonkeyCore.mInstances

def init(self):
    # create splashscreen
    isXMas = False

    switch ( QDate.currentDate().month() )
    case 11:
    case 12:
    case 1:
        isXMas = True
        break


    QSplashScreen splash( pIconManager.pixmap( isXMas ? "splashscreen_christmas.png" : "splashscreen.png", ":/application" ) )
    splash.setProperty( "isXMas", isXMas )

    QFont ft( splash.font() )
#ifndef Q_OS_WIN
    ft.setPointSize( ft.pointSize() -2 )
#endif
    ft.setBold( True )
    splash.setFont( ft )
    splash.show()

    # restore application style
    showMessage( &splash, tr( "Initializing Style..." ) )
    qApp.setStyle( settings().value( "MainWindow/Style", "system" ).toString() )

    # set default settings if first time running
    if  settings().value( "FirstTimeRunning", True ).toBool() :
        settings().setDefaultSettings()


    # initialize locales
    showMessage( &splash, tr( "Initializing locales..." ) )
    translationManager = MonkeyCore.translationsManager()
    translationManager.setFakeCLocaleEnabled( True )
    translationManager.addTranslationsMask( "qt*.qm" )
    translationManager.addTranslationsMask( "assistant*.qm" )
    translationManager.addTranslationsMask( "designer*.qm" )
    translationManager.addTranslationsMask( "monkeystudio*.qm" )
    translationManager.addForbiddenTranslationsMask( "assistant_adp*.qm" )
    translationManager.setTranslationsPaths( settings().storagePaths( Settings.SP_TRANSLATIONS ) )

    # init translations
    showMessage( &splash, tr( "Initializing Translations..." ) )
    if  not settings().value( "Translations/Accepted" ).toBool() :
         locale = TranslationDialog.getLocale( translationManager )

        if  not locale.isEmpty() :
            settings().setValue( "Translations/Locale", locale )
            settings().setValue( "Translations/Accepted", True )
            translationManager.setCurrentLocale( locale )
            translationManager.reloadTranslations()


    translationManager.setCurrentLocale( settings().value( "Translations/Locale" ).toString() )
    translationManager.reloadTranslations()

    # init shortcuts editor
    showMessage( &splash, tr( "Initializing Actions Manager..." ) )
    MonkeyCore.actionsManager().setSettings( settings() )

    # init shell and commands
    showMessage( &splash, tr( "Initializing Shell..." ) )
    interpreter()

    # start console manager
    showMessage( &splash, tr( "Initializing Console..." ) )
    consoleManager()

    # init main window
    showMessage( &splash, tr( "Initializing Main Window..." ) )
    mainWindow().initGui()

    # init abbreviations manager
    showMessage( &splash, tr( "Initializing abbreviations manager..." ) )
    abbreviationsManager()

    # init file manager
    showMessage( &splash, tr( "Initializing file manager..." ) )
    fileManager()

    # load mks scripts
    showMessage( &splash, tr( "Executing scripts..." ) )
    interpreter().loadHomeScripts()

    # init pluginsmanager
    showMessage( &splash, tr( "Initializing Plugins..." ) )
    pluginsManager().loadsPlugins()

    # restore window state
    showMessage( &splash, tr( "Restoring Workspace..." ) )
    mainWindow().setSettings( settings() )

    # restore session
    showMessage( &splash, tr( "Restoring Session..." ) )
    if  pMonkeyStudio.restoreSessionOnStartup() :
        workspace().fileSessionRestore_triggered()


    # show main window
    mainWindow().menu_Docks_aboutToShow()
    mainWindow().show()
    mainWindow().finalyzeGuiInit()

    # ready
    showMessage( &splash, tr( "%1 v%2 (%3) Ready not " ).arg( PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_VERSION_STR ) )

    # finish splashscreen
    splash.finish( mainWindow() )

    # show settings dialog the first time user start program
    if  settings().value( "FirstTimeRunning", True ).toBool() :
        # execute settings dialog
        if  UISettings.instance().exec() :
            settings().setValue( "FirstTimeRunning", False )



    # prepare apis
    pMonkeyStudio.prepareAPIs()


def settings(self):
    if  not mInstances.contains( &Settings.staticMetaObject ) :
        mInstances[&Settings.staticMetaObject] = Settings( qApp )
    return qobject_cast<Settings*>( mInstances[&Settings.staticMetaObject] )


def pluginsManager(self):
    if  not mInstances.contains( &PluginsManager.staticMetaObject ) :
        mInstances[&PluginsManager.staticMetaObject] = PluginsManager( qApp )
    return qobject_cast<PluginsManager*>( mInstances[&PluginsManager.staticMetaObject] )


def mainWindow(self):
    if  not mInstances.contains( &UIMain.staticMetaObject ) :
        mInstances[&UIMain.staticMetaObject] = UIMain()
    return qobject_cast<UIMain*>( mInstances[&UIMain.staticMetaObject] )


def menuBar(self):
    return mainWindow().menuBar()


def actionsManager(self):
    return menuBar().actionsManager()


def recentsManager(self):
    if  not mInstances.contains( &pRecentsManager.staticMetaObject ) :
        mInstances[&pRecentsManager.staticMetaObject] = pRecentsManager( qApp )
    return qobject_cast<pRecentsManager*>( mInstances[&pRecentsManager.staticMetaObject] )


def projectsManager(self):
    if  not mInstances.contains( &XUPProjectManager.staticMetaObject ) :
        mInstances[&XUPProjectManager.staticMetaObject] = XUPProjectManager( mainWindow() )
    return qobject_cast<XUPProjectManager*>( mInstances[&XUPProjectManager.staticMetaObject] )


def fileManager(self):
    if  not mInstances.contains( &pFileManager.staticMetaObject ) :
        mInstances[&pFileManager.staticMetaObject] = pFileManager( qApp )
    return qobject_cast<pFileManager*>( mInstances[&pFileManager.staticMetaObject] )


def workspace(self):
    if  not mInstances.contains( &pWorkspace.staticMetaObject ) :
        mInstances[&pWorkspace.staticMetaObject] = pWorkspace( mainWindow() )
    return qobject_cast<pWorkspace*>( mInstances[&pWorkspace.staticMetaObject] )


def consoleManager(self):
    if  not mInstances.contains( &pConsoleManager.staticMetaObject ) :
        mInstances[&pConsoleManager.staticMetaObject] = pConsoleManager( qApp )
    return qobject_cast<pConsoleManager*>( mInstances[&pConsoleManager.staticMetaObject] )


def messageManager(self):
    if  not mInstances.contains( &pQueuedMessageToolBar.staticMetaObject ) :
        mInstances[&pQueuedMessageToolBar.staticMetaObject] = pQueuedMessageToolBar( mainWindow() )
    return qobject_cast<pQueuedMessageToolBar*>( mInstances[&pQueuedMessageToolBar.staticMetaObject] )


def statusBar(self):
    if  not mInstances.contains( &StatusBar.staticMetaObject ) :
        mInstances[&StatusBar.staticMetaObject] = StatusBar( mainWindow() )
    return qobject_cast<StatusBar*>( mInstances[&StatusBar.staticMetaObject] )


def interpreter(self):
    if  not mInstances.contains( &MkSShellInterpreter.staticMetaObject ) :
        mInstances[&MkSShellInterpreter.staticMetaObject] = MkSShellInterpreter.instance( qApp )
    return qobject_cast<MkSShellInterpreter*>( mInstances[&MkSShellInterpreter.staticMetaObject] )


def abbreviationsManager(self):
    if  not mInstances.contains( &pAbbreviationsManager.staticMetaObject ) :
        mInstances[&pAbbreviationsManager.staticMetaObject] = pAbbreviationsManager( qApp )
    return qobject_cast<pAbbreviationsManager*>( mInstances[&pAbbreviationsManager.staticMetaObject] )


def multiToolBar(self):
    if  not mInstances.contains( &pMultiToolBar.staticMetaObject ) :
        mInstances[&pMultiToolBar.staticMetaObject] = pMultiToolBar( mainWindow() )
    return qobject_cast<pMultiToolBar*>( mInstances[&pMultiToolBar.staticMetaObject] )


def translationsManager(self):
    if  not mInstances.contains( &TranslationManager.staticMetaObject ) :
        mInstances[&TranslationManager.staticMetaObject] = TranslationManager( QCoreApplication.instance() )
    return qobject_cast<TranslationManager*>( mInstances[&TranslationManager.staticMetaObject] )

