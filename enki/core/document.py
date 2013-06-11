"""
document --- Opened file representation
=======================================
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QFileSystemWatcher, QObject, QTimer
from PyQt4.QtGui import QFileDialog, \
                        QFont, \
                        QIcon, \
                        QInputDialog, \
                        QMessageBox, \
                        QWidget, \
                        QVBoxLayout

from qutepart import Qutepart

from enki.core.core import core

class _FileWatcher(QObject):
    """File watcher.
    
    QFileSystemWatcher notifies client about any change (file access mode, modification date, etc.)
    But, we need signal, only after file contents had been changed
    """
    modified = pyqtSignal(bool)
    removed = pyqtSignal(bool)
    
    def __init__(self, path):
        QObject.__init__(self)
        self._contents = None
        self._watcher = QFileSystemWatcher()
        self._timer = None
        self._path = path
        self.setPath(path)
        self.enable()
    
    def __del__(self):
        self._stopTimer()
        
    def enable(self):
        """Enable signals from the watcher
        """
        self._watcher.fileChanged.connect(self._onFileChanged)
    
    def disable(self):
        """Disable signals from the watcher
        """
        self._watcher.fileChanged.disconnect(self._onFileChanged)
        self._stopTimer()
    
    def setContents(self, contents):
        """Set file contents. Watcher uses it to compare old and new contents of the file.
        """
        self._contents = contents
        # Qt File watcher may work incorrectly, if file was not existing, when it started
        self.setPath(self._path)

    def setPath(self, path):
        """Path had been changed or file had been created. Set new path
        """
        if self._watcher.files():
            self._watcher.removePaths(self._watcher.files())
        if path is not None and os.path.isfile(path):
            self._watcher.addPath(path)
        self._path = path

    def _emitModifiedStatus(self):
        """Emit self.modified signal with right status
        """
        isModified = self._contents != self._safeRead(self._path)
        self.modified.emit(isModified)
        
    def _onFileChanged(self):
        """File changed. Emit own signal, if contents changed
        """
        if os.path.exists(self._path):
            self._emitModifiedStatus()
        else:
            self.removed.emit(True)
            self._startTimer()
    
    def _startTimer(self):
        """Init a timer.
        It is used for monitoring file after deletion.
        Git removes file, than restores it.
        """
        if self._timer is None:
            self._timer = QTimer()
            self._timer.setInterval(500)
            self._timer.timeout.connect(self._onCheckIfDeletedTimer)
        self._timer.start()
    
    def _stopTimer(self):
        """Stop timer, if exists
        """
        if self._timer is not None:
            self._timer.stop()
    
    def _onCheckIfDeletedTimer(self):
        """Check, if file has been restored
        """
        if os.path.exists(self._path):
            self.removed.emit(False)
            self._emitModifiedStatus()
            self.setPath(self._path)  # restart Qt file watcher after file has been restored
            self._stopTimer()
    
    def _safeRead(self, path):
        """Read file. Ignore exceptions
        """
        try:
            with open(path, 'rb') as file:
                return file.read()
        except (OSError, IOError):
            return None


class Document(QWidget):
    """
    Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    
    This class may requre redesign, if we need to add support for non-textual or non-unicode editor.
    DO redesign instead of doing dirty hacks
    """
    
    documentDataChanged = pyqtSignal()
    """
    documentDataChanged()
    
    **Signal** emitted, when document icon or toolTip has changed
    (i.e. document has been modified externally)
    """

    def __init__( self, parentObject, filePath, createNew=False):
        """Create editor and open file.
        If file is None or createNew is True, empty not saved file is created
        IO Exceptions are not catched, therefore, must be catched on upper level
        """
        QWidget.__init__( self, parentObject)
        self._neverSaved = filePath is None or createNew
        self._filePath = filePath
        self._externallyRemoved = False
        self._externallyModified = False
        # File opening should be implemented in the document classes
        
        self._fileWatcher = _FileWatcher(filePath)
        self._fileWatcher.modified.connect(self._onWatcherFileModified)
        self._fileWatcher.removed.connect(self._onWatcherFileRemoved)
        
        if filePath and self._neverSaved:
            core.mainWindow().appendMessage('New file "%s" is going to be created' % filePath, 5000)

        self.qutepart = Qutepart(self)
        self.qutepart.setStyleSheet('QPlainTextEdit {border: 0}')
        self._applyQpartSettings()
        core.uiSettingsManager().dialogAccepted.connect(self._applyQpartSettings)
        
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qutepart)
        self.setFocusProxy(self.qutepart)
        
        if not self._neverSaved:
            originalText = self._readFile(filePath)
            self.qutepart.text = originalText
        else:
            originalText = ''

        #autodetect eol, if need
        self._configureEolMode(originalText)
        
        self._tryDetectSyntax()
    
    def _tryDetectSyntax(self):
        self.qutepart.detectSyntax(sourceFilePath=self.filePath(),
                                   firstLine=self.qutepart.lines[0])

    def del_(self):
        """Explicytly called destructor
        """
        self._fileWatcher.disable()

    def _onWatcherFileModified(self, modified):
        """File has been modified
        """
        self._externallyModified = modified
        self.documentDataChanged.emit()

    def _onWatcherFileRemoved(self, isRemoved):
        """File has been removed
        """
        self._externallyRemoved = isRemoved
        self.documentDataChanged.emit()

    def _readFile(self, filePath):
        """Read the file contents.
        Shows QMessageBox for UnicodeDecodeError, but raises IOError, if failed to read file
        """
        with open(filePath, 'rb') as openedFile:  # Exception is ok, raise it up
            self._filePath = os.path.abspath(filePath)
            data = openedFile.read()                
        
        self._fileWatcher.setContents(data)
        
        try:
            text = unicode(data, 'utf8')
        except UnicodeDecodeError, ex:
            QMessageBox.critical(None,
                                 self.tr("Can not decode file"),
                                 filePath + '\n' +
                                 unicode(str(ex), 'utf8') + 
                                 '\nProbably invalid encoding was set. ' +
                                 'You may corrupt your file, if saved it')
            text = unicode(data, 'utf8', 'replace')
        
        # Strip last EOL. It will be restored, when saving
        if text.endswith('\r\n'):
            text = text[:-2]
        elif text.endswith('\r') or text.endswith('\n'):
            text = text[:-1]
        
        return text

    def isExternallyModified(self):
        """Check if document's file has been modified externally.
        
        This method does not do any file system access, but only returns cached info
        """
        return self._externallyModified
    
    def isExternallyRemoved(self):
        """Check if document's file has been deleted externally.
        
        This method does not do any file system access, but only returns cached info
        """
        return self._externallyRemoved
    
    def isNeverSaved(self):
        """Check if document has been created, but never has been saved on disk
        """
        return self._neverSaved
        
    def filePath(self):
        """return the document file absolute path
        None if not set (new document)"""
        return self._filePath
    
    def fileName(self):
        """Document file name without a path
        None if not set (new document)"""
        if self._filePath:
            return os.path.basename(self._filePath)
        else:
            return None
    
    def setFilePath(self, newPath):
        """Change document file path.
        
        Used when saving first time, or on Save As action
        """
        core.workspace().documentClosed.emit(self)
        self._filePath = newPath
        self._fileWatcher.setPath(newPath)
        self._neverSaved = True
        core.workspace().documentOpened.emit(self)
        core.workspace().currentDocumentChanged.emit(self, self)
    
    def _saveFile(self, filePath):
        """Low level method. Always saves file, even if not modified
        """
        # Create directory
        dirPath = os.path.dirname(filePath)
        if  not os.path.exists(dirPath):
            try:
                os.mkdir(dirPath)
            except OSError, ex:
                error = unicode(str(ex), 'utf8')
                QMessageBox.critical(None,
                                     self.tr("Can not save file"),
                                     self.tr( "Cannot create directory '%s'. Error '%s'" % (dirPath, error)))
                return

        text = self.qutepart.textForSaving()
        if not text.endswith(self.qutepart.eol):
            text += self.qutepart.eol

        # Write file
        data = text.encode('utf8')
        
        self._fileWatcher.disable()
        try:
            with open(filePath, 'wb') as openedFile:
                openedFile.write(data)
            self._fileWatcher.setContents(data)
        except IOError as ex:
            QMessageBox.critical(None,
                                 self.tr("Can not write to file"),
                                 unicode(str(ex), 'utf8'))
            return
        finally:
            self._fileWatcher.enable()
        
        # Update states
        self._neverSaved = False
        self._externallyRemoved = False
        self._externallyModified = False
        self.qutepart.document().setModified(False)
        
        if self.qutepart.language() is None:
            self._tryDetectSyntax()

    def saveFile(self):
        """Save the file to file system
        
        Shows QFileDialog if necessary
        """
        # Get path
        if not self._filePath:
            path = QFileDialog.getSaveFileName (self, self.tr('Save file as...'))
            if path:
                self.setFilePath(path)
            else:
                return
        self._saveFile(self.filePath())
        
    def saveFileAs(self):
        """Ask for new file name with dialog. Save file
        """
        path = QFileDialog.getSaveFileName (self, self.tr('Save file as...'))
        if not path:
            return
        
        self.setFilePath(path)
        self._saveFile(path)
        
    def reload(self):
        """Reload the file from the disk
        
        If child class reimplemented this method, it MUST call method of the parent class
        for update internal bookkeeping"""

        text = self._readFile(self.filePath())
        pos = self.qutepart.cursorPosition
        self.qutepart.text = text
        self._externallyModified = False
        self._externallyRemoved = False
        self.qutepart.cursorPosition = pos
        
    def modelToolTip(self):
        """Tool tip for the opened files model
        """
        toolTip = self.filePath()

        if toolTip is None:
            return None

        if self.qutepart.document().isModified():
            toolTip += "<br/><font color='blue'>%s</font>" % self.tr("Locally Modified")
        if  self._externallyModified:
            toolTip += "<br/><font color='red'>%s</font>" % self.tr("Externally Modified")
        if  self._externallyRemoved:
            toolTip += "<br/><font color='red'>%s</font>" % self.tr( "Externally Deleted" )
        return '<html>' + toolTip + '</html>'
    
    def modelIcon(self):
        """Icon for the opened files model
        """
        if self.isNeverSaved():  # never has been saved
            icon = "save.png"
        elif   self._externallyRemoved  and self._externallyModified:
            icon = "modified-externally-deleted.png"
        elif self._externallyRemoved:
            icon = "deleted.png"
        elif self._externallyModified and self.qutepart.document().isModified():
            icon = "modified-externally-modified.png"
        elif self._externallyModified:
            icon = "modified-externally.png"
        elif self.qutepart.document().isModified():
            icon = "save.png"
        else:
            icon = "transparent.png"
        return QIcon(":/enkiicons/" + icon)
    
    def invokeGoTo(self):
        """Show GUI dialog, go to line, if user accepted it
        """
        line = self.qutepart.cursorPosition[0]
        gotoLine, accepted = QInputDialog.getInteger(self, self.tr( "Go To Line..." ),
                                                      self.tr( "Enter the line you want to go:" ), 
                                                      line, 1, len(self.qutepart.lines), 1)
        if accepted:
            gotoLine -= 1
            self.qutepart.cursorPosition = gotoLine, None
            self.setFocus()
    
    def printFile(self):
        """Print file
        """
        raise NotImplemented()

    def _configureEolMode(self, originalText):
        """Detect end of line mode automatically and apply detected mode
        """
        modes = set()
        for line in originalText.splitlines(True):
            if line.endswith('\r\n'):
                modes.add('\r\n')
            elif line.endswith('\n'):
                modes.add('\n')
            elif line.endswith('\r'):
                modes.add('\r')

        if len(modes) == 1:  # exactly one
            detectedMode = modes.pop()
        else:
            detectedMode = None
        
        convertor = {r'\r\n': '\r\n',
                     r'\n': '\n',
                     r'\r': '\r'}
        default = convertor[core.config()["Editor"]["EOL"]["Mode"]]

        if len(modes) > 1:
            message = "%s contains mix of End Of Line symbols. It will be saved with '%s'" % \
                        (self.filePath(), repr(default))
            core.mainWindow().appendMessage(message)
            self.qutepart.eol = default
            self.qutepart.document().setModified(True)
        elif core.config()["Editor"]["EOL"]["AutoDetect"]:
            if detectedMode is not None:
                self.qutepart.eol = detectedMode
            else:  # empty set, not detected
                self.qutepart.eol = default
        else:  # no mix, no autodetect. Force EOL
            if detectedMode is not None and \
                    detectedMode != default:
                message = "%s: End Of Line mode is '%s', but file will be saved with '%s'. " \
                          "EOL autodetection is disabled in the settings" % \
                                (self.fileName(), repr(detectedMode), repr(default))
                core.mainWindow().appendMessage(message)
                self.qutepart.document().setModified(True)
            
            self.qutepart.eol = default
    
    def _applyQpartSettings(self):
        """Apply qutepart settings
        """
        conf = core.config()['Editor']
        self.qutepart.setFont(QFont(conf['DefaultFont'], conf['DefaultFontSize']))
        self.qutepart.indentUseTabs = conf['Indentation']['UseTabs']
        self.qutepart.indentWidth = conf['Indentation']['Width']
        
        self.qutepart.completionEnabled = conf['AutoCompletion']['Enabled']
        self.qutepart.completionThreshold = conf['AutoCompletion']['Threshold']
        
        # EOL is managed separately
