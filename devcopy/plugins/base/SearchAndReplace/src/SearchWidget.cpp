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

SearchWidget.SearchWidget( SearchAndReplace* plugin, parent )
    : QFrame( parent )
    Q_ASSERT( plugin )
    mPlugin = plugin
    
    setupUi( self )
    cbSearch.completer().setCaseSensitivity( Qt.CaseSensitive )
    cbReplace.completer().setCaseSensitivity( Qt.CaseSensitive )
    fsModel = QDirModel( self )
    fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
    cbPath.lineEdit().setCompleter( QCompleter( fsModel ) )
#warning QDirModel is deprecated but QCompleter does not yet handle QFileSystemModel - please update when possible.
    cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
    pbSearchStop.setVisible( False )
    pbReplaceCheckedStop.setVisible( False )
    
    mProgress = QProgressBar( self )
    mProgress.setAlignment( Qt.AlignCenter )
    mProgress.setToolTip( tr( "Search in progress..." ) )
    mProgress.setMaximumSize( QSize( 80, 16 ) )
    MonkeyCore.mainWindow().statusBar().insertPermanentWidget( 0, mProgress )
    mProgress.setVisible( False )

    # threads
    mSearchThread = SearchThread( self )
    mReplaceThread = ReplaceThread( self )

    mDock = 0
    
    # mode actions
    tbMode = QToolButton( cbSearch.lineEdit() )
    tbMode.setIcon( pIconManager.icon( "misc.png" ) )
    tbMode.setPopupMode( QToolButton.InstantPopup )
    tbMode.setMenu( MonkeyCore.menuBar().menu( "mEdit/mSearchReplace" ) )
    tbMode.setCursor( Qt.ArrowCursor )
    tbMode.installEventFilter( self )
    
    # cd up action
    tbCdUp = QToolButton( cbPath.lineEdit() )
    tbCdUp.setIcon( pIconManager.icon( "go-up.png" ) )
    tbCdUp.setCursor( Qt.ArrowCursor )
    tbCdUp.installEventFilter( self )

    # options actions
    QAction* action

    action = QAction( cbCaseSensitive )
    action.setCheckable( True )
    cbCaseSensitive.toggled.connect(action.setChecked)
    mOptionActions[ SearchAndReplace.OptionCaseSensitive ] = action
    
    action = QAction( cbWholeWord )
    action.setCheckable( True )
    cbWholeWord.toggled.connect(action.setChecked)
    mOptionActions[ SearchAndReplace.OptionWholeWord ] = action
    
    action = QAction( cbWrap )
    action.setCheckable( True )
    cbWrap.toggled.connect(action.setChecked)
    mOptionActions[ SearchAndReplace.OptionWrap ] = action
    
    action = QAction( cbRegularExpression )
    action.setCheckable( True )
    cbRegularExpression.toggled.connect(action.setChecked)
    mOptionActions[ SearchAndReplace.OptionRegularExpression ] = action
    
    # init default options
    cbWrap.setChecked( True )

    # mac
    pMonkeyStudio.showMacFocusRect( self, False, True )
    pMonkeyStudio.setMacSmallSize( self, True, True )

#ifdef Q_OS_MAC
     QSize size( 12, 12 )

    foreach ( QAbstractButton* button, findChildren<QAbstractButton*>() )
        button.setIconSize( size )
        button.setFixedHeight( 24 )


    vlMain.setSpacing( 0 )
#endif

    # mask tooltip
    languages = pMonkeyStudio.availableLanguages()
    
    for ( i = 0; i < languages.count(); i += 10 )
        languages[ i ].prepend( "\n" )

    
    maskToolTip = tr( "Space separated list of wildcards, *.h *.cpp file???.txt\n"
        "You can use language name too so the search will only apply to the language suffixes.\n"
        "Available languages: %1" ).arg( languages.join( ", " ) )
    
    cbMask.setToolTip( maskToolTip )

    # codecs
    QStringList codecs
    for codec in QTextCodec.availableCodecs():
        codecs << codec

    codecs.sort()
    cbCodec.addItems( codecs )

    cbCodec.setCurrentIndex( cbCodec.findText( pMonkeyStudio.defaultCodec() ) )

    # connections
    cbSearch.lineEdit().textEdited.connect(self.search_textChanged)
    tbCdUp.clicked.connect(self.cdUp_clicked)
    mSearchThread.started.connect(self.searchThread_stateChanged)
    mSearchThread.finished.connect(self.searchThread_stateChanged)
    mSearchThread.progressChanged.connect(self.searchThread_progressChanged)
    mReplaceThread.started.connect(self.replaceThread_stateChanged)
    mReplaceThread.finished.connect(self.replaceThread_stateChanged)
    mReplaceThread.openedFileHandled.connect(self.replaceThread_openedFileHandled)
    mReplaceThread.error.connect(self.replaceThread_error)

    setMode( SearchAndReplace.ModeSearch )


