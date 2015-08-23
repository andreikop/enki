"""Lint plugin settings widget
"""

import os.path

from PyQt4.QtGui import QFileDialog, QWidget
from PyQt4 import uic

from enki.core.core import core
from enki.lib.get_console_output import get_console_output


def _getFlake8Version(path):
    """Get pylint version as tuple of integer items.

    Raise OSError if not found
          ValueError if failed to parse
    """
    stdout = get_console_output([path, '--version'])[0]
    try:
        versionLine = stdout.splitlines()[0]
    except IndexError:  # empty output
        raise ValueError()
    version = versionLine.split()[0]
    return [int(num) \
                for num in version.split('.')]


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbFlake8Path.clicked.connect(self._onPbFlake8PathClicked)
        self.leFlake8Path.textChanged.connect(self._updateExecuteError)

    def _onPbFlake8PathClicked(self):
        path = QFileDialog.getOpenFileName(core.mainWindow(), 'Pylint path')
        if path:
            self.leFlake8Path.setText(path)
            self._updateExecuteError(path)

    def _updateExecuteError(self, path):
        """ Check if pylint is installed.

        Return None if OK or textual error
        """
        try:
            version = _getFlake8Version(path)
        except OSError as ex:
            self.lExecuteError.setText('Failed to execute flake8: {}'.format(ex))
        except ValueError:
            self.lExecuteError.setText('Failed to parse flake8 version. Is it realy flake8?')
        else:
            self.lExecuteError.setText('Flake8 version {} is found!'.format(version))
