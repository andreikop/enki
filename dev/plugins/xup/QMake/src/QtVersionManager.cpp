#include "QtVersionManager.h"

#include <coremanager/MonkeyCore.h>
#include <shellmanager/MkSShellInterpreter.h>

#include <QProcess>
#include <QDir>
#include <QDebug>

const QString QtVersionManager::mQtVersionKey = "Versions";
const QString QtVersionManager::mQtModuleKey = "Modules";
const QString QtVersionManager::mQtConfigurationKey = "Configurations";
const QRegExp QtVersionManager::mQtVersionRegExp( "4\\.[\\d\\w-_\\.]+" );
const QRegExp QtVersionManager::mQtQMakeRegExp( QString( "QMake version (?:[\\d\\w-_\\.]+)(?:\\r|\\n|\\r\\n)Using Qt version (%1) in (.*)" ).arg( QtVersionManager::mQtVersionRegExp.pattern() ) );
const QRegExp QtVersionManager::mQtUninstallRegExp( "Qt (?:OpenSource|SDK|Commercial) .*" );

QtVersionManager::QtVersionManager( QObject* owner )
	: pSettings( owner, "QtVersions", "1.0.0" )
{
	synchronizeVersions();
	initializeInterpreterCommands( true );
}

QtVersionManager::~QtVersionManager()
{
	initializeInterpreterCommands( false );
}

QtVersionList QtVersionManager::versions() const
{
	QtVersionManager* _this = const_cast<QtVersionManager*>( this );
	QtVersionList items;
	const int count = _this->beginReadArray( mQtVersionKey );

	for ( int i = 0; i < count; i++ )
	{
		_this->setArrayIndex( i );

		items << QtVersion( value( "Version" ).toString(),
							value( "Path" ).toString(),
							value( "Default" ).toBool(),
							value( "QMakeSpec" ).toString(),
							value( "QMakeParameters" ).toString(),
							value( "HasQt4Suffixe" ).toBool() );
	}

	_this->endArray();
	return items;
}

void QtVersionManager::setVersions( const QtVersionList& versions )
{
	beginWriteArray( mQtVersionKey );

	for ( int i = 0; i < versions.count(); i++ )
	{
		setArrayIndex( i );
		const QtVersion& version = versions.at( i );

		setValue( "Version", version.Version );
		setValue( "Path", version.Path );
		setValue( "Default", version.Default );
		setValue( "QMakeSpec", version.QMakeSpec );
		setValue( "QMakeParameters", version.QMakeParameters );
		setValue( "HasQt4Suffixe", version.HasQt4Suffix );
	}

	endArray();
}

QtVersion QtVersionManager::defaultVersion() const
{
	const QtVersionList versions = this->versions();

	foreach ( const QtVersion& version, versions )
	{
		if ( version.Default )
		{
			return version;
		}
	}

	return versions.value( 0 );
}

QtVersion QtVersionManager::version( const QString& versionString ) const
{
	foreach ( const QtVersion& version, versions() )
	{
		if ( version.Version == versionString )
		{
			return version;
		}
	}

	return defaultVersion();
}

QtItemList QtVersionManager::defaultModules() const
{
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
		<< QtItem( "Qt3Support", "qt3support", "QT", "Add support for Qt Qt3Support classes" );

	//QtOpenVG Module
}

QtItemList QtVersionManager::modules() const
{
	QtVersionManager* _this = const_cast<QtVersionManager*>( this );
	QtItemList modules = defaultModules();
	const int count = _this->beginReadArray( mQtModuleKey );

	for ( int i = 0; i < count; i++ )
	{
		_this->setArrayIndex( i );

		const QtItem module( value( "Text" ).toString(),
						value( "Value" ).toString(),
						value( "Variable" ).toString(),
						value( "Help" ).toString() );

		if ( !modules.contains( module ) )
		{
			modules << module;
		}
	}

	_this->endArray();
	return modules;
}

void QtVersionManager::setModules( const QtItemList& modules )
{
	beginWriteArray( mQtModuleKey );

	for ( int i = 0; i < modules.count(); i++ )
	{
		setArrayIndex( i );
		const QtItem& module = modules.at( i );

		setValue( "Text", module.Text );
		setValue( "Value", module.Value );
		setValue( "Variable", module.Variable );
		setValue( "Help", module.Help );
	}

	endArray();
}

