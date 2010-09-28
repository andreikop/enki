#include "QtAssistantChild.h"
#include "QtAssistantViewer.h"
#include "QtAssistantInlineSearch.h"

#include <objects/pIconManager.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pQueuedMessageToolBar.h>

#include <QVBoxLayout>
#include <QTabWidget>
#include <QWebFrame>
#include <QPrintDialog>
#include <QComboBox>
#include <QWebHistory>
#include <QCheckBox>
#include <QLabel>
#include <QLineEdit>
#include <QHelpEngine>
#include <QToolButton>
#include <QPrinter>
#include <QDebug>

QtAssistantChild* QtAssistantChild::instance( QHelpEngine* engine, QWidget* parent, bool create )
{
    static QPointer<QtAssistantChild> _instance = 0;

    if ( !_instance && create )
    {
        _instance = new QtAssistantChild( engine, parent );
    }

    return _instance;
}

QtAssistantChild::QtAssistantChild( QHelpEngine* engine, QWidget* parent )
    : pAbstractChild( parent )
{
    Q_ASSERT( engine );

    mEngine = engine;
    twPages = new QTabWidget( this );
    twPages->setDocumentMode( true );
    twPages->setTabsClosable( true );
    isSearch = new QtAssistantInlineSearch( this );
    isSearch->setVisible( false );
    QWidget* wCentral = new QWidget( this );
    QVBoxLayout* centralLayout = new QVBoxLayout( wCentral );
    centralLayout->setMargin( 0 );
    centralLayout->setSpacing( 6 );
    centralLayout->addWidget( twPages );
    centralLayout->addWidget( isSearch );
    setWidget( wCentral );

    setWindowIcon( pIconManager::icon( "QtAssistant.png", ":/assistant-icons" ) );
    setFilePath( "Qt Assistant" );

    // actions
    cbUrl = new QComboBox( this );
    cbUrl->setSizePolicy( QSizePolicy( QSizePolicy::Expanding, QSizePolicy::Preferred ) );
    cbUrl->setEditable( true );

    aPrevious = new QAction( pIconManager::icon( "previous.png", ":/assistant-icons" ), tr( "Previous page" ), this );
    aNext = new QAction( pIconManager::icon( "next.png", ":/assistant-icons" ), tr( "Next page" ), this );
    aHome = new QAction( pIconManager::icon( "home.png", ":/assistant-icons" ), tr( "Home page" ), this );
    aSearchText = new QAction( pIconManager::icon( "search.png", ":/assistant-icons" ), tr( "Fint in text" ), this );
    aZoomIn = new QAction( pIconManager::icon( "zoomin.png", ":/assistant-icons" ), tr( "Zoom in" ), this );
    aZoomOut = new QAction( pIconManager::icon( "zoomout.png", ":/assistant-icons" ), tr( "Zoom out" ), this );
    aZoomReset = new QAction( pIconManager::icon( "resetzoom.png", ":/assistant-icons" ), tr( "Zoom reset" ), this );
    aAddNewPage = new QAction( pIconManager::icon( "addtab.png", ":/assistant-icons" ), tr( "Add new page" ), this );
    aAddNewPage->setEnabled( false );
    aNextTab = new QAction( pIconManager::icon( "nexttab.png", ":/assistant-icons" ), tr( "Next tab" ), this );
    aPreviousTab = new QAction( pIconManager::icon( "previoustab.png", ":/assistant-icons" ), tr( "Previous tab" ), this );

    // corner widgets
    tbCloneTab = new QToolButton( this );
    tbCloneTab->setAutoRaise( true );
    tbCloneTab->setDefaultAction( aAddNewPage );
    twPages->setCornerWidget( tbCloneTab, Qt::TopLeftCorner );

    mFirstOpenUrl = true;

    // connections
    connect( aPrevious, SIGNAL( triggered() ), this, SLOT( previousPage() ) );
    connect( aNext, SIGNAL( triggered() ), this, SLOT( nextPage() ) );
    connect( aHome, SIGNAL( triggered() ), this, SLOT( homePage() ) );
    connect( aZoomIn, SIGNAL( triggered() ), this, SLOT( zoomIn() ) );
    connect( aZoomOut, SIGNAL( triggered() ), this, SLOT( zoomOut() ) );
    connect( aZoomReset, SIGNAL( triggered() ), this, SLOT( zoomReset() ) );
    connect( aSearchText, SIGNAL( triggered() ), this, SLOT( invokeSearch() ) );
    connect( aPreviousTab, SIGNAL( triggered() ), this, SLOT( previousTab() ) );
    connect( aNextTab, SIGNAL( triggered() ), this, SLOT( nextTab() ) );
    connect( aAddNewPage, SIGNAL( triggered() ), this, SLOT( cloneTab() ) );
    connect( cbUrl, SIGNAL( currentIndexChanged( int ) ), this, SLOT( cbUrl_currentIndexChanged( int ) ) );
    connect( isSearch->toolNext, SIGNAL( clicked() ), this, SLOT( findNext() ) );
    connect( isSearch->editFind, SIGNAL( returnPressed() ), this, SLOT( findNext() ) );
    connect( isSearch->editFind, SIGNAL( textChanged( const QString& ) ), this, SLOT( findCurrentText( const QString& ) ) );
    connect( isSearch->toolPrevious, SIGNAL( clicked() ), this, SLOT( findPrevious() ) );
    connect( twPages, SIGNAL( currentChanged( int ) ), this, SLOT( updateContextActions() ) );
    connect( twPages, SIGNAL( tabCloseRequested( int ) ), this, SLOT( closeTab( int ) ) );

    updateContextActions();
    restoreSession();
}