SearchWidget.~SearchWidget()
    delete mSearchThread
    delete mReplaceThread
    delete mProgress


def mode(self):
    return mMode


def searchThread(self):
    return mSearchThread


def setResultsDock(self, dock ):
    if  mDock == dock :
        return


    mDock = dock

    # connections
    mReplaceThread.resultsHandled.connect(mDock.model().thread_resultsHandled)


def isBinary(self, file ):
     position = file.pos()
    file.seek( 0 )
     binary = file.read( 1024 ).contains( '\0' )
    file.seek( position )
    return binary


def setMode(self, mode ):
    mSearchThread.stop()
    mReplaceThread.stop()
    
    currentDocumentOnly = False
    
    # clear search results if needed.
    switch ( mode )
        case SearchAndReplace.ModeSearch:
        case SearchAndReplace.ModeReplace:
            currentDocumentOnly = True
            break
        default:
            mSearchThread.clear()
            break


    mMode = mode
    
    initializeProperties( currentDocumentOnly )
    
    if  mMode & SearchAndReplace.ModeFlagProjectFiles :
        if  mProperties.project :
             codec = mProperties.project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
            
            mProperties.codec = codec
            cbCodec.setCurrentIndex( cbCodec.findText( codec ) )


    
    Q_ASSERT( not mProperties.codec.isEmpty() )

    document = MonkeyCore.workspace().currentDocument()
    editor = document ? document.editor() : 0
     path = mProperties.project ? mProperties.project.path() : QDir.currentPath()
     searchPath = document ? QFileInfo( document.filePath() ).absolutePath() : path
     searchText = editor ? editor.selectedText() : QString.null
     wasVisible = isVisible()

    setVisible( mode != SearchAndReplace.ModeNo )

    if  isVisible() :
        if  mProperties.settings.replaceSearchText :
             isRE = mProperties.options & SearchAndReplace.OptionRegularExpression
             isEmpty = searchText.isEmpty()
             validateVisibility = not mProperties.settings.onlyWhenNotVisible or ( mProperties.settings.onlyWhenNotVisible and not wasVisible )
             validateRegExp = not mProperties.settings.onlyWhenNotRegExp or ( mProperties.settings.onlyWhenNotRegExp and not isRE )
             validateEmpty = not mProperties.settings.onlyWhenNotEmpty or ( mProperties.settings.onlyWhenNotEmpty and not isEmpty )
            
            if  validateVisibility and validateRegExp and validateEmpty :
                cbSearch.setEditText( searchText )



        if  mode & SearchAndReplace.ModeFlagSearch :
            cbSearch.setFocus()
            cbSearch.lineEdit().selectAll()

        else:
            cbReplace.setFocus()
            cbReplace.lineEdit().selectAll()

        
        if  mode & SearchAndReplace.ModeFlagDirectory :
            cbPath.setEditText( searchPath )



    switch ( mMode )
        case SearchAndReplace.ModeNo:
            wSearch.setVisible( False )
            wReplace.setVisible( False )
            wPath.setVisible( False )
            wOptions.setVisible( False )
            break
        case SearchAndReplace.ModeSearch:
            wSearch.setVisible( True )
            pbPrevious.setVisible( True )
            pbNext.setVisible( True )
            pbSearch.setVisible( False )

            wReplace.setVisible( False )

            wPath.setVisible( False )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( False )

            wOptions.setVisible( True )
            wMask.setVisible( False )
            wCodec.setVisible( False )
            break
        case SearchAndReplace.ModeReplace:
            wSearch.setVisible( True )
            pbPrevious.setVisible( True )
            pbNext.setVisible( True )
            pbSearch.setVisible( False )

            wReplace.setVisible( True )

            wPath.setVisible( False )
            pbReplace.setVisible( True )
            pbReplaceAll.setVisible( True )
            pbReplaceChecked.setVisible( False )

            wOptions.setVisible( True )
            wMask.setVisible( False )
            wCodec.setVisible( False )
            break
        case SearchAndReplace.ModeSearchDirectory:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( False )

            wPath.setVisible( True )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( False )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( True )
            break
        case SearchAndReplace.ModeReplaceDirectory:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( True )

            wPath.setVisible( True )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( True )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( True )
            break
        case SearchAndReplace.ModeSearchProjectFiles:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( False )

            wPath.setVisible( False )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( False )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( True )
            break
        case SearchAndReplace.ModeReplaceProjectFiles:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( True )

            wPath.setVisible( False )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( True )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( True )
            break
        case SearchAndReplace.ModeSearchOpenedFiles:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( False )

            wPath.setVisible( False )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( False )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( False )
            break
        case SearchAndReplace.ModeReplaceOpenedFiles:
            wSearch.setVisible( True )
            pbPrevious.setVisible( False )
            pbNext.setVisible( False )
            pbSearch.setVisible( True )

            wReplace.setVisible( True )

            wPath.setVisible( False )
            pbReplace.setVisible( False )
            pbReplaceAll.setVisible( False )
            pbReplaceChecked.setVisible( True )

            wOptions.setVisible( True )
            wMask.setVisible( True )
            wCodec.setVisible( False )
            break


    updateLabels()
    updateWidgets()


