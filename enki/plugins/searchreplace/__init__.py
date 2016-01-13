"""
searchreplace --- Search and replace functionality
==================================================

Contains search dialog and search/replace in file/directory functionality
"""

from . import controller


class Plugin():
    """Main class of the plugin. Installs and uninstalls plugin to the system
    """

    def __init__(self):
        """Plugin initialisation
        """
        self._controller = controller.Controller()

    def terminate(self):
        """Plugin termination
        """
        self._controller.terminate()
