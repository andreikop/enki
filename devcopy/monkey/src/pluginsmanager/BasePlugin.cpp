/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>, Andrei KOPATS aka hlamer <hlamer@tut.by>
** Project   : Monkey Studio IDE
** FileName  : BasePlugin.cpp
** Date      : 2009-12-09T00:37:00
** License   : GPL
** Comment   : 
** Home Page : http://www.monkeystudio.org
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
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
#include "BasePlugin.h"
#include "main.h"

#include <QCoreApplication>

BasePlugin::BasePlugin()
{
    // auto fill minimum version required using compil time version
    mPluginInfos.ApplicationVersionRequired = PACKAGE_VERSION;
}

BasePlugin::~BasePlugin()
{
    if ( isEnabled() ) 
        setEnabled( false );
}

QString BasePlugin::typeToString( BasePlugin::Type type )
{
    switch ( type )
    {
        case BasePlugin::iAll:
            return QCoreApplication::translate( "BasePlugin", "All" );
            break;
        case BasePlugin::iBase:
            return QCoreApplication::translate( "BasePlugin", "Basic" );
            break;
        case BasePlugin::iChild:
            return QCoreApplication::translate( "BasePlugin", "Child" );
            break;
        case BasePlugin::iCLITool:
            return QCoreApplication::translate( "BasePlugin", "Command Line Tool" );
            break;
        case BasePlugin::iBuilder:
            return QCoreApplication::translate( "BasePlugin", "Builder" );
            break;
        case BasePlugin::iDebugger:
            return QCoreApplication::translate( "BasePlugin", "Debugger" );
            break;
        case BasePlugin::iInterpreter:
            return QCoreApplication::translate( "BasePlugin", "Interpreter" );
            break;
        case BasePlugin::iXUP:
            return QCoreApplication::translate( "BasePlugin", "XUP Project" );
            break;
        case BasePlugin::iLast:
            return QCoreApplication::translate( "BasePlugin", "NaN" );
            break;
        default:
            //Q_ASSERT( 0 ); // comment assert as in debug it will always assert as i do a loop that contains bad type in the compelteTypeToString() member.
            return QString::null;
            break;
    }
}

QString BasePlugin::completeTypeToString( BasePlugin::Types _type )
{
    QStringList types;
    
    for ( int i = BasePlugin::iAll; i < BasePlugin::iLast; i++ )
    {
        const BasePlugin::Type type = (BasePlugin::Type)i;
        const QString typeString = typeToString( type );
        
        if ( !typeString.isEmpty() && !types.contains( typeString ) )
        {
            if ( _type.testFlag( type ) )
            {
                types << typeString;
            }
        }
    }
    
    return types.join( ", " );
}

QString BasePlugin::captionVersionString() const
{
    return QString( "%1 (%2)" ).arg( infos().Caption ).arg( infos().Version );
}

QAction* BasePlugin::stateAction() const
{
    if ( !mAction )
    {
        mAction = new QAction( const_cast<BasePlugin*>( this ) );
        mAction->setCheckable( true );
        mAction->setText( tr( "Enabled" ) );
        mAction->setObjectName( captionVersionString().replace( " ", "_" ) );
        mAction->setData( QVariant::fromValue( const_cast<BasePlugin*>( this ) ) );
    }
    
    return mAction;
}

bool BasePlugin::setEnabled( bool enabled )
{
    if ( enabled && !isEnabled() )
    {
        stateAction()->setChecked( install() );
        return stateAction()->isChecked();
    }
    else if ( !enabled && isEnabled() )
    {
        stateAction()->setChecked( !uninstall() );
        return !stateAction()->isChecked();
    }
    
    return true;
}

QString BasePlugin::settingsKey( const QString& key ) const
{
    return QString( "Plugins/%1/%2" ).arg( infos().Name ).arg(  key );
}

QVariant BasePlugin::settingsValue( const QString& key, const QVariant& value ) const
{
    return MonkeyCore::settings()->value( settingsKey( key ), value );
}

void BasePlugin::setSettingsValue( const QString& key, const QVariant& value ) const
{
    MonkeyCore::settings()->setValue( settingsKey( key ), value );
}

#ifdef __COVERAGESCANNER__
void BasePlugin::saveCodeCoverage( const QString& n, const QString& s )
{
    // set path
    QString s = QCoreApplication::applicationDirPath();
#ifndef Q_OS_WIN
    s = QDir::homePath();
#endif
    s.append( "/monkeystudio_tests" );
    
    // create path if it not exists
    QDir d( s );
    if ( !d.exists() )
        d.mkdir( s );
    
    // set os specific filename
    s = QDir::toNativeSeparators( s.append( "/monkey_cov" ) ); 
    
    // deal with coverage meter
    __coveragescanner_filename( s.toLocal8Bit().constData() );
    __coveragescanner_teststate( s.toLocal8Bit().constData() );
    __coveragescanner_testname( QString( "%1/%2" ).arg( n ).arg( infos().Name ).toLocal8Bit().constData() );
    __coveragescanner_save();
}
#endif
