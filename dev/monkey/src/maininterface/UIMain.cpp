/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIMain.cpp
** Date      : 2008-01-14T00:36:56
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
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
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
**
****************************************************************************/
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

UIMain::UIMain( QWidget* p )
	: pMainWindow( p )
{
	setUnifiedTitleAndToolBarOnMac( true );
	setIconSize( QSize( 16, 16 ) );
	setAcceptDrops( true );
	
	setCorner( Qt::TopLeftCorner, Qt::LeftDockWidgetArea );
	setCorner( Qt::TopRightCorner, Qt::RightDockWidgetArea );
	setCorner( Qt::BottomLeftCorner, Qt::LeftDockWidgetArea );
	setCorner( Qt::BottomRightCorner, Qt::RightDockWidgetArea );
}

void UIMain::dragEnterEvent( QDragEnterEvent* event )
{
	// if correct mime and same tabbar
	if ( event->mimeData()->hasUrls() )
	{
		// accept drag
		event->acceptProposedAction();
	}

	// default event
	pMainWindow::dragEnterEvent( event );
}

void UIMain::dropEvent( QDropEvent* event )
{
	if ( event->mimeData()->hasUrls() )
	{
		emit urlsDropped( event->mimeData()->urls () );
	}

	// default event
	pMainWindow::dropEvent( event );
}

void UIMain::initGui()
{
	// init menubar
	initMenuBar();
	// init recents manager
	MonkeyCore::recentsManager();
	// init toolbar
	initToolBar();
	// init workspace
	setCentralWidget( MonkeyCore::workspace() );
	// init message toolbar
	pQueuedMessageToolBar* messageTb = MonkeyCore::messageManager();
	messageTb->setObjectName( "pQueuedMessageToolBar" );
	messageTb->setVisible( false );
	messageTb->setDefaultPixmap( pIconManager::pixmap( "messages_infos.png", ":/messages" ) );
	pMonkeyStudio::setMacSmallSize( messageTb, true, true );
	centralWidget()->layout()->setMenuBar( messageTb );
	// init projects manager
	dockToolBar( Qt::LeftToolBarArea )->addDock( MonkeyCore::projectsManager(), MonkeyCore::projectsManager()->windowTitle(), QIcon( ":/project/icons/project/project.png" ) );
	// init opened files dock
	pOpenedFileExplorer* openedFileExplorer = MonkeyCore::workspace()->dockWidget();
	dockToolBar( Qt::LeftToolBarArea )->addDock( openedFileExplorer, openedFileExplorer->windowTitle(), openedFileExplorer->windowIcon() );
	// init multitoolbar
	MonkeyCore::workspace()->initMultiToolBar( MonkeyCore::multiToolBar()->toolBar( pWorkspace::defaultContext() ) );
	MonkeyCore::workspace()->initMultiToolBar( MonkeyCore::multiToolBar()->toolBar( "Coding" ) );
	// init status bar
	setStatusBar( MonkeyCore::statusBar() );
	// init connection
	initConnections();
}

void UIMain::closeEvent( QCloseEvent* event )
{
	// inform that we close mainwindow
	emit aboutToClose();
	
	// save session if needed
	if ( pMonkeyStudio::saveSessionOnClose() )
	{
		MonkeyCore::workspace()->fileSessionSave_triggered();
	}
	
	// request close all documents
	if ( !MonkeyCore::workspace()->closeAllDocuments() )
	{
		event->ignore();
		return;
	}
	
	// force to close all projects
	MonkeyCore::projectsManager()->action( XUPProjectManager::atCloseAll )->trigger();
	
	pMainWindow::closeEvent( event );
}

QMenu* UIMain::createPopupMenu()
{
	// create default menu
	QMenu* menu = new QMenu( this ); //QMainWindow::createPopupMenu();
	// add exclusive action of pDockToolBar
	QList<pDockToolBar*> tbs = findChildren<pDockToolBar*>();
	
	foreach ( pDockToolBar* tb, tbs )
	{
		if ( tb->parent() != this )
		{
			continue;
		}
		
		menu->addAction( tb->toggleExclusiveAction() );
	}
	
	return menu;
}

