#include "QtAssistantViewer.h"
#include "QtAssistantChild.h"

#include <QHelpEngine>
#include <QNetworkReply>
#include <QTimer>
#include <QDesktopServices>
#include <QWebHistory>
#include <QWheelEvent>

class HelpNetworkReply : public QNetworkReply
{
public:
	HelpNetworkReply( const QNetworkRequest& request, const QByteArray& fileData );

	virtual void abort();

	virtual qint64 bytesAvailable() const
	{ return data.length() +QNetworkReply::bytesAvailable(); }

protected:
	virtual qint64 readData( char* data, qint64 maxlen );

private:
	QByteArray data;
	qint64 origLen;
};

HelpNetworkReply::HelpNetworkReply( const QNetworkRequest& request, const QByteArray& fileData )
	: data( fileData ), origLen( fileData.length() )
{
	setRequest( request );
	setOpenMode( QIODevice::ReadOnly );

	setHeader( QNetworkRequest::ContentTypeHeader, "text/html" );
	setHeader( QNetworkRequest::ContentLengthHeader, QByteArray::number( fileData.length() ) );
	QTimer::singleShot( 0, this, SIGNAL( metaDataChanged() ) );
	QTimer::singleShot( 0, this, SIGNAL( readyRead() ) );
}

void HelpNetworkReply::abort()
{
	// nothing to do
}

qint64 HelpNetworkReply::readData( char* buffer, qint64 maxlen )
{
	qint64 len = qMin( qint64( data.length() ), maxlen );
	if ( len )
	{
		qMemCopy( buffer, data.constData(), len );
		data.remove( 0, len );
	}
	if ( !data.length() )
		QTimer::singleShot( 0, this, SIGNAL( finished() ) );
	return len;
}

class HelpNetworkAccessManager : public QNetworkAccessManager
{
public:
	HelpNetworkAccessManager( QHelpEngine* engine, QObject* parent );

protected:
	virtual QNetworkReply* createRequest( Operation op, const QNetworkRequest& request, QIODevice* outgoingData = 0 );

private:
	QHelpEngine* mHelpEngine;
};

HelpNetworkAccessManager::HelpNetworkAccessManager( QHelpEngine* engine, QObject* parent )
	: QNetworkAccessManager( parent ), mHelpEngine( engine )
{
}

QNetworkReply *HelpNetworkAccessManager::createRequest( Operation op, const QNetworkRequest& request, QIODevice* outgoingData )
{
	const QString scheme = request.url().scheme();
	if ( scheme == QLatin1String( "qthelp" ) || scheme == QLatin1String( "about" ) )
		return new HelpNetworkReply( request, mHelpEngine->fileData( request.url() ) );
	return QNetworkAccessManager::createRequest( op, request, outgoingData );
}

class HelpPage : public QWebPage
{
public:
	HelpPage( QtAssistantChild* child, QObject* parent );

protected:
	virtual QWebPage* createWindow( QWebPage::WebWindowType );

	virtual bool acceptNavigationRequest( QWebFrame* frame, const QNetworkRequest& request, NavigationType type );

private:
	QtAssistantChild* mChild;
};

HelpPage::HelpPage( QtAssistantChild* child, QObject* parent )
	: QWebPage( parent ), mChild( child )
{
}

QWebPage* HelpPage::createWindow( QWebPage::WebWindowType )
{
	return mChild->newEmptyViewer()->page();
}

static bool isLocalUrl( const QUrl& url )
{
	const QString scheme = url.scheme();
	if ( scheme.isEmpty()
		|| scheme == QLatin1String( "file" )
		|| scheme == QLatin1String( "qrc" )
		|| scheme == QLatin1String( "data" )
		|| scheme == QLatin1String( "qthelp" )
		|| scheme == QLatin1String( "about" ) )
		return true;
	return false;
}

