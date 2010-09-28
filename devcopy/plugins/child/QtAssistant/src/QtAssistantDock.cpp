#include "QtAssistantDock.h"
#include "QtAssistantChild.h"
#include "QtAssistantViewer.h"
#include "MkSQtDocInstaller.h"
#include "topicchooser.h"
#include "bookmarkmanager.h"

#include <objects/pIconManager.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <widgets/pQueuedMessageToolBar.h>

#include <coremanager/MonkeyCore.h>
#include <qscintillamanager/pEditor.h>
#include <widgets/pMenuBar.h>

#include <QHelpEngine>
#include <QHelpContentWidget>
#include <QHelpIndexWidget>
#include <QHelpSearchEngine>
#include <QHelpSearchQueryWidget>
#include <QHelpSearchResultWidget>
#include <QAction>
#include <QActionGroup>
#include <QMenu>
#include <QStackedWidget>
#include <QProgressBar>
#include <QTextBrowser>
#include <QClipboard>
#include <QKeyEvent>
#include <QDebug>

QtAssistantDock::QtAssistantDock( QWidget* parent )
    : pDockWidget( parent )
{
    setObjectName( "QtAssistantDock" );
    setWindowTitle( "Qt Assistant" );
    setWindowIcon( pIconManager::icon( "QtAssistant.png", ":/assistant-icons" ) );
    
    // create help engine with default collection
    MkSQtDocInstaller::collectionFileDirectory( true );
    mHelpEngine = new QHelpEngine( MkSQtDocInstaller::defaultHelpCollectionFileName(), this );
    
    // create bookmarks manager
    mBookmarkManager = new BookmarkManager( mHelpEngine );
    mBookmarkManager->setupBookmarkModels();
    bwBookmarks = new BookmarkWidget( mBookmarkManager, this );
    bwBookmarks->layout()->setMargin( 0 );
#ifdef Q_WS_MAC
    bwBookmarks->layout()->setSpacing( 5 );
#else
    bwBookmarks->layout()->setSpacing( 3 );
#endif
    
    // areas
    setAllowedAreas( Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea );
    
    // actions
    aContents = new QAction( pIconManager::icon( "contents.png", ":/assistant-icons" ), tr( "Contents" ), this );
    aContents->setToolTip( aContents->text() );
    aContents->setCheckable( true );
    aContents->setData( 0 );
    titleBar()->addAction( aContents, 0 );
    
    aIndex = new QAction( pIconManager::icon( "index.png", ":/assistant-icons" ), tr( "Index" ), this );
    aIndex->setToolTip( aIndex->text() );
    aIndex->setCheckable( true );
    aIndex->setData( 1 );
    titleBar()->addAction( aIndex, 1 );
    
    aBookmarks = new QAction( pIconManager::icon( "bookmarks.png", ":/assistant-icons" ), tr( "Bookmarks" ), this );
    aBookmarks->setToolTip( aBookmarks->text() );
    aBookmarks->setCheckable( true );
    aBookmarks->setData( 2 );
    titleBar()->addAction( aBookmarks, 2 );
    
    titleBar()->addSeparator( 3 );
    
    aSearch = new QAction( pIconManager::icon( "search.png", ":/assistant-icons" ), tr( "Search" ), this );
    aSearch->setToolTip( aSearch->text() );
    aSearch->setCheckable( true );
    aSearch->setData( 3 );
    titleBar()->addAction( aSearch, 4 );
    
    aShow = new QAction( pIconManager::icon( "QtAssistant.png", ":/assistant-icons" ), tr( "Show Assistant" ), this );
    aShow->setToolTip( aShow->text() );
    titleBar()->addAction( aShow, 5 );
    
    aFilter = new QAction( pIconManager::icon( "filter.png", ":/assistant-icons" ), tr( "Filter" ), this );
    aFilter->setToolTip( aFilter->text() );
    mFilters = new QMenu( this );
    QToolButton* tb = qobject_cast<QToolButton*>( titleBar()->addAction( aFilter, 6 ) );
    tb->setPopupMode( QToolButton::InstantPopup );
    aFilter->setMenu( mFilters );
    
    titleBar()->addSeparator( 7 );
    
    QActionGroup* aPagesGroup = new QActionGroup( this );
    aPagesGroup->addAction( aContents );
    aPagesGroup->addAction( aIndex );
    aPagesGroup->addAction( aBookmarks );
    aPagesGroup->addAction( aSearch );
    
    aFilterGroup = new QActionGroup( this );
    updateFilters( mHelpEngine->currentFilter() );
    
    // stacked
    QWidget* wCentral = new QWidget( this );
    QVBoxLayout* stackedLayout = new QVBoxLayout( wCentral );
    
    mStacked = new QStackedWidget( this );
    mProgress = new QProgressBar( this );
    mProgress->setRange( 0, 0 );
    mProgress->setAlignment( Qt::AlignCenter );
    mProgress->setTextVisible( false );
    mProgress->setVisible( false );
    
    stackedLayout->addWidget( mStacked );
    stackedLayout->addWidget( mProgress );
    
    setWidget( wCentral );
    
    // pages
    wContents = mHelpEngine->contentWidget();
    wBookmarks = bwBookmarks;
    
    wIndex = new QWidget( this );
    QVBoxLayout* indexLayout = new QVBoxLayout( wIndex );
    indexLayout->setMargin( 0 );
    indexLayout->setSpacing( 3 );
    mLookFor = new QLineEdit( this );
    QLabel* labelLookFor = new QLabel( tr( "&Look for:" ), this );
    labelLookFor->setBuddy( mLookFor );
    indexLayout->addWidget( labelLookFor );
    indexLayout->addWidget( mLookFor );
    indexLayout->addWidget( mHelpEngine->indexWidget() );
    
    wSearch = new QWidget( this );
    QVBoxLayout* searchLayout = new QVBoxLayout( wSearch );
    searchLayout->setMargin( 0 );
    searchLayout->setSpacing( 3 );
    searchLayout->addWidget( mHelpEngine->searchEngine()->queryWidget() );
    searchLayout->addWidget( mHelpEngine->searchEngine()->resultWidget() );
    
    mStacked->addWidget( wContents );
    mStacked->addWidget( wIndex );
    mStacked->addWidget( wBookmarks );
    mStacked->addWidget( wSearch );
    
    // prepare context menu policy
    QTextBrowser* textBrowser = mHelpEngine->searchEngine()->resultWidget()->findChild<QTextBrowser*>();
    
    mHelpEngine->contentWidget()->setContextMenuPolicy( Qt::CustomContextMenu );
    mHelpEngine->indexWidget()->setContextMenuPolicy( Qt::CustomContextMenu );
    textBrowser->setContextMenuPolicy( Qt::CustomContextMenu );
    
    // help on keyword
    aKeywordHelp = MonkeyCore::menuBar()->action( "mHelp/aKeywordHelp", tr( "Keyword Help" ), pIconManager::icon( "assistant.png", ":/help" ), "F1", tr( "Search the current word in indexes." ) );
    aSearchHelp = MonkeyCore::menuBar()->action( "mHelp/aSearchHelp", tr( "Search Help" ), pIconManager::icon( "assistant.png", ":/help" ), "Shift+F1", tr( "Search the current word using the search engine." ) );
    
    // install event filters
    mLookFor->installEventFilter( this );
    mHelpEngine->indexWidget()->installEventFilter( this );
    
    // os x gui fix
    foreach ( QWidget* widget, findChildren<QWidget*>() )
    {
        widget->setAttribute( Qt::WA_MacShowFocusRect, false );
        widget->setAttribute( Qt::WA_MacSmallSize );
    }
    
    // connections
    connect( aShow, SIGNAL( triggered() ), this, SIGNAL( helpShown() ) );
    connect( mHelpEngine->searchEngine(), SIGNAL( indexingStarted() ), mProgress, SLOT( show() ) );
    connect( mHelpEngine->searchEngine(), SIGNAL( indexingFinished() ), mProgress, SLOT( hide() ) );
    connect( aPagesGroup, SIGNAL( triggered( QAction* ) ), this, SLOT( aPagesGroup_triggered( QAction* ) ) );
    connect( mHelpEngine, SIGNAL( currentFilterChanged( const QString& ) ), this, SLOT( updateFilters( const QString& ) ) );
    connect( aFilterGroup, SIGNAL( triggered( QAction* ) ), this, SLOT( aFilterGroup_triggered( QAction* ) ) );
    connect( mHelpEngine->contentWidget(), SIGNAL( linkActivated( const QUrl& ) ), this, SLOT( openUrl( const QUrl& ) ) );
    connect( mHelpEngine->indexWidget(), SIGNAL( linkActivated( const QUrl&, const QString& ) ), this, SLOT( openUrl( const QUrl& ) ) );
    connect( mHelpEngine->indexWidget(), SIGNAL( linksActivated( const QMap<QString, QUrl>&, const QString& ) ), this, SLOT( openUrls( const QMap<QString, QUrl>&, const QString& ) ) );
    connect( mHelpEngine->indexModel(), SIGNAL( indexCreationStarted() ),this, SLOT( disableSearchLineEdit() ) );
    connect( mHelpEngine->indexModel(), SIGNAL( indexCreated() ),this, SLOT( enableSearchLineEdit() ) );
    connect( mLookFor, SIGNAL( textChanged( const QString& ) ), this, SLOT( filterIndices( const QString& ) ) );
    connect( mLookFor, SIGNAL( returnPressed() ), mHelpEngine->indexWidget(), SLOT( activateCurrentItem() ) );
    connect( mHelpEngine->searchEngine(), SIGNAL( searchingStarted() ), this, SLOT( searchingStarted() ) );
    connect( mHelpEngine->searchEngine(), SIGNAL( searchingFinished( int ) ), this, SLOT( searchingFinished( int ) ) );
    connect( mHelpEngine->searchEngine()->queryWidget(), SIGNAL( search() ), this, SLOT( search() ) );
    connect( mHelpEngine->searchEngine()->resultWidget(), SIGNAL( requestShowLink( const QUrl& ) ), this, SLOT( openUrl( const QUrl& ) ) );
    connect( mHelpEngine->contentWidget(), SIGNAL( customContextMenuRequested( const QPoint& ) ), this, SLOT( open_customContextMenuRequested( const QPoint& ) ) );
    connect( mHelpEngine->indexWidget(), SIGNAL( customContextMenuRequested( const QPoint& ) ), this, SLOT( open_customContextMenuRequested( const QPoint& ) ) );
    connect( textBrowser, SIGNAL( customContextMenuRequested( const QPoint& ) ), this, SLOT( open_customContextMenuRequested( const QPoint& ) ) );
    connect( bwBookmarks, SIGNAL( requestShowLink( const QUrl& ) ), this, SLOT( openUrl( const QUrl& ) ) );
    connect( bwBookmarks, SIGNAL( requestShowLinkInNewTab( const QUrl& ) ), this, SLOT( openInNewTabUrl( const QUrl& ) ) );
    connect( bwBookmarks, SIGNAL( addBookmark() ), this, SLOT( addBookmark() ) );
    connect( aKeywordHelp, SIGNAL( triggered() ), this, SLOT( keywordHelp() ) );
    connect( aSearchHelp, SIGNAL( triggered() ), this, SLOT( searchHelp() ) );
    
    aContents->toggle();
    
    // init documentation
    mDocInstaller = new MkSQtDocInstaller( mHelpEngine );
    
    QTimer::singleShot( 1000* 10, mDocInstaller, SLOT( checkDocumentation() ) );
}

