#include "QMakeProjectItem.h"
#include "QMake2XUP.h"
#include "QMake.h"
#include "QtVersionManager.h"

#include <xupmanager/core/XUPProjectItemInfos.h>
#include <pMonkeyStudio.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <pluginsmanager/BuilderPlugin.h>

#include <QApplication>
#include <QTextCodec>
#include <QFile>
#include <QDir>
#include <QFileInfo>
#include <QProcess>

#include <QDebug>

QMakeProjectItem.QMakeProjectItem()
        : XUPProjectItem()


QMakeProjectItem.~QMakeProjectItem()


def toString(self):
    return QMake2XUP.convertToPro( mDocument )


def registerProjectType(self):
    # get proejct type
    pType = projectType()

    # register it
    mXUPProjectInfos.unRegisterType( pType )
    mXUPProjectInfos.registerType( pType, const_cast<QMakeProjectItem*>( self ) )

    # values
     mPixmapsPath = ":/qmakeitems"
     mOperators = QStringList( "=" ) << "+=" << "-=" << "*=" << "~="
     mFilteredVariables = QStringList() << "FORMS" << "FORMS3"
                                           << "HEADERS" << "SOURCES" << "OBJECTIVE_SOURCES" << "YACCSOURCES" << "LEXSOURCES"
                                           << "TRANSLATIONS" << "RESOURCES" << "RC_FILE" << "RES_FILE" << "DEF_FILE"
                                           << "INCLUDEPATH" << "DEPENDPATH" << "VPATH" << "LIBS" << "DEFINES" << "OTHER_FILES"
     mFileVariables = QStringList( "FORMS" ) << "FORMS3" << "HEADERS"
                                       << "SOURCES" << "OBJECTIVE_SOURCES" << "YACCSOURCES" << "LEXSOURCES"
                                       << "TRANSLATIONS" << "RESOURCES" << "RC_FILE" << "RES_FILE" << "DEF_FILE" << "SUBDIRS" << "OTHER_FILES"
     mPathVariables = QStringList( "INCLUDEPATH" ) << "DEPENDPATH"
                                       << "VPATH"
     mSuffixes = StringStringListList()
                                           << qMakePair( tr( "Qt Project" ), QStringList( "*.pro" ) )
                                           << qMakePair( tr( "Qt Include Project" ), QStringList( "*.pri" ) )
     mVariableLabels = StringStringList()
            << qMakePair( QString( "FORMS" ), tr( "Forms Files" ) )
            << qMakePair( QString( "FORMS3" ), tr( "Forms 3 Files" ) )
            << qMakePair( QString( "HEADERS" ), tr( "Headers Files" ) )
            << qMakePair( QString( "SOURCES" ), tr( "Sources Files" ) )
            << qMakePair( QString( "OBJECTIVE_SOURCES" ), tr( "Objective Sources Files" ) )
            << qMakePair( QString( "TRANSLATIONS" ), tr( "Qt Translations Files" ) )
            << qMakePair( QString( "RESOURCES" ), tr( "Qt Resources Files" ) )
            << qMakePair( QString( "RC_FILE" ), tr( "Resources Files" ) )
            << qMakePair( QString( "RES_FILE" ), tr( "Compiled Resources Files" ) )
            << qMakePair( QString( "DEF_FILE" ), tr( "Definitions Files" ) )
            << qMakePair( QString( "SUBDIRS" ), tr( "Sub Projects" ) )
            << qMakePair( QString( "INCLUDEPATH" ), tr( "Includes Paths" ) )
            << qMakePair( QString( "DEPENDPATH" ), tr( "Depends Paths" ) )
            << qMakePair( QString( "VPATH" ), tr( "Virtuals Paths" ) )
            << qMakePair( QString( "LIBS" ), tr( "Libraries Files" ) )
            << qMakePair( QString( "DEFINES" ), tr( "Defines" ) )
            << qMakePair( QString( "OTHER_FILES" ), tr( "Other Files" ) )
     mVariableIcons = StringStringList()
                                            << qMakePair( QString( "FORMS" ), QString( "forms" ) )
                                            << qMakePair( QString( "FORMS3" ), QString( "forms" ) )
                                            << qMakePair( QString( "HEADERS" ), QString( "headers" ) )
                                            << qMakePair( QString( "SOURCES" ), QString( "sources" ) )
                                            << qMakePair( QString( "OBJECTIVE_SOURCES" ), QString( "objective_sources" ) )
                                            << qMakePair( QString( "TRANSLATIONS" ), QString( "translations" ) )
                                            << qMakePair( QString( "RESOURCES" ), QString( "resources" ) )
                                            << qMakePair( QString( "RC_FILE" ), QString( "rc_file" ) )
                                            << qMakePair( QString( "RES_FILE" ), QString( "res_file" ) )
                                            << qMakePair( QString( "DEF_FILE" ), QString( "def_file" ) )
                                            << qMakePair( QString( "SUBDIRS" ), QString( "project" ) )
                                            << qMakePair( QString( "INCLUDEPATH" ), QString( "includepath" ) )
                                            << qMakePair( QString( "DEPENDPATH" ), QString( "dependpath" ) )
                                            << qMakePair( QString( "VPATH" ), QString( "vpath" ) )
                                            << qMakePair( QString( "LIBS" ), QString( "libs" ) )
                                            << qMakePair( QString( "DEFINES" ), QString( "defines" ) )
                                            << qMakePair( QString( "OTHER_FILES" ), QString( "file" ) )
     cf = pMonkeyStudio.availableLanguagesSuffixes().value( "C++" )
    # HEADERS filters
    QStringList hf
    for f in cf:
    if  f.startsWith( "*.h", Qt.CaseInsensitive ) :
        hf << f
    # SOURCES filters
    QStringList sf
    for f in cf:
    if  f.startsWith( "*.c", Qt.CaseInsensitive ) :
        sf << f
    # YACC filters
    QStringList yf
    for s in sf:
    if  not yf.contains( s.replace( "c", "y", Qt.CaseInsensitive ) ) :
        yf << s
    # LEX filters
    QStringList lf
    for s in sf:
    if  s.startsWith( "*.c", Qt.CaseInsensitive ) and not lf.contains( s.replace( "c", "l", Qt.CaseInsensitive ) ) :
        lf << s
    # PROJECT filters
    QStringList pjf
    for p in mSuffixes:
    pjf << p.second
    # Variable suffixes
     mVariableSuffixes = StringStringListList()
            << qMakePair( QString( "HEADERS" ), hf )
            << qMakePair( QString( "SOURCES" ), sf )
            << qMakePair( QString( "YACCSOURCES" ), yf )
            << qMakePair( QString( "LEXSOURCES" ), lf )
            << qMakePair( QString( "OBJECTIVE_SOURCES" ), QStringList( "*.m" ) << "*.mm" )
            << qMakePair( QString( "FORMS" ), QStringList( "*.ui" ) )
            << qMakePair( QString( "FORMS3" ), QStringList( "*.ui" ) )
            << qMakePair( QString( "TRANSLATIONS" ), QStringList( "*.ts" ) )
            << qMakePair( QString( "RESOURCES" ), QStringList( "*.qrc" ) )
            << qMakePair( QString( "DEF_FILE" ), QStringList( "*.def" ) )
            << qMakePair( QString( "RC_FILE" ), QStringList( "*.rc" ) )
            << qMakePair( QString( "RES_FILE" ), QStringList( "*.res" ) )
            << qMakePair( QString( "SUBDIRS" ), QStringList( "*.pro" ) )

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


