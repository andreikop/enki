"""
workspace --- Open documents and manage it
==========================================

Terminology:

Workspace - main working area, where documents are placed.

Document - widget on workspace. Here is examples of documents:

* Textual editor
* QtDesigner (probably in the future)
* QtAssistant (probably in the future)

Document classes are herited from :class:`mks.core.abstractdocument.AbstractDocument`

:class:`mks.core.workspace.Workspace`
"""

import os.path
import sys

from PyQt4 import uic

from PyQt4.QtGui import QApplication, \
                        QDialog, QDialogButtonBox, \
                        QFileDialog, \
                        QListWidgetItem, \
                        QMessageBox, \
                        QStackedWidget
from PyQt4.QtCore import pyqtSignal, \
                         QEvent, \
                         Qt

from mks.core.core import core, DATA_FILES_PATH
import mks.core.openedfilesmodel
import mks.core.abstractdocument


class _UISaveFiles(QDialog):
    """Save files dialog.
    Shows checkable list of not saved files.
    """
    def __init__(self, workspace, documents):
        super(_UISaveFiles, self).__init__(workspace)
        self.cancelled = False
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/SaveFiles.ui'), self)
        self.buttonBox.clicked.connect(self._onButtonClicked)
        
        self._itemToDocument = {}
        for document in documents:
            item = QListWidgetItem( document.fileName(), self.listWidget )
            if document.filePath() is not None:
                item.setToolTip( document.filePath() )
            item.setCheckState( Qt.Checked )
            self._itemToDocument[item] = document
        self.buttonBox.button(self.buttonBox.Cancel).setText(self.tr('Cancel Close'))
        self.buttonBox.button(self.buttonBox.Save).setText(self.tr('Save checked'))
    
    def showEvent(self, event):
        """Show event handler, moves focus to the Cancel button
        """
        self.setFocus()
        self.buttonBox.button(QDialogButtonBox.Cancel).setFocus()
        super(_UISaveFiles, self).showEvent(event)
    
    def _onButtonClicked(self, button):
        """Button click handler.
        Saves files, if necessary, accepts or rejects dialog
        """
        stButtton = self.buttonBox.standardButton(button)
        if stButtton == QDialogButtonBox.Save:
            for i in range(self.listWidget.count()):
                if  self.listWidget.item( i ).checkState() != Qt.Unchecked:
                    self._itemToDocument[self.listWidget.item(i)].saveFile()
            self.accept()
        elif stButtton == QDialogButtonBox.Cancel:
            self.reject()
        elif stButtton == QDialogButtonBox.Discard:
            self.accept()
        else:
            assert 0