QtAssistantDock::~QtAssistantDock()
{
    mBookmarkManager->saveBookmarks();
    delete QtAssistantChild::instance( mHelpEngine, this, false );
}

bool QtAssistantDock::eventFilter( QObject* obj, QEvent* e )
{
    if ( obj == mLookFor && e->type() == QEvent::KeyPress )
    {
        QKeyEvent* ke = static_cast<QKeyEvent*>( e );
        QModelIndex idx = mHelpEngine->indexWidget()->currentIndex();
        switch ( ke->key() )
        {
            case Qt::Key_Up:
                idx = mHelpEngine->indexModel()->index( idx.row() -1, idx.column(), idx.parent() );
                if ( idx.isValid() )
                    mHelpEngine->indexWidget()->setCurrentIndex( idx );
                break;
            case Qt::Key_Down:
                idx = mHelpEngine->indexModel()->index( idx.row() +1, idx.column(), idx.parent() );
                if ( idx.isValid() )
                    mHelpEngine->indexWidget()->setCurrentIndex( idx );
                break;
            case Qt::Key_Escape:
                child()->focusCurrentTab();
                break;
            default:
                break;
        }
    }
#ifdef Q_OS_MAC
    else if ( obj == mHelpEngine->indexWidget() && e->type() == QEvent::KeyPress )
    {
        QKeyEvent* ke = static_cast<QKeyEvent*>( e );
        if ( ke->key() == Qt::Key_Return || ke->key() == Qt::Key_Enter )
            mHelpEngine->indexWidget()->activateCurrentItem();
    }
#endif
    return pDockWidget::eventFilter( obj, e );
}

