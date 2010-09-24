#include "QtVersionManager.h"

#include <coremanager/MonkeyCore.h>
#include <shellmanager/MkSShellInterpreter.h>

#include <QProcess>
#include <QDir>
#include <QDebug>

 QString QtVersionManager.mQtVersionKey = "Versions"
 QString QtVersionManager.mQtModuleKey = "Modules"
 QString QtVersionManager.mQtConfigurationKey = "Configurations"
 QRegExp QtVersionManager.mQtVersionRegExp( "4\\.[\\d\\w-_\\.]+" )
 QRegExp QtVersionManager.mQtQMakeRegExp( QString( "QMake version (?:[\\d\\w-_\\.]+)(?:\\r|\\n|\\r\\n)Using Qt version (%1) in (.*)" ).arg( QtVersionManager.mQtVersionRegExp.pattern() ) )
 QRegExp QtVersionManager.mQtUninstallRegExp( "Qt (?:OpenSource|SDK|Commercial) .*" )

QtVersionManager.QtVersionManager( QObject* owner )
        : pSettings( owner, "QtVersions", "1.0.0" )
    synchronizeVersions()
    initializeInterpreterCommands( True )


QtVersionManager.~QtVersionManager()
    initializeInterpreterCommands( False )


def versions(self):
    _this = const_cast<QtVersionManager*>( self )
    QtVersionList items
     count = _this.beginReadArray( mQtVersionKey )

    for ( i = 0; i < count; i++ )
        _this.setArrayIndex( i )

        items << QtVersion( value( "Version" ).toString(),
                            value( "Path" ).toString(),
                            value( "Default" ).toBool(),
                            value( "QMakeSpec" ).toString(),
                            value( "QMakeParameters" ).toString(),
                            value( "HasQt4Suffixe" ).toBool() )


    _this.endArray()
    return items


def setVersions(self, versions ):
    beginWriteArray( mQtVersionKey )

    for ( i = 0; i < versions.count(); i++ )
        setArrayIndex( i )
         version = versions.at( i )

        setValue( "Version", version.Version )
        setValue( "Path", version.Path )
        setValue( "Default", version.Default )
        setValue( "QMakeSpec", version.QMakeSpec )
        setValue( "QMakeParameters", version.QMakeParameters )
        setValue( "HasQt4Suffixe", version.HasQt4Suffix )


    endArray()


def defaultVersion(self):
     versions = self.versions()

    for version in versions:
        if  version.Default :
            return version



    return versions.value( 0 )


def version(self, versionString ):
    for version in versions():
        if  version.Version == versionString :
            return version



    return defaultVersion()


def defaultModules(self):
    return QtItemList()
           << QtItem( "QtCore", "core", "QT", "Add support for Qt Core classes" )
           << QtItem( "QtGui", "gui", "QT", "Add support for Qt Gui classes" )
           << QtItem( "QtMultimedia", "multimedia", "QT", "Add support for Qt Multimedia classes" )
           << QtItem( "QtNetwork", "network", "QT", "Add support for Qt Network classes" )
           << QtItem( "QtOpenGL", "opengl", "QT", "Add support for Qt OpenGL classes" )
           << QtItem( "QtScript", "script", "QT", "Add support for Qt Script classes" )
           << QtItem( "QtScriptTools", "scripttools", "QT", "Add support for Qt Script Tools classes" )
           << QtItem( "QtSql", "sql", "QT", "Add support for Qt Sql classes" )
           << QtItem( "QtSvg", "svg", "QT", "Add support for Qt Svg classes" )
           << QtItem( "QtWebKit", "webkit", "QT", "Add support for Qt WebKit classes" )
           << QtItem( "QtXml", "xml", "QT", "Add support for Qt Xml classes" )
           << QtItem( "QtXmlPatterns", "xmlpatterns", "QT", "Add support for Qt Xml Patterns classes (XQuery & XPath)" )
           << QtItem( "Phonon", "phonon", "QT", "Add support for Qt Xml Patterns classes (XQuery & XPath)" )
           << QtItem( "QtDBus", "dbus", "QT", "Add support for Qt DBus classes (unix like only)" )
           << QtItem( "Qt3Support", "qt3support", "QT", "Add support for Qt Qt3Support classes" )

    #QtOpenVG Module


