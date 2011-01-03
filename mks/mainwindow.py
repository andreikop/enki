"""
mainwindow --- Main window of the UI. Fills main menu.
======================================================


Module contains :class:`mks.mainwindow.MainWindow` implementation
"""

from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QString
from PyQt4.QtCore import QSize
from PyQt4.QtGui import qApp
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QDockWidget

from PyQt4.fresh import pMainWindow, pActionsNodeModel

import mks.monkeystudio
import mks.monkeycore

class MainWindow(pMainWindow):
    """
    Main UI window
    
    Class creates window elements, fills main menu with items.
    
    If you need to connect to some existing menu item *triggered()* signal - check action name 
    in the class constructor, than use: ::
        
        mks.monkeycore.menuBar().action( "mFile/aOpen" ).triggered.connect(self.myCoolMethod)
    
    MainWindow instance accessible as ::
    
        mks.monkeycore.mainwindow()
    
    Created by monkeycore
    """
    
    """TODO
    aboutToClose = pyqtSignal()
    urlsDropped = pyqtSignal()
    """

    def __init__(self):
        pMainWindow.__init__(self)
        self.setUnifiedTitleAndToolBarOnMac( True )
        self.setIconSize( QSize( 16, 16 ) )
        self.setAcceptDrops( True )
        
        self.setCorner( Qt.TopLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.TopRightCorner, Qt.RightDockWidgetArea )
        self.setCorner( Qt.BottomLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.BottomRightCorner, Qt.RightDockWidgetArea )
        
        self.setWindowTitle( "%s v%s" % (mks.config.PACKAGE_NAME, mks.config.PACKAGE_VERSION ) )
        self.setWindowIcon( QIcon(':/mksicons/monkey2.png') )

        # init menubar
        # create menubar menus and actions
        mb = self.menuBar()
        self.mActionsModel = pActionsNodeModel( self )
        self.menuBar().setModel( self.mActionsModel )

        
        # FIXME commented for new fresh
        #mb.setDefaultShortcutContext( Qt.ApplicationShortcut )
        """TODO
        mb.action( "aNew", self.tr( "&New..." ), QIcon(":/mksicons/new.png" ),"Ctrl+N", self.tr( "Create a new file" ) )
        mb.action( "aNewTextEditor", self.tr( "&New Text File..." ), QIcon(":/mksicons/new.png" ), '', self.tr( "Quickly create a new text based file" ) )
        """
        """TODO
        mb.menu( "mRecents", self.tr( "&Recents" ), QIcon(":/mksicons/recents.png" ) )
        mb.action( "mRecents/aClear", self.tr( "&Clear" ), QIcon(":/mksicons/clear.png" ), '', self.tr( "Clear the recents files list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.action( "aSeparator1" )
        mb.menu( "mSession", self.tr( "Session" ), QIcon(":/mksicons/session.png" ) )
        mb.action( "mSession/aSave", self.tr( "Save" ), QIcon(":/mksicons/save.png" ), '', self.tr( "Save the current session files list" ) )
        mb.action( "mSession/aRestore", self.tr( "Restore" ), QIcon(":/mksicons/restore.png" ), '', self.tr( "Restore the current session files list" ) )
        mb.action( "aSeparator2" )
        """
        """TODO
        mb.action( "mClose/aAll", self.tr( "Close &All" ), QIcon(":/mksicons/closeall.png" ), '', self.tr( "Close all files" ) ).setEnabled( False )
        mb.action( "aSeparator3" )
        mb.action( "aReload", self.tr( "Reload" ), QIcon(":/mksicons/reload.png" ), '', self.tr( "Reload the current file asking user confirmation if needed" ) ).setEnabled( False )
        mb.action( "aSaveAsBackup", self.tr( "Save As &Backup" ), QIcon(":/mksicons/backup.png" ), '', self.tr( "Save a backup of the current file" ) ).setEnabled( False )
        mb.action( "aSeparator4" )
        mb.action( "aQuickPrint", self.tr( "Quic&k Print" ), QIcon(":/mksicons/quickprint.png" ), '', self.tr( "Quick print the current file" ) ).setEnabled( False )
        mb.action( "aPrint", self.tr( "&Print..." ), QIcon(":/mksicons/print.png" ), "Ctrl+P", self.tr( "Print the current file" ) ).setEnabled( False )
        mb.action( "aSeparator5" )
        """
        """TODO
        mb.action( "aSettings", self.tr( "Settings..." ), QIcon( ":/mksicons/settings.png" ), "", self.tr( "Edit the application settings" ) )
        mb.action( "aShortcutsEditor", self.tr( "Shortcuts Editor..." ), QIcon( ":/mksicons/shortcuts.png" ), "Ctrl+Shift+E", self.tr( "Edit the application shortcuts" ) )
        mb.action( "aTranslations", self.tr( "Translations..." ), QIcon( ":/mksicons/translations.png" ), "Ctrl+T", self.tr( "Change the application translations files" ) )
        mb.action( "aSeparator1" )
        mb.action( "aSeparator3" )
        """
        """TODO
        mb.menu( "mAllCommands", self.tr( "&All Commands" ), QIcon( ":/mksicons/commands.png" ) )
        
        mb.action( "aSeparator5" )
        mb.action( "aExpandAbbreviation", self.tr( "Expand Abbreviation" ), QIcon( ":/mksicons/abbreviation.png" ), "Ctrl+E", self.tr( "Expand Abbreviation" ) ).setEnabled( False )
        mb.action( "aPrepareAPIs", self.tr( "Prepare APIs" ), QIcon( ":/mksicons/prepareapis.png" ), "Ctrl+Alt+P", self.tr( "Prepare the APIs files for auto completion / calltips" ) )
        """
        """TODO
        mb.menu( "mStyle", self.tr( "&Style" ), QIcon( ":/mksicons/style.png" ) )
        """
        """TODO
        mb.menu( "mProject", self.tr( "Project" ) )
        mb.beginGroup( "mProject" )
        
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atNew ) )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atOpen ) )
        mb.action( "aSeparator1" )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atClose ) )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atCloseAll ) )
        mb.action( "aSeparator2" )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atEdit ) )
        mb.action( "aSeparator3" )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atAddFiles ) )
        mb.addAction( '', mks.monkeycore.projectsManager().action( XUPProjectManager.atRemoveFiles ) )
        mb.action( "aSeparator4" )
        
        mb.menu( "mRecents", self.tr( "&Recents" ), QIcon( ":/mksicons/recents.png" ) )
        mb.action( "mRecents/aClear", self.tr( "&Clear" ), QIcon( ":/mksicons/clear.png" ), '', self.tr( "Clear the recents projects list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mBuilder", self.tr( "Build" ) ).menuAction().setEnabled( False )
        mb.menu( "mBuilder" ).menuAction().setVisible( False )
        
        mb.beginGroup( "mBuilder" )
        mb.menu( "mBuild", self.tr( "&Build" ), QIcon( ":/mksicons/build.png" ) )
        mb.menu( "mRebuild", self.tr( "&Rebuild" ), QIcon( ":/mksicons/rebuild.png" ) )
        mb.menu( "mClean", self.tr( "&Clean" ), QIcon( ":/mksicons/clean.png" ) )
        mb.menu( "mExecute", self.tr( "&Execute" ), QIcon( ":/mksicons/execute.png" ) )
        mb.menu( "mUserCommands", self.tr( "&User Commands" ), QIcon( ":/mksicons/misc.png" ) )
        mb.action( "aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mDebugger", self.tr( "Debugger" ) ).menuAction().setEnabled( False )
        mb.menu( "mDebugger" ).menuAction().setVisible( False )
        mb.menu( "mInterpreter", self.tr( "Interpreter" ) ).menuAction().setEnabled( False )
        mb.menu( "mInterpreter" ).menuAction().setVisible( False )
        mb.menu( "mPlugins", self.tr( "Plugins" ) )
        
        mb.beginGroup( "mPlugins" )
        mb.action( "aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mWindow", self.tr( "Window" ) )

        mb.beginGroup( "mWindow" )
        mb.action( "aCascase", self.tr( "&Cascade" ), QIcon( "" ), '', self.tr( "Cascade" ) )
        mb.action( "aTile", self.tr( "&Tile" ), QIcon( "" ), '', self.tr( "Tile" ) )
        mb.action( "aMinimize", self.tr( "&Minimize" ), QIcon( "" ), '', self.tr( "Minimize" ) )
        mb.action( "aRestore", self.tr( "&Restore" ), QIcon( "" ), '', self.tr( "Restore normal size" ) )
        mb.endGroup()
        
        """
        """TODO
        mb.action( "aAbout", self.tr( "&About..." ), QIcon( ":/mksicons/monkey2.png" ), '', self.tr( "About application..." ) )
        """
        """TODO
        # create action for styles
        agStyles = pStylesActionGroup( self.tr( "Use %1 style" ), mb.menu( "mView/mStyle" ) )
        agStyles.setCurrentStyle( mks.monkeycore.settings().value( "MainWindow/Style" ).toString() )
        mb.menu( "mView/mStyle" ).addActions( agStyles.actions() )
        
        # create plugins actions
        mks.monkeycore.pluginsManager().menuHandler().setMenu( mb.menu( "mPlugins" ) )
        
        # init recents manager
        mks.monkeycore.recentsManager()
        # init toolbar
        self.initToolBar()
        """
        
        # Default exclusive settings for the tool bars
        self.dockToolBar( Qt.LeftToolBarArea ).setExclusive(False)
        self.dockToolBar( Qt.RightToolBarArea ).setExclusive(False)
        
        self._createdMenuPathes = []
        self._createdActions = []
        
        def menu(path, name, icon):
            menuObject = self.menuBar().addMenu(path)
            menuObject.setText(name)
            if icon:
                menuObject.setIcon(QIcon(':/mksicons/' + icon))
            self._createdMenuPathes.append(path)
            
        def action(path, name, icon, shortcut, tooltip, enabled):
            if icon:  # has icon
                actObject = self.menuBar().addAction(path, name, QIcon(':/mksicons/' + icon))
            else:
                actObject = self.menuBar().addAction(path, name)
            if shortcut:
                actObject.setShortcut(shortcut)
            actObject.setToolTip(tooltip)
            actObject.setEnabled(enabled)
            self._createdActions.append(actObject)
        
        
        # Menu or action path                   Name                                Icon            Shortcut        Hint                                        Action enabled
        menu  ("mFile",                               self.tr("File"                   ), ""            )
        action("mFile/aOpen",                         self.tr( "&Open..."              ), "open.png",     "Ctrl+O" ,      self.tr( "Open a file"            ), True )
        menu  ("mFile/mSave",                         self.tr("&Save"                  ), "save.png"    ),
        action("mFile/mSave/aCurrent",                self.tr( "&Save"                 ), "save.png" ,    "Ctrl+S" ,      self.tr( "Save the current file"  ), False)
        action("mFile/mSave/aAll",                    self.tr( "Save &All"             ), "saveall.png",  'Shift+Ctrl+S', self.tr( "Save all files"         ), False)
        menu  ("mFile/mClose",                        self.tr( "&Close"                ), "close.png"   ),
        action("mFile/mClose/aCurrent",               self.tr( "&Close"                ), "close.png",    "",             self.tr( "Close the current file" ), False)
        action("mFile/aQuit",                         self.tr( "&Quit"                 ), "quit.png",     "Ctrl+Q",       self.tr( "Quit the application"   ), True )
        
        menu  ("mEdit",                               self.tr( "Edit"                  ), ""            )
        menu  ("mEdit/mSearchReplace",                self.tr( "&Search && Replace"    ), ""            )
        
        menu  ("mView",                               self.tr( "View"                  ), ""            )
        action("mView/aNext",                         self.tr( "&Next file" ),            "next.png",     "Alt+Right",    self.tr( "Active the next tab"    ), False)
        action("mView/aPrevious",                     self.tr( "&Previous file" ),        "previous.png", "Alt+Left",     self.tr( "Active the previous tab"), False)
        action("mView/aFocusCurrentDocument",         self.tr( "Focus to editor" ),       "text.png",     "Ctrl+Return",  self.tr( "Focus current document" ), False)
        
        menu  ("mDocks",                               self.tr( "Docks"                  ), ""            )
        
        menu  ("mHelp",                               self.tr( "Help"                  ), ""            )
        action("mHelp/aAboutQt",                      self.tr( "About &Qt..." ),          "qt.png",       "",             self.tr( "About Qt..."            ), True )
        
        self.menuBar().action( "mFile/aQuit" ).triggered.connect(self.close)
        self.menuBar().action( "mHelp/aAboutQt" ).triggered.connect(qApp.aboutQt)
        # docks
        self.menuBar().menu( "mDocks" ).aboutToShow.connect(self._menu_Docks_aboutToShow)
        
        """TODO
        # init message toolbar
        messageTb =  mks.monkeycore.messageManager()
        messageTb.setObjectName( "pQueuedMessageToolBar" )
        messageTb.setVisible( False )
        messageTb.setDefaultPixmap( QIcon(":/mksicons/messages_infos.png") )
        pMonkeyStudio.setMacSmallSize( messageTb, true, true )
        self.centralWidget().layout().setMenuBar( messageTb )
        # init projects manager
        dockToolBar( Qt.LeftToolBarArea ).addDock( mks.monkeycore.projectsManager(), mks.monkeycore.projectsManager().windowTitle(), QIcon( ":/mksicons/project.png" ) )
        # init multitoolbar
        mks.monkeycore.workspace().initMultiToolBar( mks.monkeycore.multiToolBar().toolBar( Workspace.defaultContext() ) )
        mks.monkeycore.workspace().initMultiToolBar( mks.monkeycore.multiToolBar().toolBar( "Coding" ) )
        # init status bar
        setStatusBar( mks.monkeycore.statusBar() )
        # init connection
        self.initConnections()
        self.menuBar().action( "mFile/aNew" ).triggered.connect(mks.monkeycore.workspace().fileNew_triggered)
        self.menuBar().action( "mFile/aNewTextEditor" ).triggered.connect(mks.monkeycore.workspace().createNewTextEditor)
        mks.monkeycore.recentsManager().openFileRequested.connect(mks.monkeycore.fileManager().openFile)
        self.menuBar().action( "mFile/mSession/aSave" ).triggered.connect(mks.monkeycore.workspace().fileSessionSave_triggered)
        self.menuBar().action( "mFile/mSession/aRestore" ).triggered.connect(mks.monkeycore.workspace().fileSessionRestore_triggered)
        self.menuBar().action( "mFile/mClose/aAll" ).triggered.connect(mks.monkeycore.workspace().fileCloseAll_triggered)
        self.menuBar().action( "mFile/aReload" ).triggered.connect(mks.monkeycore.workspace().fileReload_triggered)
        self.menuBar().action( "mFile/aSaveAsBackup" ).triggered.connect(mks.monkeycore.workspace().fileSaveAsBackup_triggered)
        self.menuBar().action( "mFile/aQuickPrint" ).triggered.connect(mks.monkeycore.workspace().fileQuickPrint_triggered)
        self.menuBar().action( "mFile/aPrint" ).triggered.connect(mks.monkeycore.workspace().filePrint_triggered)
        # edit connection
        self.menuBar().action( "mEdit/aSettings" ).triggered.connect(mks.monkeycore.workspace().editSettings_triggered)
        self.menuBar().action( "mEdit/aShortcutsEditor" ).triggered.connect(mks.monkeycore.actionsManager().editActionsShortcuts)
        self.menuBar().action( "mEdit/aTranslations" ).triggered.connect(mks.monkeycore.workspace().editTranslations_triggered)
        self.menuBar().action( "mEdit/mSearchReplace/aSearchFile" ).triggered.connect(mks.monkeycore.workspace().editSearch_triggered)
        #menuBar().action( "mEdit/aSearchPrevious" ).triggered.connect(mks.monkeycore.workspace().editSearchPrevious_triggered)
        #menuBar().action( "mEdit/aSearchNext" ).triggered.connect(mks.monkeycore.workspace().editSearchNext_triggered)
        self.menuBar().action( "mEdit/aExpandAbbreviation" ).triggered.connect(mks.monkeycore.workspace().editExpandAbbreviation_triggered)
        self.menuBar().action( "mEdit/aPrepareAPIs" ).triggered.connect(mks.monkeycore.workspace().editPrepareAPIs_triggered)
        # view connection
        agStyles.styleSelected.connect(self.changeStyle)

        # project connection
        mks.monkeycore.recentsManager().openProjectRequested.connect(mks.monkeycore.projectsManager().openProject)
        mks.monkeycore.projectsManager().fileDoubleClicked.connect(mks.monkeycore.workspace().openFile)
        # builder debugger interpreter menu
        self.menuBar().menu( "mBuilder" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        self.menuBar().menu( "mDebugger" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        self.menuBar().menu( "mInterpreter" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
        # plugins menu
        # window menu
        self.menuBar().action( "mWindow/aTile" ).triggered.connect(mks.monkeycore.workspace().tile)
        self.menuBar().action( "mWindow/aCascase" ).triggered.connect(mks.monkeycore.workspace().cascade)
        self.menuBar().action( "mWindow/aMinimize" ).triggered.connect(mks.monkeycore.workspace().minimize)
        self.menuBar().action( "mWindow/aRestore" ).triggered.connect(mks.monkeycore.workspace().restore)
        # help menu
        self.menuBar().action( "mHelp/aAbout" ).triggered.connect(mks.monkeycore.workspace().helpAboutApplication_triggered)
        """
    def __del__(self):
        for act in self._createdActions:
            self.menuBar().removeAction(act)
        for menuPath in self._createdMenuPathes:
            self.menuBar().removeMenu(menuPath)
        
        self.menuBar().setModel( None )
    
    def actionsModel(self):
        """Get actions model.
        Model used for set default shortcuts for the actions
        """
        return self.mActionsModel
    
    def _menu_Docks_aboutToShow(self):
        # get menu
        menu = self.menuBar().menu( "mDocks" )
        
        # add actions
        for dw in self.findChildren(QDockWidget):
            action = dw.toggleViewAction()
            
            action.setIcon( dw.windowIcon() )
            menu.addAction( action )
            self.menuBar().addAction( "mDocks", action )
    
