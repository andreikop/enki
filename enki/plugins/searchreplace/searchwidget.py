# -*- coding: utf-8 -*-
"""
searchwidget --- Search widget and controler
============================================

Module implements search widget and manages search and replace operations
"""

import os.path
import re


from PyQt4.QtCore import QDir, QEvent, \
                         QRect, QSize, Qt, \
                         pyqtSignal

from PyQt4.QtGui import QApplication, QCompleter, QColor, QDirModel, QFileDialog,  \
                        QFrame, QFileDialog, QIcon, \
                        QKeySequence, \
                        QPainter,  \
                        QPalette, \
                        QProgressBar, \
                        QShortcut, \
                        QToolButton, QWidget

from enki.core.core import core

import searchresultsmodel

from controller import *

class SearchWidget(QFrame):
    """Widget, appeared, when Ctrl+F pressed.
    Has different forms for different search modes
    """

    Normal = 'normal'
    Good = 'good'
    Bad = 'bad'
    Incorrect = 'incorrect'

    visibilityChanged = pyqtSignal(bool)
    """
    visibilityChanged(visible)
    
    **Signal** emitted, when widget has been shown or hidden
    """  # pylint: disable=W0105

    searchInDirectoryStartPressed = pyqtSignal(type(re.compile('')), list, unicode)
    """
    searchInDirectoryStartPressed(regEx, mask, path)
    
    **Signal** emitted, when 'search in directory' button had been pressed
    """  # pylint: disable=W0105

    searchInDirectoryStopPressed = pyqtSignal()
    """
    searchInDirectoryStopPressed()
    
    **Signal** emitted, when 'stop search in directory' button had been pressed
    """  # pylint: disable=W0105

    replaceCheckedStartPressed = pyqtSignal(unicode)
    """
    replaceCheckedStartPressed(replText)
    
    **Signal** emitted, when 'replace checked' button had been pressed
    """  # pylint: disable=W0105

    replaceCheckedStopPressed = pyqtSignal()
    """
    replaceCheckedStartPressed()
    
    **Signal** emitted, when 'stop replacing checked' button had been pressed
    """  # pylint: disable=W0105

    searchRegExpChanged = pyqtSignal(type(re.compile('')))
    """
    searchRegExpValidStateChanged(regEx)
    
    **Signal** emitted, when search regexp has been changed.
    If reg exp is invalid - regEx object contains empty pattern
    """  # pylint: disable=W0105

    searchNext = pyqtSignal()
    """
    searchNext()
    
    **Signal** emitted, when 'Search Next' had been pressed
    """  # pylint: disable=W0105

    searchPrevious = pyqtSignal()
    """
    searchPrevious()
    
    **Signal** emitted, when 'Search Previous' had been pressed
    """  # pylint: disable=W0105

    replaceFileOne = pyqtSignal(unicode)
    """
    replaceFileOne(replText)
    
    **Signal** emitted, when 'Replace' had been pressed
    """  # pylint: disable=W0105

    replaceFileAll = pyqtSignal(unicode)
    """
    replaceFileAll(replText)
    
    **Signal** emitted, when 'Replace All' had been pressed
    """  # pylint: disable=W0105

    def __init__(self, plugin):
        QFrame.__init__(self, core.workspace())
        self._mode = None
        self.plugin = plugin
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'SearchWidget.ui'), self)
        
        self.cbSearch.setCompleter(None)
        self.cbReplace.setCompleter(None)
        self.cbMask.setCompleter(None)
        
        self.fsModel = QDirModel(self.cbPath.lineEdit())
        self.fsModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.cbPath.lineEdit().setCompleter(QCompleter(self.fsModel,
                                                       self.cbPath.lineEdit() ))
        # TODO QDirModel is deprecated but QCompleter does not yet handle
        # QFileSystemodel - please update when possible."""
        self.cbSearch.setCompleter(None)
        self.pbSearchStop.setVisible( False )
        self.pbReplaceCheckedStop.setVisible( False )
        
        self._progress = QProgressBar( self )
        self._progress.setAlignment( Qt.AlignCenter )
        self._progress.setToolTip( self.tr( "Search in progress..." ) )
        self._progress.setMaximumSize( QSize( 80, 16 ) )
        core.mainWindow().statusBar().insertPermanentWidget( 1, self._progress )
        self._progress.setVisible( False )

        # cd up action
        self.tbCdUp = QToolButton( self.cbPath.lineEdit() )
        self.tbCdUp.setIcon( QIcon( ":/enkiicons/go-up.png" ) )
        self.tbCdUp.setCursor( Qt.ArrowCursor )
        self.tbCdUp.installEventFilter( self )  # for drawing button
        
        self.cbSearch.installEventFilter(self)  # for catching Tab and Shift+Tab
        self.cbReplace.installEventFilter(self)  # for catching Tab and Shift+Tab
        self.cbPath.installEventFilter(self)  # for catching Tab and Shift+Tab
        self.cbMask.installEventFilter(self)  # for catching Tab and Shift+Tab
        
        self._closeShortcut = QShortcut( QKeySequence( "Esc" ), self )
        self._closeShortcut.setContext( Qt.WidgetWithChildrenShortcut )
        self._closeShortcut.activated.connect(self.hide)

        # connections        
        self.cbSearch.lineEdit().textChanged.connect(self._onSearchRegExpChanged)
        
        self.cbSearch.lineEdit().returnPressed.connect(self._onReturnPressed)
        self.cbReplace.lineEdit().returnPressed.connect(self._onReturnPressed)
        self.cbPath.lineEdit().returnPressed.connect(self._onReturnPressed)
        self.cbMask.lineEdit().returnPressed.connect(self._onReturnPressed)
        
        self.cbRegularExpression.stateChanged.connect(self._onSearchRegExpChanged)
        self.cbCaseSensitive.stateChanged.connect(self._onSearchRegExpChanged)
        self.cbWholeWord.stateChanged.connect(self._onSearchRegExpChanged)
        
        self.tbCdUp.clicked.connect(self._onCdUpPressed)
        
        self.pbNext.pressed.connect(self.searchNext)
        self.pbPrevious.pressed.connect(self.searchPrevious)
        self.pbSearchStop.pressed.connect(self.searchInDirectoryStopPressed)
        self.pbReplaceCheckedStop.pressed.connect(self.replaceCheckedStopPressed)
        
        core.mainWindow().hideAllWindows.connect(self.hide)
        core.workspace().escPressed.connect(self.hide)
        
        core.workspace().currentDocumentChanged.connect( \
                    lambda old, new: self.setVisible(self.isVisible() and new is not None))

    def show(self):
        """Reimplemented function. Sends signal
        """
        super(SearchWidget, self).show()
        self.visibilityChanged.emit(self.isVisible())

    def hide(self):
        """Reimplemented function.
        Sends signal, returns focus to workspace
        """
        super(SearchWidget, self).hide()
        core.workspace().focusCurrentDocument()
        self.visibilityChanged.emit(self.isVisible())
    
    def setVisible(self, visible):
        """Reimplemented function. Sends signal
        """
        super(SearchWidget, self).setVisible(visible)
        self.visibilityChanged.emit(self.isVisible())
    
    def _regExEscape(self, text):
        """Improved version of re.escape()
        Doesn't escape space, comma, underscore.
        Escapes \n and \t
        """
        text = re.escape(text)
        # re.escape escapes space, comma, underscore, but, it is not necessary and makes text not readable
        for symbol in (' ,_=\'"/:@#%&'):
            text = text.replace('\\' + symbol, symbol)
        
        text = text.replace('\\\n', '\\n')
        text = text.replace('\\\t', '\\t')

        return text
    
    def _makeEscapeSeqsVisible(self, text):
        """Replace invisible \n and \t with escape sequences
        """
        text = text.replace('\\', '\\\\')
        text = text.replace('\t', '\\t')
        text = text.replace('\n', '\\n')
        return text
    
    def setMode(self, mode ):
        """Change search mode.
        i.e. from "Search file" to "Replace directory"
        """
        if self._mode == mode and self.isVisible():
            if core.workspace().currentDocument() is not None and \
               not core.workspace().currentDocument().hasFocus():
                self.cbSearch.lineEdit().selectAll()
                self.cbSearch.setFocus()

        self._mode = mode

        # Set Search and Replace text
        document = core.workspace().currentDocument()
        if document is not None and \
           document.hasFocus() and \
           document.qutepart.selectedText:
            searchText = document.qutepart.selectedText

            self.cbReplace.setEditText(self._makeEscapeSeqsVisible(searchText) )

            if self.cbRegularExpression.checkState() == Qt.Checked:
                searchText = self._regExEscape(searchText)
            self.cbSearch.setEditText( searchText )
        
        if not self.cbReplace.lineEdit().text() and \
            self.cbSearch.lineEdit().text() and \
            not self.cbRegularExpression.checkState() == Qt.Checked:
                replaceText = self.cbSearch.lineEdit().text().replace('\\', '\\\\')
                self.cbReplace.setEditText(replaceText)

        # Move focus to Search edit
        self.cbSearch.setFocus()
        self.cbSearch.lineEdit().selectAll()
        
        # Set search path
        if mode & MODE_FLAG_DIRECTORY and \
           not (self.isVisible() and self.cbPath.isVisible()):
            try:
                searchPath = os.path.abspath(unicode(os.path.curdir))
                self.cbPath.setEditText( searchPath )
            except OSError:  # current directory might have been deleted
                pass 

        # Set widgets visibility flag according to state
        widgets = (self.wSearch, self.pbPrevious, self.pbNext, self.pbSearch, self.wReplace, self.wPath, \
                   self.pbReplace, self.pbReplaceAll, self.pbReplaceChecked, self.wOptions, self.wMask)
        #                         wSear  pbPrev pbNext pbSear wRepl  wPath  pbRep  pbRAll pbRCHK wOpti wMask 
        visible = \
        {MODE_SEARCH :               (1,     1,     1,     0,     0,     0,     0,     1,     1,    1,    0,),
         MODE_REPLACE:               (1,     1,     1,     0,     1,     0,     1,     1,     0,    1,    0,),
         MODE_SEARCH_DIRECTORY:      (1,     0,     0,     1,     0,     1,     0,     0,     0,    1,    1,),
         MODE_REPLACE_DIRECTORY:     (1,     0,     0,     1,     1,     1,     0,     0,     1,    1,    1,),
         MODE_SEARCH_OPENED_FILES:   (1,     0,     0,     1,     0,     0,     0,     0,     0,    1,    1,),
         MODE_REPLACE_OPENED_FILES:  (1,     0,     0,     1,     1,     0,     0,     0,     1,    1,    1,)}
        
        for i, widget in enumerate(widgets):
            widget.setVisible(visible[mode][i])

        # Search next button text
        if mode == MODE_REPLACE:
            self.pbNext.setText('Next')
        else:
            self.pbNext.setText(u'Next↵')

        # Finaly show all with valid size
        self.show()  # show before updating widgets and labels
        self._updateLabels()
        self._updateWidgets()

    def eventFilter(self, object_, event ):
        """ Event filter for mode switch tool button
        Draws icons in the search and path lineEdits
        """
        if  event.type() == QEvent.Paint and object_ is self.tbCdUp:  # draw CdUp button in search path QLineEdit
            toolButton = object_
            lineEdit = self.cbPath.lineEdit()
            lineEdit.setContentsMargins( lineEdit.height(), 0, 0, 0 )
            
            height = lineEdit.height()
            availableRect = QRect( 0, 0, height, height )
            
            if  toolButton.rect() != availableRect :
                toolButton.setGeometry( availableRect )
            
            painter = QPainter ( toolButton )
            toolButton.icon().paint( painter, availableRect )
            
            return True
        
        elif event.type() == QEvent.KeyPress:  # Tab and Shift+Tab in QLineEdits
            
            if event.key() == Qt.Key_Tab:
                self._moveFocus(1)
                return True
            elif event.key() == Qt.Key_Backtab:
                self._moveFocus(-1)
                return True

        return QFrame.eventFilter( self, object_, event )

    def _onReturnPressed(self):
        """Return or Enter pressed on widget.
        Search next or Replace next
        """
        if self.pbReplace.isVisible():
            self.pbReplace.click()
        elif self.pbNext.isVisible():
            self.pbNext.click()
        elif self.pbSearch.isVisible():
            self.pbSearch.click()
        elif self.pbSearchStop.isVisible():
            self.pbSearchStop.click()
    
    def _moveFocus(self, step):
        """Move focus forward or backward according to step.
        Standard Qt Keyboard focus algorithm doesn't allow circular navigation
        """
        allFocusableWidgets = (self.cbSearch, self.cbReplace, self.cbPath, self.cbMask)
        visibleWidgets = [widget for widget in allFocusableWidgets \
                                    if widget.isVisible()]
        
        try:
            focusedIndex = visibleWidgets.index(QApplication.focusWidget())
        except ValueError:
            print >> sys.stderr, 'Invalid focused widget in Search Widget'
            return
        
        nextFocusedIndex = (focusedIndex + step) % len(visibleWidgets)
        
        visibleWidgets[nextFocusedIndex].setFocus()
        visibleWidgets[nextFocusedIndex].lineEdit().selectAll()

    def _updateLabels(self):
        """Update 'Search' 'Replace' 'Path' labels geometry
        """
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


    def _updateWidgets(self):
        """Update geometry of widgets with buttons
        """
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
        """Update comboboxes with last used texts
        """
        searchText = self.cbSearch.currentText()
        replaceText = self.cbReplace.currentText()
        maskText = self.cbMask.currentText()
        
        # search
        if searchText:
            index = self.cbSearch.findText( searchText )
            
            if  index == -1 :
                self.cbSearch.addItem( searchText )
        
        # replace
        if replaceText:
            index = self.cbReplace.findText( replaceText )
            
            if  index == -1 :
                self.cbReplace.addItem( replaceText )

        # mask
        if maskText:
            index = self.cbMask.findText( maskText )
            
            if  index == -1 :
                self.cbMask.addItem( maskText )
    
    def _searchPatternTextAndFlags(self):
        """Get search pattern and flags
        """
        pattern = self.cbSearch.currentText()
        
        pattern = pattern.replace(u'\u2029', '\n')  # replace unicode paragraph separator with habitual \n
        
        if not self.cbRegularExpression.checkState() == Qt.Checked:
            pattern = re.escape(pattern)
        
        if self.cbWholeWord.checkState() == Qt.Checked:
            pattern = r'\b' + pattern + r'\b'
        
        flags = 0
        if not self.cbCaseSensitive.checkState() == Qt.Checked:
            flags = re.IGNORECASE
        return pattern, flags

    def getRegExp(self):
        """Read search parameters from controls and present it as a regular expression
        """
        pattern, flags = self._searchPatternTextAndFlags()
        return re.compile(pattern, flags)
    
    def isSearchRegExpValid(self):
        """Try to compile search pattern to check if it is valid
        Returns bool result and text error
        """
        pattern, flags = self._searchPatternTextAndFlags()
        try:
            re.compile(pattern, flags)
        except re.error, ex:
            return False, unicode(ex)
        
        return True, None

    def _getSearchMask(self):
        """Get search mask as list of patterns
        """
        mask = [s.strip() for s in self.cbMask.currentText().split(' ')]
        # remove empty
        mask = filter(None, mask)
        return mask

    def setState(self, state ):
        """Change line edit color according to search result
        """
        widget = self.cbSearch.lineEdit()

        color = {SearchWidget.Normal: QApplication.instance().palette().color(QPalette.Base), \
                 SearchWidget.Good: QColor(Qt.green), \
                 SearchWidget.Bad: QColor(Qt.red),
                 SearchWidget.Incorrect: QColor(Qt.darkYellow)}
        
        stateColor = color[state]
        if state != SearchWidget.Normal:
            stateColor.setAlpha(100)
        
        pal = widget.palette()
        pal.setColor( widget.backgroundRole(), stateColor )
        widget.setPalette( pal )
    
    def setSearchInProgress(self, inProgress):
        """Search thread started or stopped
        """
        self.pbSearchStop.setVisible( inProgress )
        self.pbSearch.setVisible( not inProgress )
        self._updateWidgets()
        self._progress.setVisible( inProgress )

    def onSearchProgressChanged(self, value, total ):
        """Signal from the thread, progress changed
        """
        self._progress.setValue( value )
        self._progress.setMaximum( total )

    def setReplaceInProgress(self, inProgress):
        """Replace thread started or stopped
        """
        self.pbReplaceCheckedStop.setVisible( inProgress )
        self.pbReplaceChecked.setVisible( not inProgress )
        self._updateWidgets()
    
    def setSearchInFileActionsEnabled(self, enabled):
        """Set enabled state for Next, Prev, Replace, ReplaceAll
        """
        for button in (self.pbNext, self.pbPrevious, self.pbReplace, self.pbReplaceAll):
            button.setEnabled(enabled)
    
    def _onSearchRegExpChanged(self):
        """User edited search text or checked/unchecked checkboxes
        """
        valid, error = self.isSearchRegExpValid()
        if valid:
            self.setState(self.Normal)
            core.mainWindow().statusBar().clearMessage()
            self.pbSearch.setEnabled(len(self.getRegExp().pattern) > 0)
        else:
            core.mainWindow().statusBar().showMessage(error, 3000)
            self.setState(self.Incorrect)
            self.pbSearch.setEnabled(False)
            self.searchRegExpChanged.emit(re.compile(''))
            return

        self.searchRegExpChanged.emit(self.getRegExp())

    def _onCdUpPressed(self):
        """User pressed "Up" button, need to remove one level from search path
        """
        text = self.cbPath.currentText()
        if not os.path.exists(text):
            return
        
        editText = os.path.abspath(os.path.join(text, os.path.pardir))
        self.cbPath.setEditText(editText)

    def on_pbSearch_pressed(self):
        """Handler of click on "Search" button (for search in directory)
        """
        self.setState(SearchWidget.Normal )

        self.searchInDirectoryStartPressed.emit(self.getRegExp(),
                                                self._getSearchMask(),
                                                self.cbPath.currentText())

    def on_pbReplace_pressed(self):
        """Handler of click on "Replace" (in file) button
        """
        self.replaceFileOne.emit(self.cbReplace.currentText())

    def on_pbReplaceAll_pressed(self):
        """Handler of click on "Replace all" (in file) button
        """
        self.replaceFileAll.emit(self.cbReplace.currentText())

    def on_pbReplaceChecked_pressed(self):
        """Handler of click on "Replace checked" (in directory) button
        """
        self.replaceCheckedStartPressed.emit(self.cbReplace.currentText())

    def on_pbBrowse_pressed(self):
        """Handler of click on "Browse" button. Explores FS for search directory path
        """
        path = QFileDialog.getExistingDirectory( self, self.tr( "Search path" ), self.cbPath.currentText() )

        if path:
            self.cbPath.setEditText( path )
