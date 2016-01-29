"""
detectindent --- Automatic indentation detection
================================================
"""

from enki.core.core import core

# Bigger indents are probably not an indents
_MAX_INDENT = 8
_MIN_INDENT = 2


class Plugin:
    """Plugin interface
    """

    def __init__(self):
        # autodetect indent, need
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().languageChanged.connect(self._onLanguageChanged)

    def terminate(self):
        """Explicitly called destructor
        """
        core.workspace().documentOpened.disconnect(self._onDocumentOpened)
        core.workspace().languageChanged.disconnect(self._onLanguageChanged)

    def _onDocumentOpened(self, document):
        """Signal handler. Document had been opened
        """
        self._detectAndApplyIndentation(document)

    def _onLanguageChanged(self, document, language):
        """Signal handler. Document language had been changed
        """
        if language in ('Makefile', 'Go'):
            document.qutepart.indentUseTabs = True

    def _detectAndApplyIndentation(self, document):
        """Delect indentation automatically and apply detected mode
        Handler for signal from the workspace
        """
        # TODO improve algorighm sometimes to skip comments

        if not core.config()["Qutepart"]["Indentation"]["AutoDetect"]:
            return

        if document.qutepart.language() in ('Makefile', 'Go'):
            document.qutepart.indentUseTabs = True
            return

        def _lineIndent(line):
            """Detect indentation for single line.
            Returns whitespaces from the start of the line
            """
            return line[:len(line) - len(line.lstrip())]

        def _diffIndents(a, b):
            """Compare two indentations and return its difference or None
            """
            if a == b:
                return None
            elif a.startswith(b):
                return a[len(b):]  # rest of a
            elif b.startswith(a):
                return b[len(a):]  # rest of b
            else:  # indents are totally not equal
                return None

        # non-empty lines. Empty (without trailing whitespaces) lines between code blocks break detection algorighm
        lines = [l for l in document.qutepart.lines if l]
        lastIndent = ''
        popularityTable = {}
        for l in lines:
            currentIndent = _lineIndent(l)
            diff = _diffIndents(currentIndent, lastIndent)
            if diff is not None and \
               (len(diff) <= _MAX_INDENT and len(diff) >= _MIN_INDENT) or \
               diff == '\t':
                if diff in popularityTable:
                    popularityTable[diff] += 1
                else:
                    popularityTable[diff] = 1
            lastIndent = currentIndent

        if not popularityTable:  # no indents. Empty file?
            return  # give up

        sortedIndents = sorted(iter(popularityTable.items()), key=lambda item: item[1], reverse=True)
        theMostPopular = sortedIndents[0]

        if len(sortedIndents) >= 2:
            secondPopular = sortedIndents[1]
            if theMostPopular[1] == secondPopular[1]:  # if equal results - give up
                return

        indent, count = theMostPopular
        if count > 2:  # if more than 2 indents
            if indent == '\t':
                document.qutepart.indentUseTabs = True
            elif all([char == ' ' for char in indent]):  # if all spaces
                document.qutepart.indentUseTabs = False
                document.qutepart.indentWidth = len(indent)
        # Else - give up. If can't detect, leave as is
