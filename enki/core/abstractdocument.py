"""
abstractdocument --- Base classes for workspace documents
=========================================================

This class is inherited by textual editor, and must be inherited by other workspace widgets.

Classes:
    * :class:`enki.core.abstractdocument.AbstractDocument`
    * :class:`enki.core.abstractdocument.AbstractTextEditor`
"""

import os.path

from PyQt4.QtCore import pyqtSignal, QFileSystemWatcher, QObject, QTimer
from PyQt4.QtGui import QFileDialog, \
                        QIcon, \
                        QInputDialog, \
                        QMessageBox, \
                        QWidget

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

class AbstractDocument(QWidget):
    """
    Base class for documents on workspace, such as opened source file, Qt Designer and Qt Assistant, ...
    Inherit this class, if you want to create new document type
    
    This class may requre redesign, if we need to add support for non-textual or non-unicode editor.
    DO redesign instead of doing dirty hacks
    """
    
    modifiedChanged = pyqtSignal(bool)
    """
    modifiedChanged(modified)
    
    **Signal** emitted, when modified state changed (file edited, or saved)
    Bool parameter contains new value
    
    Signal is retransmitted by the workspace
    """  # pylint: disable=W0105
    
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

    def _setModified(self, value):
        """Set modified state for the file. Called by AbstractDocument
        """
        pass

    def isModified(self):
        """Returns True, if file is modified
        """
        pass

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
    
    def _eolSymbol(self):
        """Convert EOL mode to symbol, insertable to text
        """
        converter = { r'\r\n': '\r\n',
                      r'\r'  : '\r',
                      r'\n'  : '\n'}
        return converter[self.eolMode()]

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

        # Text may be separated with invalid EOL symbols. Join lines with EOL, set for the document
        text = self.qutepart.text
        lines = text.splitlines()
        if text.endswith('\n'):
            lines.append('')

        text = self._eolSymbol().join(lines)

        # Append \n to the end, if file is not empty. Enki always ends last line with EOL
        if text:
            text += self._eolSymbol()

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
        self._setModified(False)

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
        qutepart.cursorPosition = pos
        
    def modelToolTip(self):
        """Tool tip for the opened files model
        """
        toolTip = self.filePath()

        if toolTip is None:
            return None

        if self.isModified():
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
        elif self._externallyModified and self.isModified():
            icon = "modified-externally-modified.png"
        elif self._externallyModified:
            icon = "modified-externally.png"
        elif self.isModified():
            icon = "save.png"
        else:
            icon = "transparent.png"
        return QIcon(":/enkiicons/" + icon)
    

