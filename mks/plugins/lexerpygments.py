"""Module implementing a custom lexer using pygments.

Based on pygments lexer for Eric, written by Detlev Offenbach
"""

import pygments.token
import pygments.lexers
import pygments.styles
import pygments.util

from PyQt4.QtGui import QColor, QFont
from PyQt4.Qsci import QsciScintilla, QsciScintillaBase, QsciLexerCustom, QsciStyle


class LexerPygments(QsciLexerCustom):
    """ 
    Class implementing a custom lexer using pygments.
    """
    def __init__(self, parent = None, language = None):
        """language is language name as recognized by pygments
        """
        QsciLexerCustom.__init__(self, parent)
        self._lexer = None
        self._tokenCache = None
        self._lastBusyId = -1
        
        self._language = 'Scheme'
        
        if parent is not None:
            self._lexer = self._guessLexer(parent.text())
        
        self._style = pygments.styles.get_style_by_name('default')
        
        self.TOKEN_TO_QSTYLE = {token: self._getNextStyleId() for token in pygments.token.STANDARD_TYPES}
        self.QSTYLE_TO_TOKEN = {v: k for k, v in self.TOKEN_TO_QSTYLE.items()}
        
        if parent is not None:
            parent.textChanged.connect(self._onTextChanged)
    
    def _onTextChanged(self):
        """Handler of textChanged signal from the editor.
        Invalidates cached list of tokens
        """
        self._tokenCache = None
    
    def _getNextStyleId(self):
        """Allocate integer ID for QScintlla style
        """
        self._lastBusyId += 1
        if self._lastBusyId == QsciScintillaBase.STYLE_DEFAULT:
            self._lastBusyId = QsciScintillaBase.STYLE_LASTPREDEFINED + 1
        assert self._lastBusyId < 2 ** self.styleBitsNeeded()
        return self._lastBusyId
    
    def _toQColor(self, pygmentsColor):
        """Convert pygments color definition to QColor
        """
        if not pygmentsColor.startswith('#'):
            pygmentsColor = '#' + pygmentsColor
        return QColor(pygmentsColor)
    
    def language(self):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        if self._lexer is None:
            return 'unknown'
        else:
            return self._lexer.name
    
    def description(self, style):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        if style in self.QSTYLE_TO_TOKEN:
            return str(self.QSTYLE_TO_TOKEN[style])
        else:
            return None
    
    def _getPygStyle(self, qStyle):
        """Get pygments style by QScintlla style number
        """
        try:
            token = self.QSTYLE_TO_TOKEN[qStyle]
        except KeyError:
            return None
        
        return self._style.style_for_token(token)

    def defaultColor(self, style):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        pygStyle = self._getPygStyle(style)
        if not pygStyle or not pygStyle['color']:
            return QsciLexerCustom.defaultColor(self, style)

        return self._toQColor(pygStyle['color'])
        
    def defaultPaper(self, style):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        pygStyle = self._getPygStyle(style)
        if not pygStyle or not pygStyle['bgcolor']:
            return self._toQColor(self._style.background_color)
        else:
            return self._toQColor(pygStyle['bgcolor'])
    
    def defaultFont(self, style):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        font = QsciLexerCustom.defaultFont(self, style)
        
        pygStyle = self._getPygStyle(style)
        if not pygStyle:
            return font
        
        font.setBold(pygStyle['bold'])
        font.setItalic(pygStyle['italic'])
        font.setUnderline(pygStyle['underline'])
        return font
    
    def styleBitsNeeded(self):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        return 7
    
    def _guessLexer(self, text):
        """Try to guess a pygments lexer.
        """
        
        lexer = None
        
        if self._language:
            lexerClass = pygments.lexers.find_lexer_class(self._language)
            if lexerClass is not None:
                lexer = lexerClass()
        else:
            # step 1: guess based on filename and text
            if self.editor() is not None and \
               self.editor().parent() is not None and \
               hasattr(self.editor().parent(), 'filePath'):
                fn = self.editor().parent().filePath()  # NOTE mksv3 AbstractTextEditor specific
                if fn:
                    try:
                        lexer = pygments.lexers.guess_lexer_for_filename(fn, text)
                    except pygments.util.ClassNotFound:
                        pass
            
            # step 2: guess on text only
            if lexer is None:
                try:
                    lexer = pygments.lexers.guess_lexer(text)
                except ClassNotFound:
                    pass
        
        return lexer
    
    def _updateTokenCache(self):
        """Reparse the text with pygments
        """
        if self._lexer is None:
            return

        text = unicode(self.editor().text()).encode('utf-8')
        self._tokenCache = self._lexer.get_tokens(text)

    def styleText(self, start, end):
        """QsciLexerCustom method implmentation. See QScintlla docs
        """
        if self._tokenCache is None:
            self._updateTokenCache()

        self.startStyling(0)
        if self._tokenCache is None:
            self.setStyling(end, QsciScintillaBase.STYLE_DEFAULT)
        else:
            cpos = 0
            
            if self.editor().eolMode() == QsciScintilla.EolWindows:
                eolLen = 2
            else:
                eolLen = 1
            
            for token, txt in self._tokenCache:
                style = self.TOKEN_TO_QSTYLE[token]
                
                tlen = len(txt.encode('utf-8'))
                if eolLen > 1:
                    tlen += txt.count('\n')
                if tlen:
                    self.setStyling(tlen, style)
                cpos += tlen
