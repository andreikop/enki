"""
schemeindenthelper --- Properly indent new line in a Scheme file
================================================================

This plugin will probably be converted to something more generic, or merged to editor
"""

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QCheckBox

from mks.core.core import core
import mks.core.abstractdocument
import mks.core.uisettings
#
# Intergration with the core
#

class ModuleConfigurator(mks.core.uisettings.ModuleConfigurator):
    def __init__(self, dialog):
        mks.core.uisettings.ModuleConfigurator.__init__(self, dialog)
        self._wasEnabled = core.config()['SchemeIndentHelper']['Enabled']
        text = "Indent Scheme according to http://community.schemewiki.org/?scheme-style"
        checkBox = QCheckBox(text, dialog)
        dialog.pIndentation.layout().addWidget(checkBox)
        self._options = \
        [   mks.core.uisettings.CheckableOption(dialog, core.config(),
                                                "SchemeIndentHelper/Enabled", checkBox) ]

    def saveSettings(self):
        """Settings are stored in the core configuration file, therefore nothing to do here.
        
        Called by :mod:`mks.core.uisettings`
        """
        pass

    def applySettings(self):
        """Apply settings
        
        Called by :mod:`mks.core.uisettings`
        """
        if core.config()['SchemeIndentHelper']['Enabled']:
            Plugin.instance.install()
        else:
            Plugin.instance.uninstall()


class Plugin(QObject):
    """Module implementation
    """
    instance = None
    
    def __init__(self):
        QObject.__init__(self)
        self._installed = False

        if core.config()['SchemeIndentHelper']['Enabled']:
            self.install()
        Plugin.instance = self
            
    def install(self):
        """Install themselves
        """
        for document in core.workspace().openedDocuments():  # reapply indentation, it might be changed
            self._onDocumentOpened(document)

        if self._installed:
            return
        core.setIndentHelper("Scheme", SchemeIndentHelper)
        core.workspace().documentOpened.connect(self._onDocumentOpened)
        self._installed = True
        
    
    def del_(self):
        """Plugin.uninstall implementation. Clear the indent helper
        """
        if not self._installed:
            return
        core.setIndentHelper("Scheme", None)
        for document in core.workspace().openedDocuments():
            document.languageChanged.disconnect(self._onLanguageChanged)
        self._installed = False

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return ModuleConfigurator
    
    def _onDocumentOpened(self, document):
        """Document opened. Change it's indentation
        """
        if document.highlightingLanguage() == 'Scheme':
            document.setIndentUseTabs(False)
            document.setIndentWidth(1)
        try:
            document.languageChanged.disconnect(self._onLanguageChanged)
        except TypeError:  # not connected
            pass
        document.languageChanged.connect(self._onLanguageChanged)
    
    def _onLanguageChanged(self, old, new):
        """Document language changed. Change it's indentation, if necessary
        """
        if new == 'Scheme':
            document = self.sender()
            document.setIndentUseTabs(False)
            document.setIndentWidth(1)

class SchemeIndentHelper(mks.core.abstractdocument.IndentHelper):
    """IndentHelper implementation
    """
    @staticmethod
    def indent(editor):
        """IndentHelper.indent implementation
        """
        # currently plugin can't deal with tabs correclty, so, don't need to corrupt users file
        if editor.indentUseTabs():
            return None

        curAbsPos = editor.absCursorPosition()
        curLine, curCol = editor.cursorPosition()

        linesBefore = editor.lines()[:curLine]
        
        textBefore = '\n'.join(linesBefore)

        try:
            indentWidth = nextLineIndent(textBefore)
        except UserWarning:  # if we can't parse the text, let's leave default indentation
            return None

        return ' ' * indentWidth

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

def _filterComments(lines):
    """Primitive algorithm for filtering comments.
    Will work incorrectly for multiline comments and for ';' symbol inside a string
    """
    for index in range(len(lines)):
        try:
            foundComment = lines[index].rindex(';')
        except ValueError:
            continue
        lines[index] = lines[index][:foundComment]
    return lines

def _filterEmptyLines(lines):
    """Filter lines, which contain nothing, or contain only spaces
    """
    return filter(lambda l: l.strip(), lines)

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
    2
    >>> nextLineIndent( '(define myfunc' )
    2
    >>> nextLineIndent( '(let ((pi 3.14) (r 120))' )
    2
    """
    
    # TODO support comments sometimes, when parsing Scheme sources
    
    text = text.rstrip()
    textBeforeLastExpression = _textBeforeLastExpression(text)
    
    if not textBeforeLastExpression:
        return 0
    
    lines = textBeforeLastExpression.splitlines()
    if textBeforeLastExpression.endswith('\n'):
        lines.append('')
    lines = _filterComments(lines)
    lines = _filterEmptyLines(lines)
    
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
