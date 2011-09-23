"""
filebrowser --- Dock with file system tree
==========================================
"""
import sys
import fnmatch
import re
import os
import os.path
import operator
import logging

from PyQt4.QtCore import QDir, QRect, QEvent, QModelIndex, QObject, Qt, \
                         pyqtSignal
from PyQt4.QtGui import QAction, QCompleter, QDirModel, \
                        QFrame, QFileSystemModel, \
                        QIcon, QItemSelectionModel, QKeySequence, QComboBox, \
                        QPainter, \
                        QShortcut, QSortFilterProxyModel, QToolButton, QTreeView, QVBoxLayout, QWidget

from PyQt4.fresh import pDockWidget

from mks.core.core import core
from mks.core.uisettings import TextOption, ModuleConfigurator

class Plugin(QObject):
    """File system tree.
    
    Allows to open files quickly
    """
    instance = None

    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        # create dock
        self.dock = DockFileBrowser(core.mainWindow())
        self.dock.hide()
        # add dock to dock toolbar entry
        core.mainWindow().dockToolBar( Qt.LeftToolBarArea ).addDockWidget(self.dock)
        Plugin.instance = self
    
    def __del__(self):
        """Uninstall the plugin
        """
        Plugin.instance = None
        self.dock.deleteLater()

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return Configurator

