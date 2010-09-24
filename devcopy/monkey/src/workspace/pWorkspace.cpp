'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : pWorkspace.cpp
** Date      : 2008-01-14T00:37:21
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
#include <QToolButton>
#include <QCloseEvent>
#include <QMainWindow>
#include <QFileInfo>
#include <QFileSystemWatcher>
#include <QDir>
#include <QMdiSubWindow>
#include <QVBoxLayout>
#include <QMessageBox>

#include <QDebug>

#include "pWorkspace.h"
#include "pOpenedFileExplorer.h"
#include "pAbstractChild.h"
#include "recentsmanager/pRecentsManager.h"
#include "pFileManager.h"
#include "maininterface/ui/UISettings.h"
#include "UISaveFiles.h"
#include "maininterface/ui/UIAbout.h"
#include "templatesmanager/ui/UITemplatesWizard.h"
#include "abbreviationsmanager/pAbbreviationsManager.h"
#include "pMonkeyStudio.h"
#include "templatesmanager/pTemplatesManager.h"
#include "xupmanager/gui/XUPProjectManager.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "pluginsmanager/PluginsManager.h"
#include "coremanager/MonkeyCore.h"
#include "maininterface/UIMain.h"
#include "statusbar/StatusBar.h"
#include "shared/MkSFileDialog.h"

#include "pChild.h"
#include "qscintillamanager/pEditor.h"

#include <widgets/pQueuedMessageToolBar.h>
#include <widgets/pMenuBar.h>
#include <widgets/pMultiToolBar.h>
#include <widgets/TranslationDialog.h>
#include <objects/TranslationManager.h>

int pWorkspace.CONTENT_CHANGED_TIME_OUT = 3000
QString pWorkspace.DEFAULT_CONTEXT = QLatin1String( "Default" )

pWorkspace.pWorkspace( QMainWindow* parent )
        : QFrame( parent )
    Q_ASSERT( parent )
    mViewMode = pWorkspace.NoTabs

    mb = MonkeyCore.menuBar()

    # action group for view modes
    mViewModesGroup = QActionGroup( self )
    mViewModesGroup.addAction( mb.action( "mWindow/aNoTabs" ) )
    mViewModesGroup.addAction( mb.action( "mWindow/aTopTabs" ) )
    mViewModesGroup.addAction( mb.action( "mWindow/aBottomTabs" ) )
    mViewModesGroup.addAction( mb.action( "mWindow/aLeftTabs" ) )
    mViewModesGroup.addAction( mb.action( "mWindow/aRightTabs" ) )
    mb.action( "mWindow/aSeparator1" )

    mb.menu( "mWindow" ).insertActions( mb.action( "mWindow/aCascase" ), mViewModesGroup.actions() )
    mb.menu( "mWindow" ).insertAction( mb.action( "mWindow/aCascase" ), mb.action( "mWindow/aSeparator1" ) )

    QList<QAction*> actions = mViewModesGroup.actions()

    for ( i = pWorkspace.NoTabs; i < pWorkspace.RightTabs +1; i++ )
        action = actions.at( i )
        action.setCheckable( True )
        action.setData( i )

        if  mViewMode == i :
            action.setChecked( True )


        switch ( (pWorkspace.ViewMode)i )
        case pWorkspace.NoTabs:
            action.setText( tr( "No Tabs" ) )
            action.setToolTip( tr( "No tabs, use 'Oopened Files List' to have a list of opened documents" ) )
            break
        case pWorkspace.TopTabs:
            action.setText( tr( "Tabs at &Top" ) )
            action.setToolTip( action.text() )
            break
        case pWorkspace.BottomTabs:
            action.setText( tr( "Tabs at &Bottom" ) )
            action.setToolTip( action.text() )
            break
        case pWorkspace.LeftTabs:
            action.setText( tr( "Tabs at &Left" ) )
            action.setToolTip( action.text() )
            break
        case pWorkspace.RightTabs:
            action.setText( tr( "Tabs at &Right" ) )
            action.setToolTip( action.text() )
            break



    mOpenedFileExplorer = pOpenedFileExplorer( self )

    # layout
    mLayout = QVBoxLayout( self )
    mLayout.setMargin( 0 )
    mLayout.setSpacing( 0 )

    # multitoolbar
    hline = QFrame( self )
    hline.setFrameStyle( QFrame.HLine | QFrame.Sunken )

    # document area
    mMdiArea = QMdiArea( self )
    mMdiArea.setActivationOrder( QMdiArea.CreationOrder )
    mMdiArea.setDocumentMode( True )

    # add widgets to layout
    mLayout.addWidget( MonkeyCore.multiToolBar() )
    mLayout.addWidget( hline )
    mLayout.addWidget( mMdiArea )

    # creaet file watcher
    mFileWatcher = QFileSystemWatcher( self )
    mContentChangedTimer = QTimer( self )

    # load settings
    loadSettings()

    # connections
    mViewModesGroup.triggered.connect(self.viewModes_triggered)
    mMdiArea.subWindowActivated.connect(self.mdiArea_subWindowActivated)
    parent.urlsDropped.connect(self.internal_urlsDropped)
    connect( MonkeyCore.projectsManager(), SIGNAL( currentProjectChanged( XUPProjectItem*, XUPProjectItem* ) ), self, SLOT( internal_currentProjectChanged( XUPProjectItem*, XUPProjectItem* ) ) )
    mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
    connect( MonkeyCore.multiToolBar(), SIGNAL( notifyChanges() ), self, SLOT( multitoolbar_notifyChanges() ) )


