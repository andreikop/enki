import subprocess
import platform
import os.path
import os

from PyQt4.QtGui import QMessageBox, QIcon, QWidget, QHBoxLayout, \
                        QVBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy

from enki.core.core import core
from enki.core.uisettings import TextOption


if platform.system() == 'Windows':
    ACTION_TEXT = "Command Prompt"
else:
    ACTION_TEXT = "Terminal"


def _commandExists(program):
    def _isExe(filePath):
        return os.path.isfile(filePath) and os.access(filePath, os.X_OK)

    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exeFile = os.path.join(path, program)
        if _isExe(exeFile):
            return True

    return False


class SettingsPage(QWidget):
    """Settings page for OpenTerm plugin
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self._hLayout = QHBoxLayout()
        self._label = QLabel("Default Terminal", self)
        self._hLayout.addWidget(self._label)
        self.edit = QLineEdit(self)
        self._hLayout.addWidget(self.edit)

        self._vLayout = QVBoxLayout(self)
        self._vLayout.addLayout(self._hLayout)
        self._vLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))


class Plugin:
    def __init__(self):
        self._initSettings()
        self._addAction()
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)

    def del_(self):
        core.actionManager().removeAction('mTools/aOpenTerm')

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        page = SettingsPage(dialog)
        dialog.appendPage(ACTION_TEXT, page, QIcon(':enkiicons/console.png'))

        # Options
        dialog.appendOption(TextOption(dialog, core.config(), "OpenTerm/DefaultTerm", page.edit))

    def _chooseDefaultTerminal(self):
        if platform.system() == 'Windows':
            if _commandExists('powershell.exe'):
                return 'powershell.exe'
            else:
                return 'cmd.exe'
        elif os.path.isfile('/usr/bin/x-terminal-emulator'):
            return '/usr/bin/x-terminal-emulator'
        else:
            return 'xterm'

    def _initSettings(self):
        """Init setting for the plugin
        """
        if not "OpenTerm" in core.config():  # first start
            core.config()["OpenTerm"] = {"DefaultTerm": self._chooseDefaultTerminal()}

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction( "mTools/aOpenTerm",
                                                 ACTION_TEXT,
                                                 QIcon(':enkiicons/console.png'))
        core.actionManager().setDefaultShortcut(action, "Ctrl+T")
        action.triggered.connect(self._openTerm)

    def _openTerm(self):
        """Handler for main menu action
        """
        term = core.config()["OpenTerm"]["DefaultTerm"]
        cwd = os.getcwd()
        try:
            subprocess.Popen(term, cwd=os.getcwd())
        except Exception as ex:
            QMessageBox.information(core.mainWindow(),
                                    "Failed to open terminal",
                                    "Enki was unable to run '{0}': {1}".format(term, str(ex)))
