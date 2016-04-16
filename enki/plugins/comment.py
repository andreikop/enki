"""
(Un)comment code lines
"""

from PyQt5.QtCore import QObject

from enki.core.core import core


class Prefix:
    def isCommented(self, line):
        return line.lstrip().startswith(self.PREFIX)

    def comment(self, minIndent, line):
        return '{}{} {}'.format(line[:minIndent], self.PREFIX, line[minIndent:])

    def uncomment(self, minIndent, line):
        spaceLen = len(line) - len(line.lstrip())
        space = line[:spaceLen]
        text = line[spaceLen:]

        if text.startswith('{} '.format(self.PREFIX)):
            text = text[len(self.PREFIX) + 1:]
        elif text.startswith(self.PREFIX):
            text = text[len(self.PREFIX):]

        return space + text


class Hash(Prefix):
    PREFIX = '#'


class DoubleSlash(Prefix):
    PREFIX = '//'


# NOTE PHP supports both // and #
reversedCommentImplementations = {
    Hash: ("Bash", "Zsh", "Tcsh", "Perl", "Python", "Ruby", "R Script",
           "Makefile", "CMake", "Dockerfile",
           "Diff",
           "JSON", "YAML",
           "RPM Spec", "Debian Control"),
    DoubleSlash: ("ActionScript 2.0", "C", "C#", "C++", "D", "Go", "Java", "JavaScript", "Pascal",
                  "Objective-C", "Objective-C++", "PHP/PHP", "Rust", "Scala")
}

commentImplementations = {lang: impl
                          for impl, langs in reversedCommentImplementations.items()
                          for lang in langs
                          }


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
           document.qutepart.language() in commentImplementations):
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
        lines = document.qutepart.lines

        (selLine, selCol), (curLine, curCol) = document.qutepart.selectedPosition

        if (selLine, selCol) == (curLine, curCol):  # no any selection, modify current line
            start = selLine
            end = selLine
            singleLine = True
            rightIndex = len(lines[selLine]) - selCol  # to restore cursor position
        else:
            if (selLine, selCol) > (curLine, curCol):
                selLine, selCol, curLine, curCol = curLine, curCol, selLine, selCol
                swapped = True
            else:
                swapped = False

            if curCol == 0:  # no any characters selected in the last line
                curLine -= 1
                curCol = len(lines[curLine])

            start = min(selLine, curLine)
            end = max(selLine, curLine)

            singleLine = False

        impl = commentImplementations[document.qutepart.language()]()

        if all([impl.isCommented(line)
                for line in lines[start:end + 1]
                if line.strip()]):
            action = impl.uncomment
        else:
            action = impl.comment

        try:
            minIndent = min([len(line) - len(line.lstrip())
                             for line in lines[start:end+1]
                             if line.strip()])
        except ValueError:  # all lines are empty
            return

        with(document.qutepart):
            for index in range(start, end + 1):
                if lines[index].strip():  # if not empty
                    lines[index] = action(minIndent, lines[index])

        if singleLine:
            document.qutepart.cursorPosition = (start, len(lines[start]) - rightIndex)
        else:
            if swapped:
                document.qutepart.selectedPosition = (curLine, len(lines[curLine])), (selLine, 0)
            else:
                document.qutepart.selectedPosition = (selLine, 0), (curLine, len(lines[curLine]))
