#ifndef ENVIRONMENTVARIABLESMANAGER_H
#define ENVIRONMENTVARIABLESMANAGER_H

#include <widgets/pEnvironmentVariablesManager.h>

class MkSShellInterpreter

class EnvironmentVariablesManager : public pEnvironmentVariablesManager
public:
    EnvironmentVariablesManager()

    # interpreter commands
    void setCommand(  QString& name, value )
    void unsetCommand(  QString& name )
    void clearCommand()
    void enableCommand(  QString& name, enabled )

protected:
    # pEnvironmentVariablesManager reimplementations
    virtual bool writeVariables(  pEnvironmentVariablesModel.Variables& variables )
    virtual bool readVariables( pEnvironmentVariablesModel.Variables& variables )

    void initializeInterpreterCommands()
    static QString commandInterpreter(  QString& command, arguments, result, interpreter, data )


#endif # ENVIRONMENTVARIABLESMANAGER_H
