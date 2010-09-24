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
#include "ClassBrowser.h"
#include "pDockClassBrowser.h"
#include "ClassBrowserSettings.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <workspace/pFileManager.h>
#include <qCtagsSenseBrowser.h>
#include <xupmanager/core/XUPProjectItem.h>
#include <pMonkeyStudio.h>
#include <qCtagsSense.h>
#include <widgets/pMultiToolBar.h>
#include <workspace/pAbstractChild.h>
#include <widgets/pActionsManager.h>
#include <widgets/pDockToolBar.h>

#include <QDesktopServices>
#include <QDebug>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Class Browser" )
    mPluginInfos.Description = tr( "Plugin for browsing classes members" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "0.5.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = QPixmap( ":/icons/class.png" )


def install(self):
    # create dock
    mDock = pDockClassBrowser( self )
    # create menu action for the dock
    pActionsManager.setDefaultShortcut( mDock.toggleViewAction(), QKeySequence( "F8" ) )
    # connections
    connect( MonkeyCore.fileManager(), SIGNAL( documentOpened( pAbstractChild* ) ), self, SLOT( documentOpened( pAbstractChild* ) ) )
    connect( MonkeyCore.fileManager(), SIGNAL( currentDocumentChanged( pAbstractChild* ) ), self, SLOT( currentDocumentChanged( pAbstractChild* ) ) )
    connect( MonkeyCore.fileManager(), SIGNAL( opened( XUPProjectItem* ) ), self, SLOT( opened( XUPProjectItem* ) ) )
    connect( MonkeyCore.fileManager(), SIGNAL( buffersChanged(  QMap<QString, QString>& ) ), self, SLOT( buffersChanged(  QMap<QString, QString>& ) ) )
    connect( mDock.browser(), SIGNAL( entryActivated(  qCtagsSenseEntry& ) ), self, SLOT( entryActivated(  qCtagsSenseEntry& ) ) )
    connect( mDock.browser(), SIGNAL( fileNameActivated(  QString& ) ), self, SLOT( fileNameActivated(  QString& ) ) )
    connect( self, SIGNAL( propertiesChanged(  qCtagsSenseProperties& ) ), mDock.browser(), SLOT( setProperties(  qCtagsSenseProperties& ) ) )
    connect( self, SIGNAL( integrationModeChanged( ClassBrowser.IntegrationMode ) ), MonkeyCore.multiToolBar(), SIGNAL( notifyChanges() ) )
    # update integration mode
    setIntegrationMode( integrationMode() )
    # update properties
    propertiesChanged.emit( properties() )

    return True


def uninstall(self):
    # disconnections
    disconnect( MonkeyCore.fileManager(), SIGNAL( documentOpened( pAbstractChild* ) ), self, SLOT( documentOpened( pAbstractChild* ) ) )
    disconnect( MonkeyCore.fileManager(), SIGNAL( currentDocumentChanged( pAbstractChild* ) ), self, SLOT( currentDocumentChanged( pAbstractChild* ) ) )
    disconnect( MonkeyCore.fileManager(), SIGNAL( opened( XUPProjectItem* ) ), self, SLOT( opened( XUPProjectItem* ) ) )
    disconnect( MonkeyCore.fileManager(), SIGNAL( buffersChanged(  QMap<QString, QString>& ) ), self, SLOT( buffersChanged(  QMap<QString, QString>& ) ) )
    disconnect( mDock.browser(), SIGNAL( entryActivated(  qCtagsSenseEntry& ) ), self, SLOT( entryActivated(  qCtagsSenseEntry& ) ) )
    disconnect( mDock.browser(), SIGNAL( fileNameActivated(  QString& ) ), self, SLOT( fileNameActivated(  QString& ) ) )
    disconnect( self, SIGNAL( propertiesChanged(  qCtagsSenseProperties& ) ), mDock.browser(), SLOT( setProperties(  qCtagsSenseProperties& ) ) )
    disconnect( self, SIGNAL( integrationModeChanged( ClassBrowser.IntegrationMode ) ), MonkeyCore.multiToolBar(), SIGNAL( notifyChanges() ) )
    # it will remove itself from dock toolbar when deleted
    delete mDock

    return True


def settingsWidget(self):
    return ClassBrowserSettings( self, qApp.activeWindow() )


def properties(self):
     suffixes = QStringList()
                                 << "*.gif" << "*.png" << "*.mng" << "*.jpg" << "*.jpeg" << "*.tiff" << "*.ico" << "*.icns"
                                 << "*.pri" << "*.pro" << "*.qrc" << "*.ui" << "*.ts" << "*.qm" << "*.qch" << "*.xup" << "*.mks"
                                 << "*.txt" << "*.iss" << "*.api" << "*.sip" << "*.ini" << "*.css" << "*.bak" << "*.old"
                                 << "*.db" << "*.so" << "*.a" << "*.desktop"  << "*.gpl"

    qCtagsSenseProperties properties

    properties.SystemPaths = settingsValue( "SystemPaths" ).toStringList()
    properties.FilteredSuffixes = settingsValue( "FilteredSuffixes", suffixes ).toStringList()
    properties.UsePhysicalDatabase = settingsValue( "UsePhysicalDatabase", False ).toBool()
    properties.DatabaseFileName = settingsValue( "DatabaseFileName", defaultDatabase() ).toString()

    return properties


def setProperties(self, properties ):
    if  self.properties() != properties :
        setSettingsValue( "SystemPaths", properties.SystemPaths )
        setSettingsValue( "FilteredSuffixes", properties.FilteredSuffixes )
        setSettingsValue( "UsePhysicalDatabase", properties.UsePhysicalDatabase )
        setSettingsValue( "DatabaseFileName", properties.DatabaseFileName )

        propertiesChanged.emit( properties )



def integrationMode(self):
    return (ClassBrowser.IntegrationMode)settingsValue( "IntegrationMode", ClassBrowser.imDock ).toInt()


def setIntegrationMode(self, mode ):
    if  integrationMode() == mode :
        #return


    if  mDock :
        switch ( mode )
        case ClassBrowser.imDock:
            MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) )
            MonkeyCore.multiToolBar().toolBar( "Coding" ).removeAction( mDock.browser().membersAction() )
            break
        case ClassBrowser.imCombo:
            MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).removeDock( mDock )
            mDock.hide()
            MonkeyCore.multiToolBar().toolBar( "Coding" ).addAction( mDock.browser().membersAction() )
            break
        case ClassBrowser.imBoth:
            MonkeyCore.mainWindow().dockToolBar( Qt.RightToolBarArea ).addDock( mDock, infos().Caption, QIcon( infos().Pixmap ) )
            MonkeyCore.multiToolBar().toolBar( "Coding" ).addAction( mDock.browser().membersAction() )
            break



    if  integrationMode() != mode :
        setSettingsValue( "IntegrationMode", mode )

        integrationModeChanged.emit( mode )



def defaultDatabase(self):
    return QDir.cleanPath( QString( "%1/MkS_qCtagsSense.sqlite3" ).arg( QDesktopServices.storageLocation( QDesktopServices.TempLocation ) ) )


def documentOpened(self, document ):
    if  not document.filePath().isEmpty() :
        mDock.browser().tagEntry( document.filePath() )


    mDock.browser().setCurrentFileName( document.filePath() )


def currentDocumentChanged(self, document ):
    if  document :
        mDock.browser().setCurrentFileName( document.filePath() )

    else:
        mDock.browser().setCurrentFileName( QString.null )



def opened(self, project ):
     files = project.topLevelProjectSourceFiles()
    mDock.browser().tagEntries( files )


def buffersChanged(self,   QMap<QString, entries ):
    mDock.browser().tagEntries( entries )


def entryActivated(self, entry ):
    MonkeyCore.fileManager().goToLine( entry.fileName, QPoint( 0, entry.lineNumber ), pMonkeyStudio.defaultCodec() )


def fileNameActivated(self, fileName ):
    MonkeyCore.fileManager().openFile( fileName, pMonkeyStudio.defaultCodec() )


Q_EXPORT_PLUGIN2( BaseClassBrowser, ClassBrowser )