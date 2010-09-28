#ifndef ENVIRONMENTVARIABLESMANAGER_H
#define ENVIRONMENTVARIABLESMANAGER_H

#include <widgets/pEnvironmentVariablesManager.h>

class MkSShellInterpreter;

class EnvironmentVariablesManager : public pEnvironmentVariablesManager
{
public:
    EnvironmentVariablesManager();
    
    // interpreter commands
    void setCommand( const QString& name, const QString& value );
    void unsetCommand( const QString& name );
    void clearCommand();
    void enableCommand( const QString& name, bool enabled );

protected:
    // pEnvironmentVariablesManager reimplementations
    virtual bool writeVariables( const pEnvironmentVariablesModel::Variables& variables ) const;
    virtual bool readVariables( pEnvironmentVariablesModel::Variables& variables ) const;
    
    void initializeInterpreterCommands();
    static QString commandInterpreter( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
};

#endif // ENVIRONMENTVARIABLESMANAGER_H
