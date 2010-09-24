#include "pGroupPath.h"

pGroupPath::pGroupPath()
{
	mNum = -1;
	mMaxNum = -1;
}

pGroupPath::pGroupPath( const QString& name )
{
	mStr = name;
	mNum = -1;
	mMaxNum = -1;
}

pGroupPath::pGroupPath( const QString& name, bool guessArraySize )
{
	mStr = name;
	mNum = 0;
	mMaxNum = guessArraySize ? 0 : -1;
}

pGroupPath::pGroupPath( const pGroupPath& other )
{
	mStr = other.mStr;
	mNum = other.mNum;
	mMaxNum = other.mMaxNum;
}

pGroupPath::~pGroupPath()
{
}

pGroupPath& pGroupPath::operator=( const pGroupPath& other )
{
	if( *this != other )
	{
		mStr = other.mStr;
		mNum = other.mNum;
		mMaxNum = other.mMaxNum;
	}

	return *this;
}

bool pGroupPath::operator==( const pGroupPath& other ) const
{
	return mStr == other.mStr && mNum == other.mNum && mMaxNum == other.mMaxNum;
}

bool pGroupPath::operator!=( const pGroupPath& other ) const
{
	return !operator==( other );
}

QString pGroupPath::name() const
{
	return mStr;
}

QString pGroupPath::toString() const
{
	QString result;
	result = mStr;
	
	if ( mNum > 0 )
	{
		result += QLatin1Char( '/' );
		result += QString::number( mNum );
	}
	
	return result;
}

bool pGroupPath::isArray() const
{
	return mNum != -1;
}

int pGroupPath::arraySizeGuess() const
{
	return mMaxNum;
}

void pGroupPath::setArrayIndex( int i )
{
	mNum = i +1;
	
	if ( mMaxNum != -1 && mNum > mMaxNum )
	{
		mMaxNum = mNum;
	}
}