QtItemList QtVersionManager::defaultConfigurations() const
{
	return QtItemList()
		<< QtItem( "rtti", "rtti", "CONFIG", "RTTI support is enabled." )
		<< QtItem( "stl", "stl", "CONFIG", "STL support is enabled." )
		<< QtItem( "exceptions", "exceptions", "CONFIG", "Exception support is enabled." )
		<< QtItem( "thread", "thread", "CONFIG", "The target is a multi-threaded application or library. The proper defines and compiler flags will automatically be added to the project." )
		<< QtItem( "no_lflags_merge", "no_lflags_merge", "CONFIG", "Ensures that the list of libraries stored in the LIBS variable is not reduced to a list of unique values before it is used." )
		<< QtItem( "LIB ONLY", QString::null, QString::null, "Options for LIB template only" )
		<< QtItem( "dll", "dll", "CONFIG", "The target is a shared object/DLL.The proper include paths, compiler flags and libraries will automatically be added to the project." )
		<< QtItem( "staticlib", "staticlib", "CONFIG", "The target is a static library (lib only). The proper compiler flags will automatically be added to the project." )
		<< QtItem( "plugin", "plugin", "CONFIG", "The target is a plugin (lib only). This enables dll as well." )
		<< QtItem( "X11 ONLY", QString::null, QString::null, "Options for X11 only" )
		<< QtItem( "x11", "x11", "CONFIG", "The target is a X11 application or library. The proper include paths and libraries will automatically be added to the project." )
		<< QtItem( "MAC OS X ONLY", QString::null, QString::null, "Options for Mac OS X only" )
		<< QtItem( "ppc", "ppc", "CONFIG", "Builds a PowerPC binary." )
		<< QtItem( "ppc64", "ppc64", "CONFIG", "Builds a 64 bits PowerPC binary." )
		<< QtItem( "x86", "x86", "CONFIG", "Builds an i386 compatible binary." )
		<< QtItem( "x86_64", "x86_64", "CONFIG", "Builds an x86 64 bits compatible binary." )
		<< QtItem( "app_bundle", "app_bundle", "CONFIG", "Puts the executable into a bundle (this is the default)." )
		<< QtItem( "lib_bundle", "lib_bundle", "CONFIG", "Puts the library into a library bundle." )
		<< QtItem( "WINDOWS ONLY", QString::null, QString::null, "Options for Windows only" )
		<< QtItem( "windows", "windows", "CONFIG", "The target is a Win32 window application (app only). The proper include paths,compiler flags and libraries will automatically be added to the project." )
		<< QtItem( "console", "console", "CONFIG", "The target is a Win32 console application (app only). The proper include paths, compiler flags and libraries will automatically be added to the project." )
		<< QtItem( "flat", "flat", "CONFIG", "When using the vcapp template this will put all the source files into the source group and the header files into the header group regardless of what directory they reside in. Turning this option off will group the files within the source/header group depending on the directory they reside. This is turned on by default." )
		<< QtItem( "embed_manifest_exe", "embed_manifest_dll", "CONFIG", "Embeds a manifest file in the DLL created as part of an application project." )
		<< QtItem( "embed_manifest_dll", "embed_manifest_dll", "CONFIG", "Embeds a manifest file in the DLL created as part of an library project." )
		<< QtItem( "ACTIVEQT ONLY", QString::null, QString::null, "Option for Windows/Active Qt only" )
		<< QtItem( "qaxserver_no_postlink", "qaxserver_no_postlink", "CONFIG", "No help available" )
		<< QtItem( "Qt ONLY", QString::null, QString::null, "Options for Qt only" )
		<< QtItem( "ordered", "ordered", "CONFIG", "Sub project are built in defined order." )
		<< QtItem( "qt", "qt", "CONFIG", "The target is a Qt application/library and requires the Qt library and header files. The proper include and library paths for the Qt library will automatically be added to the project. This is defined by default, and can be fine-tuned with the QT variable." )
		<< QtItem( "resources", "resources", "CONFIG", "Configures qmake to run rcc on the content of RESOURCES if defined." )
		<< QtItem( "uic3", "uic3", "CONFIG", "Configures qmake to run uic3 on the content of FORMS3 if defined; otherwise the contents of FORMS will be processed instead." )
		<< QtItem( "QtDesigner", "designer", "CONFIG", "Add support for Qt Designer classes" )
		<< QtItem( "QtUiTools", "uitools", "CONFIG", "Add support for Qt UiTools classes" )
		<< QtItem( "QtHelp", "help", "CONFIG", "Add support for Qt Help classes" )
		<< QtItem( "QtAssistant", "assistant", "CONFIG", "Add support for Qt Assistant classes" )
		<< QtItem( "QtTest", "qtestlib", "CONFIG", "Add support for Qt Test classes" )
		<< QtItem( "QAxContainer", "qaxcontainer", "CONFIG", "Add support for QAxContainer classes (windows only)" )
		<< QtItem( "QAxServer", "qaxserver", "CONFIG", "Add support for QAxServer classes (windows only)" );
}

