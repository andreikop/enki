"""
resporepos --- Restore cursor position in a file
================================================
"""

import sys
import os.path
import json
import time

from mks.core.core import core
from mks.core.defines import CONFIG_DIR

_FILE_PATH = os.path.join(CONFIG_DIR, 'lastpos.json')
_MAX_HISTORY_SIZE = 1024

class Plugin:
    """Plugin interface
    """
    def __init__(self):
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        core.workspace().documentClosed.connect(self._onDocumentClosed)
        self._positions = self._load()  # { file path: (lasttime, position)}

    def del_(self):
        """Explicitly called destructor
        """
        self._save(self._positions)

    def _load(self):
        """Load saved data from a file.
        Returns empty list, if failed to load
        """
        positions = {}
        if os.path.exists(_FILE_PATH):
            try:
                with open(_FILE_PATH, 'r') as f:
                    positions = json.load(f)
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                text = "Failed to load old cursor positions file '%s': %s" % (_FILE_PATH, error)
                core.mainWindow().appendMessage(text)
        return positions
    
    def _save(self, positions):
        """Saves 1000 or less last positions
        """
        if len(positions) > _MAX_HISTORY_SIZE:
            # construct list of turples (path, time, pos)
            positionsAsList = [(item[0], item[1][0], item[1][1]) for item in positions.iteritems()]
            # sort by time
            positionsAsList = sorted(positionsAsList, key = lambda item: item[1], reverse = True)
            # leave only last 1000
            positionsAsList = positionsAsList[:_MAX_HISTORY_SIZE]
            # convert to tuple again
            positions = {}
            for item in positionsAsList:
                positions[item[0]] = (item[1], item[2])
        
        try:
            with open(_FILE_PATH, 'w') as f:
                json.dump(positions, f, sort_keys=True, indent=4)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to save file positions to '%s': %s" % (_FILE_PATH, error)
            print >> sys.stderr, error

    def moduleConfiguratorClass(self):
        """Module configurator
        """
        return None

    def _onDocumentOpened(self, document):
        """Document has been opened, restore position, if known
        """
        if document.filePath() in self._positions:
            time, pos = self._positions[document.filePath()]
            if pos <= len(document.text()):
                document.setCursorPosition(absPos = pos)
        
    def _onDocumentClosed(self, document):
        """Document has been closed. Save position
        """
        absPos = document.absCursorPosition()
        path = document.filePath()
        if absPos != 0:
            self._positions[document.filePath()] = (time.time(), document.absCursorPosition())
        elif path in self._positions:  # Clear zero item. Save space for useful information
            del self._positions[path]
