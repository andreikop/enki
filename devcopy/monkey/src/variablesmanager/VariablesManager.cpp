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
#include "VariablesManager.h"
#include "main.h"
#include "workspace/pFileManager.h"
#include "coremanager/MonkeyCore.h"

#include <QStringList>
#include <QList>
#include <QRegExp>
#include <QDateTime>
#include <QDir>

'''!
    Class constructor
    \param o Parent object. Passing to QObject constructor
'''
VariablesManager.VariablesManager( QObject* o )
    : QObject( o )
{

'''!
    Get value of variable
    \param name Variable name
    \param locals Local dictionary of variables
    \return Value of variable. Empty string, variable is unknown
'''
def getVariable(self, name, locals ):
    result = QString.null

    if  name == "editor_version" :
    # monkeystudio_version
        result = PACKAGE_VERSION_STR

    elif  name == "editor_version_string" :
    # monkeystudio_version_string
        result = QString( "%1 v%2 (%3)" ).arg( PACKAGE_NAME ).arg( PACKAGE_VERSION ).arg( PACKAGE_VERSION_STR )

    elif  name == "date" :
    # current date
        result = QDateTime.currentDateTime().toString( Qt.ISODate )

    elif  name == "current_project_path" or name == "cpp" :
    # current project path
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentProjectPath() )

    elif  name == "current_project_file" or name == "cp" :
    # current proejct file
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentProjectFile() )

    elif  name == "current_child_path" or name == "cfp" :
    #
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentDocumentPath() )

    elif  name == "current_child_file" or name == "cf" :
    #
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentDocumentFile() )

    elif  name == "current_item_path" or name == "cip" :
    #
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentItemPath() )

    elif  name == "current_item_file" or name == "ci" :
    #
        result = QDir.toNativeSeparators( MonkeyCore.fileManager().currentItemFile() )


    if  not result.isEmpty() :
        return result

    elif  globals.contains( name ) :
        return globals[ name ]

    elif  locals.contains( name ) :
        return locals[ name ]


    return QString( "$%1$" ).arg( name ); # was QString.null if not found, it's not a variable to replacenot  ( ie: php script that contains $variables )


'''!
    Check, variable is set localy or globaly
    \param name Name of variable
    \param locals Local dictionary
    \retval True Variable is set
    \retval False Variable is not set
'''
bool VariablesManager.isSet (QString name, locals)
    if (    name == "editor_version" or
            name == "editor_version_string" or
            name == "date" )
        return True
    return (globals.contains(name) or locals.contains(name))


'''!
    Replace all variables in the text by it's values
    \param text Text for processing
    \param locals Local dictionary of variables
    return New string
'''
QString VariablesManager.replaceAllVariables (QString text, locals)
    p = 0
    QString s
    QRegExp rex( "(\\$(?:\\w|\\s|'|\\.)+\\$)" )
    # search and interpret values
    QList<QString> findedVariables
    while ( ( p = rex.indexIn( text, p ) ) != -1 )
        # got keyword
        s = rex.capturedTexts().value( 1 )
        findedVariables.append (s)
        p += rex.matchedLength()

    # replace occurences
    for s in findedVariables:
        fuckDollar = QString(s).remove(s.size()-1,1).remove(0,1)
        toup = False
        tolow = False
        if fuckDollar.endsWith (".upper"):
            toup = True
            fuckDollar.remove (".upper")

        elif fuckDollar.endsWith (".lower"):
            tolow = True
            fuckDollar.remove (".lower")

        replaceWith = getVariable(fuckDollar,locals)
        if toup:
            replaceWith = replaceWith.toUpper()
        elif tolow:
            replaceWith = replaceWith.toLower()
        text.replace( s, replaceWith)
        text.replace( "\\n", "\n")

    # return value
    return text

