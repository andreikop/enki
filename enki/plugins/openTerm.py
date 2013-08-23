import subprocess

from os import path
from PyQt4.QtGui import QMessageBox, QIcon, QWidget, QHBoxLayout, QLabel, QLineEdit

from enki.core.core import core
from enki.core.uisettings import TextOption

class SettingsPage(QWidget):
    """Settings page for Hello World plugin
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self._layout = QHBoxLayout(self)
        self._label = QLabel("Default Terminal", self)
        self._layout.addWidget(self._label)
        self.edit = QLineEdit(self)
        self._layout.addWidget(self.edit)
        

class Plugin:
    def __init__(self):
        self._initSettings()
        self._addAction()
        self._addDock()
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def del_(self):
        pass

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        page = SettingsPage(dialog)
        dialog.appendPage(u"OpenTerm", page)
        
        # Options
        dialog.appendOption(TextOption(dialog, core.config(), "OpenTerm/defaultTerm", page.edit))

    def _initSettings(self):
        """Init setting for the plugin
        """
        if not "OpenTerm" in core.config():  # first start
            core.config()["OpenTerm"] = {}
            core.config()["OpenTerm"]["defaultTerm"] = "xterm"

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction( "mView/aOpenTerm",
                                                 "Open Term",
                                                 QIcon(':enkiicons/enki.png'))
        core.actionManager().setDefaultShortcut(action, "Ctrl+Alt+Shift+T")
        action.triggered.connect(self._openTerm)

    def _openTerm(self):
        """Handler for main menu action
        """
        term = core.config()["OpenTerm"]["defaultTerm"]
        cwd = path.dirname(core.workspace().currentDocument().filePath())
        try:
            subprocess.Popen(term, cwd=cwd)
        except:
            QMessageBox.information(core.mainWindow(), "OpenTerm error", "Enki was unable to open '{0}' terminal".format(term))
            
