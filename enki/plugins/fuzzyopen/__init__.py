from enki.core.core import core

from enki.plugins.fuzzyopen.fuzzyopen import FuzzyOpener


class Plugin:
    def __init__(self):
        self._action = core.actionManager().addAction('mNavigation/aFuzzyOpen', 'Fuzzy open')
        core.actionManager().setDefaultShortcut(self._action, "Ctrl+M")
        self._action.triggered.connect(self._onActionTriggered)

    def del_(self):
        core.actionManager().removeAction(self._action)

    def _onActionTriggered(self):
        FuzzyOpener(core.mainWindow()).exec_()
