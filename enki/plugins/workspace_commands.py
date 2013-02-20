"""
workspace_commands --- Open, SaveAs, GotoLine commands
======================================================
"""

import os.path
import glob

from enki.core.core import core
from enki.lib.pathcompleter import makeSuitableCompleter, PathCompleter

from enki.core.locator import AbstractCommand


class CommandGotoLine(AbstractCommand):
    """Go to line command implementation
    """
    @staticmethod
    def signature():
        """Command signature. For Help
        """
        return '[l] [LINE]'
    
    @staticmethod
    def description():
        """Command description. For Help
        """
        return 'Go to line'

    @staticmethod
    def pattern():
        """Pyparsing pattern
        """
        from pyparsing import Literal, Optional, Suppress, White, Word, nums  # delayed import, performance optimization

        line = Word(nums)("line")
        pat = (Literal('l ') + Suppress(Optional(White())) + Optional(line)) ^ line
        pat.leaveWhitespace()
        pat.setParseAction(CommandGotoLine.create)
        return pat
    
    @staticmethod
    def create(str, loc, tocs):
        """Callback for pyparsing. Creates an instance of command
        """
        if tocs.line:
            line = int(tocs.line)
        else:
            line = None
        return [CommandGotoLine(line)]

    @staticmethod
    def isAvailable():
        """Check if command is currently available
        """
        return core.workspace().currentDocument() is not None

    def __init__(self, line):
        self._line = line
    
    def isReadyToExecute(self):
        """Check if command is complete and ready to execute
        """
        return self._line is not None

    def execute(self):
        """Execute the command
        """
        core.workspace().currentDocument().qutepart.cursorPosition = self._line - 1, None


class CommandOpen(AbstractCommand):
    
    @staticmethod
    def signature():
        """Command signature. For Help
        """
        return '[f] PATH [LINE]'
    
    @staticmethod
    def description():
        """Command description. For Help
        """
        return 'Open file. Globs are supported'
    
    @staticmethod
    def pattern():
        """pyparsing pattern
        """
        
        def attachLocation(s, loc, tocs):
            """pyparsing callback. Saves path position in the original string
            """
            return [(loc, tocs[0])]

        from pyparsing import CharsNotIn, Combine, Literal, Optional, White, Word, nums  # delayed import, performance optimization

        path = CharsNotIn(" \t")("path")
        path.setParseAction(attachLocation)
        longPath = CharsNotIn(" \t", min=2)("path")
        longPath.setParseAction(attachLocation)
        slashPath = Combine(Literal('/') + Optional(CharsNotIn(" \t")))("path")
        slashPath.setParseAction(attachLocation)

        pat = ((Literal('f ') + Optional(White()) + Optional(path)) ^ longPath ^ slashPath) + \
                    Optional(White() + Word(nums)("line"))
        pat.leaveWhitespace()
        pat.setParseAction(CommandOpen.create)
        return pat

    @staticmethod
    def create(str, loc, tocs):
        """pyparsing callback. Creates an instance of command
        """
        if tocs.path:
            pathLocation, path = tocs.path
        else:
            pathLocation, path = 0, ''
        
        if tocs.line:
            line = int(tocs.line)
        else:
            line = None
        
        return [CommandOpen(pathLocation, path, line)]

    def __init__(self, pathLocation, path, line):
        self._path = path
        self._pathLocation = pathLocation
        self._line = line
    
    def completer(self, text, pos):
        """Command completer.
        If cursor is after path, returns PathCompleter or GlobCompleter 
        """
        if pos == self._pathLocation + len(self._path) or \
           (not self._path and pos == len(text)):
            return makeSuitableCompleter(self._path, pos - self._pathLocation)
        else:
            return None

    def constructCommand(self, completableText):
        """Construct command by path
        """
        command = 'f ' + completableText
        if self._line is not None:
            command += ' %d' % self._line
        return command

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
            return len(files) > 0 and \
                   all([os.path.isfile(p) for p in files])
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
            for path in glob.iglob(os.path.expanduser(self._path)):
                try:
                    path = os.path.abspath(path)
                except OSError:
                    pass
                expandedPathes.append(path)
        
            # 2 loops, because we should open absolute pathes. When opening files, enki changes its current directory
            for path in expandedPathes:
                if self._line is None:
                    core.workspace().goTo(path)
                else:
                    core.workspace().goTo(path, line = self._line - 1)

        else:  # file may be not existing
            path = os.path.expanduser(self._path)
            if os.path.isfile(path):
                path = os.path.abspath(path)
                if self._line is None:
                    core.workspace().goTo(path)
                else:
                    core.workspace().goTo(path, line = self._line - 1)
            else:
                core.workspace().createEmptyNotSavedDocument(path)


class CommandSaveAs(AbstractCommand):
    """Save As Locator command
    """
    
    @staticmethod
    def signature():
        """Command signature. For Help
        """
        return 's PATH'
    
    @staticmethod
    def description():
        """Command description. For Help
        """
        return 'Save file As'
    
    @staticmethod
    def pattern():
        """pyparsing pattern of the command
        """
        def attachLocation(s, loc, tocs):
            return [(loc, tocs[0])]

        from pyparsing import CharsNotIn, Literal, Optional, White  # delayed import, performance optimization

        path = CharsNotIn(" \t")("path")
        path.setParseAction(attachLocation)

        pat = (Literal('s ') + Optional(White()) + Optional(path))
        pat.leaveWhitespace()
        pat.setParseAction(CommandSaveAs.create)
        return pat

    @staticmethod
    def create(str, loc, tocs):
        """Callback for pyparsing. Creates an instance
        """
        if tocs.path:
            pathLocation, path = tocs.path
        else:
            pathLocation, path = 0, ''
        
        return [CommandSaveAs(pathLocation, path)]

    @staticmethod
    def isAvailable():
        """Check if command is available.
        It is available, if at least one document is opened
        """
        return core.workspace().currentDocument() is not None
    
    def __init__(self, pathLocation, path):
        self._path = path
        self._pathLocation = pathLocation
    
    def completer(self, text, pos):
        """Command Completer.
        Returns PathCompleter, if cursor stays after path
        """
        if pos == self._pathLocation + len(self._path) or \
           (not self._path and pos == len(text)):
            return PathCompleter(self._path, pos - self._pathLocation)
        else:
            return None

    def constructCommand(self, completableText):
        """Construct command by path
        """
        return 'f ' + completableText

    def isReadyToExecute(self):
        """Check if command is complete and ready to execute
        """
        return len(self._path) > 0 and not os.path.isdir(self._path)

    def execute(self):
        """Execute command
        """
        path = os.path.abspath(os.path.expanduser(self._path))
        core.workspace().currentDocument().setFilePath(path)
        core.workspace().currentDocument().saveFile()


class Plugin:
    """Plugin interface
    """
    def __init__(self):
        for comClass in (CommandGotoLine, CommandOpen, CommandSaveAs):
            core.locator().addCommandClass(comClass)

    def del_(self):
        """Explicitly called destructor
        """
        for comClass in (CommandGotoLine, CommandOpen, CommandSaveAs):
            core.locator().removeCommandClass(comClass)
