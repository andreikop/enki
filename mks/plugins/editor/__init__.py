"""
editor --- Text editor. Uses QScintilla internally
==================================================

This text editor is used by default
"""

from mks.core.core import core

from mks.core.uisettings import ModuleConfigurator, \
                                CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption

import shortcuts

from lexer import Lexer, LexerConfig, LexerSettingsWidget
from editor import Editor

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
            Plugin.instance.lexerConfig.save()
    
    def applySettings(self):
        """Apply editor and lexer settings
        """
        for document in core.workspace().documents():
            document.applySettings()
            document.lexer.applySettings()


class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        Plugin.instance = self
        try:
            self.lexerConfig = LexerConfig()
        except UserWarning as ex:
            core.mainWindow().appendMessage(unicode(ex))
            self.lexerConfig = None
        core.workspace().setTextEditorClass(Editor)
        self._shortcuts = shortcuts.Shortcuts()
    
    def del_(self):
        self._shortcuts.del_()
        core.workspace().setTextEditorClass(None)
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return EditorConfigurator
