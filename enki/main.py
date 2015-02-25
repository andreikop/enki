"""
Enki editor entry point.
Do not use this file directly, use
    bin/enki or
    bin/enki.py
"""

import sys
import os.path
import traceback
import logging
import logging.handlers

from optparse import OptionParser  # Replace with argparse, when python 2.6 is not supported

import enki.core.defines


class _StartProfiler:
    def __init__(self, enabled):
        self.enabled = enabled

        if enabled:
            self._steps = []
            from datetime import datetime
            self._importedDateTime = datetime
            self._startTime = datetime.now()

    def stepDone(self, description):
        if not self.enabled:
            return

        self._steps.append((description, self._importedDateTime.now()))

    def printInfo(self):
        if not self.enabled:
            return

        prev = self._startTime
        totalMs = 0
        for description, time in self._steps:
            diff = time - prev
            diffMs = (diff.seconds * 1000.) + (diff.microseconds / 1000)
            totalMs += diffMs
            prev = time
            print '%s: %d' % (description.ljust(30), diffMs)
        print 'Total                         : %d' % totalMs


def excepthook(excepttype, exceptvalue, tracebackobj):
    """Show exception dialog, write to log
    """
    text = ''.join(traceback.format_exception(excepttype, exceptvalue, tracebackobj)).strip()
    text = unicode(text, 'utf8')
    logging.critical(text)

    from PyQt4 import uic
    from PyQt4.QtCore import pyqtSignal, QObject
    from PyQt4.QtGui import QApplication, QDialog

    from enki.core.core import core, DATA_FILES_PATH

    class InGuiThread(QObject):
        """QMessageBox can be shown only from GUI thread,
        Move to GUI thread via signal-slot
        """
        showMessageSignal = pyqtSignal()

        def __init__(self):
            QObject.__init__(self)
            self.moveToThread(QApplication.instance().thread())
            self.showMessageSignal.connect(self.showMessageSlot)
            self.showMessageSignal.emit()

        def showMessageSlot(self):
            dialog = QDialog(core.mainWindow())
            uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/Exception.ui'), dialog)

            dialog.textBrowser.setText(text)

            dialog.exec_()

    core._doNotGargadgeCollectThisObjects.append(InGuiThread())


def _showErrorMessage(haveQt, header, html, plain):
    """Show error message with messagebox
    """
    print >> sys.stderr, header
    print >> sys.stderr, plain
    if haveQt:
        from PyQt4.QtGui import QApplication, QMessageBox
        app = QApplication ( sys.argv )
        QMessageBox.critical(None, header, html)
    else:
        try:
            import tkMessageBox
        except ImportError:
            return
        tkMessageBox.showwarning(header, plain)


def _checkDependencies(profiler):
    """Check if 3rdparty software is installed in the system.
    Notify user, how to install it
    """
    _SEE_SITE_PLAIN = 'See http://enki-editor.org/install-sources.html'
    _SEE_SITE_HTML = \
        'See <a href="http://enki-editor.org/install-sources.html">' \
            'installation instructions</a>'

    try:
        import PyQt4
    except ImportError, ex:
        plain =  'Failed to import Qt4 python bindings:\n' + \
                 str(ex) + '\n' + \
                 _SEE_SITE_PLAIN

        _showErrorMessage(False, 'PyQt4 not found', plain, plain)
        raise ex

    import sip
    sip.setapi('QString', 2)
    sip.setapi('QVariant', 2)

    profiler.stepDone('Import PyQt4')

    try:
        import qutepart
    except ImportError, ex:
        html = "<html>" + \
                    "Failed to import qutepart.<br/>" \
                    "See <a href=\"https://github.com/hlamer/qutepart\">qutepart site</a><br/>" \
                    "Exception:<br/>" + \
                    str(ex) + '<br/>' + \
                    _SEE_SITE_HTML + \
                "</html>"
        plain =  "Failed to import qutepart.\n" \
                 "See https://github.com/hlamer/qutepart\n" + \
                str(ex) + '\n' + \
                _SEE_SITE_PLAIN
        _showErrorMessage(True, "Qutepart not found", html, plain)
        raise ex

    profiler.stepDone('Import Qutepart')

    if qutepart.VERSION[0] != enki.core.defines.QUTEPART_SUPPORTED_MAJOR or \
       qutepart.VERSION[1] < enki.core.defines.QUTEPART_SUPPORTED_MINOR:
        text = "Qutepart version not supported\n" + \
               "This Enki version requires Qutepart {}.>={}.*\n". \
                     format(enki.core.defines.QUTEPART_SUPPORTED_MAJOR,
                            enki.core.defines.QUTEPART_SUPPORTED_MINOR) + \
               "But {}.{}.{} is detected\n\n".format(*qutepart.VERSION)

        html = "<html>" + text.replace('\n', '<br/>') + \
                    _SEE_SITE_HTML + \
                "</html>"
        plain = text + _SEE_SITE_PLAIN

        _showErrorMessage(True, "Not supported Qutepart version", html, plain)
        raise ImportError('Not supported Qutepart')


