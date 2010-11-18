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
#include "ToolsManager.h"
#include "ui/UIToolsEdit.h"
#include "ui/UIDesktopTools.h"

#include <coremanager/MonkeyCore.h>
#include <consolemanager/pConsoleManager.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <settingsmanager/Settings.h>
#include <shellmanager/MkSShellInterpreter.h>
#include <widgets/pMenuBar.h>

#include <QFileIconProvider>
#include <QDesktopServices>
#include <QImageReader>
#include <QUrl>
#include <QDebug>

QFileIconProvider* ToolsManager.mIconProvider = 0

ToolsManager.ToolsManager( QObject* p )
    : QObject( p )
    if  not mIconProvider :        mIconProvider = QFileIconProvider()

    
    initializeInterpreterCommands( True )


ToolsManager.~ToolsManager()
    initializeInterpreterCommands( False )
    delete mIconProvider
    mIconProvider = 0
    writeTools( mTools )


def scriptFilePath(self):
    return MonkeyCore.settings().homePath( Settings.SP_SCRIPTS ).append( "/tools.mks" )


def tools(self, type ):
    ToolsManager.Tools tools
    
    foreach (  ToolsManager.Tool& tool, mTools )        if ( ( tool.desktopEntry and type == ToolsManager.DesktopEntry ) 
            or ( not tool.desktopEntry and type == ToolsManager.UserEntry ) )            tools << tool


    
    return tools


def setCommand(self, caption, fileIcon, filePath, workingPath, desktopEntry, useConsoleManager ):
    for ( i = 0; i < mTools.count(); i++ )        tool = mTools[ i ]
        
        if  tool.caption == caption :            tool.fileIcon = fileIcon
            tool.filePath = filePath
            tool.workingPath = workingPath
            tool.desktopEntry = desktopEntry
            tool.useConsoleManager = useConsoleManager
            return


    
    mTools << ToolsManager.Tool( caption, fileIcon, filePath, workingPath, desktopEntry, useConsoleManager )


def unsetCommand(self, caption ):
    for ( i = 0; i < mTools.count(); i++ )        tool = mTools[ i ]
        
        if  tool.caption == caption :            mTools.removeAt( i )
            return




def clearCommand(self):
    mTools.clear()


def updateMenuCommand(self):
    updateMenuActions()


def icon(self, filePath, optionnalFilePath ):
     filePathValid = filePath.isEmpty() ? False : not QImageReader.imageFormat( filePath ).isEmpty()
     optionnalFilePathValid = optionnalFilePath.isEmpty() ? False : not QImageReader.imageFormat( optionnalFilePath ).isEmpty()
    QIcon icon
    
    if  filePathValid :        icon = QIcon( filePath )
#if QT_VERSION >= 0x040600

    else:
        icon = QIcon.fromTheme( filePath, icon )
#endif

    
    if  icon.isNull() :        if  optionnalFilePathValid :            icon = QIcon( optionnalFilePath )
#if QT_VERSION >= 0x040600

        else:
            icon = QIcon.fromTheme( optionnalFilePath, icon )
#endif


    
    if  icon.isNull() and not filePath.isEmpty() :        icon = mIconProvider.icon( filePath )

    
    if  icon.isNull() and not optionnalFilePath.isEmpty() :        icon = mIconProvider.icon( optionnalFilePath )

    
    return icon


def updateMenuActions(self):
    # get menu bar
    mb = MonkeyCore.menuBar()
    
    # clear action
    qDeleteAll( mb.menu( "mTools/mUserTools" ).actions() )
    qDeleteAll( mb.menu( "mTools/mDesktopTools" ).actions() )
    
    # initialize tools
    foreach (  ToolsManager.Tool& tool, mTools )        QAction* action
        
        if  tool.desktopEntry :            action = mb.action( QString( "mTools/mDesktopTools/%1" ).arg( tool.caption ), tool.caption, icon( tool.fileIcon, tool.filePath ), QString.null, tr( "Execute tool '%1': %2" ).arg( tool.caption ).arg( tool.filePath ) )

        else:
            action = mb.action( QString( "mTools/mUserTools/%1" ).arg( tool.caption ), tool.caption, icon( tool.fileIcon, tool.filePath ), QString.null, tr( "Execute tool '%1': %2" ).arg( tool.caption ).arg( tool.filePath ) )

        
        action.setData( QVariant.fromValue<ToolsManager.Tool>( tool ) )



def editTools_triggered(self):
    action = qobject_cast<QAction*>( sender() )
    dlg = 0
    
    switch ( ToolsManager.Type( action.data().toInt() ) )
        case ToolsManager.UserEntry:
            dlg = UIToolsEdit( self, QApplication.activeWindow() )
            break
        case ToolsManager.DesktopEntry:
            dlg = UIDesktopTools( self, QApplication.activeWindow() )
            break

    
    dlg.open()


def toolsMenu_triggered(self, action ):
    cm = MonkeyCore.consoleManager()
     tool = action.data().value<ToolsManager.Tool>()
     filePath = cm.processInternalVariables( tool.filePath )
     workingPath = cm.processInternalVariables( tool.workingPath )
    ok = False
    
    if  filePath.isEmpty() :        ok = False

    elif  tool.useConsoleManager :        pCommand cmd
        cmd.setText( tool.caption )
        commandAndArgs = filePath.split( ' ' )
        cmd.setCommand( commandAndArgs.takeFirst() )
        cmd.setArguments( commandAndArgs.join( " " ) )
        cmd.setWorkingDirectory( workingPath )
        cmd.setTryAllParsers( True )
        cm.addCommand( cmd )
        ok = True

    elif  workingPath.isEmpty() and QFile.exists( filePath ) :        ok = QDesktopServices.openUrl( QUrl.fromLocalFile( filePath ) )

    elif  workingPath.isEmpty() :        ok = QProcess.startDetached( filePath )

    else:
        process = QProcess( self )
        process.finished.connect(process.deleteLater)
        process.setWorkingDirectory( workingPath )
        process.start( filePath )
        ok = process.waitForStarted()

    
    if  not ok :        MonkeyCore.messageManager().appendMessage( tr( "Error trying to start tool: '%1'" ).arg( filePath ) )



