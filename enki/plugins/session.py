"""
session --- Reopen files when starting
======================================
"""

import sys
import os.path
import json

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
import enki.core.json_wrapper

import shutil

def getSessionFilePath():
    session_name = core.commandLineArgs().get("session_name")
    if not session_name:
        session_name = os.environ.get("ENKI_SESSION")
    # assuming session_name value is secure
    if not session_name:
        return (os.path.join(CONFIG_DIR, 'session.json'), False)
    if '/' not in session_name:
        return (os.path.join(CONFIG_DIR, 'session_%s.json' % session_name), True)
    return (session_name, True);

(_SESSION_FILE_PATH, SESSION_FILE_IS_USER_SPECIFIED) = getSessionFilePath()

class Plugin:
    """Plugin interface
    """
    def __init__(self):
        core.restoreSession.connect(self._onRestoreSession)
        core.backupSession.connect(self._onBackupSession)
        core.aboutToTerminate.connect(self._onAboutToTerminate)

    def del_(self):
        """Explicitly called destructor
        """
        pass

    def _onRestoreSession(self):
        """Enki initialisation finished.
        Now restore session
        """
        # if have documents except 'untitled' new doc, don't restore session
        if core.workspace().currentDocument() is not None:
            return

        if not os.path.exists(_SESSION_FILE_PATH):
            return

        session = enki.core.json_wrapper.load(_SESSION_FILE_PATH, 'session', None)

        if session is not None:
            for filePath in session['opened']:
                if os.path.exists(filePath):
                    core.workspace().openFile(filePath)

            if session['current'] is not None:
                document = self._documentForPath(session['current'])
                if document is not None: # document might be already deleted
                    core.workspace().setCurrentDocument(document)
    
    def _onBackupSession(self):
        """Enki initialisation finished.
        Copy session.json (or something) to session.json.bak
        """
        if not os.path.exists(_SESSION_FILE_PATH):
            return
        
        backup_file = _SESSION_FILE_PATH + ".bak";
        
        if SESSION_FILE_IS_USER_SPECIFIED:
            print >> sys.stderr, "You have specified both session name and a list of files."
            print >> sys.stderr, "Existing session is backed up at %s and will be overwritten." % backup_file
            
        # Backup session regardless of whether the session is named
        shutil.copy(_SESSION_FILE_PATH, backup_file);
        

    def _documentForPath(self, filePath):
        """Find document by it's file path.
        Raises ValueError, if document hasn't been found
        """
        for document in core.workspace().documents():
            if document.filePath() is not None and \
               document.filePath() == filePath:
                return document

        return None

    def _onAboutToTerminate(self):
        """Enki is going to be terminated.
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

        enki.core.json_wrapper.dump(_SESSION_FILE_PATH, 'session', session)