QtAssistantChild::~QtAssistantChild()
{
    saveSession();
}

QString QtAssistantChild::context() const
{
    return PLUGIN_NAME;
}

void QtAssistantChild::initializeContext( QToolBar* tb )
{
    tb->addAction( aPrevious );
    tb->addAction( aNext );
    tb->addAction( aHome );
    tb->addSeparator();
    tb->addAction( aZoomIn );
    tb->addAction( aZoomOut );
    tb->addAction( aZoomReset );
    tb->addAction( aSearchText );
    tb->addAction( aPreviousTab );
    tb->addAction( aNextTab );
    tb->addSeparator();
    tb->addWidget( cbUrl ); // QToolBar take ownership of added widgets.
}

QPoint QtAssistantChild::cursorPosition() const
{
    return QPoint( -1, -1 );
}

pEditor* QtAssistantChild::editor() const
{
    return 0;
}

bool QtAssistantChild::isModified() const
{
    return false;
}

bool QtAssistantChild::isUndoAvailable() const
{
    QtAssistantViewer* viewer = this->viewer();
    return viewer ? viewer->pageAction( QWebPage::Undo )->isEnabled() : false;
}

bool QtAssistantChild::isRedoAvailable() const
{
    QtAssistantViewer* viewer = this->viewer();
    return viewer ? viewer->pageAction( QWebPage::Redo )->isEnabled() : false;
}

bool QtAssistantChild::isCopyAvailable() const
{
    QtAssistantViewer* viewer = this->viewer();
    return viewer ? viewer->pageAction( QWebPage::Copy )->isEnabled() : false;
}

bool QtAssistantChild::isPasteAvailable() const
{
    QtAssistantViewer* viewer = this->viewer();
    return viewer ? viewer->pageAction( QWebPage::Paste )->isEnabled() : false;
}

bool QtAssistantChild::isGoToAvailable() const
{
    return false;
}

bool QtAssistantChild::isPrintAvailable() const
{
    return true;
}

QtAssistantViewer* QtAssistantChild::viewer( int index ) const
{
    return qobject_cast<QtAssistantViewer*>( twPages->widget( index == -1 ? twPages->currentIndex() : index ) );
}

QtAssistantViewer* QtAssistantChild::newEmptyViewer( qreal zoom )
{
    QtAssistantViewer* viewer = new QtAssistantViewer( mEngine, this );

    if ( mEngine->customValue( QLatin1String( "useBrowserFont" ) ).toBool() )
    {
        QFont font = qVariantValue<QFont>( mEngine->customValue( QLatin1String( "browserFont" ) ) );
        viewer->setFont( font );
    }

    viewer->setTextSizeMultiplier( zoom );

    twPages->addTab( viewer, tr( "Loading..." ) );
    twPages->setCurrentWidget( viewer );

    connect( viewer, SIGNAL( sourceChanged( const QUrl& ) ), this, SLOT( viewer_sourceChanged( const QUrl& ) ) );
    connect( viewer, SIGNAL( actionsChanged() ), this, SLOT( viewer_actionsChanged() ) );

    return viewer;
}