def eventFilter(self, object, event ):
    if  event.type() == QEvent.Paint :
        toolButton = qobject_cast<QToolButton*>( object )
        lineEdit = object == tbMode ? cbSearch.lineEdit() : cbPath.lineEdit()
        lineEdit.setContentsMargins( lineEdit.height(), 0, 0, 0 )
        
         height = lineEdit.height()
         QRect availableRect( 0, 0, height, height )
        
        if  toolButton.rect() != availableRect :
            toolButton.setGeometry( availableRect )

        
        QPainter painter( toolButton )
        toolButton.icon().paint( &painter, availableRect )
        
        return True

    
    return QWidget.eventFilter( object, event )


def keyPressEvent(self, event ):
    if  event.modifiers() == Qt.NoModifier :
        switch ( event.key() )
            case Qt.Key_Escape:
                MonkeyCore.workspace().focusEditor()
                hide()

                break

            case Qt.Key_Enter:
            case Qt.Key_Return:
                switch ( mMode )
                    case SearchAndReplace.ModeNo:
                        break
                    case SearchAndReplace.ModeSearch:
                        pbNext.click()
                        break
                    case SearchAndReplace.ModeSearchDirectory:
                    case SearchAndReplace.ModeSearchProjectFiles:
                    case SearchAndReplace.ModeSearchOpenedFiles:
                        pbSearch.click()
                        break
                    case SearchAndReplace.ModeReplace:
                        pbReplace.click()
                        break
                    case SearchAndReplace.ModeReplaceDirectory:
                    case SearchAndReplace.ModeReplaceProjectFiles:
                    case SearchAndReplace.ModeReplaceOpenedFiles:
                        pbReplaceChecked.click()
                        break


                break




    QWidget.keyPressEvent( event )


def updateLabels(self):
    width = 0

    if  lSearch.isVisible() :
        width = qMax( width, lSearch.minimumSizeHint().width() )


    if  lReplace.isVisible() :
        width = qMax( width, lReplace.minimumSizeHint().width() )


    if  lPath.isVisible() :
        width = qMax( width, lPath.minimumSizeHint().width() )


    lSearch.setMinimumWidth( width )
    lReplace.setMinimumWidth( width )
    lPath.setMinimumWidth( width )


def updateWidgets(self):
    width = 0

    if  wSearchRight.isVisible() :
        width = qMax( width, wSearchRight.minimumSizeHint().width() )


    if  wReplaceRight.isVisible() :
        width = qMax( width, wReplaceRight.minimumSizeHint().width() )


    if  wPathRight.isVisible() :
        width = qMax( width, wPathRight.minimumSizeHint().width() )


    wSearchRight.setMinimumWidth( width )
    wReplaceRight.setMinimumWidth( width )
    wPathRight.setMinimumWidth( width )


def updateComboBoxes(self):
     searchText = cbSearch.currentText()
     replaceText = cbReplace.currentText()
     maskText = cbMask.currentText()
    int index
    
    # search
    if  not searchText.isEmpty() :
        index = cbSearch.findText( searchText )
        
        if  index == -1 :
            cbSearch.addItem( searchText )


    
    # replace
    if  not replaceText.isEmpty() :
        index = cbReplace.findText( replaceText )
        
        if  index == -1 :
            cbReplace.addItem( replaceText )


    
    # mask
    if  not maskText.isEmpty() :
        index = cbMask.findText( maskText )
        
        if  index == -1 :
            cbMask.addItem( maskText )