def eventFilter(self, object, event ):
    # get document
    if  object.isWidgetType() :
        document = qobject_cast<pAbstractChild*>( object )

        if  document and event.type() == QEvent.Close :
            event.ignore()
            closeDocument( document )
            return True



    return QFrame.eventFilter( object, event )


def updateGuiState(self, document ):
    # fix fucking flickering due to window activation change on application gain / lost focus.
    if  not document and currentDocument() :
        return


    # get child
    editor = document ? document.editor() : 0
    hasDocument = document
    hasEditor = editor
    modified = hasDocument ? document.isModified() : False
    print = hasDocument ? document.isPrintAvailable() : False
    undo = hasDocument ? document.isUndoAvailable() : False
    redo = hasDocument ? document.isRedoAvailable() : False
    copy = hasDocument ? document.isCopyAvailable() : False
    paste = hasDocument ? document.isPasteAvailable() : False
    go = hasDocument ? document.isGoToAvailable() : False
    moreThanOneDocument = mMdiArea.subWindowList().count() > 1

    # context toolbar
    mtb = MonkeyCore.multiToolBar()

    if  document :
        if  not mtb.contexts().contains( document.context() ) :
            tb = mtb.toolBar( document.context() )

            initMultiToolBar( tb )
            document.initializeContext( tb )


        mtb.setCurrentContext( document.context() )

    else:
        if  not mtb.contexts().contains( DEFAULT_CONTEXT ) :
            tb = mtb.toolBar( DEFAULT_CONTEXT )

            initMultiToolBar( tb )


        mtb.setCurrentContext( DEFAULT_CONTEXT )


    multitoolbar_notifyChanges()

    # update file menu
    MonkeyCore.menuBar().action( "mFile/mSave/aCurrent" ).setEnabled( modified )
    MonkeyCore.menuBar().action( "mFile/mSave/aAll" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().action( "mFile/mClose/aCurrent" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().action( "mFile/mClose/aAll" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().action( "mFile/aReload" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().action( "mFile/aSaveAsBackup" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().action( "mFile/aQuickPrint" ).setEnabled( print )
    MonkeyCore.menuBar().action( "mFile/aPrint" ).setEnabled( print )

    # update edit menu
    MonkeyCore.menuBar().action( "mEdit/aUndo" ).setEnabled( undo )
    MonkeyCore.menuBar().action( "mEdit/aRedo" ).setEnabled( redo )
    MonkeyCore.menuBar().action( "mEdit/aCut" ).setEnabled( copy )
    MonkeyCore.menuBar().action( "mEdit/aCopy" ).setEnabled( copy )
    MonkeyCore.menuBar().action( "mEdit/aPaste" ).setEnabled( paste )

    MonkeyCore.menuBar().action( "mEdit/aGoTo" ).setEnabled( go )
    MonkeyCore.menuBar().action( "mEdit/aExpandAbbreviation" ).setEnabled( hasDocument )
    MonkeyCore.menuBar().setMenuEnabled( MonkeyCore.menuBar().menu( "mEdit/mAllCommands" ), hasEditor )
    MonkeyCore.menuBar().setMenuEnabled( MonkeyCore.menuBar().menu( "mEdit/mBookmarks" ), hasEditor )

    # update view menu
    MonkeyCore.menuBar().action( "mView/aNext" ).setEnabled( moreThanOneDocument )
    MonkeyCore.menuBar().action( "mView/aPrevious" ).setEnabled( moreThanOneDocument )

    # update status bar
    MonkeyCore.statusBar().setModified( modified )
    MonkeyCore.statusBar().setEOLMode( editor ? editor.eolMode() : (QsciScintilla.EolMode)-1 )
    MonkeyCore.statusBar().setIndentMode( editor ? ( editor.indentationsUseTabs() ? 1 : 0 ) : -1 )
    MonkeyCore.statusBar().setCursorPosition( document ? document.cursorPosition() : QPoint( -1, -1 ) )

    # internal update
    if  hasDocument :
        QDir.setCurrent( document.path() )


def defaultContext(self):
    return DEFAULT_CONTEXT


def loadSettings(self):
    # restore tabs settings
    '''
    tabBar().setTabsHaveCloseButton( tabsHaveCloseButton() )
    tabBar().setTabsHaveShortcut( tabsHaveShortcut() )
    tabBar().setTabsElided( tabsElided() )
    tabBar().setTabsColor( tabsTextColor() )
    tabBar().setCurrentTabColor( currentTabTextColor() )
    '''

    mOpenedFileExplorer.setSortMode( pMonkeyStudio.openedFileSortingMode() )
    setDocumentMode( pMonkeyStudio.documentMode() )

    mtb = MonkeyCore.multiToolBar()

    for context in mtb.contexts():
        tb = mtb.toolBar( context )

        initMultiToolBar( tb )


    multitoolbar_notifyChanges()


def initMultiToolBar(self, tb ):
    if  pMonkeyStudio.showQuickFileAccess() :
        tb.insertAction( tb.actions().value( 0 ), MonkeyCore.workspace().dockWidget().comboBoxAction() )

    else:
        tb.removeAction( MonkeyCore.workspace().dockWidget().comboBoxAction() )



def dockWidget(self):
    return mOpenedFileExplorer


def fileWatcher(self):
    return mFileWatcher


def document(self, index ):
    window = mMdiArea.subWindowList().value( index )
    return qobject_cast<pAbstractChild*>( window )


def indexOfDocument(self, document ):
    return mMdiArea.subWindowList().indexOf( document )


def documents(self):
    QList<pAbstractChild*> documents

    for window in mMdiArea.subWindowList():
        documents << qobject_cast<pAbstractChild*>( window )


    return documents


def setCurrentDocument(self, document ):
    curDocument = currentDocument()

    if  curDocument != document :
        mMdiArea.setActiveSubWindow( document )



def currentDocument(self):
    window = mMdiArea.currentSubWindow()
    return qobject_cast<pAbstractChild*>( window )


def goToLine(self, fileName, pos, codec, selectionLength ):
    for window in mMdiArea.subWindowList():
        document = qobject_cast<pAbstractChild*>( window )

        if  pMonkeyStudio.isSameFile( document.filePath(), fileName ) :
            setCurrentDocument( document )
            document.goTo( pos, selectionLength )
            return



    document = openFile( fileName, codec )

    if  document :
        document.goTo( pos, selectionLength )



def closeDocument(self, document, showDialog ):
    if  showDialog and UISaveFiles.saveDocument( window(), document, False ) == UISaveFiles.bCancelClose :
        return


    # stop watching files
     file = document.filePath()

    if  QFileInfo( file ).isFile() and mFileWatcher.files().contains( file ) :
        mFileWatcher.removePath( file )


    # close document
    documentAboutToClose.emit( document )
    document.closeFile()

    if  document.testAttribute( Qt.WA_DeleteOnClose ) :
        document.deleteLater()

    else:
        unhandleDocument( document )



def documentMode(self):
    return mViewMode


def handleDocument(self, document ):
    # init document connections
    document.fileOpened.connect(self.document_fileOpened)
    document.contentChanged.connect(self.document_contentChanged)
    document.modifiedChanged.connect(self.document_modifiedChanged)
    document.fileClosed.connect(self.document_fileClosed)
    document.fileReloaded.connect(self.document_fileReloaded)
    # update file menu
    connect( document, SIGNAL( modifiedChanged( bool ) ), MonkeyCore.menuBar().action( "mFile/mSave/aCurrent" ), SLOT( setEnabled( bool ) ) )
    # update edit menu
    connect( document, SIGNAL( undoAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aUndo" ), SLOT( setEnabled( bool ) ) )
    connect( document, SIGNAL( redoAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aRedo" ), SLOT( setEnabled( bool ) ) )
    connect( document, SIGNAL( copyAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aCut" ), SLOT( setEnabled( bool ) ) )
    connect( document, SIGNAL( copyAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aCopy" ), SLOT( setEnabled( bool ) ) )
    connect( document, SIGNAL( pasteAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aPaste" ), SLOT( setEnabled( bool ) ) )
    # update status bar
    connect( document, SIGNAL( cursorPositionChanged(  QPoint& ) ), MonkeyCore.statusBar(), SLOT( setCursorPosition(  QPoint& ) ) )
    connect( document, SIGNAL( modifiedChanged( bool ) ), MonkeyCore.statusBar(), SLOT( setModified( bool ) ) )

    # add to workspace
    document.installEventFilter( self )
    mMdiArea.blockSignals( True )
    mMdiArea.addSubWindow( document )
    mMdiArea.blockSignals( False )


def unhandleDocument(self, document ):
     maximized = document.isMaximized()

    # init document connections
    disdocument.fileOpened.connect(self.document_fileOpened)
    disdocument.contentChanged.connect(self.document_contentChanged)
    disdocument.modifiedChanged.connect(self.document_modifiedChanged)
    disdocument.fileClosed.connect(self.document_fileClosed)
    disdocument.fileReloaded.connect(self.document_fileReloaded)
    # update file menu
    disconnect( document, SIGNAL( modifiedChanged( bool ) ), MonkeyCore.menuBar().action( "mFile/mSave/aCurrent" ), SLOT( setEnabled( bool ) ) )
    # update edit menu
    disconnect( document, SIGNAL( undoAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aUndo" ), SLOT( setEnabled( bool ) ) )
    disconnect( document, SIGNAL( redoAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aRedo" ), SLOT( setEnabled( bool ) ) )
    disconnect( document, SIGNAL( copyAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aCut" ), SLOT( setEnabled( bool ) ) )
    disconnect( document, SIGNAL( copyAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aCopy" ), SLOT( setEnabled( bool ) ) )
    disconnect( document, SIGNAL( pasteAvailableChanged( bool ) ), MonkeyCore.menuBar().action( "mEdit/aPaste" ), SLOT( setEnabled( bool ) ) )
    # update status bar
    disconnect( document, SIGNAL( cursorPositionChanged(  QPoint& ) ), MonkeyCore.statusBar(), SLOT( setCursorPosition(  QPoint& ) ) )
    disconnect( document, SIGNAL( modifiedChanged( bool ) ), MonkeyCore.statusBar(), SLOT( setModified( bool ) ) )

    # remove from workspace
    document.removeEventFilter( self )
    mMdiArea.removeSubWindow( document )
    document.hide()

    # maximize current window if needed
    if  maximized :
        doc = currentDocument()

        if  doc :
            doc.showMaximized()




def openFile(self, fileName, codec ):
    # if it not exists
    if  not QFile.exists( fileName ) or not QFileInfo( fileName ).isFile() :
        return 0


    # check if file is already opened
    for window in mMdiArea.subWindowList():
        document = qobject_cast<pAbstractChild*>( window )

        if  pMonkeyStudio.isSameFile( document.filePath(), fileName ) :
            setCurrentDocument( document )
            return document



    # get a document interface that can handle the file
    document = MonkeyCore.pluginsManager().documentForFileName( fileName )

    # open it with pChild instance if no document
    if  not document :
        document = pChild


    # make connection if worksapce don t contains self document
    if  not mMdiArea.subWindowList().contains( document ) :
        handleDocument( document )


    # open file
    if  not document.openFile( fileName, codec ) :
        MonkeyCore.messageManager().appendMessage( tr( "An error occur while opening self file: '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
        closeDocument( document )

        return 0


    document.showMaximized()
    mMdiArea.setActiveSubWindow( document )

    # update gui state
    #updateGuiState( document )

    # return child instance
    return document


def closeFile(self, filePath ):
    for window in mMdiArea.subWindowList():
        document = qobject_cast<pAbstractChild*>( window )

        if  pMonkeyStudio.isSameFile( document.filePath(), filePath ) :
            closeDocument( document )
            return




def closeCurrentDocument(self):
    document = currentDocument()

    if  document :
        closeDocument( document )



def closeAllDocuments(self):
    # try save documents
    button = UISaveFiles.saveDocuments( window(), documents(), False )

    # close all object, them
    if  button != UISaveFiles.bCancelClose :
        # stop watching files
        for window in mMdiArea.subWindowList():
            document = qobject_cast<pAbstractChild*>( window )
            closeDocument( document, False )


        return True

    else:
        return False; #not close IDE



def activateNextDocument(self):
    if  mViewMode == pWorkspace.NoTabs :
        document = currentDocument()
         curIndex = mOpenedFileExplorer.model().index( document )
        index = mOpenedFileExplorer.model().index( document )

        index = curIndex.sibling( curIndex.row() +1, curIndex.column() )

        if  not index.isValid() :
            index = curIndex.sibling( 0, curIndex.column() )


        document = mOpenedFileExplorer.model().document( index )

        setCurrentDocument( document )

    else:
        mMdiArea.activateNextSubWindow()



def activatePreviousDocument(self):
    if  mViewMode == pWorkspace.NoTabs :
        document = currentDocument()
         curIndex = mOpenedFileExplorer.model().index( document )
        index = mOpenedFileExplorer.model().index( document )

        index = curIndex.sibling( curIndex.row() -1, curIndex.column() )

        if  not index.isValid() :
            index = curIndex.sibling( mOpenedFileExplorer.model().rowCount() -1, curIndex.column() )


        document = mOpenedFileExplorer.model().document( index )

        setCurrentDocument( document )

    else:
        mMdiArea.activatePreviousSubWindow()



def focusEditor(self):
    document = currentDocument()

    if  document :
        document.setFocus()



def tile(self):
    mMdiArea.tileSubWindows()


def cascade(self):
    mMdiArea.cascadeSubWindows()


def minimize(self):
    setDocumentMode( pWorkspace.NoTabs )

    for window in mMdiArea.subWindowList():
        window.showMinimized()



def restore(self):
    setDocumentMode( pWorkspace.NoTabs )

    for window in mMdiArea.subWindowList():
        window.showNormal()



def setDocumentMode(self, mode ):
    if  mViewMode == mode :
        return


    document = mMdiArea.currentSubWindow()
    mViewMode = mode

    switch ( mViewMode )
    case pWorkspace.NoTabs:
        mMdiArea.setViewMode( QMdiArea.SubWindowView )
        break
    case pWorkspace.TopTabs:
        mMdiArea.setTabPosition( QTabWidget.North )
        mMdiArea.setViewMode( QMdiArea.TabbedView )
        break
    case pWorkspace.BottomTabs:
        mMdiArea.setTabPosition( QTabWidget.South )
        mMdiArea.setViewMode( QMdiArea.TabbedView )
        break
    case pWorkspace.LeftTabs:
        mMdiArea.setTabPosition( QTabWidget.West )
        mMdiArea.setViewMode( QMdiArea.TabbedView )
        break
    case pWorkspace.RightTabs:
        mMdiArea.setTabPosition( QTabWidget.East )
        mMdiArea.setViewMode( QMdiArea.TabbedView )
        break


    mOpenedFileExplorer.setVisible( mViewMode == pWorkspace.NoTabs )

    if  document and not document.isMaximized() :
        document.showMaximized()


    for action in mViewModesGroup.actions():
        if  action.data().toInt() == mViewMode :
            if  not action.isChecked() :
                action.setChecked( True )


            return




def createNewTextEditor(self):
    result = MkSFileDialog.getNewEditorFile( window() )

    # open open file dialog
    fileName = result[ "filename" ].toString()

    # return 0 if user cancel
    if  fileName.isEmpty() :
        return 0


    # close file if already open
    closeFile( fileName )

    # create/reset file
    QFile file( fileName )

    if  not file.open( QIODevice.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Can't create file '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
        return 0


    # reset file
    file.resize( 0 )
    file.close()

    if  result.value( "addtoproject", False ).toBool() :
        # add files to scope
        MonkeyCore.projectsManager().addFilesToScope( result[ "scope" ].value<XUPItem*>(), QStringList( fileName ) )


    # open file
    return openFile( fileName, result[ "codec" ].toString() )


def document_fileOpened(self):
    document = qobject_cast<pAbstractChild*>( sender() )

    if  QFileInfo( document.filePath() ).isFile() and not mFileWatcher.files().contains( document.filePath() ) :
        mFileWatcher.addPath( document.filePath() )


    documentOpened.emit( document )


def document_contentChanged(self):
    mContentChangedTimer.start( CONTENT_CHANGED_TIME_OUT )
    document = qobject_cast<pAbstractChild*>( sender() )

    # externally deleted files make the filewatcher to no longer watch them
     path = document.filePath()

    if  not mFileWatcher.files().contains( path ) :
        mFileWatcher.addPath( path )


    documentChanged.emit( document )


def document_modifiedChanged(self, modified ):
    document = qobject_cast<pAbstractChild*>( sender() )
    documentModifiedChanged.emit( document, modified )


def document_fileClosed(self):
    document = qobject_cast<pAbstractChild*>( sender() )
    mtb = MonkeyCore.multiToolBar()

    mtb.removeContext( document.context(), True )
    documentClosed.emit( document )


def document_fileReloaded(self):
    document = qobject_cast<pAbstractChild*>( sender() )
    documentReloaded.emit( document )


def contentChangedTimer_timeout(self):
    mContentChangedTimer.stop()
    MonkeyCore.fileManager().computeModifiedBuffers()


def multitoolbar_notifyChanges(self):
    mtb = MonkeyCore.multiToolBar()
    tb = mtb.currentToolBar()
    show = tb and not tb.actions().isEmpty()

    mtb.setVisible( show )


def viewModes_triggered(self, action ):
    setDocumentMode( (pWorkspace.ViewMode)action.data().toInt() )


def mdiArea_subWindowActivated(self, _document ):
    document = qobject_cast<pAbstractChild*>( _document )

    # update gui state
    updateGuiState( document )

    # file.emit changed
    currentDocumentChanged.emit( document )


def internal_urlsDropped(self, urls ):
    # create menu
    QMenu menu
    aof = menu.addAction( tr( "Open As &File" ) )
    aop = menu.addAction( tr( "Open As &Project" ) )
    menu.addSeparator()
    menu.addAction( tr( "Cancel" ) )

    # execute menu
    action = menu.exec( QCursor.pos() )

    # check triggered action
    if  action == aof :
        for url in urls:
            if  not url.toLocalFile().trimmed().isEmpty() :
                openFile( url.toLocalFile(), pMonkeyStudio.defaultCodec() )



    elif  action == aop :
        for url in urls:
            if  not url.toLocalFile().trimmed().isEmpty() :
                MonkeyCore.projectsManager().openProject( url.toLocalFile(), pMonkeyStudio.defaultCodec() )





def internal_currentProjectChanged(self, currentProject, previousProject ):
    # uninstall old commands
    if  previousProject :
        previousProject.uninstallCommands()

        dispreviousProject.installCommandRequested.connect(self.internal_projectInstallCommandRequested)
        dispreviousProject.uninstallCommandRequested.connect(self.internal_projectUninstallCommandRequested)


    # get pluginsmanager
    pm = MonkeyCore.pluginsManager()

    # set debugger and interpreter
    bp = currentProject ? currentProject.builder() : 0
    dp = currentProject ? currentProject.debugger() : 0
    ip = currentProject ? currentProject.interpreter() : 0

    pm.setCurrentBuilder( bp and not bp.neverEnable() ? bp : 0 )
    pm.setCurrentDebugger( dp and not dp.neverEnable() ? dp : 0 )
    pm.setCurrentInterpreter( ip and not ip.neverEnable() ? ip : 0 )

    # install commands
    if  currentProject :
        currentProject.installCommandRequested.connect(self.internal_projectInstallCommandRequested)
        currentProject.uninstallCommandRequested.connect(self.internal_projectUninstallCommandRequested)

        currentProject.installCommands()


    # update menu visibility
    MonkeyCore.mainWindow().menu_CustomAction_aboutToShow()


def internal_projectInstallCommandRequested(self, cmd, mnu ):
    # create action
    action = MonkeyCore.menuBar().action( QString( "%1/%2" ).arg( mnu ).arg( cmd.text() ) , cmd.text() )
    action.setStatusTip( cmd.text() )

    # set action custom data contain the command to execute
    action.setData( QVariant.fromValue( cmd ) )

    # connect to signal
    action.triggered.connect(self.internal_projectCustomActionTriggered)

    # update menu visibility
    MonkeyCore.mainWindow().menu_CustomAction_aboutToShow()


def internal_projectUninstallCommandRequested(self, cmd, mnu ):
    menu = MonkeyCore.menuBar().menu( mnu )

    for action in menu.actions():
        if  action.menu() :
            internal_projectUninstallCommandRequested( cmd, QString( "%1/%2" ).arg( mnu ).arg( action.menu().objectName() ) )

        elif  not action.isSeparator() and action.data().value<pCommand>() == cmd :
            delete action



    # update menu visibility
    MonkeyCore.mainWindow().menu_CustomAction_aboutToShow()


def internal_projectCustomActionTriggered(self):
    action = qobject_cast<QAction*>( sender() )

    if  action :
        cm = MonkeyCore.consoleManager()
        cmd = action.data().value<pCommand>()
        cmdsHash = cmd.userData().value<pCommandMap*>()
         cmds = cmdsHash ? cmdsHash.values() : pCommandList()

        # save project files
        if  pMonkeyStudio.saveFilesOnCustomAction() :
            fileSaveAll_triggered()


        # check that command to execute exists, ask to user if he want to choose another one
        if  cmd.targetExecution().isActive and cmd.project() :
            cmd = cm.processCommand( cm.getCommand( cmds, cmd.text() ) )
            fileName = cmd.project().filePath( cmd.command() )
            workDir = cmd.workingDirectory()

            # Try to correct command by asking user
            if  not QFile.exists( fileName ) :
                project = cmd.project()
                fileName = project.targetFilePath( cmd.targetExecution() )

                if  fileName.isEmpty() :
                    return


                 QFileInfo fileInfo( fileName )

                # if not exists ask user to select one
                if  not fileInfo.exists() :
                    QMessageBox.critical( window(), tr( "Executable file not found" ), tr( "Target '%1' does not exists" ).arg( fileName ) )
                    return


                if  not fileInfo.isExecutable() :
                    QMessageBox.critical( window(), tr( "Can't execute target" ), tr( "Target '%1' is not an executable" ).arg( fileName ) )
                    return


                # file found, it is executable. Correct command
                cmd.setCommand( fileName )
                cmd.setWorkingDirectory( fileInfo.absolutePath() )


            cm.addCommand( cmd )

            return


        # generate commands list
        mCmds = cm.recursiveCommandList( cmds, cm.getCommand( cmds, cmd.text() ) )

        # the first one must not be skipped on last error
        if  not mCmds.isEmpty() :
            mCmds.first().setSkipOnError( False )


        # send command to consolemanager
        cm.addCommands( mCmds )



# file menu
def fileNew_triggered(self):
    UITemplatesWizard wizard( self )
    wizard.setType( "Files" )
    wizard.exec()


def fileOpen_triggered(self):
     mFilters = pMonkeyStudio.availableFilesFilters(); # get available filters

    # show filedialog to user
    result = MkSFileDialog.getOpenFileNames( window(), tr( "Choose the file(s) to open" ), QDir.currentPath(), mFilters, True, False )

    # open open file dialog
     fileNames = result[ "filenames" ].toStringList()

    # return 0 if user cancel
    if  fileNames.isEmpty() :
        return


    # for each entry, file
    for file in fileNames:
        if  openFile( file, result[ "codec" ].toString() ) :
            # append file to recents
            MonkeyCore.recentsManager().addRecentFile( file )

        else:
            # remove it from recents files
            MonkeyCore.recentsManager().removeRecentFile( file )




def fileSessionSave_triggered(self):
    QStringList files, projects

    # files
    for window in mMdiArea.subWindowList():
        document = qobject_cast<pAbstractChild*>( window )
        files << document.filePath()


    MonkeyCore.settings().setValue( "Session/Files", files )

    # projects
    for project in MonkeyCore.projectsManager().topLevelProjects():
        projects << project.fileName()


    MonkeyCore.settings().setValue( "Session/Projects", projects )


def fileSessionRestore_triggered(self):
    # restore files
    for file in MonkeyCore.settings(:.value( "Session/Files", QStringList() ).toStringList() )
        if ( not openFile( file, pMonkeyStudio.defaultCodec() ) ) # remove it from recents files
            MonkeyCore.recentsManager().removeRecentFile( file )



    # restore projects
    for project in MonkeyCore.settings(:.value( "Session/Projects", QStringList() ).toStringList() )
        if ( not MonkeyCore.projectsManager().openProject( project, pMonkeyStudio.defaultCodec() ) ) # remove it from recents projects
            MonkeyCore.recentsManager().removeRecentProject( project )




def fileSaveCurrent_triggered(self):
    document = currentDocument()

    if  document :
         fn = document.filePath()
        mFileWatcher.removePath( fn )
        document.saveFile()
        mFileWatcher.addPath( fn )



def fileSaveAll_triggered(self):
    for window in mMdiArea.subWindowList():
        document = qobject_cast<pAbstractChild*>( window )
         fn = document.filePath()
        mFileWatcher.removePath( fn )
        document.saveFile()
        mFileWatcher.addPath( fn )



def fileCloseCurrent_triggered(self):
    closeCurrentDocument()


def fileCloseAll_triggered(self):
    closeAllDocuments()


def fileReload_triggered(self):
    document = currentDocument()

    if  document :
        button = QMessageBox.Yes

        if  document.isModified() :
            button = QMessageBox.question( self, tr( "Confirmation needed..." ), tr( "The file has been modified, anyway ?" ), QMessageBox.Yes | QMessageBox.No, QMessageBox.No )


        if  button == QMessageBox.Yes :
            ''' fileName = document.filePath()
             codec = document.textCodec()

            closeDocument( document )
            openFile( fileName, codec );'''
            document.reload()




def fileSaveAsBackup_triggered(self):
    document = currentDocument()

    if  document :
         fileName = pMonkeyStudio.getSaveFileName( tr( "Choose a filename to backup your file" ), document.fileName(), QString.null, self )

        if  not fileName.isEmpty() :
            document.backupFileAs( fileName )




def fileQuickPrint_triggered(self):
    document = currentDocument()

    if  document :
        document.quickPrintFile()



def filePrint_triggered(self):
    document = currentDocument()

    if  document :
        document.printFile()



def fileExit_triggered(self):
    window().close()


# edit menu
def editSettings_triggered(self):
    UISettings.instance( self ).exec()


def editTranslations_triggered(self):
     locale = TranslationDialog.getLocale( MonkeyCore.translationsManager(), self )

    if  not locale.isEmpty() :
        MonkeyCore.settings().setValue( "Translations/Locale", locale )
        MonkeyCore.settings().setValue( "Translations/Accepted", True )
        MonkeyCore.translationsManager().setCurrentLocale( locale )
        MonkeyCore.translationsManager().reloadTranslations()



def editUndo_triggered(self):
    document = currentDocument()

    if  document :
        document.undo()



def editRedo_triggered(self):
    document = currentDocument()

    if  document :
        document.redo()



def editCut_triggered(self):
    document = currentDocument()

    if  document :
        document.cut()



def editCopy_triggered(self):
    document = currentDocument()

    if  document :
        document.copy()



def editPaste_triggered(self):
    document = currentDocument()

    if  document :
        document.paste()



def editSearch_triggered(self):
    document = currentDocument()

    if  document and not document.editor() :
        document.invokeSearch()



def editGoTo_triggered(self):
    document = currentDocument()

    if  document :
        document.goTo()



def editExpandAbbreviation_triggered(self):
    document = currentDocument()

    if  document :
        MonkeyCore.abbreviationsManager().expandMacro( document.editor() )



def editPrepareAPIs_triggered(self):
    pMonkeyStudio.prepareAPIs()


# help menu
def helpAboutApplication_triggered(self):
    dlg = UIAbout( self )
    dlg.open()


def helpAboutQt_triggered(self):
    qApp.aboutQt()


#ifdef __COVERAGESCANNER__
def helpTestReport_triggered(self):
    UITestReport.instance( self ).exec()

#endif