void QtAssistantChild::find( QString ttf, bool forward, bool backward )
{
    QtAssistantViewer* viewer = this->viewer();
    QPalette pal = isSearch->editFind->palette();
    pal.setColor( QPalette::Active, QPalette::Base, Qt::white );

    Q_UNUSED( backward )

    if ( viewer )
    {
        QWebPage::FindFlags options;

        if ( !forward )
        {
            options |= QWebPage::FindBackward;
        }

        if ( isSearch->checkCase->isChecked() )
        {
            options |= QWebPage::FindCaseSensitively;
        }

        bool found = viewer->findText( ttf, options );
        isSearch->labelWrapped->hide();

        if ( !found )
        {
            options |= QWebPage::FindWrapsAroundDocument;
            found = viewer->findText( ttf, options );

            if ( !found )
            {
                pal.setColor( QPalette::Active, QPalette::Base, QColor( 255, 102, 102 ) );
            }
            else
            {
                isSearch->labelWrapped->show();
            }
        }
    }

    if ( !isSearch->isVisible() )
    {
        isSearch->show();
    }

    isSearch->editFind->setPalette( pal );
}

void QtAssistantChild::undo()
{
    QtAssistantViewer* viewer = this->viewer();
    if ( viewer ) viewer->triggerPageAction( QWebPage::Undo );
}

void QtAssistantChild::redo()
{
    QtAssistantViewer* viewer = this->viewer();
    if ( viewer ) viewer->triggerPageAction( QWebPage::Redo );
}

void QtAssistantChild::cut()
{
    QtAssistantViewer* viewer = this->viewer();
    if ( viewer ) viewer->triggerPageAction( QWebPage::Cut );
}

void QtAssistantChild::copy()
{
    QtAssistantViewer* viewer = this->viewer();
    if ( viewer ) viewer->triggerPageAction( QWebPage::Copy );
}

void QtAssistantChild::paste()
{
    QtAssistantViewer* viewer = this->viewer();
    if ( viewer ) viewer->triggerPageAction( QWebPage::Paste );
}

void QtAssistantChild::goTo()
{
}

void QtAssistantChild::goTo( const QPoint& pos, int selectionLength )
{
    Q_UNUSED( pos );
    Q_UNUSED( selectionLength );
}

void QtAssistantChild::invokeSearch()
{
    QtAssistantViewer* viewer = this->viewer();

    if ( viewer )
    {
        isSearch->show();
        isSearch->editFind->selectAll();
        isSearch->editFind->setFocus( Qt::ShortcutFocusReason );
    }
}

void QtAssistantChild::saveFile()
{
}

void QtAssistantChild::backupFileAs( const QString& fileName )
{
    QtAssistantViewer* viewer = this->viewer();

    if ( !viewer )
    {
        return;
    }

    QFile file( fileName );

    if ( !file.open( QIODevice::WriteOnly ) )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "Can't open file for writing when creating backup file." ) );
        return;
    }

    file.resize( 0 );
    QTextCodec* codec = this->codec();
    const QByteArray data = codec->fromUnicode( viewer->page()->mainFrame()->toHtml() );

    if ( file.write( data ) == -1 )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "Can't write file content when creating backup." ) );
    }

    file.close();
}

bool QtAssistantChild::openFile( const QString& fileName, const QString& codec )
{
    Q_UNUSED( fileName );
    Q_UNUSED( codec );
    /*
    for ( int i = 1; i < twPages->count(); i++ )
    {
        QtAssistantViewer* viewer = this->viewer( i );

        if ( viewer->source() == QUrl( fileName ) )
        {
            twPages->setCurrentWidget( viewer );
            return true;
        }
    }

    openUrlInNewTab( QUrl( fileName ) );
    return true;
    */
    return false;
}

void QtAssistantChild::closeFile()
{
    setFilePath( QString::null );
    emit fileClosed();
}

void QtAssistantChild::reload()
{
    emit fileReloaded();
}

