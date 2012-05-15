"""
lexer --- QScintilla lexers management
======================================
"""

import os.path
import json

from PyQt4 import uic
from PyQt4.QtGui import QFont, QWidget

from PyQt4.Qsci import *  # pylint: disable=W0401,W0614

from mks.core.core import core
import mks.core.defines

def _getPygmentsSchemeLexer(editor):
    """Construct and return pygments lexer for Scheme. Sets valid language name, lazy import
    """
    try:
        import mks.plugins.editor.lexerpygments
    except ImportError:
        QMessageBox.critical(core.workspace(), "Failed to load pygments",
                             "<html>mksv3 can't highlight Scheme source, "\
                             "because <b>pygments</b> package not found</html>")
        return None
    return mks.plugins.editor.lexerpygments.LexerPygments(editor, 'Scheme')


class Lexer:
    """Wrapper for all Qscintilla lexers. Functionality:
    
    * Choose lexer for a file
    * Apply lexer settings
    """
    LEXER_FOR_LANGUAGE = {
        "Bash"          : QsciLexerBash,
        "Batch"         : QsciLexerBatch,
        "C#"            : QsciLexerCSharp,
        "C++"           : QsciLexerCPP,
        "CMake"         : QsciLexerCMake,
        "CSS"           : QsciLexerCSS,
        "D"             : QsciLexerD,
        "Diff"          : QsciLexerDiff,
        "HTML"          : QsciLexerHTML,
        "IDL"           : QsciLexerIDL,
        "Java"          : QsciLexerJava,
        "JavaScript"    : QsciLexerJavaScript,
        "Lua"           : QsciLexerLua,
        "Makefile"      : QsciLexerMakefile,
        "POV"           : QsciLexerPOV,
        "Perl"          : QsciLexerPerl,
        "Properties"    : QsciLexerProperties,
        "Python"        : QsciLexerPython,
        "Ruby"          : QsciLexerRuby,
        "Spice"         : QsciLexerSpice,
        "SQL"           : QsciLexerSQL,
        "Scheme"        : _getPygmentsSchemeLexer,
        "TeX"           : QsciLexerTeX,
        "VHDL"          : QsciLexerVHDL,
        "TCL"           : QsciLexerTCL,
        "Fortran"       : QsciLexerFortran,
        "Fortran77"     : QsciLexerFortran77,
        "Pascal"        : QsciLexerPascal,
        "PostScript"    : QsciLexerPostScript,
        "XML"           : QsciLexerXML,
        "YAML"          : QsciLexerYAML,
        "Verilog"       : QsciLexerVerilog,
    }

    def __init__(self, editor):
        """editor - reference to parent :class:`mks.plugins.editor.Editor` object
        """
        self._editor = editor
        self.currentLanguage  = None
        self.qscilexer = None
    
    def applyLanguage(self, language):
        """Apply programming language. Changes syntax highlighting mode
        """
        self.currentLanguage = language
        self.qscilexer = None
        # Create lexer
        if self.currentLanguage and \
           self.currentLanguage in self.LEXER_FOR_LANGUAGE:  # if language is supported
            lexerClass =  self.LEXER_FOR_LANGUAGE[self.currentLanguage]
            self.qscilexer = lexerClass(self._editor.qscintilla)
        if self.qscilexer is not None:
            self.applySettings()
            self._editor.qscintilla.setLexer(self.qscilexer)

    def applySettings(self):
        """Apply editor and lexer settings
        """
        if self.qscilexer is None:
            return
        
        # Apply fonts and colors
        defaultFont = QFont(core.config()["Editor"]["DefaultFont"],
                            core.config()["Editor"]["DefaultFontSize"])
        self.qscilexer.setDefaultFont(defaultFont)
        for i in range(128):
            if self.qscilexer.description(i):
                font  = self.qscilexer.font(i)
                font.setFamily(defaultFont.family())
                font.setPointSize(defaultFont.pointSize())
                self.qscilexer.setFont(font, i)
                #lexer->setColor(lexer->defaultColor(i), i);  # TODO configure lexer colors
                #lexer->setEolFill(lexer->defaultEolFill(i), i);
                #lexer->setPaper(lexer->defaultPaper(i), i);
