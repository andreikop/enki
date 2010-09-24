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

def instance(self, engine, parent, create ):
    static QPointer<QtAssistantChild> _instance = 0

    if  not _instance and create :
        _instance = QtAssistantChild( engine, parent )


    return _instance


QtAssistantChild.QtAssistantChild( QHelpEngine* engine, parent )
        : pAbstractChild( parent )
    Q_ASSERT( engine )

    mEngine = engine
    twPages = QTabWidget( self )
    twPages.setDocumentMode( True )
    twPages.setTabsClosable( True )
    isSearch = QtAssistantInlineSearch( self )
    isSearch.setVisible( False )
    wCentral = QWidget( self )
    centralLayout = QVBoxLayout( wCentral )
    centralLayout.setMargin( 0 )
    centralLayout.setSpacing( 6 )
    centralLayout.addWidget( twPages )
    centralLayout.addWidget( isSearch )
    setWidget( wCentral )

    setWindowIcon( pIconManager.icon( "QtAssistant.png", ":/assistant-icons" ) )
    setFilePath( "Qt Assistant" )

    # actions
    cbUrl = QComboBox( self )
    cbUrl.setSizePolicy( QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Preferred ) )
    cbUrl.setEditable( True )

    aPrevious = QAction( pIconManager.icon( "previous.png", ":/assistant-icons" ), tr( "Previous page" ), self )
    aNext = QAction( pIconManager.icon( "next.png", ":/assistant-icons" ), tr( "Next page" ), self )
    aHome = QAction( pIconManager.icon( "home.png", ":/assistant-icons" ), tr( "Home page" ), self )
    aSearchText = QAction( pIconManager.icon( "search.png", ":/assistant-icons" ), tr( "Fint in text" ), self )
    aZoomIn = QAction( pIconManager.icon( "zoomin.png", ":/assistant-icons" ), tr( "Zoom in" ), self )
    aZoomOut = QAction( pIconManager.icon( "zoomout.png", ":/assistant-icons" ), tr( "Zoom out" ), self )
    aZoomReset = QAction( pIconManager.icon( "resetzoom.png", ":/assistant-icons" ), tr( "Zoom reset" ), self )
    aAddNewPage = QAction( pIconManager.icon( "addtab.png", ":/assistant-icons" ), tr( "Add page" ), self )
    aAddNewPage.setEnabled( False )
    aNextTab = QAction( pIconManager.icon( "nexttab.png", ":/assistant-icons" ), tr( "Next tab" ), self )
    aPreviousTab = QAction( pIconManager.icon( "previoustab.png", ":/assistant-icons" ), tr( "Previous tab" ), self )

    # corner widgets
    tbCloneTab = QToolButton( self )
    tbCloneTab.setAutoRaise( True )
    tbCloneTab.setDefaultAction( aAddNewPage )
    twPages.setCornerWidget( tbCloneTab, Qt.TopLeftCorner )

    mFirstOpenUrl = True

    # connections
    aPrevious.triggered.connect(self.previousPage)
    aNext.triggered.connect(self.nextPage)
    aHome.triggered.connect(self.homePage)
    aZoomIn.triggered.connect(self.zoomIn)
    aZoomOut.triggered.connect(self.zoomOut)
    aZoomReset.triggered.connect(self.zoomReset)
    aSearchText.triggered.connect(self.invokeSearch)
    aPreviousTab.triggered.connect(self.previousTab)
    aNextTab.triggered.connect(self.nextTab)
    aAddNewPage.triggered.connect(self.cloneTab)
    cbUrl.currentIndexChanged.connect(self.cbUrl_currentIndexChanged)
    connect( isSearch.toolNext, SIGNAL( clicked() ), self, SLOT( findNext() ) )
    connect( isSearch.editFind, SIGNAL( returnPressed() ), self, SLOT( findNext() ) )
    connect( isSearch.editFind, SIGNAL( textChanged(  QString& ) ), self, SLOT( findCurrentText(  QString& ) ) )
    connect( isSearch.toolPrevious, SIGNAL( clicked() ), self, SLOT( findPrevious() ) )
    twPages.currentChanged.connect(self.updateContextActions)
    twPages.tabCloseRequested.connect(self.closeTab)

    updateContextActions()
    restoreSession()


