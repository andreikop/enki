"""Search and Replace plugin. S&R GUI and implementation
"""

import os.path

from PyQt4 import uic
from PyQt4.QtCore import Qt, QDir, QEvent, QObject, QRect, QSize, QString, QStringList, QTextCodec
from PyQt4.QtGui import QAction, QCompleter, QColor, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QKeyEvent, QLineEdit, QPainter,  \
                        QProgressBar, QToolButton

import mks.monkeycore

class SearchAndReplace(QObject):  # TODO (Plugin) ?
    
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

    OptionNo = 0x0
    OptionCaseSensitive = 0x1
    OptionWholeWord = 0x2
    OptionWrap = 0x4
    OptionRegularExpression = 0x8
    
    def __init__(self):
        """Plugin initialisation
        """
        QObject.__init__(self)
        self.widget = SearchWidget( self )
        
        self.actions = ( ("aReplaceFile", "&Replace...", "edit/replace.png", "Ctrl+R", "Replace in the current file...", self.modeSwitchTriggered, self.ModeReplace),
                        ("aSearchPrevious", "Search &Previous", "edit/previous.png", "Shift+F3", "Search previous occurrence", self.widget.on_pbPrevious_clicked, None),
                        ("aSearchNext", "Search &Next", "edit/next.png", "F3", "Search next occurrence", self.widget.on_pbNext_clicked, None),
                        ("aSearchDirectory", "Search in &Directory...", "search-replace-directory.png", "Ctrl+Shift+F", "Search in directory...", self.modeSwitchTriggered, self.ModeSearch),
                        ("aReplaceDirectory", "Replace in Director&y...", "search-replace-directory.png", "Ctrl+Shift+R", "Replace in directory...", self.modeSwitchTriggered, self.ModeReplaceDirectory),
                        ("aSearchProjectFiles", "Search in Project &Files...", "search-replace-project-files.png", "Ctrl+Meta+F", "Search in the current project files..", self.modeSwitchTriggered, self.ModeSearchProjectFiles),
                        ("aReplaceProjectFiles", "Replace in Projec&t Files...", "search-replace-project-files.png", "Ctrl+Meta+R", "Replace in the current project files...", self.modeSwitchTriggered, self.ModeReplaceProjectFiles),
                        ("aSearchOpenedFiles", "Search in &Opened Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+F", "Search in opened files...", self.modeSwitchTriggered, self.ModeSearchOpenedFiles),
                        ("aReplaceOpenedFiles", "Replace in Open&ed Files...", "search-replace-opened-files.png", "Ctrl+Alt+Meta+R", "Replace in opened files...", self.modeSwitchTriggered, self.ModeReplaceOpenedFiles))
        
        mks.monkeycore.workspace().layout().addWidget( self.widget )
        self.widget.setVisible( False )
        
        """TODO
        self.dock = SearchResultsDock( self.widget.searchThread() )
        mks.mks.monkeycore.mainWindow().dockToolBar( Qt.BottomToolBarArea ).addDock( self.dock, self.dock.windowTitle(), self.dock.windowIcon() )
        self.dock.setVisible( False )


        self.widget.setResultsDock( self.dock )
        """
        
        mb = mks.monkeycore.menuBar()
        
        mb.beginGroup( "mEdit/mSearchReplace" )
        for action in self.actions:
            actObject = mb.action(action[0], self.tr(action[1]), mks.monkeystudio.getIcon(action[2]), self.tr(action[3]), self.tr(action[4]))
            actObject.triggered.connect(action[5])
            actObject.modeToSwitch = action[6]
        mb.endGroup()

    def __del__(self):
        """Plugin termination
        """
        mb = mks.monkeycore.menuBar()
        
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
            if mks.workspace.openedDocuments():  # TODO check if have file based document
                self.widget.setMode(mode)


class Properties:  # TODO rework it
    searchText = ''
    replaceText = ''
    searchPath = ''
    mode = 0
    mask = []
    codec = ''
    options = 0
    openedFiles = {}
    project = None
    sourcesFiles = ''


