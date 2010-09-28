#include "CommandLineManager.h"
#include "main.h"
#include "coremanager/MonkeyCore.h"
#include "workspace/pFileManager.h"
#include "pMonkeyStudio.h"

#include <QStringList>
#include <QCoreApplication>
#include <QDebug>

CommandLineManager::CommandLineManager()
{
    mVersionShown = false;
}

CommandLineManager::~CommandLineManager()
{
}

void CommandLineManager::parse()
{
    QStringList args = QCoreApplication::arguments();
    args.removeFirst();
    
    for ( int i = 0; i < args.count(); i++ ) {
        const QString arg = args.at( i ).toLower();
        bool needNextArgument = false;
        
        if ( arg == "-projects" || arg == "-files" ) {
            needNextArgument = true;
        }
        else {
            mArguments[ arg ].clear();
        }
        
        if ( needNextArgument ) {
            if ( i == args.count() -1 ) {
                break;
            }
            
            QString param;
            
            while ( !( param = args.at( i +1 ).toLower() ).startsWith( "-" ) ) {
                mArguments[ arg ] << param;
                i++;
                
                if ( i == args.count() -1 ) {
                    break;
                }
            }
        }
    }
}

void CommandLineManager::process()
{
    foreach ( const QString& arg, mArguments.keys() ) {
        if ( arg == "-h" || arg == "--help" ) {
            showHelp();
        }
        else if ( arg == "-v" || arg == "--version" ) {
            showVersion();
        }
        else if ( arg == "-projects" ) {
            openProjects( mArguments[ arg ] );
        }
        else if ( arg == "-files" ) {
            openFiles( mArguments[ arg ] );
        }
        else {
            qWarning( "Unknow argument: %s (%s)", arg.toLocal8Bit().constData(), mArguments[ arg ].join( " " ).toLocal8Bit().constData() );
        }
    }
}

const QMap<QString, QStringList>& CommandLineManager::arguments() const
{
    return mArguments;
}

void CommandLineManager::showVersion()
{
    if ( !mVersionShown ) {
        mVersionShown = true;
        qWarning( "%s version %s (%s)", PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_VERSION_STR );
        qWarning( "%s & The Monkey Studio Team", PACKAGE_COPYRIGHTS );
        qWarning( "http://%s", PACKAGE_DOMAIN );
    }
}

void CommandLineManager::showHelp()
{
    showVersion();
    qWarning();
    qWarning( "Command line arguments:" );
    qWarning( "\t-h, --help      Show command line help" );
    qWarning( "\t-v, --version   Show program version" );
    qWarning( "\t-projects      Open the projects given as parameters (-projects project1 ...)" );
    qWarning( "\t-files         Open the files given as parameters (-files file1 ...)" );
}

void CommandLineManager::openProjects( const QStringList& fileNames )
{
    QDir dir( QCoreApplication::applicationDirPath() );
    
    foreach ( QString fileName, fileNames ) {
        if ( QFileInfo( fileName ).isRelative() ) {
            fileName = QDir::cleanPath( dir.absoluteFilePath( fileName ) );
        }
        
        MonkeyCore::fileManager()->openProject( fileName, pMonkeyStudio::defaultCodec() );
    }
}

void CommandLineManager::openFiles( const QStringList& fileNames )
{
    QDir dir( QCoreApplication::applicationDirPath() );
    
    foreach ( QString fileName, fileNames ) {
        if ( QFileInfo( fileName ).isRelative() ) {
            fileName = QDir::cleanPath( dir.absoluteFilePath( fileName ) );
        }
        
        MonkeyCore::fileManager()->openFile( fileName, pMonkeyStudio::defaultCodec() );
    }
}
