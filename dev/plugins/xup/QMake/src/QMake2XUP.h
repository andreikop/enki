#ifndef QMAKE2XUP_H
#define QMAKE2XUP_H

#include <QDomDocument>

namespace QMake2XUP
{
	QString convertFromPro( const QString& fileName, const QString& codec );
	QString convertToPro( const QDomDocument& project );
};

#endif // QMAKE2XUP_H