void UIMain::initMenuBar()
{
	// create menubar menus and actions
	pMenuBar* mb = menuBar();
	
	mb->setDefaultShortcutContext( Qt::ApplicationShortcut );
	mb->menu( "mFile", tr( "File" ) );
	mb->beginGroup( "mFile" );
		mb->action( "aNew", tr( "&New..." ), QIcon( ":/file/icons/file/new.png" ), tr( "Ctrl+N" ), tr( "Create a new file" ) );
		mb->action( "aNewTextEditor", tr( "&New Text File..." ), QIcon( ":/file/icons/file/new.png" ), QString::null, tr( "Quickly create a new text based file" ) );
		mb->action( "aOpen", tr( "&Open..." ), QIcon( ":/file/icons/file/open.png" ), tr( "Ctrl+O" ), tr( "Open a file" ) );
		mb->menu( "mRecents", tr( "&Recents" ), QIcon( ":/file/icons/file/recents.png" ) );
		mb->action( "mRecents/aClear", tr( "&Clear" ), QIcon( ":/file/icons/file/clear.png" ), QString::null, tr( "Clear the recents files list" ) );
		mb->action( "mRecents/aSeparator1" );
		mb->action( "aSeparator1" );
		mb->menu( "mSession", tr( "Session" ), QIcon( ":/file/icons/file/session.png" ) );
		mb->action( "mSession/aSave", tr( "Save" ), QIcon( ":/file/icons/file/save.png" ), QString::null, tr( "Save the current session files list" ) );
		mb->action( "mSession/aRestore", tr( "Restore" ), QIcon( ":/file/icons/file/restore.png" ), QString::null, tr( "Restore the current session files list" ) );
		mb->action( "aSeparator2" );
		mb->menu( "mSave", tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ) );
		mb->action( "mSave/aCurrent", tr( "&Save" ), QIcon( ":/file/icons/file/save.png" ), tr( "Ctrl+S" ), tr( "Save the current file" ) )->setEnabled( false );
		mb->action( "mSave/aAll", tr( "Save &All" ), QIcon( ":/file/icons/file/saveall.png" ), QString::null, tr( "Save all files" ) )->setEnabled( false );
		mb->menu( "mClose", tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ) );
		mb->action( "mClose/aCurrent", tr( "&Close" ), QIcon( ":/file/icons/file/close.png" ), tr( "Ctrl+W" ), tr( "Close the current file" ) )->setEnabled( false );
		mb->action( "mClose/aAll", tr( "Close &All" ), QIcon( ":/file/icons/file/closeall.png" ), QString::null, tr( "Close all files" ) )->setEnabled( false );
		mb->action( "aSeparator3" );
		mb->action( "aReload", tr( "Reload" ), QIcon( ":/file/icons/file/reload.png" ), QString::null, tr( "Reload the current file asking user confirmation if needed" ) )->setEnabled( false );
		mb->action( "aSaveAsBackup", tr( "Save As &Backup" ), QIcon( ":/file/icons/file/backup.png" ), QString::null, tr( "Save a backup of the current file" ) )->setEnabled( false );
		mb->action( "aSeparator4" );
		mb->action( "aQuickPrint", tr( "Quic&k Print" ), QIcon( ":/file/icons/file/quickprint.png" ), QString::null, tr( "Quick print the current file" ) )->setEnabled( false );
		mb->action( "aPrint", tr( "&Print..." ), QIcon( ":/file/icons/file/print.png" ), tr( "Ctrl+P" ), tr( "Print the current file" ) )->setEnabled( false );
		mb->action( "aSeparator5" );
		mb->action( "aQuit", tr( "&Quit" ), QIcon( ":/file/icons/file/quit.png" ), tr( "Ctrl+Q" ), tr( "Quit the application" ) );
	mb->endGroup();
	mb->menu( "mEdit", tr( "Edit" ) );
	mb->beginGroup( "mEdit" );
		mb->action( "aSettings", tr( "Settings..." ), QIcon( ":/edit/icons/edit/settings.png" ), "", tr( "Edit the application settings" ) );
		mb->action( "aShortcutsEditor", tr( "Shortcuts Editor..." ), QIcon( ":/edit/icons/edit/shortcuts.png" ), tr( "Ctrl+Shift+E" ), tr( "Edit the application shortcuts" ) );
		mb->action( "aTranslations", tr( "Translations..." ), QIcon( ":/edit/icons/edit/translations.png" ), tr( "Ctrl+T" ), tr( "Change the application translations files" ) );
		mb->action( "aSeparator1" );
		mb->action( "aUndo", tr( "&Undo" ), QIcon( ":/edit/icons/edit/undo.png" ), tr( "Ctrl+Z" ), tr( "Undo" ) )->setEnabled( false );
		mb->action( "aRedo", tr( "&Redo" ), QIcon( ":/edit/icons/edit/redo.png" ), tr( "Ctrl+Y" ), tr( "Redo" ) )->setEnabled( false );
		mb->action( "aSeparator2" );
		mb->action( "aCopy", tr( "&Copy" ), QIcon( ":/edit/icons/edit/copy.png" ), tr( "Ctrl+C" ), tr( "Copy" ) )->setEnabled( false );
		mb->action( "aCut", tr( "Cu&t" ), QIcon( ":/edit/icons/edit/cut.png" ), tr( "Ctrl+X" ), tr( "Cut" ) )->setEnabled( false );
		mb->action( "aPaste", tr( "&Paste" ), QIcon( ":/edit/icons/edit/paste.png" ), tr( "Ctrl+V" ), tr( "Paste" ) )->setEnabled( false );
		mb->action( "aSeparator3" );
		mb->menu( "mSearchReplace", tr( "&Search && Replace" ) );
		mb->action( "mSearchReplace/aSearchFile", tr( "&Search..." ), QIcon( ":/edit/icons/edit/search.png" ), tr( "Ctrl+F" ), tr( "Search in the current file..." ) );
		mb->action( "aGoTo", tr( "&Go To..." ), QIcon( ":/edit/icons/edit/goto.png" ), tr( "Ctrl+G" ), tr( "Go To..." ) )->setEnabled( false );
		mb->menu( "mAllCommands", tr( "&All Commands" ), QIcon( ":/edit/icons/edit/commands.png" ) );
		mb->menu( "mBookmarks", tr( "&Bookmarks" ), QIcon( ":/editor/bookmark.png" ) );
		mb->action( "aSeparator5" );
		mb->action( "aExpandAbbreviation", tr( "Expand Abbreviation" ), QIcon( ":/edit/icons/edit/abbreviation.png" ), tr( "Ctrl+E" ), tr( "Expand Abbreviation" ) )->setEnabled( false );
		mb->action( "aPrepareAPIs", tr( "Prepare APIs" ), QIcon( ":/edit/icons/edit/prepareapis.png" ), tr( "Ctrl+Alt+P" ), tr( "Prepare the APIs files for auto completion / calltips" ) );
	mb->endGroup();
	mb->menu( "mView", tr( "View" ) );
	mb->beginGroup( "mView" );
		mb->menu( "mStyle", tr( "&Style" ), QIcon( ":/view/icons/view/style.png" ) );
		mb->action( "aNext", tr( "&Next Tab" ), QIcon( ":/view/icons/view/next.png" ), tr( "Ctrl+Tab" ), tr( "Active the next tab" ) )->setEnabled( false );
		mb->action( "aPrevious", tr( "&Previous Tab" ), QIcon( ":/view/icons/view/previous.png" ), tr( "Ctrl+Shift+Tab" ), tr( "Active the previous tab" ) )->setEnabled( false );
		mb->action( "aFocusToEditor", tr( "Focus Editor" ), QIcon( ":/edit/icons/edit/text.png" ), tr( "Ctrl+Return" ), tr( "Set the focus to the current document editor" ) );
	mb->endGroup();
	mb->menu( "mProject", tr( "Project" ) );
	mb->beginGroup( "mProject" );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atNew ) );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atOpen ) );
		mb->action( "aSeparator1" );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atClose ) );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atCloseAll ) );
		mb->action( "aSeparator2" );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atEdit ) );
		mb->action( "aSeparator3" );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atAddFiles ) );
		mb->addAction( QString::null, MonkeyCore::projectsManager()->action( XUPProjectManager::atRemoveFiles ) );
		mb->action( "aSeparator4" );
		mb->menu( "mRecents", tr( "&Recents" ), QIcon( ":/project/icons/project/recents.png" ) );
		mb->action( "mRecents/aClear", tr( "&Clear" ), QIcon( ":/project/icons/project/clear.png" ), QString::null, tr( "Clear the recents projects list" ) );
		mb->action( "mRecents/aSeparator1" );
	mb->endGroup();
	mb->menu( "mBuilder", tr( "Build" ) )->menuAction()->setEnabled( false );
	mb->menu( "mBuilder" )->menuAction()->setVisible( false );
	mb->beginGroup( "mBuilder" );
		mb->menu( "mBuild", tr( "&Build" ), QIcon( ":/build/icons/build/build.png" ) );
		mb->menu( "mRebuild", tr( "&Rebuild" ), QIcon( ":/build/icons/build/rebuild.png" ) );
		mb->menu( "mClean", tr( "&Clean" ), QIcon( ":/build/icons/build/clean.png" ) );
		mb->menu( "mExecute", tr( "&Execute" ), QIcon( ":/build/icons/build/execute.png" ) );
		mb->menu( "mUserCommands", tr( "&User Commands" ), QIcon( ":/build/icons/build/misc.png" ) );
		mb->action( "aSeparator1" );
	mb->endGroup();
	mb->menu( "mDebugger", tr( "Debugger" ) )->menuAction()->setEnabled( false );
	mb->menu( "mDebugger" )->menuAction()->setVisible( false );
	mb->menu( "mInterpreter", tr( "Interpreter" ) )->menuAction()->setEnabled( false );
	mb->menu( "mInterpreter" )->menuAction()->setVisible( false );
	mb->menu( "mPlugins", tr( "Plugins" ) );
	mb->beginGroup( "mPlugins" );
		mb->action( "aSeparator1" );
	mb->endGroup();
	mb->menu( "mWindow", tr( "Window" ) );
	mb->beginGroup( "mWindow" );
		mb->action( "aCascase", tr( "&Cascade" ), QIcon( "" ), QString::null, tr( "Cascade" ) );
		mb->action( "aTile", tr( "&Tile" ), QIcon( "" ), QString::null, tr( "Tile" ) );
		mb->action( "aMinimize", tr( "&Minimize" ), QIcon( "" ), QString::null, tr( "Minimize" ) );
		mb->action( "aRestore", tr( "&Restore" ), QIcon( "" ), QString::null, tr( "Restore normal size" ) );
	mb->endGroup();
	mb->menu( "mDocks", tr( "Docks" ) );
	mb->menu( "mHelp", tr( "Help" ) );
	mb->beginGroup( "mHelp" );
		mb->action( "aAbout", tr( "&About..." ), QIcon( ":/application/icons/application/monkey2.png" ), QString::null, tr( "About application..." ) );
		mb->action( "aAboutQt", tr( "About &Qt..." ), QIcon( ":/help/icons/help/qt.png" ), QString::null, tr( "About Qt..." ) );
		mb->action( "aSeparator1" );
