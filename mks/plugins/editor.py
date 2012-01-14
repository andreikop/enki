"""
editor --- Text editor. Uses QScintilla internally
==================================================

This text editor is used by default
"""

import os.path
import shutil

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QColor, QFont, QFrame, QIcon, QKeyEvent, QKeySequence, QMessageBox, QWidget, QVBoxLayout

from PyQt4.Qsci import *  # pylint: disable=W0401,W0614

from mks.core.abstractdocument import AbstractTextEditor
from mks.core.core import core, DATA_FILES_PATH

import mks.core.defines
from mks.core.config import Config
from mks.core.uisettings import ModuleConfigurator, \
                                CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption

class _QsciScintilla(QsciScintilla):
    """QsciScintilla wrapper class. It is created to 
    
    
    * Catch Shift+Tab. When pressed - Qt moves focus, but it is not desired behaviour. This class catches the event
    * Catch Enter presesing and emits a signal after newline had been inserted
    * Fix EOL mode when pasting text
    """
    
    newLineInserted = pyqtSignal()
    
    def __init__(self, editor):
        self._editor = editor
        QsciScintilla.__init__(self, editor)
    
    def keyPressEvent(self, event):
        """Key pressing handler
        """
        if event.key() == Qt.Key_Backtab:  # convert the event to Shift+Tab pressing without backtab behaviour
            event.accept()
            newev = QKeyEvent(event.type(), Qt.Key_Tab, Qt.ShiftModifier)
            super(_QsciScintilla, self).keyPressEvent(newev)
        elif event.matches(QKeySequence.InsertParagraphSeparator):
            lineCount = self.lines()
            super(_QsciScintilla, self).keyPressEvent(event)
            if self.lines() > lineCount:  # bad hack, which checks, if autocompletion window is active
                self.newLineInserted.emit()
        else:
            super(_QsciScintilla, self).keyPressEvent(event)
    
    def paste(self):
        """paste() method reimplementation. Converts EOL after text had been pasted
        """
        QsciScintilla.paste(self)
        self.convertEols(self.eolMode())


