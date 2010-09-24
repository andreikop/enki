class pGroupPath
{
%TypeHeaderCode
#include <../widgets/pGroupPath.h>
%End
public:
	pGroupPath();
	pGroupPath( const QString& name );
	pGroupPath( const QString& name, bool guessArraySize );
	pGroupPath( const pGroupPath& other );
	virtual ~pGroupPath();

	QString name() const;
	QString toString() const;
	bool isArray() const;
	int arraySizeGuess() const;
	void setArrayIndex( int i );
};