QtAssistantChild* QtAssistantDock::child() const
{
    return QtAssistantChild::instance( mHelpEngine, const_cast<QtAssistantDock*>( this ) );
}

void QtAssistantDock::openUrl( const QUrl& url, bool newTab )
{
    emit helpShown();
    
    if ( newTab )
    {
        child()->openUrlInNewTab( url );
    }
    else
    {
        child()->openUrl( url );
    }
}

void QtAssistantDock::openInNewTabUrl( const QUrl& url )
{
    openUrl( url, true );
}

void QtAssistantDock::openUrls( const QMap<QString, QUrl>& links, const QString& keyword, bool newTab )
{
    if ( links.isEmpty() )
    {
        return;
    }
    
    if ( links.count() == 1 )
    {
        openUrl( links.begin().value(), newTab );
        return;
    }
    
    TopicChooser tc( this, keyword, links );
    
    if ( tc.exec() == QDialog::Accepted )
    {
        openUrl( tc.link(), newTab );
    }
}

void QtAssistantDock::aPagesGroup_triggered( QAction* action )
{
    const int index = action->data().toInt();
    mStacked->setCurrentIndex( index );
}

void QtAssistantDock::updateFilters( const QString& filter )
{
    const bool locked = aFilterGroup->blockSignals( true );
    
    qDeleteAll( aFilterGroup->actions() );
    
    foreach ( const QString& cFilter, mHelpEngine->customFilters() )
    {
        QAction* action = mFilters->addAction( cFilter );
        action->setData( cFilter );
        action->setCheckable( true );
        aFilterGroup->addAction( action );
        
        if ( cFilter == filter )
        {
            action->setChecked( true );
        }
    }
    
    aFilterGroup->blockSignals( locked );
}

