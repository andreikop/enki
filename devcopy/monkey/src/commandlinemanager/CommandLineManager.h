#ifndef COMMANDLINEMANAGER_H
#define COMMANDLINEMANAGER_H

#include <QMap>
#include <QStringList>

class CommandLineManager
public:
    CommandLineManager()
    ~CommandLineManager()

    void parse()
    void process()
     QMap<QString, arguments()

    void showVersion()
    void showHelp()
    void openProjects(  QStringList& fileNames )
    void openFiles(  QStringList& fileNames )

protected:
    QMap<QString, mArguments
    bool mVersionShown


#endif # COMMANDLINEMANAGER_H