class Workspace(QStackedWidget):
    """
    Class manages set of opened documents, allows to open new file
    
    instance is accessible as: ::
    
        from mks.core.core import core
        core.workspace()
    
    """
        
    documentOpened = pyqtSignal(mks.core.abstractdocument.AbstractDocument)
    """
    documentOpened(:class:`mks.core.abstractdocument.AbstractDocument`)
    
    **Signal** emitted, when document has been created, i.e. textual file opened, 
    or some other document added to workspace
    """
    
    documentClosed = pyqtSignal(mks.core.abstractdocument.AbstractDocument)
    """
    documentClosed(:class:`mks.core.abstractdocument.AbstractDocument`)
    
    **Signal** emitted, when document was closed
    """
        
    currentDocumentChanged = pyqtSignal(mks.core.abstractdocument.AbstractDocument,
                                        mks.core.abstractdocument.AbstractDocument)
    """
    currentDocumentChanged(:class:`mks.core.abstractdocument.AbstractDocument` old, 
    :class:`mks.core.abstractdocument.AbstractDocument` current)
    
    **Signal** emitted, when current document changed, i.e. user selected another document, 
    new document opened, current closed
    """
        
    def __init__(self, mainWindow):
        """ list of opened documents as it is displayed in the Opened Files Explorer. 
        List accessed and modified by mks.core.openedfilesmodel.OpenedFileModel class
        """
        QStackedWidget.__init__(self, mainWindow)
        self.sortedDocuments = []  # not protected, because available for OpenedFileModel
        self._oldCurrentDocument = None
        self._textEditorClass = None
        
        # create opened files explorer
        # openedFileExplorer is not protected, because it is available for OpenedFileModel
        self.openedFileExplorer = mks.core.openedfilesmodel.OpenedFileExplorer(self)
        lefttb = mainWindow.dockToolBar( Qt.LeftToolBarArea )
        lefttb.addDockWidget( self.openedFileExplorer)
        
        self.currentChanged.connect(self._onStackedLayoutIndexChanged)
        
        self.currentDocumentChanged.connect(self._updateMainWindowTitle)
        core.actionModel().action( "mFile/aOpen" ).triggered.connect(self._onFileOpenTriggered)
        core.actionModel().action( "mFile/mReload/aCurrent" ).triggered.connect(self._onFileReloadTriggered)
        core.actionModel().action( "mFile/mReload/aAll" ).triggered.connect(self._onFileReloadAllTriggered)
        core.actionModel().action( "mFile/aNew" ).triggered.connect(lambda : self.createEmptyNotSavedDocument(None))
        core.actionModel().action( "mFile/mClose/aCurrent" ).triggered.connect(self._onCloseCurrentDocument)
        core.actionModel().action( "mFile/mClose/aAll" ).triggered.connect(self.closeAllDocuments)
    
        core.actionModel().action( "mFile/mSave/aCurrent" ).triggered.connect(self._onFileSaveCurrentTriggered)
        core.actionModel().action( "mFile/mSave/aAll" ).triggered.connect(self._onFileSaveAllTriggered)
        
        core.actionModel().action( "mNavigation/aNext" ).triggered.connect(self._activateNextDocument)
        core.actionModel().action( "mNavigation/aPrevious" ).triggered.connect(self._activatePreviousDocument)
        
        core.actionModel().action( "mNavigation/aFocusCurrentDocument" ).triggered.connect(self.focusCurrentDocument)
        core.actionModel().action( "mNavigation/aGoto" ).triggered.connect(self._onGotoTriggered)
    
    def _mainWindow(self):
        """Get mainWindow instance
        """
        return self.parentWidget().parentWidget()
    
    def documentForPath(self, filePath):
        """Find document by it's file path.
        Raises ValueError, if document hasn't been found
        """
        for document in self.openedDocuments():
            if document.filePath() is not None and \
               document.filePath() == filePath:
                return document
        else:
            raise ValueError("Document not found for" + filePath)

    def _updateMainWindowTitle(self):
        """Update window title after document or it's modified state has been changed
        """
        document = self.currentDocument()
        if document:
            name = document.fileName()
            if document.isModified():
                name += '*'
        else:
            name = self._mainWindow().defaultTitle()
        self._mainWindow().setWindowTitle(name)

    def setTextEditorClass(self, newEditorClass):
        """Set text editor, which is used for open textual documents.
        New editor would be used for newly opened textual documents.
        
        newEditorClass is class, herited from :class:`mks.core.abstractdocument.AbstractDocument`
        """
        self._textEditorClass = newEditorClass
    
    def eventFilter( self, object, event ):
        """NOT AN API function
        
        Handler for QObject events of children
        """
        if  object.isWidgetType() :
            document = object
            if  event.type() == QEvent.Close:
                event.ignore()
                self.closeDocument( document )
                return True
        
        return super(Workspace, self).eventFilter(object, event )
    
    def _onStackedLayoutIndexChanged(self, index):
        """Handler of change of current document in the stacked layout.
        Only calls _onCurrentDocumentChanged(document)
        """
        document = self.widget(index)
        self._onCurrentDocumentChanged(document)
    
    def _onCurrentDocumentChanged( self, document ):
        """Connect/disconnect document signals and update enabled/disabled 
        state of the actions
        """
        
        if document is None and self.count():  # just lost focus, no real change
            return
        if document == self._oldCurrentDocument:  # just recieved focus, no real change
            return
        
        if document is not None:
            self.setFocusProxy(document)
        
        if self._oldCurrentDocument is not None:
            pass
        
        # update file menu
        core.actionModel().action( "mFile/mSave/aCurrent" ).setEnabled( document is not None and \
                                                                            (document.isModified() or 
                                                                             document.isNeverSaved()))
        core.actionModel().action( "mFile/mSave/aAll" ).setEnabled( document is not None)
        core.actionModel().action( "mFile/mClose/aCurrent" ).setEnabled( document is not None)
        core.actionModel().action( "mFile/mClose/aAll" ).setEnabled( document is not None)
        core.actionModel().action( "mNavigation/aFocusCurrentDocument" ).setEnabled( document is not None)
        core.actionModel().action( "mNavigation/aGoto" ).setEnabled( document is not None)
        ''' TODO close all
        core.actionModel().action( "mFile/mClose/aAll" ).setEnabled( document )
        '''
        core.actionModel().action( "mFile/mReload/aCurrent" ).setEnabled( document is not None )
        core.actionModel().action( "mFile/mReload/aAll" ).setEnabled( document is not None )
        ''' TODO save as backup, quick print, print
        core.actionModel().action( "mFile/aSaveAsBackup" ).setEnabled( document )
        core.actionModel().action( "mFile/aQuickPrint" ).setEnabled( print_ )
        core.actionModel().action( "mFile/aPrint" ).setEnabled( print_ )
        
        # update edit menu
        core.actionModel().action( "mEdit/aExpandAbbreviation" ).setEnabled( document )
        '''
        
        # update view menu
        moreThanOneDocument = self.count() > 1
        core.actionModel().action( "mNavigation/aNext" ).setEnabled( moreThanOneDocument )
        core.actionModel().action( "mNavigation/aPrevious" ).setEnabled( moreThanOneDocument )
        
        # internal update
        if  document and document.filePath() is not None and \
            os.path.exists(os.path.dirname(document.filePath())):
            try:
                os.chdir( os.path.dirname(document.filePath()) )
            except OSError, ex:  # directory might be deleted
                print >> sys.stderr, 'Failed to change directory:', str(ex)
        
        self.currentDocumentChanged.emit(self._oldCurrentDocument, document)
        self._oldCurrentDocument = document
        
    def setCurrentDocument( self, document ):
        """Select active (focused and visible) document form list of opened documents
        """
        self.setCurrentWidget( document )
    
    def currentDocument(self):
        """Returns currently active (focused) document. None, if no documents are opened
        """
        return self.currentWidget()
    
    def goToLine(self, filePath, line, column, selectionLength):
        """Open file, activate it, and go to specified line.
        
        selectionLength specifies, how much characters should be selected
        """
        # TODO use openFile instead?
        for document in self.openedDocuments():
            if document.filePath() is not None:
                if os.path.realpath(document.filePath()) == \
                   os.path.realpath(filePath):
                    self.setCurrentDocument(document)
                    break
        else:
            document = self.openFile(filePath)

        if  document :
            document.goTo(line, column, selectionLength )
    
    def closeDocument( self, document, showDialog=True):
        """Close opened file, remove document from workspace and delete the widget
        
        If showDialog is True and file is modified, dialog will be shown
        """
        
        if showDialog and document.isModified():
            if _UISaveFiles(self._mainWindow(), [document]).exec_() == QDialog.Rejected:
                return
        
        if len(self.sortedDocuments) > 1:  # not the last document
            if document == self.sortedDocuments[-1]:  # the last document
                self._activatePreviousDocument()
            else:  # not the last
                self._activateNextDocument()
        
        self.documentClosed.emit( document )
        # close document
        self._unhandleDocument( document )
        document.deleteLater()

    def _handleDocument( self, document ):
        """Add document to the workspace. Connect signals
        """
        # update file menu
        document.modifiedChanged.connect(core.actionModel().action( "mFile/mSave/aCurrent" ).setEnabled)
        document.modifiedChanged.connect(self._updateMainWindowTitle)
        
        # add to workspace
        document.installEventFilter( self )
        
        self.addWidget( document )
        self.setCurrentWidget( document )
    
    def _unhandleDocument( self, document ):
        """Remove document from the workspace. Disconnect signals
        """
        document.modifiedChanged.disconnect(core.actionModel().action( "mFile/mSave/aCurrent" ).setEnabled)
        # update edit menu

        # remove from workspace
        document.removeEventFilter( self )
        self.removeWidget(document)
        
    def openFile(self, filePath):
        """Open named file using suitable plugin, or textual editor, if other suitable editor not found.
        
        Returns document, if opened, None otherwise
        
        Opens modal dialog, if failed to open the file
        """
        # Close 'untitled'
        if len(self.openedDocuments()) == 1 and \
           self.openedDocuments()[0].fileName() == 'untitled' and \
           not self.openedDocuments()[0].filePath() and \
           not self.openedDocuments()[0].text() and \
           not self.openedDocuments()[0].isModified():
            self.closeDocument(self.openedDocuments()[0])        

        # check if file is already opened
        for document in self.sortedDocuments:
            if os.path.isfile(filePath) and \
               document.filePath() is not None and \
               os.path.isfile(document.filePath()) and \
               os.path.samefile( document.filePath(), filePath ) :
                self.setCurrentDocument( document )
                return document
        
        documentType = None  # TODO detect document type, choose editor
        
        # select editor for the file
        if not documentType :
            documentType = self._textEditorClass
        
        if not documentType:
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 self.tr("Don't have any editor for open %s. Is any text editor plugin enabled?" % 
                                         filePath))
            return None
        
        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document = documentType(self, filePath)
        except IOError as ex:
            QMessageBox.critical(None,
                                 self.tr("Failed to open file"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()
        
        self.documentOpened.emit( document )
        
        
        self._handleDocument( document )
        
        if not os.access(filePath, os.W_OK):
            core.messageManager().appendMessage( \
                        self.tr( "File '%s' is not writable" % filePath), 4000) # todo fix
        
        return document
    
    def createEmptyNotSavedDocument(self, filePath=None):
        """Create empty not saved document.
        Used on startup, if no file was specified, and after File->New file has been triggered
        """
        document = self._textEditorClass(self, filePath, True)
        self.documentOpened.emit( document )
        self._handleDocument( document )
        return document
        
    
    def _onCloseCurrentDocument(self):
        """Handler of File->Close->Current triggered
        """
        document = self.currentWidget()
        assert(document is not None)
        self.closeDocument( document )

    def openedDocuments(self):
        """Get list of opened documents (:class:`mks.core.abstractdocument.AbstractDocument` instances)
        """
        return self.sortedDocuments
    
    def closeAllDocuments(self):
        """Close all documents
        
        If there are not saved documents, dialog will be shown.
        
        Handler of File->Close->All
        
        Returns True, if all files had been closed, and False, if save dialog rejected
        """
        modifiedDocuments = filter(lambda d: d.isModified(), self.openedDocuments())
        if modifiedDocuments:
            if (_UISaveFiles( self, modifiedDocuments).exec_() == QDialog.Rejected):
                return False #do not close IDE

        for document in self.openedDocuments()[::-1]:
            self.closeDocument(document, False)

        return True
        
    def _activateNextDocument(self):
        """Handler of View->Next triggered
        """
        curIndex = self.sortedDocuments.index(self.currentDocument())
        nextIndex = (curIndex + 1) % len(self.sortedDocuments)
        self.setCurrentDocument( self.sortedDocuments[nextIndex] )
    
    def _activatePreviousDocument(self):
        """Handler of View->Previous triggered
        """
        curIndex = self.sortedDocuments.index(self.currentDocument())
        prevIndex = (curIndex - 1 + len(self.sortedDocuments)) % len(self.sortedDocuments)
        self.setCurrentDocument( self.sortedDocuments[prevIndex] )
    
    def focusCurrentDocument(self):
        """Set focus (cursor) to current document.
        
        Used if user has finished work with some dialog, and, probably, want's to edit text
        """
        document = self.currentDocument()
        if  document :
            document.setFocus()
       
    def _onFileOpenTriggered(self):
        """Handler of File->Open
        """
        fileNames = QFileDialog.getOpenFileNames( self.window(), self.tr( "Choose the file(s) to open" ))
                
        for path in fileNames:
            self.openFile(path)
    
    def _onFileSaveCurrentTriggered(self):
        """Handler of File->Save->Current
        """
        return self.currentDocument().saveFile()
    
    def _onFileSaveAllTriggered(self):
        """Handler of File->Save->All
        """
        for document in self.openedDocuments():
            document.saveFile()
        
    def _reloadDocument(self, document):
        """Reload the document contents
        """
        if  document.isModified():
            template = self.tr( "The file <b>%s</b> has been modified by you.\n"
                                "Do you want to reload and discard changes?" )
            text = template % document.fileName()
            ret = QMessageBox.question(self, self.tr( "Reload file..." ), text,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret != QMessageBox.Yes:
                return

        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document.reload()
        except IOError as ex:
            #TODO replace with messageManager ?
            QMessageBox.critical(None,
                                 self.tr("File not reloaded"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()
        
    def _onFileReloadTriggered(self):
        """Handler of File->Reload->Current
        """
        document = self.currentDocument()
        if  document is not None:
            self._reloadDocument(document)
    
    def _onFileReloadAllTriggered(self):
        """Handler of File->Reload->All
        """
        for document in self.openedDocuments():
            if not document.isExternallyRemoved():
                self._reloadDocument(document)
    
    def _onGotoTriggered(self):
        """Handler of Navigation->Goto
        """
        self.currentDocument().invokeGoTo()

'''TODO old code. Restore it partially, delete partially

    # document about to close
    documentAboutToClose = pyqtSignal(AbstractDocument)

    """A file has been closed. When signal emitted, document pointer is valid,
    document not yet removed from workspace

    # a file has been reloaded
    documentReloaded = pyqtSignal(AbstractDocument)

    # a file have changed
    documentChanged = pyqtSignal(AbstractDocument)
    
    buffersChanged = pyqtSignal(dict) # {file path : file contents}

    def __init__
        self.mContentChangedTimer = QTimer( self )
        
        # load settings
        self.loadSettings()

        # connections
        mViewModesGroup.triggered.connect(self.viewModes_triggered)
        parent.urlsDropped.connect(self.internal_urlsDropped)
        MonkeyCore.projectsManager().currentProjectChanged.connect(self.internal_currentProjectChanged)
        self.mContentChangedTimer.timeout.connect(self.contentChangedTimer_timeout)
        
    def fileSessionSave_triggered(self):
        files = []
        projects = []

        # files
        for window in self.mdiArea.subWindowList():
            document = window
            files.append(document.filePath())

        core.settings().setValue( "Session/Files", files )
        
        # projects
        for project in core.projectsManager().topLevelProjects():
            projects.append(project.fileName())

        core.settings().setValue( "Session/Projects", projectss )

    def fileSessionRestore_triggered(self):
        # restore files
        for file in core.settings().value("Session/Files", [] ).toStringList():
            if not self.openFile( file, mks.monkeystudio.defaultCodec() ): # remove it from recents files
                core.recentsManager().removeRecentFile( file )
        
        # restore projects
        for project in core.settings().value( "Session/Projects", [] ).toStringList():
            if not core.projectsManager().openProject( project, mks.monkeystudio.defaultCodec() ): # remove it from recents projects
                core.recentsManager().removeRecentProject( project )
    
    
    def createNewTextEditor(self):
        result = MkSFileDialog.getNewEditorFile( window() )

        # open open file dialog
        fileName = result[ "filename" ].toString()
        
        # return 0 if user cancel
        if  fileName.isEmpty() :
            return 0
        
        # close file if already open
        self.closeFile( fileName )

        # create/reset file
        file = QFile ( fileName )

        if  not file.open( QIODevice.WriteOnly ) :
            core.messageManager().appendMessage(self.tr( "Can't create file '%1'" ).arg( QFileInfo( fileName ).fileName() ) )
            return 0

        # reset file
        file.resize( 0 )
        file.close()

        if  result.value( "addtoproject", e ).toBool() :
            # add files to scope
            core.projectsManager().addFilesToScope( result[ "scope" ].value(XUPItem), [fileName] )
        
        # open file
        return self.openFile( fileName, result[ "encoding" ].toString() )

    def document_contentChanged(self):
        self.mContentChangedTimer.start( CONTENT_CHANGED_TIME_OUT )
        document = self.sender() # signal sender
        self.documentChanged.emit( document )
    
    def document_fileClosed(self):
        document = self.sender()
        self.documentClosed.emit( document )


    def document_fileReloaded(self):
        document = self.sender()
        self.documentReloaded.emit( document )

    def contentChangedTimer_timeout(self):
        self.mContentChangedTimer.stop()
        
        entries = {}
        
        for document in self.documents():
            if  document.isModified() :
                entries[ document.filePath() ] = document.text()

        self.buffersChanged.emit( entries )
    
    def viewModes_triggered(self, action ):
        self.setDocumentMode( action.data().toInt() )
    
    def internal_urlsDropped(self, urls ):
        # create menu
        menu = QMenu()
        aof = menu.addAction(self.tr( "Open As &File" ) )
        aop = menu.addAction(self.tr( "Open As &Project" ) )
        menu.addSeparator()
        menu.addAction(self.tr( "Cancel" ) )

        # execute menu
        action = menu.exec_( QCursor.pos() )

        # check triggered action
        if action == aof :
            for url in s:
                if  not url.toLocalFile().trimmed().isEmpty() :
                    self.openFile( url.toLocalFile(), c() )
        elif action == aop :
            for url in s:
                if  not url.toLocalFile().trimmed().isEmpty() :
                    core.projectsManager().openProject( url.toLocalFile(), c() )


    def internal_currentProjectChanged(self, currentProject, previousProject ):
        # uninstall old commands
        if  previousProject :
            previousProject.uninstallCommands()
            disconnect( previousProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            disconnect( previousProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )
    
        # get pluginsmanager
        pm = core.pluginsManager()
        
        # set debugger and interpreter
        bp = currentProject ? currentProject.builder() : 0
        dp = currentProject ? currentProject.debugger() : 0
        ip = currentProject ? currentProject.interpreter() : 0
        
        pm.setCurrentBuilder( bp and not bp.neverEnable() ? bp : 0 )
        pm.setCurrentDebugger( dp and not dp.neverEnable() ? dp : 0 )
        pm.setCurrentInterpreter( ip and not ip.neverEnable() ? ip : 0 )
        
        # install commands
        if  currentProject :
            connect( currentProject, L( installCommandRequested(  pCommand&, & ) ), s, T( internal_projectInstallCommandRequested(  pCommand&, & ) ) )
            connect( currentProject, L( uninstallCommandRequested(  pCommand&, & ) ), s, T( internal_projectUninstallCommandRequested(  pCommand&, & ) ) )

            currentProject.installCommands()

    def internal_projectInstallCommandRequested(self, cmd, mnu ):
        # create action
        action = core.actionModel().action( QString( "%1/%2" ).arg( mnu ).arg( cmd.text() ) , d.text() )
        action.setStatusTip( cmd.text() )

        # set action custom data contain the command to execute
        action.setData( QVariant.fromValue( cmd ) )
        
        # connect to signal
        action.triggered().connect(s.internal_projectCustomActionTriggered())
        
        # update menu visibility
        self._mainWindow().menu_CustomAction_aboutToShow()


    def internal_projectUninstallCommandRequested(self, cmd, mnu ):
        menu = core.actionModel().menu( mnu )
        
        for action in u.actions():
            if  action.menu() :
                internal_projectUninstallCommandRequested( cmd, QString( "%1/%2" ).arg( mnu ).arg( action.menu().objectName() ) )
            elif  not action.isSeparator() and action.data().value(pCommand) == cmd :
                delete action

        # update menu visibility
        self._mainWindow().menu_CustomAction_aboutToShow()

    def internal_projectCustomActionTriggered(self):
        action = self.sender()

        if  action :
            cm = core.consoleManager()
            cmd = action.data().value<pCommand>()
            cmdsHash = cmd.userData().value<pCommandMap*>()
            cmds = cmdsHash ? cmdsHash.values() : pCommandList()

            # save project files
            if  mks.monkeystudio.saveFilesOnCustomAction() :
                fileSaveAll_triggered()


            # check that command to execute exists, ask to user if he want to choose another one
            if  cmd.targetExecution().isActive and cmd.project() :
                d = cm.processCommand( cm.getCommand( cmds, d.text() ) )
                fileName = cmd.project().filePath( cmd.command() )
                workDir = cmd.workingDirectory()

                # Try to correct command by asking user
                if  not QFile.exists( fileName ) :
                    project = cmd.project()
                    e = project.targetFilePath( cmd.targetExecution() )

                    if  fileName.isEmpty() :
                        return


                     QFileInfo fileInfo( fileName )

                    # if not exists ask user to select one
                    if  not fileInfo.exists() :
                        QMessageBox.critical( window(), r( "Executable file not found" ), r( "Target '%1' does not exists" ).arg( fileName ) )
                        return


                    if  not fileInfo.isExecutable() :
                        QMessageBox.critical( window(), r( "Can't execute target" ), r( "Target '%1' is not an executable" ).arg( fileName ) )
                        return


                    # file found, it is executable. Correct command
                    cmd.setCommand( fileName )
                    cmd.setWorkingDirectory( fileInfo.absolutePath() )


                cm.addCommand( cmd )

                return


            # generate commands list
            mCmds = cm.recursiveCommandList( cmds, m.getCommand( cmds, d.text() ) )

            # the first one must not be skipped on last error
            if  not mCmds.isEmpty() :
                mCmds.first().setSkipOnError( False )


            # send command to consolemanager
            cm.addCommands( mCmds )


    # file menu
    def fileNew_triggered(self):
        wizard = UITemplatesWizard ( self )
        wizard.setType( "Files" )
        wizard.exec_()

    def fileSaveAsBackup_triggered(self):
        document = self.currentDocument()

        if  document :
            fileName = mks.monkeystudio.getSaveFileName(self.tr( "Choose a filename to backup your file" ), document.fileName(), '', self )

            if  not fileName.isEmpty() :
                document.backupFileAs( fileName )

    def fileQuickPrint_triggered(self):
        document = self.currentDocument()

        if  document :
            document.quickPrintFile()

    def filePrint_triggered(self):
        document = self.currentDocument()

        if  document :
            document.printFile()


    def editTranslations_triggered(self):
        locale = TranslationDialog.getLocale( core.translationsManager(), self )

        if  not locale.isEmpty() :
            core.settings().setValue( "Translations/Locale", locale )
            core.settings().setValue( "Translations/Accepted", True )
            core.translationsManager().setCurrentLocale( locale )
            core.translationsManager().reloadTranslations()


    def editExpandAbbreviation_triggered(self):
        document = self.currentDocument()

        if  document :
            core.abbreviationsManager().expandMacro( document.editor() )



    def editPrepareAPIs_triggered(self):
        mks.monkeystudio.prepareAPIs()

    # help menu
    def helpAboutApplication_triggered(self):
        dlg = UIAbout( self )
        dlg.open()
    '''