QtItemList QtVersionManager::configurations() const
{
	QtVersionManager* _this = const_cast<QtVersionManager*>( this );
	QtItemList configurations = defaultConfigurations();
	const int count = _this->beginReadArray( mQtConfigurationKey );

	for ( int i = 0; i < count; i++ )
	{
		_this->setArrayIndex( i );

		const QtItem configuration( value( "Text" ).toString(),
									value( "Value" ).toString(),
									value( "Variable" ).toString(),
									value( "Help" ).toString() );

		if ( !configurations.contains( configuration ) )
		{
			configurations << configuration;
		}
	}

	_this->endArray();
	return configurations;
}

void QtVersionManager::setConfigurations( const QtItemList& configurations )
{
	beginWriteArray( mQtConfigurationKey );

	for ( int i = 0; i < configurations.count(); i++ )
	{
		setArrayIndex( i );
		const QtItem& configuration = configurations.at( i );

		setValue( "Text", configuration.Text );
		setValue( "Value", configuration.Value );
		setValue( "Variable", configuration.Variable );
		setValue( "Help", configuration.Help );
	}

	endArray();
}

#if defined( Q_OS_WIN )
QStringList QtVersionManager::possibleQtPaths() const
{
	QSet<QString> paths;

	paths << QString::null; // for qmake available in PATH

	// get users uninstall
	QSettings* settings = new QSettings( QSettings::UserScope, "Microsoft", "Windows" );
	settings->beginGroup( "CurrentVersion/Uninstall" );

	foreach ( const QString& key, settings->childGroups() )
	{
		QString path = settings->value( QString( "%1/MINGW_INSTDIR" ).arg( key ) ).toString();

		if ( path.isEmpty() )
		{
			path = settings->value( QString( "%1/QTSDK_INSTDIR" ).arg( key ) ).toString();

			if ( !path.isEmpty() )
			{
				path.append( "/qt" );
			}
		}

		if ( !path.isEmpty() )
		{
			paths << path;
		}
	}

	// get system uninstalls
	delete settings;
	settings = new QSettings( QSettings::SystemScope, "Microsoft", "Windows" );
	settings->beginGroup( "CurrentVersion/Uninstall" );

	foreach ( const QString& key, settings->childGroups() )
	{
		QString path = settings->value( QString( "%1/MINGW_INSTDIR" ).arg( key ) ).toString();

		if ( path.isEmpty() )
		{
			path = settings->value( QString( "%1/QTSDK_INSTDIR" ).arg( key ) ).toString();

			if ( !path.isEmpty() )
			{
				path.append( "/qt" );
			}
		}

		if ( !path.isEmpty() && !paths.contains( path ) )
		{
			paths << path;
		}
	}

	delete settings;
	return paths.toList();
}
#elif defined( Q_OS_MAC )
QStringList QtVersionManager::possibleQtPaths() const
{
	return QStringList() << QString::null; // for qmake available in PATH
}
#else
QStringList QtVersionManager::possibleQtPaths() const
{
	return QStringList() << QString::null; // for qmake available in PATH
}
#endif

