#include "SearchWidget.h"
#include "SearchAndReplace.h"
#include "SearchThread.h"
#include "ReplaceThread.h"
#include "SearchResultsDock.h"

#include <coremanager/MonkeyCore.h>
#include <objects/pIconManager.h>
#include <maininterface/UIMain.h>
#include <workspace/pFileManager.h>
#include <xupmanager/core/XUPProjectItem.h>
#include <workspace/pWorkspace.h>
#include <workspace/pAbstractChild.h>
#include <workspace/pChild.h>
#include <qscintillamanager/pEditor.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pMenuBar.h>

#include <QTextCodec>
#include <QFileDialog>
#include <QCompleter>
#include <QDirModel>
#include <QPainter>
#include <QStatusBar>
#include <QProgressBar>
#include <QLineEdit>
#include <QToolButton>
#include <QKeyEvent>

SearchWidget::SearchWidget( SearchAndReplace* plugin, QWidget* parent )
    : QFrame( parent )
{
    Q_ASSERT( plugin );
    mPlugin = plugin;
    
    setupUi( this );
    cbSearch->completer()->setCaseSensitivity( Qt::CaseSensitive );
    cbReplace->completer()->setCaseSensitivity( Qt::CaseSensitive );
    QDirModel* fsModel = new QDirModel( this );
    fsModel->setFilter( QDir::AllDirs | QDir::NoDotAndDotDot );
    cbPath->lineEdit()->setCompleter( new QCompleter( fsModel ) );
#warning QDirModel is deprecated but QCompleter does not yet handle QFileSystemModel - please update when possible.
    cbMask->completer()->setCaseSensitivity( Qt::CaseSensitive );
    pbSearchStop->setVisible( false );
    pbReplaceCheckedStop->setVisible( false );
    
    mProgress = new QProgressBar( this );
    mProgress->setAlignment( Qt::AlignCenter );
    mProgress->setToolTip( tr( "Search in progress..." ) );
    mProgress->setMaximumSize( QSize( 80, 16 ) );
    MonkeyCore::mainWindow()->statusBar()->insertPermanentWidget( 0, mProgress );
    mProgress->setVisible( false );

    // threads
    mSearchThread = new SearchThread( this );
    mReplaceThread = new ReplaceThread( this );

    mDock = 0;
    
    // mode actions
    tbMode = new QToolButton( cbSearch->lineEdit() );
    tbMode->setIcon( pIconManager::icon( "misc.png" ) );
    tbMode->setPopupMode( QToolButton::InstantPopup );
    tbMode->setMenu( MonkeyCore::menuBar()->menu( "mEdit/mSearchReplace" ) );
    tbMode->setCursor( Qt::ArrowCursor );
    tbMode->installEventFilter( this );
    
    // cd up action
    tbCdUp = new QToolButton( cbPath->lineEdit() );
    tbCdUp->setIcon( pIconManager::icon( "go-up.png" ) );
    tbCdUp->setCursor( Qt::ArrowCursor );
    tbCdUp->installEventFilter( this );

    // options actions
    QAction* action;

    action = new QAction( cbCaseSensitive );
    action->setCheckable( true );
    connect( cbCaseSensitive, SIGNAL( toggled( bool ) ), action, SLOT( setChecked( bool ) ) );
    mOptionActions[ SearchAndReplace::OptionCaseSensitive ] = action;
    
    action = new QAction( cbWholeWord );
    action->setCheckable( true );
    connect( cbWholeWord, SIGNAL( toggled( bool ) ), action, SLOT( setChecked( bool ) ) );
    mOptionActions[ SearchAndReplace::OptionWholeWord ] = action;
    
    action = new QAction( cbWrap );
    action->setCheckable( true );
    connect( cbWrap, SIGNAL( toggled( bool ) ), action, SLOT( setChecked( bool ) ) );
    mOptionActions[ SearchAndReplace::OptionWrap ] = action;
    
    action = new QAction( cbRegularExpression );
    action->setCheckable( true );
    connect( cbRegularExpression, SIGNAL( toggled( bool ) ), action, SLOT( setChecked( bool ) ) );
    mOptionActions[ SearchAndReplace::OptionRegularExpression ] = action;
    
    // init default options
    cbWrap->setChecked( true );

    // mac
    pMonkeyStudio::showMacFocusRect( this, false, true );
    pMonkeyStudio::setMacSmallSize( this, true, true );

#ifdef Q_OS_MAC
    const QSize size( 12, 12 );

    foreach ( QAbstractButton* button, findChildren<QAbstractButton*>() )
    {
        button->setIconSize( size );
        button->setFixedHeight( 24 );
    }

    vlMain->setSpacing( 0 );
#endif

    // mask tooltip
    QStringList languages = pMonkeyStudio::availableLanguages();
    
    for ( int i = 0; i < languages.count(); i += 10 )
    {
        languages[ i ].prepend( "\n" );
    }
    
    QString maskToolTip = tr( "Space separated list of wildcards, ie: *.h *.cpp file???.txt\n"
        "You can use language name too so the search will only apply to the language suffixes.\n"
        "Available languages: %1" ).arg( languages.join( ", " ) );
    
    cbMask->setToolTip( maskToolTip );

    // codecs
    QStringList codecs;
    foreach ( const QString& codec, QTextCodec::availableCodecs() )
    {
        codecs << codec;
    }
    codecs.sort();
    cbCodec->addItems( codecs );

    cbCodec->setCurrentIndex( cbCodec->findText( pMonkeyStudio::defaultCodec() ) );

    // connections
    connect( cbSearch->lineEdit(), SIGNAL( textEdited( const QString& ) ), this, SLOT( search_textChanged() ) );
    connect( tbCdUp, SIGNAL( clicked() ), this, SLOT( cdUp_clicked() ) );
    connect( mSearchThread, SIGNAL( started() ), this, SLOT( searchThread_stateChanged() ) );
    connect( mSearchThread, SIGNAL( finished() ), this, SLOT( searchThread_stateChanged() ) );
    connect( mSearchThread, SIGNAL( progressChanged( int, int ) ), this, SLOT( searchThread_progressChanged( int, int ) ) );
    connect( mReplaceThread, SIGNAL( started() ), this, SLOT( replaceThread_stateChanged() ) );
    connect( mReplaceThread, SIGNAL( finished() ), this, SLOT( replaceThread_stateChanged() ) );
    connect( mReplaceThread, SIGNAL( openedFileHandled( const QString&, const QString&, const QString& ) ), this, SLOT( replaceThread_openedFileHandled( const QString&, const QString&, const QString& ) ) );
    connect( mReplaceThread, SIGNAL( error( const QString& ) ), this, SLOT( replaceThread_error( const QString& ) ) );

    setMode( SearchAndReplace::ModeSearch );
}

