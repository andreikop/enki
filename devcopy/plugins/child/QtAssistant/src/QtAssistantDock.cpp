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

QtAssistantDock.QtAssistantDock( QWidget* parent )
    : pDockWidget( parent )
    setObjectName( "QtAssistantDock" )
    setWindowTitle( "Qt Assistant" )
    setWindowIcon( pIconManager.icon( "QtAssistant.png", ":/assistant-icons" ) )
    
    # create help engine with default collection
    MkSQtDocInstaller.collectionFileDirectory( True )
    mHelpEngine = QHelpEngine( MkSQtDocInstaller.defaultHelpCollectionFileName(), self )
    
    # create bookmarks manager
    mBookmarkManager = BookmarkManager( mHelpEngine )
    mBookmarkManager.setupBookmarkModels()
    bwBookmarks = BookmarkWidget( mBookmarkManager, self )
    bwBookmarks.layout().setMargin( 0 )
#ifdef Q_WS_MAC
    bwBookmarks.layout().setSpacing( 5 )
#else:
    bwBookmarks.layout().setSpacing( 3 )
#endif
    
    # areas
    setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
    
    # actions
    aContents = QAction( pIconManager.icon( "contents.png", ":/assistant-icons" ), tr( "Contents" ), self )
    aContents.setToolTip( aContents.text() )
    aContents.setCheckable( True )
    aContents.setData( 0 )
    titleBar().addAction( aContents, 0 )
    
    aIndex = QAction( pIconManager.icon( "index.png", ":/assistant-icons" ), tr( "Index" ), self )
    aIndex.setToolTip( aIndex.text() )
    aIndex.setCheckable( True )
    aIndex.setData( 1 )
    titleBar().addAction( aIndex, 1 )
    
    aBookmarks = QAction( pIconManager.icon( "bookmarks.png", ":/assistant-icons" ), tr( "Bookmarks" ), self )
    aBookmarks.setToolTip( aBookmarks.text() )
    aBookmarks.setCheckable( True )
    aBookmarks.setData( 2 )
    titleBar().addAction( aBookmarks, 2 )
    
    titleBar().addSeparator( 3 )
    
    aSearch = QAction( pIconManager.icon( "search.png", ":/assistant-icons" ), tr( "Search" ), self )
    aSearch.setToolTip( aSearch.text() )
    aSearch.setCheckable( True )
    aSearch.setData( 3 )
    titleBar().addAction( aSearch, 4 )
    
    aShow = QAction( pIconManager.icon( "QtAssistant.png", ":/assistant-icons" ), tr( "Show Assistant" ), self )
    aShow.setToolTip( aShow.text() )
    titleBar().addAction( aShow, 5 )
    
    aFilter = QAction( pIconManager.icon( "filter.png", ":/assistant-icons" ), tr( "Filter" ), self )
    aFilter.setToolTip( aFilter.text() )
    mFilters = QMenu( self )
    tb = qobject_cast<QToolButton*>( titleBar().addAction( aFilter, 6 ) )
    tb.setPopupMode( QToolButton.InstantPopup )
    aFilter.setMenu( mFilters )
    
    titleBar().addSeparator( 7 )
    
    aPagesGroup = QActionGroup( self )
    aPagesGroup.addAction( aContents )
    aPagesGroup.addAction( aIndex )
    aPagesGroup.addAction( aBookmarks )
    aPagesGroup.addAction( aSearch )
    
    aFilterGroup = QActionGroup( self )
    updateFilters( mHelpEngine.currentFilter() )
    
    # stacked
    wCentral = QWidget( self )
    stackedLayout = QVBoxLayout( wCentral )
    
    mStacked = QStackedWidget( self )
    mProgress = QProgressBar( self )
    mProgress.setRange( 0, 0 )
    mProgress.setAlignment( Qt.AlignCenter )
    mProgress.setTextVisible( False )
    mProgress.setVisible( False )
    
    stackedLayout.addWidget( mStacked )
    stackedLayout.addWidget( mProgress )
    
    setWidget( wCentral )
    
    # pages
    wContents = mHelpEngine.contentWidget()
    wBookmarks = bwBookmarks
    
    wIndex = QWidget( self )
    indexLayout = QVBoxLayout( wIndex )
    indexLayout.setMargin( 0 )
    indexLayout.setSpacing( 3 )
    mLookFor = QLineEdit( self )
    labelLookFor = QLabel( tr( "&Look for:" ), self )
    labelLookFor.setBuddy( mLookFor )
    indexLayout.addWidget( labelLookFor )
    indexLayout.addWidget( mLookFor )
    indexLayout.addWidget( mHelpEngine.indexWidget() )
    
    wSearch = QWidget( self )
    searchLayout = QVBoxLayout( wSearch )
    searchLayout.setMargin( 0 )
    searchLayout.setSpacing( 3 )
    searchLayout.addWidget( mHelpEngine.searchEngine().queryWidget() )
    searchLayout.addWidget( mHelpEngine.searchEngine().resultWidget() )
    
    mStacked.addWidget( wContents )
    mStacked.addWidget( wIndex )
    mStacked.addWidget( wBookmarks )
    mStacked.addWidget( wSearch )
    
    # prepare context menu policy
    textBrowser = mHelpEngine.searchEngine().resultWidget().findChild<QTextBrowser*>()
    
    mHelpEngine.contentWidget().setContextMenuPolicy( Qt.CustomContextMenu )
    mHelpEngine.indexWidget().setContextMenuPolicy( Qt.CustomContextMenu )
    textBrowser.setContextMenuPolicy( Qt.CustomContextMenu )
    
    # help on keyword
    aKeywordHelp = MonkeyCore.menuBar().action( "mHelp/aKeywordHelp", tr( "Keyword Help" ), pIconManager.icon( "assistant.png", ":/help" ), "F1", tr( "Search the current word in indexes." ) )
    aSearchHelp = MonkeyCore.menuBar().action( "mHelp/aSearchHelp", tr( "Search Help" ), pIconManager.icon( "assistant.png", ":/help" ), "Shift+F1", tr( "Search the current word using the search engine." ) )
    
    # install event filters
    mLookFor.installEventFilter( self )
    mHelpEngine.indexWidget().installEventFilter( self )
    
    # os x gui fix
    foreach ( QWidget* widget, findChildren<QWidget*>() )
        widget.setAttribute( Qt.WA_MacShowFocusRect, False )
        widget.setAttribute( Qt.WA_MacSmallSize )

    
    # connections
    aShow.triggered.connect(self.helpShown)
    mHelpEngine.searchEngine().indexingStarted.connect(mProgress.show)
    mHelpEngine.searchEngine().indexingFinished.connect(mProgress.hide)
    aPagesGroup.triggered.connect(self.aPagesGroup_triggered)
    mHelpEngine.currentFilterChanged.connect(self.updateFilters)
    aFilterGroup.triggered.connect(self.aFilterGroup_triggered)
    mHelpEngine.contentWidget().linkActivated.connect(self.openUrl)
    mHelpEngine.indexWidget().linkActivated.connect(self.openUrl)
    mHelpEngine.indexWidget().linksActivated.connect(self.openUrls)
    mHelpEngine.indexModel().indexCreationStarted.connect(self.disableSearchLineEdit)
    mHelpEngine.indexModel().indexCreated.connect(self.enableSearchLineEdit)
    mLookFor.textChanged.connect(self.filterIndices)
    mLookFor.returnPressed.connect(mHelpEngine.indexWidget().activateCurrentItem)
    mHelpEngine.searchEngine().searchingStarted.connect(self.searchingStarted)
    mHelpEngine.searchEngine().searchingFinished.connect(self.searchingFinished)
    mHelpEngine.searchEngine().queryWidget().search.connect(self.search)
    mHelpEngine.searchEngine().resultWidget().requestShowLink.connect(self.openUrl)
    mHelpEngine.contentWidget().customContextMenuRequested.connect(self.open_customContextMenuRequested)
    mHelpEngine.indexWidget().customContextMenuRequested.connect(self.open_customContextMenuRequested)
    textBrowser.customContextMenuRequested.connect(self.open_customContextMenuRequested)
    bwBookmarks.requestShowLink.connect(self.openUrl)
    bwBookmarks.requestShowLinkInNewTab.connect(self.openInNewTabUrl)
    bwBookmarks.addBookmark.connect(self.addBookmark)
    aKeywordHelp.triggered.connect(self.keywordHelp)
    aSearchHelp.triggered.connect(self.searchHelp)
    
    aContents.toggle()
    
    # init documentation
    mDocInstaller = MkSQtDocInstaller( mHelpEngine )
    
    QTimer.singleShot( 1000* 10, mDocInstaller, SLOT( checkDocumentation() ) )