def initializeProperties(self, currentDocumentOnly ):
     QMap<QString, suffixes = pMonkeyStudio.availableLanguagesSuffixes()
     keys = suffixes.keys()
    mProperties.searchText = cbSearch.currentText()
    mProperties.replaceText = cbReplace.currentText()
    mProperties.searchPath = cbPath.currentText()
    mProperties.mode = mMode
    mProperties.mask.clear()
    mProperties.codec = cbCodec.currentText()
    mProperties.options = SearchAndReplace.Options( SearchAndReplace.ModeNo )
    mProperties.openedFiles.clear()
    mProperties.project = MonkeyCore.fileManager().currentProject()
    mProperties.sourcesFiles.clear()
    mProperties.settings = mPlugin.settings()

    # update masks
    for part in cbMask.currentText(:.split( " ", QString.SkipEmptyParts ) )
         index = keys.indexOf( QRegExp( QRegExp.escape( part ), Qt.CaseInsensitive ) )

        if  index != -1 :
            foreach (  QString& suffixe, suffixes[ keys.at( index ) ] )
                if  not mProperties.mask.contains( suffixe ) :
                    mProperties.mask << suffixe



        else:
            mProperties.mask << part


    
    # set default mask if needed
    if  mProperties.mask.isEmpty() :
        mProperties.mask << "*"


    # update options
    foreach (  SearchAndReplace.Option& option, mOptionActions.keys() )
        action = mOptionActions[ option ]

        if  action.isChecked() :
            mProperties.options |= option


    
    # update project
    mProperties.project = mProperties.project ? mProperties.project.topLevelProject() : 0
    
    if  currentDocumentOnly :
        return


    # update opened files
    for document in MonkeyCore.workspace().documents():
        mProperties.openedFiles[ document.filePath() ] = document.fileBuffer()


    # update sources files
    mProperties.sourcesFiles = mProperties.project ? mProperties.project.topLevelProjectSourceFiles() : QStringList()


def showMessage(self, status ):
    if  status.isEmpty() :
        MonkeyCore.mainWindow().statusBar().clearMessage()

    else:
        MonkeyCore.mainWindow().statusBar().showMessage( status, 30000 )



def setState(self, field, state ):
    widget = 0
    color = QColor( Qt.white )

    switch ( field )
        case SearchWidget.Search:
            widget = cbSearch.lineEdit()
            break
        case SearchWidget.Replace:
            widget = cbReplace.lineEdit()
            break


    switch ( state )
        case SearchWidget.Normal:
            color = QColor( Qt.white )
            break
        case SearchWidget.Good:
            color = QColor( Qt.green )
            break
        case SearchWidget.Bad:
            color = QColor( Qt.red )
            break


    pal = widget.palette()
    pal.setColor( widget.backgroundRole(), color )
    widget.setPalette( pal )


def searchFile(self, forward, incremental ):
    document = MonkeyCore.workspace().currentDocument()
    child = document ? static_cast<pChild*>( document ) : 0
    editor = child ? child.editor() : 0

    if  not editor :
        setState( SearchWidget.Search, SearchWidget.Bad )
        showMessage( tr( "No active editor" ) )
        return False


    # get cursor position
     isRE = mProperties.options & SearchAndReplace.OptionRegularExpression
     isCS = mProperties.options & SearchAndReplace.OptionCaseSensitive
     isWW = mProperties.options & SearchAndReplace.OptionWholeWord
     isWrap = mProperties.options & SearchAndReplace.OptionWrap
    int x, y, temp
    
    if  forward :        if  incremental :            editor.getSelection( &y, &x, &temp, &temp )

        else:
            editor.getSelection( &temp, &temp, &y, &x )


    else:
        if  incremental :            editor.getSelection( &temp, &temp, &y, &x )

        else:
            editor.getSelection( &y, &x, &temp, &temp )



    # search
     found = editor.findFirst( mProperties.searchText, isRE, isCS, isWW, isWrap, forward, y, x, True )

    # change background acording to found or not
    setState( SearchWidget.Search, found ? SearchWidget.Good : SearchWidget.Bad )

    # show message if needed
    showMessage( found ? QString.null : tr( "Not Found" ) )

    # return found state
    return found