SearchWidget::~SearchWidget()
{
    delete mSearchThread;
    delete mReplaceThread;
    delete mProgress;
}

SearchAndReplace::Mode SearchWidget::mode() const
{
    return mMode;
}

SearchThread* SearchWidget::searchThread() const
{
    return mSearchThread;
}

void SearchWidget::setResultsDock( SearchResultsDock* dock )
{
    if ( mDock == dock )
    {
        return;
    }

    mDock = dock;

    // connections
    connect( mReplaceThread, SIGNAL( resultsHandled( const QString&, const SearchResultsModel::ResultList& ) ), mDock->model(), SLOT( thread_resultsHandled( const QString&, const SearchResultsModel::ResultList& ) ) );
}

bool SearchWidget::isBinary( QFile& file )
{
    const qint64 position = file.pos();
    file.seek( 0 );
    const bool binary = file.read( 1024 ).contains( '\0' );
    file.seek( position );
    return binary;
}

void SearchWidget::setMode( SearchAndReplace::Mode mode )
{
    mSearchThread->stop();
    mReplaceThread->stop();
    
    bool currentDocumentOnly = false;
    
    // clear search results if needed.
    switch ( mode )
    {
        case SearchAndReplace::ModeSearch:
        case SearchAndReplace::ModeReplace:
            currentDocumentOnly = true;
            break;
        default:
            mSearchThread->clear();
            break;
    }

    mMode = mode;
    
    initializeProperties( currentDocumentOnly );
    
    if ( mMode & SearchAndReplace::ModeFlagProjectFiles )
    {
        if ( mProperties.project )
        {
            const QString codec = mProperties.project->temporaryValue( "codec", pMonkeyStudio::defaultCodec() ).toString();
            
            mProperties.codec = codec;
            cbCodec->setCurrentIndex( cbCodec->findText( codec ) );
        }
    }
    
    Q_ASSERT( !mProperties.codec.isEmpty() );

    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();
    pEditor* editor = document ? document->editor() : 0;
    const QString path = mProperties.project ? mProperties.project->path() : QDir::currentPath();
    const QString searchPath = document ? QFileInfo( document->filePath() ).absolutePath() : path;
    const QString searchText = editor ? editor->selectedText() : QString::null;
    const bool wasVisible = isVisible();

    setVisible( mode != SearchAndReplace::ModeNo );

    if ( isVisible() )
    {
        if ( mProperties.settings.replaceSearchText )
        {
            const bool isRE = mProperties.options & SearchAndReplace::OptionRegularExpression;
            const bool isEmpty = searchText.isEmpty();
            const bool validateVisibility = !mProperties.settings.onlyWhenNotVisible || ( mProperties.settings.onlyWhenNotVisible && !wasVisible );
            const bool validateRegExp = !mProperties.settings.onlyWhenNotRegExp || ( mProperties.settings.onlyWhenNotRegExp && !isRE );
            const bool validateEmpty = !mProperties.settings.onlyWhenNotEmpty || ( mProperties.settings.onlyWhenNotEmpty && !isEmpty );
            
            if ( validateVisibility && validateRegExp && validateEmpty )
            {
                cbSearch->setEditText( searchText );
            }
        }

        if ( mode & SearchAndReplace::ModeFlagSearch )
        {
            cbSearch->setFocus();
            cbSearch->lineEdit()->selectAll();
        }
        else
        {
            cbReplace->setFocus();
            cbReplace->lineEdit()->selectAll();
        }
        
        if ( mode & SearchAndReplace::ModeFlagDirectory )
        {
            cbPath->setEditText( searchPath );
        }
    }

    switch ( mMode )
    {
        case SearchAndReplace::ModeNo:
            wSearch->setVisible( false );
            wReplace->setVisible( false );
            wPath->setVisible( false );
            wOptions->setVisible( false );
            break;
        case SearchAndReplace::ModeSearch:
            wSearch->setVisible( true );
            pbPrevious->setVisible( true );
            pbNext->setVisible( true );
            pbSearch->setVisible( false );

            wReplace->setVisible( false );

            wPath->setVisible( false );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( false );

            wOptions->setVisible( true );
            wMask->setVisible( false );
            wCodec->setVisible( false );
            break;
        case SearchAndReplace::ModeReplace:
            wSearch->setVisible( true );
            pbPrevious->setVisible( true );
            pbNext->setVisible( true );
            pbSearch->setVisible( false );

            wReplace->setVisible( true );

            wPath->setVisible( false );
            pbReplace->setVisible( true );
            pbReplaceAll->setVisible( true );
            pbReplaceChecked->setVisible( false );

            wOptions->setVisible( true );
            wMask->setVisible( false );
            wCodec->setVisible( false );
            break;
        case SearchAndReplace::ModeSearchDirectory:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( false );

            wPath->setVisible( true );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( false );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( true );
            break;
        case SearchAndReplace::ModeReplaceDirectory:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( true );

            wPath->setVisible( true );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( true );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( true );
            break;
        case SearchAndReplace::ModeSearchProjectFiles:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( false );

            wPath->setVisible( false );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( false );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( true );
            break;
        case SearchAndReplace::ModeReplaceProjectFiles:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( true );

            wPath->setVisible( false );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( true );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( true );
            break;
        case SearchAndReplace::ModeSearchOpenedFiles:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( false );

            wPath->setVisible( false );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( false );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( false );
            break;
        case SearchAndReplace::ModeReplaceOpenedFiles:
            wSearch->setVisible( true );
            pbPrevious->setVisible( false );
            pbNext->setVisible( false );
            pbSearch->setVisible( true );

            wReplace->setVisible( true );

            wPath->setVisible( false );
            pbReplace->setVisible( false );
            pbReplaceAll->setVisible( false );
            pbReplaceChecked->setVisible( true );

            wOptions->setVisible( true );
            wMask->setVisible( true );
            wCodec->setVisible( false );
            break;
    }

    updateLabels();
    updateWidgets();
}

