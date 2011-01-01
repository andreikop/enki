"""File Brower plugin. Implements dock with file system tree
"""

import sys
import fnmatch
import re
import os
import os.path

from PyQt4.QtCore import QDir, QModelIndex, QObject, Qt
from PyQt4.QtGui import QAction, QDialogButtonBox, QFileDialog, QFrame, QFileSystemModel, QIcon, QKeySequence, QLineEdit, QMenu, \
                                         QShortcut, QSortFilterProxyModel, QToolButton, QTreeView, QVBoxLayout, QWidget

from PyQt4.fresh import pDockWidget
""" FIXME
from PyQt4.fresh import pStringListEditor
"""

import mks.monkeycore
import mks.settings

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

class FileBrowser(QObject):  # TODO (Plugin) ?
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        # create dock
        self.dock = pDockFileBrowser(mks.monkeycore.mainWindow())
        # add dock to dock toolbar entry
        mks.monkeycore.mainWindow().dockToolBar( Qt.LeftToolBarArea ).addDockWidget( self.dock,
                                                                                     self.dock.windowTitle(),
                                                                                     QIcon(':/mksicons/open.png'))
        """ FIXME
        # create menu action for the dock
        pActionsManager.setDefaultShortcut( self.dock.toggleViewAction(), QKeySequence( "F7" ) )
        """
    
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
        self.editor.setValues( mks.settings.value("FileBrowser/NegativeFilter") )
        
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
        mks.settings.setValue( "NegativeFilter", pyStrList)
        """
        self.plugin.dock.setFilters(pyStrList);

class FileBrowserFilteredModel(QSortFilterProxyModel):
    def __init__(self, parent):
        QSortFilterProxyModel.__init__(self, parent)
    
    def setFilters(self, filters):
        # FIXME duplicating code, copypaste from search plugin
        regExPatterns = map(fnmatch.translate, filters)
        compositeRegExpPattern = '(' + ')|('.join(regExPatterns) + ')'
        self.filterRegExp = re.compile(compositeRegExpPattern)
        
        self.invalidateFilter()

    def columnCount(self, parent = QModelIndex()):
        return 1
    
    def hasChildren(self, parent = QModelIndex()):
        return self.sourceModel().hasChildren( self.mapToSource( parent ) )
        
    def filterAcceptsRow(self, source_row, source_parent):
        if  source_parent == QModelIndex():
            return True
        return not self.filterRegExp.match(source_parent.child( source_row, 0 ).data().toString() )

class pDockFileBrowser(pDockWidget):
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
        
        # actions. Table (Text, icon name, slot, button index on tool bar)
        # will be created after all widgets created
        actions = (("Go Up",                                                       "up_arrow",  self.aUp_triggered,           0),
                        ("Select a root folder",                             "goto",         self.aGoTo_triggered,        1),
                        ("Add selected folder to bookmarks",         "add",          self.aAdd_triggered,          2),
                        ("Remove selected folder from bookmarks", "remove",    self.aRemove_triggered,    3))
        
        
        for action in actions:
            actionObject = QAction(self.tr(action[0]), self)
            actionObject.setIcon(QIcon(":/mksicons/%s.png" % action[1]))
            actionObject.setToolTip( actionObject.text() )
            actionObject.triggered.connect(action[2])
            self.titleBar().addAction(actionObject, action[3] )
            # fixme self.mTree.addAction(actionObject)
        
        # add separator between actions
        self.titleBar().addSeparator( 2 )
        
        # bookmarks menu
        self.mBookmarksMenu = QMenu( self )
        aBookmarks = QAction( self.tr( "Bookmarks..." ), self )
        aBookmarks.setIcon( QIcon(":/mksicons/bookmark.png" ) )
        aBookmarks.setToolTip( aBookmarks.text() )
        tb = self.titleBar().addAction( aBookmarks, 5 )
        tb.setPopupMode( QToolButton.InstantPopup )
        aBookmarks.setMenu( self.mBookmarksMenu )
        
        # add separator
        self.titleBar().addSeparator( 6 )

        # central widget
        wdg = QWidget( self )
        self.setWidget( wdg )
        
        # vertical layout
        vl = QVBoxLayout( wdg )
        vl.setMargin( 5 )
        vl.setSpacing( 3 )
        
        # lineedit
        self.mLineEdit = QLineEdit()
        self.mLineEdit.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.mLineEdit.setAttribute( Qt.WA_MacSmallSize )
        self.mLineEdit.setReadOnly( True )
        vl.addWidget( self.mLineEdit )
        
        # hline
        hline = QFrame( self )
        hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )
        vl.addWidget( hline )
        
        # dir model
        self.mDirsModel = QFileSystemModel( self )
        self.mDirsModel.setNameFilterDisables( False )
        self.mDirsModel.setFilter( QDir.AllDirs | QDir.AllEntries | QDir.CaseSensitive | QDir.NoDotAndDotDot )
        
        # create proxy model
        self.mFilteredModel = FileBrowserFilteredModel( self )
        self.mFilteredModel.setSourceModel( self.mDirsModel )
        self.setFilters(mks.settings.value("FileBrowser/NegativeFilter"))
        
        # files view
        self.mTree = QTreeView()
        self.mTree.setAttribute( Qt.WA_MacShowFocusRect, False )
        self.mTree.setAttribute( Qt.WA_MacSmallSize )
        self.mTree.setContextMenuPolicy( Qt.ActionsContextMenu )
        self.mTree.setHeaderHidden( True )
        self.mTree.setUniformRowHeights( True )
        vl.addWidget( self.mTree )
        
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
        self.mTree.doubleClicked.connect(self.tv_doubleClicked)
        
        self.setCurrentPath( mks.settings.value("FileBrowser/Path") )
        self.setCurrentFilePath( mks.settings.value("FileBrowser/FilePath") )
        self.mBookmarks = mks.settings.value("FileBrowser/Bookmarks")
        self.updateBookMarksMenu()

    def __del__(self):    
        pass
        """FIXME
        mks.settings.setValue("FileBrowser/Path", self.currentPath())
        mks.settings.setValue("FileBrowser/FilePath", self.currentFilePath())
        mks.settings.setValue("FileBrowser/Bookmarks", self.mBookmarks)
        """

    def aUp_triggered(self):
        """Handler of click on Up button.
        """
        # cd up only if not the root index
        index = self.mTree.rootIndex()
        
        if  not index.isValid() :
            return
        
        index = index.parent()
        index = self.mFilteredModel.mapToSource( index )
        path = unicode(self.mDirsModel.filePath( index ))
        
        if not sys.platform.startswith('win'):
            if  not path:
                return
        
        self.setCurrentPath( path )

    def aGoTo_triggered(self):
        action = self.sender()
        path = QFileDialog.getExistingDirectory( self, action.toolTip(), self.currentPath() )
        if path:
            self.setCurrentPath( path )
    
    def aAdd_triggered(self):
        path = self.currentPath()
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        if  path and not path in self.mBookmarks:
            self.mBookmarks.append(path)
            self.updateBookMarksMenu()

    def aRemove_triggered(self):
        path = self.currentPath()
        if not os.path.isdir(path):
            path = os.path.dirname(path)
        
        if  path in self.mBookmarks:
            self.mBookmarks.remove( path )
            self.updateBookMarksMenu()

    def bookmark_triggered(self, action ):
        self.setCurrentPath( action.data().toString() )

    def tv_activated(self, idx ):
        index = self.mFilteredModel.mapToSource( idx )
        
        if  self.mDirsModel.isDir( index ) :
            self.setCurrentPath( unicode(self.mDirsModel.filePath( index )) )
        else:
            mks.monkeycore.workspace().openFile( unicode(self.mDirsModel.filePath( index )))

    def tv_doubleClicked(self, idx ):
        """Handler of click on item in the tree
        """
        index = self.mFilteredModel.mapToSource( idx )
        
        if  not self.mDirsModel.isDir( index ) :
            mks.monkeycore.workspace().openFile( unicode(self.mDirsModel.filePath( index )))

    def currentPath(self):
        """Get current path (root of the tree)
        """
        index = self.mTree.rootIndex()
        index = self.mFilteredModel.mapToSource( index )
        return unicode(self.mDirsModel.filePath( index ))

    def setCurrentPath(self, s ):
        """Set current path (root of the tree)
        """
        # get index
        index = self.mDirsModel.index( s )
        # set current path
        self.mFilteredModel.invalidate()
        self.mTree.setRootIndex( self.mFilteredModel.mapFromSource( index ) )
        # set lineedit path
        self.mLineEdit.setText( unicode(self.mDirsModel.filePath( index )) )
        self.mLineEdit.setToolTip( self.mLineEdit.text() )

    def currentFilePath(self):
        """Get current file path (selected item)
        """
        index = self.mTree.selectionModel().selectedIndexes().value( 0 )
        index = self.mFilteredModel.mapToSource( index )
        return unicode(self.mDirsModel.filePath( index ))

    def setCurrentFilePath(self, s ):
        """Set current file path (selected item)
        """
        # get index
        index = self.mDirsModel.index( s )
        index = self.mFilteredModel.mapFromSource( index )
        self.mTree.setCurrentIndex( index )

    def setFilters(self, filters ):
        """Set filter wildcards for filtering out unneeded files
        """
        self.mFilteredModel.setFilters( filters ) # fixme remove this and prev?

    def updateBookMarksMenu(self):
        self.mBookmarksMenu.clear()
        
        for path in self.mBookmarks:
            action = self.mBookmarksMenu.addAction(path)
            action.setToolTip( path )
            action.setStatusTip( path )
            action.setData( path )
