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
    \file pTemplatesManager.cpp
    \date 2008-01-14T00:37:13
    \author Andrei KOPATS, AZEVEDO
    \brief Implementation of pTemplatesManager class
'''

#include "pTemplatesManager.h"
#include "pMonkeyStudio.h"
#include "workspace/pFileManager.h"
#include "xupmanager/core/XUPItem.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "coremanager/MonkeyCore.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "settingsmanager/Settings.h"

#include <QTextCodec>
#include <QMessageBox>

using namespace pMonkeyStudio

'''!
    Class constructor
    \param o Parent object. Passing to QObject constructor
'''
pTemplatesManager.pTemplatesManager( QObject* o )
    : QObject( o )
{

'''!
    Read template from file
    \param s Path of template config file (.ini)
    \return Inmemory representation of template
'''
def getTemplate(self, s ):
    # open ini file
    QSettings set( s, QSettings.IniFormat )
    
    # fill template infos
    pTemplate t
    t.Name = QFileInfo( s ).dir().dirName()
    t.Language = set.value( "Language", tr( "Other" ) ).toString()
    t.Type = set.value( "Type", tr( "Wrong template type" ) ).toString()
    t.Description = set.value( "Description", tr( "No desctiption" ) ).toString()
    t.Icon = set.value( "Icon" ).toString()
    t.Script = set.value( "Script" ).toString()
    t.DirPath = QFileInfo( s ).absolutePath().append( "/" )
    t.Files = set.value( "Files" ).toStringList()
    t.FilesToOpen = set.value( "FilesToOpen" ).toStringList()
    t.ProjectsToOpen = set.value( "ProjectsToOpen" ).toStringList()
    t.FilesToAdd = set.value( "FilesToAdd" ).toStringList()
    t.Variables = VarList()
    
    # set template vars
    foreach( QString v, set.value( "Variables" ).toStringList() )
        t.Variables[v] = set.value( v +"Values" ).toStringList()
    
    # return template
    return t


'''!
    Read all availible templates
    \return List of templates, in all configured path
'''
def getTemplates(self):
    TemplateList l
    for p in MonkeyCore.settings(:.storagePaths( Settings.SP_TEMPLATES ) )
        foreach ( QFileInfo f, getFiles( QDir( unTokenizeHome( QDir.isRelativePath( p ) ? qApp.applicationDirPath().append( "/%1" ).arg( p ) : p ) ), QStringList( "template.ini" ), True ) )
            l << getTemplate( f.absoluteFilePath() )
    return l


'''!
    Create files from already configured template
    \param scope The project scope where to add files. Else NULL
    \param op The scope operator to use
    \param temp Template to realise
    \param dictionnary Dictionary of variables for template
    \return Result of creation
    \retval True All files is created successfully
    \retval False Some error ocurred
'''
def realiseTemplate(self, scope, temp, codec, dictionnary ):
    # get destination
    dest = dictionnary["Destination"]
    
    # check destination
    if  dest.isEmpty() :
        QMessageBox.warning( 0, tr( "Error..." ), tr( "Destination not set." ) )
        return False

    
    # check destination exists
    QDir destdir( dest )
    if  not destdir.exists() :
        if  not destdir.mkpath( dest ) :
            QMessageBox.warning( 0, tr( "Error..." ), tr( "Can't create destination '%1'" ).arg( dest ) )
            return False


    
    # append final slashe
    if  not dest.endsWith( "/" ) :
        dest.append( '/' )
    
    # replace values in files/projects to open
    QStringList fo, po
    for ( i = 0; i < temp.FilesToOpen.count(); i++ )
        fo << VariablesManager.instance().replaceAllVariables( temp.FilesToOpen.at( i ), dictionnary )
    for ( i = 0; i < temp.ProjectsToOpen.count(); i++ )
        po << VariablesManager.instance().replaceAllVariables( temp.ProjectsToOpen.at( i ), dictionnary )
    
    # get files
    QHash<QString, files
    for f in temp.Files:
        # check if sources and destination are differents
        QString sf, df
        sf = f
        df = f
        if  f.contains( '|' ) :
            sf = f.section( '|', 0, 0 )
            df = f.section( '|', 1, 1 )

        
        # process variables
        s = VariablesManager.instance().replaceAllVariables( df, dictionnary )
        
        # check value validity
        if  s.isEmpty() :
            QMessageBox.warning( 0, tr( "Error..." ), tr( "Empty filename detected for file %1" ).arg( sf ) )
            return False

        
        # append file to list
        files[sf] = s

    
    # create files
    for f in files.keys():
        # get source file
        k = QFile.exists( QString( "%1%2" ).arg( temp.DirPath, f ) ) ? f : VariablesManager.instance().replaceAllVariables( f, dictionnary )
        
        # get file name
        s = QString( "%1%2" ).arg( dest, files[f] )
        
        # check file destination exists
        QDir fd( QFileInfo( s ).path() )
        if  not fd.exists() :
            if  not fd.mkpath( fd.path() ) :
                QMessageBox.warning( 0, tr( "Error..." ), tr( "Can't create destination '%1'" ).arg( fd.path() ) )
                return False


        
        # copy file
        if  not QFile.copy( QString( "%1%2" ).arg( temp.DirPath, k ), s ) :
            QMessageBox.warning( 0, tr( "Error..." ), tr( "Can't copy '%1%2' to '%3'" ).arg( temp.DirPath, k, s ) )
            return False

        
        # open file
        QFile file( s )
        if  not file.open( QIODevice.ReadWrite | QIODevice.Text ) :
            QMessageBox.warning( 0, tr( "Error..." ), tr ( "Can't edit file %1: %2" ).arg( s, file.errorString() ) )
            return False

        
        # get contents
         originalData = QString.fromUtf8( file.readAll() )
        c = originalData
        
        # write process contents
        textCodec = QTextCodec.codecForName( codec.toUtf8() )
        c = VariablesManager.instance().replaceAllVariables( c, dictionnary )
        
        if  originalData != c :
            # reset file
            file.resize( 0 )
            file.write( textCodec.fromUnicode( c ) )

        
        # close file
        file.close()
        
        # open files if needed
        if  fo.contains( files[f] ) :
            MonkeyCore.fileManager().openFile( s, codec )
        if  po.contains( files[f] ) :
            MonkeyCore.fileManager().openProject( s, codec )
        
        # add files to project if needed
        if  scope and temp.FilesToAdd.contains( f ) :
            MonkeyCore.projectsManager().addFilesToScope( scope, QStringList( s ) )


    
    # return process state
    return True

