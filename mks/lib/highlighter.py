"""
highlighter --- QSyntaxHighlighter implementation
=================================================

Currently this implementation is hardcoded for Scheme language, has limited functionality and 
used only for MIT Scheme terminal. But, it will probably be generic and configurable for any language
"""

import re

from PyQt4.QtGui import QColor, QFont, QSyntaxHighlighter, \
                        QTextBlockUserData, QTextCharFormat, QTextCursor, QTextEdit


class _FoundBrace:
    """Container structure for found in a block brace
    """
    def __init__(self, block, pos, brace):
        self.pos = pos
        self.brace = brace
        self.block = block

class _FoundBracesIterator:
    """Iterator over all braces in the document
    """
    def __init__(self, block, index, forward):
        self._block = block
        self._index = index
        self._forward = forward
    
    def __iter__(self):
        return self
    
    def next(self):
        while True:
            if not self._block.isValid():
                raise StopIteration()
            foundBraces = self._block.userData().foundBraces
            if self._forward:
                if self._index < len(foundBraces):
                    ret = foundBraces[self._index]
                    self._index += 1
                    return ret
                else:  # end of block, switch block and iterate again
                    self._block = self._block.next()
                    self._index = 0
            else:
                if self._index >= 0:
                    ret = foundBraces[self._index]
                    self._index -= 1
                    return ret
                else:  # end of block, switch block and iterate again
                    self._block = self._block.previous()
                    if self._block.isValid():
                        self._index = len(self._block.userData().foundBraces) - 1

class _FoundString:
    """Container structure for found in a block string (quoted sequence of chars)
    """
    def __init__(self, pos, len):
        self.pos = pos
        self.len = len

def _makeFormat(bg=None, fg=None, bold=False):
    """Make QTextCharFormat with gived parameters
    """
    format = QTextCharFormat()
    if bg is not None:
        format.setBackground(QColor(bg))
    if fg is not None:
        format.setForeground(QColor(fg))
    if bold:
        format.setFontWeight(QFont.Bold)

    return format

# TODO have own QPalette
DEFAULT_STYLE = {   'defaultBackground':    QColor("#ffffff"),
                    'defaultForeground':    QColor("#000000"),
                    'matchedBrace':         _makeFormat(bg="#ffff7f", fg="#ff0000"),
                    'unMatchedBrace':       _makeFormat(bg="#ff0000", fg="#ffffff"),
                    'keyword':              _makeFormat(fg="#008000", bold=True),
                    'standardFunction':     _makeFormat(fg="#008000"),
                    'number':               _makeFormat(fg='#666666'),
                    'string':               _makeFormat(fg='#BA2121'),
                }

