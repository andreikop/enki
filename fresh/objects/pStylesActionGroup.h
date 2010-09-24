#ifndef PSTYLESACTIONGROUP_H
#define PSTYLESACTIONGROUP_H

#include "MonkeyExport.h"

#include <QActionGroup>
#include <QMap>

class Q_MONKEY_EXPORT pStylesActionGroup : public QActionGroup
{
	Q_OBJECT

public:
	pStylesActionGroup( const QString& textFormat = QLatin1String( "%1" ), QObject* parent = 0 );
	
	static QStringList availableStyles();
	
	static QString systemStyle();
	QAction* systemAction() const;
	
	static QString applicationStyle();
	QAction* applicationAction() const;
	
	bool isCheckable() const;
	QString currentStyle() const;

public slots:
	void refreshActions();
	
	void setCheckable( bool checkable );
	void setCurrentStyle( const QString& style );

protected:
	bool mCheckable;
	QString mTextFormat;
	QMap<QString, QAction*> mActions;

protected slots:
	void actionTriggered( QAction* action );

signals:
	void styleSelected( const QString& style );
};

#endif // PSTYLESACTIONGROUP_H
