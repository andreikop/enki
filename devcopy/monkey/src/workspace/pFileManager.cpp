'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pFileManager.cpp
** Date      : 2008-01-14T00:37:20
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
#include "pFileManager.h"
#include "pWorkspace.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "pAbstractChild.h"
#include "coremanager/MonkeyCore.h"
#include "pMonkeyStudio.h"
#include "settingsmanager/Settings.h"
#include "shellmanager/MkSShellInterpreter.h"

#include <widgets/pQueuedMessageToolBar.h>

pFileManager.pFileManager( QObject* o )
        : QObject( o )
    initializeInterpreterCommands()

    # files
    connect( MonkeyCore.workspace(), SIGNAL( documentOpened( pAbstractChild* ) ), self, SIGNAL( documentOpened( pAbstractChild* ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( documentModifiedChanged( pAbstractChild*, bool ) ), self, SIGNAL( documentModifiedChanged( pAbstractChild*, bool ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( documentChanged( pAbstractChild* ) ), self, SIGNAL( documentChanged( pAbstractChild* ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( documentAboutToClose( pAbstractChild* ) ), self, SIGNAL( documentAboutToClose( pAbstractChild* ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( documentClosed( pAbstractChild* ) ), self, SIGNAL( documentClosed( pAbstractChild* ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( documentReloaded( pAbstractChild* ) ), self, SIGNAL( documentReloaded( pAbstractChild* ) ) )
    connect( MonkeyCore.workspace(), SIGNAL( currentDocumentChanged( pAbstractChild* ) ), self, SIGNAL( currentDocumentChanged( pAbstractChild* ) ) )

    # projects
    connect( MonkeyCore.projectsManager(), SIGNAL( projectOpened( XUPProjectItem* ) ), self, SIGNAL( opened( XUPProjectItem* ) ) )
    connect( MonkeyCore.projectsManager(), SIGNAL( projectAboutToClose( XUPProjectItem* ) ), self, SIGNAL( aboutToClose( XUPProjectItem* ) ) )
    connect( MonkeyCore.projectsManager(), SIGNAL( currentProjectChanged( XUPProjectItem* ) ), self, SIGNAL( currentChanged( XUPProjectItem* ) ) )
    connect( MonkeyCore.projectsManager(), SIGNAL( currentProjectChanged( XUPProjectItem*, XUPProjectItem* ) ), self, SIGNAL( currentChanged( XUPProjectItem*, XUPProjectItem* ) ) )


def initializeInterpreterCommands(self):
    # register command
    help = MkSShellInterpreter.tr
                   (
                       "This command manage the associations, usage:\n"
                       "The suffixes are a comma separated list of suffixes (ie: \"*.txt, *.doc\")\n"
                       "\tassociation add [type] [suffixes]\n"
                       "\tassociation set [type] [suffixes]\n"
                       "\tassociation del [type] [suffixes]\n"
                       "\tassociation list [type] -- If type is missing, suffixes will be shown.\n"
                       "\tassociation clear [type] -- If type is missing, suffixes will be cleared."
                   )

    MonkeyCore.interpreter().addCommandImplementation( "association", pFileManager.commandInterpreter, help, self )


def commandInterpreter(self, command, arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    manager = static_cast<pFileManager*>( data )
     allowedOperations = QStringList( "add" ) << "set" << "del" << "list" << "clear"

    if  result :
        *result = MkSShellInterpreter.NoError


    if  arguments.isEmpty() :
        if  result :
            *result = MkSShellInterpreter.InvalidCommand


        return MkSShellInterpreter.tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) )


     operation = arguments.first()

    if  not allowedOperations.contains( operation ) :
        if  result :
            *result = MkSShellInterpreter.InvalidCommand


        return MkSShellInterpreter.tr( "Unknown operation: '%1'." ).arg( operation )


    if  operation == "add" :
        if  arguments.count() != 3 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'add' operation take 2 arguments, %1 given." ).arg( arguments.count() -1 )


         type = arguments.at( 1 )
         suffixes = arguments.at( 2 ).split( ",", QString.SkipEmptyParts )

        manager.addCommand( type, suffixes )


    if  operation == "set" :
        if  arguments.count() != 3 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'set' operation take 2 arguments, %1 given." ).arg( arguments.count() -1 )


         type = arguments.at( 1 )
         suffixes = arguments.at( 2 ).split( ",", QString.SkipEmptyParts )

        manager.setCommand( type, suffixes )


    if  operation == "del" :
        if  arguments.count() != 3 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'del' operation take 2 arguments, %1 given." ).arg( arguments.count() -1 )


         type = arguments.at( 1 )
         suffixes = arguments.at( 2 ).split( ",", QString.SkipEmptyParts )

        manager.removeCommand( type, suffixes )


    if  operation == "list" :
        if  arguments.count() > 2 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'list' operation take 0 or 1 argument, %1 given." ).arg( arguments.count() -1 )


         type = arguments.value( 1 )
        QStringList output

        if  type.isNull() :
            for ctype in manager.associations().keys():
                output << QString( "%1:" ).arg( ctype )
                output << QString( "\t%1" ).arg( manager.associations( ctype ).join( ", " ) )


        else:
            output << QString( "%1:" ).arg( type )
            output << QString( "\t%1" ).arg( manager.associations( type ).join( ", " ) )


        if  not output.isEmpty() :
            output.prepend( MkSShellInterpreter.tr( "Found associations:" ) )

        else:
            output << MkSShellInterpreter.tr( "No associations found." )


        return output.join( "\n" )


    if  operation == "clear" :
        if  arguments.size() > 2 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'clear' operation take 0 or 1 argument, %1 given." ).arg( arguments.count() -1 )


         type = arguments.value( 1 )

        manager.clearCommand( type )


    return QString.null


def clearCommand(self, type ):
    if  type.isNull() :
        mAssociations.clear()

    else:
        mAssociations.remove( type )



def addCommand(self, type, suffixes ):
    for suffix in suffixes:
         trimmedSuffix = suffix.trimmed()

        if  not mAssociations[ type ].contains( trimmedSuffix ) :
            mAssociations[ type ] << trimmedSuffix




def addCommand(self, type, suffix ):
    addCommand( type, QStringList( suffix ) )


def setCommand(self, type, suffixes ):
    clearCommand( type )
    addCommand( type, suffixes )


def setCommand(self, type, suffix ):
    setCommand( type, QStringList( suffix ) )


def removeCommand(self, type, suffixes ):
    result = associations( type )

    for suffix in suffixes:
         trimmedSuffix = suffix.trimmed()

        result.removeOne( trimmedSuffix )


    if  result.isEmpty() :
        clearCommand( type )

    else:
        mAssociations[ type ] = result



def removeCommand(self, type, suffix ):
    removeCommand( type, QStringList( suffix ) )


 QMap<QString, pFileManager.associations()
    return mAssociations


def associations(self, type ):
    return mAssociations.value( type )


def generateScript(self):
    # write content in utf8
     fn = MonkeyCore.settings().homePath( Settings.SP_SCRIPTS ).append( "/associations.mks" )
    QFile file( fn )
    QStringList buffer

    if  not file.open( QIODevice.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Can't open file for generating associations script: %1" ).arg( file.errorString() ) )
        return


    file.resize( 0 )

    buffer << "# Monkey Studio IDE Associations"
    buffer << "# reset associations"
    buffer << "association clear"
    buffer << "# introduce ones per language"
    buffer << "# association add\tlanguage/type\tSuffixes"
    buffer << "# association set\tlanguage/type\tSuffixes"

    for type in mAssociations.keys():
        buffer << QString( "# %1" ).arg( type )

        if  not mAssociations[ type ].isEmpty() :
            buffer << QString( "association set \"%1\" \"%2\"" )
            .arg( type )
            .arg( mAssociations[ type ].join( ", " ) )



    if  file.write( buffer.join( "\n" ).toUtf8() ) == -1 :
        MonkeyCore.messageManager().appendMessage( tr( "Can't write generated associations script: %1" ).arg( file.errorString() ) )


    file.close()


def openedDocument(self, fileName ):
    for document in MonkeyCore.workspace().documents():
        if  pMonkeyStudio.isSameFile( document.filePath(), fileName ) :
            return document



    return 0


def fileBuffer(self, fileName, codec, ok ):
    document = openedDocument( fileName )

    if  document :
        ok = True
        return document.fileBuffer()


    QString result
    ok = False
    QFile file( fileName )

    if  file.exists() :
        if  file.open( QIODevice.ReadOnly ) :
            c = QTextCodec.codecForName( codec.toUtf8() )
            result = c.toUnicode( file.readAll() )
            ok = True
            file.close()



    return result


def computeModifiedBuffers(self):
    QMap<QString, entries

    for document in MonkeyCore.workspace().documents():
        if  document.isModified() :
             content = document.fileBuffer()
            entries[ document.filePath() ] = content



    buffersChanged.emit( entries )


def currentProject(self):
    return MonkeyCore.projectsManager().currentProject()


def currentProjectFile(self):
    curProject = currentProject()
    return curProject ? curProject.fileName() : QString.null


def currentProjectPath(self):
    curProject = currentProject()
    return curProject ? curProject.path() : QString.null


def currentDocument(self):
    return MonkeyCore.workspace().currentDocument()


def currentDocumentFile(self):
    document = currentDocument()
    return document ? document.filePath() : QString.null


def currentDocumentPath(self):
    return QFileInfo( currentDocumentFile() ).path()


def currentItem(self):
    return MonkeyCore.projectsManager().currentItem()


def currentItemFile(self):
    item = currentItem()

    if  item and item.type() == XUPItem.File :
        fn = item.cacheValue( "content" )
        return item.project().filePath( fn )


    return QString.null


def currentItemPath(self):
    item = currentItem()

    if  item and item.type() == XUPItem.Path :
        fn = item.cacheValue( "content" )
        return item.project().filePath( fn )


    return QString.null


def openFile(self, fileName, codec ):
    return MonkeyCore.workspace().openFile( fileName, codec )


def closeFile(self, fileName ):
    MonkeyCore.workspace().closeFile( fileName )


def goToLine(self, fileName, pos, codec, selectionLength ):
    MonkeyCore.workspace().goToLine( fileName, pos, codec, selectionLength )


def openProject(self, fileName, codec ):
    MonkeyCore.projectsManager().openProject( fileName, codec )

