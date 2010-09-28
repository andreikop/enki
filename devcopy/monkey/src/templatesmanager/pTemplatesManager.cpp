/****************************************************************************
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
****************************************************************************/
/*!
    \file pTemplatesManager.cpp
    \date 2008-01-14T00:37:13
    \author Andrei KOPATS, Filepe AZEVEDO
    \brief Implementation of pTemplatesManager class
*/

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

using namespace pMonkeyStudio;

/*!
    Class constructor
    \param o Parent object. Passing to QObject constructor
*/
pTemplatesManager::pTemplatesManager( QObject* o )
    : QObject( o )
{}

/*!
    Read template from file
    \param s Path of template config file (.ini)
    \return Inmemory representation of template
*/
pTemplate pTemplatesManager::getTemplate( const QString& s )
{
    // open ini file
    QSettings set( s, QSettings::IniFormat );
    
    // fill template infos
    pTemplate t;
    t.Name = QFileInfo( s ).dir().dirName();
    t.Language = set.value( "Language", tr( "Other" ) ).toString();
    t.Type = set.value( "Type", tr( "Wrong template type" ) ).toString();
    t.Description = set.value( "Description", tr( "No desctiption" ) ).toString();
    t.Icon = set.value( "Icon" ).toString();
    t.Script = set.value( "Script" ).toString();
    t.DirPath = QFileInfo( s ).absolutePath().append( "/" );
    t.Files = set.value( "Files" ).toStringList();
    t.FilesToOpen = set.value( "FilesToOpen" ).toStringList();
    t.ProjectsToOpen = set.value( "ProjectsToOpen" ).toStringList();
    t.FilesToAdd = set.value( "FilesToAdd" ).toStringList();
    t.Variables = VarList();
    
    // set template vars
    foreach( QString v, set.value( "Variables" ).toStringList() )
        t.Variables[v] = set.value( v +"Values" ).toStringList();
    
    // return template
    return t;
}

/*!
    Read all availible templates
    \return List of templates, finded in all configured path
*/
TemplateList pTemplatesManager::getTemplates()
{
    TemplateList l;
    foreach( QString p, MonkeyCore::settings()->storagePaths( Settings::SP_TEMPLATES ) )
        foreach ( QFileInfo f, getFiles( QDir( unTokenizeHome( QDir::isRelativePath( p ) ? qApp->applicationDirPath().append( "/%1" ).arg( p ) : p ) ), QStringList( "template.ini" ), true ) )
            l << getTemplate( f.absoluteFilePath() );
    return l;
}

/*!
    Create files from already configured template
    \param scope The project scope where to add files. Else NULL
    \param op The scope operator to use
    \param temp Template to realise
    \param dictionnary Dictionary of variables for template
    \return Result of creation
    \retval true All files is created successfully
    \retval false Some error ocurred
*/
bool pTemplatesManager::realiseTemplate( XUPItem* scope, const pTemplate& temp, const QString& codec, const VariablesManager::Dictionary& dictionnary )
{
    // get destination
    QString dest = dictionnary["Destination"];
    
    // check destination
    if ( dest.isEmpty() )
    {
        QMessageBox::warning( 0, tr( "Error..." ), tr( "Destination not set." ) );
        return false;
    }
    
    // check destination exists
    QDir destdir( dest );
    if ( !destdir.exists() )
    {
        if ( !destdir.mkpath( dest ) )
        {
            QMessageBox::warning( 0, tr( "Error..." ), tr( "Can't create destination '%1'" ).arg( dest ) );
            return false;
        }
    }
    
    // append final slashe
    if ( !dest.endsWith( "/" ) )
        dest.append( '/' );
    
    // replace values in files/projects to open
    QStringList fo, po;
    for ( int i = 0; i < temp.FilesToOpen.count(); i++ )
        fo << VariablesManager::instance()->replaceAllVariables( temp.FilesToOpen.at( i ), dictionnary );
    for ( int i = 0; i < temp.ProjectsToOpen.count(); i++ )
        po << VariablesManager::instance()->replaceAllVariables( temp.ProjectsToOpen.at( i ), dictionnary );
    
    // get files
    QHash<QString, QString> files;
    foreach( const QString& f, temp.Files )
    {
        // check if sources and destination are differents
        QString sf, df;
        sf = f;
        df = f;
        if ( f.contains( '|' ) )
        {
            sf = f.section( '|', 0, 0 );
            df = f.section( '|', 1, 1 );
        }
        
        // process variables
        QString s = VariablesManager::instance()->replaceAllVariables( df, dictionnary );
        
        // check value validity
        if ( s.isEmpty() )
        {
            QMessageBox::warning( 0, tr( "Error..." ), tr( "Empty filename detected for file %1" ).arg( sf ) );
            return false;
        }
        
        // append file to list
        files[sf] = s;
    }
    
    // create files
    foreach( QString f, files.keys() )
    {
        // get source file
        QString k = QFile::exists( QString( "%1%2" ).arg( temp.DirPath, f ) ) ? f : VariablesManager::instance()->replaceAllVariables( f, dictionnary );
        
        // get file name
        QString s = QString( "%1%2" ).arg( dest, files[f] );
        
        // check file destination exists
        QDir fd( QFileInfo( s ).path() );
        if ( !fd.exists() )
        {
            if ( !fd.mkpath( fd.path() ) )
            {
                QMessageBox::warning( 0, tr( "Error..." ), tr( "Can't create destination '%1'" ).arg( fd.path() ) );
                return false;
            }
        }
        
        // copy file
        if ( !QFile::copy( QString( "%1%2" ).arg( temp.DirPath, k ), s ) )
        {
            QMessageBox::warning( 0, tr( "Error..." ), tr( "Can't copy '%1%2' to '%3'" ).arg( temp.DirPath, k, s ) );
            return false;
        }
        
        // open file
        QFile file( s );
        if ( !file.open( QIODevice::ReadWrite | QIODevice::Text ) )
        {
            QMessageBox::warning( 0, tr( "Error..." ), tr ( "Can't edit file %1: %2" ).arg( s, file.errorString() ) );
            return false;
        }
        
        // get contents
        const QString originalData = QString::fromUtf8( file.readAll() );
        QString c = originalData;
        
        // write process contents
        QTextCodec* textCodec = QTextCodec::codecForName( codec.toUtf8() );
        c = VariablesManager::instance()->replaceAllVariables( c, dictionnary );
        
        if ( originalData != c )
        {
            // reset file
            file.resize( 0 );
            file.write( textCodec->fromUnicode( c ) );
        }
        
        // close file
        file.close();
        
        // open files if needed
        if ( fo.contains( files[f] ) )
            MonkeyCore::fileManager()->openFile( s, codec );
        if ( po.contains( files[f] ) )
            MonkeyCore::fileManager()->openProject( s, codec );
        
        // add files to project if needed
        if ( scope && temp.FilesToAdd.contains( f ) )
        {
            MonkeyCore::projectsManager()->addFilesToScope( scope, QStringList( s ) );
        }
    }
    
    // return process state
    return true;
}
