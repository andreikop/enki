"""File Brower plugin. Implements dock with file system tree
"""

import sys
import fnmatch
import re
import os
import os.path

from PyQt4.QtCore import QDir, QModelIndex, QObject, QTimer, Qt
from PyQt4.QtGui import QAction, QDialogButtonBox, QFileDialog, QFrame, QFileSystemModel, \
                        QIcon, QItemSelectionModel, QKeySequence, QLineEdit, QMenu, \
                        QShortcut, QSortFilterProxyModel, QToolButton, QTreeView, QVBoxLayout, QWidget

from PyQt4.fresh import pDockWidget
from PyQt4.fresh import pStringListEditor

import mks.monkeycore

"""
    def fillPluginInfos(self):
        self.pluginInfos.Caption = self.tr( "File Browser" )
        self.pluginInfos.Description = self.tr( "Plugin for browsing file outside the project" )
        self.pluginInfos.Author = "Azevedo Filipe aka Nox P@sNox <pasnox@gmail.com>, Andei aka hlamer <hlamer@tut.by>"
        self.pluginInfos.Type = BasePlugin.iBase
        self.pluginInfos.Name = PLUGIN_NAME
        self.pluginInfos.Version = "1.0.0"
        self.pluginInfos.FirstStartEnabled = True
        self.pluginInfos.HaveSettingsWidget = True
        self.pluginInfos.Pixmap = QPixmap( ":/icons/browser.png" )
"""

