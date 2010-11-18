#include "CommandLineManager.h"
#include "main.h"
#include "coremanager/MonkeyCore.h"
#include "workspace/pFileManager.h"
#include "pMonkeyStudio.h"

#include <QStringList>
#include <QCoreApplication>
#include <QDebug>

CommandLineManager.CommandLineManager()
    mVersionShown = False


CommandLineManager.~CommandLineManager()


def parse(self):
    args = QCoreApplication.arguments()
    args.removeFirst()
    
    for ( i = 0; i < args.count(); i++ )         arg = args.at( i ).toLower()
        needNextArgument = False
        
        if  arg == "-projects" or arg == "-files" :            needNextArgument = True

        else:
            mArguments[ arg ].clear()

        
        if  needNextArgument :            if  i == args.count() -1 :                break

            
            QString param
            
            while ( not ( param = args.at( i +1 ).toLower() ).startsWith( "-" ) )                mArguments[ arg ] << param
                i++
                
                if  i == args.count() -1 :                    break






def process(self):
    for arg in mArguments.keys():        if  arg == "-h" or arg == "--help" :            showHelp()

        elif  arg == "-v" or arg == "--version" :            showVersion()

        elif  arg == "-projects" :            openProjects( mArguments[ arg ] )

        elif  arg == "-files" :            openFiles( mArguments[ arg ] )

        else:
            qWarning( "Unknow argument: %s (%s)", arg.toLocal8Bit().constData(), mArguments[ arg ].join( " " ).toLocal8Bit().constData() )




 QMap<QString, CommandLineManager.arguments()
    return mArguments


def showVersion(self):
    if  not mVersionShown :        mVersionShown = True
        qWarning( "%s version %s (%s)", PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_VERSION_STR )
        qWarning( "%s & The Monkey Studio Team", PACKAGE_COPYRIGHTS )
        qWarning( "http:#%s", PACKAGE_DOMAIN )



def showHelp(self):
    showVersion()
    qWarning()
    qWarning( "Command line arguments:" )
    qWarning( "\t-h, --help      Show command line help" )
    qWarning( "\t-v, --version   Show program version" )
    qWarning( "\t-projects      Open the projects given as parameters (-projects project1 ...)" )
    qWarning( "\t-files         Open the files given as parameters (-files file1 ...)" )


def openProjects(self, fileNames ):
    QDir dir( QCoreApplication.applicationDirPath() )
    
    for fileName in fileNames:        if  QFileInfo( fileName ).isRelative() :            fileName = QDir.cleanPath( dir.absoluteFilePath( fileName ) )

        
        MonkeyCore.fileManager().openProject( fileName, pMonkeyStudio.defaultCodec() )



def openFiles(self, fileNames ):
    QDir dir( QCoreApplication.applicationDirPath() )
    
    for fileName in fileNames:        if  QFileInfo( fileName ).isRelative() :            fileName = QDir.cleanPath( dir.absoluteFilePath( fileName ) )

        
        MonkeyCore.fileManager().openFile( fileName, pMonkeyStudio.defaultCodec() )