QtAssistantChild.~QtAssistantChild()
    saveSession()


def context(self):
    return PLUGIN_NAME


def initializeContext(self, tb ):
    tb.addAction( aPrevious )
    tb.addAction( aNext )
    tb.addAction( aHome )
    tb.addSeparator()
    tb.addAction( aZoomIn )
    tb.addAction( aZoomOut )
    tb.addAction( aZoomReset )
    tb.addAction( aSearchText )
    tb.addAction( aPreviousTab )
    tb.addAction( aNextTab )
    tb.addSeparator()
    tb.addWidget( cbUrl ); # QToolBar take ownership of added widgets.


def cursorPosition(self):
    return QPoint( -1, -1 )


def editor(self):
    return 0


def isModified(self):
    return False


def isUndoAvailable(self):
    viewer = self.viewer()
    return viewer ? viewer.pageAction( QWebPage.Undo ).isEnabled() : False


def isRedoAvailable(self):
    viewer = self.viewer()
    return viewer ? viewer.pageAction( QWebPage.Redo ).isEnabled() : False


def isCopyAvailable(self):
    viewer = self.viewer()
    return viewer ? viewer.pageAction( QWebPage.Copy ).isEnabled() : False


def isPasteAvailable(self):
    viewer = self.viewer()
    return viewer ? viewer.pageAction( QWebPage.Paste ).isEnabled() : False


def isGoToAvailable(self):
    return False


def isPrintAvailable(self):
    return True


def viewer(self, index ):
    return qobject_cast<QtAssistantViewer*>( twPages.widget( index == -1 ? twPages.currentIndex() : index ) )


def newEmptyViewer(self, zoom ):
    viewer = QtAssistantViewer( mEngine, self )

    if  mEngine.customValue( QLatin1String( "useBrowserFont" ) ).toBool() :
        font = qVariantValue<QFont>( mEngine.customValue( QLatin1String( "browserFont" ) ) )
        viewer.setFont( font )


    viewer.setTextSizeMultiplier( zoom )

    twPages.addTab( viewer, tr( "Loading..." ) )
    twPages.setCurrentWidget( viewer )

    viewer.sourceChanged.connect(self.viewer_sourceChanged)
    viewer.actionsChanged.connect(self.viewer_actionsChanged)

    return viewer


def find(self, ttf, forward, backward ):
    viewer = self.viewer()
    pal = isSearch.editFind.palette()
    pal.setColor( QPalette.Active, QPalette.Base, Qt.white )

    Q_UNUSED( backward )

    if  viewer :
        QWebPage.FindFlags options

        if  not forward :
            options |= QWebPage.FindBackward


        if  isSearch.checkCase.isChecked() :
            options |= QWebPage.FindCaseSensitively


        found = viewer.findText( ttf, options )
        isSearch.labelWrapped.hide()

        if  not found :
            options |= QWebPage.FindWrapsAroundDocument
            found = viewer.findText( ttf, options )

            if  not found :
                pal.setColor( QPalette.Active, QPalette.Base, QColor( 255, 102, 102 ) )

            else:
                isSearch.labelWrapped.show()




    if  not isSearch.isVisible() :
        isSearch.show()


    isSearch.editFind.setPalette( pal )


