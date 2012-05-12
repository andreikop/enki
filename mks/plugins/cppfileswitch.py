"""
cppfileswitch --- Switch C/C++ between header and implementation files
======================================================================
"""

import fnmatch
import glob
import operator

from PyQt4.QtCore import QObject

from mks.core.core import core

_HEADER_SUFFIXES = ["*.h", "*.hh", "*.hpp", "*.hxx", "*.h++"]
_IMPLEMENTATION_SUFFIXES = ["*.c", "*.cc", "*.cpp", "*.cxx", "*.c++"]

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
        return any(fnmatch.fnmatch(filePath, pattern) \
                            for pattern in _HEADER_SUFFIXES)
    
    def _isImplementation(self, filePath):
        """Check if file is a header
        """
        return any(fnmatch.fnmatch(filePath, pattern) \
                            for pattern in _IMPLEMENTATION_SUFFIXES)

    def _expandGlobs(self, listOfGlobs):
        """Expland list of globs
        """
        return reduce(operator.add, [glob.glob(globPattern) \
                                        for globPattern in listOfGlobs])

    def _getFileToSwitch(self):
        """Try to find implementation for header, header for implementation
        """
        filePath = core.workspace().currentDocument().filePath()
        filePathWithoutSuffix = filePath[:filePath.rindex('.')]
        filesToSwitch = []
        if self._isHeader(filePath):
            filesToSwitch = self._expandGlobs([filePathWithoutSuffix + suffix \
                                                for suffix in _IMPLEMENTATION_SUFFIXES])
        elif self._isImplementation(filePath):
            filesToSwitch = self._expandGlobs([filePathWithoutSuffix + suffix \
                                                for suffix in _HEADER_SUFFIXES])
        if filesToSwitch:
            return filesToSwitch[0]
        else:
            return None
    
    def _onTriggered(self):
        """Action handler. Do the job
        """
        path = self._getFileToSwitch()
        if path is not None:
            core.workspace().openFile(path)