void QtAssistantChild::printFile()
{
    QtAssistantViewer* viewer = this->viewer();

    if ( !viewer )
    {
        return;
    }

    QPrinter printer( QPrinter::HighResolution );
    QPrintDialog dlg( &printer, this );
    dlg.addEnabledOption( QAbstractPrintDialog::PrintPageRange );
    dlg.addEnabledOption( QAbstractPrintDialog::PrintCollateCopies );
    dlg.setWindowTitle( tr( "Print Document" ) );

    if ( dlg.exec() == QDialog::Accepted )
    {
        viewer->print( &printer );
    }
}

void QtAssistantChild::quickPrintFile()
{
    QtAssistantViewer* viewer = this->viewer();

    if ( !viewer )
    {
        return;
    }

    QPrinter printer( QPrinter::HighResolution );

    if ( printer.printerName().isEmpty() )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "There is no default printer, please set one before trying quick print" ) );
    }
    else
    {
        viewer->print( &printer );
    }
}

void QtAssistantChild::openUrl( const QUrl& url )
{
    QtAssistantViewer* viewer = this->viewer();

    if ( viewer && !mFirstOpenUrl )
    {
        viewer->setSource( url );
    }
    else
    {
        mFirstOpenUrl = false;
        openUrlInNewTab( url );
    }
}

void QtAssistantChild::openUrlInNewTab( const QUrl& url )
{
    QtAssistantViewer* viewer = newEmptyViewer();
    viewer->setSource( url );
}

void QtAssistantChild::cloneTab()
{
    QtAssistantViewer* viewer = this->viewer();

    if ( viewer )
    {
        const QUrl url = viewer->source();
        newEmptyViewer()->setSource( url );
    }
}

void QtAssistantChild::closeTab( int index )
{
    delete twPages->widget( index );
}

void QtAssistantChild::focusCurrentTab()
{
    if ( MonkeyCore::workspace()->currentDocument() == this )
    {
        if ( twPages->currentWidget() )
        {
            twPages->currentWidget()->setFocus();
        }
    }
}

void QtAssistantChild::saveSession()
{
    QString zoomCount;
    QString currentPages;
    QLatin1Char sep( '|' );

    for ( int i = 0; i < twPages->count(); ++i )
    {
        QtAssistantViewer* viewer = this->viewer( i );

        if ( !viewer->source().isEmpty() && viewer->source().isValid() )
        {
            currentPages.append( viewer->source().toString() ).append( sep );
            zoomCount.append( QString::number( viewer->textSizeMultiplier() ) ).append( sep );
        }
    }

    mEngine->setCustomValue( QLatin1String( "LastTabPage" ), twPages->currentIndex() );
    mEngine->setCustomValue( QLatin1String( "LastShownPages" ), currentPages );
    mEngine->setCustomValue( QLatin1String( "LastPagesZoomWebView" ), zoomCount );
}

void QtAssistantChild::restoreSession()
{
    QLatin1String zoom( "LastPagesZoomWebView" );
    const QStringList lastShownPageList = mEngine->customValue( QLatin1String( "LastShownPages" ) ).toString().split( QLatin1Char( '|' ), QString::SkipEmptyParts );

    if ( !lastShownPageList.isEmpty() )
    {
        QVector<QString> zoomList = mEngine->customValue( zoom ).toString().split( QLatin1Char( '|' ), QString::SkipEmptyParts ).toVector();

        if ( zoomList.isEmpty() )
        {
            zoomList.fill( QLatin1String( "1.0" ), lastShownPageList.size() );
        }

        if ( zoomList.count() < lastShownPageList.count() )
        {
            for ( int i = 0; i < lastShownPageList.count(); i++ )
            {
                zoomList << QLatin1String( "1.0" );
            }
        }
        else
        {
            zoomList.resize( lastShownPageList.count() );
        }

        QVector<QString>::const_iterator zIt = zoomList.constBegin();
        QStringList::const_iterator it = lastShownPageList.constBegin();

        for ( ; it != lastShownPageList.constEnd(); ++it, ++zIt )
        {
            QtAssistantViewer* viewer = newEmptyViewer( (*zIt).toFloat() );
            viewer->setSource( (*it) );
        }

        twPages->setCurrentIndex( mEngine->customValue( QLatin1String( "LastTabPage" ), 0 ).toInt() );
    }
    /*
    else
        openUrl( QUrl( QLatin1String( "help" ) ) );
    */
}

void QtAssistantChild::previousTab()
{
    int index = twPages->currentIndex() -1;
    twPages->setCurrentIndex( index >= 0 ? index : twPages->count() -1 );
}