void QtAssistantDock::aFilterGroup_triggered( QAction* action )
{
    mHelpEngine->setCurrentFilter( action->data().toString() );
}

void QtAssistantDock::open_customContextMenuRequested( const QPoint& pos )
{
    QWidget* widget = qobject_cast<QWidget*>( sender() );
    QUrl url;
    QMenu menu( this );
    
    QAction* aOpenUrl = menu.addAction( tr( "Open Link" ) );
    QAction* aOpenUrlNewTab = menu.addAction( tr( "Open Link in New Tab" ) );
    QAction* aCopyAnchor = menu.addAction( tr( "Copy &Link(s) Location" ) );
    
    menu.addSeparator();
    
    QAction* aCopy = menu.addAction( tr( "&Copy" ) );
    aCopy->setShortcut( QKeySequence::Copy );

    QAction* aSelectAll = menu.addAction( tr( "Select All" ) );
    aSelectAll->setShortcut( QKeySequence::SelectAll );
    
    if ( widget == mHelpEngine->contentWidget() )
    {
        const QModelIndex index = mHelpEngine->contentWidget()->indexAt( pos );
        const QHelpContentItem* ci = mHelpEngine->contentModel()->contentItemAt( index );
        url = ci ? ci->url() : url;
        aCopy->setEnabled( index.isValid() );
        aSelectAll->setEnabled( false );
    }
    else if ( widget == mHelpEngine->indexWidget() )
    {
        const QModelIndex index = mHelpEngine->indexWidget()->indexAt( pos );
        const QString keyword = mHelpEngine->indexModel()->data( index, Qt::DisplayRole ).toString();
        QMap<QString, QUrl> links = mHelpEngine->indexModel()->linksForKeyword( keyword );
        url = links.isEmpty() ? url : links.begin().value();
        aCopy->setEnabled( index.isValid() );
        aSelectAll->setEnabled( false );
    }
    else if ( widget->inherits( "QTextBrowser" ) )
    {
        QTextBrowser* textBrowser = qobject_cast<QTextBrowser*>( widget );
        url = mHelpEngine->searchEngine()->resultWidget()->linkAt( pos );
        aCopy->setEnabled( textBrowser->textCursor().hasSelection() );
        aSelectAll->setEnabled( !textBrowser->toPlainText().isEmpty() );
    }
    else
    {
        Q_ASSERT( 0 );
        return;
    }
    
    aOpenUrl->setEnabled( !url.isEmpty() && url.isValid() );
    aOpenUrlNewTab->setEnabled( aOpenUrl->isEnabled() );
    aCopyAnchor->setEnabled( aOpenUrl->isEnabled() );
    
    QAction* action = menu.exec( widget->mapToGlobal( pos ) );
    
    if ( action == aOpenUrl || action == aOpenUrlNewTab )
    {
        if ( widget != mHelpEngine->indexWidget() )
        {
            openUrl( url, action == aOpenUrlNewTab );
        }
        else
        {
            const QModelIndex index = mHelpEngine->indexWidget()->indexAt( pos );
            const QString keyword = mHelpEngine->indexModel()->data( index, Qt::DisplayRole ).toString();
            QMap<QString, QUrl> links = mHelpEngine->indexModel()->linksForKeyword( keyword );
            openUrls( links, keyword, action == aOpenUrlNewTab );
        }
    }
    else if ( action == aCopyAnchor )
    {
        if ( widget != mHelpEngine->indexWidget() )
        {
            QApplication::clipboard()->setText( url.toString() );
        }
        else
        {
            const QModelIndex index = mHelpEngine->indexWidget()->indexAt( pos );
            const QString keyword = mHelpEngine->indexModel()->data( index, Qt::DisplayRole ).toString();
            QMap<QString, QUrl> links = mHelpEngine->indexModel()->linksForKeyword( keyword );
            QStringList entries;
            
            foreach ( const QUrl& link, links )
            {
                entries << link.toString();
            }
            
            QApplication::clipboard()->setText( entries.join( "\n" ) );
        }
    }
    else if ( action == aCopy )
    {
        if ( widget == mHelpEngine->contentWidget() )
        {
            const QModelIndex index = mHelpEngine->contentWidget()->indexAt( pos );
            const QHelpContentItem* ci = mHelpEngine->contentModel()->contentItemAt( index );
            QApplication::clipboard()->setText( ci->title() );
        }
        else if ( widget == mHelpEngine->indexWidget() )
        {
            const QModelIndex index = mHelpEngine->indexWidget()->indexAt( pos );
            const QString keyword = mHelpEngine->indexModel()->data( index, Qt::DisplayRole ).toString();
            QApplication::clipboard()->setText( keyword );
        }
        else if ( widget->inherits( "QTextBrowser" ) )
        {
            QTextBrowser* textBrowser = qobject_cast<QTextBrowser*>( widget );
            textBrowser->copy();
        }
    }
    else if ( action == aSelectAll )
    {
        if ( !widget->inherits( "QTextBrowser" ) )
        {
            Q_ASSERT( 0 );
            return;
        }
        
        QTextBrowser* textBrowser = qobject_cast<QTextBrowser*>( widget );
        textBrowser->selectAll();
    }
}