def handleSubdirs(self, subdirs ):
    QStringList projects
    proj = subdirs.project()

    for cit in subdirs.childrenList():
        if  cit.type() == XUPItem.File :
            cacheFns = splitMultiLineValue( cit.cacheValue( "content" ) )

            for cacheFn in cacheFns:
                if  cacheFn.isEmpty() :
                    continue


                fn = filePath( cacheFn )
                QFileInfo fi( fn )

                if  cacheFn.endsWith( "/" ) :
                    cacheFn.chop( 1 )


                sepPos = cacheFn.lastIndexOf( "/" )

                if  sepPos != -1 :
                    cacheFn = cacheFn.mid( sepPos +1 )


                if  fi.isDir() :
                    fi.setFile( fn, QString( "%1.pro" ).arg( cacheFn ) )


                fn = fi.absoluteFilePath()

                if  not projects.contains( fn ) :
                    projects << fn





    for cit in proj.childrenList():
        if  cit.type() == XUPItem.Project :
            if  projects.contains( cit.project().fileName() ) :
                projects.removeAll( cit.project().fileName() )




    for fn in projects:
        # open project
        project = newProject()
        proj.addChild( project )

        # remove and delete project if can't open
        if  not project.open( fn, temporaryValue( "codec" ).toString() ) :
            proj.removeChild( project )
            topLevelProject().setLastError( tr( "Failed to handle subdirs file %1" ).arg( fn ) )
            return False



    return True


