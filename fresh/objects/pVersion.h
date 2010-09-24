#ifndef PVERSION_H
#define PVERSION_H

#include "MonkeyExport.h"

#include <QString>

class Q_MONKEY_EXPORT pVersion
{
public:
	pVersion( const QString& version );
	
	const QString& toString() const;

	bool operator==( const pVersion& other ) const;
	bool operator!=( const pVersion& other ) const;
	bool operator<( const pVersion& other ) const;
	bool operator>( const pVersion& other ) const;
	bool operator<=( const pVersion& other ) const;
	bool operator>=( const pVersion& other ) const;

protected:
	QString mVersion;
	int major;
	int minor;
	int patch;
	int build;
	QString extra;
};

#endif // PVERSION_H
