"""
lexer --- QScintilla lexers management
======================================
"""

import os.path
import json

from PyQt4.QtGui import QColor, QFont, QWidget

import PyQt4.Qsci

from enki.core.core import core
import enki.core.defines

def _getPygmentsSchemeLexer(editor):
    """Construct and return pygments lexer for Scheme. Sets valid language name, lazy import
    """
    try:
        import enki.plugins.editor.lexerpygments
    except ImportError:
        QMessageBox.critical(core.workspace(), "Failed to load pygments",
                             "<html>enki can't highlight Scheme source, "\
                             "because <b>pygments</b> package not found</html>")
        return None
    return enki.plugins.editor.lexerpygments.LexerPygments(editor, 'Scheme')

def _getLexer(editor, lexerName):
    """Get lexer by lexer name
    """
    LEXER_FOR_LANGUAGE = {
        "Bash"          : 'QsciLexerBash',
        "Batch"         : 'QsciLexerBatch',
        "C#"            : 'QsciLexerCSharp',
        "C++"           : 'QsciLexerCPP',
        "CMake"         : 'QsciLexerCMake',
        "CSS"           : 'QsciLexerCSS',
        "D"             : 'QsciLexerD',
        "Diff"          : 'QsciLexerDiff',
        "HTML"          : 'QsciLexerHTML',
        "IDL"           : 'QsciLexerIDL',
        "Java"          : 'QsciLexerJava',
        "JavaScript"    : 'QsciLexerJavaScript',
        "Lua"           : 'QsciLexerLua',
        "Makefile"      : 'QsciLexerMakefile',
        "POV"           : 'QsciLexerPOV',
        "Perl"          : 'QsciLexerPerl',
        "Properties"    : 'QsciLexerProperties',
        "Python"        : 'QsciLexerPython',
        "Ruby"          : 'QsciLexerRuby',
        "Spice"         : 'QsciLexerSpice',
        "SQL"           : 'QsciLexerSQL',
        "TeX"           : 'QsciLexerTeX',
        "VHDL"          : 'QsciLexerVHDL',
        "TCL"           : 'QsciLexerTCL',
        "Fortran"       : 'QsciLexerFortran',
        "Fortran77"     : 'QsciLexerFortran77',
        "Pascal"        : 'QsciLexerPascal',
        "PostScript"    : 'QsciLexerPostScript',
        "XML"           : 'QsciLexerXML',
        "YAML"          : 'QsciLexerYAML',
        "Verilog"       : 'QsciLexerVerilog'
    }
    
    if lexerName == 'Scheme':
        return _getPygmentsSchemeLexer(editor)
    elif lexerName in LEXER_FOR_LANGUAGE:
        className = LEXER_FOR_LANGUAGE[lexerName]
        if hasattr(PyQt4.Qsci, className):
            classObject = getattr(PyQt4.Qsci, className)
            return classObject(editor)
        else:  # old QScintilla, doesn't support this lexer
            return None

class Lexer:
    """Wrapper for all Qscintilla lexers. Functionality:
    
    * Choose lexer for a file
    * Apply lexer settings
    """

    def __init__(self, editor):
        """editor - reference to parent :class:`enki.plugins.editor.Editor` object
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
        if self.currentLanguage:
            self.qscilexer = _getLexer(self._editor, self.currentLanguage)  # might return None
        if self.qscilexer is not None:
            self.applySettings()
            self._editor.qscintilla.setLexer(self.qscilexer)

    def applySettings(self):
        """Apply editor and lexer settings
        """
        if self.qscilexer is None:
            return
        
        # Apply fonts and colors
        config = core.config()["Editor"]
        defaultFont = QFont(config["DefaultFont"],
                            config["DefaultFontSize"])
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
                if config["DefaultDocumentColours"]:
                    self.qscilexer.setPaper(QColor(config["DefaultDocumentPaper"]), i)
                    self.qscilexer.setEolFill(True, i);
                else:
                    self.qscilexer.setPaper(self.qscilexer.defaultPaper(i), i)
                    self.qscilexer.setEolFill(self.qscilexer.defaultEolFill(i), i)

        if config["DefaultDocumentColours"]:
            self.qscilexer.setColor(QColor(config["DefaultDocumentPen"]), 0)
        else:
            self.qscilexer.setColor(self.qscilexer.defaultColor(0), 0)