def replaceFile(self, all ):
    document = MonkeyCore.workspace().currentDocument()
    child = document ? static_cast<pChild*>( document ) : 0
    editor = child ? child.editor() : 0

    if  not editor :
        setState( SearchWidget.Search, SearchWidget.Bad )
        showMessage( tr( "No active editor" ) )
        return False


    count = 0
    
    if  all :
         isWrap = mProperties.options & SearchAndReplace.OptionWrap
        int x, y

        editor.getCursorPosition( &y, &x )

        if  isWrap :
            # don't need to give wrap parameter for search as we start at begin of document
            editor.setCursorPosition( 0, 0 )
            mProperties.options &= ~SearchAndReplace.OptionWrap


        editor.beginUndoAction()
        
        while ( searchFile( True, False ) ) # search next
            editor.replace( mProperties.replaceText )
            count++


        editor.endUndoAction()
        editor.setCursorPosition( y, x ); # restore cursor position
        
        # restore wrap property if needed
        if  isWrap :
            mProperties.options |= SearchAndReplace.OptionWrap


    else:
        int x, y, temp

        editor.getSelection( &y, &x, &temp, &temp )
        editor.setCursorPosition( y, x )

        if  searchFile( True, False ) :
            editor.beginUndoAction()
            editor.replace( mProperties.replaceText )
            editor.endUndoAction()
            count++
            pbNext.click(); # move selection to next item



    showMessage( tr( "%1 occurrence(s) replaced." ).arg( count ) )

    return True


def searchThread_stateChanged(self):
    pbSearchStop.setVisible( mSearchThread.isRunning() )
    updateWidgets()
    mProgress.setVisible( mSearchThread.isRunning() )


def searchThread_progressChanged(self, value, total ):
    mProgress.setValue( value )
    mProgress.setMaximum( total )


def replaceThread_stateChanged(self):
    pbReplaceCheckedStop.setVisible( mReplaceThread.isRunning() )
    updateWidgets()


def replaceThread_openedFileHandled(self, fileName, content, codec ):
    document = MonkeyCore.fileManager().openFile( fileName, codec )
    editor = document.editor()

    Q_ASSERT( editor )

    editor.beginUndoAction()
    editor.selectAll()
    editor.removeSelectedText()
    editor.insert( content )
    editor.endUndoAction()


def replaceThread_error(self, error ):
    MonkeyCore.messageManager().appendMessage( error )


def search_textChanged(self):
    initializeProperties( True )
    
    # clear search results if needed.
    switch ( mMode )
        case SearchAndReplace.ModeSearch:
            searchFile( True, True )
        case SearchAndReplace.ModeReplace:
            break
        default:
            mSearchThread.clear()
            break



def cdUp_clicked(self):
    QDir dir( cbPath.currentText() )
    
    if  not dir.exists() :
        return

    
    dir.cdUp()
    
    cbPath.setEditText( dir.absolutePath() )


def on_pbPrevious_clicked(self):
    updateComboBoxes()
    initializeProperties( True )
    searchFile( False, False )


def on_pbNext_clicked(self):
    updateComboBoxes()
    initializeProperties( True )
    searchFile( True, False )


def on_pbSearch_clicked(self):
    setState( SearchWidget.Search, SearchWidget.Normal )
    updateComboBoxes()
    initializeProperties( False )
    
    if  mProperties.searchText.isEmpty() :
        MonkeyCore.messageManager().appendMessage( tr( "You can't search for NULL text." ) )
        return

    
    if  mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not mProperties.project :
        MonkeyCore.messageManager().appendMessage( tr( "You can't search in project files because there is no opened projet." ) )
        return

    
    mSearchThread.search( mProperties )


def on_pbSearchStop_clicked(self):
    mSearchThread.stop()


def on_pbReplace_clicked(self):
    updateComboBoxes()
    initializeProperties( True )
    replaceFile( False )


def on_pbReplaceAll_clicked(self):
    updateComboBoxes()
    initializeProperties( True )
    replaceFile( True )


def on_pbReplaceChecked_clicked(self):
    QHash<QString, items
    model = mDock ? mDock.model() : 0

    Q_ASSERT( model )

    updateComboBoxes()
    initializeProperties( False )
    
    if  mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not mProperties.project :
        MonkeyCore.messageManager().appendMessage( tr( "You can't replace in project files because there is no opened projet." ) )
        return


    foreach (  SearchResultsModel.ResultList& results, model.results() )
        foreach ( SearchResultsModel.Result* result, results )
            if  result.enabled and result.checkState == Qt.Checked :
                items[ result.fileName ] << result

            else:
                 index = mDock.model().index( result )
                mDock.model().setData( index, False, SearchResultsModel.EnabledRole )




    mReplaceThread.replace( mProperties, items )


def on_pbReplaceCheckedStop_clicked(self):
    mReplaceThread.stop()


def on_pbBrowse_clicked(self):
     path = QFileDialog.getExistingDirectory( self, tr( "Search path" ), cbPath.currentText() )

    if  not path.isEmpty() :
        cbPath.setEditText( path )