#ifdef __COVERAGESCANNER__
		mb->action( "aTestReport", tr( "&Test Report" ), QIcon( ) , tr( "Pause" ), tr( "Coverage Meter Test Report..." ) );
		mb->action( "aSeparator2" );
#endif
	mb->endGroup();

	// create action for styles
	agStyles = new pStylesActionGroup( tr( "Use %1 style" ), mb->menu( "mView/mStyle" ) );
	agStyles->setCurrentStyle( MonkeyCore::settings()->value( "MainWindow/Style" ).toString() );
	mb->menu( "mView/mStyle" )->addActions( agStyles->actions() );
	
	// create plugins actions
	MonkeyCore::pluginsManager()->menuHandler()->setMenu( mb->menu( "mPlugins" ) );
}

void UIMain::initToolBar()
{
	// recents
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->menu( "mFile/mRecents" )->menuAction() );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->menu( "mFile/mSession" )->menuAction() );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->menu( "mProject/mRecents" )->menuAction() );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	// settings
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aSettings" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aShortcutsEditor" ) );
	// file action
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mFile/aNew" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mFile/aNewTextEditor" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mFile/aOpen" ) );
	dockToolBar( Qt::TopToolBarArea )->addActions( menuBar()->menu( "mFile/mSave" )->actions() );
	dockToolBar( Qt::TopToolBarArea )->addActions( menuBar()->menu( "mFile/mClose" )->actions() );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mFile/aQuickPrint" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	// edit action
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aUndo" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aRedo" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aCut" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aCopy" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aPaste" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mEdit/aGoTo" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	// help action
	dockToolBar( Qt::TopToolBarArea )->addAction( menuBar()->action( "mHelp/aAbout" ) );
	dockToolBar( Qt::TopToolBarArea )->addAction();
	// console action
	dockToolBar( Qt::TopToolBarArea )->addAction( MonkeyCore::consoleManager()->stopAction() );
}

