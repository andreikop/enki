"""
restorepos --- Restore cursor position in a file
================================================
"""

import os.path
import time

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
import enki.core.json_wrapper

_FILE_PATH = os.path.join(CONFIG_DIR, 'lastpos.json')
_MAX_HISTORY_SIZE = 1024


class Plugin:
    """Plugin interface
    """

    def __init__(self):
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().documentClosed.connect(self._onDocumentClosed)
        self._positions = enki.core.json_wrapper.load(
            _FILE_PATH, 'cursor positions', {})  # { file path: (lasttime, position)}

    def del_(self):
        """Explicitly called destructor
        """
        self._save(self._positions)

    def _save(self, positions):
        """Saves 1000 or less last positions
        """
        if len(positions) > _MAX_HISTORY_SIZE:
            # construct list of turples (path, time, pos)
            positionsAsList = [(item[0], item[1][0], item[1][1]) for item in positions.items()]
            # sort by time
            positionsAsList = sorted(positionsAsList, key=lambda item: item[1], reverse=True)
            # leave only last 1000
            positionsAsList = positionsAsList[:_MAX_HISTORY_SIZE]
            # convert to tuple again
            positions = {}
            for item in positionsAsList:
                positions[item[0]] = (item[1], item[2])

        enki.core.json_wrapper.dump(_FILE_PATH, 'cursor positions', positions)

    def _onDocumentOpened(self, document):
        """Document has been opened, restore position, if known
        """
        if document.filePath() is None:
            return

        if document.filePath() in self._positions:
            time, pos = self._positions[document.filePath()]
            if pos <= len(document.qutepart.text):
                document.qutepart.absCursorPosition = pos

    def _onDocumentClosed(self, document):
        """Document has been closed. Save position
        """
        absPos = document.qutepart.absCursorPosition
        path = document.filePath()
        if absPos != 0:
            self._positions[document.filePath()] = (time.time(), document.qutepart.absCursorPosition)
        elif path in self._positions:  # Clear zero item. Save space for useful information
            del self._positions[path]