QtVersionList QtVersionManager::getQtVersions( const QStringList& paths ) const
{
	QtVersionList versions;
	bool hasDefaultVersion = defaultVersion().isValid();

	foreach ( const QString& path, paths )
	{
		QtVersion sysQt;
		QProcess process;
		QString datas;
		bool hasSuffix = true;
		QString prefix = path.isEmpty() ? QString::null : path +"/bin/";

		// trying with -qt4 suffix first
		process.start( QString( "\"%1qmake-qt4\" -v" ).arg( prefix ) );
		process.waitForFinished();
		datas = QString::fromLocal8Bit( process.readAll() ).trimmed();

		// else without suffix
		if ( !mQtQMakeRegExp.exactMatch( datas ) )
		{
			process.start( QString( "\"%1qmake\" -v" ).arg( prefix ) );
			process.waitForFinished();
			datas = QString::fromLocal8Bit( process.readAll() ).trimmed();
			hasSuffix = false;
		}

		// if matching output add version
		if ( mQtQMakeRegExp.exactMatch( datas ) )
		{
			const QString version = mQtQMakeRegExp.cap( 1 );
			const QString path = QDir::toNativeSeparators( mQtQMakeRegExp.cap( 2 ).replace( "\\", "/" ).section( '/', 0, -2 ) );

			sysQt.Version = QString( "Qt System (%1)" ).arg( version );
			sysQt.Path = path;
			sysQt.Default = hasDefaultVersion ? false : true;
			sysQt.QMakeSpec = QString::null;
			sysQt.QMakeParameters = "\"$cp$\"";
			sysQt.HasQt4Suffix = hasSuffix;

			if ( !hasDefaultVersion )
			{
				hasDefaultVersion = true;
			}

			versions << sysQt;
		}
	}

	return versions;
}

void QtVersionManager::synchronizeVersions()
{
	const QStringList paths = possibleQtPaths();
	const QtVersionList newVersions = getQtVersions( paths );
	const QtVersionList versions = this->versions();
	QMap<quint32, QtVersion> items;

	// add existing items
	for ( int i = 0; i < versions.count(); i++ )
	{
		const QtVersion& version = versions.at( i );

		items[ version.hash() ] = version;
	}

	// add new ones if needed
	foreach ( const QtVersion& newVersion, newVersions )
	{
		if ( items.contains( newVersion.hash() ) )
		{
			const QtVersion& v = items[ newVersion.hash() ];

			if ( v.Version == newVersion.Version )
			{
				continue;
			}
		}

		items[ newVersion.hash() ] = newVersion;
	}

	// update qt versions
	setVersions( items.values() );
}

void QtVersionManager::initializeInterpreterCommands( bool initialize )
{
	if ( initialize ) {
		// register command
		QString help = MkSShellInterpreter::tr(
			"This command manage the Qt versions, usage:\n"
			"\tqtversion xml [version]"
		);

		MonkeyCore::interpreter()->addCommandImplementation( "qtversion", QtVersionManager::commandInterpreter, help, this );
	}
	else {
		MonkeyCore::interpreter()->removeCommandImplementation( "qtversion" );
	}
}

QString QtVersionManager::commandInterpreter( const QString& command, const QStringList& _arguments, int* result, MkSShellInterpreter* interpreter, void* data )
{
	Q_UNUSED( command );
	Q_UNUSED( interpreter );
	QtVersionManager* manager = static_cast<QtVersionManager*>( data );
	QStringList arguments = _arguments;
	const QStringList allowedOperations = QStringList( "xml" );

	if ( result ) {
		*result = MkSShellInterpreter::NoError;
	}

	if ( arguments.isEmpty() ) {
		if ( result ) {
			*result = MkSShellInterpreter::InvalidCommand;
		}

		return MkSShellInterpreter::tr( "Operation not defined. Available operations are: %1." ).arg( allowedOperations.join( ", " ) );
	}

	const QString operation = arguments.takeFirst();

	if ( !allowedOperations.contains( operation ) ) {
		if ( result ) {
			*result = MkSShellInterpreter::InvalidCommand;
		}

		return MkSShellInterpreter::tr( "Unknown operation: '%1'." ).arg( operation );
	}

	if ( operation == "xml" ) {
		if ( arguments.count() != 1 ) {
			if ( result ) {
				*result = MkSShellInterpreter::InvalidCommand;
			}

			return MkSShellInterpreter::tr( "'set' operation take 1 argument, %1 given." ).arg( arguments.count() );
		}

		const QString version = arguments.at( 0 );

		return manager->version( version ).toXml();
	}

	return QString::null;
}

