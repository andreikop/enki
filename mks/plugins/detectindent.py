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
        core.workspace().documentOpened.connect(self._detectAndApplyIndentation)

    def del_(self):
        """Explicitly called destructor
        """
        core.workspace().documentOpened.disconnect(self._detectAndApplyIndentation)

    def moduleConfiguratorClass(self):
        """Module configurator
        """
        return None

    def _detectAndApplyIndentation(self, document):
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

        if haveTabs:
            document.setIndentUseTabs(True)
        elif haveSpaces:
            document.setIndentUseTabs(False)
        else:
            pass  # Don't touch current mode, if not sure
