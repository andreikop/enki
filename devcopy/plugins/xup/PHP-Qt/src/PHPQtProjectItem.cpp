#include "PHPQtProjectItem.h"

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

def projectType(self):
    return PHPQtProjectItem.PHPQtProject


def registerProjectType(self):
    # get proejct type
    pType = projectType()

    # register it
    mXUPProjectInfos.unRegisterType( pType )
    mXUPProjectInfos.registerType( pType, const_cast<PHPQtProjectItem*>( self ) )

    # values
     mPixmapsPath = ":/phpqtitems"
     mOperators = QStringList( "=" )
     mFilteredVariables = QStringList( "FORMS" ) << "PHP_FILES"
     mFileVariables = QStringList( "FORMS" ) << "PHP_FILES"
     mPathVariables = QStringList()
     mSuffixes = StringStringListList()
                                           << qMakePair( tr( "PHP-Qt Project" ), QStringList( "*.xphpqt" ) )
     mVariableLabels = StringStringList()
            << qMakePair( QString( "FORMS" ), tr( "Qt Forms" ) )
            << qMakePair( QString( "PHP_FILES" ), tr( "PHP Files" ) )
     mVariableIcons = StringStringList()
                                            << qMakePair( QString( "FORMS" ), QString( "forms" ) )
                                            << qMakePair( QString( "PHP_FILES" ), QString( "php" ) )

    # Variable suffixes
     mVariableSuffixes = StringStringListList()
            << qMakePair( QString( "FORMS" ), QStringList( "*.ui" ) )
            << qMakePair( QString( "PHP_FILES" ), QStringList( "*.php*" ) )

    # register values
    mXUPProjectInfos.registerPixmapsPath( pType, mPixmapsPath )
    mXUPProjectInfos.registerOperators( pType, mOperators )
    mXUPProjectInfos.registerFilteredVariables( pType, mFilteredVariables )
    mXUPProjectInfos.registerFileVariables( pType, mFileVariables )
    mXUPProjectInfos.registerPathVariables( pType, mPathVariables )
    mXUPProjectInfos.registerSuffixes( pType, mSuffixes )
    mXUPProjectInfos.registerVariableLabels( pType, mVariableLabels )
    mXUPProjectInfos.registerVariableIcons( pType, mVariableIcons )
    mXUPProjectInfos.registerVariableSuffixes( pType, mVariableSuffixes )


def newProject(self):
    return PHPQtProjectItem()


def interpreter(self, plugin ):
    plug = plugin

    if  plug.isEmpty() :
        plug = "PHP"


    return XUPProjectItem.interpreter( plug )


def installCommands(self):
    # get plugins
    ip = interpreter()

    # temp command
    pCommand cmd

    # build command
    if  ip :
        cmd = ip.interpretCommand()


    cmd.setUserData( QVariant.fromValue( &mCommands ) )
    cmd.setProject( self )
    cmd.setSkipOnError( False )
     cmdInterpret = cmd

    # get qt version
    mainFile = relativeFilePath( projectSettingsValue( "MAIN_FILE" ) )

    if  mainFile.isEmpty() :
        mainFile = relativeFilePath( findFile( "main.php" ).value( 0 ).absoluteFilePath() )


    # available commands
    if  ip :
        # execute project
        cmd = cmdInterpret
        cmd.setText( tr( "Start" ) )
        cmd.setArguments( mainFile )
        cmd.setParsers( QStringList() )
        cmd.setTryAllParsers( False )
        addCommand( cmd, "mInterpreter" )



    # install defaults commands
    XUPProjectItem.installCommands()