bool SearchWidget::eventFilter( QObject* object, QEvent* event )
{
    if ( event->type() == QEvent::Paint )
    {
        QToolButton* toolButton = qobject_cast<QToolButton*>( object );
        QLineEdit* lineEdit = object == tbMode ? cbSearch->lineEdit() : cbPath->lineEdit();
        lineEdit->setContentsMargins( lineEdit->height(), 0, 0, 0 );
        
        const int height = lineEdit->height();
        const QRect availableRect( 0, 0, height, height );
        
        if ( toolButton->rect() != availableRect )
        {
            toolButton->setGeometry( availableRect );
        }
        
        QPainter painter( toolButton );
        toolButton->icon().paint( &painter, availableRect );
        
        return true;
    }
    
    return QWidget::eventFilter( object, event );
}

void SearchWidget::keyPressEvent( QKeyEvent* event )
{
    if ( event->modifiers() == Qt::NoModifier )
    {
        switch ( event->key() )
        {
            case Qt::Key_Escape:
            {
                MonkeyCore::workspace()->focusEditor();
                hide();

                break;
            }
            case Qt::Key_Enter:
            case Qt::Key_Return:
            {
                switch ( mMode )
                {
                    case SearchAndReplace::ModeNo:
                        break;
                    case SearchAndReplace::ModeSearch:
                        pbNext->click();
                        break;
                    case SearchAndReplace::ModeSearchDirectory:
                    case SearchAndReplace::ModeSearchProjectFiles:
                    case SearchAndReplace::ModeSearchOpenedFiles:
                        pbSearch->click();
                        break;
                    case SearchAndReplace::ModeReplace:
                        pbReplace->click();
                        break;
                    case SearchAndReplace::ModeReplaceDirectory:
                    case SearchAndReplace::ModeReplaceProjectFiles:
                    case SearchAndReplace::ModeReplaceOpenedFiles:
                        pbReplaceChecked->click();
                        break;
                }

                break;
            }
        }
    }

    QWidget::keyPressEvent( event );
}

