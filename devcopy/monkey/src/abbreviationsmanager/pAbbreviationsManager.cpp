'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pAbbreviationsManager.cpp
** Date      : 2008-01-14T00:36:48
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
#include "pAbbreviationsManager.h"
#include "qscintillamanager/pEditor.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"
#include "shellmanager/MkSShellInterpreter.h"

#include <widgets/pQueuedMessageToolBar.h>
#include <qscilexer.h>

#include <QFile>
#include <QDir>
#include <QDebug>

pAbbreviationsManager.pAbbreviationsManager( QObject* parent )
    : QObject( parent )
    initialize()


def initialize(self):
    # register command
    help = MkSShellInterpreter.tr
    (
        "This command manage the abbreviations, usage:\n"
        "\tabbreviation add [macro] [description] [language] [code]\n"
        "\tabbreviation del [macro] [language]\n"
        "\tabbreviation show [macro] [language]\n"
        "\tabbreviation list [language]\n"
        "\tabbreviation clear"
    )
    
    MonkeyCore.interpreter().addCommandImplementation( "abbreviation", pAbbreviationsManager.commandInterpreter, help, self )


def commandInterpreter(self, command, arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    manager = static_cast<pAbbreviationsManager*>( data )
     allowedOperations = QStringList( "add" ) << "del" << "show" << "list" << "clear"
    
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
        if  arguments.count() != 5 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'add' operation take 4 arguments, %1 given." ).arg( arguments.count() -1 )

        
         macro = arguments.at( 1 )
         description = arguments.at( 2 )
         language = arguments.at( 3 )
         snippet = QString( arguments.at( 4 ) ).replace( "\\n", "\n" )
        
        manager.add( pAbbreviation( macro, description, language, snippet ) )

    
    if  operation == "del" :
        if  arguments.count() != 3 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'del' operation take 2 arguments, %1 given." ).arg( arguments.count() -1 )

        
         macro = arguments.at( 1 )
         language = arguments.at( 2 )
        
        manager.remove( macro, language )

    
    if  operation == "show" :
        if  arguments.count() != 3 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'show' operation take 2 arguments, %1 given." ).arg( arguments.count() -1 )

        
         macro = arguments.at( 1 )
         language = arguments.at( 2 )
         abbreviation = manager.abbreviation( macro, language )
        
        if  abbreviation.Macro.isEmpty() :
            return MkSShellInterpreter.tr( "Macro not found." )

        
        QStringList output
        
        output << QString( "%1:" ).arg( abbreviation.Description )
        output << abbreviation.Snippet
        
        return output.join( "\n" )

    
    if  operation == "list" :
        if  arguments.count() != 2 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'list' operation take 1 argument, %1 given." ).arg( arguments.count() -1 )

        
         language = arguments.at( 1 )
        QStringList output
        
        for abbreviation in manager.abbreviations():
            if  abbreviation.Language == language :
                output << abbreviation.Macro


        
        if  not output.isEmpty() :
            output.prepend( MkSShellInterpreter.tr( "Found macros:" ) )

        else:
            output << MkSShellInterpreter.tr( "No macros found." )

        
        return output.join( "\n" )

    
    if  operation == "clear" :
        if  arguments.count() != 1 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand

            
            return MkSShellInterpreter.tr( "'clear' operation take no arguments, %1 given." ).arg( arguments.count() -1 )

        
        manager.clear()

    
    return QString.null


def clear(self):
    mAbbreviations.clear()


def add(self, abbreviation ):
{    
    for abbr in mAbbreviations:
        if  abbr.Macro == abbreviation.Macro and abbr.Language == abbreviation.Language :
            mAbbreviations.removeOne( abbr )
            break


    
    mAbbreviations << abbreviation


def add(self, abbreviations ):
    for oAbbr in mAbbreviations:
        for nAbbr in abbreviations:
            if  oAbbr.Macro == nAbbr.Macro and oAbbr.Language == nAbbr.Language :
                mAbbreviations.removeOne( oAbbr )
                break



    
    mAbbreviations << abbreviations


def set(self, abbreviations ):
    mAbbreviations = abbreviations


def remove(self, abbreviation ):
    mAbbreviations.removeOne( abbreviation )


def remove(self, abbreviations ):
    for abbreviation in abbreviations:
        mAbbreviations.removeOne( abbreviation )



def remove(self, macro, language ):
    for abbreviation in mAbbreviations:
        if  abbreviation.Macro == macro and abbreviation.Language == language :
            mAbbreviations.removeOne( abbreviation )




 pAbbreviationList& pAbbreviationsManager.abbreviations()
    return mAbbreviations


def abbreviation(self, macro, language ):
    for abbreviation in mAbbreviations:
        if  abbreviation.Macro == macro and abbreviation.Language == language :
            return abbreviation


    
    return pAbbreviation()


def expandMacro(self, editor ):
    # need valid editor & lexer
    if  not editor or not editor.lexer() :
        return

    
    # get current cursor position
     pos = editor.cursorPosition()
    
    # get macro
    macro = editor.text( pos.y() ).left( pos.x() )
    
    # calculate the index
    i = macro.lastIndexOf( " " )
    if  i == -1 :
        i = macro.lastIndexOf( "\t" )

    
    # get clean macro
    macro = macro.mid( i ).trimmed()
    
    if  macro.isEmpty() :
        MonkeyCore.messageManager().appendMessage( tr( "Empty macro not " ) )
        return

    
    # get language
     lng = editor.lexer().language()
    
    # look for abbreviation and lexer to replace
    for abbreviation in mAbbreviations:
        # if template is found for language
        if  abbreviation.Language == lng and abbreviation.Macro == macro :
            # begin undo
            editor.beginUndoAction()
            
            # select macro in document
            editor.setSelection( pos.y(), i +1, pos.y(), i +1 +macro.length() )
            
            # remove macro from document
            editor.removeSelectedText()
            
            # for calculate final cursor position if it found a |
            QPoint op
            int k
            
            # get code lines
            lines = abbreviation.Snippet.split( "\n" )
            j = 0
            
            # iterating code lines
            for line in lines:
                # looking for cursor position
                k = line.indexOf( "|" )
                
                # calculate cursor position
                if  k != -1 :
                    op.ry() = pos.y() +j
                    op.rx() = k +i +1
                    line.replace( "|", "" )

                
                # if no last line
                if  j < lines.count() -1 :
                    # insert code line and an end of line
                    editor.insert( line +"\n" )
                    # set cursor on next line
                    editor.setCursorPosition( pos.y() +j +1, 0 )

                
                # insert codel ine
                else:
                    editor.insert( line )

                
                # process indentation for code line if line is not first one
                if  j > 0 :
                    editor.setIndentation( pos.y() +j, editor.indentation( pos.y() ) +editor.indentation( pos.y() +j ) )

                
                # increment j for calculate correct line
                j++

            
            # set cursor position is needed
            if  not op.isNull() :
                editor.setCursorPosition( op.y(), op.x() )

            
            # end undo
            editor.endUndoAction()
            
            # hide autocompletion combobox
            editor.cancelList()
            
            # finish
            return


    
    MonkeyCore.messageManager().appendMessage( tr( "No '%1' macro found for '%2' language" ).arg( macro ).arg( lng ) )


def generateScript(self):
    QMap<QString, abbreviations
    
    # group abbreviations by language
    for abbreviation in mAbbreviations:
        abbreviations[ abbreviation.Language ] << abbreviation

    
    # write content in utf8
     fn = MonkeyCore.settings().homePath( Settings.SP_SCRIPTS ).append( "/abbreviations.mks" )
    QFile file( fn )
    QStringList buffer
    
    if  not file.open( QIODevice.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Can't open file for generating abbreviations script: %1" ).arg( file.errorString() ) )
        return

    
    file.resize( 0 )
    
    buffer << "# Monkey Studio IDE Code Snippets"
    buffer << "# reset abbreviations"
    buffer << "abbreviation clear"
    buffer << "# introduce ones per language"
    buffer << "# abbreviation\tadd\tMacro\tDescription\tLanguage\tSnippet"
    
    for language in abbreviations.keys():
        buffer << QString( "# %1" ).arg( language )
        
        foreach (  pAbbreviation& abbreviation, abbreviations[ language ] )
            buffer << QString( "abbreviation add \"%1\" \"%2\" \"%3\" \"%4\"" )
                .arg( abbreviation.Macro )
                .arg( abbreviation.Description )
                .arg( abbreviation.Language )
                .arg( QString( abbreviation.Snippet ).replace( "\n", "\\n" ) )


    
    if  file.write( buffer.join( "\n" ).toUtf8() ) == -1 :
        MonkeyCore.messageManager().appendMessage( tr( "Can't write generated abbreviations script: %1" ).arg( file.errorString() ) )

    
    file.close()

