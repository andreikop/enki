"""
workspace_commands --- Open, SaveAs, GotoLine commands
======================================================
"""

import os.path
import glob

from enki.core.core import core
from enki.lib.pathcompleter import makeSuitableCompleter, PathCompleter

from enki.core.locator import AbstractCommand, InvalidCmdArgs, StatusCompleter


class CommandGotoLine(AbstractCommand):
    """Go to line command implementation
    """
    command = 'l'
    signature = 'l [LINE]<br/>[LINE]'
    description = 'Go to line'
    isDefaultNumericCommand = True

    def __init__(self, args):
        AbstractCommand.__init__(self, args)
        if len(args) != 1:
            raise InvalidCmdArgs()

        try:
            self._line = int(args[0])
        except ValueError:
            raise InvalidCmdArgs()

    @staticmethod
    def isAvailable():
        """Check if command is currently available
        """
        return core.workspace().currentDocument() is not None

    def isReadyToExecute(self):
        """Check if command is complete and ready to execute
        """
        return True

    def execute(self):
        """Execute the command
        """
        core.workspace().currentDocument().qutepart.cursorPosition = self._line - 1, None

    def completer(self):
        return StatusCompleter("Go to line {}".format(self._line))


def _expandDotDirectories(path):
    """Replace ./ and ../ with CURRENT FILE directory

    Current Enki directory is a project directory.
    But it is more comfortable to use current file directory for open and save commands.
    """

    # TODO: Check Windows factor
    if path:
        if path.startswith("./") or path.startswith("../"):
            doc = core.workspace().currentDocument()
            if doc is not None:
                fp = doc.filePath()
                if fp is not None:
                    dn = os.path.dirname(fp)
                    return os.path.join(dn, path)

    return path


class CommandOpen(AbstractCommand):

    command = 'o'
    signature = 'o PATH [LINE]<br/>/PATH [LINE]<br/>./PATH [LINE]<br/>../PATH [LINE]<br/>~/PATH [LINE]'
    description = 'Open file. Globs are supported'
    isDefaultPathCommand = True

    def __init__(self, args):
        AbstractCommand.__init__(self, args)
        if len(args) > 2:
            raise InvalidCmdArgs()

        if args:
            self._path = _expandDotDirectories(args[0])
        else:
            self._path = None

        if len(args) == 2:
            try:
                self._line = int(args[1])
            except ValueError:
                raise InvalidCmdArgs()
        else:
            self._line = None

    def completer(self):
        """Command completer.
        If cursor is after path, returns PathCompleter or GlobCompleter
        """
        if self._path is not None:
            return makeSuitableCompleter(self._path)
        else:
            try:
                curDir = os.getcwd()
            except:
                return None
            return makeSuitableCompleter(curDir + '/')

    @staticmethod
    def _isGlob(text):
        return '*' in text or \
               '?' in text or \
               '[' in text

    def isReadyToExecute(self):
        """Check if command is complete and ready to execute
        """
        if self._isGlob(self._path):
            files = glob.glob(os.path.expanduser(self._path))
            return files and \
                   all([os.path.isfile(f) for f in files])
        else:
            if not self._path:
                return False

            if os.path.exists(self._path) and \
               not os.path.isfile(self._path):  # a directory
                return False

            if self._path.endswith('/'):  # going to create a directory
                return False

            return True

    def execute(self):
        """Execute the command
        """
        if self._isGlob(self._path):
            expandedPathes = []
            for filePath in glob.iglob(os.path.expanduser(self._path)):
                try:
                    absFilePath = os.path.abspath(filePath)
                except OSError:
                    expandedPathes.append(filePath)
                else:
                    expandedPathes.append(absFilePath)

            # 2 loops, because we should open absolute pathes. When opening files, enki changes its current directory
            for path in expandedPathes:
                if self._line is None:
                    core.workspace().goTo(path)
                else:
                    core.workspace().goTo(path, line = self._line - 1)

        else:  # file may be not existing
            path = os.path.expanduser(self._path)
            if os.path.isfile(path):
                try:
                    path = os.path.abspath(path)
                except OSError:  # current dir deleted
                    return

                if self._line is None:
                    core.workspace().goTo(path)
                else:
                    core.workspace().goTo(path, line = self._line - 1)
            else:
                core.workspace().createEmptyNotSavedDocument(path)

    def onItemClicked(self, fullText):
        self._path = fullText

    def lineEditText(self):
        if self._line is not None:
            return '{} {} {}'.format(self.command, self._path, self._line)
        else:
            return '{} {}'.format(self.command, self._path)


class CommandSaveAs(AbstractCommand):
    """Save As Locator command
    """
    command = 's'
    signature = 's PATH'
    description = 'Save file As'

    @staticmethod
    def isAvailable():
        """Check if command is available.
        It is available, if at least one document is opened
        """
        return core.workspace().currentDocument() is not None

    def __init__(self, args):
        AbstractCommand.__init__(self, args)
        if len(args) > 1:
            raise InvalidCmdArgs()

        self._path = _expandDotDirectories(args[0]) if args else ''

    def completer(self):
        """Command Completer.
        Return PathCompleter.
        """
        return PathCompleter(self._path)

    def isReadyToExecute(self):
        """Check if command is complete and ready to execute
        """
        return len(self._path) > 0 and not os.path.isdir(self._path)

    def execute(self):
        """Execute command
        """
        try:
            path = os.path.abspath(os.path.expanduser(self._path))
        except OSError:  # directory deleted
            return

        core.workspace().currentDocument().setFilePath(path)
        core.workspace().currentDocument().saveFile()

    def onItemClicked(self, fullText):
        self._path = fullText

    def lineEditText(self):
        return '{} {}'.format(self.command, self._path)


_CMD_CLASSES = (CommandGotoLine, CommandOpen, CommandSaveAs)


class Plugin:
    """Plugin interface
    """
    def __init__(self):
        for cmdClass in _CMD_CLASSES:
            core.locator().addCommandClass(cmdClass)

    def del_(self):
        """Explicitly called destructor
        """
        for cmdClass in _CMD_CLASSES:
            core.locator().removeCommandClass(cmdClass)