void QtAssistantDock::disableSearchLineEdit()
{
    mLookFor->setDisabled( true );
}

void QtAssistantDock::enableSearchLineEdit()
{
    updateFilters( mHelpEngine->currentFilter() );
    mLookFor->setEnabled( true );
    filterIndices( mLookFor->text() );
}

void QtAssistantDock::filterIndices( const QString& filter )
{
    mHelpEngine->indexWidget()->filterIndices( filter, filter.contains( '*' ) ? filter : QString::null );
}

void QtAssistantDock::searchingStarted()
{
    setCursor( Qt::WaitCursor );
}

void QtAssistantDock::searchingFinished( int hits )
{
    Q_UNUSED( hits )
    unsetCursor();
}

void QtAssistantDock::search()
{
    const QList<QHelpSearchQuery> query = mHelpEngine->searchEngine()->queryWidget()->query();
    mHelpEngine->searchEngine()->search( query );
}

void QtAssistantDock::addBookmark()
{
    QtAssistantViewer* viewer = child()->viewer();
    
    if ( viewer )
    {
        if ( viewer->source().isEmpty() )
        {
            return;
        }
        
        mBookmarkManager->showBookmarkDialog( this, viewer->documentTitle(), viewer->source().toString() );
    }
}

bool QtAssistantDock::isWordCharacter( const QChar& character ) const
{
    return character.isLetterOrNumber() || character.isMark() || character == '_';
}