QtAssistantDock.~QtAssistantDock()
    mBookmarkManager.saveBookmarks()
    delete QtAssistantChild.instance( mHelpEngine, self, False )


def eventFilter(self, obj, e ):
    if  obj == mLookFor and e.type() == QEvent.KeyPress :
        ke = static_cast<QKeyEvent*>( e )
        idx = mHelpEngine.indexWidget().currentIndex()
        switch ( ke.key() )
            case Qt.Key_Up:
                idx = mHelpEngine.indexModel().index( idx.row() -1, idx.column(), idx.parent() )
                if  idx.isValid() :
                    mHelpEngine.indexWidget().setCurrentIndex( idx )
                break
            case Qt.Key_Down:
                idx = mHelpEngine.indexModel().index( idx.row() +1, idx.column(), idx.parent() )
                if  idx.isValid() :
                    mHelpEngine.indexWidget().setCurrentIndex( idx )
                break
            case Qt.Key_Escape:
                child().focusCurrentTab()
                break
            default:
                break


#ifdef Q_OS_MAC
    elif  obj == mHelpEngine.indexWidget() and e.type() == QEvent.KeyPress :
        ke = static_cast<QKeyEvent*>( e )
        if  ke.key() == Qt.Key_Return or ke.key() == Qt.Key_Enter :
            mHelpEngine.indexWidget().activateCurrentItem()

