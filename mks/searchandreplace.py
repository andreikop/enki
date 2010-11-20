"""Search and Replace plugin. S&R GUI and implementation
"""

from PyQt4 import uic
from PyQt4.QtCore import Qt, QTextCodec, QDirModel
from PyQt4.QtGui import QFileDialog, QCompleter, QPainter, QProgressBar, QLineEdit, QToolButton, QKeyEvent \
                        QFrame, QAction

import mks.monkeycore

class SearchAndReplace:  # TODO (Plugin) ?
    
    ModeFlagSearch = 0x1
    ModeFlagReplace = 0x2
    ModeFlagFile = 0x4
    ModeFlagDirectory = 0x4
    ModeFlagProjectFiles = 0x10
    ModeFlagOpenedFiles = 0x11

    ModeNo = 0
    ModeSearch = ModeFlagSearch | ModeFlagFile
    ModeReplace = ModeFlagReplace | ModeFlagFile
    ModeSearchDirectory = ModeFlagSearch | ModeFlagDirectory
    ModeReplaceDirectory = ModeFlagReplace | ModeFlagDirectory
    ModeSearchProjectFiles = ModeFlagSearch | ModeFlagProjectFiles
    ModeReplaceProjectFiles = ModeFlagReplace | ModeFlagProjectFiles
    ModeSearchOpenedFiles = ModeFlagSearch | ModeFlagOpenedFiles
    ModeReplaceOpenedFiles = ModeFlagReplace | ModeFlagOpenedFiles

    actions = ( ("aReplaceFile", "&Replace...", "edit/replace.png", "Ctrl+R", "Replace in the current file...", self.modeSwitchTriggered, ModeReplace),
                ("aSearchPrevious", "Search &Previous", "edit/previous.png", "Shift+F3", "Search previous occurrence", self.widget.on_pbPrevious_clicked, None),
                ("aSearchNext", "Search &Next", "edit/next.png", "F3", "Search next occurrence", self.widget.on_pbNext_clicked, None),
                ("aSearchDirectory", "Search in &Directory...", "search-replace-directory.png", "Ctrl+Shift+F", "Search in directory...", self.modeSwitchTriggered, ModeSearch),
                ("aReplaceDirectory", "Replace in Director&y...", "search-replace-directory.png", "Ctrl+Shift+R", "Replace in directory...", self.modeSwitchTriggered, ModeReplaceDirectory),
                ("aSearchProjectFiles", "Search in Project &Files...", "search-replace-project-files.png", "Ctrl+Meta+F", "Search in the current project files..", self.modeSwitchTriggered, ModeSearchProjectFiles)
                ("aReplaceProjectFiles", "Replace in Projec&t Files...", "search-replace-project-files.png", "Ctrl+Meta+R", "Replace in the current project files...", self.modeSwitchTriggered, ModeReplaceProjectFiles),
                ("aSearchOpenedFiles", "Search in &Opened Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+F", "Search in opened files...", self.modeSwitchTriggered, ModeSearchOpenedFiles),
                ("aReplaceOpenedFiles", "Replace in Open&ed Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+R", "Replace in opened files...", self.modeSwitchTriggered, ModeReplaceOpenedFiles))
    
    def __init__(self):
        """Plugin initialisation
        """
        self.widget = SearchWidget( self )
        mks.mks.monkeycore.workspace().layout().addWidget( self.widget )
        self.widget.setVisible( False )

        self.dock = SearchResultsDock( self.widget.searchThread() )
        mks.mks.mks.monkeycore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( self.dock, self.dock.windowTitle(), self.dock.windowIcon() )
        self.dock.setVisible( False )

        self.widget.setResultsDock( self.dock )
        
        mb = mks.mks.monkeycore.menuBar()
        
        mb.beginGroup( "mEdit/mSearchReplace" )
        for action in self.actions:
            actObject = mb.action(action[0], self.tr(action[1]), mks.monkeystudio.getIcon(action[2]), self.tr(action[3]), self.tr(action[4]))
            actObject.triggered.connect(action[5])
            actObject.modeToSwitch = action[6]
        mb.endGroup()

    def __del__(self):
        """Plugin termination
        """
        mb = mks.mks.monkeycore.menuBar()
        
        mb.beginGroup( "mEdit/mSearchReplace" )
        for action in self.actions:
            mb.action( action[0]).deleteLater()
        mb.endGroup()
    
    def modeSwitchTriggered(self):
        newMode = self.sender().modeToSwitch
        # TODO if  ( document and document.editor() ) or not document :
        if mode & ModeFlagFile:
            # TODO check if editor is a QScintilla
            self.widget.setMode(mode)
        elif mode & ModeFlagDirectory:
            self.widget.setMode(mode)
        elif mode & ModeFlagProjectFiles:  # TODO
            pass
        elif mode & ModeFlagOpenedFiles:
            if mks.workspace.openedDocuments()  # TODO check if have file based document
                self.widget.setMode(mode)


