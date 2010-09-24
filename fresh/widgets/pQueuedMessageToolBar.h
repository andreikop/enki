#ifndef PQUEUEDMESSAGETOOLBAR_H
#define PQUEUEDMESSAGETOOLBAR_H

#include "objects/MonkeyExport.h"
#include "pQueuedMessageWidget.h"

#include <QToolBar>

class Q_MONKEY_EXPORT pQueuedMessageToolBar : public QToolBar
{
	Q_OBJECT
	
public:
	pQueuedMessageToolBar( QWidget* parent = 0 );
	virtual ~pQueuedMessageToolBar();
	
	static void setDefaultTimeout( int timeout );
	static const int& defaultTimeout();
	
	static void setDefaultPixmap( const QPixmap& pixmap );
	static const QPixmap& defaultPixmap();
	
	static void setDefaultBackground( const QBrush& brush );
	static const QBrush& defaultBackground();
	
	static void setDefaultForeground( const QBrush& brush );
	static const QBrush& defaultForeground();

protected:
	static int mDefaultTimeout;
	static QPixmap* mDefaultPixmap;
	static QBrush mDefaultBackground;
	static QBrush mDefaultForeground;
	QPalette mDefaultPalette;
	pQueuedMessageWidget* mQueuedWidget;

public slots:
	int appendMessage( const pQueuedMessage& message );
	int appendMessage( const QString& message, int milliseconds = pQueuedMessageToolBar::defaultTimeout(), const QPixmap& pixmap = pQueuedMessageToolBar::defaultPixmap(), const QBrush& background = pQueuedMessageToolBar::defaultBackground(), const QBrush& foreground = pQueuedMessageToolBar::defaultForeground() );
	void removeMessage( const pQueuedMessage& message );
	void removeMessage( int id );

protected slots:
	void messageShown( const pQueuedMessage& message );
	void messageCleared();
};

#endif // PQUEUEDMESSAGETOOLBAR_H
