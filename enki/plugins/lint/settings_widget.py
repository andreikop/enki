"""Lint plugin settings widget
"""

import os.path

from PyQt4.QtGui import QFileDialog, QWidget
from PyQt4 import uic

from enki.core.core import core
from enki.lib.get_console_output import get_console_output


def _getPylintVersion(path):
    """Get pylint version as tuple of integer items.

    Raise OSError if not found
          ValueError if failed to parse
    """
    stdout, stderr = get_console_output(path, ['--version'])
    try:
        versionLine = [line \
                            for line in stdout.splitlines() \
                                if line.startswith('pylint')][0]
        version = versionLine.split()[1].rstrip(',')
    except IndexError:  # incorrect version string
        raise ValueError()
    return [int(num) \
                for num in version.split('.')]


class SettingsWidget(QWidget):
    """Settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Settings.ui'), self)
        self.pbPylintPath.clicked.connect(self._onPbPylintPathClicked)
        self.lePylintPath.textChanged.connect(self._updateExecuteError)

    def _onPbPylintPathClicked(self):
        path = QFileDialog.getOpenFileName(core.mainWindow(), 'Pylint path')
        if path:
            self.lePylintPath.setText(path)
            self._updateExecuteError(path)

    def _updateExecuteError(self, path):
        """ Check if pylint is installed.

        Return None if OK or textual error
        """
        try:
            version = _getPylintVersion(path)
        except OSError as ex:
            self.lExecuteError.setText('Failed to execute pylint: {}'.format(ex))
        except ValueError:
            self.lExecuteError.setText('Failed to parse pyling version. Does pyling work?')
        else:
            if version[0] >= 1:
                self.lExecuteError.setText('Pylint is found!')
            else:
                versionStr = '.'.join([str(num) for num in version])
                text = 'Not supported pylint version {}. Pylint >= 1 is required.'.format(versionStr)
                self.lExecuteError.setText(text)
