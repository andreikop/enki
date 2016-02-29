"""
(Un)comment code lines
"""

from PyQt5.QtCore import QObject

from enki.core.core import core


class Python:
    def isCommented(self, line):
        return line.lstrip().startswith('#')

    def comment(self, minIndent, line):
        return line[:minIndent] + '# ' + line[minIndent:]

    def uncomment(self, minIndent, line):
        spaceLen = len(line) - len(line.lstrip())
        space = line[:spaceLen]
        text = line[spaceLen:]

        if text.startswith('# '):
            text = text[2:]
        elif text.startswith('#'):
            text = text[1:]

        return space + text


class Plugin(QObject):

    def __init__(self):
        """Create and install the plugin
        """
        QObject.__init__(self)
        self._action = None
        core.workspace().currentDocumentChanged.connect(self._updateAction)
        core.workspace().languageChanged.connect(self._updateAction)

    def terminate(self):
        """Uninstall the plugin
        """
        core.workspace().currentDocumentChanged.disconnect(self._updateAction)
        core.workspace().languageChanged.disconnect(self._updateAction)
        if self._action is not None:
            core.actionManager().removeAction(self._action)
            del self._action

    def _updateAction(self):
        """Create, show or hide, enable or disable action
        """
        document = core.workspace().currentDocument()
        if(document is not None and
           document.qutepart.language() in ('Python',)):
            if self._action is None:
                self._action = core.actionManager().addAction("mEdit/aUnComment",
                                                              "(Un)comment selected lines",
                                                              shortcut='Ctrl+U')
                self._action.triggered.connect(self._onTriggered)
            self._action.setVisible(True)
        else:
            if self._action is not None:
                self._action.setVisible(False)

    def _onTriggered(self):
        document = core.workspace().currentDocument()
        (selLine, selCol), (curLine, curCol) = document.qutepart.selectedPosition
        start = min(selLine, curLine)
        end = max(selLine, curLine)

        lines = document.qutepart.lines
        impl = Python()

        if impl.isCommented(lines[start]):
            action = impl.uncomment
        else:
            action = impl.comment

        minIndent = min([len(line) - len(line.lstrip())
                         for line in lines[start:end+1]])

        with(document.qutepart):
            for index in range(start, end + 1):
                lines[index] = action(minIndent, lines[index])