class FileBrowser(QObject):
    """File system tree. Allows to open files quickly
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        # create dock
        self.dock = DockFileBrowser(mks.monkeycore.mainWindow())
        self.dock.hide()
        # add dock to dock toolbar entry
        mks.monkeycore.mainWindow().dockToolBar( Qt.LeftToolBarArea ).addDockWidget( self.dock,
                                                                                     self.dock.windowTitle(),
                                                                                     QIcon(':/mksicons/open.png'))
    
    def __del__(self):
        """Uninstall the plugin
        """
        self.dock.deleteLater()

    def settingsWidget(self):
        """Get settings widget of the plugin
        """
        return FileBrowserSettings( self )

class FileBrowserSettings(QWidget):
    """Plugin settings widget
    """
    def __init__(self, plugin): 
        QWidget.__init__(self, plugin)
        self.plugin = plugin
        
        # list editor
        self.editor = pStringListEditor( self, self.tr( "Except Suffixes" ) )
        self.editor.setValues( mks.monkeycore.config()["FileBrowser"]["NegativeFilter"] )
        
        # apply button
        dbbApply = QDialogButtonBox( self )
        dbbApply.addButton( QDialogButtonBox.Apply )
        
        # global layout
        vbox = QVBoxLayout( self )
        vbox.addWidget( self.editor )
        vbox.addWidget( dbbApply )
        
        # connections
        dbbApply.button( QDialogButtonBox.Apply ).clicked.connect(self.applySettings)

    def applySettings(self):
        """Handler of clicking Apply button. Applying settings
        """
        pyStrList = map(str, self.editor.values())
        """FIXME
        mks.monkeycore.config()["FileBrowser"]["NegativeFilter"] = pyStrList
        """
        self.plugin.dock.setFilters(pyStrList)

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

class DockFileBrowser(pDockWidget):
    """UI interface of FileBrowser plugin. 
        
    Dock with file system tree, Box, navigation in a file system
    tree, for moving root of tree to currently selected dirrectory and
    up (relatively for current dirrectory)
    """
    
    def __init__(self, parent):
        pDockWidget.__init__(self, parent)
        self.setObjectName("FileBrowserDock")
        self.setWindowTitle(self.tr( "File Browser" ))
        # restrict areas
        self.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
        
        """ FIXME
        # create menu action for the dock
        pActionsManager.setDefaultShortcut( self.dock.toggleViewAction(), QKeySequence( "F7" ) )
        """
        self.showAction().setShortcut("F7")
        mks.monkeycore.mainWindow().addAction(self.showAction())
        self.visibilityChanged.connect(self._onVisibilityChanged)
    
    def _onVisibilityChanged(self, visible):
        if visible:
            self._initialize()
            self.visibilityChanged.disconnect(self._onVisibilityChanged)
    
    def _initialize(self):
        """Delayed initialization of the widget for quicker start of application
        """
        def createAction(text, icon, slot, index):
            """Create action object and add it to title bar
            """
            actionObject = QAction(self.tr(text), self)
            actionObject.setIcon(QIcon(":/mksicons/%s.png" % icon))
            actionObject.setToolTip( actionObject.text() )
            actionObject.triggered.connect(slot)
            self.titleBar().addAction(actionObject, index )

        createAction("Go Up",                                 "up_arrow",  self.aUp_triggered,        0)
        createAction("Select a root folder",                  "goto",      self.aGoTo_triggered,      1)
        self.titleBar().addSeparator( 2 )
        createAction("Add selected folder to bookmarks",      "add",       self.aAdd_triggered,       3)
        createAction("Remove selected folder from bookmarks", "remove",    self.aRemove_triggered,    4)
        
        # bookmarks menu
        self.mBookmarksMenu = QMenu( self )
        aBookmarks = QAction( self.tr( "Bookmarks..." ), self )
        aBookmarks.setIcon( QIcon(":/mksicons/bookmark.png" ) )
        aBookmarks.setToolTip( aBookmarks.text() )
        toolButton = self.titleBar().addAction( aBookmarks, 5 )
        toolButton.setPopupMode( QToolButton.InstantPopup )
        aBookmarks.setMenu( self.mBookmarksMenu )
        
        # add separator
        self.titleBar().addSeparator( 6 )

        # central widget
        wdg = QWidget( self )
        self.setWidget( wdg )
        
        # vertical layout
        vertLayout = QVBoxLayout( wdg )
        vertLayout.setMargin( 5 )
        vertLayout.setSpacing( 3 )
        
        # lineedit
        self.mLineEdit = QLineEdit()
        self.mLineEdit.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.mLineEdit.setAttribute( Qt.WA_MacSmallSize )
        self.mLineEdit.setReadOnly( True )
        vertLayout.addWidget( self.mLineEdit )
        
        # hline
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        vertLayout.addWidget( hline )
        
        # dir model
        self.mDirsModel = QFileSystemModel( self )
        self.mDirsModel.setNameFilterDisables( False )
        self.mDirsModel.setFilter( QDir.AllDirs | QDir.AllEntries | QDir.CaseSensitive | QDir.NoDotAndDotDot )
        # self.mDirsModel.directoryLoaded.connect(self._setFocusToTree)  TODO don't have this signal in my Qt version
        
        # create proxy model
        self.mFilteredModel = FileBrowserFilteredModel( self )
        self.mFilteredModel.setSourceModel( self.mDirsModel )
        self.setFilters(mks.monkeycore.config()["FileBrowser"]["NegativeFilter"])
        
        # files view
        self.mTree = QTreeView()
        self.mTree.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.mTree.setAttribute( Qt.WA_MacSmallSize )
        self.mTree.setContextMenuPolicy( Qt.ActionsContextMenu )
        self.mTree.setHeaderHidden( True )
        self.mTree.setUniformRowHeights( True )
        vertLayout.addWidget( self.mTree )
        
        # assign model to views
        self.mTree.setModel( self.mFilteredModel)
        
        if not sys.platform.startswith('win'):
            self.mDirsModel.setRootPath( "/" )
        else:
            self.mDirsModel.setRootPath('')
        
        # redirirect focus proxy
        self.setFocusProxy( self.mTree )
        
        # shortcut accessible only when self.mTree has focus
        aUpShortcut = QShortcut( QKeySequence( "BackSpace" ), self.mTree )
        aUpShortcut.setContext( Qt.WidgetShortcut )
        
        # connections
        aUpShortcut.activated.connect(self.aUp_triggered)
        self.mBookmarksMenu.triggered.connect(self.bookmark_triggered)
        self.mTree.activated.connect(self.tv_activated)
        
        self.setCurrentPath( mks.monkeycore.config()["FileBrowser"]["Path"] )
        self.setCurrentFilePath( mks.monkeycore.config()["FileBrowser"]["FilePath"] )
        self.mBookmarks = mks.monkeycore.config()["FileBrowser"]["Bookmarks"]
        self.updateBookMarksMenu()

    def _filteredModelIndexToPath(self, index):
        """Map index to file path
        """
        srcIndex = self.mFilteredModel.mapToSource( index )
        return unicode(self.mDirsModel.filePath( srcIndex ))
    
    def aUp_triggered(self):
        """Handler of click on Up button.
        """
        current = self.mTree.currentIndex()
        if not current.isValid():
            current = self.mTree.rootIndex().child(0, 0)
            self.mTree.setCurrentIndex(current)
        
        # move tree root up, if necessary
        if current.parent() == self.mTree.rootIndex() or \
           current == self.mTree.rootIndex():  # need to move root up
            if self.mTree.rootIndex().parent().isValid():  # not reached root of the FS tree
                self.setCurrentPath( self._filteredModelIndexToPath(self.mTree.rootIndex().parent()))
        
        parentOfCurrent = self.mTree.currentIndex().parent()
        if parentOfCurrent != self.mTree.rootIndex():  # if not reached top
            self.mTree.setCurrentIndex(parentOfCurrent)  # move selection up

    def aGoTo_triggered(self):
        """GoTo (Select root folder) clicked
        """
        action = self.sender()
        path = QFileDialog.getExistingDirectory( self, action.toolTip(), self.currentPath() )
        if path:
            self.setCurrentPath( path )
    
    def aAdd_triggered(self):
        """Add bookmark action triggered
        """
        path = self.currentPath()
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        if  path and not path in self.mBookmarks:
            self.mBookmarks.append(path)
            self.updateBookMarksMenu()

    def aRemove_triggered(self):
        """Remove bookmark triggered
        """
        path = self.currentPath()
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        if  path in self.mBookmarks:
            self.mBookmarks.remove( path )
            self.updateBookMarksMenu()

    def bookmark_triggered(self, action ):
        """Bookmark triggered, go to marked folder
        """
        self.setCurrentPath( action.data().toString() )

    def tv_activated(self, idx ):
        """File or dirrectory doubleClicked
        """
        index = self.mFilteredModel.mapToSource( idx )
        
        if  self.mDirsModel.isDir( index ) :
            self.setCurrentPath( unicode(self.mDirsModel.filePath( index )) )
        else:
            mks.monkeycore.workspace().openFile( unicode(self.mDirsModel.filePath( index )))

    def currentPath(self):
        """Get current path (root of the tree)
        """
        index = self.mTree.rootIndex()
        index = self.mFilteredModel.mapToSource( index )
        return unicode(self.mDirsModel.filePath( index ))

    def _setFocusToTree(self, allowTimer = False):
        """Moves focus and selection to the first item, if nothing focused
        """
        rootIndex = self.mTree.rootIndex()
        
        selected =  self.mTree.selectionModel().selectedIndexes()
        for index in selected:
            if index.parent() == rootIndex:   # Already having selected item
                return
        
        firstChild = self.mFilteredModel.index(0, 0, rootIndex)
        if firstChild.isValid():  # There may be no rows, if directory is empty, or not loaded yet
            self.mTree.selectionModel().select(firstChild, QItemSelectionModel.SelectCurrent)
        else:
            """TODO QFileSystemModel version supports directoryLoaded() signal only the from version 4.7.0.
            When this signal is supported by Ubuntu version of PyQt4, remove this timer and replace it with signal
            from the QFileSystemModel
            """
            if allowTimer:
                QTimer.singleShot(100, self._setFocusToTree)

    def setCurrentPath(self, path):
        """Set current path (root of the tree)
        """
        # get index
        index = self.mDirsModel.index(path)
        
        # set current path
        self.mFilteredModel.invalidate()
        self.mTree.setRootIndex( self.mFilteredModel.mapFromSource( index ) )
        
        self._setFocusToTree(True)
        
        # set lineedit path
        self.mLineEdit.setText( unicode(self.mDirsModel.filePath( index )) )
        self.mLineEdit.setToolTip( self.mLineEdit.text() )

    def currentFilePath(self):
        """Get current file path (selected item)
        """
        index = self.mTree.selectionModel().selectedIndexes().value( 0 )
        index = self.mFilteredModel.mapToSource( index )
        return unicode(self.mDirsModel.filePath( index ))

    def setCurrentFilePath(self, filePath):
        """Set current file path (selected item)
        """
        # get index
        index = self.mDirsModel.index(filePath)
        index = self.mFilteredModel.mapFromSource( index )
        self.mTree.setCurrentIndex( index )

    def setFilters(self, filters ):
        """Set filter wildcards for filter out unneeded files
        """
        self.mFilteredModel.setFilters( filters )

    def updateBookMarksMenu(self):
        """Create new Bookmarks menu
        """
        self.mBookmarksMenu.clear()
        
        for path in self.mBookmarks:
            action = self.mBookmarksMenu.addAction(path)
            action.setToolTip( path )
            action.setStatusTip( path )
            action.setData( path )
