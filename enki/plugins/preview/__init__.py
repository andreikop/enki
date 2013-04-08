"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import QObject, Qt

from enki.core.core import core


def isRestFile(document):
    """Check if document is a ReST file
    Currently, there are no highlighting language for ReST
    """
    return document is not None and \
           document.fileName() is not None and \
           document.fileName().endswith('.rst')


class Plugin(QObject):
    """Plugin interface implementation
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        
        if not 'Preview' in core.config():  # migration from old configs versions
            print 'no preview'
            core.config()['Preview'] = {'Enabled': True,
                                        'JavaScriptEnabled' : True}

        self._dock = None
        self._dockInstalled = False
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().languageChanged.connect(self._onDocumentChanged)
    
    def _onDocumentChanged(self):
        """Document or Language changed.
        Create dock, if necessary
        """
        if self._canHighlight(core.workspace().currentDocument()):
            if not self._dockInstalled:
                self._createDock()
        else:
            if self._dockInstalled:
                self._removeDock()
    
    def _canHighlight(self, document):
        """Check if can highlight document
        """
        if document is None:
            return False
        
        if document.language() is not None and \
           document.language() in ('HTML', 'Markdown'):
            return True
        
        if isRestFile(document):
            return True
        
        return False

    def _createDock(self):
        """Install dock
        """
        # create dock
        if self._dock is None:
            from enki.plugins.preview.preview import PreviewDock
            self._dock = PreviewDock()
        # add dock to dock toolbar entry
        core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
        core.actionManager().addAction("mView/aPreview", self._dock.showAction())
        self._dockInstalled = True
        if core.config()['Preview']['Enabled']:
            self._dock.show()
    
    def _removeDock(self):
        """Remove dock from GUI
        """
        if core.config()['Preview']['Enabled'] != self._dock.isVisible():
            core.config()['Preview']['Enabled'] = self._dock.isVisible()
            core.config().flush()
        
        core.actionManager().removeAction("mView/aPreview")
        core.mainWindow().removeDockWidget(self._dock)
        self._dockInstalled = False
    
    def del_(self):
        """Uninstall the plugin
        """
        if self._dockInstalled:
            self._removeDock()
        
        if self._dock is not None:
            self._dock.del_()
