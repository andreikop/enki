#ifndef QTVERSIONMANAGER_H
#define QTVERSIONMANAGER_H

#include <objects/pSettings.h>

#include <QFile>
#include <QDomDocument>

class MkSShellInterpreter

struct QtVersion
    QtVersion()
        Default = False
        HasQt4Suffix = False

    QtVersion(  QString& version, path, def, qmakeSpec, qmakeParams, haveSuffixe )
        Version = version
        Path = path
        Default = def
        QMakeSpec = qmakeSpec
        QMakeParameters = qmakeParams
        HasQt4Suffix = haveSuffixe


    quint32 hash()
        return qHash( QString( "%1/%2" ).arg( Path ).arg( QMakeSpec )'''.arg( QMakeParameters ).arg( HasQt4Suffix )''' )


    bool isValid()
        return not Version.isEmpty() and not Path.isEmpty() and QFile.exists( Path )


    bool isSystem()
        return Version.startsWith( "Qt System", Qt.CaseInsensitive )


    QString qmake()
        return QString( "%1/bin/qmake%2" ).arg( Path ).arg( binarySuffixe() )

    QString qmakeSpec()
        return ( QMakeSpec != "default" and not QMakeSpec.isEmpty() ) ? QString( "-spec %1" ).arg( QMakeSpec ) : QString()

    QString qmakeParameters()
        return qmakeSpec().append( " " +QMakeParameters )

    QString lupdate()
        return QString( "%1/bin/lupdate%2" ).arg( Path ).arg( binarySuffixe() )

    QString lrelease()
        return QString( "%1/bin/lrelease%2" ).arg( Path ).arg( binarySuffixe() )

    QString designer()
        return QString( "%1/bin/designer%2" ).arg( Path ).arg( binarySuffixe() )

    QString assistant()
        return QString( "%1/bin/assistant%2" ).arg( Path ).arg( binarySuffixe() )

    QString linguist()
        return QString( "%1/bin/linguist%2" ).arg( Path ).arg( binarySuffixe() )

    QString binarySuffixe()
        return HasQt4Suffix ? QString( "-qt4" ) : QString.null


    QString toXml()
        QDomDocument document( "Qt Version Definition" )
        rootElement = document.createElement( "QtVersion" )
        versionElement = document.createElement( "Version" )
        pathElement = document.createElement( "Path" )
        defaultElement = document.createElement( "Default" )
        qmakeSpecElement = document.createElement( "QMakeSpec" )
        qmakeParametersElement = document.createElement( "QMakeParameters" )
        hasQt4SuffixElement = document.createElement( "HasQt4Suffix" )

        versionElement.setAttribute( "value", Version )
        pathElement.setAttribute( "value", Path )
        defaultElement.setAttribute( "value", Default )
        qmakeSpecElement.setAttribute( "value", QMakeSpec )
        qmakeParametersElement.setAttribute( "value", QMakeParameters )
        hasQt4SuffixElement.setAttribute( "value", HasQt4Suffix )

        document.appendChild( rootElement )
        rootElement.appendChild( versionElement )
        rootElement.appendChild( pathElement )
        rootElement.appendChild( defaultElement )
        rootElement.appendChild( qmakeSpecElement )
        rootElement.appendChild( qmakeParametersElement )
        rootElement.appendChild( hasQt4SuffixElement )

        return document.toString( 4 )


    bool operator==(  QtVersion& other )
        return Version == other.Version and Path == other.Path
               and QMakeSpec == other.QMakeSpec and QMakeParameters == other.QMakeParameters
               and HasQt4Suffix == other.HasQt4Suffix


    bool operator!=(  QtVersion& other )
        return not operator==( other )


    QString Version
    QString Path
    bool Default
    QString QMakeSpec
    QString QMakeParameters
    bool HasQt4Suffix


struct QtItem
    QtItem()    QtItem(  QString& t, v, s, h = QString.null )
            : Text( t ), Value( v ), Variable( s ), Help( h )
    bool operator==(  QtItem& o )
        return Text == o.Text and Value == o.Value and Variable == o.Variable and Help == o.Help

    bool operator!=(  QtItem& o )
        return not operator==( o )


    QString Text
    QString Value
    QString Variable
    QString Help


typedef QList<QtVersion> QtVersionList
typedef QList<QtItem> QtItemList

Q_DECLARE_METATYPE( QtVersion )
Q_DECLARE_METATYPE( QtVersionList )
Q_DECLARE_METATYPE( QtItem )
Q_DECLARE_METATYPE( QtItemList )

class QtVersionManager : public pSettings
    Q_OBJECT

public:
    QtVersionManager( owner = 0 )
    ~QtVersionManager()

    QtVersionList versions()
    void setVersions(  QtVersionList& versions )

    QtVersion defaultVersion()
    QtVersion version(  QString& versionString )

    QtItemList defaultModules()
    QtItemList modules()
    void setModules(  QtItemList& modules )

    QtItemList defaultConfigurations()
    QtItemList configurations()
    void setConfigurations(  QtItemList& configurations )

protected:
    static  QString mQtVersionKey
    static  QString mQtModuleKey
    static  QString mQtConfigurationKey
    static  QRegExp mQtVersionRegExp
    static  QRegExp mQtQMakeRegExp
    static  QRegExp mQtUninstallRegExp

    QStringList possibleQtPaths()
    QtVersionList getQtVersions(  QStringList& paths )
    void synchronizeVersions()

    # interpreter handling
    void initializeInterpreterCommands( bool initialize )
    static QString commandInterpreter(  QString& command, arguments, result, interpreter, data )


#endif # QTVERSIONMANAGER_H