QString QtAssistantDock::currentWord( const QString& text, int cursorPos ) const
{
    int start = cursorPos;
    int end = cursorPos;
    QString word = text;
    
    while ( isWordCharacter( word[ start ] ) )
    {
        if ( start == 0 || !isWordCharacter( word[ start -1 ] ) )
            break;
        start--;
    }
    
    while ( isWordCharacter( word[ end ] ) )
    {
        if ( end == word.length() -1 || !isWordCharacter( word[ end +1 ] ) )
            break;
        end++;
    }
    
    if ( start != end || isWordCharacter( word[ cursorPos ] ) )
    {
        word = word.mid( start, end -start +1 );
    }
    else
    {
        word.clear();
    }
    
    return word;
}

QString QtAssistantDock::currentWord() const
{
    QWidget* widget = QApplication::focusWidget();
    
    if ( !widget )
    {
        return QString::null;
    }
    
    QString className = widget->metaObject()->className();
    QString selectedText;
    
    if ( className == "QComboBox" )
    {
        QComboBox* cb = qobject_cast<QComboBox*>( widget );
        
        if ( cb->isEditable() )
        {
            widget = cb->lineEdit();
            className = "QLineEdit";
        }
    }
    
    if ( className == "pEditor" )
    {
        pEditor* editor = qobject_cast<pEditor*>( widget );
        QString tab = QString( "" ).fill( ' ', editor->tabWidth() );
        
        if ( editor->hasSelectedText() )
        {
            selectedText = editor->selectedText().replace( "\t", tab );
            selectedText = currentWord( selectedText, 0 );
        }
        else
        {
            selectedText = editor->currentLineText().replace( "\t", tab );
            selectedText = currentWord( selectedText, editor->cursorPosition().x() );
        }
    }
    else if ( className == "QLineEdit" )
    {
        QLineEdit* lineedit = qobject_cast<QLineEdit*>( widget );
        
        if ( lineedit->hasSelectedText() )
        {
            selectedText = currentWord( lineedit->selectedText(), 0 );
        }
        else
        {
            selectedText = currentWord( lineedit->text(), lineedit->cursorPosition() );
        }
    }
    
    return selectedText;
}

void QtAssistantDock::keywordHelp()
{
    const QString selectedText = currentWord();
    
    if ( !selectedText.isEmpty() )
    {
        mLookFor->setText( selectedText );
        mHelpEngine->indexWidget()->activateCurrentItem();
        
        if ( !mHelpEngine->indexWidget()->currentIndex().isValid() )
        {
            MonkeyCore::messageManager()->appendMessage( tr( "No help found for: %1" ).arg( selectedText ) );
        }
    }
}

void QtAssistantDock::searchHelp()
{
    const QString selectedText = currentWord();
    
    if ( !selectedText.isEmpty() )
    {
        QHelpSearchQuery query( QHelpSearchQuery::DEFAULT, QStringList( selectedText ) );
        mHelpEngine->searchEngine()->search( QList<QHelpSearchQuery>() << query );
        aSearch->trigger();
        show();
    }
}
