#ifndef QTVERSIONMANAGER_H
#define QTVERSIONMANAGER_H

#include <objects/pSettings.h>

#include <QFile>
#include <QDomDocument>

class MkSShellInterpreter;

struct QtVersion
{
	QtVersion() { Default = false; HasQt4Suffix = false; }
	QtVersion( const QString& version, const QString& path, bool def, const QString& qmakeSpec, const QString& qmakeParams, bool haveSuffixe )
	{ Version = version; Path = path; Default = def; QMakeSpec = qmakeSpec; QMakeParameters = qmakeParams; HasQt4Suffix = haveSuffixe; }

	quint32 hash() const
	{ return qHash( QString( "%1/%2" ).arg( Path ).arg( QMakeSpec )/*.arg( QMakeParameters ).arg( HasQt4Suffix )*/ ); }

	bool isValid() const
	{ return !Version.isEmpty() && !Path.isEmpty() && QFile::exists( Path ); }

	bool isSystem() const
	{ return Version.startsWith( "Qt System", Qt::CaseInsensitive ); }

	QString qmake() const
	{ return QString( "%1/bin/qmake%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString qmakeSpec() const
	{ return ( QMakeSpec != "default" && !QMakeSpec.isEmpty() ) ? QString( "-spec %1" ).arg( QMakeSpec ) : QString(); }
	QString qmakeParameters() const
	{ return qmakeSpec().append( " " +QMakeParameters ); }
	QString lupdate() const
	{ return QString( "%1/bin/lupdate%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString lrelease() const
	{ return QString( "%1/bin/lrelease%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString designer() const
	{ return QString( "%1/bin/designer%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString assistant() const
	{ return QString( "%1/bin/assistant%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString linguist() const
	{ return QString( "%1/bin/linguist%2" ).arg( Path ).arg( binarySuffixe() ); }
	QString binarySuffixe() const
	{ return HasQt4Suffix ? QString( "-qt4" ) : QString::null; }

	QString toXml() const
	{
		QDomDocument document( "Qt Version Definition" );
		QDomElement rootElement = document.createElement( "QtVersion" );
		QDomElement versionElement = document.createElement( "Version" );
		QDomElement pathElement = document.createElement( "Path" );
		QDomElement defaultElement = document.createElement( "Default" );
		QDomElement qmakeSpecElement = document.createElement( "QMakeSpec" );
		QDomElement qmakeParametersElement = document.createElement( "QMakeParameters" );
		QDomElement hasQt4SuffixElement = document.createElement( "HasQt4Suffix" );

		versionElement.setAttribute( "value", Version );
		pathElement.setAttribute( "value", Path );
		defaultElement.setAttribute( "value", Default );
		qmakeSpecElement.setAttribute( "value", QMakeSpec );
		qmakeParametersElement.setAttribute( "value", QMakeParameters );
		hasQt4SuffixElement.setAttribute( "value", HasQt4Suffix );

		document.appendChild( rootElement );
		rootElement.appendChild( versionElement );
		rootElement.appendChild( pathElement );
		rootElement.appendChild( defaultElement );
		rootElement.appendChild( qmakeSpecElement );
		rootElement.appendChild( qmakeParametersElement );
		rootElement.appendChild( hasQt4SuffixElement );

		return document.toString( 4 );
	}

	bool operator==( const QtVersion& other ) const
	{
		return Version == other.Version && Path == other.Path
			&& QMakeSpec == other.QMakeSpec && QMakeParameters == other.QMakeParameters
			&& HasQt4Suffix == other.HasQt4Suffix;
	}

	bool operator!=( const QtVersion& other ) const
	{ return !operator==( other ); }

	QString Version;
	QString Path;
	bool Default;
	QString QMakeSpec;
	QString QMakeParameters;
	bool HasQt4Suffix;
};

struct QtItem
{
	QtItem() {}
	QtItem( const QString& t, const QString& v, const QString& s, const QString& h = QString::null )
		: Text( t ), Value( v ), Variable( s ), Help( h ) {}

	bool operator==( const QtItem& o ) { return Text == o.Text && Value == o.Value && Variable == o.Variable && Help == o.Help; }
	bool operator!=( const QtItem& o ) { return !operator==( o ); }

	QString Text;
	QString Value;
	QString Variable;
	QString Help;
};

typedef QList<QtVersion> QtVersionList;
typedef QList<QtItem> QtItemList;

Q_DECLARE_METATYPE( QtVersion );
Q_DECLARE_METATYPE( QtVersionList );
Q_DECLARE_METATYPE( QtItem );
Q_DECLARE_METATYPE( QtItemList );

class QtVersionManager : public pSettings
{
	Q_OBJECT

public:
	QtVersionManager( QObject* owner = 0 );
	~QtVersionManager();

	QtVersionList versions() const;
	void setVersions( const QtVersionList& versions );

	QtVersion defaultVersion() const;
	QtVersion version( const QString& versionString ) const;

	QtItemList defaultModules() const;
	QtItemList modules() const;
	void setModules( const QtItemList& modules );

	QtItemList defaultConfigurations() const;
	QtItemList configurations() const;
	void setConfigurations( const QtItemList& configurations );

protected:
	static const QString mQtVersionKey;
	static const QString mQtModuleKey;
	static const QString mQtConfigurationKey;
	static const QRegExp mQtVersionRegExp;
	static const QRegExp mQtQMakeRegExp;
	static const QRegExp mQtUninstallRegExp;

	QStringList possibleQtPaths() const;
	QtVersionList getQtVersions( const QStringList& paths ) const;
	void synchronizeVersions();

	// interpreter handling
	void initializeInterpreterCommands( bool initialize );
	static QString commandInterpreter( const QString& command, const QStringList& arguments, int* result, MkSShellInterpreter* interpreter, void* data );
};

#endif // QTVERSIONMANAGER_H