def modules(self):
    _this = const_cast<QtVersionManager*>( self )
    modules = defaultModules()
     count = _this.beginReadArray( mQtModuleKey )

    for ( i = 0; i < count; i++ )
        _this.setArrayIndex( i )

         QtItem module( value( "Text" ).toString(),
                             value( "Value" ).toString(),
                             value( "Variable" ).toString(),
                             value( "Help" ).toString() )

        if  not modules.contains( module ) :
            modules << module



    _this.endArray()
    return modules


def setModules(self, modules ):
    beginWriteArray( mQtModuleKey )

    for ( i = 0; i < modules.count(); i++ )
        setArrayIndex( i )
         module = modules.at( i )

        setValue( "Text", module.Text )
        setValue( "Value", module.Value )
        setValue( "Variable", module.Variable )
        setValue( "Help", module.Help )


    endArray()


def defaultConfigurations(self):
    return QtItemList()
           << QtItem( "rtti", "rtti", "CONFIG", "RTTI support is enabled." )
           << QtItem( "stl", "stl", "CONFIG", "STL support is enabled." )
           << QtItem( "exceptions", "exceptions", "CONFIG", "Exception support is enabled." )
           << QtItem( "thread", "thread", "CONFIG", "The target is a multi-threaded application or library. The proper defines and compiler flags will automatically be added to the project." )
           << QtItem( "no_lflags_merge", "no_lflags_merge", "CONFIG", "Ensures that the list of libraries stored in the LIBS variable is not reduced to a list of unique values before it is used." )
           << QtItem( "LIB ONLY", QString.null, QString.null, "Options for LIB template only" )
           << QtItem( "dll", "dll", "CONFIG", "The target is a shared object/DLL.The proper include paths, flags and libraries will automatically be added to the project." )
           << QtItem( "staticlib", "staticlib", "CONFIG", "The target is a static library (lib only). The proper compiler flags will automatically be added to the project." )
           << QtItem( "plugin", "plugin", "CONFIG", "The target is a plugin (lib only). This enables dll as well." )
           << QtItem( "X11 ONLY", QString.null, QString.null, "Options for X11 only" )
           << QtItem( "x11", "x11", "CONFIG", "The target is a X11 application or library. The proper include paths and libraries will automatically be added to the project." )
           << QtItem( "MAC OS X ONLY", QString.null, QString.null, "Options for Mac OS X only" )
           << QtItem( "ppc", "ppc", "CONFIG", "Builds a PowerPC binary." )
           << QtItem( "ppc64", "ppc64", "CONFIG", "Builds a 64 bits PowerPC binary." )
           << QtItem( "x86", "x86", "CONFIG", "Builds an i386 compatible binary." )
           << QtItem( "x86_64", "x86_64", "CONFIG", "Builds an x86 64 bits compatible binary." )
           << QtItem( "app_bundle", "app_bundle", "CONFIG", "Puts the executable into a bundle (self is the default)." )
           << QtItem( "lib_bundle", "lib_bundle", "CONFIG", "Puts the library into a library bundle." )
           << QtItem( "WINDOWS ONLY", QString.null, QString.null, "Options for Windows only" )
           << QtItem( "windows", "windows", "CONFIG", "The target is a Win32 window application (app only). The proper include paths, flags and libraries will automatically be added to the project." )
           << QtItem( "console", "console", "CONFIG", "The target is a Win32 console application (app only). The proper include paths, flags and libraries will automatically be added to the project." )
           << QtItem( "flat", "flat", "CONFIG", "When using the vcapp template self will put all the source files into the source group and the header files into the header group regardless of what directory they reside in. Turning self option off will group the files within the source/header group depending on the directory they reside. This is turned on by default." )
           << QtItem( "embed_manifest_exe", "embed_manifest_dll", "CONFIG", "Embeds a manifest file in the DLL created as part of an application project." )
           << QtItem( "embed_manifest_dll", "embed_manifest_dll", "CONFIG", "Embeds a manifest file in the DLL created as part of an library project." )
           << QtItem( "ACTIVEQT ONLY", QString.null, QString.null, "Option for Windows/Active Qt only" )
           << QtItem( "qaxserver_no_postlink", "qaxserver_no_postlink", "CONFIG", "No help available" )
           << QtItem( "Qt ONLY", QString.null, QString.null, "Options for Qt only" )
           << QtItem( "ordered", "ordered", "CONFIG", "Sub project are built in defined order." )
           << QtItem( "qt", "qt", "CONFIG", "The target is a Qt application/library and requires the Qt library and header files. The proper include and library paths for the Qt library will automatically be added to the project. This is defined by default, can be fine-tuned with the QT variable." )
           << QtItem( "resources", "resources", "CONFIG", "Configures qmake to run rcc on the content of RESOURCES if defined." )
           << QtItem( "uic3", "uic3", "CONFIG", "Configures qmake to run uic3 on the content of FORMS3 if defined; otherwise the contents of FORMS will be processed instead." )
           << QtItem( "QtDesigner", "designer", "CONFIG", "Add support for Qt Designer classes" )
           << QtItem( "QtUiTools", "uitools", "CONFIG", "Add support for Qt UiTools classes" )
           << QtItem( "QtHelp", "help", "CONFIG", "Add support for Qt Help classes" )
           << QtItem( "QtAssistant", "assistant", "CONFIG", "Add support for Qt Assistant classes" )
           << QtItem( "QtTest", "qtestlib", "CONFIG", "Add support for Qt Test classes" )
           << QtItem( "QAxContainer", "qaxcontainer", "CONFIG", "Add support for QAxContainer classes (windows only)" )
           << QtItem( "QAxServer", "qaxserver", "CONFIG", "Add support for QAxServer classes (windows only)" )


