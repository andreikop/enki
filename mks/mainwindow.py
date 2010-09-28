from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QString
from PyQt4.QtCore import QSize
from PyQt4.QtGui import qApp
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QDockWidget

from PyQt4.fresh import pMainWindow

import mks.monkeycore


class MainWindow(pMainWindow):
    
    aboutToClose = pyqtSignal()
    urlsDropped = pyqtSignal()
    
    def __init__(self):
        pMainWindow.__init__(self)
        """TODO
        self.setUnifiedTitleAndToolBarOnMac( True )
        self.setIconSize( QSize( 16, 16 ) )
        self.setAcceptDrops( True )
        
        self.setCorner( Qt.TopLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.TopRightCorner, Qt.RightDockWidgetArea )
        self.setCorner( Qt.BottomLeftCorner, Qt.LeftDockWidgetArea )
        self.setCorner( Qt.BottomRightCorner, Qt.RightDockWidgetArea )
        """
    
    def initGui(self):
        # init menubar
        #self.initMenuBar()
        """TODO
        # init recents manager
        mks.monkeycore.recentsManager()
        # init toolbar
        self.initToolBar()
        # init workspace
        self.setCentralWidget( mks.mks.monkeycore.workspace() )
        # init message toolbar
        messageTb =  mks.mks.monkeycore.messageManager()
        messageTb.setObjectName( "pQueuedMessageToolBar" )
        messageTb.setVisible( False )
        messageTb.setDefaultPixmap( mks.iconmanager.pixmap( "messages_infos.png", ":/messages" ) )
        pMonkeyStudio.setMacSmallSize( messageTb, true, true )
        self.centralWidget().layout().setMenuBar( messageTb )
        # init projects manager
        dockToolBar( Qt.LeftToolBarArea ).addDock( mks.monkeycore.projectsManager(), mks.monkeycore.projectsManager().windowTitle(), QIcon( ":/project/icons/project/project.png" ) )
        # init opened files dock
        pOpenedFileExplorer* openedFileExplorer = mks.monkeycore.workspace().dockWidget()
        dockToolBar( Qt.LeftToolBarArea ).addDock( openedFileExplorer, openedFileExplorer.windowTitle(), openedFileExplorer.windowIcon() )
        # init multitoolbar
        mks.monkeycore.workspace().initMultiToolBar( mks.monkeycore.multiToolBar().toolBar( pWorkspace.defaultContext() ) )
        mks.monkeycore.workspace().initMultiToolBar( mks.monkeycore.multiToolBar().toolBar( "Coding" ) )
        # init status bar
        setStatusBar( mks.monkeycore.statusBar() )
        # init connection
        initConnections()
        """

    def initMenuBar(self):
        # create menubar menus and actions
        mb = self.menuBar()
        
        mb.setDefaultShortcutContext( Qt.ApplicationShortcut )
        
        mb.menu( "mFile", self.tr( "File" ) )
        
        mb.beginGroup( "mFile" )
        mb.action( "aNew", self.tr( "&New..." ), QIcon( ":/file/icons/file/new.png" ), self.tr( "Ctrl+N" ), self.tr( "Create a new file" ) )
        mb.action( "aNewTextEditor", self.tr( "&New Text File..." ), QIcon( ":/file/icons/file/new.png" ), '', self.tr( "Quickly create a new text based file" ) )
        mb.action( "aOpen", self.tr( "&Open..." ), QIcon( ":/file/icons/file/open.png" ), self.tr( "Ctrl+O" ), self.tr( "Open a file" ) )
        mb.menu( "mRecents", self.tr( "&Recents" ), QIcon( ":/file/icons/file/recents.png" ) )
        mb.action( "mRecents/aClear", self.tr( "&Clear" ), QIcon( ":/file/icons/file/clear.png" ), '', self.tr( "Clear the recents files list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.action( "aSeparator1" )
        mb.menu( "mSession", self.tr( "Session" ), QIcon( ":/file/icons/file/session.png" ) )
        mb.action( "mSession/aSave", self.tr( "Save" ), QIcon( ":/file/icons/file/save.png" ), '', self.tr( "Save the current session files list" ) )
        mb.action( "mSession/aRestore", self.tr( "Restore" ), QIcon( ":/file/icons/file/restore.png" ), '', self.tr( "Restore the current session files list" ) )
        mb.action( "aSeparator2" )
        mb.menu( "mSave", self.tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ) )
        mb.action( "mSave/aCurrent", self.tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ), self.tr( "Ctrl+S" ), self.tr( "Save the current file" ) ).setEnabled( False )
        mb.action( "mSave/aAll", self.tr( "Save &All" ), QIcon( ":/file/icons/file/saveall.png" ), '', self.tr( "Save all files" ) ).setEnabled( False )
        mb.menu( "mClose", self.tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ) )
        mb.action( "mClose/aCurrent", self.tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ), self.tr( "Ctrl+W" ), self.tr( "Close the current file" ) ).setEnabled( False )
        mb.action( "mClose/aAll", self.tr( "Close &All" ), QIcon( ":/file/icons/file/closeall.png" ), '', self.tr( "Close all files" ) ).setEnabled( False )
        mb.action( "aSeparator3" )
        mb.action( "aReload", self.tr( "Reload" ), QIcon( ":/file/icons/file/reload.png" ), '', self.tr( "Reload the current file asking user confirmation if needed" ) ).setEnabled( False )
        mb.action( "aSaveAsBackup", self.tr( "Save As &Backup" ), QIcon( ":/file/icons/file/backup.png" ), '', self.tr( "Save a backup of the current file" ) ).setEnabled( False )
        mb.action( "aSeparator4" )
        mb.action( "aQuickPrint", self.tr( "Quic&k Print" ), QIcon( ":/file/icons/file/quickprint.png" ), '', self.tr( "Quick print the current file" ) ).setEnabled( False )
        mb.action( "aPrint", self.tr( "&Print..." ), QIcon( ":/file/icons/file/print.png" ), self.tr( "Ctrl+P" ), self.tr( "Print the current file" ) ).setEnabled( False )
        mb.action( "aSeparator5" )
        mb.action( "aQuit", self.tr( "&Quit" ), QIcon( ":/file/icons/file/quit.png" ), self.tr( "Ctrl+Q" ), self.tr( "Quit the application" ) )
        mb.endGroup()
        
        mb.menu( "mEdit", self.tr( "Edit" ) )
        
        mb.beginGroup( "mEdit" )
        mb.action( "aSettings", self.tr( "Settings..." ), QIcon( ":/edit/icons/edit/settings.png" ), "", self.tr( "Edit the application settings" ) )
        mb.action( "aShortcutsEditor", self.tr( "Shortcuts Editor..." ), QIcon( ":/edit/icons/edit/shortcuts.png" ), self.tr( "Ctrl+Shift+E" ), self.tr( "Edit the application shortcuts" ) )
        mb.action( "aTranslations", self.tr( "Translations..." ), QIcon( ":/edit/icons/edit/translations.png" ), self.tr( "Ctrl+T" ), self.tr( "Change the application translations files" ) )
        mb.action( "aSeparator1" )
        mb.action( "aUndo", self.tr( "&Undo" ), QIcon( ":/edit/icons/edit/undo.png" ), self.tr( "Ctrl+Z" ), self.tr( "Undo" ) ).setEnabled( False )
        mb.action( "aRedo", self.tr( "&Redo" ), QIcon( ":/edit/icons/edit/redo.png" ), self.tr( "Ctrl+Y" ), self.tr( "Redo" ) ).setEnabled( False )
        mb.action( "aSeparator2" )
        mb.action( "aCopy", self.tr( "&Copy" ), QIcon( ":/edit/icons/edit/copy.png" ), self.tr( "Ctrl+C" ), self.tr( "Copy" ) ).setEnabled( False )
        mb.action( "aCut", self.tr( "Cu&t" ), QIcon( ":/edit/icons/edit/cut.png" ), self.tr( "Ctrl+X" ), self.tr( "Cut" ) ).setEnabled( False )
        mb.action( "aPaste", self.tr( "&Paste" ), QIcon( ":/edit/icons/edit/paste.png" ), self.tr( "Ctrl+V" ), self.tr( "Paste" ) ).setEnabled( False )
        mb.action( "aSeparator3" )
        mb.menu( "mSearchReplace", self.tr( "&Search && Replace" ) )
        mb.action( "mSearchReplace/aSearchFile", self.tr( "&Search..." ), QIcon( ":/edit/icons/edit/search.png" ), self.tr( "Ctrl+F" ), self.tr( "Search in the current file..." ) )
        mb.action( "aGoTo", self.tr( "&Go To..." ), QIcon( ":/edit/icons/edit/goto.png" ), self.tr( "Ctrl+G" ), self.tr( "Go To..." ) ).setEnabled( False )
        mb.menu( "mAllCommands", self.tr( "&All Commands" ), QIcon( ":/edit/icons/edit/commands.png" ) )
        mb.menu( "mBookmarks", self.tr( "&Bookmarks" ), QIcon( ":/editor/bookmark.png" ) )
        mb.action( "aSeparator5" )
        mb.action( "aExpandAbbreviation", self.tr( "Expand Abbreviation" ), QIcon( ":/edit/icons/edit/abbreviation.png" ), self.tr( "Ctrl+E" ), self.tr( "Expand Abbreviation" ) ).setEnabled( False )
        mb.action( "aPrepareAPIs", self.tr( "Prepare APIs" ), QIcon( ":/edit/icons/edit/prepareapis.png" ), self.tr( "Ctrl+Alt+P" ), self.tr( "Prepare the APIs files for auto completion / calltips" ) )
        mb.endGroup()
        
        mb.menu( "mView", self.tr( "View" ) )
        
        mb.beginGroup( "mView" )
        mb.menu( "mStyle", self.tr( "&Style" ), QIcon( ":/view/icons/view/style.png" ) )
        mb.action( "aNext", self.tr( "&Next Tab" ), QIcon( ":/view/icons/view/next.png" ), self.tr( "Ctrl+Tab" ), self.tr( "Active the next tab" ) ).setEnabled( False )
        mb.action( "aPrevious", self.tr( "&Previous Tab" ), QIcon( ":/view/icons/view/previous.png" ), self.tr( "Ctrl+Shift+Tab" ), self.tr( "Active the previous tab" ) ).setEnabled( False )
        mb.action( "aFocusToEditor", self.tr( "Focus Editor" ), QIcon( ":/edit/icons/edit/text.png" ), self.tr( "Ctrl+Return" ), self.tr( "Set the focus to the current document editor" ) )
        mb.endGroup()
        
        mb.menu( "mProject", self.tr( "Project" ) )
        mb.beginGroup( "mProject" )
        """TODO
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
        """
        mb.menu( "mRecents", self.tr( "&Recents" ), QIcon( ":/project/icons/project/recents.png" ) )
        mb.action( "mRecents/aClear", self.tr( "&Clear" ), QIcon( ":/project/icons/project/clear.png" ), '', self.tr( "Clear the recents projects list" ) )
        mb.action( "mRecents/aSeparator1" )
        mb.endGroup()
        
        mb.menu( "mBuilder", self.tr( "Build" ) ).menuAction().setEnabled( False )
        mb.menu( "mBuilder" ).menuAction().setVisible( False )
        
        mb.beginGroup( "mBuilder" )
        mb.menu( "mBuild", self.tr( "&Build" ), QIcon( ":/build/icons/build/build.png" ) )
        mb.menu( "mRebuild", self.tr( "&Rebuild" ), QIcon( ":/build/icons/build/rebuild.png" ) )
        mb.menu( "mClean", self.tr( "&Clean" ), QIcon( ":/build/icons/build/clean.png" ) )
        mb.menu( "mExecute", self.tr( "&Execute" ), QIcon( ":/build/icons/build/execute.png" ) )
        mb.menu( "mUserCommands", self.tr( "&User Commands" ), QIcon( ":/build/icons/build/misc.png" ) )
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
        mb.menu( "mDocks", self.tr( "Docks" ) )
        mb.menu( "mHelp", self.tr( "Help" ) )
        
        mb.beginGroup( "mHelp" )
        mb.action( "aAbout", self.tr( "&About..." ), QIcon( ":/application/icons/application/monkey2.png" ), '', self.tr( "About application..." ) )
        mb.action( "aAboutQt", self.tr( "About &Qt..." ), QIcon( ":/help/icons/help/qt.png" ), '', self.tr( "About Qt..." ) )
        mb.action( "aSeparator1" )
        mb.endGroup()
        
        """TODO
        # create action for styles
        agStyles = pStylesActionGroup( self.tr( "Use %1 style" ), mb.menu( "mView/mStyle" ) )
        agStyles.setCurrentStyle( mks.monkeycore.settings().value( "MainWindow/Style" ).toString() )
        mb.menu( "mView/mStyle" ).addActions( agStyles.actions() )
        
        # create plugins actions
        mks.mks.monkeycore.pluginsManager().menuHandler().setMenu( mb.menu( "mPlugins" ) )
        """
    
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
        """TODO
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
        """
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
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mFile/mRecents" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mFile/mSession" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mProject/mRecents" ).menuAction() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # settings
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aSettings" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aShortcutsEditor" ) )
        # file action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aNew" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aNewTextEditor" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aOpen" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addActions( menuBar().menu( "mFile/mSave" ).actions() )
        self.dockToolBar( Qt.TopToolBarArea ).addActions( menuBar().menu( "mFile/mClose" ).actions() )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aQuickPrint" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # edit action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aUndo" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aRedo" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aCut" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aCopy" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aPaste" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aGoTo" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # help action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mHelp/aAbout" ) )
        self.dockToolBar( Qt.TopToolBarArea ).addAction()
        # console action
        self.dockToolBar( Qt.TopToolBarArea ).addAction( MonkeyCore.consoleManager().stopAction() )


    def initConnections(self):
        """TODO
        # file connection
        self.connect( self.menuBar().action( "mFile/aNew" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileNew_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aNewTextEditor" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( createNewTextEditor() ) )
        self.connect( self.menuBar().action( "mFile/aOpen" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileOpen_triggered() ) )
        self.connect( MonkeyCore.recentsManager(), SIGNAL( openFileRequested(  QString&,  QString& ) ), MonkeyCore.fileManager(), SLOT( openFile(  QString&,  QString& ) ) )
        self.connect( self.menuBar().action( "mFile/mSession/aSave" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileSessionSave_triggered() ) )
        self.connect( self.menuBar().action( "mFile/mSession/aRestore" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileSessionRestore_triggered() ) )
        self.connect( self.menuBar().action( "mFile/mSave/aCurrent" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileSaveCurrent_triggered() ) )
        self.connect( self.menuBar().action( "mFile/mSave/aAll" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileSaveAll_triggered() ) )
        self.connect( self.menuBar().action( "mFile/mClose/aCurrent" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileCloseCurrent_triggered() ) )
        self.connect( self.menuBar().action( "mFile/mClose/aAll" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileCloseAll_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aReload" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileReload_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aSaveAsBackup" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileSaveAsBackup_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aQuickPrint" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileQuickPrint_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aPrint" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( filePrint_triggered() ) )
        self.connect( self.menuBar().action( "mFile/aQuit" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( fileExit_triggered() ) )
        # edit connection
        self.connect( self.menuBar().action( "mEdit/aSettings" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editSettings_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aShortcutsEditor" ), SIGNAL( triggered() ), MonkeyCore.actionsManager(), SLOT( editActionsShortcuts() ) )
        self.connect( self.menuBar().action( "mEdit/aTranslations" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editTranslations_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aUndo" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editUndo_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aRedo" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editRedo_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aCut" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editCut_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aCopy" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editCopy_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aPaste" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editPaste_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/mSearchReplace/aSearchFile" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editSearch_triggered() ) )
        #self.connect( self.menuBar().action( "mEdit/aSearchPrevious" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editSearchPrevious_triggered() ) )
        #self.connect( self.menuBar().action( "mEdit/aSearchNext" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editSearchNext_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aGoTo" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editGoTo_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aExpandAbbreviation" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editExpandAbbreviation_triggered() ) )
        self.connect( self.menuBar().action( "mEdit/aPrepareAPIs" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( editPrepareAPIs_triggered() ) )
        # view connection
        self.connect( agStyles, SIGNAL( styleSelected(  QString& ) ), this, SLOT( changeStyle(  QString& ) ) )
        self.connect( self.menuBar().action( "mView/aNext" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( activateNextDocument() ) )
        self.connect( self.menuBar().action( "mView/aPrevious" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( activatePreviousDocument() ) )
        self.connect( self.menuBar().action( "mView/aFocusToEditor" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( focusEditor() ) )
        # docks
        self.connect( self.menuBar().menu( "mDocks" ), SIGNAL( aboutToShow() ), this, SLOT( menu_Docks_aboutToShow() ) )
        # project connection
        self.connect( MonkeyCore.recentsManager(), SIGNAL( openProjectRequested(  QString&,  QString& ) ), MonkeyCore.projectsManager(), SLOT( openProject(  QString&,  QString& ) ) )
        self.connect( MonkeyCore.projectsManager(), SIGNAL( fileDoubleClicked(  QString&,  QString& ) ), MonkeyCore.workspace(), SLOT( openFile(  QString&,  QString& ) ) )
        # builder debugger interpreter menu
        self.connect( self.menuBar().menu( "mBuilder" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) )
        self.connect( self.menuBar().menu( "mDebugger" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) )
        self.connect( self.menuBar().menu( "mInterpreter" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) )
        # plugins menu
        # window menu
        self.connect( self.menuBar().action( "mWindow/aTile" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( tile() ) )
        self.connect( self.menuBar().action( "mWindow/aCascase" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( cascade() ) )
        self.connect( self.menuBar().action( "mWindow/aMinimize" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( minimize() ) )
        self.connect( self.menuBar().action( "mWindow/aRestore" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( restore() ) )
        # help menu
        self.connect( self.menuBar().action( "mHelp/aAbout" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( helpAboutApplication_triggered() ) )
        self.connect( self.menuBar().action( "mHelp/aAboutQt" ), SIGNAL( triggered() ), MonkeyCore.workspace(), SLOT( helpAboutQt_triggered() ) )
        """
    
    def finalyzeGuiInit(self):
        self.setWindowTitle( "%s v%s (%s)" % (mks.config.PACKAGE_NAME, mks.config.PACKAGE_VERSION, mks.config.PACKAGE_VERSION_STR ) )
        self.setWindowIcon( self.menuBar().action( "mHelp/aAbout" ).icon() )
    
    def menu_Docks_aboutToShow(self):
        # get menu
        menu = self.menuBar().menu( "mDocks" )
        menu.clear()
        
        # add actions
        for dw in self.findChildren(QDockWidget):
            action = dw.toggleViewAction()
            
            action.setIcon( dw.windowIcon() )
            menu.addAction( action )
            self.menuBar().addAction( "mDocks", action )

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
