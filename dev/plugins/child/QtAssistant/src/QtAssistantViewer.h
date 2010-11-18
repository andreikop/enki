#ifndef QTASSISTANTVIEWER_H
#define QTASSISTANTVIEWER_H

#include <QWebView>
#include <QAction>

class QHelpEngine;
class QtAssistantChild;

class QtAssistantViewer : public QWebView
{
	Q_OBJECT
	
public:
	QtAssistantViewer( QHelpEngine* engine, QtAssistantChild* child, const QUrl& homeUrl = QUrl() );
	
	void setSource( const QUrl& url );

	inline QUrl source() const
	{ return url(); }

	inline QString documentTitle() const
	{ return title(); }

	inline bool hasSelection() const
	{ return !selectedText().isEmpty(); }

	void resetZoom();
	void zoomIn( int range = 1 );
	void zoomOut( int range = 1 );

	inline void copy()
	{ triggerPageAction( QWebPage::Copy ); }

	inline bool isForwardAvailable() const
	{ return pageAction( QWebPage::Forward )->isEnabled(); }

	inline bool isBackwardAvailable() const
	{ return pageAction( QWebPage::Back )->isEnabled(); }

public slots:
	void home();
	void backward()
	{ back(); }

protected:
	virtual void wheelEvent( QWheelEvent* event );
	virtual void mouseReleaseEvent( QMouseEvent* event );

private slots:
	void actionChanged();
	void loadFinished( bool ok );

private:
	QHelpEngine* mEngine;
	QtAssistantChild* mChild;
	QUrl mHomeUrl;

signals:
	void copyAvailable( bool enabled );
	void cutAvailable( bool enabled );
	void pasteAvailable( bool enabled );
	void undoAvailable( bool enabled );
	void redoAvailable( bool enabled );
	void forwardAvailable( bool enabled );
	void backwardAvailable( bool enabled );
	void actionsChanged();
	void highlighted( const QString& );
	void sourceChanged( const QUrl& );
};

#endif // QTASSISTANTVIEWER_H
