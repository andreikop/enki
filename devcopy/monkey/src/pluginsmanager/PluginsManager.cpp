'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : PluginsManager.cpp
** Date      : 2008-01-14T00:37:01
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
#include "PluginsManager.h"
#include "PluginsMenu.h"
#include "pMonkeyStudio.h"
#include "ui/UIPluginsSettings.h"
#include "coremanager/MonkeyCore.h"
#include "main.h"

#include <objects/pVersion.h>

#include <QPluginLoader>

#include <QDebug>

PluginsManager.PluginsManager( QObject* p )
        : QObject( p )
    mMenuHandler = PluginsMenu( self )
    mBuilder = 0
    mDebugger = 0
    mInterpreter = 0


def plugins(self):
    return mPlugins


def loadsPlugins(self):
    # loads static plugins
    for o in QPluginLoader.staticInstances():
    if  not addPlugin( o ) :
        qWarning("%s", tr( "Failed to load static plugin" ).toLocal8Bit().constData() )
    # load dynamic plugins
    QDir d
    for s in MonkeyCore.settings(:.storagePaths( Settings.SP_PLUGINS ) )
        d.setPath( QDir.isRelativePath( s ) ? qApp.applicationDirPath().append( "/%1" ).arg( s ) : s )
        # load all plugins
        foreach (  QFileInfo& f, pMonkeyStudio.getFiles( d ) )
            # don't proced no library file
            if  not QLibrary.isLibrary( f.absoluteFilePath() ) :
                continue
#ifdef Q_OS_MAC
            # don't proceed Qt plugins on mac
            if  f.absoluteFilePath().contains( "/qt/" ) :
                continue
#endif
            # load plugin
            QPluginLoader l( f.absoluteFilePath() )
            # try unload it and reload it in case of old one in memory
            if  not l.instance() :
                l.unload()
                l.load()

            # continue on no plugin
            if  not l.instance() :
                qWarning("%s", tr( "Failed to load plugin ( %1 ): Error: %2" ).arg( f.absoluteFilePath(), l.errorString() ).toLocal8Bit().constData() )
                continue

            # try to add plugin to plugins list, unload it
            elif  not addPlugin( l.instance() ) :
                l.unload()


    # installs user requested plugins
    enableUserPlugins()


def addPlugin(self, o ):
    # try to cast instance to BasePlugin
    bp = qobject_cast<BasePlugin*>( o )

    # if not return
    if  not bp :
        return False

    # generally it should be called from constructor, can't call virtual method
    bp.fillPluginInfos()

    # inforce application minimum requirement
     pVersion appVersion( PACKAGE_VERSION )
     pVersion pluginVersion( bp.infos().ApplicationVersionRequired )

    if  appVersion < pluginVersion :
        qWarning( "Uncompatible plugin %s: require version %s, version %s", bp.infos().Name.toLocal8Bit().constData(), pluginVersion.toString().toLocal8Bit().constData(), appVersion.toString().toLocal8Bit().constData() )
        return False


    # check dupplicates
    for p in mPlugins:
        if  p.infos().Name == bp.infos().Name :
            qWarning("%s", tr( "Skipping duplicate plugin: %1, type: %2" ).arg( p.infos().Name ).arg( p.infos().Type ).toLocal8Bit().constData() )
            return False



    # show plugin infos
    qWarning("%s", tr( "Found plugin: %1, type: %2" ).arg( bp.infos().Name ).arg( bp.infos().Type ).toLocal8Bit().constData() )

    # add it to plugins list
    mPlugins << bp

    mMenuHandler.addPlugin( bp )

    # return
    return True


def enableUserPlugins(self):
    for bp in mPlugins:
        # check first start state
        if  MonkeyCore.settings().value( "FirstTimeRunning", True ).toBool() :
            if  not bp.infos().FirstStartEnabled :
                MonkeyCore.settings().setValue( QString( "Plugins/%1" ).arg( bp.infos().Name ), False )



        # check in settings if we must install self plugin
        if  not MonkeyCore.settings().value( QString( "Plugins/%1" ).arg( bp.infos().Name ), True ).toBool() :
            qWarning("%s", tr( "User wantn't to intall plugin: %1" ).arg( bp.infos().Name ).toLocal8Bit().constData() )

        # if not enabled, it
        elif  not bp.isEnabled() :
            if  bp.setEnabled( True ) :
                qWarning("%s", tr( "Successfully enabled plugin: %1" ).arg( bp.infos().Name ).toLocal8Bit().constData() )

            else:
                qWarning("%s", tr( "Unsuccessfully enabled plugin: %1" ).arg( bp.infos().Name ).toLocal8Bit().constData() )


        else:
            qWarning("%s", tr( "Already enabled plugin: %1" ).arg( bp.infos().Name ).toLocal8Bit().constData() )




def documentForFileName(self, fileName ):
    foreach ( ChildPlugin* plugin, plugins<ChildPlugin*>( PluginsManager.stEnabled ) )
        document = plugin.createDocument( fileName )

        if  document :
            return document



    return 0


QMap<QString, PluginsManager.childSuffixes()
    QMap<QString, l
    foreach ( ChildPlugin* cp, const_cast<PluginsManager*>( self ).plugins<ChildPlugin*>( PluginsManager.stEnabled ) )
    for k in cp.suffixes().keys():
    l[k] << cp.suffixes().value( k )
    return l


def childFilters(self):
    QString f
    QMap<QString, l = childSuffixes()
    for k in l.keys():
    f += QString( "%1 (%2);;" ).arg( k ).arg( l.value( k ).join( " " ) )
    if  f.endsWith( ";;" ) :
        f.chop( 2 )
    return f


def setCurrentBuilder(self, b ):
    # if same cancel
    if  mBuilder == b :
        return

    # disabled all builder
    foreach ( BuilderPlugin* bp, plugins<BuilderPlugin*>( PluginsManager.stAll ) )
    bp.setEnabled( False )

    # enabled the one we choose
    mBuilder = b
    if  mBuilder :
        mBuilder.setEnabled( True )


def currentBuilder(self):
    return mBuilder


def setCurrentDebugger(self, d ):
    # if same cancel
    if  mDebugger == d :
        return

    # disabled all debugger
    foreach ( DebuggerPlugin* dp, plugins<DebuggerPlugin*>( PluginsManager.stAll ) )
    dp.setEnabled( False )

    # enabled the one we choose
    mDebugger = d
    if  mDebugger :
        mDebugger.setEnabled( True )


def currentDebugger(self):
    return mDebugger


def setCurrentInterpreter(self, i ):
    # if same cancel
    if  mInterpreter == i :
        return

    # disabled all debugger
    foreach ( InterpreterPlugin* ip, plugins<InterpreterPlugin*>( PluginsManager.stAll ) )
    ip.setEnabled( False )

    # enabled the one we choose
    mInterpreter = i
    if  mInterpreter :
        mInterpreter.setEnabled( True )


def currentInterpreter(self):
    return mInterpreter


def manageRequested(self):
    ( UIPluginsSettings() ).show()


def clearPlugins(self):
    for bp in mPlugins:
        qWarning( "Clearing plugin...%s", bp.infos().Name.toLocal8Bit().constData() )
        bp.setEnabled( False )

    qDeleteAll( mPlugins )
    mPlugins.clear()