def getVariableContent(self, variableName ):
    '''
        $$[QT_INSTALL_HEADERS] : read content from qt conf
        $${QT_INSTALL_HEADERS} or $$QT_INSTALL_HEADERS : read content from var
        $$(QT_INSTALL_HEADERS) : read from environment when qmake run
        $(QTDIR) : read from generated makefile
    '''

    name = QString( variableName ).replace( '$', "" ).replace( '{', "" ).replace( '}', "" ).replace( '[', "" ).replace( ']', "" ).replace( '(', "" ).replace( ')', "" )

    # environment var
    if  variableName.startsWith( "$$(" ) or variableName.startsWith( "$(" ) :
        if  name == "PWD" :
            return rootIncludeProject().path()

        else:
            return QString.fromLocal8Bit( qgetenv( name.toLocal8Bit().constData() ) )


    elif  variableName.startsWith( "$$[" ) :
        proj = rootIncludeProject()

        if  proj.variableCache().contains( name ) :
            return proj.variableCache().value( name )


        QString result
        manager = QMake.versionManager()
         version = manager.version( projectSettingsValue( "QT_VERSION" ) )

        if  version.isValid() :
            QProcess query
            query.start( QString( "%1 -query %2" ).arg( version.qmake() ).arg( name ) )
            query.waitForFinished()
            result = QString.fromLocal8Bit( query.readAll() ).trimmed()

            if  result == "**Unknown**" :
                result.clear()



        #proj.variableCache()[ name ] = result
        return result

    else:
        if  name == "PWD" :
            return project().path()

        elif  name == "_PRO_FILE_" :
            return rootIncludeProject().fileName()

        elif  name == "_PRO_FILE_PWD_" :
            return rootIncludeProject().path()

        else:
            return rootIncludeProject().variableCache().value( name )



    return QString.null


def analyze(self, item ):
    QStringList values
    project = item.project()
    riProject = rootIncludeProject()

    for cItem in item.childrenList():
        switch ( cItem.type() )
        case XUPItem.Value:
        case XUPItem.File:
        case XUPItem.Path:
            content = interpretContent( cItem.attribute( "content" ) )

            if  cItem.type() != XUPItem.Value :
                fn = project.filePath( content )

                if  QFile.exists( fn ) :
                    fn = riProject.relativeFilePath( fn )


                content = fn


            values << content

            cItem.setCacheValue( "content", content )
            break

        case XUPItem.Function:
            parameters = interpretContent( cItem.attribute( "parameters" ) )

            cItem.setCacheValue( "parameters", parameters )
            break

        case XUPItem.Project:
        case XUPItem.Comment:
        case XUPItem.EmptyLine:
        case XUPItem.Variable:
        case XUPItem.Scope:
        case XUPItem.DynamicFolder:
        case XUPItem.Folder:
        default:
            break


        if  not analyze( cItem ) :
            return False



    if  item.type() == XUPItem.Variable :
        name = item.attribute( "name" )
        op = item.attribute( "operator", "=" )

        if  op == "=" :
            riProject.variableCache()[ name ] = values.join( " " )

        elif  op == "-=" :
            for value in values:
                riProject.variableCache()[ name ].replace( QRegExp( QString( "\\b%1\\b" ).arg( value ) ), QString.null )


        elif  op == "+=" :
            riProject.variableCache()[ name ] += " " +values.join( " " )

        elif  op == "*=" :
            #if  not riProject.variableCache()[ name ].contains( content ) :
                riProject.variableCache()[ name ] += " " +values.join( " " )


        elif  op == "~=" :
            topLevelProject().setLastError( tr( "Don't know how to interpret ~= operator" ) )



    # handle include projects
    if  item.attribute( "name" ).toLower() == "include" :
        if  not handleIncludeFile( item ) :
            return False



    # handle sub projects
    if  item.attribute( "name" ) == "SUBDIRS" :
        if  not handleSubdirs( item ) :
            return False



    return True


