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


class LexerSettingsWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'EditorLexerSettings.ui'), self)


class LexerConfig:
    """Class manages settings of QScintilla lexers. Functionality:
    
    * Create configuration file with lexer defaults
    * Load and save the file
    """
    _CONFIG_PATH = os.path.join(mks.core.defines.CONFIG_DIR, 'lexers.json')
    instance = None
    
    def __init__(self):
        if os.path.exists(self._CONFIG_PATH):  # File exists, load it
            self.config = self._load()
        else:  # First start, generate file
            self.config = self._defaultConfig()
        LexerConfig.instance = self
    
    def __del__(self):
        LexerConfig.instance = None

    def _defaultConfig(self):
        """Generate default lexer configuration file. File contains QScintilla defaults
        """
        config = {}

        for language, lexerClass in Lexer.LEXER_FOR_LANGUAGE.items():
            if lexerClass == _getPygmentsSchemeLexer:
                continue  # no any configuration for scheme lexer. Don't try to instantile it to avoid warnings
            
            lexerObject = lexerClass(None)

            def _set(key, value):
                config['%s/%s' % (language, key)] = value
            
            for attribute in Lexer.LEXER_BOOL_ATTRIBUTES:
                if hasattr(lexerObject, attribute):
                    _set(attribute, getattr(lexerObject, attribute)())
            _set('indentOpeningBrace', bool(lexerObject.autoIndentStyle() & QsciScintilla.AiOpening))
            _set('indentClosingBrace', bool(lexerObject.autoIndentStyle() & QsciScintilla.AiClosing))
            if hasattr(lexerObject, "indentationWarning"):
                reason = getattr(lexerObject, "indentationWarning")()
                reasonFromQsci = dict((v, k) for k, v in Lexer.PYTHON_INDENTATION_WARNING_TO_QSCI.items())
                if reason == QsciLexerPython.NoWarning:
                    _set('indentationWarning', False)
                    # MkS default reason
                    _set('indentationWarningReason', reasonFromQsci[QsciLexerPython.Inconsistent])
                else:
                    _set('indentationWarning', True)
                    _set('indentationWarningReason', reasonFromQsci[reason])
        
        return config

    def save(self):
        """Save the config
        """
        if self.config == self._defaultConfig():
            try:
                os.path.unlink(self._CONFIG_PATH)
            except:  # nothing to do here
                pass
        else:
            try:
                with open(self._CONFIG_PATH, 'w') as f:
                    json.dump(self.config, f, sort_keys=True, indent=4)
            except (OSError, IOError), ex:
                error = unicode(str(ex), 'utf8')
                text = "Failed to save lexer settings file '%s': %s" % (self._CONFIG_PATH, error)
                core.mainWindow().appendMessage(text)

    def _load(self):
        """Load the config
        """
        try:
            with open(self._CONFIG_PATH, 'r') as f:
                return json.load(f)
        except (OSError, IOError), ex:
            error = unicode(str(ex), 'utf8')
            text = "Failed to load lexer settings file '%s': %s" % (self._CONFIG_PATH, error)
            core.mainWindow().appendMessage(text)
            return None


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

    PYTHON_INDENTATION_WARNING_TO_QSCI = { "Inconsistent"    : QsciLexerPython.Inconsistent,
                                           "TabsAfterSpaces" : QsciLexerPython.TabsAfterSpaces,
                                           "Spaces"          : QsciLexerPython.Spaces,
                                           "Tabs"            : QsciLexerPython.Tabs}

    LEXER_BOOL_ATTRIBUTES =  ("foldComments",
                              "foldCompact",
                              "foldQuotes",
                              "foldDirectives",
                              "foldAtBegin",
                              "foldAtParenthesis",
                              "foldAtElse",
                              "foldAtModule",
                              "foldPreprocessor",
                              "stylePreprocessor",
                              "caseSensitiveTags",
                              "backslashEscapes")
    
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
        if self.qscilexer is None or \
            LexerConfig.instance is None:
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
        
        # Apply language specific settings
        if self.currentLanguage == 'Scheme':
            return

        def _getLexerOPtion(key):
            return LexerConfig.instance.config['%s/%s' % (self.currentLanguage, key)]
        
        for attribute in self.LEXER_BOOL_ATTRIBUTES:
            setterName = 'set' + attribute[0].capitalize() + attribute[1:]
            if hasattr(self.qscilexer, setterName):
                try:  # no key in the previous version
                    getattr(self.qscilexer, setterName)(_getLexerOPtion(attribute))
                except KeyError:
                    pass
        
        autoIndentStyle = 0
        if _getLexerOPtion('indentOpeningBrace'):
            autoIndentStyle &= QsciScintilla.AiOpening
        if _getLexerOPtion('indentClosingBrace'):
            autoIndentStyle &= QsciScintilla.AiClosing
        self.qscilexer.setAutoIndentStyle(autoIndentStyle)
        if hasattr(self.qscilexer, "setIndentationWarning"):
            if _getLexerOPtion('indentationWarning'):
                qsciReason = self.PYTHON_INDENTATION_WARNING_TO_QSCI[_getLexerOPtion('indentationWarningReason')]
                self.qscilexer.setIndentationWarning(qsciReason)
