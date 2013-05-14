"""
qpartsettings --- GUI dialogs for Qutepart settings
===================================================

Appends pages to the settings dialogue.

This is not a True plugin, because it 'knows' pathes to editor settings,
which are not a part of enki API. But, this code has been moved out
from the core for make it smaller.
"""

import os

from PyQt4.QtGui import QWidget

from enki.core.core import core

from enki.core.uisettings import CheckableOption, ChoiseOption, FontOption, NumericOption, ColorOption


class _FontSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Font.ui'), self)


class _IndentationSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Indentation.ui'), self)


class _AutocompletionSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Autocompletion.ui'), self)


class _EolSettingsWidget(QWidget):
    """Font settings widget. Insertted as a page to UISettings
    """
    def __init__(self, *args):
        QWidget.__init__(self, *args)
        from PyQt4 import uic  # lazy import for better startup performance
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'Eol.ui'), self)


class Plugin:
    """Plugin interface implementation
    
    Waits for GUI dialogue invocation.
    Adds options to the dialogue.
    Applies settings.
    """
    def __init__(self):
        Plugin.instance = self
        core.uiSettingsManager().aboutToExecute.connect(self._onSettingsDialogAboutToExecute)
    
    def del_(self):
        pass
    
    def _onSettingsDialogAboutToExecute(self, dialog):
        """UI settings dialogue is about to execute.
        Add own options
        """
        fontWidget = _FontSettingsWidget(dialog)
        indentWidget = _IndentationSettingsWidget(dialog)
        complWidget = _AutocompletionSettingsWidget(dialog)
        eolWidget = _EolSettingsWidget(dialog)
        
        dialog.appendPage(u"Editor/Font", fontWidget)
        dialog.appendPage(u"Editor/Indentation", indentWidget)
        dialog.appendPage(u"Editor/Autocompletion", complWidget)
        dialog.appendPage(u"Editor/EOL", eolWidget)

        cfg = core.config()
        options = \
        (
            FontOption(dialog, cfg, "Editor/DefaultFont", "Editor/DefaultFontSize",
                       fontWidget.lFont, fontWidget.pbFont),
            
            ChoiseOption(dialog, cfg, "Editor/Indentation/UseTabs",
                         {indentWidget.rbIndentationSpaces : False,
                          indentWidget.rbIndentationTabs: True}),
            NumericOption(dialog, cfg, "Editor/Indentation/Width", indentWidget.sIndentationWidth),
            CheckableOption(dialog, cfg, "Editor/Indentation/AutoDetect", indentWidget.cbAutodetectIndent),
            
            ChoiseOption(dialog, cfg, "Editor/EOL/Mode",
                         {eolWidget.rbEolUnix: r'\n',
                          eolWidget.rbEolWindows: r'\r\n',
                          eolWidget.rbEolMac: r'\r'}),            
            CheckableOption(dialog, cfg, "Editor/EOL/AutoDetect", eolWidget.cbAutoDetectEol),
            
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/Enabled", complWidget.gbAutoCompletion),
            NumericOption(dialog, cfg, "Editor/AutoCompletion/Threshold", complWidget.sThreshold),
        )
        
        for option in options:
            dialog.appendOption(option)


""" Old options. TODO Uncomment or delete
            CheckableOption(dialog, cfg, "Editor/Indentation/ConvertUponOpen", dialog.cbConvertIndentationUponOpen),
            
            CheckableOption(dialog, cfg, "Editor/ShowLineNumbers", dialog.cbShowLineNumbers),
            CheckableOption(dialog, cfg, "Editor/EnableCodeFolding", dialog.cbEnableCodeFolding),
            ColorOption(dialog, cfg, "Editor/SelectionBackgroundColor", dialog.tbSelectionBackground),
            CheckableOption(dialog, cfg, "Editor/MonochromeSelectionForeground", dialog.gbMonochromeSelectionForeground),
            ColorOption(dialog, cfg, "Editor/SelectionForegroundColor", dialog.tbSelectionForeground),
            CheckableOption(dialog, cfg, "Editor/DefaultDocumentColours", dialog.gbDefaultDocumentColours),
            ColorOption(dialog, cfg, "Editor/DefaultDocumentPen", dialog.tbDefaultDocumentPen),
            ColorOption(dialog, cfg, "Editor/DefaultDocumentPaper", dialog.tbDefaultDocumentPaper),
        
            ChoiseOption(dialog, cfg, "Editor/AutoCompletion/Source",
                         { dialog.rbDocument: "Document",
                           dialog.rbApi: "APIs",
                           dialog.rbFromBoth: "All" }),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/CaseSensitivity",
                            dialog.cbAutoCompletionCaseSensitivity),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/ReplaceWord", dialog.cbAutoCompletionReplaceWord),
            CheckableOption(dialog, cfg, "Editor/AutoCompletion/ShowSingle", dialog.cbAutoCompletionShowSingle),
        
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

            ChoiseOption(dialog, cfg, "Editor/WhitespaceVisibility",
                         {dialog.rbWsInvisible: "Invisible",
                          dialog.rbWsVisible: "Visible",
                          dialog.rbWsVisibleAfterIndent: "VisibleAfterIndent"}),
"""
