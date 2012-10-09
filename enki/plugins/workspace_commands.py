"""
workspace_commands --- Open, SaveAs, GotoLine commands
======================================================
"""

import os.path
import glob
import re

from enki.core.core import core
from enki.lib.pathcompleter import makeSuitableCompleter, PathCompleter
from enki.lib.fuzzycompleter import FuzzySearchCompleter, ViewMode, HidedField

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
        core.workspace().currentDocument().goTo(line = self._line - 1)


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
               not os.path.isfile(self._path):
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


class CommandFuzzySearch(AbstractCommand):
    """Fuzzy search command implementation for finding any word from document
    """
    @staticmethod
    def signature():
        return 'z [word]'
    
    @staticmethod
    def description():
        return 'Fuzzy search'

    @staticmethod
    def pattern():
        """Match only C/C++ indentifiers
        """
        from pyparsing import Literal, Optional, Suppress, White, Word, srange  # delayed import, performance optimization

        line = Word(srange("[a-zA-Z_]"), srange("[a-zA-Z0-9_]"))("line")
        pat = Literal('z ') + Suppress(Optional(White())) + Optional(line)
        pat.leaveWhitespace()
        pat.setParseAction(CommandFuzzySearch.create)
        return pat
    
    @staticmethod
    def create(str, loc, tocs):
        """tocs contain typed word for searching
        Return instance of CommandFuzzySearch
        """
        return [CommandFuzzySearch(tocs.line)]

    @staticmethod
    def isAvailable():
        """Searching available if any document opened
        """
        return core.workspace().currentDocument() is not None

    def __init__(self, word):
        self._fuzzy_word = word
    
    def completer(self, text, pos):
        """Retrieve unique words(like C/C++ identifiers) from document and
        call FuzzySearchCompleter for fuzzy searching and display results
        """
        if len(self._fuzzy_word) > 0:
            full_text = core.workspace().currentDocument().text()
            words = re.findall(r"\b([a-zA-Z_]\w*)\b", full_text, re.I);
            word_occurrence = {} # key: unique word, value: count of occurance this word in document stored in list
            for word in words:
                count = word_occurrence.get(word, [0])
                count[0] += 1
                word_occurrence[word] = count
            return FuzzySearchCompleter(self._fuzzy_word, word_occurrence, ViewMode.SEARCH_ANY_WORD)
        else:
            return None

    def constructCommand(self, completableText):
        """Construct command by typed word
        """
        #print "CommandFuzzySearch::constructCommand ", completableText
        return 'z ' + completableText
    
    def isReadyToExecute(self):
        """Return True if any part of word is typed
        """
        #print "CommandFuzzySearch::isReadyToExecute", self._fuzzy_word
        return self._fuzzy_word is not None

    def execute(self):
        """Find first occurance of fuzzy word in document
        and rewind document to this place
        """
        #print "CommandFuzzySearch::execute", self._fuzzy_word
        exp = '\\b' + self._fuzzy_word + '\\b'
        regExp = re.compile(exp)
        text = core.workspace().currentDocument().text()
        matchObject = regExp.search(text)
        if matchObject is None:
            print "CommandFuzzySearch::execute Info: Can't find", '\"' + self._fuzzy_word + '\"', "in document"
            return
        pos = matchObject.start()
        core.workspace().currentDocument().goTo(absPos = pos,
                                                selectionLength = len(self._fuzzy_word))
        return


