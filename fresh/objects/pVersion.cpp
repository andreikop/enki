#include "pVersion.h"

#include <QStringList>

pVersion::pVersion( const QString& version )
{
	mVersion = version.trimmed();
	const QStringList parts = mVersion.split( "." );
	const int index = parts.value( 3 ).indexOf( QRegExp( "[A-Z|a-z]" ) );

	major = parts.value( 0 ).toInt();
	minor = parts.value( 1 ).toInt();
	patch = parts.value( 2 ).toInt();

	if ( index != -1 ) {
		build = parts.value( 3 ).mid( 0, index ).toInt();
		extra = parts.value( 3 ).mid( index );
	}
	else {
		build = parts.value( 3 ).toInt();
	}
}

const QString& pVersion::toString() const
{
	return mVersion;
}

bool pVersion::operator==( const pVersion& other ) const
{
	return major == other.major
		&& minor == other.minor
		&& patch == other.patch
		&& build == other.build
		&& extra == other.extra;
}

bool pVersion::operator!=( const pVersion& other ) const
{
	return !operator==( other );
}

bool pVersion::operator<( const pVersion& other ) const
{
	if ( *this == other ) {
		return false;
	}

	if ( major != other.major ) {
		return major < other.major;
	}

	if ( minor != other.minor ) {
		return minor < other.minor;
	}

	if ( patch != other.patch ) {
		return patch < other.patch;
	}

	if ( build != other.build ) {
		return build < other.build;
	}

	if ( extra.isEmpty() && !other.extra.isEmpty() ) {
		return false;
	}
	
	if ( !extra.isEmpty() && other.extra.isEmpty() ) {
		return true;
	}
	
	return extra < other.extra; // not the best but afaik ;)
}

bool pVersion::operator>( const pVersion& other ) const
{
	if ( *this == other ) {
		return false;
	}

	if ( major != other.major ) {
		return major > other.major;
	}

	if ( minor != other.minor ) {
		return minor > other.minor;
	}

	if ( patch != other.patch ) {
		return patch > other.patch;
	}

	if ( build != other.build ) {
		return build > other.build;
	}
	
	if ( extra.isEmpty() && !other.extra.isEmpty() ) {
		return true;
	}
	
	if ( !extra.isEmpty() && other.extra.isEmpty() ) {
		return false;
	}

	return extra > other.extra; // not the best but afaik ;)
}

bool pVersion::operator<=( const pVersion& other ) const
{
	return operator<( other ) || operator==( other );
}

bool pVersion::operator>=( const pVersion& other ) const
{
	return operator>( other ) || operator==( other );
}
