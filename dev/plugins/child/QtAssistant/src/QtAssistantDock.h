#ifndef QTASSISTANTDOCK_H
#define QTASSISTANTDOCK_H

#include <widgets/pDockWidget.h>

#include <QUrl>

class QAction;
class QMenu;
class QActionGroup;
class QStackedWidget;
class QLineEdit;
class QProgressBar;

class QtAssistantDock : public pDockWidget
{
	Q_OBJECT
	
public:
	QtAssistantDock( QWidget* parent = 0 );
	virtual ~QtAssistantDock();
	
	class QtAssistantChild* child() const;

protected:
	QAction* aShow;
	QAction* aContents;
	QAction* aIndex;
	QAction* aBookmarks;
	QAction* aSearch;
	QAction* aFilter;
	QMenu* mFilters;
	QActionGroup* aFilterGroup;
	QStackedWidget* mStacked;
	QWidget* wContents;
	QWidget* wIndex;
	QLineEdit* mLookFor;
	QWidget* wBookmarks;
	QWidget* wSearch;
	QProgressBar* mProgress;
	QAction* aKeywordHelp;
	QAction* aSearchHelp;
	
	class QHelpEngine* mHelpEngine;
	class MkSQtDocInstaller* mDocInstaller;
	class BookmarkManager* mBookmarkManager;
	class BookmarkWidget* bwBookmarks;
	
	bool eventFilter( QObject* obj, QEvent* e );
	
	bool isWordCharacter( const QChar& character ) const;
	QString currentWord( const QString& text, int cursorPos ) const;
	QString currentWord() const;

public slots:
	void openUrl( const QUrl& url, bool newTab = false );
	void openInNewTabUrl( const QUrl& url );
	void openUrls( const QMap<QString, QUrl>& links, const QString& keyword, bool newTab = false );

protected slots:
	void aPagesGroup_triggered( QAction* action );
	void updateFilters( const QString& filter );
	void aFilterGroup_triggered( QAction* action );
	void open_customContextMenuRequested( const QPoint& pos );
	void disableSearchLineEdit();
	void enableSearchLineEdit();
	void filterIndices( const QString& filter );
	void searchingStarted();
	void searchingFinished( int hits );
	void search();
	void addBookmark();
	void keywordHelp();
	void searchHelp();

signals:
	void helpShown();
};

#endif // QTASSISTANTDOCK_H