void SearchWidget::updateLabels()
{
    int width = 0;

    if ( lSearch->isVisible() )
    {
        width = qMax( width, lSearch->minimumSizeHint().width() );
    }

    if ( lReplace->isVisible() )
    {
        width = qMax( width, lReplace->minimumSizeHint().width() );
    }

    if ( lPath->isVisible() )
    {
        width = qMax( width, lPath->minimumSizeHint().width() );
    }

    lSearch->setMinimumWidth( width );
    lReplace->setMinimumWidth( width );
    lPath->setMinimumWidth( width );
}

void SearchWidget::updateWidgets()
{
    int width = 0;

    if ( wSearchRight->isVisible() )
    {
        width = qMax( width, wSearchRight->minimumSizeHint().width() );
    }

    if ( wReplaceRight->isVisible() )
    {
        width = qMax( width, wReplaceRight->minimumSizeHint().width() );
    }

    if ( wPathRight->isVisible() )
    {
        width = qMax( width, wPathRight->minimumSizeHint().width() );
    }

    wSearchRight->setMinimumWidth( width );
    wReplaceRight->setMinimumWidth( width );
    wPathRight->setMinimumWidth( width );
}

void SearchWidget::updateComboBoxes()
{
    const QString searchText = cbSearch->currentText();
    const QString replaceText = cbReplace->currentText();
    const QString maskText = cbMask->currentText();
    int index;
    
    // search
    if ( !searchText.isEmpty() )
    {
        index = cbSearch->findText( searchText );
        
        if ( index == -1 )
        {
            cbSearch->addItem( searchText );
        }
    }
    
    // replace
    if ( !replaceText.isEmpty() )
    {
        index = cbReplace->findText( replaceText );
        
        if ( index == -1 )
        {
            cbReplace->addItem( replaceText );
        }
    }
    
    // mask
    if ( !maskText.isEmpty() )
    {
        index = cbMask->findText( maskText );
        
        if ( index == -1 )
        {
            cbMask->addItem( maskText );
        }
    }
}