def open(self, fileName, codec ):
    buffer = QMake2XUP.convertFromPro( fileName, codec )

    # parse content
    QString errorMsg
    int errorLine
    int errorColumn
    if  not mDocument.setContent( buffer, &errorMsg, &errorLine, &errorColumn ) :
        topLevelProject().setLastError( QString( "%1 on line: %2, column: %3" ).arg( errorMsg ).arg( errorLine ).arg( errorColumn ) )
        return False


    # check project validity
    mDomElement = mDocument.firstChildElement( "project" )
    if  mDomElement.isNull() :
        topLevelProject().setLastError("no project node" )
        return False


    # all is ok
    setTemporaryValue( "codec", codec )
    setTemporaryValue( "fileName", fileName )
    topLevelProject().setLastError( QString.null )

    return analyze( self )


def save(self):
    return XUPProjectItem.save()


def targetFilePath(self, allowToAskUser, targetType, platformType ):
    return XUPProjectItem.targetFilePath( allowToAskUser, targetType, platformType )

    '''
    if  QFile.exists( target ) :
        return target


    riProject = rootIncludeProject()
    target = riProject.variableCache().value( "TARGET" )
    destdir = riProject.variableCache().value( "DESTDIR" )

    if  target.isEmpty() :
        target = QFileInfo( fileName() ).baseName()


    if  destdir.isEmpty() :
        destdir = riProject.variableCache().value( "DLLDESTDIR" )


    if  destdir.isEmpty() :
        destdir = riProject.path()


    if  QDir( destdir ).isRelative() :
        destdir = riProject.filePath( destdir )


    target = QDir.cleanPath( QString( "%1/%2" ).arg( destdir ).arg( target ) )

    # fix target name. Step 1 - try to use settings
    if  not QFile.exists( target ):
        target = XUPProjectItem.targetFilePath( allowToAskUser, targetType, platformType )


    return target
    '''


def builder(self, plugin ):
    plug = plugin

    if  plug.isEmpty() :
        manager = QMake.versionManager()
         version = manager.version( projectSettingsValue( "QT_VERSION" ) )

        if  version.isValid() :
            if  version.QMakeSpec.contains( "msvc", Qt.CaseInsensitive ) :
                plug = "MSVCMake"



        if  plug.isEmpty() :
            plug = "GNUMake"



    return XUPProjectItem.builder( plug )


def debugger(self, plugin ):
    plug = plugin

    if  plug.isEmpty() :
        plug = "BeaverDebugger"


    return XUPProjectItem.debugger( plug )


def interpreter(self, plugin ):
    plug = plugin

    if  plug.isEmpty() :
        '''
        manager = QMake.versionManager()
         version = manager.version( projectSettingsValue( "QT_VERSION" ) )

        if  version.isValid() :
            if  version.QMakeSpec.contains( "msvc", Qt.CaseInsensitive ) :
                plug = "MSVC"



        if  plug.isEmpty() :
            plug = "G++"

        '''


    return XUPProjectItem.interpreter( plug )