"""TODO
    def dragEnterEvent( self, event ):
        # if correct mime and same tabbar
        if  event.mimeData().hasUrls() :
            # accept drag
            event.acceptProposedAction()
        
        # default event
        pMainWindow.dragEnterEvent( self, event )
    
    def dropEvent( self, event ):
        if  event.mimeData().hasUrls() :
            self.urlsDropped.emit( event.mimeData().urls () )
        
        # default event
        pMainWindow.dropEvent( self, event )
    
    
    def closeEvent( self, event ):
        # inform that we close mainwindow
        self.aboutToClose.emit()
        
        # save session if needed
        if  mks.monkeystudio.saveSessionOnClose() :
            mks.monkeycore.workspace().fileSessionSave_triggered()
        
        # request close all documents
        if  not mks.monkeycore.workspace().closeAllDocuments() :
            event.ignore()
            return
        
        
        # force to close all projects
        mks.monkeycore.projectsManager().action( XUPProjectManager.atCloseAll ).trigger()
        pMainWindow.closeEvent( self, event )
    
    
    def createPopupMenu(self):
        # create default menu
        menu = QMenu( self );
        # add exclusive action of pDockToolBar
        tbs = self.findChildren(pDockToolBar)
        
        for tb in tbs:
            if  tb.parent() != self :
                continue
            
            menu.addAction( tb.toggleExclusiveAction() )
        
        return menu

    def initToolBar(self):
        # recents
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().menu( "mFile/mRecents" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().menu( "mFile/mSession" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().menu( "mProject/mRecents" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # settings
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mEdit/aSettings" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mEdit/aShortcutsEditor" ) )
        # file action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mFile/aNew" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mFile/aNewTextEditor" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mFile/aOpen" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addActions( self.menuBar().menu( "mFile/mSave" ).actions() )
        self.dockToolBar( Qt.TopToolBarArea ).addActions( self.menuBar().menu( "mFile/mClose" ).actions() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mFile/aQuickPrint" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # help action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( self.menuBar().action( "mHelp/aAbout" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # console action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( mks.monkeycore.consoleManager().stopAction() )

def updateMenuVisibility( self, menu ):
        menuAction = menu.menuAction()
        
        menuVisible = False

        for action in menu.actions():
            if  action.isSeparator() :
                continue
            
            subMenu = action.menu()

            if  subMenu :
                if  self.updateMenuVisibility( subMenu ) :
                    menuVisible = True
            else:
                menuVisible = True
        
        menuAction.setVisible( menuVisible )
        menuAction.setEnabled( menuVisible )
        
        return menuVisible
    
    def menu_CustomAction_aboutToShow(self):
        menus = []

        if  sender() :
            menus.append(sender())
        else:
            menus.append[self.menuBar().menu( "mBuilder" )]
            menus.append[self.menuBar().menu( "mDebugger")]
            menus.append[self.menuBar().menu( "mInterpreter")]

        for m in menus:
            self.updateMenuVisibility( m )
    
    def changeStyle( style ):
        qApp.setStyle( style )
        qApp.setPalette( qApp.style().standardPalette() )
        self.settings().setValue( "MainWindow/Style", style )
"""