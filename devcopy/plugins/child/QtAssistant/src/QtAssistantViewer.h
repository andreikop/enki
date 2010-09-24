#ifndef QTASSISTANTVIEWER_H
#define QTASSISTANTVIEWER_H

#include <QWebView>
#include <QAction>

class QHelpEngine
class QtAssistantChild

class QtAssistantViewer : public QWebView
    Q_OBJECT

public:
    QtAssistantViewer( QHelpEngine* engine, child, homeUrl = QUrl() )

    void setSource(  QUrl& url )

    inline QUrl source()
        return url()


    inline QString documentTitle()
        return title()


    inline bool hasSelection()
        return not selectedText().isEmpty()


    void resetZoom()
    void zoomIn( range = 1 )
    void zoomOut( range = 1 )

    inline void copy()
        triggerPageAction( QWebPage.Copy )


    inline bool isForwardAvailable()
        return pageAction( QWebPage.Forward ).isEnabled()


    inline bool isBackwardAvailable()
        return pageAction( QWebPage.Back ).isEnabled()


public slots:
    void home()
    void backward()
        back()


protected:
    virtual void wheelEvent( QWheelEvent* event )
    virtual void mouseReleaseEvent( QMouseEvent* event )

private slots:
    void actionChanged()
    void loadFinished( bool ok )

private:
    QHelpEngine* mEngine
    QtAssistantChild* mChild
    QUrl mHomeUrl

signals:
    void copyAvailable( bool enabled )
    void cutAvailable( bool enabled )
    void pasteAvailable( bool enabled )
    void undoAvailable( bool enabled )
    void redoAvailable( bool enabled )
    void forwardAvailable( bool enabled )
    void backwardAvailable( bool enabled )
    void actionsChanged()
    void highlighted(  QString& )
    void sourceChanged(  QUrl& )


#endif # QTASSISTANTVIEWER_H
