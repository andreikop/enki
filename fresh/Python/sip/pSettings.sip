class pSettings : QSettings
{
%TypeHeaderCode
#include <../objects/pSettings.h>
%End

public:
	pSettings( QObject* parent = 0, const QString& name = _PACKAGE_NAME, const QString& version = _PACKAGE_VERSION_STR );
	static void setIniInformations( const QString& name = _PACKAGE_NAME, const QString& version = _PACKAGE_VERSION_STR );
	static QString programName();
	static QString programVersion();
	static QString getIniFile( const QString& name, const QString& version );

	virtual void restoreState( QMainWindow* window );
	virtual void saveState( QMainWindow* );
	virtual void setDefaultSettings();
};
