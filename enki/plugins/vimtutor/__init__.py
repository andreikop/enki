import os.path

from PyQt4.QtGui import QIcon, QMessageBox

from enki.core.core import core

class Plugin:
    def __init__(self):
        self._action = core.actionManager().addAction('mHelp/aVimTutor',
                                                      'Vim mode tutorial',
                                                      QIcon(":/enkiicons/vim.png"))
        self._action.triggered.connect(self._onTriggered)

    def del_(self):
        core.actionManager().removeAction(self._action)

    def _onTriggered(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'vimtutor.txt'))
        try:
            with open(path) as vimtutor_file:
                text = vimtutor_file.read()
        except Exception as ex:
            QMessageBox.warning(core.mainWindow(),
                                "Failed to read vimtutor text",
                                str(ex))
            return

        document = core.workspace().createEmptyNotSavedDocument()
        document.qutepart.text = text
