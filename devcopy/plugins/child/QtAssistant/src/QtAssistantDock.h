#ifndef QTASSISTANTDOCK_H
#define QTASSISTANTDOCK_H

#include <widgets/pDockWidget.h>

#include <QUrl>

class QAction
class QMenu
class QActionGroup
class QStackedWidget
class QLineEdit
class QProgressBar

class QtAssistantDock : public pDockWidget
    Q_OBJECT

public:
    QtAssistantDock( parent = 0 )
    virtual ~QtAssistantDock()

    class QtAssistantChild* child()

protected:
    QAction* aShow
    QAction* aContents
    QAction* aIndex
    QAction* aBookmarks
    QAction* aSearch
    QAction* aFilter
    QMenu* mFilters
    QActionGroup* aFilterGroup
    QStackedWidget* mStacked
    QWidget* wContents
    QWidget* wIndex
    QLineEdit* mLookFor
    QWidget* wBookmarks
    QWidget* wSearch
    QProgressBar* mProgress
    QAction* aKeywordHelp
    QAction* aSearchHelp

    class QHelpEngine* mHelpEngine
    class MkSQtDocInstaller* mDocInstaller
    class BookmarkManager* mBookmarkManager
    class BookmarkWidget* bwBookmarks

    bool eventFilter( QObject* obj, e )

    bool isWordCharacter(  QChar& character )
    QString currentWord(  QString& text, cursorPos )
    QString currentWord()

public slots:
    void openUrl(  QUrl& url, newTab = False )
    void openInNewTabUrl(  QUrl& url )
    void openUrls(  QMap<QString, links, keyword, newTab = False )

protected slots:
    void aPagesGroup_triggered( QAction* action )
    void updateFilters(  QString& filter )
    void aFilterGroup_triggered( QAction* action )
    void open_customContextMenuRequested(  QPoint& pos )
    void disableSearchLineEdit()
    void enableSearchLineEdit()
    void filterIndices(  QString& filter )
    void searchingStarted()
    void searchingFinished( int hits )
    void search()
    void addBookmark()
    void keywordHelp()
    void searchHelp()

signals:
    void helpShown()


#endif # QTASSISTANTDOCK_H