void QtAssistantChild::nextTab()
{
    int index = twPages->currentIndex();
    twPages->setCurrentIndex( index < twPages->count() -1 ? index +1 : 0 );
}

void QtAssistantChild::previousPage()
{
    viewer()->back();
    updateContextActions();
}

void QtAssistantChild::nextPage()
{
    viewer()->forward();
    updateContextActions();
}

void QtAssistantChild::homePage()
{
    viewer()->home();
}

void QtAssistantChild::zoomIn()
{
    viewer()->zoomIn();
}

void QtAssistantChild::zoomOut()
{
    viewer()->zoomOut();
}

void QtAssistantChild::zoomReset()
{
    viewer()->resetZoom();
}

void QtAssistantChild::findNext()
{
    find( isSearch->editFind->text(), true, false );
}

void QtAssistantChild::findPrevious()
{
    find( isSearch->editFind->text(), false, true );
}

void QtAssistantChild::findCurrentText(const QString &text)
{
    find( text, false, false );
}

void QtAssistantChild::updateContextActions()
{
    QtAssistantViewer* viewer = this->viewer();

    aAddNewPage->setEnabled( viewer );
    aPrevious->setEnabled( viewer && twPages->currentWidget() == viewer ? viewer->isBackwardAvailable() : false );
    aNext->setEnabled( viewer && twPages->currentWidget() == viewer ? viewer->isForwardAvailable() : false );
    aHome->setEnabled( viewer && twPages->currentWidget() == viewer ? true : false );
    aZoomIn->setEnabled( viewer && twPages->currentWidget() == viewer ? true : false );
    aZoomOut->setEnabled( viewer && twPages->currentWidget() == viewer ? true : false );
    aZoomReset->setEnabled( viewer && twPages->currentWidget() == viewer ? true : false );
    aSearchText->setEnabled( viewer && twPages->currentWidget() == viewer ? true : false );
    aPreviousTab->setEnabled( twPages->count() > 1 );
    aNextTab->setEnabled( twPages->count() > 1 );

    const bool locked = cbUrl->blockSignals( true );

    cbUrl->clear();

    if ( viewer && twPages->currentWidget() )
    {
        QSet<QString> entries;

        foreach ( const QWebHistoryItem& item, viewer->history()->items() )
        {
            if ( !entries.contains( item.url().toString() ) )
            {
                entries << item.url().toString();
                cbUrl->addItem( item.title(), item.url() );
                cbUrl->setItemData( cbUrl->count() -1, item.url().toString(), Qt::ToolTipRole );
            }
        }

        cbUrl->setCurrentIndex( cbUrl->findData( viewer->history()->currentItem().url() ) );
    }

    cbUrl->blockSignals( locked );

    cbUrl->setEnabled( viewer && twPages->currentWidget() == viewer );

    viewer_actionsChanged();
}

void QtAssistantChild::viewer_sourceChanged( const QUrl& url )
{
    Q_UNUSED( url );
    QtAssistantViewer* viewer = qobject_cast<QtAssistantViewer*>( sender() );
    const int index = twPages->indexOf( viewer );
    twPages->setTabText( index, viewer->documentTitle() );

    if ( twPages->currentWidget() == viewer )
    {
        updateContextActions();
    }
}

void QtAssistantChild::viewer_actionsChanged()
{
    QtAssistantViewer* viewer = qobject_cast<QtAssistantViewer*>( sender() );

    emit undoAvailableChanged( viewer && twPages->currentWidget() == viewer ? viewer->pageAction( QWebPage::Undo )->isEnabled() : false );
    emit redoAvailableChanged( viewer && twPages->currentWidget() == viewer ? viewer->pageAction( QWebPage::Redo )->isEnabled() : false );
    emit pasteAvailableChanged( viewer && twPages->currentWidget() == viewer ? viewer->pageAction( QWebPage::Paste )->isEnabled() : false );
    emit copyAvailableChanged( viewer && twPages->currentWidget() == viewer ? viewer->pageAction( QWebPage::Copy )->isEnabled() : false );
}

void QtAssistantChild::cbUrl_currentIndexChanged( int index )
{
    QtAssistantViewer* viewer = this->viewer();
    QUrl url = cbUrl->itemData( index ).toUrl();
    url = url.isValid() ? url : cbUrl->itemText( index );
    viewer->setSource( url );
}