#endif
    return pDockWidget.eventFilter( obj, e )


def child(self):
    return QtAssistantChild.instance( mHelpEngine, const_cast<QtAssistantDock*>( self ) )


def openUrl(self, url, newTab ):
    helpShown.emit()
    
    if  newTab :
        child().openUrlInNewTab( url )

    else:
        child().openUrl( url )



def openInNewTabUrl(self, url ):
    openUrl( url, True )


def openUrls(self,   QMap<QString, links, keyword, newTab ):
    if  links.isEmpty() :
        return

    
    if  links.count() == 1 :
        openUrl( links.begin().value(), newTab )
        return

    
    TopicChooser tc( self, keyword, links )
    
    if  tc.exec() == QDialog.Accepted :
        openUrl( tc.link(), newTab )



def aPagesGroup_triggered(self, action ):
     index = action.data().toInt()
    mStacked.setCurrentIndex( index )


def updateFilters(self, filter ):
     locked = aFilterGroup.blockSignals( True )
    
    qDeleteAll( aFilterGroup.actions() )
    
    for cFilter in mHelpEngine.customFilters():
        action = mFilters.addAction( cFilter )
        action.setData( cFilter )
        action.setCheckable( True )
        aFilterGroup.addAction( action )
        
        if  cFilter == filter :
            action.setChecked( True )


    
    aFilterGroup.blockSignals( locked )


def aFilterGroup_triggered(self, action ):
    mHelpEngine.setCurrentFilter( action.data().toString() )