class AbstractTextEditor(AbstractDocument):
    """Base class for text editors.
    """
    
    indentWidthChanged = pyqtSignal(int)
    """
    indentWidthChanged(width)
    
    **Signal** emitted, when indentation with has been changed

    Signal is retransmitted by the workspace
    """  # pylint: disable=W0105

    indentUseTabsChanged = pyqtSignal(bool)
    """
    indentUseTabsChanged(use)
    
    **Signal** emitted, when indentation mode has been changed

    Signal is retransmitted by the workspace
    """  # pylint: disable=W0105

    def __init__(self, parentObject, filePath, createNew=False, terminalWidget=False):
        """If terminalWidget is True, editor is used not as fully functional editor, but as interactive terminal.
        In this mode line numbers and autocompletion won't be shown
        """
        AbstractDocument.__init__(self, parentObject, filePath, createNew)
        self._language = None
    
    def eolMode(self):
        """Return document's EOL mode. Possible values are:
        
        * ``\\n``  - UNIX EOL
        * ``\\r\\n`` - Windows EOL
        * ``\\r`` - Mac EOL
        * ``None`` - not defined for the editor type
        """
        return None
    
    def setEolMode(self, mode):
        """Set editor EOL mode.
        See eolMode() for a alowed mode values
        """
        pass
    
    def indentWidth(self):
        """Get width of tabulation symbol and count of spaces to insert, when Tab pressed
        """
        raise NotImplemented()
    
    def setIndentWidth(self, width):
        """Set width of tabulation symbol and count of spaces to insert, when Tab pressed
        """
        if width == self.indentWidth():
            return
        self._applyIndentWidth(width)
        self.indentWidthChanged.emit(width)
    
    def _applyIndentWidth(self, width):
        """Apply indentation width
        """
        raise NotImplemented()

    def indentUseTabs(self):
        """Get indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        """
        raise NotImplemented()
    
    def setIndentUseTabs(self, use):
        """Set indentation uses tabs flag.
        If true - \t inserted by Tab button, if false - spaces
        """
        if use == self.indentUseTabs():
            return
        self._applyIndentUseTabs(use)
        self.indentUseTabsChanged.emit(use)
    
    def _applyIndentUseTabs(self, use):
        """Apply indent uses tabs option
        """
        raise NotImplemented()

    def replace(self, text,
                startAbsPos=None, startLine=None, startCol=None,
                endAbsPos=None, endLine=None, endCol=None):
        """Replace text at specified position with text.
        
        startAbsPos or (startLine and startCol) must be specified.
        
        endAbsPos or (endLine and endCol) must be specified
        """
        if startAbsPos is None:
            assert startLine is not None and startCol is not None
            startAbsPos = self._toAbsPosition(startLine, startCol)
        if endAbsPos is None:
            assert endLine is not None and endCol is not None
            endAbsPos = self._toAbsPosition(endLine, endCol)
        self._replace(startAbsPos, endAbsPos, text)

    def beginUndoAction(self):
        """Start doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        
        DO NOT FORGET to call **endUndoAction()** after you have finished
        """
        pass

    def endUndoAction(self):
        """Finish doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        """
        pass

    def invokeGoTo(self):
        """Show GUI dialog, go to line, if user accepted it
        """
        line = self.qutepart.cursorPosition[0]
        gotoLine, accepted = QInputDialog.getInteger(self, self.tr( "Go To Line..." ),
                                                      self.tr( "Enter the line you want to go:" ), 
                                                      line, 1, self.lineCount(), 1)
        if accepted:
            gotoLine -= 1
            self.qutepart.cursorPosition = gotoLine, None
            self.setFocus()

        
    def line(self, index):
        """Get line of the text by its index. Lines are indexed from 0.
        
        None, if index is invalid
        """
        return self.lines()[index]
    
    def setLine(self, index, text):
        """Replace text in the line with the text.
        Shortcut for replace(...)
        """
        self.replace(text, startLine=index, startCol=0,
                           endLine=index, endCol=len(self.line(index)))
    
    def lines(self):
        """Get text as list of lines. EOL symbol is not included.
        If the last line ends with EOL, additional empty line is added.
        """
        text = self.qutepart.text
        lines = text.splitlines()
        if text.endswith('\n'):
            lines.append('')
        elif not lines:  # empty text contains one empty line
            lines.append('')
        return lines

    def lineCount(self):
        """Get line count
        """
        pass

    def wordUnderCursor(self):
        """Get word under cursor.
        What is a "word" depends on current language
        Return (word, wordStartAbsPos, wordEndAbsPos) or (None, None, None)
        """
        raise NotImplemented()

    def _toAbsPosition(self, line, col):
        """Convert (line, column) to absolute position
        """
        lines = self.lines()
        
        lines = lines[:line + 1]  # remove not included lines
        if lines:
            lines[-1] = lines[-1][:col]  # remove not included symbols
            
        pos = sum([len(l) for l in lines])  # sum of all visible symbols
        pos += (len(lines) - 1)  # EOL symbols
        
        return pos

    def _toLineCol(self, absPosition):
        """Convert absolute position to (line, column)
        """
        textBefore = self.qutepart.text[:absPosition]
        line = textBefore.count('\n')
        eolIndex = textBefore.rfind('\n')  # -1 is ok
        col = len(textBefore) - eolIndex - 1
        return line, col

    def _configureEolMode(self, originalText):
        """Detect end of line mode automatically and apply detected mode
        """
        modes = set()
        for line in originalText.splitlines(True):
            if line.endswith('\r\n'):
                modes.add(r'\r\n')
            elif line.endswith('\n'):
                modes.add(r'\n')
            elif line.endswith('\r'):
                modes.add(r'\r')

        default = core.config()["Editor"]["EOL"]["Mode"]
        
        moreThanOne = len(modes) > 1
        
        if not moreThanOne and len(modes) == 1:
            detectedMode = modes.pop()
        else:
            detectedMode = None
        
        if moreThanOne:
            message = "%s contains mix of End Of Line symbols. It will be saved with '%s'" % \
                        (self.filePath(), default)
            core.mainWindow().appendMessage(message, 10000)
            self.setEolMode(default)
            self._setModified(True)
        elif core.config()["Editor"]["EOL"]["AutoDetect"]:
            if detectedMode is not None:
                self.setEolMode (detectedMode)
            else:  # empty set, not detected
                self.setEolMode(default)
        else:  # no mix, no autodetect. Force EOL
            if detectedMode is not None and \
                    detectedMode != default:
                message = "%s: End Of Line mode is '%s', but file will be saved with '%s'. " \
                          "EOL autodetection is disabled in the settings" % (self.fileName(), detectedMode, default)
                core.mainWindow().appendMessage(message, 10000)
                self._setModified(True)
            
            self.setEolMode(default)

    def printFile(self):
        """Print file
        """
        raise NotImplemented()