def writeTools(self, tools ):
    # write content in utf8
     fn = scriptFilePath()
    QFile file( fn )
    QStringList buffer
    
    if  not file.open( QIODevice.WriteOnly ) :        qWarning() << QString( "Can't open file for generating tools script: %1" ).arg( file.errorString() ).toLocal8Bit().constData()
        return False

    
    file.resize( 0 )
    
    buffer << "# Monkey Studio IDE Tools"
    buffer << "# reset tools"
    buffer << "tools clear"
    buffer << "# Available commands:"
    buffer << "# tools set\tcaption\tfileIcon\tfilePath\tworkingPath\tdesktopEntry\tuseConsoleManager"
    buffer << "# tools unset\tcaption"
    buffer << "# tools clear"
    buffer << "# tools update-menu"
    buffer << "# tools list"
    buffer << "# introduce tools"
    
    for tool in tools:        buffer << QString( "# %1" ).arg( tool.caption )
        buffer << QString( "tools set \"%1\" \"%2\" \"%3\" \"%4\" \"%5\" \"%6\"" )
            .arg( tool.caption )
            .arg( tool.fileIcon )
            .arg( tool.filePath )
            .arg( tool.workingPath )
            .arg( tool.desktopEntry )
            .arg( tool.useConsoleManager )

    
    buffer << "# Update the menu"
    buffer << "tools update-menu"
    
    if  file.write( buffer.join( "\n" ).toUtf8() ) == -1 :        qWarning() << QString( "Can't write generated tools script: %1" ).arg( file.errorString() ).toLocal8Bit().constData()

    
    file.close()
    
    return True


def initializeInterpreterCommands(self, initialize ):
    if  initialize :        # register command
        help = MkSShellInterpreter.tr(
            "This command manage the tools, usage:\n"
            "\ttools set [caption] [fileIcon] [filePath] [workingPath] [desktopEntry:True|False] [useConsoleManager:True|False]\n"
            "\ttools unset [caption]\n"
            "\ttools clear\n"
            "\ttools update-menu\n"
            "\ttools list"
        )
        
        MonkeyCore.interpreter().addCommandImplementation( "tools", ToolsManager.commandInterpreter, help, self )

    else:
        MonkeyCore.interpreter().removeCommandImplementation( "tools" )



def commandInterpreter(self, command, _arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    manager = static_cast<ToolsManager*>( data )
    arguments = _arguments
     allowedOperations = QStringList( "set" ) << "unset" << "clear" << "update-menu" << "list"
    
    if  result :        *result = MkSShellInterpreter.NoError

    
    if  arguments.isEmpty() :        if  result :            *result = MkSShellInterpreter.InvalidCommand

        
        return MkSShellInterpreter.tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) )

    
     operation = arguments.takeFirst()
    
    if  not allowedOperations.contains( operation ) :        if  result :            *result = MkSShellInterpreter.InvalidCommand

        
        return MkSShellInterpreter.tr( "Unknown operation: '%1'." ).arg( operation )

    
    if  operation == "set" :        if  arguments.count() != 6 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'set' operation take 6 arguments, %1 given." ).arg( arguments.count() )

        
         caption = arguments.at( 0 )
         fileIcon = arguments.at( 1 )
         filePath = arguments.at( 2 )
         workingPath = arguments.at( 3 )
         desktopEntry = QVariant( arguments.at( 4 ) ).toBool()
         useConsoleManager = QVariant( arguments.at( 5 ) ).toBool()
        
        manager.setCommand( caption, fileIcon, filePath, workingPath, desktopEntry, useConsoleManager )

    
    if  operation == "unset" :        if  arguments.count() != 1 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'unset' operation take 1 arguments, %1 given." ).arg( arguments.count() )

        
         caption = arguments.at( 0 )
        
        manager.unsetCommand( caption )

    
    if  operation == "clear" :        if  arguments.count() != 0 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'clear' operation take no arguments, %1 given." ).arg( arguments.count() )

        
        manager.clearCommand()

    
    if  operation == "update-menu" :        if  arguments.count() != 0 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'update-menu' operation take no arguments, %1 given." ).arg( arguments.count() )

        
        manager.updateMenuCommand()

    
    if  operation == "list" :        if  arguments.count() != 0 :            if  result :                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'list' operation take no arguments, %1 given." ).arg( arguments.count() )

        
        QStringList output
        
        foreach (  ToolsManager.Tool& tool, manager.mTools )            output << QString( "%1: \"%2\" \"%3\" \"%4\" \"%5\" \"%6\"" )
                .arg( tool.caption )
                .arg( tool.fileIcon )
                .arg( tool.filePath )
                .arg( tool.workingPath )
                .arg( tool.desktopEntry )
                .arg( tool.useConsoleManager )

        
        if  not output.isEmpty() :            output.prepend( MkSShellInterpreter.tr( "Found tools:" ) )

        else:
            output << MkSShellInterpreter.tr( "No tools found." )

        
        return output.join( "\n" )

    
    return QString.null