def configurations(self):
    _this = const_cast<QtVersionManager*>( self )
    configurations = defaultConfigurations()
     count = _this.beginReadArray( mQtConfigurationKey )

    for ( i = 0; i < count; i++ )
        _this.setArrayIndex( i )

         QtItem configuration( value( "Text" ).toString(),
                                    value( "Value" ).toString(),
                                    value( "Variable" ).toString(),
                                    value( "Help" ).toString() )

        if  not configurations.contains( configuration ) :
            configurations << configuration



    _this.endArray()
    return configurations


def setConfigurations(self, configurations ):
    beginWriteArray( mQtConfigurationKey )

    for ( i = 0; i < configurations.count(); i++ )
        setArrayIndex( i )
         configuration = configurations.at( i )

        setValue( "Text", configuration.Text )
        setValue( "Value", configuration.Value )
        setValue( "Variable", configuration.Variable )
        setValue( "Help", configuration.Help )


    endArray()


#if defined( Q_OS_WIN )
def possibleQtPaths(self):
    QSet<QString> paths

    paths << QString.null; # for qmake available in PATH

    # get users uninstall
    settings = QSettings( QSettings.UserScope, "Microsoft", "Windows" )
    settings.beginGroup( "CurrentVersion/Uninstall" )

    for key in settings.childGroups():
        path = settings.value( QString( "%1/MINGW_INSTDIR" ).arg( key ) ).toString()

        if  path.isEmpty() :
            path = settings.value( QString( "%1/QTSDK_INSTDIR" ).arg( key ) ).toString()

            if  not path.isEmpty() :
                path.append( "/qt" )



        if  not path.isEmpty() :
            paths << path



    # get system uninstalls
    delete settings
    settings = QSettings( QSettings.SystemScope, "Microsoft", "Windows" )
    settings.beginGroup( "CurrentVersion/Uninstall" )

    for key in settings.childGroups():
        path = settings.value( QString( "%1/MINGW_INSTDIR" ).arg( key ) ).toString()

        if  path.isEmpty() :
            path = settings.value( QString( "%1/QTSDK_INSTDIR" ).arg( key ) ).toString()

            if  not path.isEmpty() :
                path.append( "/qt" )



        if  not path.isEmpty() and not paths.contains( path ) :
            paths << path



    delete settings
    return paths.toList()