def installCommands(self):
    # get plugins
    bp = builder()

    # config variable
    riProject = rootIncludeProject()
    config = splitMultiLineValue( riProject.variableCache().value( "CONFIG" ) )
    haveDebug = config.contains( "debug" )
    haveRelease = config.contains( "release" )
    haveDebugRelease = config.contains( "debug_and_release" )

    # temp command
    pCommand cmd

    # build command
    if  bp :
        cmd = bp.buildCommand()

    cmd.setUserData( QVariant.fromValue( &mCommands ) )
    cmd.setProject( self )
    cmd.setSkipOnError( False )
     cmdBuild = cmd

    # get qt version
    manager = QMake.versionManager()
     version = manager.version( projectSettingsValue( "QT_VERSION" ) )

    # evaluate some variables
    QString s
    s = riProject.variableCache().value( "TARGET" )

    if  s.isEmpty() :
        s = QFileInfo( fileName() ).baseName()


     target = s
    s = riProject.variableCache().value( "DESTDIR" )

    if  s.isEmpty() :
        s = riProject.variableCache().value( "DLLDESTDIR" )


    if  QDir( s ).isRelative() :
        s.prepend( "$cpp$/" )


    if  s.endsWith( '/' ) :
        s.chop( 1 )


     destdir = s

    # compiler
    if  bp and cmdBuild.isValid() :
        # build debug
        if  haveDebug or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Build Debug" ) )
            if  haveDebugRelease :
                cmd.setArguments( "debug" )

            addCommand( cmd, "mBuilder/mBuild" )


        # build release
        if  haveRelease or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Build Release" ) )
            if  haveDebugRelease :
                cmd.setArguments( "release" )

            addCommand( cmd, "mBuilder/mBuild" )


        # build all
        if  haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Build All" ) )
            cmd.setArguments( "all" )
            addCommand( cmd, "mBuilder/mBuild" )


        # clean debug
        if  haveDebug or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Clean Debug" ) )
            if  haveDebugRelease :
                cmd.setArguments( "debug-clean" )

            else:
                cmd.setArguments( "clean" )

            addCommand( cmd, "mBuilder/mClean" )


        # clean release
        if  haveRelease or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Clean Release" ) )
            if  haveDebugRelease :
                cmd.setArguments( "release-clean" )

            else:
                cmd.setArguments( "clean" )

            addCommand( cmd, "mBuilder/mClean" )


        # clean all
        if  haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Clean All" ) )
            cmd.setArguments( "clean" )
            addCommand( cmd, "mBuilder/mClean" )


        # distclean debug
        if  haveDebug or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Distclean Debug" ) )
            if  haveDebugRelease :
                cmd.setArguments( "debug-distclean" )

            else:
                cmd.setArguments( "distclean" )

            addCommand( cmd, "mBuilder/mClean" )


        # distclean release
        if  haveRelease or haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Distclean Release" ) )
            if  haveDebugRelease :
                cmd.setArguments( "release-distclean" )

            else:
                cmd.setArguments( "distclean" )

            addCommand( cmd, "mBuilder/mClean" )


        # distclean all
        if  haveDebugRelease :
            cmd = cmdBuild
            cmd.setText( tr( "Distclean All" ) )
            cmd.setArguments( "distclean" )
            addCommand( cmd, "mBuilder/mClean" )


        # add qt commands only if possible
        if  version.isValid() :
            # qmake command
            cmd = pCommand()
            cmd.setText( tr( "QMake" ) )
            cmd.setCommand( version.qmake() )
            cmd.setArguments( version.qmakeParameters() )
            cmd.setWorkingDirectory( "$cpp$" )
            cmd.setUserData( QVariant.fromValue( &mCommands ) )
            cmd.setProject( self )
            cmd.setSkipOnError( False )
            addCommand( cmd, "mBuilder" )

            # lupdate command
            cmd = pCommand()
            cmd.setText( tr( "lupdate" ) )
            cmd.setCommand( version.lupdate() )
            cmd.setArguments( "\"$cp$\"" )
            cmd.setWorkingDirectory( "$cpp$" )
            cmd.setUserData( QVariant.fromValue( &mCommands ) )
            cmd.setProject( self )
            cmd.setSkipOnError( False )
            addCommand( cmd, "mBuilder" )

            # lrelease command
            cmd = pCommand()
            cmd.setText( tr( "lrelease" ) )
            cmd.setCommand( version.lrelease() )
            cmd.setArguments( "\"$cp$\"" )
            cmd.setWorkingDirectory( "$cpp$" )
            cmd.setUserData( QVariant.fromValue( &mCommands ) )
            cmd.setProject( self )
            cmd.setSkipOnError( False )
            addCommand( cmd, "mBuilder" )

            # rebuild debug
            if  haveDebug or haveDebugRelease :
                cmd = cmdBuild
                cmd.setText( tr( "Rebuild Debug" ) )
                cmd.setCommand( ( QStringList() << tr( "QMake" ) << tr( "Distclean Debug" ) << tr( "QMake" ) << tr( "Build Debug" ) ).join( ";" ) )
                cmd.setArguments( QString() )
                addCommand( cmd, "mBuilder/mRebuild" )


            # rebuild release
            if  haveRelease or haveDebugRelease :
                cmd = cmdBuild
                cmd.setText( tr( "Rebuild Release" ) )
                cmd.setCommand( ( QStringList() << tr( "QMake" ) << tr( "Distclean Release" ) << tr( "QMake" ) << tr( "Build Release" ) ).join( ";" ) )
                cmd.setArguments( QString() )
                addCommand( cmd, "mBuilder/mRebuild" )


            # rebuild all
            if  haveDebugRelease :
                cmd = cmdBuild
                cmd.setText( tr( "Rebuild All" ) )
                cmd.setCommand( ( QStringList() << tr( "QMake" ) << tr( "Distclean All" ) << tr( "QMake" ) << tr( "Build All" ) ).join( ";" ) )
                cmd.setArguments( QString() )
                addCommand( cmd, "mBuilder/mRebuild" )


        elif  projectSettingsValue( "SHOW_QT_VERSION_WARNING", "1" ) == "1" :
            setProjectSettingsValue( "SHOW_QT_VERSION_WARNING", "0" )
            topLevelProject().save()
            MonkeyCore.messageManager().appendMessage( tr( "Some actions can't be created, there is no default Qt version setted, go in your project settings ( %1 ) to fix self." ).arg( displayText() ) )


        # execute debug
        if  haveDebug or haveDebugRelease :
             debugTarget = targetFilePath( False, XUPProjectItem.DebugTarget, XUPProjectItem.CurrentPlatform )

            cmd = cmdBuild
            cmd.targetExecution().isActive = True
            cmd.targetExecution().targetType = XUPProjectItem.DebugTarget
            cmd.targetExecution().platformType = XUPProjectItem.CurrentPlatform
            cmd.setText( tr( "Execute Debug" ) )
            cmd.setCommand( debugTarget )
            cmd.setArguments( QString() )
            cmd.setWorkingDirectory( QFileInfo( debugTarget ).absolutePath() )
            cmd.setParsers( QStringList() )
            cmd.setTryAllParsers( False )
            addCommand( cmd, "mBuilder/mExecute" )


        # execute release
        if  haveRelease or haveDebugRelease :
             releaseTarget = targetFilePath( False, XUPProjectItem.ReleaseTarget, XUPProjectItem.CurrentPlatform )

            cmd = cmdBuild
            cmd.targetExecution().isActive = True
            cmd.targetExecution().targetType = XUPProjectItem.ReleaseTarget
            cmd.targetExecution().platformType = XUPProjectItem.CurrentPlatform
            cmd.setText( tr( "Execute Release" ) )
            cmd.setCommand( releaseTarget )
            cmd.setArguments( QString() )
            cmd.setWorkingDirectory( QFileInfo( releaseTarget ).absolutePath() )
            cmd.setParsers( QStringList() )
            cmd.setTryAllParsers( False )
            addCommand( cmd, "mBuilder/mExecute" )


        if  not ( haveDebug or haveDebugRelease ) and not ( haveRelease or haveDebugRelease ) :
             defaultTarget = targetFilePath( False, XUPProjectItem.DefaultTarget, XUPProjectItem.CurrentPlatform )

            cmd = cmdBuild
            cmd.targetExecution().isActive = True
            cmd.targetExecution().targetType = XUPProjectItem.DefaultTarget
            cmd.targetExecution().platformType = XUPProjectItem.CurrentPlatform
            cmd.setText( tr( "Execute" ) )
            cmd.setCommand( defaultTarget )
            cmd.setArguments( QString() )
            cmd.setWorkingDirectory( QFileInfo( defaultTarget ).absolutePath() )
            cmd.setParsers( QStringList() )
            cmd.setTryAllParsers( False )
            addCommand( cmd, "mBuilder/mExecute" )



    # install defaults commands
    XUPProjectItem.installCommands()

