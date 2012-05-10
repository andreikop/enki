"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import QObject, Qt
from PyQt4.QtGui import QIcon
from PyQt4.QtWebKit import QWebView

from mks.core.core import core

from mks.fresh.dockwidget.pDockWidget import pDockWidget

class Plugin(QObject):
    """Plugin interface implementation
    """
    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        self._dock = None
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().languageChanged.connect(self._onDocumentChanged)

    def _onDocumentChanged(self):
        """Document or Language changed.
        Create dock, if necessary
        """
        if core.workspace().currentDocument() is not None and \
           core.workspace().currentDocument().highlightingLanguage() is not None and \
           core.workspace().currentDocument().highlightingLanguage() in ('HTML', 'Markdown'):
            # create dock
            self._dock = PreviewDock(core.mainWindow())
            # add dock to dock toolbar entry
            core.mainWindow().addDockWidget(Qt.RightDockWidgetArea, self._dock)
            
            core.workspace().currentDocumentChanged.disconnect(self._onDocumentChanged)
            core.workspace().languageChanged.disconnect(self._onDocumentChanged)
    
    def del_(self):
        """Uninstall the plugin
        """
        if self._dock is not None:
            core.mainWindow().removeDockWidget(self._dock)
            self._dock.del_()

class PreviewDock(pDockWidget):
    """GUI and implementation
    """
    def __init__(self, *args):
        pDockWidget.__init__(self, *args)

        self.setObjectName("PreviewDock")
        self.setWindowTitle(self.tr( "&Preview" ))
        self.setWindowIcon(QIcon(':/mksicons/internet.png'))
        self.showAction().setShortcut("Alt+P")
        core.actionManager().addAction("mDocks/aPreview", self.showAction())

        self._view = QWebView(self)
        self.setWidget(self._view)
        self.setFocusProxy(self._view)
        
        core.workspace().currentDocumentChanged.connect(self._onDocumentChanged)
        core.workspace().textChanged.connect(self._onTextChanged)
        
        self._scrollPos = {}
        self._vAtEnd = {}
        self._hAtEnd = {}
        
        self._onDocumentChanged(None, core.workspace().currentDocument())
    
    def del_(self):
        """Uninstall themselves
        """
        core.actionManager().removeAction("mDocks/aPreview")
    
    def _saveScrollPos(self, document):
        """Save scroll bar position for document
        """
        frame = self._view.page().mainFrame()
        pos = frame.scrollPosition()
        self._scrollPos[document.filePath()] = pos
        self._hAtEnd[document.filePath()] = frame.scrollBarMaximum(Qt.Horizontal) == pos.x()
        self._vAtEnd[document.filePath()] = frame.scrollBarMaximum(Qt.Vertical) == pos.y()

    def _restoreScrollPos(self):
        """Restore scroll bar position for document
        """
        document = core.workspace().currentDocument()
        self._view.page().mainFrame().contentsSizeChanged.disconnect(self._restoreScrollPos)
        
        if not document.filePath() in self._hAtEnd:
            return  # no data for this document
        
        frame = self._view.page().mainFrame()

        frame.setScrollPosition(self._scrollPos[document.filePath()])
        
        if self._hAtEnd[document.filePath()]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))
        
        if self._vAtEnd[document.filePath()]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))
    

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if old is not None:
            self._saveScrollPos(old)

        if new is not None:
            self._showDocument(new)

    def _onTextChanged(self, document, text):
        """Text changed, update preview
        """
        self._saveScrollPos(document)
        self._showDocument(document)

    def _showDocument(self, document):
        """Set HTML to the view and restore position
        """
        self._view.setHtml(self._getHtml(document))
        self._view.page().mainFrame().contentsSizeChanged.connect(self._restoreScrollPos)
    
    def _getHtml(self, document):
        """Get HTML for document
        """
        text = document.text()
        if document.highlightingLanguage() == 'HTML':
            return text
        elif document.highlightingLanguage() == 'Markdown':
            return self._convertMarkdown(text)
        else:
            return 'No preview for this type of file'

    def _convertMarkdown(self, text):
        """Convert Markdown to HTML
        """
        try:
            import markdown
        except ImportError:
            return "Markdown preview requires <i>python-markdown</i> package<br/>" \
                   "Install it with your package manager or see " \
                   "<a href=http://packages.python.org/Markdown/install.html>installation instructions</a>"
        
        return markdown.markdown(text)
