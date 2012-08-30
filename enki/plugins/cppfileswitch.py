"""
cppfileswitch --- Switch C/C++ between header and implementation files
======================================================================
"""

import fnmatch
import os.path

from PyQt4.QtCore import QObject

from enki.core.core import core

_HEADER_SUFFIXES = [".h", ".hh", ".hpp", ".hxx", ".h++"]
_IMPLEMENTATION_SUFFIXES = [".c", ".cc", ".cpp", ".cxx", ".c++"]

class Plugin(QObject):
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        self._action = None
        core.workspace().currentDocumentChanged.connect(self._updateAction)
        core.workspace().languageChanged.connect(self._updateAction)
    
    def del_(self):
        """Uninstall the plugin
        """
        core.workspace().currentDocumentChanged.disconnect(self._updateAction)
        core.workspace().languageChanged.disconnect(self._updateAction)
        if self._action is not None:
            core.actionManager().removeAction(self._action)
            del self._action

    def _updateAction(self):
        """Create, show or hide, enable or disable action
        """
        document = core.workspace().currentDocument()
        if document is not None and \
           document.language() == 'C++':
            if self._action is None:
                self._action = core.actionManager().addAction("mNavigation/aHeaderImplementation",
                                                              "Switch C/C++ header/implementation",
                                                              shortcut = 'Ctrl+I')
                self._action.triggered.connect(self._onTriggered)
            self._action.setVisible(True)
            self._action.setEnabled(self._getFileToSwitch() is not None)
        else:
            if self._action is not None:
                self._action.setVisible(False)
    
    def _isHeader(self, filePath):
        """Check if file is a header
        """
        return any([filePath.endswith(suffix)
                            for suffix in _HEADER_SUFFIXES])
    
    def _isImplementation(self, filePath):
        """Check if file is a header
        """
        return any([filePath.endswith(suffix)
                            for suffix in _IMPLEMENTATION_SUFFIXES])

    def _tryFindFileOnFileSystem(self):
        """Try to find file on File system with the same path, but different suffix
        """
        filePath = core.workspace().currentDocument().filePath()
        filePathWithoutSuffix = filePath[:filePath.rindex('.')]

        if self._isHeader(filePath):
            variants = [filePathWithoutSuffix + suffix \
                            for suffix in _IMPLEMENTATION_SUFFIXES]
        elif self._isImplementation(filePath):
            variants = [filePathWithoutSuffix + suffix \
                            for suffix in _HEADER_SUFFIXES]
        else:  # oops, unknown file. Suffixes DB is not up to date
            variants = []
        
        existing = [path
                        for path in variants \
                            if os.path.isfile(path)]
        if existing:
            return existing[0]
        else:
            return None
        
    def _tryFindFileAmongOpened(self):
        """Try to find file with the same name but different suffix among opened files
        Works, when header and implementation are in different directories, but both opened
        """
        fileName = core.workspace().currentDocument().fileName()
        fileNameWithoutSuffix = fileName[:fileName.rindex('.')]

        if self._isHeader(fileName):
            variants = [fileNameWithoutSuffix + suffix \
                            for suffix in _IMPLEMENTATION_SUFFIXES]
        elif self._isImplementation(fileName):
            variants = [fileNameWithoutSuffix + suffix \
                            for suffix in _HEADER_SUFFIXES]
        
        matchingDocuments = [document.filePath() \
                                for document in core.workspace().documents() \
                                    if document.fileName() in variants]
        if matchingDocuments:
            return matchingDocuments[0]
        else:
            return None
    
        
    def _getFileToSwitch(self):
        """Try to find implementation for header, header for implementation
        """
        res = self._tryFindFileOnFileSystem()
        if res:
            return res
        else:
            return self._tryFindFileAmongOpened()

    def _onTriggered(self):
        """Action handler. Do the job
        """
        path = self._getFileToSwitch()
        if path is not None:
            core.workspace().openFile(path)
