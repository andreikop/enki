#include "EnvironmentVariablesManager.h"
#include "shellmanager/MkSShellInterpreter.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"

#include <QCoreApplication>
#include <QFile>
#include <QDebug>

EnvironmentVariablesManager::EnvironmentVariablesManager()
    : pEnvironmentVariablesManager()
{
    initializeInterpreterCommands();
}

bool EnvironmentVariablesManager::writeVariables( const pEnvironmentVariablesModel::Variables& variables ) const
{
    // write content in utf8
    const QString fn = MonkeyCore::settings()->homePath( Settings::SP_SCRIPTS ).append( "/environment-variables.mks" );
    QFile file( fn );
    QStringList buffer;
    
    if ( !file.open( QIODevice::WriteOnly ) ) {
        qWarning() << QString( "Can't open file for generating environment variables script: %1" ).arg( file.errorString() ).toLocal8Bit().constData();
        return false;
    }
    
    file.resize( 0 );
    
    buffer << "# Monkey Studio IDE Environment Variables";
    buffer << "# reset variables";
    buffer << "environment clear";
    buffer << "# Available commands:";
    buffer << "# environment set\tname\tvalue";
    buffer << "# environment unset\tname";
    buffer << "# environment clear";
    buffer << "# environment enable\tname\ttrue/false";
    buffer << "# introduce new ones per name/state";
    
    foreach ( const QString& name, variables.keys() ) {
        buffer << QString( "# %1" ).arg( name );
        buffer << QString( "environment set \"%1\" \"%2\"" )
            .arg( name )
            .arg( variables[ name ].value );
        buffer << QString( "environment enable \"%1\" \"%2\"" )
            .arg( name )
            .arg( QVariant( variables[ name ].enabled ).toString() );
    }
    
    if ( file.write( buffer.join( "\n" ).toUtf8() ) == -1 ) {
        qWarning() << QString( "Can't write generated environment variables script: %1" ).arg( file.errorString() ).toLocal8Bit().constData();
    }
    
    file.close();
    
    return true;
}

bool EnvironmentVariablesManager::readVariables( pEnvironmentVariablesModel::Variables& variables ) const
{
    Q_UNUSED( variables );
    return true;
}

void EnvironmentVariablesManager::initializeInterpreterCommands()
{
    // register command
    QString help = MkSShellInterpreter::tr(
        "This command manage the environment variables, usage:\n"
        "\tenvironment set [name] [value]\n"
        "\tenvironment unset [name]\n"
        "\tenvironment clear\n"
        "\tenvironment enable [name] [true/false]\n"
        "\tenvironment list"
    );
    
    MonkeyCore::interpreter()->addCommandImplementation( "environment", EnvironmentVariablesManager::commandInterpreter, help, this );
}

QString EnvironmentVariablesManager::commandInterpreter( const QString& command, const QStringList& _arguments, int* result, MkSShellInterpreter* interpreter, void* data )
{
    Q_UNUSED( command );
    Q_UNUSED( interpreter );
    EnvironmentVariablesManager* manager = static_cast<EnvironmentVariablesManager*>( data );
    QStringList arguments = _arguments;
    const QStringList allowedOperations = QStringList( "set" ) << "unset" << "clear" << "enable" << "list";
    
    if ( result ) {
        *result = MkSShellInterpreter::NoError;
    }
    
    if ( arguments.isEmpty() ) {
        if ( result ) {
            *result = MkSShellInterpreter::InvalidCommand;
        }
        
        return MkSShellInterpreter::tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) );
    }
    
    const QString operation = arguments.takeFirst();
    
    if ( !allowedOperations.contains( operation ) ) {
        if ( result ) {
            *result = MkSShellInterpreter::InvalidCommand;
        }
        
        return MkSShellInterpreter::tr( "Unknown operation: '%1'." ).arg( operation );
    }
    
    if ( operation == "set" ) {
        if ( arguments.count() != 2 ) {
            if ( result ) {
                *result = MkSShellInterpreter::InvalidCommand;
            }
            
            return MkSShellInterpreter::tr( "'set' operation take 2 arguments, %1 given." ).arg( arguments.count() );
        }
        
        const QString name = arguments.at( 0 );
        const QString value = arguments.at( 1 );
        
        manager->setCommand( name, value );
    }
    
    if ( operation == "unset" ) {
        if ( arguments.count() != 1 ) {
            if ( result ) {
                *result = MkSShellInterpreter::InvalidCommand;
            }
            
            return MkSShellInterpreter::tr( "'unset' operation take 1 arguments, %1 given." ).arg( arguments.count() );
        }
        
        const QString name = arguments.at( 0 );
        
        manager->unsetCommand( name );
    }
    
    if ( operation == "clear" ) {
        if ( arguments.count() != 0 ) {
            if ( result ) {
                *result = MkSShellInterpreter::InvalidCommand;
            }
            
            return MkSShellInterpreter::tr( "'clear' operation take no arguments, %1 given." ).arg( arguments.count() );
        }
        
        manager->clearCommand();
    }
    
    if ( operation == "enable" ) {
        if ( arguments.count() != 2 ) {
            if ( result ) {
                *result = MkSShellInterpreter::InvalidCommand;
            }
            
            return MkSShellInterpreter::tr( "'enable' operation take 2 arguments, %1 given." ).arg( arguments.count() );
        }
        
        const QString name = arguments.at( 0 );
        const bool enabled = QVariant( arguments.at( 1 ) ).toBool();
        
        manager->enableCommand( name, enabled );
    }
    
    if ( operation == "list" ) {
        if ( arguments.count() != 0 ) {
            if ( result ) {
                *result = MkSShellInterpreter::InvalidCommand;
            }
            
            return MkSShellInterpreter::tr( "'list' operation take no arguments, %1 given." ).arg( arguments.count() );
        }
        
        QStringList output;
        
        foreach ( const pEnvironmentVariablesModel::Variable& variable, manager->variables() ) {
            output << QString( "%1(%2)=\"%3\"" )
                .arg( variable.name )
                .arg( QVariant( variable.enabled ).toString() )
                .arg( variable.value );
        }
        
        if ( !output.isEmpty() ) {
            output.prepend( MkSShellInterpreter::tr( "Found environment variables:" ) );
        }
        else {
            output << MkSShellInterpreter::tr( "No environment variables found." );
        }
        
        return output.join( "\n" );
    }
    
    return QString::null;
}


void EnvironmentVariablesManager::setCommand( const QString& name, const QString& value )
{
    pEnvironmentVariablesModel::Variables variables = this->variables();
    if ( !variables.contains( name ) ) {
        variables[ name ].name = name;
    }
    variables[ name ].value = value;
    setVariables( variables );
}

void EnvironmentVariablesManager::unsetCommand( const QString& name )
{
    pEnvironmentVariablesModel::Variables variables = this->variables();
    variables.remove( name );
    setVariables( variables );
}

void EnvironmentVariablesManager::clearCommand()
{
    setVariables( pEnvironmentVariablesModel::Variables() );
}

void EnvironmentVariablesManager::enableCommand( const QString& name, bool enabled )
{
    pEnvironmentVariablesModel::Variables variables = this->variables();
    if ( variables.contains( name ) ) {
        variables[ name ].enabled = enabled;
    }
    setVariables( variables );
}