class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """
    def __init__(self, plugin, parent):
        QFrame.__init__(parent)
        self.plugin = plugin
        uic.loadUi('mks/SearchWidget.ui', self)
        
        self.cbSearch.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.cbReplace.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.fsModel = QDirModel( self )
        self.fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.cbPath.lineEdit().setCompleter( QCompleter( self.fsModel ) )
        #warning QDirModel is deprecated but QCompleter does not yet handle QFileSystemModel - please update when possible.
        self.cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.cbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self.mProgress = QProgressBar( self )
        self.mProgress.setAlignment( Qt.AlignCenter )
        self.mProgress.setToolTip( tr( "Search in progress..." ) )
        self.mProgress.setMaximumSize( QSize( 80, 16 ) )
        mks.mks.monkeycore.mainWindow().statusBar().insertPermanentWidget( 0, self.mProgress )
        self.mProgress.setVisible( False )

        # threads
        self.mSearchThread = SearchThread( self )
        self.mReplaceThread = ReplaceThread( self )

        self.mDock = 0
        
        # mode actions
        self.tbMode = QToolButton( self.cbSearch.lineEdit() )
        self.tbMode.setIcon( pIconManager.icon( "misc.png" ) )
        self.tbMode.setPopupMode( QToolButton.InstantPopup )
        self.tbMode.setMenu( mks.monkeycore.menuBar().menu( "mEdit/mSearchReplace" ) )
        self.tbMode.setCursor( Qt.ArrowCursor )
        self.tbMode.installEventFilter( self )
        
        # cd up action
        self.tbCdUp = QToolButton( self.cbPath.lineEdit() )
        self.tbCdUp.setIcon( pIconManager.icon( "go-up.png" ) )
        self.tbCdUp.setCursor( Qt.ArrowCursor )
        self.tbCdUp.installEventFilter( self )

        # options actions
        self.mModeActions = {}
        action = QAction( self.cbCaseSensitive )
        action.setCheckable( True )
        self.cbCaseSensitive.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionCaseSensitive ] = action
        
        action = QAction( self.cbWholeWord )
        action.setCheckable( True )
        self.cbWholeWord.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionWholeWord ] = action
        
        action = QAction( self.cbWrap )
        action.setCheckable( True )
        self.cbWrap.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionWrap ] = action
        
        action = QAction( self.cbRegularExpression )
        action.setCheckable( True )
        self.cbRegularExpression.toggled.connect(action.setChecked)
        self.mModeActions[ SearchAndReplace.OptionRegularExpression ] = action
        
        # init default options
        self.cbWrap.setChecked( True )
        
        """TODO
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
        """
        
        """TODO
        # mask tooltip
        languages = pMonkeyStudio.availableLanguages()
        
        for ( i = 0; i < languages.count(); i += 10 )
            languages[ i ].prepend( "\n" )

        
        maskToolTip = tr( "Space separated list of wildcards, *.h *.cpp file???.txt\n"
            "You can use language name too so the search will only apply to the language suffixes.\n"
            "Available languages: %1" ).arg( languages.join( ", " ) )
        
        self.cbMask.setToolTip( maskToolTip )
        """
        
        # codecs
        cbCodec.addItems( QTextCodec.availableCodecs().sorted() )
        
        """TODO
        cbCodec.setCurrentIndex( cbCodec.findText( pMonkeyStudio.defaultCodec() ) )
        """

        # connections
        self.cbSearch.lineEdit().textEdited.connect(self.search_textChanged)
        self.tbCdUp.clicked.connect(self.cdUp_clicked)
        self.mSearchThread.started.connect(self.searchThread_stateChanged)
        self.mSearchThread.finished.connect(self.searchThread_stateChanged)
        self.mSearchThread.progressChanged.connect(self.searchThread_progressChanged)
        self.mReplaceThread.started.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.finished.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.openedFileHandled.connect(self.replaceThread_openedFileHandled)
        self.mReplaceThread.error.connect(self.replaceThread_error)

        setMode( SearchAndReplace.ModeSearch )

    def mode(self):  # FIXME remove
        returnself.mMode

    def searchThread(self):  # FIXME remove
        return self.mSearchThread

    def setResultsDock(self, dock ):
        if  self.mDock == dock :
            return

        self.mDock = dock

        # connections
        self.mReplaceThread.resultsHandled.connect(self.mDock.model().thread_resultsHandled)

    def isBinary(self, file ):
        position = file.pos()
        file.seek( 0 )
        binary = file.read( 1024 ).contains( '\0' )
        file.seek( position )
        return binary

    def setMode(self, mode ):
        self.mSearchThread.stop()
        self.mReplaceThread.stop()
        
        currentDocumentOnly = False
        
        # clear search results if needed.
        if mode & SearchAndReplace.ModeFlagFile:
            currentDocumentOnly = True
        else
            currentDocumentOnly = False
            self.mSearchThread.clear()
        
        self.mMode = mode
        
        self.initializeProperties( currentDocumentOnly )
        
        if self.mMode & SearchAndReplace.ModeFlagProjectFiles :
            if  mProperties.project :
                codec = mProperties.project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
                
                mProperties.codec = codec
                cbCodec.setCurrentIndex( cbCodec.findText( codec ) )

        assert( not mProperties.codec.isEmpty() )
        
        document = mks.monkeycore.workspace().currentDocument()
        # TODO editor = document ? document.editor() : 0
        path = mProperties.project ? mProperties.project.path() : QDir.currentPath()
        searchPath = document ? QFileInfo( document.filePath() ).absolutePath() : path
        # TODO searchText = editor ? editor.selectedText() : QString.null
        wasVisible = self.isVisible()

        self.setVisible( mode != SearchAndReplace.ModeNo )

        if  isVisible() :
            if  mProperties.settings.replaceSearchText :
                isRE = mProperties.options & SearchAndReplace.OptionRegularExpression
                isEmpty = searchText.isEmpty()
                validateVisibility = not mProperties.settings.onlyWhenNotVisible or ( mProperties.settings.onlyWhenNotVisible and not wasVisible )
                validateRegExp = not mProperties.settings.onlyWhenNotRegExp or ( mProperties.settings.onlyWhenNotRegExp and not isRE )
                validateEmpty = not mProperties.settings.onlyWhenNotEmpty or ( mProperties.settings.onlyWhenNotEmpty and not isEmpty )
                
                if  validateVisibility and validateRegExp and validateEmpty :
                    self.cbSearch.setEditText( searchText )

            if  mode & SearchAndReplace.ModeFlagSearch :
                self.cbSearch.setFocus()
                self.cbSearch.lineEdit().selectAll()
            else:
                self.cbReplace.setFocus()
                self.cbReplace.lineEdit().selectAll()
            
            if  mode & SearchAndReplace.ModeFlagDirectory :
                self.cbPath.setEditText( searchPath )
        
        # hlamer: I'm sory for long lines, but, even workse without it
        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask, self.wCodec,)
        #                                                       wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAL  pbRCHK wOpti wMask wCodec
        visible = {SearchAndReplace.ModeNo     :             (    0,     0,     0,     0,     0,     0,     0,     0,     0,    0,    0,    0,),
                   SearchAndReplace.ModeSearch :             (    0,     1,     1,     1,     0,     0,     0,     0,     0,    0,    0,    0,),
                   SearchAndReplace.ModeReplace:             (    1,     1,     1,     0,     1,     0,     1,     1,     1,    0,    0,    0,),
                   SearchAndReplace.ModeSearchDirectory:     (    1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeReplaceDirectory:    (    1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,    1,),
                   SearchAndReplace.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeSearchProjectFiles:  (    1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,    1,),
                   SearchAndReplace.ModeReplaceProjectFiles: (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    1,),
                   SearchAndReplace.ModeSearchOpenedFiles:   (    1,     0,     0,     1,     1,     0,     0,     0,     0     1,    1,    0,),
                   SearchAndReplace.ModeReplaceOpenedFiles:  (    1,     0,     0,     1,     1,     0,     0,     0,     1     1,    1,    0,),
                    
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i]

        self.updateLabels()()
        self.updateWidgets()()

    def eventFilter(self, object, event ):
        if  event.type() == QEvent.Paint :
            toolButton = qobject_cast<QToolButton*>( object )
            lineEdit = object == self.tbMode ? self.cbSearch.lineEdit() : self.cbPath.lineEdit()
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
                    mks.monkeycore.workspace().focusEditor()
                    hide()

                    break

                case Qt.Key_Enter:
                case Qt.Key_Return:
                    switch (self.mMode )
                        case SearchAndReplace.ModeNo:
                            break
                        case SearchAndReplace.ModeSearch:
                            self.pbNext.click()
                            break
                        case SearchAndReplace.ModeSearchDirectory:
                        case SearchAndReplace.ModeSearchProjectFiles:
                        case SearchAndReplace.ModeSearchOpenedFiles:
                            self.pbSearch.click()
                            break
                        case SearchAndReplace.ModeReplace:
                            self.pbReplace.click()
                            break
                        case SearchAndReplace.ModeReplaceDirectory:
                        case SearchAndReplace.ModeReplaceProjectFiles:
                        case SearchAndReplace.ModeReplaceOpenedFiles:
                            self.pbReplaceChecked.click()
                            break


                    break




        QWidget.keyPressEvent( event )


    def self.updateLabels()(self):
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


    def self.updateWidgets()(self):
        width = 0

        if  self.wSearchRight.isVisible() :
            width = qMax( width, self.wSearchRight.minimumSizeHint().width() )


        if  self.wReplaceRight.isVisible() :
            width = qMax( width, self.wReplaceRight.minimumSizeHint().width() )


        if  self.wPathRight.isVisible() :
            width = qMax( width, self.wPathRight.minimumSizeHint().width() )


        self.wSearchRight.setMinimumWidth( width )
        self.wReplaceRight.setMinimumWidth( width )
        self.wPathRight.setMinimumWidth( width )


    def updateComboBoxes(self):
         searchText = self.cbSearch.currentText()
         replaceText = self.cbReplace.currentText()
         maskText = self.cbMask.currentText()
        int index
        
        # search
        if  not searchText.isEmpty() :
            index = self.cbSearch.findText( searchText )
            
            if  index == -1 :
                self.cbSearch.addItem( searchText )


        
        # replace
        if  not replaceText.isEmpty() :
            index = self.cbReplace.findText( replaceText )
            
            if  index == -1 :
                self.cbReplace.addItem( replaceText )


        
        # mask
        if  not maskText.isEmpty() :
            index = self.cbMask.findText( maskText )
            
            if  index == -1 :
                self.cbMask.addItem( maskText )




    def self.initializeProperties(self, currentDocumentOnly ):
         QMap<QString, suffixes = pMonkeyStudio.availableLanguagesSuffixes()
         keys = suffixes.keys()
        mProperties.searchText = self.cbSearch.currentText()
        mProperties.replaceText = self.cbReplace.currentText()
        mProperties.searchPath = self.cbPath.currentText()
        mProperties.mode =self.mMode
        mProperties.mask.clear()
        mProperties.codec = cbCodec.currentText()
        mProperties.options = SearchAndReplace.Options( SearchAndReplace.ModeNo )
        mProperties.openedFiles.clear()
        mProperties.project = mks.monkeycore.fileManager().currentProject()
        mProperties.sourcesFiles.clear()
        mProperties.settings = mPlugin.settings()

        # update masks
        for part in self.cbMask.currentText(:.split( " ", QString.SkipEmptyParts ) )
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
        foreach (  SearchAndReplace.Option& option, self.mModeActions.keys() )
            action = self.mModeActions[ option ]

            if  action.isChecked() :
                mProperties.options |= option


        
        # update project
        mProperties.project = mProperties.project ? mProperties.project.topLevelProject() : 0
        
        if  currentDocumentOnly :
            return


        # update opened files
        for document in mks.monkeycore.workspace().documents():
            mProperties.openedFiles[ document.filePath() ] = document.fileBuffer()


        # update sources files
        mProperties.sourcesFiles = mProperties.project ? mProperties.project.topLevelProjectSourceFiles() : QStringList()


    def showMessage(self, status ):
        if  status.isEmpty() :
            mks.mks.monkeycore.mainWindow().statusBar().clearMessage()

        else:
            mks.mks.monkeycore.mainWindow().statusBar().showMessage( status, 30000 )



    def setState(self, field, state ):
        widget = 0
        color = QColor( Qt.white )

        switch ( field )
            case SearchWidget.Search:
                widget = self.cbSearch.lineEdit()
                break
            case SearchWidget.Replace:
                widget = self.cbReplace.lineEdit()
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
        document = mks.monkeycore.workspace().currentDocument()
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
        document = mks.monkeycore.workspace().currentDocument()
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
                self.pbNext.click(); # move selection to next item



        showMessage( tr( "%1 occurrence(s) replaced." ).arg( count ) )

        return True


    def searchThread_stateChanged(self):
        self.cbSearchStop.setVisible( self.mSearchThread.isRunning() )
        self.updateWidgets()()
        self.mProgress.setVisible( self.mSearchThread.isRunning() )


    def searchThread_progressChanged(self, value, total ):
        self.mProgress.setValue( value )
        self.mProgress.setMaximum( total )


    def replaceThread_stateChanged(self):
        self.pbReplaceCheckedStop.setVisible( self.mReplaceThread.isRunning() )
        self.updateWidgets()()


    def replaceThread_openedFileHandled(self, fileName, content, codec ):
        document = mks.monkeycore.fileManager().openFile( fileName, codec )
        editor = document.editor()

        Q_ASSERT( editor )

        editor.beginUndoAction()
        editor.selectAll()
        editor.removeSelectedText()
        editor.insert( content )
        editor.endUndoAction()


    def replaceThread_error(self, error ):
        mks.monkeycore.messageManager().appendMessage( error )


    def search_textChanged(self):
        self.initializeProperties( True )
        
        # clear search results if needed.
        switch (self.mMode )
            case SearchAndReplace.ModeSearch:
                searchFile( True, True )
            case SearchAndReplace.ModeReplace:
                break
            default:
                self.mSearchThread.clear()
                break



    def cdUp_clicked(self):
        QDir dir( self.cbPath.currentText() )
        
        if  not dir.exists() :
            return

        
        dir.cdUp()
        
        self.cbPath.setEditText( dir.absolutePath() )


    def on_pbPrevious_clicked(self):
        updateComboBoxes()
        self.initializeProperties( True )
        searchFile( False, False )


    def on_pbNext_clicked(self):
        updateComboBoxes()
        self.initializeProperties( True )
        searchFile( True, False )


    def on_pbSearch_clicked(self):
        setState( SearchWidget.Search, SearchWidget.Normal )
        updateComboBoxes()
        self.initializeProperties( False )
        
        if  mProperties.searchText.isEmpty() :
            mks.monkeycore.messageManager().appendMessage( tr( "You can't search for NULL text." ) )
            return

        
        if  mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not mProperties.project :
            mks.monkeycore.messageManager().appendMessage( tr( "You can't search in project files because there is no opened projet." ) )
            return

        
        self.mSearchThread.search( mProperties )


    def on_pbSearchStop_clicked(self):
        self.mSearchThread.stop()


    def on_pbReplace_clicked(self):
        updateComboBoxes()
        self.initializeProperties( True )
        replaceFile( False )


    def on_pbReplaceAll_clicked(self):
        updateComboBoxes()
        self.initializeProperties( True )
        replaceFile( True )


    def on_pbReplaceChecked_clicked(self):
        QHash<QString, items
        model = self.mDock ? self.mDock.model() : 0

        Q_ASSERT( model )

        updateComboBoxes()
        self.initializeProperties( False )
        
        if  mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not mProperties.project :
            mks.monkeycore.messageManager().appendMessage( tr( "You can't replace in project files because there is no opened projet." ) )
            return


        foreach (  SearchResultsModel.ResultList& results, model.results() )
            foreach ( SearchResultsModel.Result* result, results )
                if  result.enabled and result.checkState == Qt.Checked :
                    items[ result.fileName ] << result

                else:
                     index = self.mDock.model().index( result )
                    self.mDock.model().setData( index, False, SearchResultsModel.EnabledRole )




        self.mReplaceThread.replace( mProperties, items )


    def on_pbReplaceCheckedStop_clicked(self):
        self.mReplaceThread.stop()


    def on_pbBrowse_clicked(self):
         path = QFileDialog.getExistingDirectory( self, tr( "Search path" ), self.cbPath.currentText() )

        if  not path.isEmpty() :
            self.cbPath.setEditText( path )