def _parseCommandLine():
    usage = "\n" \
            "  %prog [options]                             Restore previous session\n" \
            "  %prog [options] FILE [+LINE_NUMBER_TO_GO]   Open file\n" \
            "  %prog [options] FILES                       Open or create files\n"
    parser = OptionParser(usage=usage,
                          version="%prog " + enki.core.defines.PACKAGE_VERSION)

    parser.add_option("-n", "--no-session", dest="no_session", action="store_true",
                      help="Do not restore session")
    
    parser.add_option("-s", "--session", dest="session_name", action="store",
                      help="Session name or file, overrides ENKI_SESSION environment variable")

    parser.add_option("-p", "--profiling", dest="profiling", action="store_true",
                      help="profile initialization and exit. For developers")

    (options, args) = parser.parse_args()

    cmdLine = {"profiling" : options.profiling,
               "session_name": options.session_name,
               "no-session" : options.no_session}

    # Parse +N spec.
    plusNSpecs = filter(lambda s: s.startswith('+'), args)
    files = filter(lambda s: not s.startswith('+'), args)

    if plusNSpecs:
        if len(plusNSpecs) > 1:
            print >> sys.stderr, "Only one +N spec are allowed"
            sys.exit(-1)
        spec = plusNSpecs[0]
        try:
            cmdLine["firstFileLineToGo"] = int(spec[1:])
        except ValueError:
            print >> sys.stderr, "Invalid +N spec value: '%s'" % spec
            sys.exit(-1)


    # Get list of absolute pathes of files to open. List may contain not existing files
    filePathes = [os.path.abspath(arg) for arg in files]
    # convert to unicode for avoid Python <-> Qt interaction problems
    filePathes = [unicode(f, 'utf8') for f in filePathes]
    cmdLine["files"] = filePathes

    return cmdLine


def _openFiles(core, cmdLine, profiler):
    existingFiles = []
    notExistingFiles = []
    dirs = []
    for filePath in cmdLine["files"]:
        if os.path.exists(filePath):
            if os.path.isdir(filePath):
                dirs.append(filePath)
            else:
                existingFiles.append(filePath)
        else:
            notExistingFiles.append(filePath)

    # open file by path and line number
    if "firstFileLineToGo" in cmdLine and \
       len(existingFiles) == 1:
        line = cmdLine["firstFileLineToGo"] - 1  # convert from users to internal indexing
        core.workspace().goTo(existingFiles[0], line=line)
    elif existingFiles or notExistingFiles:
        core.workspace().openFiles(existingFiles)
        for filePath in notExistingFiles:
            core.workspace().createEmptyNotSavedDocument(filePath)
    elif dirs:
        try:
            os.chdir(dirs[0])
        except:
            pass
    else:
        if not cmdLine["no-session"]:
            core.restoreSession.emit()
        profiler.stepDone('Restore session')

        if core.workspace().currentDocument() is None:
            core.workspace().createEmptyNotSavedDocument()


def main():
    cmdLine = _parseCommandLine()

    profiler = _StartProfiler(cmdLine["profiling"])

    try:
        _checkDependencies(profiler)
    except ImportError:
        sys.exit(-1)

    # Imports only here. Hack for ability to get help and version info even on system without PyQt.
    import PyQt4.QtGui
    import qutepart

    logging.basicConfig(level=logging.ERROR)
    logging.getLogger('qutepart').removeHandler(qutepart.consoleHandler)

    sys.excepthook = excepthook

    app = PyQt4.QtGui.QApplication ( sys.argv )
    app.setApplicationName( enki.core.defines.PACKAGE_NAME )
    app.setOrganizationName( enki.core.defines.PACKAGE_ORGANISATION )
    app.setOrganizationDomain( enki.core.defines.PACKAGE_URL )
    app.lastWindowClosed.connect(app.quit)

    profiler.stepDone('Construct application')

    # init the core
    from enki.core.core import core
    core.init(profiler, cmdLine)

    _openFiles(core, cmdLine, profiler)

    profiler.stepDone('Open files')

    if core.workspace().currentDocument():
        core.workspace().currentDocument().setFocus()

    core.mainWindow().loadState()
    profiler.stepDone('Load state')

    core.mainWindow().show()

    profiler.stepDone('Show main window')

    # execute application
    if profiler.enabled:
        core.workspace().forceCloseAllDocuments()
        result = 0
    else:
        result = app.exec_()

    core.term()

    profiler.printInfo()

    profiler.stepDone('Terminate core')

    return result