void SearchWidget::initializeProperties( bool currentDocumentOnly )
{
    const QMap<QString, QStringList> suffixes = pMonkeyStudio::availableLanguagesSuffixes();
    const QStringList keys = suffixes.keys();
    mProperties.searchText = cbSearch->currentText();
    mProperties.replaceText = cbReplace->currentText();
    mProperties.searchPath = cbPath->currentText();
    mProperties.mode = mMode;
    mProperties.mask.clear();
    mProperties.codec = cbCodec->currentText();
    mProperties.options = SearchAndReplace::Options( SearchAndReplace::ModeNo );
    mProperties.openedFiles.clear();
    mProperties.project = MonkeyCore::fileManager()->currentProject();
    mProperties.sourcesFiles.clear();
    mProperties.settings = mPlugin->settings();

    // update masks
    foreach ( const QString& part, cbMask->currentText().split( " ", QString::SkipEmptyParts ) )
    {
        const int index = keys.indexOf( QRegExp( QRegExp::escape( part ), Qt::CaseInsensitive ) );

        if ( index != -1 )
        {
            foreach ( const QString& suffixe, suffixes[ keys.at( index ) ] )
            {
                if ( !mProperties.mask.contains( suffixe ) )
                {
                    mProperties.mask << suffixe;
                }
            }
        }
        else
        {
            mProperties.mask << part;
        }
    }
    
    // set default mask if needed
    if ( mProperties.mask.isEmpty() )
    {
        mProperties.mask << "*";
    }

    // update options
    foreach ( const SearchAndReplace::Option& option, mOptionActions.keys() )
    {
        QAction* action = mOptionActions[ option ];

        if ( action->isChecked() )
        {
            mProperties.options |= option;
        }
    }
    
    // update project
    mProperties.project = mProperties.project ? mProperties.project->topLevelProject() : 0;
    
    if ( currentDocumentOnly )
    {
        return;
    }

    // update opened files
    foreach ( pAbstractChild* document, MonkeyCore::workspace()->documents() )
    {
        mProperties.openedFiles[ document->filePath() ] = document->fileBuffer();
    }

    // update sources files
    mProperties.sourcesFiles = mProperties.project ? mProperties.project->topLevelProjectSourceFiles() : QStringList();
}

void SearchWidget::showMessage( const QString& status )
{
    if ( status.isEmpty() )
    {
        MonkeyCore::mainWindow()->statusBar()->clearMessage();
    }
    else
    {
        MonkeyCore::mainWindow()->statusBar()->showMessage( status, 30000 );
    }
}

void SearchWidget::setState( SearchWidget::InputField field, SearchWidget::State state )
{
    QWidget* widget = 0;
    QColor color = QColor( Qt::white );

    switch ( field )
    {
        case SearchWidget::Search:
            widget = cbSearch->lineEdit();
            break;
        case SearchWidget::Replace:
            widget = cbReplace->lineEdit();
            break;
    }

    switch ( state )
    {
        case SearchWidget::Normal:
            color = QColor( Qt::white );
            break;
        case SearchWidget::Good:
            color = QColor( Qt::green );
            break;
        case SearchWidget::Bad:
            color = QColor( Qt::red );
            break;
    }

    QPalette pal = widget->palette();
    pal.setColor( widget->backgroundRole(), color );
    widget->setPalette( pal );
}