def open_customContextMenuRequested(self, pos ):
    widget = qobject_cast<QWidget*>( sender() )
    QUrl url
    QMenu menu( self )
    
    aOpenUrl = menu.addAction( tr( "Open Link" ) )
    aOpenUrlNewTab = menu.addAction( tr( "Open Link in New Tab" ) )
    aCopyAnchor = menu.addAction( tr( "Copy &Link(s) Location" ) )
    
    menu.addSeparator()
    
    aCopy = menu.addAction( tr( "&Copy" ) )
    aCopy.setShortcut( QKeySequence.Copy )

    aSelectAll = menu.addAction( tr( "Select All" ) )
    aSelectAll.setShortcut( QKeySequence.SelectAll )
    
    if  widget == mHelpEngine.contentWidget() :
         index = mHelpEngine.contentWidget().indexAt( pos )
         ci = mHelpEngine.contentModel().contentItemAt( index )
        url = ci ? ci.url() : url
        aCopy.setEnabled( index.isValid() )
        aSelectAll.setEnabled( False )

    elif  widget == mHelpEngine.indexWidget() :
         index = mHelpEngine.indexWidget().indexAt( pos )
         keyword = mHelpEngine.indexModel().data( index, Qt.DisplayRole ).toString()
        QMap<QString, links = mHelpEngine.indexModel().linksForKeyword( keyword )
        url = links.isEmpty() ? url : links.begin().value()
        aCopy.setEnabled( index.isValid() )
        aSelectAll.setEnabled( False )

    elif  widget.inherits( "QTextBrowser" ) :
        textBrowser = qobject_cast<QTextBrowser*>( widget )
        url = mHelpEngine.searchEngine().resultWidget().linkAt( pos )
        aCopy.setEnabled( textBrowser.textCursor().hasSelection() )
        aSelectAll.setEnabled( not textBrowser.toPlainText().isEmpty() )

    else:
        Q_ASSERT( 0 )
        return

    
    aOpenUrl.setEnabled( not url.isEmpty() and url.isValid() )
    aOpenUrlNewTab.setEnabled( aOpenUrl.isEnabled() )
    aCopyAnchor.setEnabled( aOpenUrl.isEnabled() )
    
    action = menu.exec( widget.mapToGlobal( pos ) )
    
    if  action == aOpenUrl or action == aOpenUrlNewTab :
        if  widget != mHelpEngine.indexWidget() :
            openUrl( url, action == aOpenUrlNewTab )

        else:
             index = mHelpEngine.indexWidget().indexAt( pos )
             keyword = mHelpEngine.indexModel().data( index, Qt.DisplayRole ).toString()
            QMap<QString, links = mHelpEngine.indexModel().linksForKeyword( keyword )
            openUrls( links, keyword, action == aOpenUrlNewTab )


    elif  action == aCopyAnchor :
        if  widget != mHelpEngine.indexWidget() :
            QApplication.clipboard().setText( url.toString() )

        else:
             index = mHelpEngine.indexWidget().indexAt( pos )
             keyword = mHelpEngine.indexModel().data( index, Qt.DisplayRole ).toString()
            QMap<QString, links = mHelpEngine.indexModel().linksForKeyword( keyword )
            QStringList entries
            
            for link in links:
                entries << link.toString()

            
            QApplication.clipboard().setText( entries.join( "\n" ) )


    elif  action == aCopy :
        if  widget == mHelpEngine.contentWidget() :
             index = mHelpEngine.contentWidget().indexAt( pos )
             ci = mHelpEngine.contentModel().contentItemAt( index )
            QApplication.clipboard().setText( ci.title() )

        elif  widget == mHelpEngine.indexWidget() :
             index = mHelpEngine.indexWidget().indexAt( pos )
             keyword = mHelpEngine.indexModel().data( index, Qt.DisplayRole ).toString()
            QApplication.clipboard().setText( keyword )

        elif  widget.inherits( "QTextBrowser" ) :
            textBrowser = qobject_cast<QTextBrowser*>( widget )
            textBrowser.copy()


    elif  action == aSelectAll :
        if  not widget.inherits( "QTextBrowser" ) :
            Q_ASSERT( 0 )
            return

        
        textBrowser = qobject_cast<QTextBrowser*>( widget )
        textBrowser.selectAll()



