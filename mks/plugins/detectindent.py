"""
detectindent --- Automatic indentation detection
================================================
"""

from mks.core.core import core


class Plugin:
    """Plugin interface
    """
    def __init__(self):
        #autodetect indent, need
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().languageChanged.connect(self._onLanguageChanged)

    def del_(self):
        """Explicitly called destructor
        """
        core.workspace().documentOpened.disconnect(self._onDocumentOpened)
        core.workspace().languageChanged.disconnect(self._onLanguageChanged)

    def moduleConfiguratorClass(self):
        """Module configurator
        """
        return None

    def _onDocumentOpened(self, document):
        """Signal handler. Document had been opened
        """
        self._detectAndApplyIndentation(document)

    def _onLanguageChanged(self, document, old, new):
        """Signal handler. Document language had been changed
        """
        if new == 'Makefile':
            self._detectAndApplyIndentation(document, True)

    def _detectAndApplyIndentation(self, document, isMakefile=False):
        """Delect indentation automatically and apply detected mode
        Handler for signal from the workspace
        """
        if not core.config()["Editor"]["Indentation"]["AutoDetect"]:
            return

        text = document.text()
        haveTabs = '\t' in text
        for line in text.splitlines():  #TODO improve algorythm sometimes to skip comments
            if line.startswith(' '):
                haveSpaces = True
                break
        else:
            haveSpaces = False

        if haveTabs or isMakefile:
            document.setIndentUseTabs(True)
        elif haveSpaces:
            document.setIndentUseTabs(False)
        else:
            pass  # Don't touch current mode, if not sure
