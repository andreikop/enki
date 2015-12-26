"""
session --- Reopen files when starting
======================================
"""
from PyQt5.QtCore import QTimer

import os.path

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
import enki.core.json_wrapper


_AUTO_SAVE_INTERVAL_MS = 60 * 1000


def getSessionFilePath():
    if core.commandLineArgs()['session_name']:
        session_name = core.commandLineArgs()['session_name']
    elif 'ENKI_SESSION' in os.environ:
        session_name = os.environ['ENKI_SESSION']
    else:
        session_name = ''

    if session_name:
        session_filename = 'session_{}.json'.format(session_name)

        for char in r'<>:"/\|?*' + ' ':  # reserved characters for file name on Windows. By MSDN. And space
            session_filename = session_filename.replace(char, '_')
    else:
        session_filename = 'session.json'

    return os.path.join(CONFIG_DIR, session_filename)


_SESSION_FILE_PATH = getSessionFilePath()


class Plugin:
    """Plugin interface
    """

    def __init__(self):
        core.restoreSession.connect(self._onRestoreSession)
        core.aboutToTerminate.connect(self._saveSession)
        self._timer = QTimer(core)
        self._timer.timeout.connect(self._autoSaveSession)
        self._timer.setInterval(_AUTO_SAVE_INTERVAL_MS)
        self._timer.start()

    def del_(self):
        """Explicitly called destructor
        """
        core.restoreSession.disconnect(self._onRestoreSession)
        core.aboutToTerminate.disconnect(self._saveSession)

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
                if document is not None:  # document might be already deleted
                    core.workspace().setCurrentDocument(document)

            if 'project' in session:
                path = session['project']
                if path is not None and os.path.isdir(path):
                    core.project().open(path)

    def _documentForPath(self, filePath):
        """Find document by it's file path.
        Raises ValueError, if document hasn't been found
        """
        for document in core.workspace().documents():
            if document.filePath() is not None and \
               document.filePath() == filePath:
                return document

        return None

    def _saveSession(self, showWarnings=True):
        """Enki is going to be terminated.
        Save session
        """
        fileList = [document.filePath()
                    for document in core.workspace().documents()
                    if document.filePath() is not None and
                    os.path.exists(document.filePath()) and
                    '/.git/' not in document.filePath() and
                    not (document.fileName().startswith('svn-commit') and
                         document.fileName().endswith('.tmp'))]

        if not fileList:
            return

        currentPath = None
        if core.workspace().currentDocument() is not None:
            currentPath = core.workspace().currentDocument().filePath()

        session = {'current': currentPath,
                   'opened': fileList,
                   'project': core.project().path()}

        enki.core.json_wrapper.dump(_SESSION_FILE_PATH, 'session', session, showWarnings)

    def _autoSaveSession(self):
        self._saveSession(showWarnings=False)
