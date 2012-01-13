"""
schemeindenthelper --- Properly indent new line in a Scheme file
================================================================

This plugin will probably be converted to something more generic, or merged to editor
"""

from PyQt4.QtCore import QObject
from mks.core.core import core

#
# Intergration with the core
#

class Plugin(QObject):
    """Module implementation
    """
    def __init__(self):
        QObject.__init__(self)
        
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        for document in core.workspace().openedDocuments():
            if document.highlightingLanguage() == 'Scheme':
                document.newLineInserted.connect(self._onNewLineInserted)
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings

    def _onDocumentOpened(self, document):
        """New document had been opened. Connect to its signals
        """
        if document.highlightingLanguage() == 'Scheme':
            document.newLineInserted.connect(self._onNewLineInserted)
        document.languageChanged.connect(self._onDocumentLanguageChanged)

    def _onDocumentLanguageChanged(self, old, new):
        """Document language changed. Probably, now it is scheme document
        """
        document = self.sender()
        if old == 'Scheme':
            document.newLineInserted.disconnect(self._onNewLineInserted)
        if new == 'Scheme':
            document.newLineInserted.connect(self._onNewLineInserted)

    def _onNewLineInserted(self):
        """New line inserted to Scheme document. Indent it properly
        """
        editor = self.sender()

        # currently plugin can't deal with tabs correclty, so, don't need to corrupt users file
        if editor.indentUseTabs():
            return

        curAbsPos = editor.absCursorPosition()
        curLine, curCol = editor.cursorPosition()

        linesBefore = editor.lines()[:curLine - 1]
        # if the last line before cursor is empty - use editors default indent
        if linesBefore and not linesBefore[-1].strip():
            return
        
        textBefore = '\n'.join(linesBefore)

        try:
            indentWidth = nextLineIndent(textBefore)
        except UserWarning:  # if we can't parse the text, let's leave default indentation
            return
    
        indent = ' ' * indentWidth
        
        lineText = editor.line(curLine).lstrip()

        editor.setLine(curLine, indent + lineText)
        editor.goTo(line=curLine, col=len(indent))

#
# Plugin functionality
# See http://community.schemewiki.org/?scheme-style

def _lastString(text):
    """Move backward to the start of "" quoted string.
    Return the string
    
    >>> _lastString('asldjfsldf "2345678"')
    '"2345678"'
    >>> _lastString('asldjfsldf foo bar"')
    Traceback (most recent call last):
    ...
    UserWarning: Not closed string
    """
    try:
        return text[text.rindex('"', 0, len(text) - 2):]  # skip closing, search for opening
    except ValueError:
        raise UserWarning("Not closed string")
    
def _lastWord(text):
    """Move backward to the start of the word at the end of a string.
    Return the word
    
    >>> _lastWord( 'aaaaaaaa bbb ccc 1234' )
    '1234'
    >>> _lastWord( 'asdfg' )
    'asdfg'
    >>> _lastWord( '(asdfg' )
    'asdfg'
    >>> _lastWord( ')asdfg' )
    'asdfg'
    """
    for index, char in enumerate(text[::-1]):
        if char.isspace() or \
           char in ('(', ')'):
            return text[len(text) - index :]
    else:
        return text
    
def _lastExpressionInParenthes(origText):
    """Move backward to the expression start. 
    Return count of skipped characters.
    
    >>> _lastExpressionInParenthes( '()' )
    '()'
    >>> _lastExpressionInParenthes( '(myfunc)' )
    '(myfunc)'
    >>> _lastExpressionInParenthes( 'blablabla (myfunc)' )
    '(myfunc)'
    >>> _lastExpressionInParenthes( 'blablabla (myfunc a)' )
    '(myfunc a)'
    >>> _lastExpressionInParenthes( 'blablabla (myfunc (+ a b))' )
    '(myfunc (+ a b))'
    >>> _lastExpressionInParenthes( '(myfunc "asdf")' )
    '(myfunc "asdf")'
    >>> _lastExpressionInParenthes( '(myfunc "as(df")' )
    '(myfunc "as(df")'
    >>> _lastExpressionInParenthes( '(myfunc ("asdf")' )
    '("asdf")'
    >>> _lastExpressionInParenthes( 'myfunc "asdf")' )
    Traceback (most recent call last):
    ...
    UserWarning: Expression start not found
    """
    rest = origText[:-1]  # skip ')'

    found = False
    while rest and not found:
        if rest[-1] == '"':  # string end
            lastStringLen = len(_lastString(rest))
            rest = rest[:-lastStringLen]
        elif rest[-1] == ')':  # nested expression end
            expInParLen = len(_lastExpressionInParenthes(rest))
            rest = rest[:-expInParLen]
        elif rest[-1] == '(':  # ok, expression start had beed found
            rest = rest[:-1]
            found = True
        else:  # remove the last character and continue iteration
            rest = rest[:-1]
    
    if found:
        expressionLen = len(origText) - len(rest)
        return origText[-expressionLen:]
    else:
        raise UserWarning("Expression start not found")

def _lastExpression(text):
    """Move backward to the end of skipped expression.
    Return count of skipped symbols
    
    >>> _lastExpression( ' (myfunc a' )
    'a'
    >>> _lastExpression( ' (myfunc (if (pair? a) a b)' )
    '(if (pair? a) a b)'
    """
    if text.endswith(')'):
        return _lastExpressionInParenthes(text)
    else:
        return _lastWord(text)

def _textBeforeLastExpression(text):
    """Return the line, which is placed Before the last expression in the text
    
    >>> _textBeforeLastExpression('(myfunc a')
    '(myfunc '
    """
    lastExpression = _lastExpression(text)
    return text[:-len(lastExpression)]

def nextLineIndent(text):
    """Parse Scheme source code and suggest indentation for the next line
    Function raises UserWarning, if failed to parse the source
    
    >>> nextLineIndent( '(myfunc a' )
    8
    >>> nextLineIndent( '(myfunc (if (a) a b)' )
    8
    >>> nextLineIndent( '(myfunc a)' )
    0
    >>> nextLineIndent( '  (myfunc a)' )
    2
    >>> nextLineIndent( '    (define' )
    5
    >>> nextLineIndent( 'a\\nb' )
    0
    >>> nextLineIndent( '  a\\n\\n' )
    0
    >>> nextLineIndent( '(define myfunc' )
    2
    >>> nextLineIndent( '(let ((pi 3.14) (r 120))' )
    2
    """
    
    # TODO support comments sometimes, when parsing Scheme sources
    
    text = text.rstrip(' \t')
    textBeforeLastExpression = _textBeforeLastExpression(text)
    
    if not textBeforeLastExpression:
        return 0
    
    lines = textBeforeLastExpression.splitlines()
    if textBeforeLastExpression.endswith('\n'):
        lines.append('')
    
    strippedLastLine = lines[-1].rstrip()
    if strippedLastLine.endswith('define'):  # special case
        return len(strippedLastLine) - len('define') + 1
    if strippedLastLine.endswith('let'):  # special case
        return len(strippedLastLine) - len('let') + 1
    else:
        return len(lines[-1])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
