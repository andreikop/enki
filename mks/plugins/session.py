"""
session --- Reopen files when starting
======================================
"""

import sys
import os.path
import json

from mks.core.core import core
from mks.core.defines import CONFIG_DIR

_SESSION_FILE_PATH = os.path.join(CONFIG_DIR, 'session.json')

class Plugin:
    """Plugin interface
    """
    def __init__(self):
        core.restoreSession.connect(self._onRestoreSession)
        core.aboutToTerminate.connect(self._onAboutToTerminate)

    def del_(self):
        """Explicitly called destructor
        """
        pass

    def _restoreSession(self):
        """Try to restore session.
        Returns bool result
        """
        # if have documents except 'untitled' new doc, don't restore session
        if core.workspace().currentDocument() is not None:
            return
        
        if not os.path.exists(_SESSION_FILE_PATH):
            return
        
        try:
            with open(_SESSION_FILE_PATH, 'r') as f:
                session = json.load(f)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to load session file '%s': %s" % (_SESSION_FILE_PATH, error)
            core.mainWindow().appendMessage(text)
            return
        
        for filePath in session['opened']:
            if os.path.exists(filePath):
                core.workspace().openFile(filePath)
        
        if session['current'] is not None:
            try:
                document = core.workspace().documentForPath(session['current'])
            except ValueError:  # document might be already deleted
                return
            
            core.workspace().setCurrentDocument(document)
        
    def _onRestoreSession(self):
        """mksv3 initialisation finished.
        Now restore session
        """
        self._restoreSession()
        if core.workspace().currentDocument() is None:  # no session or failed to restore
            if core.workspace().textEditorClass():
                core.workspace().createEmptyNotSavedDocument()

    def _onAboutToTerminate(self):
        """mksv3 is going to be terminated.
        Save session
        """
        fileList = [document.filePath() \
                        for document in core.workspace().documents() \
                            if document.filePath() is not None and \
                                os.path.exists(document.filePath()) and \
                                not '/.git/' in document.filePath() and \
                                not (document.fileName().startswith('svn-commit') and \
                                     document.fileName().endswith('.tmp'))]
        
        if not fileList:
            return

        currentPath = None
        if core.workspace().currentDocument() is not None:
            currentPath = core.workspace().currentDocument().filePath()
        
        session = {'current' : currentPath,
                   'opened' : fileList}
        
        try:
            with open(_SESSION_FILE_PATH, 'w') as f:
                json.dump(session, f, sort_keys=True, indent=4)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to save session file '%s': %s" % (_SESSION_FILE_PATH, error)
            print >> sys.stderr, error