class CommandShowTags(AbstractCommand):
    """Command implementation displaing tags for current document, previously
    generated by ctags. Algorithm of matching tags and typed word based on fuzzy searching.
    """
    @staticmethod
    def signature():
        return 't [word]'
    
    @staticmethod
    def description():
        return 'Show tags (symbols) for current document'

    @staticmethod
    def pattern():
        """Match only C/C++ indentifiers. For distinguish tags with same identifiers
        to typed word added separator ;" and offset of relativity to first
        similar tags
        """
        from pyparsing import Literal, Optional, Suppress, White, Word, srange  # delayed import, performance optimization

        tag = Word(srange("[a-zA-Z_]"), srange("[a-zA-Z0-9_]"))("tag")
        offsetOfIdenticalTags = Word(srange("[0-9]"))("offset")
        pat = (Literal('t ') + Suppress(Optional(White())) + Optional(tag)
               + Optional(Literal(HidedField.SEPARATOR)) + Optional(offsetOfIdenticalTags))
        pat.leaveWhitespace()
        pat.setParseAction(CommandShowTags.create)
        return pat
    
    @staticmethod
    def create(str, loc, tocs):
        """tocs contain typed tag for searching and offset between similar tags
        Return instance of CommandShowTags
        """
        return [CommandShowTags(tocs.tag, tocs.offset)]

    @staticmethod
    def isAvailable():
        """Tags available only for opened document
        and if file ".tags" exist in directory with this document
        """
        from errno import ENOENT
        
        haveDocument = core.workspace().currentDocument() is not None
        
        if haveDocument:
            openedDoc = core.workspace().currentDocument()
            tagsFileDir = os.path.dirname(openedDoc.filePath())
            tagsFile = os.path.join(tagsFileDir, ".tags")
            haveDocument = os.path.exists(tagsFile)
        return haveDocument

    """SymbolsDict is a dictionary, where:
    key is tag name;
    value - list of tags adresses, because tag may be declared in some places of one document.
    It is global, for preventing scanning tags file each time when created new instance of CommandShowTags
    and called only methods like isReadyToExecute
    """
    SymbolsDict = {}
    
    @staticmethod
    def loadTagFile(path, documentName):
        """Load and parse tags file as described in http://ctags.sourceforge.net/FORMAT
        Result of parsing stores in SymbolsDict
        """
        from errno import ENOENT
        
        try:
            tagsFile = open(path, 'r')
            lines = tagsFile.readlines()
            tagsFile.close()
        except OSError, ex:
            if ex.errno != ENOENT: 
                error = unicode(str(ex), 'utf8')
                text = "Failed opening file '%s': %s" % (path, error)
                core.mainWindow().appendMessage(text)
        
        CommandShowTags.SymbolsDict = {}
        for line in lines:
            #   Skip tag file information
            if line.startswith("!_"):
                continue
            parts = line.split('\t', 2)
            #   Extract tags only for current document
            tagName = parts[0]
            tagFile = parts[1]
            rest = parts[2]
            if tagFile != documentName:
                continue
            #   Extract tag absolute address
            parts = rest.split(";\"\t")
            if len(parts) == 1:
                tagAddress = parts[0]
            elif len(parts) == 2:
                tagAddress = parts[0]
                tagExtensionFields = parts[1]
            else:
                print "CommandShowTags::completer incorrect tag format =", line
            #   Store tag name and it address in SymbolsDict
            symbol = CommandShowTags.SymbolsDict.get(tagName, [])
            symbol.append(tagAddress)
            CommandShowTags.SymbolsDict[tagName] = symbol
        
    def __init__(self, tag, offset):
        """offset is number of relativity to first duplicated tags
        """
        self._fuzzy_word = unicode(tag)
        if offset is not "":
            self._offsetOfIdenticalTags = int(offset)
        else:
            self._offsetOfIdenticalTags = 0
    
    def completer(self, text, pos):
        """Load tags for current document and call FuzzySearchCompleter for fuzzy searching and displaying results
        """
        openedDoc = core.workspace().currentDocument()
        docName = os.path.split(openedDoc.filePath())[1]
        tagsFileDir = os.path.split(openedDoc.filePath())[0]
        tagsFileName = os.path.join(tagsFileDir, ".tags")
        CommandShowTags.loadTagFile(tagsFileName, docName)
        
        return FuzzySearchCompleter(self._fuzzy_word.lower(), CommandShowTags.SymbolsDict, ViewMode.SEARCH_TAGS)

    def constructCommand(self, completableText):
        """Construct command by typed tag
        """
        #print "CommandShowTags::constructCommand", completableText
        return 't ' + completableText
    
    def isReadyToExecute(self):
        """Return True if SymbolsDict have typed tag.
        Store real address of choosed tag (for distinguish between similar tags)
        """
        #print "CommandShowTags::isReadyToExecute", self._fuzzy_word, self._offsetOfIdenticalTags
        if self._fuzzy_word not in CommandShowTags.SymbolsDict:
            return False
        
        tagAddresses = CommandShowTags.SymbolsDict[self._fuzzy_word]
        if self._offsetOfIdenticalTags >= len(tagAddresses):
            print "CommandShowTags::isReadyToExecute Warn: Incorrect tag file", self._offsetOfIdenticalTags, tagAddresses
            return False
        
        self._address = tagAddresses[self._offsetOfIdenticalTags]
        return True

    def execute(self):
        """Rewind document to position of tag, which pointed by field tagAddress in ctags file.
        tagAddress may be:
        - A decimal line number;
        - A search command - defined as regular expression.
        - Combination of both addressing modes, like:
            /^int c;$/
            /struct xyz {/;/int count;/
            389;/struct foo/;/char *s;/
        """
        address = self._address
        #print "CommandShowTags::execute", address
        
        #   Address is decimal line number. Rewind document
        if address.isdigit():
            self._selectTag(int(address) - 1)
            return
        
        #   Parsing combination of line number and regular expression.
        
        #   Check for a decimal line number
        lineNumber = 0
        if address[0].isdigit():
            i = 0
            while address[i].isdigit:
                i += 1
            lineNumber = int(address[0 : i - 1])
            address = address[0 : i] # remove line number and semicolon
        address = address[1 : -1] # remove heading and trailing slashes
        
        absPos = 0  #   TODO add convert line number to absolute position in document
        #   Divide tagAddress(now it may contain only regular expressions) on parts
        # and find next part only after previous part was finded
        parts = address.split("/;/")
        if len(parts) == 0:
            print "CommandShowTags::execute Warn: Incorrect tagAddress =", self._address
            return
        for exp in parts:
            #   Making correct pythonic regular expression
            haveCaret = False
            haveEnd = False
            if exp.startswith("^"):
                haveCaret = True
                exp = exp[1 : ]
            if exp.endswith('$'):
                haveEnd = True
                exp = exp[ : -1]
            exp = re.escape(exp)
            if haveCaret:
                exp = '^' + exp
            if haveEnd:
                exp = exp + '$'
            regExp = re.compile(exp, re.M)
            #   Find tag in entire document
            text = core.workspace().currentDocument().text()
            matchObject = regExp.search(text, absPos)
            if matchObject is None:
                print "CommandShowTags::execute Info: Can't find", '\"' + self._fuzzy_word + '\"', "in document"
                return
            absPos = matchObject.start()
        #   Rewind document
        self._selectTag(absPos)

    def _selectTag(self, linePos):
        """Rewind document and select tag in line, started from linePos
        """
        exp = '\\b' + self._fuzzy_word + '\\b'
        regExp = re.compile(exp)
        text = core.workspace().currentDocument().text()
        matchObject = regExp.search(text, linePos)
        if matchObject is None:
            print "CommandShowTags::_selectTag Info: Can't find", '\"' + self._fuzzy_word + '\"', "in document"
        else:
            core.workspace().currentDocument().goTo(absPos = matchObject.start(),
                                                    selectionLength = len(self._fuzzy_word))


class Plugin:
    """Plugin interface
    """
    def __init__(self):
        for comClass in (CommandGotoLine, CommandOpen, CommandSaveAs, CommandFuzzySearch, CommandShowTags):
            core.locator().addCommandClass(comClass)

    def del_(self):
        """Explicitly called destructor
        """
        for comClass in (CommandGotoLine, CommandOpen, CommandSaveAs, CommandFuzzySearch, CommandShowTags):
            core.locator().removeCommandClass(comClass)