def disableSearchLineEdit(self):
    mLookFor.setDisabled( True )


def enableSearchLineEdit(self):
    updateFilters( mHelpEngine.currentFilter() )
    mLookFor.setEnabled( True )
    filterIndices( mLookFor.text() )


def filterIndices(self, filter ):
    mHelpEngine.indexWidget().filterIndices( filter, filter.contains( '*' ) ? filter : QString.null )


def searchingStarted(self):
    setCursor( Qt.WaitCursor )


def searchingFinished(self, hits ):
    Q_UNUSED( hits )
    unsetCursor()


def search(self):
     QList<QHelpSearchQuery> query = mHelpEngine.searchEngine().queryWidget().query()
    mHelpEngine.searchEngine().search( query )


def addBookmark(self):
    viewer = child().viewer()
    
    if  viewer :
        if  viewer.source().isEmpty() :
            return

        
        mBookmarkManager.showBookmarkDialog( self, viewer.documentTitle(), viewer.source().toString() )



def isWordCharacter(self, character ):
    return character.isLetterOrNumber() or character.isMark() or character == '_'


def currentWord(self, text, cursorPos ):
    start = cursorPos
    end = cursorPos
    word = text
    
    while ( isWordCharacter( word[ start ] ) )
        if  start == 0 or not isWordCharacter( word[ start -1 ] ) :
            break
        start--

    
    while ( isWordCharacter( word[ end ] ) )
        if  end == word.length() -1 or not isWordCharacter( word[ end +1 ] ) :
            break
        end++

    
    if  start != end or isWordCharacter( word[ cursorPos ] ) :
        word = word.mid( start, end -start +1 )

    else:
        word.clear()

    
    return word


def currentWord(self):
    widget = QApplication.focusWidget()
    
    if  not widget :
        return QString.null

    
    className = widget.metaObject().className()
    QString selectedText
    
    if  className == "QComboBox" :
        cb = qobject_cast<QComboBox*>( widget )
        
        if  cb.isEditable() :
            widget = cb.lineEdit()
            className = "QLineEdit"


    
    if  className == "pEditor" :
        editor = qobject_cast<pEditor*>( widget )
        tab = QString( "" ).fill( ' ', editor.tabWidth() )
        
        if  editor.hasSelectedText() :
            selectedText = editor.selectedText().replace( "\t", tab )
            selectedText = currentWord( selectedText, 0 )

        else:
            selectedText = editor.currentLineText().replace( "\t", tab )
            selectedText = currentWord( selectedText, editor.cursorPosition().x() )


    elif  className == "QLineEdit" :
        lineedit = qobject_cast<QLineEdit*>( widget )
        
        if  lineedit.hasSelectedText() :
            selectedText = currentWord( lineedit.selectedText(), 0 )

        else:
            selectedText = currentWord( lineedit.text(), lineedit.cursorPosition() )


    
    return selectedText


def keywordHelp(self):
     selectedText = currentWord()
    
    if  not selectedText.isEmpty() :
        mLookFor.setText( selectedText )
        mHelpEngine.indexWidget().activateCurrentItem()
        
        if  not mHelpEngine.indexWidget().currentIndex().isValid() :
            MonkeyCore.messageManager().appendMessage( tr( "No help found for: %1" ).arg( selectedText ) )




def searchHelp(self):
     selectedText = currentWord()
    
    if  not selectedText.isEmpty() :
        QHelpSearchQuery query( QHelpSearchQuery.DEFAULT, QStringList( selectedText ) )
        mHelpEngine.searchEngine().search( QList<QHelpSearchQuery>() << query )
        aSearch.trigger()
        show()