bool SearchWidget::searchFile( bool forward, bool incremental )
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();
    pChild* child = document ? static_cast<pChild*>( document ) : 0;
    pEditor* editor = child ? child->editor() : 0;

    if ( !editor )
    {
        setState( SearchWidget::Search, SearchWidget::Bad );
        showMessage( tr( "No active editor" ) );
        return false;
    }

    // get cursor position
    const bool isRE = mProperties.options & SearchAndReplace::OptionRegularExpression;
    const bool isCS = mProperties.options & SearchAndReplace::OptionCaseSensitive;
    const bool isWW = mProperties.options & SearchAndReplace::OptionWholeWord;
    const bool isWrap = mProperties.options & SearchAndReplace::OptionWrap;
    int x, y, temp;
    
    if ( forward ) {
        if ( incremental ) {
            editor->getSelection( &y, &x, &temp, &temp );
        }
        else {
            editor->getSelection( &temp, &temp, &y, &x );
        }
    }
    else {
        if ( incremental ) {
            editor->getSelection( &temp, &temp, &y, &x );
        }
        else {
            editor->getSelection( &y, &x, &temp, &temp );
        }
    }

    // search
    const bool found = editor->findFirst( mProperties.searchText, isRE, isCS, isWW, isWrap, forward, y, x, true );

    // change background acording to found or not
    setState( SearchWidget::Search, found ? SearchWidget::Good : SearchWidget::Bad );

    // show message if needed
    showMessage( found ? QString::null : tr( "Not Found" ) );

    // return found state
    return found;
}

bool SearchWidget::replaceFile( bool all )
{
    pAbstractChild* document = MonkeyCore::workspace()->currentDocument();
    pChild* child = document ? static_cast<pChild*>( document ) : 0;
    pEditor* editor = child ? child->editor() : 0;

    if ( !editor )
    {
        setState( SearchWidget::Search, SearchWidget::Bad );
        showMessage( tr( "No active editor" ) );
        return false;
    }

    int count = 0;
    
    if ( all )
    {
        const bool isWrap = mProperties.options & SearchAndReplace::OptionWrap;
        int x, y;

        editor->getCursorPosition( &y, &x );

        if ( isWrap )
        {
            // don't need to give wrap parameter for search as we start at begin of document
            editor->setCursorPosition( 0, 0 );
            mProperties.options &= ~SearchAndReplace::OptionWrap;
        }

        editor->beginUndoAction();
        
        while ( searchFile( true, false ) ) // search next
        {
            editor->replace( mProperties.replaceText );
            count++;
        }

        editor->endUndoAction();
        editor->setCursorPosition( y, x ); // restore cursor position
        
        // restore wrap property if needed
        if ( isWrap )
        {
            mProperties.options |= SearchAndReplace::OptionWrap;
        }
    }
    else
    {
        int x, y, temp;

        editor->getSelection( &y, &x, &temp, &temp );
        editor->setCursorPosition( y, x );

        if ( searchFile( true, false ) )
        {
            editor->beginUndoAction();
            editor->replace( mProperties.replaceText );
            editor->endUndoAction();
            count++;
            pbNext->click(); // move selection to next item
        }
    }

    showMessage( tr( "%1 occurrence(s) replaced." ).arg( count ) );

    return true;
}

void SearchWidget::searchThread_stateChanged()
{
    pbSearchStop->setVisible( mSearchThread->isRunning() );
    updateWidgets();
    mProgress->setVisible( mSearchThread->isRunning() );
}

void SearchWidget::searchThread_progressChanged( int value, int total )
{
    mProgress->setValue( value );
    mProgress->setMaximum( total );
}

