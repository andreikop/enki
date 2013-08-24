"""
workspace_actions --- Workspace actons, such as "Open file", "Next document", ..
================================================================================
"""

import os.path
import stat

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QApplication, QFileDialog, QInputDialog, QMessageBox

from enki.core.core import core

class Plugin(QObject):
    def __init__(self):
        QObject.__init__(self)
        
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)
        core.workspace().documentOpened.connect(self._onDocumentOpenedOrClosed)
        core.workspace().documentClosed.connect(self._onDocumentOpenedOrClosed)

        core.actionManager().action( "mFile/aOpen" ).triggered.connect(self._onFileOpenTriggered)
        core.actionManager().action( "mFile/mReload/aCurrent" ).triggered.connect(self._onFileReloadTriggered)
        core.actionManager().action( "mFile/mReload/aAll" ).triggered.connect(self._onFileReloadAllTriggered)
        core.actionManager().action( "mFile/aNew" ).triggered.connect(lambda : core.workspace().createEmptyNotSavedDocument(None))
        core.actionManager().action( "mFile/mClose/aCurrent" ).triggered.connect(self._onCloseCurrentDocument)
        core.actionManager().action( "mFile/mClose/aAll" ).triggered.connect(core.workspace().closeAllDocuments)
    
        core.actionManager().action( "mFile/mSave/aCurrent" ).triggered.connect(self._onFileSaveCurrentTriggered)
        core.actionManager().action( "mFile/mSave/aAll" ).triggered.connect(self._onFileSaveAllTriggered)
        core.actionManager().action( "mFile/mSave/aSaveAs" ).triggered.connect(self._onFileSaveAsTriggered)
        
        core.actionManager().action('mFile/mFileSystem').menu().aboutToShow.connect(self._onFsMenuAboutToShow)
        core.actionManager().action( "mFile/mFileSystem/aRename" ).triggered.connect(self._onRename)
        core.actionManager().action( "mFile/mFileSystem/aToggleExecutable" ).triggered.connect(self._onToggleExecutable)
        
        core.actionManager().action( "mNavigation/aNext" ).triggered.connect(core.workspace().activateNextDocument)
        core.actionManager().action( "mNavigation/aPrevious" ).triggered.connect(core.workspace().activatePreviousDocument)
        
        core.actionManager().action( "mNavigation/aFocusCurrentDocument" ).triggered.connect(core.workspace().focusCurrentDocument)
        core.actionManager().action( "mNavigation/aGoto" ).triggered.connect(lambda: core.workspace().currentDocument().invokeGoTo())

    
    def del_(self):
        pass

    def _onCurrentDocumentChanged( self, oldDocument, newDocument):
        """Update actions enabled state
        """
        # update file menu
        
        # enabled, even if not modified. Filewatcher doesn't work on Ssh-FS
        core.actionManager().action( "mFile/mSave/aCurrent" ).setEnabled( newDocument is not None )
        
        core.actionManager().action( "mFile/mSave/aAll" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mFile/mSave/aSaveAs" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mFile/mClose/aCurrent" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mFile/mClose/aAll" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mNavigation/aFocusCurrentDocument" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mNavigation/aGoto" ).setEnabled( newDocument is not None)
        core.actionManager().action( "mFile/mReload/aCurrent" ).setEnabled( newDocument is not None )
        core.actionManager().action( "mFile/mReload/aAll" ).setEnabled( newDocument is not None )
        core.actionManager().action( "mFile/mFileSystem/aRename" ).setEnabled(
                                        newDocument is not None and newDocument.filePath() is not None)
        core.actionManager().action( "mFile/mFileSystem/aToggleExecutable" ).setEnabled(
                                        newDocument is not None and newDocument.filePath() is not None)

    def _onDocumentOpenedOrClosed(self):
        # update view menu
        moreThanOneDocument = len(core.workspace().documents()) > 1
        core.actionManager().action( "mNavigation/aNext" ).setEnabled( moreThanOneDocument )
        core.actionManager().action( "mNavigation/aPrevious" ).setEnabled( moreThanOneDocument )

    def _onFileOpenTriggered(self):
        """Handler of File->Open
        """
        fileNames = QFileDialog.getOpenFileNames( core.mainWindow(),
                                                  self.tr( "Classic open dialog. Main menu -> Navigation -> Locator is better" ))
                
        for path in fileNames:
            core.workspace().openFile(path)
    
    def _onFileReloadTriggered(self):
        """Handler of File->Reload->Current
        """
        document = core.workspace().currentDocument()
        if  document is not None:
            self._reloadDocument(document)
    
    def _onFileReloadAllTriggered(self):
        """Handler of File->Reload->All
        """
        for document in core.workspace().documents():
            if document.filePath() is not None and \
               os.path.isfile(document.filePath()):
                self._reloadDocument(document)
    
    def _reloadDocument(self, document):
        """Reload the document contents
        """
        if  document.qutepart.document().isModified():
            template = self.tr( "The file <b>%s</b> has been modified by you.\n"
                                "Do you want to reload and discard changes?" )
            text = template % document.fileName()
            ret = QMessageBox.question(core.mainWindow(), self.tr( "Reload file..." ), text,
                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret != QMessageBox.Yes:
                return

        # open file
        try:
            QApplication.setOverrideCursor( Qt.WaitCursor )
            document.reload()
        except IOError as ex:
            QMessageBox.critical(None,
                                 self.tr("File not reloaded"),
                                 unicode(str(ex), 'utf8'))
            return None
        finally:
            QApplication.restoreOverrideCursor()
    
    def _onCloseCurrentDocument(self):
        """Handler of File->Close->Current triggered
        """
        document = core.workspace().currentDocument()
        assert(document is not None)
        core.workspace().closeDocument( document )

    def _onFileSaveCurrentTriggered(self):
        """Handler of File->Save->Current
        """
        return core.workspace().currentDocument().saveFile()
    
    def _onFileSaveAllTriggered(self):
        """Handler of File->Save->All
        """
        for document in core.workspace().documents():
            document.saveFile()
    
    def _onFileSaveAsTriggered(self):
        """Handler for File->Save->Save as
        """
        core.workspace().currentDocument().saveFileAs();
    
    def _onRename(self):
        """Handler for File->File System->Rename"""
        document = core.workspace().currentDocument()
        if document.qutepart.document().isModified() or \
           document.isExternallyModified() or \
           document.isExternallyRemoved() or \
           document.isNeverSaved():
            QMessageBox.warning(core.mainWindow(), 'Rename file', 'Save the file before renaming')
            return
        
        text, ok = QInputDialog.getText(core.mainWindow(), 'Rename file', 'New file name', text=document.filePath())
        if not ok:
            return
        
        try:
            os.rename(document.filePath(), text)
        except (OSError, IOError) as ex:
            QMessageBox.critical(core.mainWindow(), 'Failed to rename file', str(ex))
        else:
            document.setFilePath(text)
            document.saveFile()
    
    EXECUTABLE_FLAGS = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    
    def _isCurrentFileExecutable(self):
        """True if executable, False if not, None if no file or not saved"""
        document = core.workspace().currentDocument()
        if document is None:
            return None
        filePath = core.workspace().currentDocument().filePath()
        if filePath is None:
            return None
        
        if not os.path.isfile(filePath):
            return None

        try:
            st = os.stat(filePath)
        except:
            return None
        
        return st.st_mode & self.EXECUTABLE_FLAGS
    
    def _onFsMenuAboutToShow(self):
        action = core.actionManager().action('mFile/mFileSystem/aToggleExecutable')
        executable = self._isCurrentFileExecutable()
        action.setEnabled(executable is not None)
        
        if executable:
            action.setText('Make Not executable')
        else:
            action.setText('Make executable')
    
    def _onToggleExecutable(self):
        executable = self._isCurrentFileExecutable()
        assert executable is not None, 'aToggleExecutable must have been disabled'
        filePath = core.workspace().currentDocument().filePath()
        
        try:
            st = os.stat(filePath)
        except (IOError, OSError) as ex:
            QMessageBox.critical(core.mainWindow(), 'Failed to change executable mode',
                                 'Failed to get current file mode: %s' % str(ex))
            return
        
        if executable:
            newMode = st.st_mode & (~ self.EXECUTABLE_FLAGS)
        else:
            newMode = st.st_mode | self.EXECUTABLE_FLAGS
        
        try:
            os.chmod(filePath, newMode)
        except (IOError, OSError) as ex:
            QMessageBox.critical(core.mainWindow(), 'Failed to change executable mode',
                                 'Failed to set current file mode: %s' % str(ex))
            return
