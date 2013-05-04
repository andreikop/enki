"""
workspace_actions --- Workspace actons, such as "Open file", "Next document", ..
================================================================================
"""

import os.path

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QApplication, QFileDialog, QMessageBox

from enki.core.core import core

class Plugin(QObject):
    def __init__(self):
        QObject.__init__(self)
        
        core.workspace().currentDocumentChanged.connect(self._onCurrentDocumentChanged)

        core.actionManager().action( "mFile/aOpen" ).triggered.connect(self._onFileOpenTriggered)
        core.actionManager().action( "mFile/mReload/aCurrent" ).triggered.connect(self._onFileReloadTriggered)
        core.actionManager().action( "mFile/mReload/aAll" ).triggered.connect(self._onFileReloadAllTriggered)
        core.actionManager().action( "mFile/aNew" ).triggered.connect(lambda : core.workspace().createEmptyNotSavedDocument(None))
        core.actionManager().action( "mFile/mClose/aCurrent" ).triggered.connect(self._onCloseCurrentDocument)
        core.actionManager().action( "mFile/mClose/aAll" ).triggered.connect(core.workspace().closeAllDocuments)
    
        core.actionManager().action( "mFile/mSave/aCurrent" ).triggered.connect(self._onFileSaveCurrentTriggered)
        core.actionManager().action( "mFile/mSave/aAll" ).triggered.connect(self._onFileSaveAllTriggered)
        core.actionManager().action( "mFile/mSave/aSaveAs" ).triggered.connect(self._onFileSaveAsTriggered)
        
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
    
