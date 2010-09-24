
class QSingleton : QSingletonExpose
{
%TypeHeaderCode
#include <../objects/QSingleton.h>
%End

protected:
	QSingleton();
	virtual ~QSingleton();

public:
	static T* instance( P* pointer );
	static T* instance();
	static bool instanceAvailable();
	static void cleanInstance();
};
