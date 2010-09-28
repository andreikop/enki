#include "PyQtProjectItem.h"

#include <xupmanager/core/XUPProjectItemInfos.h>
#include <pMonkeyStudio.h>
#include <pluginsmanager/BuilderPlugin.h>
#include <pluginsmanager/InterpreterPlugin.h>

#include <QApplication>
#include <QTextCodec>
#include <QFile>
#include <QDir>
#include <QFileInfo>

#include <QDebug>

int PyQtProjectItem::projectType() const
{
    return PyQtProjectItem::PyQtProject;
}

void PyQtProjectItem::registerProjectType() const
{
    // get proejct type
    int pType = projectType();

    // register it
    mXUPProjectInfos->unRegisterType( pType );
    mXUPProjectInfos->registerType( pType, const_cast<PyQtProjectItem*>( this ) );

    // values
    const QString mPixmapsPath = ":/pyqtitems";
    const QStringList mOperators = QStringList( "=" );
    const QStringList mFilteredVariables = QStringList( "FORMS" ) << "PYTHON_FILES";
    const QStringList mFileVariables = QStringList( "FORMS" ) << "PYTHON_FILES";
    const QStringList mPathVariables = QStringList();
    const StringStringListList mSuffixes = StringStringListList()
        << qMakePair( tr( "PyQt Project" ), QStringList( "*.xpyqt" ) );
    const StringStringList mVariableLabels = StringStringList()
        << qMakePair( QString( "FORMS" ), tr( "Qt Forms" ) )
        << qMakePair( QString( "PYTHON_FILES" ), tr( "Python Files" ) );
    const StringStringList mVariableIcons = StringStringList()
        << qMakePair( QString( "FORMS" ), QString( "forms" ) )
        << qMakePair( QString( "PYTHON_FILES" ), QString( "python" ) );

    // Variable suffixes
    const StringStringListList mVariableSuffixes = StringStringListList()
        << qMakePair( QString( "FORMS" ), QStringList( "*.ui" ) )
        << qMakePair( QString( "PYTHON_FILES" ), QStringList( "*.py*" ) );

    // register values
    mXUPProjectInfos->registerPixmapsPath( pType, mPixmapsPath );
    mXUPProjectInfos->registerOperators( pType, mOperators );
    mXUPProjectInfos->registerFilteredVariables( pType, mFilteredVariables );
    mXUPProjectInfos->registerFileVariables( pType, mFileVariables );
    mXUPProjectInfos->registerPathVariables( pType, mPathVariables );
    mXUPProjectInfos->registerSuffixes( pType, mSuffixes );
    mXUPProjectInfos->registerVariableLabels( pType, mVariableLabels );
    mXUPProjectInfos->registerVariableIcons( pType, mVariableIcons );
    mXUPProjectInfos->registerVariableSuffixes( pType, mVariableSuffixes );
}

XUPProjectItem* PyQtProjectItem::newProject() const
{
    return new PyQtProjectItem();
}

InterpreterPlugin* PyQtProjectItem::interpreter( const QString& plugin ) const
{
    QString plug = plugin;

    if ( plug.isEmpty() )
    {
        plug = "Python";
    }

    return XUPProjectItem::interpreter( plug );
}

void PyQtProjectItem::installCommands()
{
    // get plugins
    InterpreterPlugin* ip = interpreter();
    
    // temp command
    pCommand cmd;

    // build command
    if ( ip )
    {
        cmd = ip->interpretCommand();
    }
    
    cmd.setUserData( QVariant::fromValue( &mCommands ) );
    cmd.setProject( this );
    cmd.setSkipOnError( false );
    const pCommand cmdInterpret = cmd;
    
    // get qt version
    QString mainFile = relativeFilePath( projectSettingsValue( "MAIN_FILE" ) );
    
    if ( mainFile.isEmpty() )
    {
        mainFile = relativeFilePath( findFile( "main.py" ).value( 0 ).absoluteFilePath() );
    }
    
    // available commands
    if ( ip )
    {
        // execute project
        cmd = cmdInterpret;
        cmd.setText( tr( "Start" ) );
        cmd.setArguments( mainFile );
        cmd.setParsers( QStringList() );
        cmd.setTryAllParsers( false );
        addCommand( cmd, "mInterpreter" );
        
    }
    
    // install defaults commands
    XUPProjectItem::installCommands();
}
