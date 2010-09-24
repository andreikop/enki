#ifndef MKSSHELLINTERPRETER_H
#define MKSSHELLINTERPRETER_H

#include <objects/MonkeyExport.h>
#include "widgets/pConsoleCommand.h"

#include <QPointer>
#include <QObject>
#include <QHash>

'''
Pointer to function
def commandImplementation(self, command, arguments, result, interpreter, data ):
'''
typedef QString (*CommandImplementationPtr)( QString&,  QStringList&, int*, MkSShellInterpreter*, void* )

class Q_MONKEY_EXPORT MkSShellInterpreter : public QObject, pConsoleCommand
    Q_OBJECT

public:
    enum Error
        NoError = 0,
        InvalidCommand = -1,
        NoResultVariable = -2,
        UnknowError = -3


    static MkSShellInterpreter* instance( parent = 0 )

    bool loadScript(  QString& fileName )
    void loadHomeScripts()
    QString usage(  QString& command )
    QString interpret(  QString& command, result )

    void addCommandImplementation(  QString& command, function, help = QString.null, data = 0 )
    void removeCommandImplementation(  QString& command )
    void setCommandHelp(  QString& command, help )

protected:
    static QPointer<MkSShellInterpreter> mInstance
    QHash<QString, mCommandImplementations
    QHash<QString, mCommandImplementationsData
    QHash<QString, mCommandHelps

    MkSShellInterpreter( parent = 0 )
    static QString interpretHelp(  QString&, arguments, result, interpreter, data )
    static QString interpretEcho(  QString&, arguments, result, interpreter, data )

signals:
    void commandExecuted(  QString& command, output, result )


#endif # MKSSHELLINTERPRETER_H
