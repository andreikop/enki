"""
recentfiles --- Recent files menu and Undo Close action
=======================================================
"""
import os.path
import json

from PyQt4.QtCore import QObject, QVariant

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
import enki.core.json_wrapper

_FILE_PATH = os.path.join(CONFIG_DIR, 'recent_files.json')
_MAX_SIZE = 100

class Plugin(QObject):
    """Plugin interface
    """
    def __init__(self):
        QObject.__init__(self)
        self._recentFileActions = []
        self._recent = enki.core.json_wrapper.load(_FILE_PATH, 'recent file list', [])
        self._undoClose = core.actionManager().addAction("mFile/mUndoClose/aUndoClose",
                                                         "Undo close",
                                                         shortcut = 'Shift+Ctrl+U')
        core.workspace().documentClosed.connect(self._onDocumentClosed)
        self._undoClose.triggered.connect(self._onUndoClose)
        menu = core.actionManager().action("mFile/mUndoClose").menu()
        menu.aboutToShow.connect(self._onMenuAboutToShow)
        menu.aboutToHide.connect(self._onMenuAboutToHide)

    def del_(self):
        """Explicitly called destructor
        """
        core.workspace().documentClosed.disconnect(self._onDocumentClosed)
        core.actionManager().removeAction(self._undoClose)
        enki.core.json_wrapper.dump(_FILE_PATH, 'recent file', self._recent)

    def _onDocumentClosed(self, document):
        """Document has been closed, remember it
        """
        path = document.filePath()
        
        if path is None:
            return
        
        if path in self._recent:
            self._recent.remove(path)
        self._recent.insert(0, path)
        if len(self._recent) > _MAX_SIZE:
            self._recent.remove(self._recent[-1])
        self._updateUndoCloseAction()
        
    def _existingNotOpenedRecents(self):
        """List of existing recent files
        """
        opened = set([document.filePath() \
                        for document in core.workspace().documents()])
        return [path for path in self._recent \
                    if os.path.exists(path) and \
                    not path in opened]

    def _updateUndoCloseAction(self):
        """Update action text and enabled state
        """
        existing = self._existingNotOpenedRecents()
        if existing:
            self._undoClose.setEnabled(True)
            self._undoClose.setText(existing[0])
        else:
            self._undoClose.setEnabled(False)
            self._undoClose.setText("Nothing to reopen")

    def _onUndoClose(self):
        """Undo Close triggered. Open file
        """
        existing = self._existingNotOpenedRecents()
        
        if not existing:
            core.mainWindow().statusBar().showMessage("No existing recent files")
            return
        
        doc = core.workspace().openFile(existing[0])
        if doc is not None:  # sucessfully opened
            self._recent.remove(existing[0])
    
    def _onMenuItemTriggered(self):
        """One of recents, but not first, triggered
        """
        action = self.sender()
        path = action.data().toString()
        core.workspace().openFile(path)
    
    def _onMenuAboutToShow(self):
        """Menu is going to be shown. Fill it
        """
        self._updateUndoCloseAction()
        
        existing = self._existingNotOpenedRecents()
        if len(existing) <= 1:
            return
        
        recents = self._existingNotOpenedRecents()
        count = min(len(recents), 10)
        for path in recents[1:count]:  # first already available as Undo Close action
            actionId = "mFile/mUndoClose/a%s" % path.replace('/', ':')
            action = core.actionManager().addAction(actionId, path)
            action.setData(QVariant(path))
            action.triggered.connect(self._onMenuItemTriggered)
            self._recentFileActions.append(action)

    def _onMenuAboutToHide(self):
        """Menu is going to be hidden. Clear it
        """
        for action in self._recentFileActions:
            core.actionManager().removeAction(action)
        self._recentFileActions = []