#elif defined( Q_OS_MAC )
def possibleQtPaths(self):
    return QStringList() << QString.null; # for qmake available in PATH

#else:
def possibleQtPaths(self):
    return QStringList() << QString.null; # for qmake available in PATH

#endif

def getQtVersions(self, paths ):
    QtVersionList versions
    hasDefaultVersion = defaultVersion().isValid()

    for path in paths:
        QtVersion sysQt
        QProcess process
        QString datas
        hasSuffix = True
        prefix = path.isEmpty() ? QString.null : path +"/bin/"

        # trying with -qt4 suffix first
        process.start( QString( "\"%1qmake-qt4\" -v" ).arg( prefix ) )
        process.waitForFinished()
        datas = QString.fromLocal8Bit( process.readAll() ).trimmed()

        # else without suffix
        if  not mQtQMakeRegExp.exactMatch( datas ) :
            process.start( QString( "\"%1qmake\" -v" ).arg( prefix ) )
            process.waitForFinished()
            datas = QString.fromLocal8Bit( process.readAll() ).trimmed()
            hasSuffix = False


        # if matching output add version
        if  mQtQMakeRegExp.exactMatch( datas ) :
             version = mQtQMakeRegExp.cap( 1 )
             path = QDir.toNativeSeparators( mQtQMakeRegExp.cap( 2 ).replace( "\\", "/" ).section( '/', 0, -2 ) )

            sysQt.Version = QString( "Qt System (%1)" ).arg( version )
            sysQt.Path = path
            sysQt.Default = hasDefaultVersion ? False : True
            sysQt.QMakeSpec = QString.null
            sysQt.QMakeParameters = "\"$cp$\""
            sysQt.HasQt4Suffix = hasSuffix

            if  not hasDefaultVersion :
                hasDefaultVersion = True


            versions << sysQt



    return versions


def synchronizeVersions(self):
     paths = possibleQtPaths()
     newVersions = getQtVersions( paths )
     versions = self.versions()
    QMap<quint32, items

    # add existing items
    for ( i = 0; i < versions.count(); i++ )
         version = versions.at( i )

        items[ version.hash() ] = version


    # add ones if needed
    for newVersion in newVersions:
        if  items.contains( newVersion.hash() ) :
             v = items[ newVersion.hash() ]

            if  v.Version == newVersion.Version :
                continue



        items[ newVersion.hash() ] = newVersion


    # update qt versions
    setVersions( items.values() )


def initializeInterpreterCommands(self, initialize ):
    if  initialize :
        # register command
        help = MkSShellInterpreter.tr(
                           "This command manage the Qt versions, usage:\n"
                           "\tqtversion xml [version]"
                       )

        MonkeyCore.interpreter().addCommandImplementation( "qtversion", QtVersionManager.commandInterpreter, help, self )

    else:
        MonkeyCore.interpreter().removeCommandImplementation( "qtversion" )



def commandInterpreter(self, command, _arguments, result, interpreter, data ):
    Q_UNUSED( command )
    Q_UNUSED( interpreter )
    manager = static_cast<QtVersionManager*>( data )
    arguments = _arguments
     allowedOperations = QStringList( "xml" )

    if  result :
        *result = MkSShellInterpreter.NoError


    if  arguments.isEmpty() :
        if  result :
            *result = MkSShellInterpreter.InvalidCommand


        return MkSShellInterpreter.tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) )


     operation = arguments.takeFirst()

    if  not allowedOperations.contains( operation ) :
        if  result :
            *result = MkSShellInterpreter.InvalidCommand


        return MkSShellInterpreter.tr( "Unknown operation: '%1'." ).arg( operation )


    if  operation == "xml" :
        if  arguments.count() != 1 :
            if  result :
                *result = MkSShellInterpreter.InvalidCommand


            return MkSShellInterpreter.tr( "'set' operation take 1 argument, %1 given." ).arg( arguments.count() )


         version = arguments.at( 0 )

        return manager.version( version ).toXml()


    return QString.null