void UIMain::initConnections()
{
	// file connection
	connect( menuBar()->action( "mFile/aNew" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileNew_triggered() ) );
	connect( menuBar()->action( "mFile/aNewTextEditor" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( createNewTextEditor() ) );
	connect( menuBar()->action( "mFile/aOpen" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileOpen_triggered() ) );
	connect( MonkeyCore::recentsManager(), SIGNAL( openFileRequested( const QString&, const QString& ) ), MonkeyCore::fileManager(), SLOT( openFile( const QString&, const QString& ) ) );
	connect( menuBar()->action( "mFile/mSession/aSave" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileSessionSave_triggered() ) );
	connect( menuBar()->action( "mFile/mSession/aRestore" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileSessionRestore_triggered() ) );
	connect( menuBar()->action( "mFile/mSave/aCurrent" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileSaveCurrent_triggered() ) );
	connect( menuBar()->action( "mFile/mSave/aAll" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileSaveAll_triggered() ) );
	connect( menuBar()->action( "mFile/mClose/aCurrent" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileCloseCurrent_triggered() ) );
	connect( menuBar()->action( "mFile/mClose/aAll" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileCloseAll_triggered() ) );
	connect( menuBar()->action( "mFile/aReload" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileReload_triggered() ) );
	connect( menuBar()->action( "mFile/aSaveAsBackup" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileSaveAsBackup_triggered() ) );
	connect( menuBar()->action( "mFile/aQuickPrint" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileQuickPrint_triggered() ) );
	connect( menuBar()->action( "mFile/aPrint" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( filePrint_triggered() ) );
	connect( menuBar()->action( "mFile/aQuit" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( fileExit_triggered() ) );
	// edit connection
	connect( menuBar()->action( "mEdit/aSettings" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editSettings_triggered() ) );
	connect( menuBar()->action( "mEdit/aShortcutsEditor" ), SIGNAL( triggered() ), MonkeyCore::actionsManager(), SLOT( editActionsShortcuts() ) );
	connect( menuBar()->action( "mEdit/aTranslations" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editTranslations_triggered() ) );
	connect( menuBar()->action( "mEdit/aUndo" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editUndo_triggered() ) );
	connect( menuBar()->action( "mEdit/aRedo" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editRedo_triggered() ) );
	connect( menuBar()->action( "mEdit/aCut" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editCut_triggered() ) );
	connect( menuBar()->action( "mEdit/aCopy" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editCopy_triggered() ) );
	connect( menuBar()->action( "mEdit/aPaste" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editPaste_triggered() ) );
	connect( menuBar()->action( "mEdit/mSearchReplace/aSearchFile" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editSearch_triggered() ) );
	//connect( menuBar()->action( "mEdit/aSearchPrevious" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editSearchPrevious_triggered() ) );
	//connect( menuBar()->action( "mEdit/aSearchNext" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editSearchNext_triggered() ) );
	connect( menuBar()->action( "mEdit/aGoTo" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editGoTo_triggered() ) );
	connect( menuBar()->action( "mEdit/aExpandAbbreviation" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editExpandAbbreviation_triggered() ) );
	connect( menuBar()->action( "mEdit/aPrepareAPIs" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( editPrepareAPIs_triggered() ) );
	// view connection
	connect( agStyles, SIGNAL( styleSelected( const QString& ) ), this, SLOT( changeStyle( const QString& ) ) );
	connect( menuBar()->action( "mView/aNext" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( activateNextDocument() ) );
	connect( menuBar()->action( "mView/aPrevious" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( activatePreviousDocument() ) );
	connect( menuBar()->action( "mView/aFocusToEditor" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( focusEditor() ) );
	// docks
	connect( menuBar()->menu( "mDocks" ), SIGNAL( aboutToShow() ), this, SLOT( menu_Docks_aboutToShow() ) );
	// project connection
	connect( MonkeyCore::recentsManager(), SIGNAL( openProjectRequested( const QString&, const QString& ) ), MonkeyCore::projectsManager(), SLOT( openProject( const QString&, const QString& ) ) );
	connect( MonkeyCore::projectsManager(), SIGNAL( fileDoubleClicked( const QString&, const QString& ) ), MonkeyCore::workspace(), SLOT( openFile( const QString&, const QString& ) ) );
	// builder debugger interpreter menu
	connect( menuBar()->menu( "mBuilder" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) );
	connect( menuBar()->menu( "mDebugger" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) );
	connect( menuBar()->menu( "mInterpreter" ), SIGNAL( aboutToShow() ), this, SLOT( menu_CustomAction_aboutToShow() ) );
	// plugins menu
	// window menu
	connect( menuBar()->action( "mWindow/aTile" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( tile() ) );
	connect( menuBar()->action( "mWindow/aCascase" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( cascade() ) );
	connect( menuBar()->action( "mWindow/aMinimize" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( minimize() ) );
	connect( menuBar()->action( "mWindow/aRestore" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( restore() ) );
	// help menu
	connect( menuBar()->action( "mHelp/aAbout" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( helpAboutApplication_triggered() ) );
	connect( menuBar()->action( "mHelp/aAboutQt" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( helpAboutQt_triggered() ) );
#ifdef __COVERAGESCANNER__
	connect( menuBar()->action( "mHelp/aTestReport" ), SIGNAL( triggered() ), MonkeyCore::workspace(), SLOT( helpTestReport_triggered() ) );
#endif
}

void UIMain::finalyzeGuiInit()
{
	setWindowTitle( QObject::tr( "%1 v%2 (%3)" ).arg( PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_VERSION_STR ) );
	setWindowIcon( menuBar()->action( "mHelp/aAbout" )->icon() );
}

void UIMain::menu_Docks_aboutToShow()
{
	// get menu
	QMenu* menu = menuBar()->menu( "mDocks" );
	menu->clear();

	// add actions
	foreach ( QDockWidget* dw, findChildren<QDockWidget*>() )
	{
		QAction* action = dw->toggleViewAction();

		action->setIcon( dw->windowIcon() );
		menu->addAction( action );
		menuBar()->addAction( "mDocks", action );
	}
}

bool UIMain::updateMenuVisibility( QMenu* menu )
{
	QAction* menuAction = menu->menuAction();
	bool menuVisible = false;
	
	foreach ( QAction* action, menu->actions() )
	{
		if ( action->isSeparator() )
		{
			continue;
		}
		
		QMenu* subMenu = action->menu();
		
		if ( subMenu )
		{
			if ( updateMenuVisibility( subMenu ) )
			{
				menuVisible = true;
			}
		}
		else
		{
			menuVisible = true;
		}
	}
	
	menuAction->setVisible( menuVisible );
	menuAction->setEnabled( menuVisible );
	
	return menuVisible;
}

void UIMain::menu_CustomAction_aboutToShow()
{
	QList<QMenu*> menus;
	
	if ( sender() )
	{
		menus << qobject_cast<QMenu*>( sender() );
	}
	else
	{
		menus << menuBar()->menu( "mBuilder" ) << menuBar()->menu( "mDebugger" ) << menuBar()->menu( "mInterpreter" );
	}
	
	foreach ( QMenu* m, menus )
	{
		updateMenuVisibility( m );
	}
}

void UIMain::changeStyle( const QString& style )
{
	qApp->setStyle( style );
	qApp->setPalette( qApp->style()->standardPalette() );
	settings()->setValue( "MainWindow/Style", style );
}
