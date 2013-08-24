import subprocess

import os.path
from PyQt4.QtGui import QMessageBox, QIcon, QWidget, QHBoxLayout, \
                        QVBoxLayout, QLabel, QLineEdit, QSpacerItem, QSizePolicy

from enki.core.core import core
from enki.core.uisettings import TextOption


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
        core.actionManager().removeAction('mView/aOpenTerm')

    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        """
        page = SettingsPage(dialog)
        dialog.appendPage(u"Terminal", page, QIcon(':enkiicons/console.png'))
        
        # Options
        dialog.appendOption(TextOption(dialog, core.config(), "OpenTerm/DefaultTerm", page.edit))

    def _initSettings(self):
        """Init setting for the plugin
        """
        if not "OpenTerm" in core.config():  # first start
            core.config()["OpenTerm"] = {}
            if os.path.isfile('/usr/bin/x-terminal-emulator'):
                core.config()["OpenTerm"]["DefaultTerm"] = '/usr/bin/x-terminal-emulator'
            else:
                core.config()["OpenTerm"]["DefaultTerm"] = 'xterm'

    def _addAction(self):
        """Add action to main menu
        """
        action = core.actionManager().addAction( "mView/aOpenTerm",
                                                 "Open Terminal",
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
