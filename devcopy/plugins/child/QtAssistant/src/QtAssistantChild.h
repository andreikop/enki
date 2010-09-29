#ifndef QTASSISTANTCHILD_H
#define QTASSISTANTCHILD_H

#include <workspace/pAbstractChild.h>

class QHelpEngine
class QtAssistantInlineSearch
class QToolButton
class QComboBox

class QtAssistantChild : public pAbstractChild
    Q_OBJECT

    friend class QtAssistant
    friend class QtAssistantDock

public:
    static QtAssistantChild* instance( QHelpEngine* engine, parent = 0, create = True )

    QtAssistantChild( QHelpEngine* engine, parent = 0 )
    virtual ~QtAssistantChild()

    virtual QString context()
    virtual void initializeContext( QToolBar* tb )
    virtual QPoint cursorPosition()
    virtual pEditor* editor()
    virtual bool isModified()
    virtual bool isUndoAvailable()
    virtual bool isRedoAvailable()
    virtual bool isCopyAvailable()
    virtual bool isPasteAvailable()
    virtual bool isGoToAvailable()
    virtual bool isPrintAvailable()

    class QtAssistantViewer* viewer( index = -1 )
    QtAssistantViewer* newEmptyViewer( zoom = 1.0 )

protected:
    QHelpEngine* mEngine
    QTabWidget* twPages
    QtAssistantInlineSearch* isSearch
    QToolButton* tbCloneTab
    QAction* aPrevious
    QAction* aNext
    QAction* aHome
    QAction* aSearchText
    QAction* aZoomIn
    QAction* aZoomOut
    QAction* aZoomReset
    QAction* aAddNewPage
    QAction* aNextTab
    QAction* aPreviousTab
    QPointer<QComboBox> cbUrl
    bool mFirstOpenUrl

    void find( QString ttf, forward, backward )

public slots:
    virtual void undo()
    virtual void redo()
    virtual void cut()
    virtual void copy()
    virtual void paste()
    virtual void goTo()
    virtual void goTo(  QPoint& position, selectionLength = -1 )
    virtual void invokeSearch()
    virtual void saveFile()
    virtual void backupFileAs(  QString& fileName )
    virtual bool openFile(  QString& fileName, codec )
    virtual void closeFile()
    virtual void reload()
    virtual void printFile()
    virtual void quickPrintFile()

    void openUrl(  QUrl& url )
    void openUrlInNewTab(  QUrl& url )
    void cloneTab()
    void closeTab( int index )

    void focusCurrentTab()
    void saveSession()
    void restoreSession()

    void previousTab()
    void nextTab()
    void previousPage()
    void nextPage()
    void homePage()
    void zoomIn()
    void zoomOut()
    void zoomReset()

    void findNext()
    void findPrevious()
    void findCurrentText(  QString& text )

protected slots:
    void updateContextActions()
    void viewer_sourceChanged(  QUrl& url )
    void viewer_actionsChanged()
    void cbUrl_currentIndexChanged( int index )


#endif # QTASSISTANTCHILD_H
