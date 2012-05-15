"""
preview --- HTML, Markdown preview
==================================
"""

from PyQt4.QtCore import pyqtSignal, QObject, QSize, Qt, QThread
from PyQt4.QtGui import QIcon
from PyQt4.QtWebKit import QWebView

from mks.core.core import core

from mks.fresh.dockwidget.pDockWidget import pDockWidget

from threading import Lock

zen = \
"""Beautiful is better than ugly.<br/>
Explicit is better than implicit.<br/>
Simple is better than complex.<br/>
Complex is better than complicated.<br/>
Flat is better than nested.<br/>
Sparse is better than dense.<br/>
Readability counts.<br/>
Special cases aren't special enough to break the rules.<br/>
Although practicality beats purity.<br/>
Errors should never pass silently.<br/>
Unless explicitly silenced.<br/>
In the face of ambiguity, refuse the temptation to guess.<br/>
There should be one-- and preferably only one --obvious way to do it.<br/>
Although that way may not be obvious at first unless you're Dutch.<br/>
Now is better than never.<br/>
Although never is often better than *right* now.<br/>
If the implementation is hard to explain, it's a bad idea.<br/>
If the implementation is easy to explain, it may be a good idea.<br/>
Namespaces are one honking great idea -- let's do more of those!"""

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
           core.workspace().currentDocument().language() is not None and \
           core.workspace().currentDocument().language() in ('HTML', 'Markdown'):
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

class ConverterThread(QThread):
    """Thread converts markdown to HTML
    """
    htmlReady = pyqtSignal(unicode, unicode)
    
    def __init__(self):
        QThread.__init__(self)
        self._lock = Lock()
    
    def process(self, filePath, language, text):
        """Convert data and emit result
        """
        with self._lock:
            self._filePath = filePath
            self._haveData = True
            self._language = language
            self._text = text
            if not self.isRunning():
                self.start(QThread.LowPriority)
    
    def _getHtml(self, language, text):
        """Get HTML for document
        """
        if language == 'HTML':
            return text
        elif language == 'Markdown':
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

    def run(self):
        """Thread function
        """
        while True:  # exits with break
            with self._lock:
                filePath = self._filePath
                language = self._language
                text = self._text
                self._haveData = False
            
            html = self._getHtml(self._language, self._text)
            
            with self._lock:
                if not self._haveData:
                    self.htmlReady.emit(filePath, html)
                    break
                # else - next iteration


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
        
        self._thread = ConverterThread()
        self._thread.htmlReady.connect(self._setHtml)

        self._visiblePath = None
        self._onDocumentChanged(None, core.workspace().currentDocument())

    def del_(self):
        """Uninstall themselves
        """
        core.actionManager().removeAction("mDocks/aPreview")
        self._thread.wait()
    
    def _saveScrollPos(self):
        """Save scroll bar position for document
        """
        frame = self._view.page().mainFrame()
        if frame.contentsSize() == QSize(0, 0):
            return # no valida data, nothing to save
        
        pos = frame.scrollPosition()
        self._scrollPos[self._visiblePath] = pos
        self._hAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Horizontal) == pos.x()
        self._vAtEnd[self._visiblePath] = frame.scrollBarMaximum(Qt.Vertical) == pos.y()

    def _restoreScrollPos(self):
        """Restore scroll bar position for document
        """
        self._view.page().mainFrame().contentsSizeChanged.disconnect(self._restoreScrollPos)
        
        if not self._visiblePath in self._scrollPos:
            return  # no data for this document
        
        frame = self._view.page().mainFrame()

        frame.setScrollPosition(self._scrollPos[self._visiblePath])
        
        if self._hAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Horizontal, frame.scrollBarMaximum(Qt.Horizontal))
        
        if self._vAtEnd[self._visiblePath]:
            frame.setScrollBarValue(Qt.Vertical, frame.scrollBarMaximum(Qt.Vertical))

    def _onDocumentChanged(self, old, new):
        """Current document changed, update preview
        """
        if new is not None:
            self._thread.process(new.filePath(), new.language(), new.text())
        else:
            self._setHtml(None, zen)  # empty dock looks so empty

    def _onTextChanged(self, document, text):
        """Text changed, update preview
        """
        self._thread.process(document.filePath(), document.language(), document.text())

    def _setHtml(self, filePath, html):
        """Set HTML to the view and restore scroll bars position.
        Called by the thread
        """
        self._saveScrollPos()
        self._visiblePath = filePath
        self._view.page().mainFrame().contentsSizeChanged.connect(self._restoreScrollPos)
        self._view.setHtml(html)
