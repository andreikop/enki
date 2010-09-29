'''***************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIMain.cpp
** Date      : 2008-01-14T00:36:56
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
**
	Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with self program; if not, to the Free Software
	Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "UIMain.h"
#include "main.h"
#include "coremanager/MonkeyCore.h"
#include "pMonkeyStudio.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "recentsmanager/pRecentsManager.h"
#include "consolemanager/pConsoleManager.h"
#include "workspace/pFileManager.h"
#include "pluginsmanager/PluginsManager.h"
#include "pluginsmanager/PluginsMenu.h"
#include "statusbar/StatusBar.h"
#include "workspace/pOpenedFileExplorer.h"

#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pDockToolBar.h>
#include <widgets/pMultiToolBar.h>
#include <widgets/pMenuBar.h>
#include <objects/pStylesActionGroup.h>

#include <QCloseEvent>
#include <QMenu>
#include <QStyleFactory>
#include <QDebug>

UIMain.UIMain( QWidget* p )
	: pMainWindow( p )
	setUnifiedTitleAndToolBarOnMac( True )
	setIconSize( QSize( 16, 16 ) )
	setAcceptDrops( True )
	
	setCorner( Qt.TopLeftCorner, Qt.LeftDockWidgetArea )
	setCorner( Qt.TopRightCorner, Qt.RightDockWidgetArea )
	setCorner( Qt.BottomLeftCorner, Qt.LeftDockWidgetArea )
	setCorner( Qt.BottomRightCorner, Qt.RightDockWidgetArea )


def dragEnterEvent(self, event ):
	# if correct mime and same tabbar
	if  event.mimeData().hasUrls() :
		# accept drag
		event.acceptProposedAction()


	# default event
	pMainWindow.dragEnterEvent( event )


def dropEvent(self, event ):
	if  event.mimeData().hasUrls() :
		urlsDropped.emit( event.mimeData().urls () )


	# default event
	pMainWindow.dropEvent( event )


def initGui(self):
	# init menubar
	initMenuBar()
	# init recents manager
	MonkeyCore.recentsManager()
	# init toolbar
	initToolBar()
	# init workspace
	setCentralWidget( MonkeyCore.workspace() )
	# init message toolbar
	messageTb = MonkeyCore.messageManager()
	messageTb.setObjectName( "pQueuedMessageToolBar" )
	messageTb.setVisible( False )
	messageTb.setDefaultPixmap( pIconManager.pixmap( "messages_infos.png", ":/messages" ) )
	pMonkeyStudio.setMacSmallSize( messageTb, True, True )
	centralWidget().layout().setMenuBar( messageTb )
	# init projects manager
	dockToolBar( Qt.LeftToolBarArea ).addDock( MonkeyCore.projectsManager(), MonkeyCore.projectsManager().windowTitle(), QIcon( ":/project/icons/project/project.png" ) )
	# init opened files dock
	openedFileExplorer = MonkeyCore.workspace().dockWidget()
	dockToolBar( Qt.LeftToolBarArea ).addDock( openedFileExplorer, openedFileExplorer.windowTitle(), openedFileExplorer.windowIcon() )
	# init multitoolbar
	MonkeyCore.workspace().initMultiToolBar( MonkeyCore.multiToolBar().toolBar( pWorkspace.defaultContext() ) )
	MonkeyCore.workspace().initMultiToolBar( MonkeyCore.multiToolBar().toolBar( "Coding" ) )
	# init status bar
	setStatusBar( MonkeyCore.statusBar() )
	# init connection
	initConnections()


def closeEvent(self, event ):
	# inform that we close mainwindow
	aboutToClose.emit()
	
	# save session if needed
	if  pMonkeyStudio.saveSessionOnClose() :
		MonkeyCore.workspace().fileSessionSave_triggered()

	
	# request close all documents
	if  not MonkeyCore.workspace().closeAllDocuments() :
		event.ignore()
		return

	
	# force to close all projects
	MonkeyCore.projectsManager().action( XUPProjectManager.atCloseAll ).trigger()
	
	pMainWindow.closeEvent( event )


def createPopupMenu(self):
	# create default menu
	menu = QMenu( self ); #QMainWindow.createPopupMenu()
	# add exclusive action of pDockToolBar
	QList<pDockToolBar*> tbs = findChildren<pDockToolBar*>()
	
	for tb in tbs:
		if  tb.parent() != self :
			continue

		
		menu.addAction( tb.toggleExclusiveAction() )

	
	return menu


def initMenuBar(self):
	# create menubar menus and actions
	mb = menuBar()
	
	mb.setDefaultShortcutContext( Qt.ApplicationShortcut )
	mb.menu( "mFile", tr( "File" ) )
	mb.beginGroup( "mFile" )
		mb.action( "aNew", tr( "&New..." ), QIcon( ":/file/icons/file/new.png" ), tr( "Ctrl+N" ), tr( "Create a file" ) )
		mb.action( "aNewTextEditor", tr( "&New Text File..." ), QIcon( ":/file/icons/file/new.png" ), QString.null, tr( "Quickly create a text based file" ) )
		mb.action( "aOpen", tr( "&Open..." ), QIcon( ":/file/icons/file/open.png" ), tr( "Ctrl+O" ), tr( "Open a file" ) )
		mb.menu( "mRecents", tr( "&Recents" ), QIcon( ":/file/icons/file/recents.png" ) )
		mb.action( "mRecents/aClear", tr( "&Clear" ), QIcon( ":/file/icons/file/clear.png" ), QString.null, tr( "Clear the recents files list" ) )
		mb.action( "mRecents/aSeparator1" )
		mb.action( "aSeparator1" )
		mb.menu( "mSession", tr( "Session" ), QIcon( ":/file/icons/file/session.png" ) )
		mb.action( "mSession/aSave", tr( "Save" ), QIcon( ":/file/icons/file/save.png" ), QString.null, tr( "Save the current session files list" ) )
		mb.action( "mSession/aRestore", tr( "Restore" ), QIcon( ":/file/icons/file/restore.png" ), QString.null, tr( "Restore the current session files list" ) )
		mb.action( "aSeparator2" )
		mb.menu( "mSave", tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ) )
		mb.action( "mSave/aCurrent", tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ), tr( "Ctrl+S" ), tr( "Save the current file" ) ).setEnabled( False )
		mb.action( "mSave/aAll", tr( "Save &All" ), QIcon( ":/file/icons/file/saveall.png" ), QString.null, tr( "Save all files" ) ).setEnabled( False )
		mb.menu( "mClose", tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ) )
		mb.action( "mClose/aCurrent", tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ), tr( "Ctrl+W" ), tr( "Close the current file" ) ).setEnabled( False )
		mb.action( "mClose/aAll", tr( "Close &All" ), QIcon( ":/file/icons/file/closeall.png" ), QString.null, tr( "Close all files" ) ).setEnabled( False )
		mb.action( "aSeparator3" )
		mb.action( "aReload", tr( "Reload" ), QIcon( ":/file/icons/file/reload.png" ), QString.null, tr( "Reload the current file asking user confirmation if needed" ) ).setEnabled( False )
		mb.action( "aSaveAsBackup", tr( "Save As &Backup" ), QIcon( ":/file/icons/file/backup.png" ), QString.null, tr( "Save a backup of the current file" ) ).setEnabled( False )
		mb.action( "aSeparator4" )
		mb.action( "aQuickPrint", tr( "Quic&k Print" ), QIcon( ":/file/icons/file/quickprint.png" ), QString.null, tr( "Quick print the current file" ) ).setEnabled( False )
		mb.action( "aPrint", tr( "&Print..." ), QIcon( ":/file/icons/file/print.png" ), tr( "Ctrl+P" ), tr( "Print the current file" ) ).setEnabled( False )
		mb.action( "aSeparator5" )
		mb.action( "aQuit", tr( "&Quit" ), QIcon( ":/file/icons/file/quit.png" ), tr( "Ctrl+Q" ), tr( "Quit the application" ) )
	mb.endGroup()
	mb.menu( "mEdit", tr( "Edit" ) )
	mb.beginGroup( "mEdit" )
		mb.action( "aSettings", tr( "Settings..." ), QIcon( ":/edit/icons/edit/settings.png" ), "", tr( "Edit the application settings" ) )
		mb.action( "aShortcutsEditor", tr( "Shortcuts Editor..." ), QIcon( ":/edit/icons/edit/shortcuts.png" ), tr( "Ctrl+Shift+E" ), tr( "Edit the application shortcuts" ) )
		mb.action( "aTranslations", tr( "Translations..." ), QIcon( ":/edit/icons/edit/translations.png" ), tr( "Ctrl+T" ), tr( "Change the application translations files" ) )
		mb.action( "aSeparator1" )
		mb.action( "aUndo", tr( "&Undo" ), QIcon( ":/edit/icons/edit/undo.png" ), tr( "Ctrl+Z" ), tr( "Undo" ) ).setEnabled( False )
		mb.action( "aRedo", tr( "&Redo" ), QIcon( ":/edit/icons/edit/redo.png" ), tr( "Ctrl+Y" ), tr( "Redo" ) ).setEnabled( False )
		mb.action( "aSeparator2" )
		mb.action( "aCopy", tr( "&Copy" ), QIcon( ":/edit/icons/edit/copy.png" ), tr( "Ctrl+C" ), tr( "Copy" ) ).setEnabled( False )
		mb.action( "aCut", tr( "Cu&t" ), QIcon( ":/edit/icons/edit/cut.png" ), tr( "Ctrl+X" ), tr( "Cut" ) ).setEnabled( False )
		mb.action( "aPaste", tr( "&Paste" ), QIcon( ":/edit/icons/edit/paste.png" ), tr( "Ctrl+V" ), tr( "Paste" ) ).setEnabled( False )
		mb.action( "aSeparator3" )
		mb.menu( "mSearchReplace", tr( "&Search and Replace" ) )
		mb.action( "mSearchReplace/aSearchFile", tr( "&Search..." ), QIcon( ":/edit/icons/edit/search.png" ), tr( "Ctrl+F" ), tr( "Search in the current file..." ) )
		mb.action( "aGoTo", tr( "&Go To..." ), QIcon( ":/edit/icons/edit/goto.png" ), tr( "Ctrl+G" ), tr( "Go To..." ) ).setEnabled( False )
		mb.menu( "mAllCommands", tr( "&All Commands" ), QIcon( ":/edit/icons/edit/commands.png" ) )
		mb.menu( "mBookmarks", tr( "&Bookmarks" ), QIcon( ":/editor/bookmark.png" ) )
		mb.action( "aSeparator5" )
		mb.action( "aExpandAbbreviation", tr( "Expand Abbreviation" ), QIcon( ":/edit/icons/edit/abbreviation.png" ), tr( "Ctrl+E" ), tr( "Expand Abbreviation" ) ).setEnabled( False )
		mb.action( "aPrepareAPIs", tr( "Prepare APIs" ), QIcon( ":/edit/icons/edit/prepareapis.png" ), tr( "Ctrl+Alt+P" ), tr( "Prepare the APIs files for auto completion / calltips" ) )
	mb.endGroup()
	mb.menu( "mView", tr( "View" ) )
	mb.beginGroup( "mView" )
		mb.menu( "mStyle", tr( "&Style" ), QIcon( ":/view/icons/view/style.png" ) )
		mb.action( "aNext", tr( "&Next Tab" ), QIcon( ":/view/icons/view/next.png" ), tr( "Ctrl+Tab" ), tr( "Active the next tab" ) ).setEnabled( False )
		mb.action( "aPrevious", tr( "&Previous Tab" ), QIcon( ":/view/icons/view/previous.png" ), tr( "Ctrl+Shift+Tab" ), tr( "Active the previous tab" ) ).setEnabled( False )
		mb.action( "aFocusToEditor", tr( "Focus Editor" ), QIcon( ":/edit/icons/edit/text.png" ), tr( "Ctrl+Return" ), tr( "Set the focus to the current document editor" ) )
	mb.endGroup()
	mb.menu( "mProject", tr( "Project" ) )
	mb.beginGroup( "mProject" )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atNew ) )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atOpen ) )
		mb.action( "aSeparator1" )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atClose ) )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atCloseAll ) )
		mb.action( "aSeparator2" )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atEdit ) )
		mb.action( "aSeparator3" )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atAddFiles ) )
		mb.addAction( QString.null, MonkeyCore.projectsManager().action( XUPProjectManager.atRemoveFiles ) )
		mb.action( "aSeparator4" )
		mb.menu( "mRecents", tr( "&Recents" ), QIcon( ":/project/icons/project/recents.png" ) )
		mb.action( "mRecents/aClear", tr( "&Clear" ), QIcon( ":/project/icons/project/clear.png" ), QString.null, tr( "Clear the recents projects list" ) )
		mb.action( "mRecents/aSeparator1" )
	mb.endGroup()
	mb.menu( "mBuilder", tr( "Build" ) ).menuAction().setEnabled( False )
	mb.menu( "mBuilder" ).menuAction().setVisible( False )
	mb.beginGroup( "mBuilder" )
		mb.menu( "mBuild", tr( "&Build" ), QIcon( ":/build/icons/build/build.png" ) )
		mb.menu( "mRebuild", tr( "&Rebuild" ), QIcon( ":/build/icons/build/rebuild.png" ) )
		mb.menu( "mClean", tr( "&Clean" ), QIcon( ":/build/icons/build/clean.png" ) )
		mb.menu( "mExecute", tr( "&Execute" ), QIcon( ":/build/icons/build/execute.png" ) )
		mb.menu( "mUserCommands", tr( "&User Commands" ), QIcon( ":/build/icons/build/misc.png" ) )
		mb.action( "aSeparator1" )
	mb.endGroup()
	mb.menu( "mDebugger", tr( "Debugger" ) ).menuAction().setEnabled( False )
	mb.menu( "mDebugger" ).menuAction().setVisible( False )
	mb.menu( "mInterpreter", tr( "Interpreter" ) ).menuAction().setEnabled( False )
	mb.menu( "mInterpreter" ).menuAction().setVisible( False )
	mb.menu( "mPlugins", tr( "Plugins" ) )
	mb.beginGroup( "mPlugins" )
		mb.action( "aSeparator1" )
	mb.endGroup()
	mb.menu( "mWindow", tr( "Window" ) )
	mb.beginGroup( "mWindow" )
		mb.action( "aCascase", tr( "&Cascade" ), QIcon( "" ), QString.null, tr( "Cascade" ) )
		mb.action( "aTile", tr( "&Tile" ), QIcon( "" ), QString.null, tr( "Tile" ) )
		mb.action( "aMinimize", tr( "&Minimize" ), QIcon( "" ), QString.null, tr( "Minimize" ) )
		mb.action( "aRestore", tr( "&Restore" ), QIcon( "" ), QString.null, tr( "Restore normal size" ) )
	mb.endGroup()
	mb.menu( "mDocks", tr( "Docks" ) )
	mb.menu( "mHelp", tr( "Help" ) )
	mb.beginGroup( "mHelp" )
		mb.action( "aAbout", tr( "&About..." ), QIcon( ":/application/icons/application/monkey2.png" ), QString.null, tr( "About application..." ) )
		mb.action( "aAboutQt", tr( "About &Qt..." ), QIcon( ":/help/icons/help/qt.png" ), QString.null, tr( "About Qt..." ) )
		mb.action( "aSeparator1" )
#ifdef __COVERAGESCANNER__
		mb.action( "aTestReport", tr( "&Test Report" ), QIcon( ) , tr( "Pause" ), tr( "Coverage Meter Test Report..." ) )
		mb.action( "aSeparator2" )
#endif
	mb.endGroup()

	# create action for styles
	agStyles = pStylesActionGroup( tr( "Use %1 style" ), mb.menu( "mView/mStyle" ) )
	agStyles.setCurrentStyle( MonkeyCore.settings().value( "MainWindow/Style" ).toString() )
	mb.menu( "mView/mStyle" ).addActions( agStyles.actions() )
	
	# create plugins actions
	MonkeyCore.pluginsManager().menuHandler().setMenu( mb.menu( "mPlugins" ) )


def initToolBar(self):
	# recents
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mFile/mRecents" ).menuAction() )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mFile/mSession" ).menuAction() )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().menu( "mProject/mRecents" ).menuAction() )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	# settings
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aSettings" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aShortcutsEditor" ) )
	# file action
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aNew" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aNewTextEditor" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aOpen" ) )
	dockToolBar( Qt.TopToolBarArea ).addActions( menuBar().menu( "mFile/mSave" ).actions() )
	dockToolBar( Qt.TopToolBarArea ).addActions( menuBar().menu( "mFile/mClose" ).actions() )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mFile/aQuickPrint" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	# edit action
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aUndo" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aRedo" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aCut" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aCopy" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aPaste" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mEdit/aGoTo" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	# help action
	dockToolBar( Qt.TopToolBarArea ).addAction( menuBar().action( "mHelp/aAbout" ) )
	dockToolBar( Qt.TopToolBarArea ).addAction()
	# console action
	dockToolBar( Qt.TopToolBarArea ).addAction( MonkeyCore.consoleManager().stopAction() )


def initConnections(self):
	# file connection
	menuBar().action( "mFile/aNew" ).triggered.connect(MonkeyCore.workspace().fileNew_triggered)
	menuBar().action( "mFile/aNewTextEditor" ).triggered.connect(MonkeyCore.workspace().createNewTextEditor)
	menuBar().action( "mFile/aOpen" ).triggered.connect(MonkeyCore.workspace().fileOpen_triggered)
	MonkeyCore.recentsManager().openFileRequested.connect(MonkeyCore.fileManager().openFile)
	menuBar().action( "mFile/mSession/aSave" ).triggered.connect(MonkeyCore.workspace().fileSessionSave_triggered)
	menuBar().action( "mFile/mSession/aRestore" ).triggered.connect(MonkeyCore.workspace().fileSessionRestore_triggered)
	menuBar().action( "mFile/mSave/aCurrent" ).triggered.connect(MonkeyCore.workspace().fileSaveCurrent_triggered)
	menuBar().action( "mFile/mSave/aAll" ).triggered.connect(MonkeyCore.workspace().fileSaveAll_triggered)
	menuBar().action( "mFile/mClose/aCurrent" ).triggered.connect(MonkeyCore.workspace().fileCloseCurrent_triggered)
	menuBar().action( "mFile/mClose/aAll" ).triggered.connect(MonkeyCore.workspace().fileCloseAll_triggered)
	menuBar().action( "mFile/aReload" ).triggered.connect(MonkeyCore.workspace().fileReload_triggered)
	menuBar().action( "mFile/aSaveAsBackup" ).triggered.connect(MonkeyCore.workspace().fileSaveAsBackup_triggered)
	menuBar().action( "mFile/aQuickPrint" ).triggered.connect(MonkeyCore.workspace().fileQuickPrint_triggered)
	menuBar().action( "mFile/aPrint" ).triggered.connect(MonkeyCore.workspace().filePrint_triggered)
	menuBar().action( "mFile/aQuit" ).triggered.connect(MonkeyCore.workspace().fileExit_triggered)
	# edit connection
	menuBar().action( "mEdit/aSettings" ).triggered.connect(MonkeyCore.workspace().editSettings_triggered)
	menuBar().action( "mEdit/aShortcutsEditor" ).triggered.connect(MonkeyCore.actionsManager().editActionsShortcuts)
	menuBar().action( "mEdit/aTranslations" ).triggered.connect(MonkeyCore.workspace().editTranslations_triggered)
	menuBar().action( "mEdit/aUndo" ).triggered.connect(MonkeyCore.workspace().editUndo_triggered)
	menuBar().action( "mEdit/aRedo" ).triggered.connect(MonkeyCore.workspace().editRedo_triggered)
	menuBar().action( "mEdit/aCut" ).triggered.connect(MonkeyCore.workspace().editCut_triggered)
	menuBar().action( "mEdit/aCopy" ).triggered.connect(MonkeyCore.workspace().editCopy_triggered)
	menuBar().action( "mEdit/aPaste" ).triggered.connect(MonkeyCore.workspace().editPaste_triggered)
	menuBar().action( "mEdit/mSearchReplace/aSearchFile" ).triggered.connect(MonkeyCore.workspace().editSearch_triggered)
	#menuBar().action( "mEdit/aSearchPrevious" ).triggered.connect(MonkeyCore.workspace().editSearchPrevious_triggered)
	#menuBar().action( "mEdit/aSearchNext" ).triggered.connect(MonkeyCore.workspace().editSearchNext_triggered)
	menuBar().action( "mEdit/aGoTo" ).triggered.connect(MonkeyCore.workspace().editGoTo_triggered)
	menuBar().action( "mEdit/aExpandAbbreviation" ).triggered.connect(MonkeyCore.workspace().editExpandAbbreviation_triggered)
	menuBar().action( "mEdit/aPrepareAPIs" ).triggered.connect(MonkeyCore.workspace().editPrepareAPIs_triggered)
	# view connection
	agStyles.styleSelected.connect(self.changeStyle)
	menuBar().action( "mView/aNext" ).triggered.connect(MonkeyCore.workspace().activateNextDocument)
	menuBar().action( "mView/aPrevious" ).triggered.connect(MonkeyCore.workspace().activatePreviousDocument)
	menuBar().action( "mView/aFocusToEditor" ).triggered.connect(MonkeyCore.workspace().focusEditor)
	# docks
	menuBar().menu( "mDocks" ).aboutToShow.connect(self.menu_Docks_aboutToShow)
	# project connection
	MonkeyCore.recentsManager().openProjectRequested.connect(MonkeyCore.projectsManager().openProject)
	MonkeyCore.projectsManager().fileDoubleClicked.connect(MonkeyCore.workspace().openFile)
	# builder debugger interpreter menu
	menuBar().menu( "mBuilder" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
	menuBar().menu( "mDebugger" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
	menuBar().menu( "mInterpreter" ).aboutToShow.connect(self.menu_CustomAction_aboutToShow)
	# plugins menu
	# window menu
	menuBar().action( "mWindow/aTile" ).triggered.connect(MonkeyCore.workspace().tile)
	menuBar().action( "mWindow/aCascase" ).triggered.connect(MonkeyCore.workspace().cascade)
	menuBar().action( "mWindow/aMinimize" ).triggered.connect(MonkeyCore.workspace().minimize)
	menuBar().action( "mWindow/aRestore" ).triggered.connect(MonkeyCore.workspace().restore)
	# help menu
	menuBar().action( "mHelp/aAbout" ).triggered.connect(MonkeyCore.workspace().helpAboutApplication_triggered)
	menuBar().action( "mHelp/aAboutQt" ).triggered.connect(MonkeyCore.workspace().helpAboutQt_triggered)
#ifdef __COVERAGESCANNER__
	menuBar().action( "mHelp/aTestReport" ).triggered.connect(MonkeyCore.workspace().helpTestReport_triggered)
#endif


def finalyzeGuiInit(self):
	setWindowTitle( QObject.tr( "%1 v%2 (%3)" ).arg( PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_VERSION_STR ) )
	setWindowIcon( menuBar().action( "mHelp/aAbout" ).icon() )


def menu_Docks_aboutToShow(self):
	# get menu
	menu = menuBar().menu( "mDocks" )
	menu.clear()

	# add actions
	foreach ( QDockWidget* dw, findChildren<QDockWidget*>() )
		action = dw.toggleViewAction()

		action.setIcon( dw.windowIcon() )
		menu.addAction( action )
		menuBar().addAction( "mDocks", action )



def updateMenuVisibility(self, menu ):
	menuAction = menu.menuAction()
	menuVisible = False
	
	for action in menu.actions():
		if  action.isSeparator() :
			continue

		
		subMenu = action.menu()
		
		if  subMenu :
			if  updateMenuVisibility( subMenu ) :
				menuVisible = True


		else:
			menuVisible = True


	
	menuAction.setVisible( menuVisible )
	menuAction.setEnabled( menuVisible )
	
	return menuVisible


def menu_CustomAction_aboutToShow(self):
	QList<QMenu*> menus
	
	if  sender() :
		menus << qobject_cast<QMenu*>( sender() )

	else:
		menus << menuBar().menu( "mBuilder" ) << menuBar().menu( "mDebugger" ) << menuBar().menu( "mInterpreter" )

	
	for m in menus:
		updateMenuVisibility( m )



def changeStyle(self, style ):
	qApp.setStyle( style )
	qApp.setPalette( qApp.style().standardPalette() )
	settings().setValue( "MainWindow/Style", style )

