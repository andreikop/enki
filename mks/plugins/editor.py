"""
editor --- Text editor. Uses QScintilla internally
==================================================

This text editor is used by default
"""

import os.path
import shutil
import fnmatch

from PyQt4.QtCore import Qt, QEvent
from PyQt4.QtGui import QColor, QFont, QFrame, QIcon, QKeyEvent, QVBoxLayout

from PyQt4.Qsci import *

import mks.core.abstractdocument
from mks.core.core import core

from mks.core.config import Config

class _QsciScintilla(QsciScintilla):
    """QsciScintilla wrapper class created only for filter Shift+Tab events.
    
    When Shift+Tab pressed - Qt moves focus, but it is not desired behaviour
    """    
    def keyPressEvent(self, event):
        """Key pressing handler
        """
        if event.key() == Qt.Key_Backtab:
            event.accept()
            newev = QKeyEvent(event.type(), Qt.Key_Tab, Qt.ShiftModifier)
            super(_QsciScintilla, self).keyPressEvent(newev)
        else:
            super(_QsciScintilla, self).keyPressEvent(event)

class EditorConfigurator():  # FIXME ModuleConfigurator
    def __init__(self, dialog):
        self._options = []
        self._createEditorSettings(dialog)
        self._createLexerSettings(dialog)
    
    def _createEditorSettings(self, dialog):
        cfg = core.config()
        from mks.plugins.uisettings import CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption  # FIXME
        self._options.append(CheckableOption(dialog, cfg, "Editor/Indentation/ConvertUponOpen", dialog.cbConvertIndentationUponOpen))
        self._options.append(CheckableOption(dialog, cfg, "Editor/CreateBackupUponOpen", dialog.cbCreateBackupUponOpen))
        self._options.append(ColorOption(dialog, cfg, "Editor/SelectionBackgroundColor", dialog.tbSelectionBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/SelectionForegroundColor", dialog.tbSelectionForeground))
        self._options.append(CheckableOption(dialog, cfg, "Editor/DefaultDocumentColours", dialog.gbDefaultDocumentColours))
        self._options.append(ColorOption(dialog, cfg, "Editor/DefaultDocumentPen", dialog.tbDefaultDocumentPen))
        self._options.append(ColorOption(dialog, cfg, "Editor/DefaultDocumentPaper", dialog.tbDefaultDocumentPaper))
        self._options.append(FontOption(dialog, cfg, "Editor/DefaultFont", "Editor/DefaultFontSize",
                            dialog.lDefaultDocumentFont, dialog.pbDefaultDocumentFont))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/AutoCompletion/Enabled", dialog.gbAutoCompletion))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/AutoCompletion/Source",
                            (dialog.rbDocument, dialog.rbApi, dialog.rbFromBoth),
                            Editor._AUTOCOMPLETION_MODE_TO_QSCI.keys()))
        self._options.append(CheckableOption(dialog, cfg, "Editor/AutoCompletion/CaseSensitivity", dialog.cbAutoCompletionCaseSensitivity))
        self._options.append(CheckableOption(dialog, cfg, "Editor/AutoCompletion/ReplaceWord", dialog.cbAutoCompletionReplaceWord))
        self._options.append(CheckableOption(dialog, cfg, "Editor/AutoCompletion/ShowSingle", dialog.cbAutoCompletionShowSingle))
        self._options.append(NumericOption(dialog, cfg, "Editor/AutoCompletion/Threshold", dialog.sAutoCompletionThreshold))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/CallTips/Enabled", dialog.gbCalltips))
        self._options.append(NumericOption(dialog, cfg, "Editor/CallTips/VisibleCount", dialog.sCallTipsVisible))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/CallTips/Style",
                            (dialog.rbCallTipsNoContext, dialog.rbCallTipsContext, dialog.rbCallTipsNoAutoCompletionContext),
                            Editor._CALL_TIPS_STYLE_TO_QSCI.keys()))
        self._options.append(ColorOption(dialog, cfg, "Editor/CallTips/BackgroundColor", dialog.tbCalltipsBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/CallTips/ForegroundColor", dialog.tbCalltipsForeground))
        self._options.append(ColorOption(dialog, cfg, "Editor/CallTips/HighlightColor", dialog.tbCalltipsHighlight))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/Indentation/Guides", dialog.gbIndentationGuides))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/Indentation/UseTabs",
                            (dialog.rbIndentationSpaces, dialog.rbIndentationTabs),
                            (False, True)))
        self._options.append(CheckableOption(dialog, cfg, "Editor/Indentation/AutoDetect", dialog.cbAutodetectIndent))
        self._options.append(NumericOption(dialog, cfg, "Editor/Indentation/Width", dialog.sIndentationWidth))
        self._options.append(ColorOption(dialog, cfg, "Editor/Indentation/GuidesBackgroundColor", dialog.tbIndentationGuidesBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/Indentation/GuidesForegroundColor", dialog.tbIndentationGuidesForeground))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/BraceMatching/Enabled", dialog.gbBraceMatchingEnabled))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/BraceMatching/Mode",
                            (dialog.rbStrictBraceMatch, dialog.rbSloppyBraceMatch),
                            Editor._BRACE_MATCHING_TO_QSCI.keys()))
        self._options.append(ColorOption(dialog, cfg, "Editor/BraceMatching/MatchedForegroundColor", dialog.tbMatchedBraceForeground))
        self._options.append(ColorOption(dialog, cfg, "Editor/BraceMatching/MatchedBackgroundColor", dialog.tbMatchedBraceBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/BraceMatching/UnmatchedBackgroundColor", dialog.tbUnmatchedBraceBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/BraceMatching/UnmatchedForegroundColor", dialog.tbUnmatchedBraceForeground))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/Edge/Enabled", dialog.gbEdgeModeEnabled))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/Edge/Mode", (dialog.rbEdgeLine, dialog.rbEdgeBackground),
                            Editor._EDGE_MODE_TO_QSCI.keys()))
        self._options.append(NumericOption(dialog, cfg, "Editor/Edge/Column", dialog.sEdgeColumnNumber))
        self._options.append(ColorOption(dialog, cfg, "Editor/Edge/Color", dialog.tbEdgeColor))

        self._options.append(CheckableOption(dialog, cfg, "Editor/Caret/LineVisible", dialog.gbCaretLineVisible))
        self._options.append(ColorOption(dialog, cfg, "Editor/Caret/LineBackgroundColor", dialog.tbCaretLineBackground))
        self._options.append(ColorOption(dialog, cfg, "Editor/Caret/ForegroundColor", dialog.tbCaretForeground))
        self._options.append(NumericOption(dialog, cfg, "Editor/Caret/Width", dialog.sCaretWidth))

        self._options.append(ChoiseOption(dialog, cfg, "Editor/EOL/Mode", (dialog.rbEolUnix, dialog.rbEolWindows, dialog.rbEolMac),
                            Editor._EOL_CONVERTOR_TO_QSCI.keys()))
        self._options.append(CheckableOption(dialog, cfg, "Editor/EOL/Visibility", dialog.cbEolVisibility))
        self._options.append(CheckableOption(dialog, cfg, "Editor/EOL/AutoDetect", dialog.cbAutoDetectEol))
        self._options.append(CheckableOption(dialog, cfg, "Editor/EOL/AutoConvert", dialog.cbAutoEolConversion))
        self._options.append(ChoiseOption(dialog, cfg, "Editor/WhitespaceVisibility",
                            (dialog.rbWsInvisible, dialog.rbWsVisible, dialog.rbWsVisibleAfterIndent),
                            Editor._WHITE_MODE_TO_QSCI.keys()))
        
        self._options.append(CheckableOption(dialog, cfg, "Editor/Wrap/Enabled", dialog.cbWrapLongLines))
    
    def _createLexerSettings(self, dialog):
        lexerItem = dialog.twMenu.findItems("Language", Qt.MatchExactly | Qt.MatchRecursive)[0]
        editor = core.workspace().currentDocument()

        if editor is None or \
           editor._lexer._currentLanguage is None:  # If language is unknown
            lexerItem.setDisabled(True)
            return
        
        lexerConfig = Plugin.instance.lexerConfig._config
        lexerItem.setText(0, editor._lexer._currentLanguage)
        lexer = editor._lexer._qscilexer
        beginning = "%s/" % editor._lexer._currentLanguage
        
        boolAttributeControls = (dialog.cbLexerFoldComments,
                                 dialog.cbLexerFoldCompact,
                                 dialog.cbLexerFoldQuotes,
                                 dialog.cbLexerFoldDirectives,
                                 dialog.cbLexerFoldAtBegin,
                                 dialog.cbLexerFoldAtParenthesis,
                                 dialog.cbLexerFoldAtElse,
                                 dialog.cbLexerFoldAtModule,
                                 dialog.cbLexerFoldPreprocessor,
                                 dialog.cbLexerStylePreprocessor,
                                 dialog.cbLexerCaseSensitiveTags,
                                 dialog.cbLexerBackslashEscapes)
        
        from mks.plugins.uisettings import CheckableOption, ChoiseOption  # fixme
        
        for attribute, control in zip(_LexerConfiguration._LEXER_BOOL_ATTRIBUTES, boolAttributeControls):
            if hasattr(lexer, attribute):
                self._options.append(CheckableOption(dialog, lexerConfig, beginning + attribute, control))
            else:
                control.hide()

        self._options.append(CheckableOption(dialog, lexerConfig, beginning + "indentOpeningBrace", dialog.cbLexerIndentOpeningBrace))
        self._options.append(CheckableOption(dialog, lexerConfig, beginning + "indentClosingBrace", dialog.cbLexerIndentClosingBrace))

        if hasattr(lexer, "indentationWarning"):
            self._options.append(CheckableOption(dialog, lexerConfig, beginning + "indentationWarning", dialog.gbLexerHighlightingIndentationWarning))
            self._options.append(ChoiseOption(dialog, lexerConfig, beginning + "indentationWarningReason", 
                                             (dialog.cbIndentationWarningInconsistent,
                                              dialog.cbIndentationWarningTabsAfterSpaces,
                                              dialog.cbIndentationWarningTabs,
                                              dialog.cbIndentationWarningSpaces),
                                              _Lexer._PYTHON_INDENTATION_WARNING_TO_QSCI.keys()))
        else:
            dialog.gbLexerHighlightingIndentationWarning.hide()

    def saveSettings(self):
        # Main settings should be saved by the core
        Plugin.instance.lexerConfig._config.flush()
    
    def applySettings(self):
        for document in core.workspace().openedDocuments():
            document.applySettings()
            document._lexer._applySettings()

