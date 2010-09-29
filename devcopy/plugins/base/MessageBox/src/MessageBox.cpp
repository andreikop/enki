'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : MessageBox.cpp
** Date      : 2008-01-14T00:39:59
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
'''!
    \file MessageBox.cpp
    \date 2008-01-14T00:40:08
    \author Andrei Kopats
    \brief implementation of main class of MessageBox plugin
'''
#include "MessageBox.h"
#include "ui/MessageBoxDocks.h"
#include "ui/UIMessageBoxSettings.h"

#include <coremanager/MonkeyCore.h>
#include <maininterface/UIMain.h>
#include <consolemanager/pConsoleManager.h>
#include <widgets/pDockToolBar.h>

#include <QIcon>
#include <QTabWidget>

def fillPluginInfos(self):
    mPluginInfos.Caption = tr( "Message Box" )
    mPluginInfos.Description = tr( "Plugin for catching internal command console" )
    mPluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>"
    mPluginInfos.Type = BasePlugin.iBase
    mPluginInfos.Name = PLUGIN_NAME
    mPluginInfos.Version = "1.0.0"
    mPluginInfos.FirstStartEnabled = True
    mPluginInfos.HaveSettingsWidget = True
    mPluginInfos.Pixmap = pIconManager.pixmap( "warning.png", ":/icons" )



'''!
    Install plugin
    
    If plugin is installed - it visible on main window and it's actions are in the main menu
    \return Status of process 
    \retval True Successfully enabled
    \retval False Some error ocurred
'''
def install(self):
    # create actions
    mb = MonkeyCore.menuBar()
    QAction* warning
    QAction* error

    mb.beginGroup( "mView" )
        warning = mb.action( "aShowNextWarning", tr( "Next Warning..." ), pIconManager.icon( "warning.png", ":/icons" ), tr( "Ctrl+Shift++" ), tr( "Show the next build step warning." ) )
        error = mb.action( "aShowNextError", tr( "Next Error..." ), pIconManager.icon( "error.png", ":/icons" ), tr( "Ctrl+Alt++" ), tr( "Show the next build step error." ) )
    mb.endGroup()
    
    # create docks
    mMessageBoxDocks = MessageBoxDocks( self )
    
    # add docks to main window
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( mMessageBoxDocks.mBuildStep, mMessageBoxDocks.mBuildStep.windowTitle(), mMessageBoxDocks.mBuildStep.windowIcon() )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( mMessageBoxDocks.mOutput, mMessageBoxDocks.mOutput.windowTitle(), mMessageBoxDocks.mOutput.windowIcon() )
    MonkeyCore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( mMessageBoxDocks.mCommand, mMessageBoxDocks.mCommand.windowTitle(), mMessageBoxDocks.mCommand.windowIcon() )
    
    # connections
    warning.triggered.connect(mMessageBoxDocks.showNextWarning)
    error.triggered.connect(mMessageBoxDocks.showNextError)
    MonkeyCore.consoleManager().started.connect(self.onConsoleStarted)
    
    return True


'''!
    Unnstall plugin
    
    If plugin is installed - it visible on main window and it's actions are in the main menu
    \return Status of process 
    \retval True Successfully enabled
    \retval False Some error ocurred
'''
def uninstall(self):
    # delete actions
    mb = MonkeyCore.menuBar()
    QAction* action

    mb.beginGroup( "mView" )
        action = mb.action( "aShowNextWarning" )
        disaction.triggered.connect(mMessageBoxDocks.showNextWarning)
        delete action

        action = mb.action( "aShowNextError" )
        disaction.triggered.connect(mMessageBoxDocks.showNextError)
        delete action
    mb.endGroup()
    
    # disconnections
    disMonkeyCore.consoleManager().started.connect(self.onConsoleStarted)
    
    # delete docks
    delete mMessageBoxDocks
    
    return True


'''!
    Get settings widget for configuring plugin
    \return Pointer to widget
'''
def settingsWidget(self):
{ return UIMessageBoxSettings( self );

def onConsoleStarted(self):
    if  settingsValue( "ActivateDock", True ).toBool() :
        dock = (UIMessageBoxSettings.Dock)settingsValue( "ActivatedDock", UIMessageBoxSettings.Output ).toInt()
        switch ( dock )
            case UIMessageBoxSettings.BuildStep:
                mMessageBoxDocks.mBuildStep.show()
                break
            case UIMessageBoxSettings.Output:
                mMessageBoxDocks.mOutput.show()
                break
            case UIMessageBoxSettings.Command:
                mMessageBoxDocks.mCommand.show()
                break




Q_EXPORT_PLUGIN2( BaseMessageBox, MessageBox )