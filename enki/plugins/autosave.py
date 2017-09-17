"""
autosave --- saves all files if enki loses focus
=============================================================
"""
import inspect

from PyQt5.QtWidgets import QApplication

from enki.core.core import core

# TODO Setting page
# TODO chechbox if autosave is activated
# TODO checkbox if current file or all files should be saved

class Plugin:
    """Plugin interface implementation

    The plugin add a focus lost event,
    get all opened files and save them.
    """

    def __init__(self):
        """Connect to QApplication OnFocusChanged event"""
        self._qapplication = QApplication.instance()
        self._qapplication.focusWindowChanged.connect(self._onFocusChanged)

    def terminate(self):
        pass

    def _onFocusChanged(self, newWindow):
        """Tests if no window is focused"""
        print("OnFocusChanged")
        if newWindow == None:
            print("Save file")
            self._saveFiles()

    def _saveFiles(self):
        """Saves all open files"""
        for document in core.workspace().documents():
            document.saveFile()