class LexerSettingsWidget(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        uic.loadUi(os.path.join(DATA_FILES_PATH,'ui/plugins/EditorLexerSettings.ui'), self)

class EditorConfigurator(ModuleConfigurator):
    """ModuleConfigurator interface implementation
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = []
        self._createEditorOptions(dialog)
        self._createLexerOptions(dialog)
    
    def _createEditorOptions(self, dialog):
        """Create editor (not lexer) specific options
        """
        cfg = core.config()
        self._options.extend(\
        (
            CheckableOption(dialog, cfg, "Editor/Indentation/ConvertUponOpen", dialog.cbConvertIndentationUponOpen),
            CheckableOption(dialog, cfg, "Editor/CreateBackupUponOpen", dialog.cbCreateBackupUponOpen),
            CheckableOption(dialog, cfg, "Editor/ShowLineNumbers", dialog.cbShowLineNumbers),
            CheckableOption(dialog, cfg, "Editor/EnableCodeFolding", dialog.cbEnableCodeFolding),
            ColorOption(dialog, cfg, "Editor/SelectionBackgroundColor", dialog.tbSelectionBackground),
            ColorOption(dialog, cfg, "Editor/SelectionForegroundColor", dialog.tbSelectionForeground),
            CheckableOption(dialog, cfg, "Editor/DefaultDocumentColours", dialog.gbDefaultDocumentColours),
            ColorOption(dialog, cfg, "Editor/DefaultDocumentPen", dialog.tbDefaultDocumentPen),
            ColorOption(dialog, cfg, "Editor/DefaultDocumentPaper", dialog.tbDefaultDocumentPaper),
            FontOption(dialog, cfg, "Editor/DefaultFont", "Editor/DefaultFontSize",
                        dialog.lDefaultDocumentFont, dialog.pbDefaultDocumentFont),
        
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/Enabled", dialog.gbAutoCompletion),
            ChoiseOption(dialog, cfg, "Editor/AutoCompletion/Source",
                         { dialog.rbDocument: "Document",
                           dialog.rbApi: "APIs",
                           dialog.rbFromBoth: "All" }),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/CaseSensitivity",
                            dialog.cbAutoCompletionCaseSensitivity),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/ReplaceWord", dialog.cbAutoCompletionReplaceWord),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/ShowSingle", dialog.cbAutoCompletionShowSingle),
            NumericOption(dialog, cfg, "Editor/AutoCompletion/Threshold", dialog.sAutoCompletionThreshold),
        
            # TODO restore or remove
            #CheckableOption(dialog, cfg, "Editor/CallTips/Enabled", dialog.gbCalltips),
            #NumericOption(dialog, cfg, "Editor/CallTips/VisibleCount", dialog.sCallTipsVisible),
            #ChoiseOption(dialog, cfg, "Editor/CallTips/Style",
            #             { dialog.rbCallTipsNoContext : "NoContext",
            #               dialog.rbCallTipsContext : "Context",
            #               dialog.rbCallTipsNoAutoCompletionContext: "NoAutoCompletionContext"}),
            #ColorOption(dialog, cfg, "Editor/CallTips/BackgroundColor", dialog.tbCalltipsBackground),
            #ColorOption(dialog, cfg, "Editor/CallTips/ForegroundColor", dialog.tbCalltipsForeground),
            #ColorOption(dialog, cfg, "Editor/CallTips/HighlightColor", dialog.tbCalltipsHighlight),
        
            CheckableOption(dialog, cfg, "Editor/Indentation/Guides", dialog.gbIndentationGuides),
            ChoiseOption(dialog, cfg, "Editor/Indentation/UseTabs",
                         {dialog.rbIndentationSpaces : False,
                          dialog.rbIndentationTabs: True}),
            CheckableOption(dialog, cfg, "Editor/Indentation/AutoDetect", dialog.cbAutodetectIndent),
            NumericOption(dialog, cfg, "Editor/Indentation/Width", dialog.sIndentationWidth),
            ColorOption(dialog, cfg, "Editor/Indentation/GuidesBackgroundColor", dialog.tbIndentationGuidesBackground),
            ColorOption(dialog, cfg, "Editor/Indentation/GuidesForegroundColor", dialog.tbIndentationGuidesForeground),
        
            CheckableOption(dialog, cfg, "Editor/BraceMatching/Enabled", dialog.gbBraceMatchingEnabled),
            ColorOption(dialog, cfg, "Editor/BraceMatching/MatchedForegroundColor", dialog.tbMatchedBraceForeground),
            ColorOption(dialog, cfg, "Editor/BraceMatching/MatchedBackgroundColor", dialog.tbMatchedBraceBackground),
            ColorOption(dialog, cfg, "Editor/BraceMatching/UnmatchedBackgroundColor",
                        dialog.tbUnmatchedBraceBackground),
            ColorOption(dialog, cfg, "Editor/BraceMatching/UnmatchedForegroundColor",
                        dialog.tbUnmatchedBraceForeground),
        
            CheckableOption(dialog, cfg, "Editor/Edge/Enabled", dialog.gbEdgeModeEnabled),
            ChoiseOption(dialog, cfg, "Editor/Edge/Mode",
                         {dialog.rbEdgeLine: "Line",
                          dialog.rbEdgeBackground: "Background"}),
            NumericOption(dialog, cfg, "Editor/Edge/Column", dialog.sEdgeColumnNumber),
            ColorOption(dialog, cfg, "Editor/Edge/Color", dialog.tbEdgeColor),

            CheckableOption(dialog, cfg, "Editor/Caret/LineVisible", dialog.gbCaretLineVisible),
            ColorOption(dialog, cfg, "Editor/Caret/LineBackgroundColor", dialog.tbCaretLineBackground),
            ColorOption(dialog, cfg, "Editor/Caret/ForegroundColor", dialog.tbCaretForeground),
            NumericOption(dialog, cfg, "Editor/Caret/Width", dialog.sCaretWidth),

            ChoiseOption(dialog, cfg, "Editor/EOL/Mode",
                         {dialog.rbEolUnix: r'\n',
                          dialog.rbEolWindows: r'\r\n',
                          dialog.rbEolMac: r'\r'}),
            CheckableOption(dialog, cfg, "Editor/EOL/AutoDetect", dialog.cbAutoDetectEol),
            ChoiseOption(dialog, cfg, "Editor/WhitespaceVisibility",
                         {dialog.rbWsInvisible: "Invisible",
                          dialog.rbWsVisible: "Visible",
                          dialog.rbWsVisibleAfterIndent: "VisibleAfterIndent"}),
        ))
    
    def _createLexerOptions(self, dialog):
        """Create lexer (not editor) specific options
        """
        editor = core.workspace().currentDocument()

        if editor is None or \
           editor.lexer.currentLanguage is None or \
           editor.lexer.currentLanguage == 'Scheme' or \
           Plugin.instance.lexerConfig is None:  # If language is unknown, or lexer configuration are not available
            return
        
        widget = LexerSettingsWidget(dialog)
        dialog.appendPage(u"Editor/%s" % editor.lexer.currentLanguage, widget)
        
        lexerConfig = Plugin.instance.lexerConfig.config
        lexer = editor.lexer.qscilexer
        beginning = "%s/" % editor.lexer.currentLanguage
        
        boolAttributeControls = (widget.cbLexerFoldComments,
                                 widget.cbLexerFoldCompact,
                                 widget.cbLexerFoldQuotes,
                                 widget.cbLexerFoldDirectives,
                                 widget.cbLexerFoldAtBegin,
                                 widget.cbLexerFoldAtParenthesis,
                                 widget.cbLexerFoldAtElse,
                                 widget.cbLexerFoldAtModule,
                                 widget.cbLexerFoldPreprocessor,
                                 widget.cbLexerStylePreprocessor,
                                 widget.cbLexerCaseSensitiveTags,
                                 widget.cbLexerBackslashEscapes)
        
        for attribute, control in zip(Lexer.LEXER_BOOL_ATTRIBUTES, boolAttributeControls):
            if hasattr(lexer, attribute):
                self._options.append(CheckableOption(dialog, lexerConfig, beginning + attribute, control))
            else:
                control.hide()

        self._options.extend(( \
             CheckableOption(dialog, lexerConfig, beginning + "indentOpeningBrace", widget.cbLexerIndentOpeningBrace),
             CheckableOption(dialog, lexerConfig, beginning + "indentClosingBrace", widget.cbLexerIndentClosingBrace)))

        if hasattr(lexer, "indentationWarning"):
            self._options.extend((
                CheckableOption(dialog, lexerConfig,
                                beginning + "indentationWarning", widget.gbLexerHighlightingIndentationWarning),
                ChoiseOption(dialog, lexerConfig, beginning + "indentationWarningReason", 
                             {widget.cbIndentationWarningInconsistent: "Inconsistent",
                             widget.cbIndentationWarningTabsAfterSpaces: "TabsAfterSpaces",
                             widget.cbIndentationWarningTabs: "Tabs",
                             widget.cbIndentationWarningSpaces: "Spaces"})))
        else:
            widget.gbLexerHighlightingIndentationWarning.hide()

    def saveSettings(self):
        """Main settings should be saved by the core. Save only lexer settings
        """
        if Plugin.instance.lexerConfig is not None:
            try:
                Plugin.instance.lexerConfig.config.flush()
            except UserWarning as ex:
                core.messageManager().appendMessage(unicode(ex))
    
    def applySettings(self):
        """Apply editor and lexer settings
        """
        for document in core.workspace().openedDocuments():
            document.applySettings()
            document.lexer.applySettings()

class LexerConfig:
    """Class manages settings of QScintilla lexers. Functionality:
    
    * Create configuration file with lexer defaults
    * Load and save the file
    """
    _CONFIG_PATH = os.path.join(mks.core.defines.CONFIG_DIR, 'lexers.cfg')
    
    def __init__(self):
        if os.path.exists(self._CONFIG_PATH):  # File exists, load it
            self.config = Config(True, self._CONFIG_PATH)
            self._convertConfigValueTypes()
        else:  # First start, generate file
            self.config = Config(True, self._CONFIG_PATH)
            self._generateDefaultConfig()
            self.config.flush()

    def _convertConfigValueTypes(self):
        """There are no scheme for lexer configuration, therefore need to convert types manually
        """
        for languageOptions in self.config.itervalues():
            for key in languageOptions.iterkeys():
                value = languageOptions[key]
                if value == 'True':
                    languageOptions[key] = True
                elif value == 'False':
                    languageOptions[key] = False
                elif value.isdigit():
                    languageOptions[key] = int(value)

    def _generateDefaultConfig(self):
        """Generate default lexer configuration file. File contains QScintilla defaults
        """
        for language, lexerClass in Lexer.LEXER_FOR_LANGUAGE.items():
            self.config[language] = {}
            lexerSection = self.config[language]
            lexerObject = lexerClass(None)

            for attribute in Lexer.LEXER_BOOL_ATTRIBUTES:
                if hasattr(lexerObject, attribute):
                    lexerSection[attribute] = getattr(lexerObject, attribute)()
            lexerSection['indentOpeningBrace'] = bool(lexerObject.autoIndentStyle() & QsciScintilla.AiOpening)
            lexerSection['indentClosingBrace'] = bool(lexerObject.autoIndentStyle() & QsciScintilla.AiClosing)
            if hasattr(lexerObject, "indentationWarning"):
                reason = getattr(lexerObject, "indentationWarning")()
                reasonFromQsci = dict((v, k) for k, v in Lexer.PYTHON_INDENTATION_WARNING_TO_QSCI.items())
                if reason == QsciLexerPython.NoWarning:
                    lexerSection['indentationWarning'] = False
                    # MkS default reason
                    lexerSection['indentationWarningReason'] = reasonFromQsci[QsciLexerPython.Inconsistent]
                else:
                    lexerSection['indentationWarning'] = True
                    lexerSection['indentationWarningReason'] = reasonFromQsci[reason]

def _getPygmentsSchemeLexer(editor):
    """Construct and return pygments lexer for Scheme. Sets valid language name, lazy import
    """
    try:
        import mks.plugins.lexerpygments
    except ImportError:
        QMessageBox.critical(core.workspace(), "Failed to load pygments",
                             "<html>mksv3 can't highlight Scheme source, "\
                             "because <b>pygments</b> library not found</html>")
        return None
    return mks.plugins.lexerpygments.LexerPygments(editor, 'Scheme')

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
           Plugin.instance.lexerConfig is None:
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
        lexerSection = Plugin.instance.lexerConfig.config[self.currentLanguage]
        
        for attribute in self.LEXER_BOOL_ATTRIBUTES:
            setterName = 'set' + attribute[0].capitalize() + attribute[1:]
            if hasattr(self.qscilexer, setterName):
                getattr(self.qscilexer, setterName)(lexerSection[attribute])
        
        autoIndentStyle = 0
        if lexerSection['indentOpeningBrace']:
            autoIndentStyle &= QsciScintilla.AiOpening
        if lexerSection['indentClosingBrace']:
            autoIndentStyle &= QsciScintilla.AiClosing
        self.qscilexer.setAutoIndentStyle(autoIndentStyle)
        if hasattr(self.qscilexer, "setIndentationWarning"):
            if lexerSection['indentationWarning']:
                qsciReason = self.PYTHON_INDENTATION_WARNING_TO_QSCI[lexerSection['indentationWarningReason']]
                self.qscilexer.setIndentationWarning(qsciReason)


class Editor(AbstractTextEditor):
    """Text editor widget.
    
    Uses QScintilla internally
    """
    
    _MARKER_BOOKMARK = -1  # QScintilla marker type
    
    _EOL_CONVERTOR_TO_QSCI = {r'\n'     : QsciScintilla.EolUnix,
                              r'\r\n'   : QsciScintilla.EolWindows,
                              r'\r'     : QsciScintilla.EolMac}
    
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
    
    #
    # Own methods
    #
    
    def __init__(self, parentObject, filePath, createNew=False, terminalWidget=False):
        super(Editor, self).__init__(parentObject, filePath, createNew)
        
        self._terminalWidget = terminalWidget
        self._eolMode = None
        
        # Configure editor
        self.qscintilla = _QsciScintilla(self)
        self.qscintilla.newLineInserted.connect(self.newLineInserted)
        
        pixmap = QIcon(":/mksicons/bookmark.png").pixmap(16, 16)
        self._MARKER_BOOKMARK = self.qscintilla.markerDefine(pixmap, -1)
        
        self._initQsciShortcuts()
        
        self.qscintilla.setUtf8(True)
        
        self.qscintilla.setAttribute(Qt.WA_MacSmallSize)
        self.qscintilla.setFrameStyle(QFrame.NoFrame | QFrame.Plain)

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.qscintilla)
        
        self.setFocusProxy(self.qscintilla)
        # connections
        self.qscintilla.cursorPositionChanged.connect(self.cursorPositionChanged)
        self.qscintilla.modificationChanged.connect(self.modifiedChanged)
        
        self.applySettings()
        self.lexer = Lexer(self)
        
        if not self._neverSaved:
            try:
                originalText = self._readFile(filePath)
            except IOError as ex:  # exception in constructor
                self.deleteLater()  # make sure C++ object deleted
                raise ex
            self.setText(originalText)
        else:
            originalText = ''
        
        myConfig = core.config()["Editor"]
        
        # make backup if needed
        if  myConfig["CreateBackupUponOpen"]:
            if self.filePath() and not createNew:
                try:
                    shutil.copy(self.filePath(), self.filePath() + '.bak')
                except (IOError, OSError) as ex:
                    self.deleteLater()
                    raise ex
        
        #autodetect indent, need
        if  myConfig["Indentation"]["AutoDetect"]:
            self._autoDetectIndent()
        
        # convert tabs if needed
        if  myConfig["Indentation"]["ConvertUponOpen"]:
            self._convertIndentation()
        
        #autodetect eol, need
        self._configureEolMode(originalText)
        
        self.modifiedChanged.emit(self.isModified())
        self.cursorPositionChanged.emit(*self.cursorPosition())

    def _initQsciShortcuts(self):
        """Clear default QScintilla shortcuts, and restore only ones, which are needed for MkS.
        
        Other shortcuts are disabled, or are configured with mks.plugins.editorshortcuts and defined here
        """
        qsci = self.qscintilla
        qsci.SendScintilla( qsci.SCI_CLEARALLCMDKEYS )
        # Some shortcuts are hardcoded there.
        #If we made is a QActions, it will shadow Qt default keys for move focus, etc
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_TAB, qsci.SCI_TAB)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_ESCAPE, qsci.SCI_CANCEL)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_RETURN, qsci.SCI_NEWLINE)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_DOWN, qsci.SCI_LINEDOWN)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_UP, qsci.SCI_LINEUP)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_RIGHT, qsci.SCI_CHARRIGHT)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_LEFT, qsci.SCI_CHARLEFT)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_BACK, qsci.SCI_DELETEBACK)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_PRIOR, qsci.SCI_PAGEUP)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_NEXT, qsci.SCI_PAGEDOWN)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_HOME, qsci.SCI_VCHOME)
        qsci.SendScintilla( qsci.SCI_ASSIGNCMDKEY, qsci.SCK_END, qsci.SCI_LINEEND)
        for key in range(ord('A'), ord('Z')):
            qsci.SendScintilla(qsci.SCI_ASSIGNCMDKEY, key + (qsci.SCMOD_CTRL << 16), qsci.SCI_NULL)

    def applySettings(self):  # pylint: disable=R0912,R0915
        """Apply own settings form the config
        """
        myConfig = core.config()["Editor"]

        if myConfig["ShowLineNumbers"] and not self._terminalWidget:
            self.qscintilla.linesChanged.connect(self._onLinesChanged)
            self._onLinesChanged()
        else:
            try:
                self.qscintilla.linesChanged.disconnect(self._onLinesChanged)
            except TypeError:  # not connected
                pass
            self.qscintilla.setMarginWidth(0, 0)
        
        if myConfig["EnableCodeFolding"] and not self._terminalWidget:
            self.qscintilla.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        else:
            self.qscintilla.setFolding(QsciScintilla.NoFoldStyle)
        
        self.qscintilla.setSelectionBackgroundColor(QColor(myConfig["SelectionBackgroundColor"]))
        self.qscintilla.setSelectionForegroundColor(QColor(myConfig["SelectionForegroundColor"]))
        if myConfig["DefaultDocumentColours"]:
            # set scintilla default colors
            self.qscintilla.setColor(QColor(myConfig["DefaultDocumentPen"]))
            self.qscintilla.setPaper(QColor(myConfig["DefaultDocumentPaper"]))

        self.qscintilla.setFont(QFont(myConfig["DefaultFont"], myConfig["DefaultFontSize"]))
        # Auto Completion
        if myConfig["AutoCompletion"]["Enabled"] and not self._terminalWidget:
            self.qscintilla.setAutoCompletionSource(\
                                            self._AUTOCOMPLETION_MODE_TO_QSCI[myConfig["AutoCompletion"]["Source"]])
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
            self.qscintilla.setUnmatchedBraceBackgroundColor(\
                                                        QColor(myConfig["BraceMatching"]["UnmatchedBackgroundColor"]))
            self.qscintilla.setUnmatchedBraceForegroundColor(\
                                                        QColor(myConfig["BraceMatching"]["UnmatchedForegroundColor"]))
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
        self.qscintilla.setWhitespaceVisibility(self._WHITE_MODE_TO_QSCI[myConfig["WhitespaceVisibility"]])
        
        if myConfig["Wrap"]["Enabled"]:
            self.qscintilla.setWrapMode(self._WRAP_MODE_TO_QSCI[myConfig["Wrap"]["Mode"]])
            self.qscintilla.setWrapVisualFlags(self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["EndVisualFlag"]],
                                               self._WRAP_FLAG_TO_QSCI[myConfig["Wrap"]["StartVisualFlag"]],
                                               myConfig["Wrap"]["LineIndentWidth"])
        else:
            self.qscintilla.setWrapMode(QsciScintilla.WrapNone)

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
        for i in range(self.qscintilla.lines()):
            # get current line indent width
            lineIndent = self.qscintilla.indentation(i)
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
        text = self.text()
        haveTabs = '\t' in text
        for line in text.splitlines():  #TODO improve algorythm sometimes to skip comments
            if line.startswith(' '):
                haveSpaces = True
                break
        else:
            haveSpaces = False
        
        if haveTabs:
            self.qscintilla.setIndentationsUseTabs (True)
        elif haveSpaces:
            self.qscintilla.setIndentationsUseTabs (False)
        else:
            pass  # Don't touch current mode, if not sure

    def _onLinesChanged(self):
        """Handler of change of lines count in the qscintilla
        """
        digitsCount = len(str(self.qscintilla.lines()))
        if digitsCount:
            digitsCount += 1
        self.qscintilla.setMarginWidth(0, '0' * digitsCount)

    #
    # AbstractDocument interface
    #
    
    def _setModified(self, modified):
        """Update modified state for the file. Called by AbstractTextEditor, must be implemented by the children
        """
        self.qscintilla.setModified(modified)

    def isModified(self):
        """Check is file has been modified
        """
        return self.qscintilla.isModified()
    
    #
    # AbstractTextEditor interface
    #
    
    def eolMode(self):
        """Line end mode of the file
        """
        return self._eolMode

    def setEolMode(self, mode):
        """Set line end mode of the file
        """
        self.qscintilla.setEolMode(self._EOL_CONVERTOR_TO_QSCI[mode])
        self.qscintilla.convertEols(self._EOL_CONVERTOR_TO_QSCI[mode])
        self._eolMode = mode

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
    
    def _applyHighlightingLanguage(self, language):
        """Set programming language of the file.
        Called Only by :mod:`mks.plugins.associations` to select syntax highlighting language.
        """
        self.lexer.applyLanguage(language)

    def text(self):
        """Contents of the editor
        """
        text = self.qscintilla.text()
        lines = text.splitlines()
        if text.endswith('\r') or text.endswith('\n'):
               lines.append('')
        return '\n'.join(lines)
    
    def setText(self, text):
        """Set text in the QScintilla, clear modified flag, update line numbers bar
        """
        self.qscintilla.setText(text)
        self.qscintilla.linesChanged.emit()
        self._setModified(False)

    def selectedText(self):
        """Get selected text
        """
        return self.qscintilla.selectedText()
        
    def selection(self):
        """Get coordinates of selected area as ((startLine, startCol), (endLine, endCol))
        """
        startLine, startCol, endLine, endCol = self.qscintilla.getSelection()
        if startLine == -1:
            cursorPos = self.cursorPosition()
            return (cursorPos, cursorPos)

        return ((startLine + 1, startCol), (endLine + 1, endCol))

    def absSelection(self):
        """Get coordinates of selected area as (startAbsPos, endAbsPos)
        """
        start, end = self.selection()
        return (self._toAbsPosition(*start), self._toAbsPosition(*end))

    def cursorPosition(self):
        """Get cursor position as tuple (line, col)
        """
        line, col = self.qscintilla.getCursorPosition()
        return line + 1, col
    
    def _setCursorPosition(self, line, col):
        """Implementation of AbstractTextEditor.setCursorPosition
        """
        self.qscintilla.setCursorPosition(line - 1, col)

    def replaceSelectedText(self, text):
        """Replace selected text with text
        """
        self.qscintilla.beginUndoAction()
        self.qscintilla.removeSelectedText()
        self.qscintilla.insert(text)
        self.qscintilla.endUndoAction()
    
    def _replace(self, startAbsPos, endAbsPos, text):
        """Replace text at position with text
        """
        startLine, startCol = self._toLineCol(startAbsPos)
        endLine, endCol = self._toLineCol(endAbsPos)
        self.qscintilla.setSelection(startLine - 1, startCol,
                                     endLine - 1, endCol)
        self.replaceSelectedText(text)
    
    def beginUndoAction(self):
        """Start doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        
        DO NOT FORGET to call **endUndoAction()** after you have finished
        """
        self.qscintilla.beginUndoAction()

    def endUndoAction(self):
        """Finish doing set of modifications, which will be managed as one action.
        User can Undo and Redo all modifications with one action
        """
        self.qscintilla.endUndoAction()

    def _goTo(self, line, column, selectionLine = None, selectionCol = None):
        """Go to specified line and column. Select text if necessary
        """
        line -= 1
        if selectionLine is not None:
            selectionLine -= 1

        if selectionLine is None:
            self.qscintilla.setCursorPosition(line, column)
        else:
            self.qscintilla.setSelection(selectionLine, selectionCol,
                                         line, column)
        self.qscintilla.ensureLineVisible(line)
    
    def lineCount(self):
        """Get line count
        """
        return self.qscintilla.lines()

    #
    # Public methods for editorshortcuts
    #
    
    def toggleBookmark(self):
        """Set or clear bookmark on the line
        """
        row = self.qscintilla.getCursorPosition()[0]
        if self.qscintilla.markersAtLine(row) & 1 << self._MARKER_BOOKMARK:
            self.qscintilla.markerDelete(row, self._MARKER_BOOKMARK)
        else:
            self.qscintilla.markerAdd(row, self._MARKER_BOOKMARK)
        
    def nextBookmark(self):
        """Move to the next bookmark
        """
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindNext(row + 1, 1 << self._MARKER_BOOKMARK), 0)
        
    def prevBookmark(self):
        """Move to the previous bookmark
        """
        row = self.qscintilla.getCursorPosition()[0]
        self.qscintilla.setCursorPosition(
                    self.qscintilla.markerFindPrevious(row - 1, 1 << self._MARKER_BOOKMARK), 0)


class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        Plugin.instance = self
        try:
            self.lexerConfig = LexerConfig()
        except UserWarning as ex:
            core.messageManager().appendMessage(unicode(ex))
            self.lexerConfig = None
        core.workspace().setTextEditorClass(Editor)
    
    def __term__(self):
        core.workspace().setTextEditorClass(None)
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return EditorConfigurator

#TODO restore or delete old code

#    def eventFilter(self, selfObject, event):
#        '''It is not an editor API function
#        Catches key press events from QScintilla for support bookmarks and autocompletion'''
#        
#        if event.type() == QEvent.KeyPress:
#            if not event.isAutoRepeat():
#                row = self.qscintilla.getCursorPosition()[0]
#                if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_Space: # autocompletion shortcut
#                    ''' TODO autocompletion shortcut?
#                    switch (autoCompletionSource())
#                        case QsciScintilla.AcsAll:
#                            autoCompleteFromAll()
#                            break
#                        case QsciScintilla.AcsAPIs:
#                            autoCompleteFromAPIs()
#                            break
#                        case QsciScintilla.AcsDocument:
#                            autoCompleteFromDocument()
#                            break
#                        default:
#                            break
#                    '''
#                    return True
#        return False
#    
#    def __init__
#        self.qscintilla.textChanged.connect(self.contentChanged)

#    def isPrintAvailable(self):
#        return True

#    def backupFileAs(self, filePath):
#        shutil.copy(self.filePath(), fileName)
#    
#    def print_(self, quickPrint):
#        # get printer
#        p = QsciPrinter()
#        
#        # set wrapmode
#        p.setWrapMode(PyQt4.Qsci.WrapWord)

#        if  quickPrint:
#            # check if default printer is set
#            if  p.printerName().isEmpty() :
#                core.messageManager().appendMessage(\
#                    tr("There is no default printer, set one before trying quick print"))
#                return
#            
#            # print and return
#            p.printRange(self.qscintilla)
#            return
#        
#        d = QPrintDialog (p) # printer dialog

#        if d.exec_(): # if ok
#            # print
#            f = -1
#            t = -1
#            if  d.printRange() == QPrintDialog.Selection:
#                f, unused, t, unused1 = getSelection()
#            p.printRange(self.qscintilla, f, t)
#    
#    def printFile(self):
#        self.print_(False)

#    def quickPrintFile(self):
#        self.print_(True)