class Highlighter(QSyntaxHighlighter):
    """Scheme (Lisp dialect) syntax highlighter. See module description
    """
    KEYWORDS = ("case-lambda", "call/cc", "class", "define-class", "exit-handler", "field", "import", "inherit", 
    "init-field", "interface", "let\*-values", "let-values", "let/ec", "mixin", "opt-lambda", "override", "protect",
    "provide", "public", "rename", "require", "require-for-syntax", "syntax", "syntax-case", "syntax-error", "unit/sig",
    "unless", "when", "with-syntax", "and", "begin", "call-with-current-continuation", "call-with-input-file",
    "call-with-output-file", "case", "cond", "define", "define-syntax", "delay", "do", "dynamic-wind", "else",
    "for-each", "if", "lambda", "let", "let\*", "let-syntax", "letrec", "letrec-syntax", "map", "or", "syntax-rules")
    
    STANDARD_FUNCTIONS = ("'", "\*", "\+", ",", ",@", "-", "\.\.\.", "/", ";", "<", "<=", "=", "<=", ">", ">=", "`", "abs",
    "acos", "angle", "append", "apply", "asin", "assoc", "assq", "assv", "atan", "boolean\?", "caar", "cadr",
    "call-with-input-file", "call-with-output-file", "call-with-values", "car", "cdddar", "cddddr", "cdr", "ceiling", 
    "char->integer", "char-alphabetic\?", "char-ci<=\?", "char-ci<\?", "char-ci=\?", "char-ci>=\?", "char-ci>\?",
    "char-downcase", "char-lower-case\?", "char-numeric\?", "char-ready\?", "char-upcase", "char-upper-case\?",
    "char-whitespace\?", "char<=\?", "char<\?", "char=\?", "char>=\?", "char>\?", "char\?", "close-input-port",
    "close-output-port", "complex\?","cons", "cos", "current-input-port", "current-output-port", "denominator",
    "display", "eof-object\?", "eq\?",
    "equal\?", "eqv\?", "eval", "even\?", "exact->inexact", "exact\?", "exp", "expt", "#f", "floor", "force", "gcd", 
    "imag-part", "inexact->exact", "inexact\?", "input-port\?", "integer->char", "integer\?", "interaction-environment",
    "lcm", "length", "list", "list->string", "list->vector", "list-ref", "list-tail", "list\?", "load", "log",
    "magnitude", "make-polar", "make-rectangular", "make-string", "make-vector", "max", "member", "memq", "memv", "min",
    "modulo", "negative\?", "newline", "not", "null-environment", "null\?", "number->string", "number\?", "numerator",
    "odd\?", "open-input-file", "open-output-file", "output-port\?", "pair\?", "peek-char", "port\?", "positive\?",
    "procedure\?", "quasiquote", "quote", "quotient", "rational\?", "rationalize", "read", "read-char", "real-part",
    "real\?", "remainder", "reverse", "round", "scheme-report-environment", "set!", "set-car!", "set-cdr!", "sin",
    "sqrt", "string", "string->list", "string->number", "string->symbol", "string-append", "string-ci<=\?",
    "string-ci<\?", "string-ci=\?", "string-ci>=\?", "string-ci>\?", "string-copy", "string-fill!", "string-length",
    "string-ref", "string-set!", "string<=\?", "string<\?", "string=\?", "string>=\?", "string>\?", "string\?", "substring", 
    "symbol->string", "symbol\?", "#t", "tan", "transcript-off", "transcript-on", "truncate", "values", "vector", 
    "vector->list", "vector-fill!", "vector-length", "vector-ref", "vector-set!", "with-input-from-file",
    "with-output-to-file", "write", "write-char", "zero\?")
    
    NUMBERS = (r"\d", )

    def __init__(self, textEdit):
        QSyntaxHighlighter.__init__(self, textEdit)
        self._textEdit = textEdit
        textEdit.setFont(QFont("Monospace"))

        self._bracePattern = re.compile('[\(\)]')

        """Single line string formatting are applied at the end. Therefore even if some items in the string
        was highlighted with other style, it will be replaced
        """
        self._patternsToApply = { 'keyword':          self._makePatternFromList(self.KEYWORDS),
                                  'standardFunction': self._makePatternFromList(self.STANDARD_FUNCTIONS),
                                  'number':           self._makePatternFromList(self.NUMBERS),
                                }

        textEdit.cursorPositionChanged.connect(self._rehighlightMatchingBraces)
        textEdit.textChanged.connect(self._rehighlightMatchingBraces)  # When user presses Del, cursor is not moved

    def _makePatternFromList(self, strings):
        """Convert list of patterns for keywords, etc to one long pattern
        """
        for s in strings:
            if s[0].isalnum():
                s = r'\b' + s
            else:
                s = r'[^\b]' + s
            if s[-1].isalnum():
                s = s + r'\b'
            else:
                s = s + r'[^\b]'

        pattern = '|'.join(strings)  # join to one pattern
        return re.compile(pattern)

    def highlightBlock(self, text):
        """QSyntaxHighlighter.highlightBlock implementation. Does all job
        """
        self._updateStringIndex(text)
        self._updateBraceIndex(text)

        # Highlight keywords, standard functions etc.
        for style, pattern in self._patternsToApply.items():
            for match in pattern.finditer(text):
                if not self._insideString(match.start()):
                    self.setFormat(match.start(), len(match.group(0)), DEFAULT_STYLE[style])
        
        # Highlight strings
        for foundString in self.currentBlockUserData().foundStrings:
            self.setFormat(foundString.pos, foundString.len, DEFAULT_STYLE["string"])
    
    def _updateBraceIndex(self, text):
        """Regenerate index of found braces for a block
        """
        foundBraces = []
        for match in self._bracePattern.finditer(text):
            if not self._insideString(match.start()):
                foundBraces.append(_FoundBrace(self.currentBlock(), match.start(), match.group(0)))
        
        data = self.currentBlockUserData()
        if data is None:
            data = QTextBlockUserData()
        data.foundBraces = foundBraces
        self.setCurrentBlockUserData(data)
    
    def _findMatchingBrace(self, block, pos, brace):
        """Find matching brace for the brace
        """
        foundBraces = block.userData().foundBraces
        braceIndex = None
        for index, foundBrace in enumerate(foundBraces):
            if foundBrace.pos == pos:
                braceIndex = index
                break;
        else:
            assert 0  # Brace must be found!
        
        forward = brace == '('
        if forward:
            startIndex = braceIndex + 1
        else:
            startIndex = braceIndex - 1
        openedCount = 1
        for foundBrace in _FoundBracesIterator(block, startIndex, forward):
            if foundBrace.brace == brace:
                openedCount += 1
            else:
                openedCount -= 1
            if openedCount == 0:
                return foundBrace
        
        return None

    def _makeBraceExtraSelection(self, block, pos, matched):
        """Make QTextEdit.ExtraSelection for highlighted brace
        """
        sel = QTextEdit.ExtraSelection()
        sel.cursor = QTextCursor(block)
        sel.cursor.setPosition(block.position() + pos, QTextCursor.MoveAnchor)
        sel.cursor.setPosition(block.position() + pos + 1, QTextCursor.KeepAnchor)
        if matched:
            sel.format = DEFAULT_STYLE['matchedBrace']
        else:
            sel.format = DEFAULT_STYLE['unMatchedBrace']
        return sel

    def _updateStringIndex(self, text):
        """Regenerate index of found strings.
        
        This algorythm is suitable for either multiline strings and multiline comments.
        There are no any difference for highlighter
        """
        block = self.currentBlock()
        if block.previous().isValid():
            prevState = block.previous().userState()
        else:
            prevState = 0
        
        start = 0
        state = prevState
        foundStrings = []
        for match in re.finditer('"', text):
            if state:  # string end
                foundStrings.append(_FoundString(start, match.start() + 1 - start))
                state = 0
            else:  # string start
                state = 1
                start = match.start()
        if state:
            foundStrings.append(_FoundString(start, len(text) - start))
        
        block.setUserState(state)

        data = self.currentBlockUserData()
        if data is None:
            data = QTextBlockUserData()
        data.foundStrings = foundStrings
        self.setCurrentBlockUserData(data)
    
    def _insideString(self, pos, block=None):
        """Check if position is inside a string. i.e. keyword and braces in a string must not be highlighted
        """
        if block is None:
            block_ = self.currentBlock()
        else:
            block_ = block
        
        for foundString in block_.userData().foundStrings:
            endPos = foundString.pos + foundString.len - 1
            if pos > endPos:
                return False
            elif pos > foundString.pos:
                return True

    def _rehighlightMatchingBraces(self):
        """Rehighlight matching braces after cursor has been moved or text has been changed
        """
        cursor = self._textEdit.textCursor()
        block = cursor.block()
        pos = None
        brace = None
        if not cursor.atBlockStart():
            charBefore = block.text()[cursor.positionInBlock() - 1]
            if self._bracePattern.match(charBefore) and not self._insideString(cursor.positionInBlock() - 1, block):
                pos = cursor.positionInBlock() - 1
                brace = charBefore
        if brace is None:
            if not cursor.atBlockEnd():
                charAfter = block.text()[cursor.positionInBlock()]
                if self._bracePattern.match(charAfter) and not self._insideString(cursor.positionInBlock(), block):
                    pos = cursor.positionInBlock()
                    brace = charAfter
        
        selections = []
        if brace is not None:
            matchedBrace = self._findMatchingBrace(block, pos, brace)
            if matchedBrace is not None:
                selections.append(self._makeBraceExtraSelection(matchedBrace.block, matchedBrace.pos, True))
                selections.append(self._makeBraceExtraSelection(block, pos, True))
            else:
                selections.append(self._makeBraceExtraSelection(block, pos, False))
        self._textEdit.setExtraSelections(selections)
