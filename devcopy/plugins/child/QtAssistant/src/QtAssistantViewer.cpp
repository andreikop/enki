#include "QtAssistantViewer.h"
#include "QtAssistantChild.h"

#include <QHelpEngine>
#include <QNetworkReply>
#include <QTimer>
#include <QDesktopServices>
#include <QWebHistory>
#include <QWheelEvent>

class HelpNetworkReply : public QNetworkReply
public:
    HelpNetworkReply(  QNetworkRequest& request, fileData )

    virtual void abort()

    virtual qint64 bytesAvailable()
        return data.length() +QNetworkReply.bytesAvailable()


protected:
    virtual qint64 readData( char* data, maxlen )

private:
    QByteArray data
    qint64 origLen


HelpNetworkReply.HelpNetworkReply(  QNetworkRequest& request, fileData )
        : data( fileData ), origLen( fileData.length() )
    setRequest( request )
    setOpenMode( QIODevice.ReadOnly )

    setHeader( QNetworkRequest.ContentTypeHeader, "text/html" )
    setHeader( QNetworkRequest.ContentLengthHeader, QByteArray.number( fileData.length() ) )
    QTimer.singleShot( 0, self, SIGNAL( metaDataChanged() ) )
    QTimer.singleShot( 0, self, SIGNAL( readyRead() ) )


def abort(self):
    # nothing to do


def readData(self, buffer, maxlen ):
    len = qMin( qint64( data.length() ), maxlen )
    if  len :
        qMemCopy( buffer, data.constData(), len )
        data.remove( 0, len )

    if  not data.length() :
        QTimer.singleShot( 0, self, SIGNAL( finished() ) )
    return len


class HelpNetworkAccessManager : public QNetworkAccessManager
public:
    HelpNetworkAccessManager( QHelpEngine* engine, parent )

protected:
    virtual QNetworkReply* createRequest( Operation op, request, outgoingData = 0 )

private:
    QHelpEngine* mHelpEngine


HelpNetworkAccessManager.HelpNetworkAccessManager( QHelpEngine* engine, parent )
        : QNetworkAccessManager( parent ), mHelpEngine( engine )


QNetworkReply *HelpNetworkAccessManager.createRequest( Operation op, request, outgoingData )
     scheme = request.url().scheme()
    if  scheme == QLatin1String( "qthelp" ) or scheme == QLatin1String( "about" ) :
        return HelpNetworkReply( request, mHelpEngine.fileData( request.url() ) )
    return QNetworkAccessManager.createRequest( op, request, outgoingData )


class HelpPage : public QWebPage
public:
    HelpPage( QtAssistantChild* child, parent )

protected:
    virtual QWebPage* createWindow( QWebPage.WebWindowType )

    virtual bool acceptNavigationRequest( QWebFrame* frame, request, type )

private:
    QtAssistantChild* mChild


HelpPage.HelpPage( QtAssistantChild* child, parent )
        : QWebPage( parent ), mChild( child )


def createWindow(self,  QWebPage.WebWindowType ):
    return mChild.newEmptyViewer().page()


static bool isLocalUrl(  QUrl& url )
     scheme = url.scheme()
    if  scheme.isEmpty(:
            or scheme == QLatin1String( "file" )
            or scheme == QLatin1String( "qrc" )
            or scheme == QLatin1String( "data" )
            or scheme == QLatin1String( "qthelp" )
            or scheme == QLatin1String( "about" ) )
        return True
    return False


def acceptNavigationRequest(self,  QWebFrame*, request, QWebPage.NavigationType ):
     url = request.url()

    if  isLocalUrl( url ) :
        return True

    else:
        #QDesktopServices.openUrl( url )
        return True



# QtAssistantViewer

QtAssistantViewer.QtAssistantViewer( QHelpEngine* engine, child, homeUrl )
        : QWebView( child )
    Q_ASSERT( engine )
    Q_ASSERT( child )

    mEngine = engine
    mChild = child
    mHomeUrl = homeUrl

    setPage( HelpPage( mChild, self ) )

    page().setNetworkAccessManager( HelpNetworkAccessManager( engine, self ) )

    pageAction( QWebPage.OpenLinkInNewWindow ).setText( tr( "Open Link in New Tab" ) )
    pageAction( QWebPage.DownloadLinkToDisk ).setVisible( False )
    pageAction( QWebPage.DownloadImageToDisk ).setVisible( False )
    pageAction( QWebPage.OpenImageInNewWindow ).setVisible( False )

    connect( pageAction( QWebPage.Copy ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Cut ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Paste ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Undo ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Redo ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Back ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( pageAction( QWebPage.Forward ), SIGNAL( changed() ), self, SLOT( actionChanged() ) )
    connect( page(), SIGNAL( linkHovered(  QString&,  QString&,  QString& ) ), self, SIGNAL( highlighted(  QString& ) ) )
    self.loadFinished.connect(self.loadFinished)


def setSource(self, url ):
    mHomeUrl = mHomeUrl.isValid() ? mHomeUrl : url
    load( url )


def resetZoom(self):
    setTextSizeMultiplier( 1.0 )


def zoomIn(self, range ):
    Q_UNUSED( range )
    setTextSizeMultiplier( textSizeMultiplier() +.5 )


def zoomOut(self, range ):
    Q_UNUSED( range )
    setTextSizeMultiplier( textSizeMultiplier() -.5 )


def home(self):
    if  history().canGoBack() :
        history().goToItem( history().backItems( history().count() ).first() )



def wheelEvent(self, e ):
    if  e.modifiers() & Qt.ControlModifier :
         delta = e.delta()
        if  delta > 0 :
            zoomOut()
        elif  delta < 0 :
            zoomIn()
        e.accept()
        return

    QWebView.wheelEvent( e )


def mouseReleaseEvent(self, e ):
    if  e.button() == Qt.XButton1 :
        triggerPageAction( QWebPage.Back )
        return


    if  e.button() == Qt.XButton2 :
        triggerPageAction( QWebPage.Forward )
        return


    QWebView.mouseReleaseEvent( e )


def actionChanged(self):
    a = qobject_cast<QAction*>( sender() )

    if  a == pageAction( QWebPage.Copy ) :
        copyAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Cut ) :
        cutAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Paste ) :
        pasteAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Undo ) :
        undoAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Redo ) :
        redoAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Back ) :
        backwardAvailable.emit( a.isEnabled() )
    elif  a == pageAction( QWebPage.Forward ) :
        forwardAvailable.emit( a.isEnabled() )

    actionsChanged.emit()


def loadFinished(self, ok ):
    Q_UNUSED( ok )
    sourceChanged.emit( url() )