void SearchWidget::replaceThread_stateChanged()
{
    pbReplaceCheckedStop->setVisible( mReplaceThread->isRunning() );
    updateWidgets();
}

void SearchWidget::replaceThread_openedFileHandled( const QString& fileName, const QString& content, const QString& codec )
{
    pAbstractChild* document = MonkeyCore::fileManager()->openFile( fileName, codec );
    pEditor* editor = document->editor();

    Q_ASSERT( editor );

    editor->beginUndoAction();
    editor->selectAll();
    editor->removeSelectedText();
    editor->insert( content );
    editor->endUndoAction();
}

void SearchWidget::replaceThread_error( const QString& error )
{
    MonkeyCore::messageManager()->appendMessage( error );
}

void SearchWidget::search_textChanged()
{
    initializeProperties( true );
    
    // clear search results if needed.
    switch ( mMode )
    {
        case SearchAndReplace::ModeSearch:
            searchFile( true, true );
        case SearchAndReplace::ModeReplace:
            break;
        default:
            mSearchThread->clear();
            break;
    }
}

void SearchWidget::cdUp_clicked()
{
    QDir dir( cbPath->currentText() );
    
    if ( !dir.exists() )
    {
        return;
    }
    
    dir.cdUp();
    
    cbPath->setEditText( dir.absolutePath() );
}

void SearchWidget::on_pbPrevious_clicked()
{
    updateComboBoxes();
    initializeProperties( true );
    searchFile( false, false );
}

void SearchWidget::on_pbNext_clicked()
{
    updateComboBoxes();
    initializeProperties( true );
    searchFile( true, false );
}

void SearchWidget::on_pbSearch_clicked()
{
    setState( SearchWidget::Search, SearchWidget::Normal );
    updateComboBoxes();
    initializeProperties( false );
    
    if ( mProperties.searchText.isEmpty() )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "You can't search for NULL text." ) );
        return;
    }
    
    if ( mProperties.mode & SearchAndReplace::ModeFlagProjectFiles && !mProperties.project )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "You can't search in project files because there is no opened projet." ) );
        return;
    }
    
    mSearchThread->search( mProperties );
}

void SearchWidget::on_pbSearchStop_clicked()
{
    mSearchThread->stop();
}

void SearchWidget::on_pbReplace_clicked()
{
    updateComboBoxes();
    initializeProperties( true );
    replaceFile( false );
}

void SearchWidget::on_pbReplaceAll_clicked()
{
    updateComboBoxes();
    initializeProperties( true );
    replaceFile( true );
}

void SearchWidget::on_pbReplaceChecked_clicked()
{
    QHash<QString, SearchResultsModel::ResultList> items;
    SearchResultsModel* model = mDock ? mDock->model() : 0;

    Q_ASSERT( model );

    updateComboBoxes();
    initializeProperties( false );
    
    if ( mProperties.mode & SearchAndReplace::ModeFlagProjectFiles && !mProperties.project )
    {
        MonkeyCore::messageManager()->appendMessage( tr( "You can't replace in project files because there is no opened projet." ) );
        return;
    }

    foreach ( const SearchResultsModel::ResultList& results, model->results() )
    {
        foreach ( SearchResultsModel::Result* result, results )
        {
            if ( result->enabled && result->checkState == Qt::Checked )
            {
                items[ result->fileName ] << result;
            }
            else
            {
                const QModelIndex index = mDock->model()->index( result );
                mDock->model()->setData( index, false, SearchResultsModel::EnabledRole );
            }
        }
    }

    mReplaceThread->replace( mProperties, items );
}

void SearchWidget::on_pbReplaceCheckedStop_clicked()
{
    mReplaceThread->stop();
}

void SearchWidget::on_pbBrowse_clicked()
{
    const QString path = QFileDialog::getExistingDirectory( this, tr( "Search path" ), cbPath->currentText() );

    if ( !path.isEmpty() )
    {
        cbPath->setEditText( path );
    }
}