class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """
    def __init__(self, plugin):
        QFrame.__init__(self, mks.monkeycore.workspace())
        self.plugin = plugin
        uic.loadUi('mks/SearchWidget.ui', self)
        
        self.mProperties = Properties()
        
        self.cbSearch.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.cbReplace.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.fsModel = QDirModel( self )
        self.fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.cbPath.lineEdit().setCompleter( QCompleter( self.fsModel ) )
        #warning QDirModel is deprecated but QCompleter does not yet handle QFileSystemModel - please update when possible.
        self.cbMask.completer().setCaseSensitivity( Qt.CaseSensitive )
        self.pbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self.mProgress = QProgressBar( self )
        self.mProgress.setAlignment( Qt.AlignCenter )
        self.mProgress.setToolTip( self.tr( "Search in progress..." ) )
        self.mProgress.setMaximumSize( QSize( 80, 16 ) )
        mks.monkeycore.mainWindow().statusBar().insertPermanentWidget( 0, self.mProgress )
        self.mProgress.setVisible( False )
        
        """TODO
        # threads
        self.mSearchThread = SearchThread( self )
        self.mReplaceThread = ReplaceThread( self )
        """

        self.mDock = 0
        
        # mode actions
        self.tbMode = QToolButton( self.cbSearch.lineEdit() )
        self.tbMode.setIcon( mks.monkeystudio.getIcon( "misc.png" ) )
        self.tbMode.setPopupMode( QToolButton.InstantPopup )
        self.tbMode.setMenu( mks.monkeycore.menuBar().menu( "mEdit/mSearchReplace" ) )
        self.tbMode.setCursor( Qt.ArrowCursor )
        self.tbMode.installEventFilter( self )
        
        # cd up action
        self.tbCdUp = QToolButton( self.cbPath.lineEdit() )
        self.tbCdUp.setIcon( mks.monkeystudio.getIcon( "go-up.png" ) )
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

        
        maskToolTip = self.tr( "Space separated list of wildcards, *.h *.cpp file???.txt\n"
            "You can use language name too so the search will only apply to the language suffixes.\n"
            "Available languages: %1" ).arg( languages.join( ", " ) )
        
        self.cbMask.setToolTip( maskToolTip )
        """
        
        # codecs
        slist = QStringList()
        for c in sorted(QTextCodec.availableCodecs()):
            slist.append(QString(c))
        self.cbCodec.addItems(slist)
        
        """TODO
        self.cbCodec.setCurrentIndex( self.cbCodec.findText( pMonkeyStudio.defaultCodec() ) )
        """

        # connections
        self.cbSearch.lineEdit().textEdited.connect(self.search_textChanged)
        self.tbCdUp.clicked.connect(self.cdUp_clicked)
        """TODO
        self.mSearchThread.started.connect(self.searchThread_stateChanged)
        self.mSearchThread.finished.connect(self.searchThread_stateChanged)
        self.mSearchThread.progressChanged.connect(self.searchThread_progressChanged)
        self.mReplaceThread.started.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.finished.connect(self.replaceThread_stateChanged)
        self.mReplaceThread.openedFileHandled.connect(self.replaceThread_openedFileHandled)
        self.mReplaceThread.error.connect(self.replaceThread_error)
        """
        self.setMode( SearchAndReplace.ModeSearch )

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
        """TODO
        self.mSearchThread.stop()
        self.mReplaceThread.stop()
        """
        
        currentDocumentOnly = False
        
        # clear search results if needed.
        if mode & SearchAndReplace.ModeFlagFile:
            currentDocumentOnly = True
        else:
            currentDocumentOnly = False
            self.mSearchThread.clear()
        
        self.mMode = mode
        
        self.initializeProperties( currentDocumentOnly )
        
        if self.mMode & SearchAndReplace.ModeFlagProjectFiles :
            if  self.mProperties.project :
                codec = self.mProperties.project.temporaryValue( "codec", pMonkeyStudio.defaultCodec() ).toString()
                
                self.mProperties.codec = codec
                self.cbCodec.setCurrentIndex( self.cbCodec.findText( codec ) )

        assert( not self.mProperties.codec.isEmpty() )
        
        document = mks.monkeycore.workspace().currentDocument()
        editor = document.qscintilla  # FIXME
        # TODO editor = document ? document.editor() : 0
        path = os.path.abspath(os.path.curdir)
        if editor:
            searchText = editor.selectedText()
        else:
            searchText = ''
        
        wasVisible = self.isVisible()

        self.setVisible( mode != SearchAndReplace.ModeNo )

        if  self.isVisible() :
            if  self.mProperties.settings.replaceSearchText :
                isRE = self.mProperties.options & SearchAndReplace.OptionRegularExpression
                isEmpty = searchText.isEmpty()
                validateVisibility = not self.mProperties.settings.onlyWhenNotVisible or ( self.mProperties.settings.onlyWhenNotVisible and not wasVisible )
                validateRegExp = not self.mProperties.settings.onlyWhenNotRegExp or ( self.mProperties.settings.onlyWhenNotRegExp and not isRE )
                validateEmpty = not self.mProperties.settings.onlyWhenNotEmpty or ( self.mProperties.settings.onlyWhenNotEmpty and not isEmpty )
                
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
                   SearchAndReplace.ModeSearchOpenedFiles:   (    1,     0,     0,     1,     1,     0,     0,     0,     0,    1,    1,    0,),
                   SearchAndReplace.ModeReplaceOpenedFiles:  (    1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,    0,)}
        
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i])

        self.updateLabels()
        self.updateWidgets()

    def eventFilter(self, object, event ):
        if  event.type() == QEvent.Paint :
            toolButton = object
            if toolButton == self.tbMode:
                lineEdit = self.cbSearch.lineEdit()
            else:
                self.cbPath.lineEdit()
            lineEdit.setContentsMargins( lineEdit.height(), 0, 0, 0 )
            
            height = lineEdit.height()
            availableRect = QRect( 0, 0, height, height )
            
            if  toolButton.rect() != availableRect :
                toolButton.setGeometry( availableRect )
            
            painter = QPainter ( toolButton )
            toolButton.icon().paint( painter, availableRect )
            
            return True

        return QFrame.eventFilter( self, object, event )


    def keyPressEvent(self, event ):
        if  event.modifiers() == Qt.NoModifier :
            if event.key() == Qt.Key_Escape:
                mks.monkeycore.workspace().focusEditor()
                self.hide
            elif event.key() in (Qt.Key_Enter, Qt.Key_Return):
                if self.mMode == SearchAndReplace.ModeNo:
                    pass
                elif self.mMode == SearchAndReplace.ModeSearch:
                        self.pbNext.click()
                elif self.mMode in (SearchAndReplace.ModeSearchDirectory, \
                                    SearchAndReplace.ModeSearchProjectFiles, \
                                    SearchAndReplace.ModeSearchOpenedFiles):
                    self.pbSearch.click()
                elif self.mMode == SearchAndReplace.ModeReplace:
                    self.pbReplace.click()
                elif self.mMode in (SearchAndReplace.ModeReplaceDirectory, \
                                    SearchAndReplace.ModeReplaceProjectFiles, \
                                    SearchAndReplace.ModeReplaceOpenedFiles):
                    self.pbReplaceChecked.click()

        QWidget.keyPressEvent( event )

    def updateLabels(self):
        width = 0

        if  self.lSearch.isVisible() :
            width = max( width, self.lSearch.minimumSizeHint().width() )

        if   self.lReplace.isVisible() :
            width = max( width,  self.lReplace.minimumSizeHint().width() )

        if  self.lPath.isVisible() :
            width = max( width, self.lPath.minimumSizeHint().width() )

        self.lSearch.setMinimumWidth( width )
        self.lReplace.setMinimumWidth( width )
        self.lPath.setMinimumWidth( width )


    def updateWidgets(self):
        width = 0

        if  self.wSearchRight.isVisible() :
            width = max( width, self.wSearchRight.minimumSizeHint().width() )

        if  self.wReplaceRight.isVisible() :
            width = max( width, self.wReplaceRight.minimumSizeHint().width() )

        if  self.wPathRight.isVisible() :
            width = max( width, self.wPathRight.minimumSizeHint().width() )

        self.wSearchRight.setMinimumWidth( width )
        self.wReplaceRight.setMinimumWidth( width )
        self.wPathRight.setMinimumWidth( width )

    def updateComboBoxes(self):
        searchText = self.cbSearch.currentText()
        replaceText = self.cbReplace.currentText()
        maskText = self.cbMask.currentText()
        
        # search
        if not searchText.isEmpty() :
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
    
    def initializeProperties(self, currentDocumentOnly ):
        """TODO
        suffixes = pMonkeyStudio.availableLanguagesSuffixes()
        keys = suffixes.keys()
        """
        self.mProperties.searchText = self.cbSearch.currentText()
        self.mProperties.replaceText = self.cbReplace.currentText()
        self.mProperties.searchPath = self.cbPath.currentText()
        self.mProperties.mode = self.mMode
        self.mProperties.mask = []
        self.mProperties.codec = self.cbCodec.currentText()
        self.mProperties.options = SearchAndReplace.ModeNo
        self.mProperties.openedFiles = []
        """TODO
        self.mProperties.project = mks.monkeycore.fileManager().currentProject()
        """
        self.mProperties.sourcesFiles = {}
        
        """TODO
        # update masks
        for part in self.cbMask.currentText().split( " ", QString.SkipEmptyParts ):
            index = keys.indexOf( QRegExp( QRegExp.escape( part ), Qt.CaseInsensitive ) )

            if  index != -1 :
                foreach (  QString& suffixe, suffixes[ keys.at( index ) ] )
                    if  not self.mProperties.mask.contains( suffixe ) :
                        self.mProperties.mask << suffixe
            else:
                self.mProperties.mask << part
        """

        # set default mask if needed
        if  self.mProperties.mask:
            self.mProperties.mask << "*"

        # update options
        for option in self.mModeActions.keys():
            if  self.mModeActions[option].isChecked() :
                self.mProperties.options |= option
        
        """TODO
        # update project
        self.mProperties.project = self.mProperties.project.topLevelProject()
        """
        
        if  currentDocumentOnly :
            return

        # update opened files
        for document in mks.monkeycore.workspace().documents():
            self.mProperties.openedFiles[ document.filePath() ] = document.fileBuffer()

        # update sources files
        self.mProperties.sourcesFiles = []
        if self.mProperties.project:
            self.mProperties.sourcesFiles = self.mProperties.project.topLevelProjectSourceFiles()

    def showMessage (self, status ):
        if  status.isEmpty() :
            mks.monkeycore.mainWindow().statusBar().clearMessage()
        else:
            mks.monkeycore.mainWindow().statusBar().showMessage( status, 30000 )

    def setState(self, field, state ):
        widget = 0
        color = QColor( Qt.white )
        
        if field == SearchWidget.Search:
            widget = self.cbSearch.lineEdit()
        elif field == SearchWidget.Replace:
            widget = self.cbReplace.lineEdit()
        
        widget= {SearchWidget.Search: self.cbSearch.lineEdit(),
                 SearchWidget.Replace: self.cbReplace.lineEdit()}
        
        color = {SearchWidget.Normal: Qt.white, \
                 SearchWidget.Good: Qt.green, \
                 SearchWidget.Bad: Qt.red}
        
        pal = widget[field].palette()
        pal.setColor( widget.backgroundRole(), color[state] )
        widget[field].setPalette( pal )
    
    def searchFile(self, forward, incremental ):
        document = mks.monkeycore.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current editor specific, 
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        # get cursor position
        isRE = self.mProperties.options & SearchAndReplace.OptionRegularExpression
        isCS = self.mProperties.options & SearchAndReplace.OptionCaseSensitive
        isWW = self.mProperties.options & SearchAndReplace.OptionWholeWord
        isWrap = self.mProperties.options & SearchAndReplace.OptionWrap
        
        if  forward :
            if  incremental :
                x, y, temp, temp = editor.getSelection()
            else:
                temp, temp, y, x = editor.getSelection()
        else:
            if  incremental:
                temp, temp, y, x = editor.getSelection()
            else:
                y, x, temp, temp = editor.getSelection()
        
        # search
        found = editor.findFirst( self.mProperties.searchText, isRE, isCS, isWW, isWrap, forward, y, x, True )

        # change background acording to found or not
        if found:
            self.setState( SearchWidget.Search, SearchWidget.Good)
        else:
            self.setState( SearchWidget.Search, SearchWidget.Bad)
        
        # return found state
        return found

    def replaceFile(self, all ):
        document = mks.monkeycore.workspace().currentDocument()
        if document:
            editor = document.qscintilla  # FIXME current version specific
        
        if  not editor :
            self.setState( SearchWidget.Search, SearchWidget.Bad )
            self.showMessage( self.tr( "No active editor" ) )
            return False

        count = 0
        
        if  all :
            isWrap = self.mProperties.options & SearchAndReplace.OptionWrap
            x, y = editor.getCursorPosition(y, x)

            if  isWrap :
                # don't need to give wrap parameter for search as we start at begin of document
                editor.setCursorPosition( 0, 0 )
                self.mProperties.options &= ~SearchAndReplace.OptionWrap

            editor.beginUndoAction()
            
            count = 0
            while ( self.searchFile( True, False ) ): # search next
                editor.replace( self.mProperties.replaceText )
                count += 1

            editor.endUndoAction()
            editor.setCursorPosition( y, x ) # restore cursor position
            
            # restore wrap property if needed
            if  isWrap :
                self.mProperties.options |= SearchAndReplace.OptionWrap

        else:
            y, x, temp, temp = editor.getSelection()
            editor.setCursorPosition( y, x )

            if  self.searchFile( True, False ) :
                editor.beginUndoAction()
                editor.replace( self.mProperties.replaceText )
                editor.endUndoAction()
                count += 1
                self.pbNext.click(); # move selection to next item

        self.showMessage( self.tr( "%1 occurrence(s) replaced." % count ))

        return True

    def searchThread_stateChanged(self):
        self.pbSearchStop.setVisible( self.mSearchThread.isRunning() )
        self.updateWidgets()
        self.mProgress.setVisible( self.mSearchThread.isRunning() )

    def searchThread_progressChanged(self, value, total ):
        self.mProgress.setValue( value )
        self.mProgress.setMaximum( total )

    def replaceThread_stateChanged(self):
        self.pbReplaceCheckedStop.setVisible( self.mReplaceThread.isRunning() )
        self.updateWidgets()

    def replaceThread_openedFileHandled(self, fileName, content, codec ):
        document = mks.monkeycore.fileManager().openFile( fileName, codec )
        editor = document.editor()

        assert( editor )

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
        if self.mMode == SearchAndReplace.ModeSearch:
            self.searchFile( True, True )
        elif self.mMode == SearchAndReplace.ModeReplace:
            self.mSearchThread.clear()

    def cdUp_clicked(self):
        
        if not os.path.exists(self.cbPath.currentText()):
            return

        self.cbPath.setEditText( os.path.abspath(self.cbPath.currentText() + os.path.pardir))

    def on_pbPrevious_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.searchFile( False, False )

    def on_pbNext_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.searchFile( True, False )

    def on_pbSearch_clicked(self):
        self.setState( SearchWidget.Search, SearchWidget.Normal )
        self.updateComboBoxes()
        self.initializeProperties( False )
        
        if  self.mProperties.searchText.isEmpty() :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't search for NULL text." ) )
            return

        if  self.mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not self.mProperties.project :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't search in project files because there is no opened projet." ) )
            return

        self.mSearchThread.search( self.mProperties )

    def on_pbSearchStop_clicked(self):
        self.mSearchThread.stop()

    def on_pbReplace_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.replaceFile( False )

    def on_pbReplaceAll_clicked(self):
        self.updateComboBoxes()
        self.initializeProperties( True )
        self.replaceFile( True )

    def on_pbReplaceChecked_clicked(self):
        model = self.mDock.model()

        self.updateComboBoxes()
        self.initializeProperties( False )
        
        if  self.mProperties.mode & SearchAndReplace.ModeFlagProjectFiles and not self.mProperties.project :
            mks.monkeycore.messageManager().appendMessage( self.tr( "You can't replace in project files because there is no opened projet." ) )
            return

        for results in model.results():
            for result in results:
                if  result.enabled and result.checkState == Qt.Checked :
                    items[ result.fileName ].append(result)
                else:
                    index = model.index( result )
                    self.mDock.model().setData( index, False, SearchResultsModel.EnabledRole )

        self.mReplaceThread.replace( self.mProperties, items )

    def on_pbReplaceCheckedStop_clicked(self):
        self.mReplaceThread.stop()

    def on_pbBrowse_clicked(self):
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if  not path.isEmpty() :
            self.cbPath.setEditText( path )
