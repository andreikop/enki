#ifndef PGROUPPATH_H
#define PGROUPPATH_H

#include "objects/MonkeyExport.h"

#include <QString>

class Q_MONKEY_EXPORT pGroupPath
{
public:
	pGroupPath();
	pGroupPath( const QString& name );
	pGroupPath( const QString& name, bool guessArraySize );
	pGroupPath( const pGroupPath& other );
	virtual ~pGroupPath();

	pGroupPath& operator=( const pGroupPath& other );
	bool operator==( const pGroupPath& other ) const;
	bool operator!=( const pGroupPath& other ) const;
	
	QString name() const;
	QString toString() const;
	bool isArray() const;
	int arraySizeGuess() const;
	void setArrayIndex( int i );

protected:
	QString mStr;
	int mNum;
	int mMaxNum;
};

#endif // PGROUPPATH_H