def undo(self):
    viewer = self.viewer()
    if  viewer ) viewer.triggerPageAction( QWebPage.Undo :


def redo(self):
    viewer = self.viewer()
    if  viewer ) viewer.triggerPageAction( QWebPage.Redo :


def cut(self):
    viewer = self.viewer()
    if  viewer ) viewer.triggerPageAction( QWebPage.Cut :


def copy(self):
    viewer = self.viewer()
    if  viewer ) viewer.triggerPageAction( QWebPage.Copy :


def paste(self):
    viewer = self.viewer()
    if  viewer ) viewer.triggerPageAction( QWebPage.Paste :


def goTo(self):


def goTo(self, pos, selectionLength ):
    Q_UNUSED( pos )
    Q_UNUSED( selectionLength )


def invokeSearch(self):
    viewer = self.viewer()

    if  viewer :
        isSearch.show()
        isSearch.editFind.selectAll()
        isSearch.editFind.setFocus( Qt.ShortcutFocusReason )



def saveFile(self):


def backupFileAs(self, fileName ):
    viewer = self.viewer()

    if  not viewer :
        return


    QFile file( fileName )

    if  not file.open( QIODevice.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Can't open file for writing when creating backup file." ) )
        return


    file.resize( 0 )
    codec = self.codec()
     data = codec.fromUnicode( viewer.page().mainFrame().toHtml() )

    if  file.write( data ) == -1 :
        MonkeyCore.messageManager().appendMessage( tr( "Can't write file content when creating backup." ) )


    file.close()


def openFile(self, fileName, codec ):
    Q_UNUSED( fileName )
    Q_UNUSED( codec )
    '''
    for ( i = 1; i < twPages.count(); i++ )
        viewer = self.viewer( i )

        if  viewer.source() == QUrl( fileName ) :
            twPages.setCurrentWidget( viewer )
            return True



    openUrlInNewTab( QUrl( fileName ) )
    return True
    '''
    return False


def closeFile(self):
    setFilePath( QString.null )
    fileClosed.emit()


def reload(self):
    fileReloaded.emit()


def printFile(self):
    viewer = self.viewer()

    if  not viewer :
        return


    QPrinter printer( QPrinter.HighResolution )
    QPrintDialog dlg( &printer, self )
    dlg.addEnabledOption( QAbstractPrintDialog.PrintPageRange )
    dlg.addEnabledOption( QAbstractPrintDialog.PrintCollateCopies )
    dlg.setWindowTitle( tr( "Print Document" ) )

    if  dlg.exec() == QDialog.Accepted :
        viewer.print( &printer )



def quickPrintFile(self):
    viewer = self.viewer()

    if  not viewer :
        return


    QPrinter printer( QPrinter.HighResolution )

    if  printer.printerName().isEmpty() :
        MonkeyCore.messageManager().appendMessage( tr( "There is no default printer, set one before trying quick print" ) )

    else:
        viewer.print( &printer )



def openUrl(self, url ):
    viewer = self.viewer()

    if  viewer and not mFirstOpenUrl :
        viewer.setSource( url )

    else:
        mFirstOpenUrl = False
        openUrlInNewTab( url )



def openUrlInNewTab(self, url ):
    viewer = newEmptyViewer()
    viewer.setSource( url )


def cloneTab(self):
    viewer = self.viewer()

    if  viewer :
         url = viewer.source()
        newEmptyViewer().setSource( url )



def closeTab(self, index ):
    delete twPages.widget( index )


def focusCurrentTab(self):
    if  MonkeyCore.workspace().currentDocument() == self :
        if  twPages.currentWidget() :
            twPages.currentWidget().setFocus()




def saveSession(self):
    QString zoomCount
    QString currentPages
    QLatin1Char sep( '|' )

    for ( i = 0; i < twPages.count(); ++i )
        viewer = self.viewer( i )

        if  not viewer.source().isEmpty() and viewer.source().isValid() :
            currentPages.append( viewer.source().toString() ).append( sep )
            zoomCount.append( QString.number( viewer.textSizeMultiplier() ) ).append( sep )



    mEngine.setCustomValue( QLatin1String( "LastTabPage" ), twPages.currentIndex() )
    mEngine.setCustomValue( QLatin1String( "LastShownPages" ), currentPages )
    mEngine.setCustomValue( QLatin1String( "LastPagesZoomWebView" ), zoomCount )


def restoreSession(self):
    QLatin1String zoom( "LastPagesZoomWebView" )
     lastShownPageList = mEngine.customValue( QLatin1String( "LastShownPages" ) ).toString().split( QLatin1Char( '|' ), QString.SkipEmptyParts )

    if  not lastShownPageList.isEmpty() :
        QVector<QString> zoomList = mEngine.customValue( zoom ).toString().split( QLatin1Char( '|' ), QString.SkipEmptyParts ).toVector()

        if  zoomList.isEmpty() :
            zoomList.fill( QLatin1String( "1.0" ), lastShownPageList.size() )


        if  zoomList.count() < lastShownPageList.count() :
            for ( i = 0; i < lastShownPageList.count(); i++ )
                zoomList << QLatin1String( "1.0" )


        else:
            zoomList.resize( lastShownPageList.count() )


        QVector<QString>zIt = zoomList.constBegin()
        it = lastShownPageList.constBegin()

        for ( ; it != lastShownPageList.constEnd(); ++it, ++zIt )
            viewer = newEmptyViewer( (*zIt).toFloat() )
            viewer.setSource( (*it) )


        twPages.setCurrentIndex( mEngine.customValue( QLatin1String( "LastTabPage" ), 0 ).toInt() )

    '''
    else:
        openUrl( QUrl( QLatin1String( "help" ) ) )
    '''


def previousTab(self):
    index = twPages.currentIndex() -1
    twPages.setCurrentIndex( index >= 0 ? index : twPages.count() -1 )


def nextTab(self):
    index = twPages.currentIndex()
    twPages.setCurrentIndex( index < twPages.count() -1 ? index +1 : 0 )


def previousPage(self):
    viewer().back()
    updateContextActions()


def nextPage(self):
    viewer().forward()
    updateContextActions()


def homePage(self):
    viewer().home()


def zoomIn(self):
    viewer().zoomIn()


def zoomOut(self):
    viewer().zoomOut()


def zoomReset(self):
    viewer().resetZoom()


def findNext(self):
    find( isSearch.editFind.text(), True, False )


def findPrevious(self):
    find( isSearch.editFind.text(), False, True )


def findCurrentText(self, &text):
    find( text, False, False )


def updateContextActions(self):
    viewer = self.viewer()

    aAddNewPage.setEnabled( viewer )
    aPrevious.setEnabled( viewer and twPages.currentWidget() == viewer ? viewer.isBackwardAvailable() : False )
    aNext.setEnabled( viewer and twPages.currentWidget() == viewer ? viewer.isForwardAvailable() : False )
    aHome.setEnabled( viewer and twPages.currentWidget() == viewer ? True : False )
    aZoomIn.setEnabled( viewer and twPages.currentWidget() == viewer ? True : False )
    aZoomOut.setEnabled( viewer and twPages.currentWidget() == viewer ? True : False )
    aZoomReset.setEnabled( viewer and twPages.currentWidget() == viewer ? True : False )
    aSearchText.setEnabled( viewer and twPages.currentWidget() == viewer ? True : False )
    aPreviousTab.setEnabled( twPages.count() > 1 )
    aNextTab.setEnabled( twPages.count() > 1 )

     locked = cbUrl.blockSignals( True )

    cbUrl.clear()

    if  viewer and twPages.currentWidget() :
        QSet<QString> entries

        for item in viewer.history().items():
            if  not entries.contains( item.url().toString() ) :
                entries << item.url().toString()
                cbUrl.addItem( item.title(), item.url() )
                cbUrl.setItemData( cbUrl.count() -1, item.url().toString(), Qt.ToolTipRole )



        cbUrl.setCurrentIndex( cbUrl.findData( viewer.history().currentItem().url() ) )


    cbUrl.blockSignals( locked )

    cbUrl.setEnabled( viewer and twPages.currentWidget() == viewer )

    viewer_actionsChanged()


def viewer_sourceChanged(self, url ):
    Q_UNUSED( url )
    viewer = qobject_cast<QtAssistantViewer*>( sender() )
     index = twPages.indexOf( viewer )
    twPages.setTabText( index, viewer.documentTitle() )

    if  twPages.currentWidget() == viewer :
        updateContextActions()



def viewer_actionsChanged(self):
    viewer = qobject_cast<QtAssistantViewer*>( sender() )

    undoAvailableChanged.emit( viewer and twPages.currentWidget() == viewer ? viewer.pageAction( QWebPage.Undo ).isEnabled() : False )
    redoAvailableChanged.emit( viewer and twPages.currentWidget() == viewer ? viewer.pageAction( QWebPage.Redo ).isEnabled() : False )
    pasteAvailableChanged.emit( viewer and twPages.currentWidget() == viewer ? viewer.pageAction( QWebPage.Paste ).isEnabled() : False )
    copyAvailableChanged.emit( viewer and twPages.currentWidget() == viewer ? viewer.pageAction( QWebPage.Copy ).isEnabled() : False )


def cbUrl_currentIndexChanged(self, index ):
    viewer = self.viewer()
    url = cbUrl.itemData( index ).toUrl()
    url = url.isValid() ? url : cbUrl.itemText( index )
    viewer.setSource( url )