class _LexerConfiguration:
    """Class manages settings of QScintilla lexers. Functionality:
    * Create configuration file with lexer defaults
    * Load and save the file
    """
    _CONFIG_PATH = os.path.expanduser('~/.mksv3.lexers.cfg')
    _LEXER_BOOL_ATTRIBUTES = ("foldComments",
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
    
    def __init__(self):
        if os.path.exists(self._CONFIG_PATH):  # File exists, load it
            try:
                self._config = Config(True, self._CONFIG_PATH)
            except UserWarning, ex:
                core.messageManager().appendMessage(unicode(str(ex), 'utf_8'))
                self._config = None
            self._convertConfigValueTypes()
        else:  # First start, generate file
            self._config = Config(True, self._CONFIG_PATH)
            self._generateDefaultConfig()
            self._config.flush()

    def _convertConfigValueTypes(self):
        """There are no scheme for lexer configuration, therefore need to convert types manually
        """
        for languageOptions in self._config.itervalues():
            for key in languageOptions.iterkeys():
                value = languageOptions[key]
                if value == 'True':
                    languageOptions[key] = True
                elif value == 'False':
                    languageOptions[key] = False
                elif value.isdigit():
                    languageOptions[key] = int(value)

    def _generateDefaultConfig(self):
        for language, lexerClass in _Lexer._lexerForLanguage.items():
            self._config[language] = {}
            lexerSection = self._config[language]
            lexerObject = lexerClass()

            for attribute in _LexerConfiguration._LEXER_BOOL_ATTRIBUTES:
                if hasattr(lexerObject, attribute):
                    lexerSection[attribute] = getattr(lexerObject, attribute)()
            lexerSection['indentOpeningBrace'] = bool(lexerObject.autoIndentStyle() & QsciScintilla.AiOpening)
            lexerSection['indentClosingBrace'] = bool(lexerObject.autoIndentStyle() & QsciScintilla.AiClosing)
            if hasattr(lexerObject, "indentationWarning"):
                reason = getattr(lexerObject, "indentationWarning")()
                reasonFromQsci = dict((v, k) for k, v in _Lexer._PYTHON_INDENTATION_WARNING_TO_QSCI.items())
                if reason == QsciLexerPython.NoWarning:
                    lexerSection['indentationWarning'] = False
                    # MkS default reason
                    lexerSection['indentationWarningReason'] = reasonFromQsci[QsciLexerPython.Inconsistent]
                else:
                    lexerSection['indentationWarning'] = True
                    lexerSection['indentationWarningReason'] = reasonFromQsci[reason]

class _Lexer:
    """Wrapper for all Qscintilla lexers. Functionality:
    * Choose lexer for file
    * Apply lexer settings
    """
    _lexerForLanguage = {
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
        "SQL"           : QsciLexerSQL,
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
        "Spice"         : QsciLexerSpice,
    }

    _PYTHON_INDENTATION_WARNING_TO_QSCI = {"Inconsistent"    : QsciLexerPython.Inconsistent,
                                           "TabsAfterSpaces" : QsciLexerPython.TabsAfterSpaces,
                                           "Spaces"          : QsciLexerPython.Spaces,
                                           "Tabs"            : QsciLexerPython.Tabs}
    
    def __init__(self, editor):
        """editor - reference to parent :class:`mks.plugins.editor.Editor` object
        """
        self._editor = editor
        # Detect language
        self._currentLanguage = self._getLanguage()
        # Create lexer
        if self._currentLanguage:
            lexerClass =  self._lexerForLanguage[self._currentLanguage]
            self._qscilexer = lexerClass()
            self._applySettings()
            self._editor.qscintilla.setLexer(self._qscilexer)
    
    def _getLanguage(self):
        """Get language name by file path
        """
        if not self._editor.filePath():  #  None or empty
            return None
        
        for language in self._lexerForLanguage.iterkeys():
            for pattern in core.config()["Editor"]["Assotiations"][language]:
                if fnmatch.fnmatch(self._editor.filePath(), pattern):
                    return language
        else:
            return None
        
    def _applySettings(self):
        # Apply fonts and colors
        defaultFont = QFont(core.config()["Editor"]["DefaultFont"],
                            core.config()["Editor"]["DefaultFontSize"])
        self._qscilexer.setDefaultFont(defaultFont)
        for i in range(128):
            if self._qscilexer.description(i):
                font  = self._qscilexer.font(i)
                font.setFamily(defaultFont.family())
                self._qscilexer.setFont(font, i)
                #lexer->setColor(lexer->defaultColor(i), i);  # TODO configure lexer colors
                #lexer->setEolFill(lexer->defaultEolFill(i), i);
                #lexer->setPaper(lexer->defaultPaper(i), i);
        
        # Apply language specific settings
        lexerSection = Plugin.instance.lexerConfig._config[self._currentLanguage]  # FIXME 
        
        for attribute in _LexerConfiguration._LEXER_BOOL_ATTRIBUTES:
            setterName = 'set' + attribute[0].capitalize() + attribute[1:]
            if hasattr(self._qscilexer, setterName):
                getattr(self._qscilexer, setterName)(lexerSection[attribute])
        
        autoIndentStyle = 0
        if lexerSection['indentOpeningBrace']:
            autoIndentStyle &= QsciScintilla.AiOpening
        if lexerSection['indentClosingBrace']:
            autoIndentStyle &= QsciScintilla.AiClosing
        self._qscilexer.setAutoIndentStyle(autoIndentStyle)
        
        if hasattr(self._qscilexer, "setIndentationWarning"):
            if lexerSection['indentationWarning']:
                qsciReason = self._PYTHON_INDENTATION_WARNING_TO_QSCI[lexerSection['indentationWarningReason']]
                self._qscilexer.setIndentationWarning(qsciReason)
        
        self._editor.qscintilla.setLexer(self._qscilexer)  # Settings are not applied without this action


class Editor(mks.core.abstractdocument.AbstractDocument):
    """Text editor widget.
    
    Uses QScintilla internally
    """
    
    _MARKER_BOOKMARK = -1  # QScintilla marker type
    
    _EOL_CONVERTOR_TO_QSCI = {r'\n'     : QsciScintilla.EolUnix,
                              r'\r\n'   : QsciScintilla.EolWindows,
                              r'\r'     : QsciScintilla.EolMac}
    
    _EOL_CONVERTOR_FROM_QSCI = {QsciScintilla.EolWindows    : r"\r\n",
                                QsciScintilla.EolUnix       : r"\n",
                                QsciScintilla.EolMac        : r"\r"}
    
    _WRAP_MODE_TO_QSCI = {"WrapWord"      : QsciScintilla.WrapWord,
                          "WrapCharacter" : QsciScintilla.WrapCharacter}
    
    _WRAP_FLAG_TO_QSCI = {"None"           : QsciScintilla.WrapFlagNone,
                          "ByText"         : QsciScintilla.WrapFlagByText,
                          "ByBorder"       : QsciScintilla.WrapFlagByBorder}

    _EDGE_MODE_TO_QSCI = {"Line"        : QsciScintilla.EdgeLine,
                          "Background"  : QsciScintilla.EdgeBackground} 
    
    _WHITE_MODE_TO_QSCI = {"Invisible"           : QsciScintilla.WsInvisible,
                           "Visible"             : QsciScintilla.WsVisible,
                           "VisibleAfterIndent"  : QsciScintilla.WsVisibleAfterIndent}
        
    _AUTOCOMPLETION_MODE_TO_QSCI = {"APIs"      : QsciScintilla.AcsAPIs,
                                    "Document"  : QsciScintilla.AcsDocument,
                                    "All"       : QsciScintilla.AcsAll}
    
    _BRACE_MATCHING_TO_QSCI = {"Strict"    : QsciScintilla.StrictBraceMatch,
                               "Sloppy"    : QsciScintilla.SloppyBraceMatch}
    
    _CALL_TIPS_STYLE_TO_QSCI = {"NoContext"                : QsciScintilla.CallTipsNoContext,
                                "NoAutoCompletionContext"  : QsciScintilla.CallTipsNoAutoCompletionContext,
                                "Context"                  : QsciScintilla.CallTipsContext}
    
    def __init__(self, parentObject, filePath):
        super(Editor, self).__init__(parentObject, filePath)
        
        # Configure editor
        self.qscintilla = _QsciScintilla(self)
        
        pixmap = QIcon(":/mksicons/bookmark.png").pixmap(16, 16)
        self._MARKER_BOOKMARK = self.qscintilla.markerDefine(pixmap, -1)
        
        self.initQsciShortcuts()

        self.qscintilla.installEventFilter(self)
        
        #self.qscintilla.markerDefine(QPixmap(":/editor/bookmark.png").scaled(self.mPixSize), mdBookmark)
        
        self.qscintilla.setUtf8(True) # deal with utf8
        
        self.qscintilla.setAttribute(Qt.WA_MacSmallSize)
        self.qscintilla.setFrameStyle(QFrame.NoFrame | QFrame.Plain)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qscintilla)
        
        self.setFocusProxy(self.qscintilla)
        # connections
        self.qscintilla.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.qscintilla.modificationChanged.connect(self.modifiedChanged)
        self.qscintilla.linesChanged.connect(self._onLinesChanged)
        
        self.applySettings()
        self._lexer = _Lexer(self)
        
        if filePath:
            try:
                text = self._readFile(filePath)
            except IOError, ex:  # exception in constructor
                self.deleteLater()  # make sure C++ object deleted
                raise ex
            self.setText(text)
        
        myConfig = core.config()["Editor"]
        
        # make backup if needed
        if  myConfig["CreateBackupUponOpen"]:
            if self.filePath():
                try:
                    shutil.copy(self.filePath(), self.filePath() + '.bak')
                except (IOError, OSError), ex:
                    self.deleteLater()
                    raise ex
        
        #autodetect indent, need
        if  myConfig["Indentation"]["AutoDetect"]:
            self._autoDetectIndent()
        
        # convert tabs if needed
        if  myConfig["Indentation"]["ConvertUponOpen"]:
            self._convertIndentation()
        
        #autodetect eol, need
        if  myConfig["EOL"]["AutoDetect"]:
            self._autoDetectEol()
        
        # convert eol
        if  myConfig["EOL"]["AutoConvert"]:
            oldText = self.qscintilla.text()
            self.qscintilla.convertEols(self.qscintilla.eolMode())
            text = self.qscintilla.text()
            if text != oldText:
                core.messageManager().appendMessage('EOLs converted. You can UNDO the changes', 5000)
        self.modifiedChanged.emit(self.isModified())
        self.cursorPositionChanged.emit(*self.cursorPosition())

    def initQsciShortcuts(self):
        qsci = self.qscintilla
        qsci.SendScintilla( qsci.SCI_CLEARALLCMDKEYS )
        # Some shortcuts are hardcoded there.
        #If we made is a QActions, it will shadow Qt default keys for move focus, etc
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_TAB, qsci.SCI_TAB);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_ESCAPE, qsci.SCI_CANCEL);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_RETURN, qsci.SCI_NEWLINE);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_DOWN, qsci.SCI_LINEDOWN);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_UP, qsci.SCI_LINEUP);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_RIGHT, qsci.SCI_CHARRIGHT);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_LEFT, qsci.SCI_CHARLEFT);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_BACK, qsci.SCI_DELETEBACK);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_PRIOR, qsci.SCI_PAGEUP);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_NEXT, qsci.SCI_PAGEDOWN);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_HOME, qsci.SCI_VCHOME);
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_END, qsci.SCI_LINEEND);
        for key in range(ord('A'), ord('Z')):
            qsci.SendScintilla(qsci.SCI_ASSIGNCMDKEY, key + (qsci.SCMOD_CTRL << 16), qsci.SCI_NULL)
        
    def applySettings(self):
        """Apply own settings form the config
        """
        self.qscintilla.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        
        myConfig = core.config()["Editor"]
        self.qscintilla.setSelectionBackgroundColor(QColor(myConfig["SelectionBackgroundColor"]))
        self.qscintilla.setSelectionForegroundColor(QColor(myConfig["SelectionForegroundColor"]))
        if myConfig["DefaultDocumentColours"]:
            # set scintilla default colors
            self.qscintilla.setColor(QColor(myConfig["DefaultDocumentPen"]))
            self.qscintilla.setPaper(QColor(myConfig["DefaultDocumentPaper"]))

        self.qscintilla.setFont(QFont(myConfig["DefaultFont"], myConfig["DefaultFontSize"]))
        # Auto Completion
        if myConfig["AutoCompletion"]["Enabled"]:
            self.qscintilla.setAutoCompletionSource(self._AUTOCOMPLETION_MODE_TO_QSCI[myConfig["AutoCompletion"]["Source"]])
            self.qscintilla.setAutoCompletionThreshold(myConfig["AutoCompletion"]["Threshold"])
            self.qscintilla.setAutoCompletionCaseSensitivity(myConfig["AutoCompletion"]["CaseSensitivity"])
            self.qscintilla.setAutoCompletionReplaceWord(myConfig["AutoCompletion"]["ReplaceWord"])
            self.qscintilla.setAutoCompletionShowSingle(myConfig["AutoCompletion"]["ShowSingle"])
        else:
            self.qscintilla.setAutoCompletionSource(QsciScintilla.AcsNone)
        
        # CallTips
        if myConfig["CallTips"]["Enabled"]:
            self.qscintilla.setCallTipsStyle(self._CALL_TIPS_STYLE_TO_QSCI[myConfig["CallTips"]["Style"]])
            self.qscintilla.setCallTipsVisible(myConfig["CallTips"]["VisibleCount"])
            self.qscintilla.setCallTipsBackgroundColor(QColor(myConfig["CallTips"]["BackgroundColor"]))
            self.qscintilla.setCallTipsForegroundColor(QColor(myConfig["CallTips"]["ForegroundColor"]))
            self.qscintilla.setCallTipsHighlightColor(QColor(myConfig["CallTips"]["HighlightColor"]))
        else:
            self.qscintilla.setCallTipsStyle(QsciScintilla.CallTipsNone)

        # Indentation
        self.qscintilla.setAutoIndent(myConfig["Indentation"]["AutoIndent"])
        self.qscintilla.setBackspaceUnindents(myConfig["Indentation"]["BackspaceUnindents"])
        self.qscintilla.setIndentationGuides(myConfig["Indentation"]["Guides"])
        self.qscintilla.setIndentationGuidesBackgroundColor(QColor(myConfig["Indentation"]["GuidesBackgroundColor"]))
        self.qscintilla.setIndentationGuidesForegroundColor(QColor(myConfig["Indentation"]["GuidesForegroundColor"]))
        self.qscintilla.setIndentationsUseTabs(myConfig["Indentation"]["UseTabs"])
        self.qscintilla.setIndentationWidth(myConfig["Indentation"]["Width"])
        self.qscintilla.setTabWidth(myConfig["Indentation"]["Width"])
        self.qscintilla.setTabIndents(myConfig["Indentation"]["TabIndents"])

        # Brace Matching
        if myConfig["BraceMatching"]["Enabled"]:
            self.qscintilla.setBraceMatching(self._BRACE_MATCHING_TO_QSCI[myConfig["BraceMatching"]["Mode"]])
            self.qscintilla.setMatchedBraceBackgroundColor(QColor(myConfig["BraceMatching"]["MatchedBackgroundColor"]))
            self.qscintilla.setMatchedBraceForegroundColor(QColor(myConfig["BraceMatching"]["MatchedForegroundColor"]))
            self.qscintilla.setUnmatchedBraceBackgroundColor(QColor(myConfig["BraceMatching"]["UnmatchedBackgroundColor"]))
            self.qscintilla.setUnmatchedBraceForegroundColor(QColor(myConfig["BraceMatching"]["UnmatchedForegroundColor"]))
        else:
            self.qscintilla.setBraceMatching(QsciScintilla.NoBraceMatch)
        
        # Edge Mode
        if myConfig["Edge"]["Enabled"]:
            self.qscintilla.setEdgeMode(self._EDGE_MODE_TO_QSCI[myConfig["Edge"]["Mode"]])
            self.qscintilla.setEdgeColor(QColor(myConfig["Edge"]["Color"]))
            self.qscintilla.setEdgeColumn(myConfig["Edge"]["Column"])
        else:
            self.qscintilla.setEdgeMode(QsciScintilla.EdgeNone)

        # Caret
        self.qscintilla.setCaretLineVisible(myConfig["Caret"]["LineVisible"])
        self.qscintilla.setCaretLineBackgroundColor(QColor(myConfig["Caret"]["LineBackgroundColor"]))
        self.qscintilla.setCaretForegroundColor(QColor(myConfig["Caret"]["ForegroundColor"]))
        self.qscintilla.setCaretWidth(myConfig["Caret"]["Width"])
        
        # Special Characters
        self.qscintilla.setEolMode(self._EOL_CONVERTOR_TO_QSCI[myConfig["EOL"]["Mode"]])
        self.qscintilla.setEolVisibility(myConfig["EOL"]["Visibility"])
        
        self.qscintilla.setWhitespaceVisibility(self._WHITE_MODE_TO_QSCI[myConfig["WhitespaceVisibility"]])
        
        if myConfig["Wrap"]["Enabled"]:
            self.qscintilla.setWrapMode(self._WRAP_MODE_TO_QSCI[myConfig["Wrap"]["Mode"]])
            self.qscintilla.setWrapVisualFlags(self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["EndVisualFlag"]],
                                               self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["StartVisualFlag"]],
                                               myConfig["Wrap"]["LineIndentWidth"])
        else:
            self.qscintilla.setWrapMode(QsciScintilla.WrapNone)

    def text(self):
        """Contents of the editor
        """
        return self.qscintilla.text()
    
    def setText(self, text):
        """Set text in the QScintilla, clear modified flag, update line numbers bar
        """
        self.qscintilla.setText(text)
        self._onLinesChanged()
        self._setModified(False)
    
    def _setModified(self, modified):
        """Clear modified state for the file. Called by AbstractDocument, must be implemented by the children
        """
        self.qscintilla.setModified(False)
    
    def _onLinesChanged(self):
        """Handler of change of lines count in the qscintilla
        """
        digitsCount = len(str(self.qscintilla.lines()))
        if digitsCount:
            digitsCount += 1
        self.qscintilla.setMarginWidth(0, '0' * digitsCount)
    
    def eolMode(self):
        """Line end mode of the file
        """
        mode = self.qscintilla.eolMode()
        return self._EOL_CONVERTOR_FROM_QSCI[mode]

    def setEolMode(self, mode):
        """Set line end mode of the file
        """
        self.qscintilla.setEolMode(self._EOL_CONVERTOR_TO_QSCI[mode])
        self.qscintilla.convertEols(self._EOL_CONVERTOR_TO_QSCI[mode])

    def indentWidth(self):
        """Indentation width in symbol places (spaces)
        """
        return self.qscintilla.indentationWidth()
    
    def setIndentWidth(self, width):
        """Set indentation width in symbol places (spaces)
        """
        return self.qscintilla.setIndentationWidth(width)
    
    def indentUseTabs(self):
        """Indentation uses Tabs instead of Spaces
        """
        return self.qscintilla.indentationsUseTabs()
    
    def setIndentUseTabs(self, use):
        """Set iindentation mode (Tabs or spaces)
        """
        return self.qscintilla.setIndentationsUseTabs(use)
    
    def cursorPosition(self):
        """Get cursor position as touple (line, col)
        """
        line, col = self.qscintilla.getCursorPosition()
        return line + 1, col
        
    def isModified(self):
        """Check is file has been modified
        """
        return self.qscintilla.isModified()
        
    def goTo(self, line, column, selectionLength=-1):
        """Go to specified line and column. Select text if necessary
        """
        self.qscintilla.setCursorPosition(line, column)
        self.qscintilla.setSelection(line, column, line, column +selectionLength)
        self.qscintilla.ensureLineVisible(line)
        self.qscintilla.setFocus()

    def _convertIndentation(self):
        """Try to fix indentation mode of the file, if there are mix of different indentation modes
        (tabs and spaces)
        """
        # get original text
        originalText = self.qscintilla.text()
        # all modifications must believe as only one action
        self.qscintilla.beginUndoAction()
        # get indent width
        indentWidth = self.qscintilla.indentationWidth()
        
        if indentWidth == 0:
            indentWidth = self.qscintilla.tabWidth()
        
        # iterate each line
        lastLineWasTroncate = False  # remember if last line was troncate
        for i in range(self.qscintilla.lines()):
            # get current line indent width
            lineIndent = self.qscintilla.indentation(i)
            """
            # check if need troncate
            t = lineIndent /indentWidth
            r = lineIndent % indentWidth
            if  r != 0 and r != indentWidth :
                r += indentWidth -r
                lineIndent = (t * indentWidth) +r
                lastLineWasTroncate = True
            elif  lastLineWasTroncate and lineIndent != 0:
                lastLineWasTroncate = self.qscintilla.indentation(i + 1) == lineIndent
                lineIndent += indentWidth
            """
            # remove indentation
            self.qscintilla.setIndentation(i, 0)
            # restore it with possible troncate indentation
            self.qscintilla.setIndentation(i, lineIndent)
        
        # end global undo action
        self.qscintilla.endUndoAction()
        # compare original and newer text
        if  originalText == self.qscintilla.text():
            # clear undo buffer
            self.qscintilla.SendScintilla(QsciScintilla.SCI_EMPTYUNDOBUFFER)
            # set unmodified
            self._setModified(False)
        else:
            core.messageManager().appendMessage('Indentation converted. You can Undo the changes', 5000)

    def _autoDetectIndent(self):
        """Delect indentation automatically and apply detected mode
        """
        haveTabs = '\t' in self.qscintilla.text()
        for line in self.qscintilla.text().split('\n'):  #TODO improve algorythm sometimes for skip comments
            if unicode(line).startswith(' '):
                haveSpaces = True
                break
        else:
            haveSpaces = False
        
        if haveTabs and not haveSpaces:
            self.qscintilla.setIndentationsUseTabs (True)
        elif haveSpaces and not haveTabs:
            self.qscintilla.setIndentationsUseTabs (False)
        else:
            pass  # Don't touch current mode, if not sure

    def _autoDetectEol(self):
        """Detect end of line mode automatically and apply detected mode
        """
        if '\r\n' in self.qscintilla.text():
            self.qscintilla.setEolMode (QsciScintilla.EolWindows)
        elif '\n' in self.qscintilla.text():
            self.qscintilla.setEolMode (QsciScintilla.EolUnix)
        elif '\r' in self.qscintilla.text():
            self.qscintilla.setEolMode (QsciScintilla.EolMac)
        
    def toggleBookmark(self):
        row = self.qscintilla.getCursorPosition()[0]
        if self.qscintilla.markersAtLine(row) & 1 << self._MARKER_BOOKMARK:
            self.qscintilla.markerDelete(row, self._MARKER_BOOKMARK)
        else:
            self.qscintilla.markerAdd(row, self._MARKER_BOOKMARK)
        
    def nextBookmark(self):
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindNext(row + 1, 1 << self._MARKER_BOOKMARK), 0)
        
    def prevBookmark(self):
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindPrevious(row - 1, 1 << self._MARKER_BOOKMARK), 0)
    
