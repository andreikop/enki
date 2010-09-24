#ifndef PMULTITOOLBAR_H
#define PMULTITOOLBAR_H

#include "objects/MonkeyExport.h"

#include <QStackedWidget>
#include <QMap>

class QToolBar;

class Q_MONKEY_EXPORT pMultiToolBar : public QStackedWidget
{
	Q_OBJECT
	
public:
	pMultiToolBar( QWidget* parent = 0 );
	virtual ~pMultiToolBar();
	
	QString currentContext() const;
	void setCurrentContext( const QString& context );
	
	void removeContext( const QString& context, bool del = false );
	QStringList contexts() const;
	QToolBar* toolBar( const QString& context ) const;
	QToolBar* currentToolBar() const;

protected:
	mutable QMap<int, QToolBar*> mToolBars;
	
	void updateMaps();

protected slots:
	void _q_currentChanged( int index );
	void _q_widgetRemoved( int index );

signals:
	void currentContextChanged( const QString& context );
	void contextRemoved( const QString& context );
	void notifyChanges();
};

#endif // PMULTITOOLBAR_H