bool HelpPage::acceptNavigationRequest( QWebFrame*, const QNetworkRequest& request, QWebPage::NavigationType )
{
	const QUrl url = request.url();
	
	if ( isLocalUrl( url ) )
	{
		return true;
	}
	else
	{
		//QDesktopServices::openUrl( url );
		return true;
	}
}

// QtAssistantViewer

QtAssistantViewer::QtAssistantViewer( QHelpEngine* engine, QtAssistantChild* child, const QUrl& homeUrl )
	: QWebView( child )
{
	Q_ASSERT( engine );
	Q_ASSERT( child );
	
	mEngine = engine;
	mChild = child;
	mHomeUrl = homeUrl;
	
	setPage( new HelpPage( mChild, this ) );

	page()->setNetworkAccessManager( new HelpNetworkAccessManager( engine, this ) );

	pageAction( QWebPage::OpenLinkInNewWindow )->setText( tr( "Open Link in New Tab" ) );
	pageAction( QWebPage::DownloadLinkToDisk )->setVisible( false );
	pageAction( QWebPage::DownloadImageToDisk )->setVisible( false );
	pageAction( QWebPage::OpenImageInNewWindow )->setVisible( false );

	connect( pageAction( QWebPage::Copy ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Cut ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Paste ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Undo ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Redo ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Back ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( pageAction( QWebPage::Forward ), SIGNAL( changed() ), this, SLOT( actionChanged() ) );
	connect( page(), SIGNAL( linkHovered( const QString&, const QString&, const QString& ) ), this, SIGNAL( highlighted( const QString& ) ) );
	connect( this, SIGNAL( loadFinished( bool ) ), this, SLOT( loadFinished( bool ) ) );
}

void QtAssistantViewer::setSource( const QUrl& url )
{
	mHomeUrl = mHomeUrl.isValid() ? mHomeUrl : url;
	load( url );
}

void QtAssistantViewer::resetZoom()
{
	setTextSizeMultiplier( 1.0 );
}

void QtAssistantViewer::zoomIn( int range )
{
	Q_UNUSED( range );
	setTextSizeMultiplier( textSizeMultiplier() +.5 );
}

void QtAssistantViewer::zoomOut( int range )
{
	Q_UNUSED( range );
	setTextSizeMultiplier( textSizeMultiplier() -.5 );
}

void QtAssistantViewer::home()
{
	if ( history()->canGoBack() )
	{
		history()->goToItem( history()->backItems( history()->count() ).first() );
	}
}

void QtAssistantViewer::wheelEvent( QWheelEvent* e )
{
	if ( e->modifiers() & Qt::ControlModifier )
	{
		const int delta = e->delta();
		if ( delta > 0 )
			zoomOut();
		else if ( delta < 0 )
			zoomIn();
		e->accept();
		return;
	}
	QWebView::wheelEvent( e );
}

void QtAssistantViewer::mouseReleaseEvent( QMouseEvent* e )
{
	if ( e->button() == Qt::XButton1 )
	{
		triggerPageAction( QWebPage::Back );
		return;
	}

	if ( e->button() == Qt::XButton2 )
	{
		triggerPageAction( QWebPage::Forward );
		return;
	}

	QWebView::mouseReleaseEvent( e );
}

void QtAssistantViewer::actionChanged()
{
	QAction* a = qobject_cast<QAction*>( sender() );
	
	if ( a == pageAction( QWebPage::Copy ) )
		emit copyAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Cut ) )
		emit cutAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Paste ) )
		emit pasteAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Undo ) )
		emit undoAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Redo ) )
		emit redoAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Back ) )
		emit backwardAvailable( a->isEnabled() );
	else if ( a == pageAction( QWebPage::Forward ) )
		emit forwardAvailable( a->isEnabled() );
	
	emit actionsChanged();
}

void QtAssistantViewer::loadFinished( bool ok )
{
	Q_UNUSED( ok );
	emit sourceChanged( url() );
}