class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        self.lexerConfig = _LexerConfiguration()
        core.workspace().setTextEditorClass(Editor)
        Plugin.instance = self
    
    def __term__(self):
        core.workspace().setTextEditorClass(None)
    
    def getModuleConfigurator(self):
        return EditorConfigurator

"""TODO restore or delete old code

    def eventFilter(self, selfObject, event):
        '''It is not an editor API function
        Catches key press events from QScintilla for support bookmarks and autocompletion'''
        
        if event.type() == QEvent.KeyPress:
            if not event.isAutoRepeat():
                row = self.qscintilla.getCursorPosition()[0]
                if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Space: # autocompletion shortcut
                    ''' TODO autocompletion shortcut?
                    switch (autoCompletionSource())
                        case QsciScintilla.AcsAll:
                            autoCompleteFromAll()
                            break
                        case QsciScintilla.AcsAPIs:
                            autoCompleteFromAPIs()
                            break
                        case QsciScintilla.AcsDocument:
                            autoCompleteFromDocument()
                            break
                        default:
                            break
                    '''
                    return True
        return False
    
    def __init__
        self.qscintilla.textChanged.connect(self.contentChanged)

    def isPrintAvailable(self):
        return True

    def invokeSearch ():
        '''MonkeyCore.searchWidget().showSearchFile ();'''
        pass

    def language(self):
        # return the editor language
        if  self.qscintilla.lexer() :
            return self.qscintilla.lexer().language()

        # return nothing
        return ''

    def backupFileAs(self, filePath):
        shutil.copy(self.filePath(), fileName)
    
    def closeFile(self):
        self.qscintilla.clear()
        self._setModified(False)
        self.setFilePath('')
        self.fileClosed.emit()

    def print_(self, quickPrint):
        # get printer
        p = QsciPrinter()
        
        # set wrapmode
        p.setWrapMode(PyQt4.Qsci.WrapWord)

        if  quickPrint:
            # check if default printer is set
            if  p.printerName().isEmpty() :
                core.messageManager().appendMessage(\
                    tr("There is no default printer, set one before trying quick print"))
                return
            
            # print and return
            p.printRange(self.qscintilla)
            return
        
        d = QPrintDialog (p) # printer dialog

        if d.exec_(): # if ok
            # print
            f = -1
            t = -1
            if  d.printRange() == QPrintDialog.Selection:
                f, unused, t, unused1 = getSelection()
            p.printRange(self.qscintilla, f, t)
    
    def printFile(self):
        self.print_(False)

    def quickPrintFile(self):
        self.print_(True)

class _pEditor(QsciScintilla):
    
        self.mPixSize = QSize(16, 16)
        # register image for bookmarks
        self.markerDefine(QPixmap(":/editor/bookmark.png").scaled(self.mPixSize), mdBookmark)
        
        # Create shortcuts manager, not created
        qSciShortcutsManager.instance()
    
    def findFirst(self, expr, re, cs, wo, wrap, forward, line, index, show):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        return QsciScintilla.findFirst(expr, re, cs, wo, wrap, forward, line, index, show)
    #else:
        mSearchState.inProgress = False

        if  expr.isEmpty() :        return False


        mSearchState.expr = expr
        mSearchState.wrap = wrap
        mSearchState.forward = forward

        mSearchState.flags = (cs ? SCFIND_MATCHCASE : 0) | (wo ? SCFIND_WHOLEWORD : 0) | (re ? SCFIND_REGEXP : 0)

        if  line < 0 or index < 0 :        mSearchState.startpos = SendScintilla(SCI_GETCURRENTPOS)

        else:
            mSearchState.startpos = positionFromLineIndex(line, index)


        if  forward :        mSearchState.endpos = SendScintilla(SCI_GETLENGTH)

        else:
            mSearchState.endpos = 0


        mSearchState.show = show

        return search()
    #endif


    def findNext(self):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        return QsciScintilla.findNext()
    #else:
        if  not mSearchState.inProgress :        return False


        return search()
    #endif


    def replace(self, replaceStr):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        QsciScintilla.replace(replaceStr)
    #else:
        if  not mSearchState.inProgress :        return


        static QRegExp rxd("\\$(\\d+)")
        rxd.setMinimal(True)
   ?         isRE = mSearchState.flags & SCFIND_REGEXP
            rx = mSearchState.rx
            captures = rx.capturedTexts()
            text = replaceStr
            start = SendScintilla(SCI_GETSELECTIONSTART)

            SendScintilla(SCI_TARGETFROMSELECTION)
            
            # remove selection
            removeSelectedText()
            
            # compute replace text
            if  isRE and captures.count() > 1 :        pos = 0
            
            while ((pos = rxd.indexIn(text, pos)) != -1)             id = rxd.cap(1).toInt()
                
                if  id < 0 or id >= captures.count() :                pos += rxd.matchedLength()
                    continue

                
                # update replace text with partial occurrences
                text.replace(pos, rxd.matchedLength(), captures.at(id))
                
                # next
                pos += captures.at(id).length()


        
        # insert replace text
            len = text.toUtf8().length(); # scintilla position are count from qbytearray data: ie: non ascii leter are 2 or more bits.
            insert(text)

        # Reset the selection.
        SendScintilla(SCI_SETSELECTIONSTART, start)
        SendScintilla(SCI_SETSELECTIONEND, start +len)

        if  mSearchState.forward :        mSearchState.startpos = start +len

    #endif

    def search(self):
        SendScintilla(SCI_SETSEARCHFLAGS, mSearchState.flags)

        pos = simpleSearch()

        # See if it was found.  If not and wraparound is wanted, again.
        if  pos == -1 and mSearchState.wrap :        if  mSearchState.forward :            mSearchState.startpos = 0
                mSearchState.endpos = SendScintilla(SCI_GETLENGTH)

            else:
                mSearchState.startpos = SendScintilla(SCI_GETLENGTH)
                mSearchState.endpos = 0


            pos = simpleSearch()


        if  pos == -1 :        mSearchState.inProgress = False
            return False


        # It was found.
        targstart = SendScintilla(SCI_GETTARGETSTART)
        targend = SendScintilla(SCI_GETTARGETEND)

        # Ensure the text found is visible if required.
        if  mSearchState.show :        startLine = SendScintilla(SCI_LINEFROMPOSITION, targstart)
            endLine = SendScintilla(SCI_LINEFROMPOSITION, targend)

            for (i = startLine; i <= endLine; ++i)            SendScintilla(SCI_ENSUREVISIBLEENFORCEPOLICY, i)



        # Now set the selection.
        SendScintilla(SCI_SETSEL, targstart, targend)

        # Finally adjust the start position so that we don't find the same one
        # again.
        if  mSearchState.forward :        mSearchState.startpos = targend

        elif  (mSearchState.startpos = targstart -1) < 0 :        mSearchState.startpos = 0


        mSearchState.inProgress = True
        return True


    def simpleSearch(self):
        if  mSearchState.startpos == mSearchState.endpos :        return -1


        SendScintilla(SCI_SETTARGETSTART, mSearchState.startpos)
        SendScintilla(SCI_SETTARGETEND, mSearchState.endpos)
        
            isCS = mSearchState.flags & SCFIND_MATCHCASE
            isWW = mSearchState.flags & SCFIND_WHOLEWORD
            isRE = mSearchState.flags & SCFIND_REGEXP
            from = qMin(mSearchState.startpos, mSearchState.endpos)
            to = qMax(mSearchState.startpos, mSearchState.endpos)
            data = self.text().toUtf8().mid(from, to -from); # scintilla position are from qbytearray size, non ascii letter are 2 or more bits.
            text = QString.fromUtf8(data)
            pattern = isRE ? mSearchState.expr : QRegExp.escape(mSearchState.expr)
            rx = mSearchState.rx
            
            if  isWW :        pattern.prepend("\\b").append("\\b")

        
        rx.setMinimal(True)
        rx.setPattern(pattern)
        rx.setCaseSensitivity(isCS ? Qt.CaseSensitive : Qt.CaseInsensitive)
        
        pos = mSearchState.forward ? rx.indexIn(text, from -from) : rx.lastIndexIn(text, to -from)
        
        if  pos != -1 :         start = from +text.left(pos).toUtf8().length()
                end = start +text.mid(pos, rx.matchedLength()).toUtf8().length()
                SendScintilla(SCI_SETTARGETSTART, start)
                SendScintilla(SCI_SETTARGETEND, end)

        
        return pos

    def currentLineText(self):
        int line
        int index
        
        getCursorPosition(&line, &index)
        
        return text(line)
    """