class Configurator(ModuleConfigurator):
    """ Module configurator.
    
    Used for configure files sorting mode
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = \
        [   TextOption(dialog, core.config(), "FileBrowser/NegativeFilter", dialog.lFilesToHide) ]
    
    def saveSettings(self):
        pass
    
    def applySettings(self):
        Plugin.instance.dock.setFilters(core.config()["FileBrowser"]["NegativeFilter"])

class FileBrowserFilteredModel(QSortFilterProxyModel):
    """Model filters out files using negative filter.
    i.e. does not show .o .pyc and other temporary files
    """
    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)
    
    def setFilters(self, filters):
        """Set list of negative filters. (Wildards of files, which are not visible)
        """
        regExPatterns = map(fnmatch.translate, filters)
        compositeRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
        self.filterRegExp = re.compile(compositeRegExpPattern)
        
        self.invalidateFilter()

    def columnCount(self, parent = QModelIndex()):
        """Column count for the model
        """
        return 1
    
    def hasChildren(self, parent = QModelIndex()):
        """Check if node has children. QAbstractItemModel standard method
        """
        return self.sourceModel().hasChildren( self.mapToSource( parent ) )
        
    def filterAcceptsRow(self, source_row, source_parent):
        """ Main method. Check if file matches filter
        """
        if  source_parent == QModelIndex():
            return True
        return not self.filterRegExp.match(source_parent.child( source_row, 0 ).data().toString() )


class SmartRecents(QObject):
    """Class stores File Browser recent directories and provides variants for combo box.
    
    
    "Active directory" in this class means the last directory, where one or more files has been opened
    """
    MAX_RECENTS_SIZE = 8
    
    STATISTICS_SIZE = 10.
    BONUS_FOR_OPENING = 10.
    MAX_POINTS_COUNT = 100.
    
    _recentsChanged = pyqtSignal(list)

    def __init__(self, fileBrowser):
        QObject.__init__(self)
        self._currDir = None
        self._currIsActive = False
        self._popularDirs = None
        self._loadPopularDirs()
        core.workspace().currentDocumentChanged.connect(self._updateRecents)
        
        # incoming connections
        fileBrowser.rootChanged.connect(self._onRootChanged)
        fileBrowser.fileActivated.connect(self._onFileActivated)
        # outgoing connections
        self._recentsChanged.connect(fileBrowser.updateComboItems)

    def _loadPopularDirs(self):
        """Load popular directories from the config
        """
        self._popularDirs = core.config()["FileBrowser"]["PopularDirs"]  # Directory: popularity points
        for k in self._popularDirs.iterkeys():
            try:
                self._popularDirs[k] = float(self._popularDirs[k])
            except ValueError as ex:
                logging.error('Invalid PopularDirs value: ' + unicode(ex))
                self._popularDirs[k] = 0.0

    def _dirsByPopularity(self):
        """Return list of dirrectories, sorted by popularity
        """
        if not self._popularDirs:
            return ()
        
        dirAndPopularity = sorted(self._popularDirs.iteritems(), key=operator.itemgetter(1), reverse=True)
        dirs = zip(*dirAndPopularity)[0]  # take only first elements
        return dirs
    
    def _onFileActivated(self):
        """FileBrowserDock notifies SmartRecents that file has been activated
        """
        if self._currIsActive:  # statistics already has been updated
            return
        
        self._currIsActive = True

        # Replace the least popular
        if self._currDir not in self._popularDirs:
            if len(self._popularDirs) == self.STATISTICS_SIZE:
                leastPopular = self._dirsByPopularity()[-1]
                del self._popularDirs[leastPopular]
            self._popularDirs[self._currDir] = 0

        self._popularDirs[self._currDir] += self.BONUS_FOR_OPENING

        # Normalization
        pointsSum = sum(self._popularDirs.itervalues())
        multiplier = self.MAX_POINTS_COUNT / pointsSum
        if multiplier < 1:
            for k in self._popularDirs.iterkeys():
                self._popularDirs[k] *= multiplier
        
        core.config()["FileBrowser"]["PopularDirs"] = self._popularDirs
        core.config().flush()
        
        # History update is not scheduled here, because it will be scheduled when workspace changes current file

    def _onRootChanged(self, newCurrDir):
        """FileBrowserDock notifies SmartRecents that user changed current directory
        """
        self._currDir = unicode(newCurrDir, 'utf8')
        self._currIsActive = False
        self._updateRecents()

    def _updateRecents(self):
        """Generate new list of directories, which will be shown in the combo box.
        Emit this list
        """
        history = []
        includedDirs = set()
        if self._currDir is not None:
            history.append((self._currDir, self._currDir, None))
            includedDirs.add(self._currDir)
        # Separator
        if len(history) > 1:
            history.insert(1, None)  # separator
        # Popular directories
        firstPopularDir = True
        popularDirs = self._dirsByPopularity()
        for directory in popularDirs:
            if not directory in includedDirs:
                if firstPopularDir:
                    history.append(None)  # separator
                    firstPopularDir = False
                history.append( (directory, directory, ':mksicons/bookmark.png') )
                includedDirs.add(directory)
            if len(history) >= self.MAX_RECENTS_SIZE:
                break
        
        self._recentsChanged.emit(history)

class SmartHistory(QObject):
    """Class remembers file browser history and manages Back and Forward buttons
    """
    def __init__(self, fileBrowser):
        QObject.__init__(self)
        self._fileBrowser = fileBrowser
        self._currDir = None
        self._currIsActive = False
        self._history = []
        self._historyIndex = -1

        self._aBack = QAction(  QIcon(':mksicons/previous.png'),
                                self.tr("Back"),
                                self)
        self._aBack.setShortcut('Ctrl+Alt+B')
        fileBrowser.titleBar().addAction(self._aBack, 0)
        core.actionModel().addAction("mNavigation/mFileBrowser/aBack", self._aBack)
        self._aBack.triggered.connect(self._onTbBackTriggered)

        self._aForward = QAction(   QIcon(':mksicons/next.png'),
                                    self.tr("Forward"),
                                    self)
        self._aForward.setShortcut('Ctrl+Alt+F')
        fileBrowser.titleBar().addAction(self._aForward, 1)
        core.actionModel().addAction("mNavigation/mFileBrowser/aForward", self._aForward)
        self._aForward.triggered.connect(self._onTbForwardTriggered)
        
        fileBrowser.titleBar().addSeparator(2)
        
        # incoming connections
        fileBrowser.rootChanged.connect(self._onRootChanged)
        fileBrowser.fileActivated.connect(self._onFileActivated)

    def _onRootChanged(self, newCurrDir):
        """FileBrowserDock notifies SmartHistory that root has been changed
        """
        self._currDir = unicode(newCurrDir, 'utf8')
        self._currIsActive = False
        self._updateActions()

    def _onFileActivated(self):
        """FileBrowserDock notifies SmartHistory that file has been activated
        """
        if self._currIsActive:
            return
        self._currIsActive = True
        self._updateHistory()

    def _updateHistory(self):
        """Directory has been activated. Update history
        """
        if  self._history and \
            self._history[self._historyIndex] == self._currDir:
                return # Do nothing, if moved back or forward

        if (self._historyIndex + 1) < len(self._history):  # not on the top of the stack
            # Cut history
            self._history = self._history[:self._historyIndex + 1]
        
        # Append new root to the history
        self._history.append(self._currDir)
        self._historyIndex += 1
        
        self._updateActions()
        
    def _onTbBackTriggered(self):
        """Back action handler
        """
        if not self._currIsActive:
            self._updateHistory()
        
        self._historyIndex -= 1
        self._fileBrowser.setCurrentPath(self._history[self._historyIndex])
    
    def _onTbForwardTriggered(self):
        """Forward action handler
        """
        self._historyIndex += 1
        self._fileBrowser.setCurrentPath(self._history[self._historyIndex])

    def _updateActions(self):
        """Update actions enabled state
        """
        if self._history and self._currDir != self._history[self._historyIndex]:
            self._aBack.setEnabled(True)
            self._aBack.setStatusTip(self._history[-1])
            self._aBack.setToolTip(self._history[-1])
        elif self._history and self._historyIndex > 0:
            self._aBack.setEnabled(True)
            self._aBack.setStatusTip(self._history[self._historyIndex - 1])
            self._aBack.setToolTip(self._history[self._historyIndex - 1])
        else:
            self._aBack.setEnabled(False)
            self._aBack.setStatusTip(self.tr("Back"))
            self._aBack.setToolTip(self.tr("Back"))
        
        if (self._historyIndex + 1) < len(self._history):
            self._aForward.setEnabled(True)
            self._aForward.setStatusTip(self._history[self._historyIndex + 1])
            self._aForward.setToolTip(self._history[self._historyIndex + 1])
        else:
            self._aForward.setEnabled(False)
            self._aForward.setStatusTip(self.tr("Forward"))
            self._aForward.setToolTip(self.tr("Forward"))


class DockFileBrowser(pDockWidget):
    """UI interface of FileBrowser plugin. 
        
    Dock with file system tree, Box, navigation in a file system
    tree, for moving root of tree to currently selected directory and
    up (relatively for current directory)
    """
    rootChanged = pyqtSignal(unicode)
    fileActivated = pyqtSignal()
    
    def __init__(self, parent):
        pDockWidget.__init__(self, parent)
        
        self._filteredModel = None
        self._showPopupAction = None
        self._comboBox = None
        self._completionModel = None
        self._tbCdUp = None
        self._tree = None
        self._comboCount = None
        self._dirsModel = None
        
        self.setObjectName("FileBrowserDock")
        self.setWindowTitle(self.tr( "File Browser" ))
        self.setWindowIcon(QIcon(':/mksicons/open.png'))
        # restrict areas
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        
        self.showAction().setShortcut("F7")
        core.actionModel().addAction("mDocks/aFileBrowser", self.showAction())
        
        self.visibilityChanged.connect(self._onVisibilityChanged)
    
    def __term__(self):
        core.actionModel().removeAction("mDocks/aFileBrowser")

    def _onVisibilityChanged(self, visible):
        """Postnoted widget initialization.
        Create element, when widget appears first timer
        """
        if visible:
            self._initialize()
            self.visibilityChanged.disconnect(self._onVisibilityChanged)
    
    def _initialize(self):
        """Delayed initialization of the widget for quicker start of application
        """
        # central widget
        wdg = QWidget( self )
        self.setWidget( wdg )
        
        # vertical layout
        vertLayout = QVBoxLayout( wdg )
        vertLayout.setMargin( 5 )
        vertLayout.setSpacing( 3 )
        
        # lineedit
        self._comboBox = QComboBox()
        self._comboBox.setAttribute( Qt.WA_MacShowFocusRect, False )
        self._comboBox.setAttribute( Qt.WA_MacSmallSize )
        self._comboBox.setEditable(True)
        self._comboBox.setMinimumContentsLength(1)
        self._comboBox.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self._comboBox.lineEdit().setReadOnly( False )
        self._completionModel = QDirModel(self._comboBox.lineEdit())
        self._completionModel.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self._comboBox.lineEdit().setCompleter(QCompleter(self._completionModel,
                                               self._comboBox.lineEdit()))
        """TODO QDirModel is deprecated but QCompleter does not yet handle
        QFileSystemModel - please update when possible."""
        self._comboCount = 0

        vertLayout.addWidget( self._comboBox )
        
        # hline
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        vertLayout.addWidget( hline )
        
        # dir model
        self._dirsModel = QFileSystemModel( self )
        self._dirsModel.setNameFilterDisables( False )
        self._dirsModel.setFilter( QDir.AllDirs | QDir.AllEntries | QDir.CaseSensitive | QDir.NoDotAndDotDot )
        # self._dirsModel.directoryLoaded.connect(self._setFocusToTree)  TODO don't have this signal in my Qt version
        
        # create proxy model
        self._filteredModel = FileBrowserFilteredModel( self )
        self._filteredModel.setSourceModel( self._dirsModel )
        self.setFilters(core.config()["FileBrowser"]["NegativeFilter"])
        
        # files view
        self._tree = QTreeView()
        self._tree.setAttribute( Qt.WA_MacShowFocusRect, False )
        self._tree.setAttribute( Qt.WA_MacSmallSize )
        self._tree.setContextMenuPolicy( Qt.ActionsContextMenu )
        self._tree.setHeaderHidden( True )
        self._tree.setUniformRowHeights( True )
        vertLayout.addWidget( self._tree )
        
        # assign model to views
        self._tree.setModel( self._filteredModel)

        # jump to current file path action
        self._aJumpToCurrent = QAction(QIcon(':mksicons/text.png'),
                                       self.tr("Jump to current file path"),
                                       self)
        self._aJumpToCurrent.setShortcut('Ctrl+Alt+J')
        self.titleBar().addAction(self._aJumpToCurrent, 0)
        core.actionModel().addAction("mNavigation/mFileBrowser/aJumpToCurrent", self._aJumpToCurrent)
        self._aJumpToCurrent.triggered.connect(self._onTbJumpToCurrentTriggered)
        self.rootChanged.connect(self._updateJumpToCurrentAction)
        core.workspace().currentDocumentChanged.connect(self._updateJumpToCurrentAction)
        
        # add separator
        self.titleBar().addSeparator(1)

        # cd up action
        self._tbCdUp = QToolButton( self._comboBox.lineEdit() )
        self._tbCdUp.setIcon( QIcon( ":/mksicons/go-up.png" ) )
        self._tbCdUp.setCursor( Qt.ArrowCursor )
        self._tbCdUp.installEventFilter( self )
        
        # Show popup action
        self._showPopupAction = QAction(QIcon(':mksicons/filtered.png'), "File browser menu", self)
        self._showPopupAction.setShortcut('Shift+F7')
        core.actionModel().addAction("mNavigation/mFileBrowser/aMenuShow", self._showPopupAction)
        
        if not sys.platform.startswith('win'):
            self._dirsModel.setRootPath( "/" )
        else:
            self._dirsModel.setRootPath('')
        
        # redirirect focus proxy
        self.setFocusProxy( self._tree )
        
        # shortcut accessible only when self._tree has focus
        aUpShortcut = QShortcut( QKeySequence( "BackSpace" ), self._tree )
        aUpShortcut.setContext( Qt.WidgetShortcut )
        
        # incoming connections
        aUpShortcut.activated.connect(self._onTbCdUpClicked)
        showPopupSlot = lambda triggered: self._comboBox.showPopup()
        self._showPopupAction.triggered.connect(showPopupSlot)
        self._tree.activated.connect(self.tv_activated)
        self._tbCdUp.clicked.connect(self._onTbCdUpClicked)
        # reconnected in self.updateComboItems()
        self._comboBox.currentIndexChanged[int].connect(self._onComboItemSelected)
        
        self._smartRecents = SmartRecents(self)
        self._smartHistory = SmartHistory(self)
        
        self.setCurrentPath( os.path.abspath(os.path.curdir) )
    
    def eventFilter(self, object_, event ):
        """ Event filter for mode switch tool button
        Draws icons in the search and path lineEdits
        """
        if  event.type() == QEvent.Paint:
            toolButton = object_
            lineEdit = self._comboBox.lineEdit()
            height = lineEdit.height()
            lineEdit.setContentsMargins( height, 0, 0, 0 )
            
            availableRect = QRect( 0, 0, height, height )
            toolButton.setGeometry( availableRect )
            
            painter = QPainter ( toolButton )
            toolButton.icon().paint( painter, availableRect )
            
            return True

        return pDockWidget.eventFilter( self, object_, event )
    
    def _filteredModelIndexToPath(self, index):
        """Map index to file path
        """
        srcIndex = self._filteredModel.mapToSource( index )
        return unicode(self._dirsModel.filePath( srcIndex ))
    
    def _onTbCdUpClicked(self):
        """Handler of click on Up button.
        """
        current = self._tree.currentIndex()
        if not current.isValid():
            current = self._tree.rootIndex().child(0, 0)
            self._tree.setCurrentIndex(current)
        
        # move tree root up, if necessary
        if current.parent() == self._tree.rootIndex() or \
           current == self._tree.rootIndex():  # need to move root up
            if self._tree.rootIndex().parent().isValid():  # not reached root of the FS tree
                self.setCurrentPath( self._filteredModelIndexToPath(self._tree.rootIndex().parent()))
        
        parentOfCurrent = self._tree.currentIndex().parent()
        if parentOfCurrent != self._tree.rootIndex():  # if not reached top
            self._tree.setCurrentIndex(parentOfCurrent)  # move selection up
    
    def _onTbJumpToCurrentTriggered(self):
        """Jump to directory of current file
        """
        self.setCurrentPath(os.path.abspath(os.curdir))
    
    def _onComboItemSelected(self, index):
        """Handler of item selection in the combo box
        """
        if self._comboBox.count() > self._comboCount:  # It is user input
            path = unicode(self._comboBox.itemText(index), 'utf8')
            if os.path.isdir(path):
                self.setCurrentPath(path)
        else:
            path = unicode(self._comboBox.itemData(index).toString(), 'utf8')
            self.setCurrentPath(path)
        self._tree.setFocus()
    
    def updateComboItems(self, items):
        """Update items in the combo box according to current history
        """
        self._comboBox.currentIndexChanged[int].disconnect()
        self._comboBox.clear()
        for index, item in enumerate(items):
            if item is not None:
                self._comboBox.addItem(item[0])  #  text
                self._comboBox.setItemData(index, item[1])  # path
                if item[2] is not None:
                    self._comboBox.setItemIcon(index, QIcon(item[2]))
            else:
                self._comboBox.insertSeparator(self._comboBox.count())
        self._comboCount = self._comboBox.count()
        self._comboBox.currentIndexChanged[int].connect(self._onComboItemSelected)
        
    def tv_activated(self, idx ):
        """File or directory doubleClicked
        """
        index = self._filteredModel.mapToSource( idx )
        path = unicode(self._dirsModel.filePath( index ))
        
        if  self._dirsModel.isDir( index ) :
            self.setCurrentPath(path)
        else:
            self.fileActivated.emit()
            core.workspace().openFile(path)

    def currentPath(self):
        """Get current path (root of the tree)
        """
        index = self._tree.rootIndex()
        index = self._filteredModel.mapToSource( index )
        return unicode(self._dirsModel.filePath( index ))

    def _setFocusToTree(self):
        """Moves focus and selection to the first item, if nothing focused
        If attempts > 0 and model not yet loaded data, function will call semself 
        automatically later after 10ms for do next attempt to set focus to the first child
        """
        rootIndex = self._tree.rootIndex()
        
        selected =  self._tree.selectionModel().selectedIndexes()
        for index in selected:
            if index.parent() == rootIndex:   # Already having selected item
                return
        
        firstChild = self._filteredModel.index(0, 0, rootIndex)
        if firstChild.isValid():  # There may be no rows, if directory is empty, or not loaded yet
            self._tree.selectionModel().select(firstChild, QItemSelectionModel.SelectCurrent)

    def _updateJumpToCurrentAction(self):
        """Update action enabled state after current file or current directory changed
        """
        self._aJumpToCurrent.setEnabled(os.path.abspath(os.curdir) != self.currentPath())

    def setCurrentPath(self, path):
        """Set current path (root of the tree)
        """
        # get index
        index = self._dirsModel.index(path)
        
        # set current path
        self._filteredModel.invalidate()
        self._tree.setRootIndex( self._filteredModel.mapFromSource( index ) )
        
        self._setFocusToTree()
        
        # set lineedit path
        text = unicode(self._dirsModel.filePath( index ), 'utf8')
        self._comboBox.setToolTip( text )
        
        # notify SmartRecents and own slots
        self.rootChanged.emit(text)

    def currentFilePath(self):
        """Get current file path (selected item)
        """
        index = self._tree.selectionModel().selectedIndexes().value( 0 )
        index = self._filteredModel.mapToSource( index )
        return unicode(self._dirsModel.filePath( index ))

    def setCurrentFilePath(self, filePath):
        """Set current file path (selected item)
        """
        # get index
        index = self._dirsModel.index(filePath)
        index = self._filteredModel.mapFromSource( index )
        self._tree.setCurrentIndex( index )

    def setFilters(self, filters):
        """Set filter wildcards for filter out unneeded files
        """
        filters = filters.split()
        self._filteredModel.setFilters( filters )
