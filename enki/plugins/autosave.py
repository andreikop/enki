"""
autosave --- saves all files if enki loses focus
=============================================================
"""
import inspect

from PyQt5.QtWidgets import QApplication, QWidget, QCheckBox, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel

from enki.core.core import core
from enki.core.uisettings import CheckableOption

# DONE Setting page
# DONE checkbox if autosave is activated,
# DONE Cleanup code (Terminate plugin, etc.)

class SettingsPage(QWidget):
    """Settings page for Autosave plugi"""
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        text = """
            <h2>Autosave</h2>
            <p> The Autosave plugin saves your files, if Enki looses focus.</p>
            <p></p>"""
        self._label = QLabel(text, self)
        self.checkbox = QCheckBox('Enable Autosave')
        self._layout = QVBoxLayout(self)
        self._layout.addWidget(self._label)
        self._layout.addWidget(self.checkbox)
        self._layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))

class Plugin:
    """Plugin interface implementation

    The plugin looks for focusWindowChanged event, get all opened files
    and saves them.
    """

    def __init__(self):
        """Connect to QApplication OnFocusChanged event"""
        self._qapplication = QApplication.instance()
        self._qapplication.focusWindowChanged.connect(self._onFocusChanged)

        self._qmainwindow = core.mainWindow()
        self._qmainwindow.destroyed.connect(self._onClose)

        self._checkSettings()

        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def terminate(self):
        """clean up"""
        core.uiSettingsManager().aboutToExecute.disconnect(self._onSettingsDialogAboutToExecute)

    def _onFocusChanged(self, newWindow):
        """Tests if no window is focused"""
        if newWindow == None and self._isAutoSaveActive():
            self._saveFiles()

    def _onClose(self, qobject):
        """Save files on close of main window"""
        self._saveFiles()

    def _saveFiles(self):
        """Saves all open files"""
        for document in core.workspace().documents():
            document.saveFile()

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        page = SettingsPage(dialog)
        dialog.appendPage(u"Autosave", page)

        # Options
        dialog.appendOption(CheckableOption(dialog, core.config(), "Autosave/Active", page.checkbox))

    def _checkSettings(self):
        """Check if settings are present in the core configuration file,
        else create and return them.
        """
        if not "Autosave" in core.config():
            core.config()["Autosave"] = {}
            core.config()["Autosave"]["Active"] = False
        return core.config()["Autosave"]["Active"]

    def _isAutoSaveActive(self):
        """Return if autosave is enabled"""
        return core.config()["Autosave"]["Active"]
