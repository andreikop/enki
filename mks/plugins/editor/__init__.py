"""
editor --- Text editor. Uses QScintilla internally
==================================================

This text editor is used by default
"""

from mks.core.core import core

from mks.core.uisettings import ModuleConfigurator, \
                                CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption

import shortcuts

from lexer import Lexer
from editor import Editor

class EditorConfigurator(ModuleConfigurator):
    """ModuleConfigurator interface implementation
    """
    def __init__(self, dialog):
        ModuleConfigurator.__init__(self, dialog)
        self._options = []
        self._createEditorOptions(dialog)
    
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
            CheckableOption(dialog, cfg, "Editor/MonochromeSelectionForeground", dialog.gbMonochromeSelectionForeground),
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
    

class Plugin:
    """Plugin interface implementation
    
    Installs and removes editor from the system
    """
    def __init__(self):
        Plugin.instance = self
        core.workspace().setTextEditorClass(Editor)
        self._shortcuts = shortcuts.Shortcuts()
        core.uiSettingsManager().dialogAccepted.connect(self._applySettings)
    
    def del_(self):
        self._shortcuts.del_()
        core.workspace().setTextEditorClass(None)
    
    def _applySettings(self):
        """Settings dialogue has been accepted.
        Apply editor and lexer settings
        """
        for document in core.workspace().documents():
            document.applySettings()
            document.lexer.applySettings()
    
    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return EditorConfigurator
