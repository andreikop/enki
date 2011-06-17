import os.path
from PyQt4 import uic
from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QButtonGroup, \
                        QCheckBox, \
                        QDialog, \
                        QDialogButtonBox, \
                        QFont, \
                        QFontDialog, \
                        QIcon, \
                        QListWidgetItem, \
                        QRadioButton


from PyQt4.Qsci import QsciScintilla

from mks.core.core import core, DATA_FILES_PATH
from mks.plugins.editor import Editor

def tr(s):
    return s

class Plugin:
    """Module implementation
    """
    def __init__(self):
        self._action = core.actionModel().addAction("mSettings/aSettings",
                                                    tr( "Settings..."), 
                                                    QIcon(':/mksicons/settings.png'))
        self._action.setStatusTip(tr( "Edit settigns..."))
        self._action.triggered.connect(self._onEditSettings)
        self._onEditSettings()
    
    def __term__(self):
        core.actionModel().removeAction(self._action)

    def _onEditSettings(self):
        UISettings(core.mainWindow()).exec_()


class UISettings(QDialog):
    """Settings dialog
    """
    
    _AUTOCOMPLETION_SOURCE = Editor._AUTOCOMPLETION_MODE_TO_QSCI.keys()
    _CALL_TIPS_STYLE = Editor._CALL_TIPS_STYLE_TO_QSCI.keys()
    _BRACE_MATCHING = Editor._BRACE_MATCHING_TO_QSCI.keys()
    _EDGE_MODE = Editor._EDGE_MODE_TO_QSCI.keys()
    _EOL_MODE = Editor._EOL_CONVERTOR_TO_QSCI.keys()
    _WHITE_MODE = Editor._WHITE_MODE_TO_QSCI.keys()
    _WRAP_MODE = Editor._WRAP_MODE_TO_QSCI.keys()
    _WRAP_FLAG = Editor._WRAP_FLAG_TO_QSCI.keys()
    _SORT_MODE = ["OpeningOrder", "FileName", "URL", "Suffixes"]

    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self._createdObjects = []
        
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISettings.ui'), self)

        self.setAttribute( Qt.WA_DeleteOnClose )
        self.twMenu.topLevelItem( 2 ).setExpanded( True )

        # sorting mode
        self.bgSort = QButtonGroup(self.gbWorkspace)
        for index, mode in enumerate(self._SORT_MODE):
            button = QRadioButton(tr(mode))
            self._createdObjects.append(button)
            self.bgSort.addButton(button, index)
            self.gbWorkspace.layout().addWidget(button)
        
        self.loadSettings()


    def reject(self):
        """ TODO
        settings = MonkeyCore.settings()        
        for lexer in mLexers:
            lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )
        """
        QDialog.reject(self)

    def accept(self):
        self.saveSettings()
        """TODO
        self.applyProperties()
        MonkeyCore.workspace().loadSettings()
        self.apply()
        """
        QDialog.accept(self)

    def loadSettings(self):
        config = core.config()
        self._selectId(self.bgSort, self._SORT_MODE.index(config["Workspace"]["FileSortMode"]))
    
    def saveSettings(self):
        config = core.config()
        # General
        config["Workspace"]["FileSortMode"] = self._SORT_MODE[self.bgSort.checkedId()]
        
        config.flush()

    @staticmethod
    def _selectId(buttonGroup, id):
        buttons = buttonGroup.buttons()
        for button in buttons:
            if buttonGroup.id(button) == id:
                button.setChecked(True)
                break
        else:
            assert 0

        """
        for b in self.findChildren(pColorButton):
            b.setColorNameHidden( True )
        #ifdef Q_WS_MAC
            b.setIconSize( QSize( 32, 12 ) )
        #else:
            b.setIconSize( QSize( 32, 16 ) )
        #endif
        """
        
        """
        for s in availableLanguages():
            mLexers[s] = lexerForLanguage( s )
        """
        
        
        """
        # loads text codecs
        self.cbDefaultCodec.addItems( availableTextCodecs() )
        """

        """TODO
        # auto completion source
        self.bgAutoCompletionSource = QButtonGroup( self.gbAutoCompletionSource )
        self.bgAutoCompletionSource.addButton( self.rbAcsDocument, QsciScintilla.AcsDocument )
        self.bgAutoCompletionSource.addButton( self.rbAcsAPIs, QsciScintilla.AcsAPIs )
        self.bgAutoCompletionSource.addButton( self.rbAcsAll, QsciScintilla.AcsAll )

        # calltips style
        self.bgCallTipsStyle = QButtonGroup( self.gbCalltipsEnabled )
        self.bgCallTipsStyle.addButton( self.rbCallTipsNoContext, QsciScintilla.CallTipsNoContext )
        self.bgCallTipsStyle.addButton( self.rbCallTipsNoAutoCompletionContext, QsciScintilla.CallTipsNoAutoCompletionContext )
        self.bgCallTipsStyle.addButton( self.rbCallTipsContext, QsciScintilla.CallTipsContext )

        # brace match
        self.bgBraceMatch = QButtonGroup( self.gbBraceMatchingEnabled )
        self.bgBraceMatch.addButton( self.rbStrictBraceMatch, QsciScintilla.StrictBraceMatch )
        self.bgBraceMatch.addButton( self.rbSloppyBraceMatch, QsciScintilla.SloppyBraceMatch )

        # edge mode
        self.bgEdgeMode = QButtonGroup( self.gbEdgeModeEnabled )
        self.bgEdgeMode.addButton( self.rbEdgeLine, QsciScintilla.EdgeLine )
        self.bgEdgeMode.addButton( self.rbEdgeBackground, QsciScintilla.EdgeBackground )

        # fold style
        self.bgFoldStyle = QButtonGroup( self.gbFoldMarginEnabled )
        self.bgFoldStyle.addButton( self.rbPlainFoldStyle, QsciScintilla.PlainFoldStyle )
        self.bgFoldStyle.addButton( self.rbCircledTreeFoldStyle, QsciScintilla.CircledTreeFoldStyle )
        self.bgFoldStyle.addButton( self.rbCircledFoldStyle, QsciScintilla.CircledFoldStyle )
        self.bgFoldStyle.addButton( self.rbBoxedFoldStyle, QsciScintilla.BoxedFoldStyle )
        self.bgFoldStyle.addButton( self.rbBoxedTreeFoldStyle, QsciScintilla.BoxedTreeFoldStyle )

        # eol mode
        self.bgEolMode = QButtonGroup( self.gbEolMode )
        self.bgEolMode.addButton( self.rbEolUnix, QsciScintilla.EolUnix )
        self.bgEolMode.addButton( self.rbEolMac, QsciScintilla.EolMac )
        self.bgEolMode.addButton( self.rbEolWindows, QsciScintilla.EolWindows )

        # whitespace visibility
        self.bgWhitespaceVisibility = QButtonGroup( self.gbWhitespaceVisibilityEnabled )
        self.bgWhitespaceVisibility.addButton( self.rbWsVisible, QsciScintilla.WsVisible )
        self.bgWhitespaceVisibility.addButton( self.rbWsVisibleAfterIndent, QsciScintilla.WsVisibleAfterIndent )

        # wrap mode
        self.bgWrapMode = QButtonGroup( self.gbWrapModeEnabled )
        self.bgWrapMode.addButton( self.rbWrapWord, QsciScintilla.WrapWord )
        self.bgWrapMode.addButton( self.rbWrapCharacter, QsciScintilla.WrapCharacter )

        # wrap visual flag
        self.bgStartWrapVisualFlag = QButtonGroup( wStartWrapVisualFlags )
        self.bgStartWrapVisualFlag.addButton( self.rbStartWrapFlagByText, QsciScintilla.WrapFlagByText )
        self.bgStartWrapVisualFlag.addButton( self.rbStartWrapFlagByBorder, QsciScintilla.WrapFlagByBorder )
        self.bgEndWrapVisualFlag = QButtonGroup( wEndWrapVisualFlags )
        self.bgEndWrapVisualFlag.addButton( self.rbEndWrapFlagByText, QsciScintilla.WrapFlagByText )
        self.bgEndWrapVisualFlag.addButton( self.rbEndWrapFlagByBorder, QsciScintilla.WrapFlagByBorder )

        # fill lexers combo
        self.cbSourceAPIsLanguages.addItems( availableLanguages() )
        self.cbLexersAssociationsLanguages.addItems( availableLanguages() )
        self.cbLexersHighlightingLanguages.addItems( availableLanguages() )

        # resize column
        self.twLexersAssociations.setColumnWidth( 0, 200 )

        # python indentation warning
        self.cbLexersHighlightingIndentationWarning.addItem( self.tr( "No warning" ), QsciLexerPython.NoWarning )
        self.cbLexersHighlightingIndentationWarning.addItem( self.tr( "Inconsistent" ), QsciLexerPython.Inconsistent )
        self.cbLexersHighlightingIndentationWarning.addItem( self.tr( "Tabs after spaces" ), QsciLexerPython.TabsAfterSpaces )
        self.cbLexersHighlightingIndentationWarning.addItem( self.tr( "Spaces" ), QsciLexerPython.Spaces )
        self.cbLexersHighlightingIndentationWarning.addItem( self.tr( "Tabs" ), QsciLexerPython.Tabs )

        # resize column
        self.twAbbreviations.setColumnWidth( 0, 100 )
        self.twAbbreviations.setColumnWidth( 1, 180 )

        # read settings
        self.loadSettings()

        # connections
        # event filter
        # margin font
        self.tbMarginsFont.clicked.connect(self.tbFonts_clicked)
        # lexer elements highlighting
        self.pbLexersHighlightingForeground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingBackground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingFont.clicked.connect(self.lexersHighlightingFont_clicked)
        self.pbLexersHighlightingAllForeground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingAllBackground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingAllFont.clicked.connect(self.lexersHighlightingFont_clicked)
        for cb in self.gbLexersHighlightingElements.findChildren(QCheckBox):
            if  self.cb != self.cbLexersHighlightingFillEol :
                self.cb.clicked.connect(self.cbLexersHighlightingProperties_clicked)
        # apply button
        self.dbbButtons.button( QDialogButtonBox.Apply ).clicked.connect(self.apply)

        for widget in  self.findChildren(QWidget):
            widget.setAttribute( Qt.WA_MacSmallSize, True )
            widget.setAttribute( Qt.WA_MacShowFocusRect, False )

        # resize to minimum size
        self.resize( self.minimumSizeHint() )

--------------------------------------------------------

        # General
        self.cbSaveSession.setChecked( saveSessionOnClose() )
        self.cbRestoreSession.setChecked( restoreSessionOnStartup() )


        # Editor
        editorConfig = core.config()["Editor"]
        #  General
        
        self.cbAutoSyntaxCheck.setChecked( autoSyntaxCheck() )
        
        self.cbConvertTabsUponOpen.setChecked( myConfig["Indentation"]["ConvertUponOpen"] )
        self.cbCreateBackupUponOpen.setChecked( myConfig["CreateBackupUponOpen"] )
        
        self.cbDefaultCodec.setCurrentIndex( self.cbDefaultCodec.findText( defaultCodec() ) )
        
        self.tbSelectionBackground.setColor( myConfig["SelectionBackgroundColor"] )
        self.tbSelectionForeground.setColor( myConfig["SelectionForegroundColor"] )
        self.gbDefaultDocumentColours.setChecked( myConfig["DefaultDocumentColours"] )
        self.tbDefaultDocumentPen.setColor( myConfig["DefaultDocumentPen"] )
        self.tbDefaultDocumentPaper.setColor( myConfig["DefaultDocumentPaper"] )
        defFont = QFont(myConfig["DefaultFont"], myConfig["DefaultFontSize"])
        lDefaultDocumentFont.setFont( defFont )
        lDefaultDocumentFont.setToolTip( defFont.toString() )
        #  Auto Completion
        self.cbAutoCompletionCaseSensitivity.setChecked( myConfig["AutoCompletion"]["CaseSensitivity"] )
        self.cbAutoCompletionReplaceWord.setChecked( myConfig["AutoCompletion"]["ReplaceWord"] )
        self.cbAutoCompletionShowSingle.setChecked( myConfig["AutoCompletion"]["ShowSingle"] )
        sAutoCompletionThreshold.setValue( myConfig["AutoCompletion"]["Threshold"] )
        self.bgAutoCompletionSource.button( _AUTOCOMPLETION_SOURCE[myConfig["AutoCompletion"]["Source"]] ).setChecked( True )
        
        #  Call Tips
        self.gbCalltipsEnabled.setChecked( myConfig["CallTips"]["Style"] != "None" )
        sCallTipsVisible.setValue( myConfig["CallTips"]["Visible"] )
        self.bgCallTipsStyle.button( myConfig["CallTips"]["Style"] ).setChecked( True )
        self.tbCalltipsBackground.setColor( QColor(myConfig["CallTips"]["BackgroundColor"]) )
        self.tbCalltipsForeground.setColor( QColor(myConfig["CallTips"]["ForegroundColor"]) )
        self.tbCalltipsHighlight.setColor( QColor(myConfig["CallTips"]["HighlightColor"]) )
        #  Indentation
        self.cbAutoIndent.setChecked( myConfig["Indentation"]["AutoIndent"] )
        self.cbBackspaceUnindents.setChecked( myConfig["Indentation"]["BackspaceUnindents"] )
        self.cbIndentationGuides.setChecked( myConfig["Indentation"]["Guides"] )
        self.cbIndentationUseTabs.setChecked( myConfig["Indentation"]["UseTabs"] )
        self.cbAutodetectIndent.setChecked( myConfig["Indentation"]["AutoDetect"] )
        self.cbTabIndents.setChecked( myConfig["Indentation"]["TabIndents"] )
        sIndentationTabWidth.setValue( myConfig["Indentation"]["TabWidth"] )
        sIndentationWidth.setValue( myConfig["Indentation"]["Width"] )
        self.tbIndentationGuidesBackground.setColor( QColor(myConfig["Indentation"]["GuidesBackgroundColor"]) )
        self.tbIndentationGuidesForeground.setColor( QColor(myConfig["Indentation"]["GuidesForegroundColor"]) )
        #  Brace Matching
        self.gbBraceMatchingEnabled.setChecked( myConfig["BraceMatching"]["Mode"] != 'None' )
        self.bgBraceMatch.button( myConfig["BraceMatching"]["Mode"] ).setChecked( True )
        self.tbMatchedBraceForeground.setColor( QColor(myConfig["BraceMatching"]["MatchedForegroundColor"]) )
        self.tbMatchedBraceBackground.setColor( QColor(myConfig["BraceMatching"]["MatchedBackgroundColor"]) )
        self.tbUnmatchedBraceBackground.setColor( QColor(myConfig["BraceMatching"]["UnmatchedBackgroundColor"]) )
        self.tbUnmatchedBraceForeground.setColor( QColor(myConfig["BraceMatching"]["UnmatchedForegroundColor"]) )
        #  Edge Mode
        self.gbEdgeModeEnabled.setChecked( myConfig["Edge"]["Mode"] != 'None' )
        self.bgEdgeMode.button( myConfig["Edge"]["Mode"] ).setChecked( True )
        sEdgeColumnNumber.setValue( myConfig["Edge"]["Column"] )
        self.tbEdgeColor.setColor( QColor(myConfig["Edge"]["Color"]) )
        #  Caret
        self.gbCaretLineVisible.setChecked( myConfig["Caret"]["LineVisible"] )
        self.tbCaretLineBackground.setColor( QColor(myConfig["Caret"]["LineBackgroundColor"]) )
        self.tbCaretForeground.setColor( myConfig["Caret"]["ForegroundColor"]) )
        sCaretWidth.setValue( myConfig["Caret"]["Width"] )
        #  Margins
        
        self.gbLineNumbersMarginEnabled.setChecked( lineNumbersMarginEnabled() )
        sLineNumbersMarginWidth.setValue( lineNumbersMarginWidth() )
        self.cbLineNumbersMarginAutoWidth.setChecked( lineNumbersMarginAutoWidth() )
        
        self.gbFoldMarginEnabled.setChecked( folding() != QsciScintilla.NoFoldStyle )
        if  self.bgFoldStyle.button( folding() ) :
            self.bgFoldStyle.button( folding() ).setChecked( True )
        self.tbFoldMarginForeground.setColor( foldMarginForegroundColor() )
        self.tbFoldMarginBackground.setColor( foldMarginBackgroundColor() )
        self.gbMarginsEnabled.setChecked( marginsEnabled() )
        self.tbMarginsForeground.setColor( marginsForegroundColor() )
        self.tbMarginsBackground.setColor( marginsBackgroundColor() )
        self.tbMarginsFont.setFont( marginsFont() )
        
        #  Special Characters
        self.bgEolMode.button( myConfig["EOL"]["Mode"] ).setChecked( True )
        self.cbEolVisibility.setChecked( myConfig["EOL"]["Visibility"] )
        self.cbAutoDetectEol.setChecked( myConfig["EOL"]["AutoDetect"] )
        self.cbAutoEolConversion.setChecked( myConfig["EOL"]["AutoConvert"] )
        self.gbWhitespaceVisibilityEnabled.setChecked( myConfig["WhitespaceVisibility"] != "Invisible")
        self.bgWhitespaceVisibility.button( myConfig["WhitespaceVisibility"] ).setChecked( True )
        self.gbWrapModeEnabled.setChecked( myConfig["Wrap"]["Mode"] != 'None' )
        self.bgWrapMode.button( myConfig["Wrap"]["Mode"] ).setChecked( True )
        #self.bgStartWrapVisualFlag.button( myConfig["Wrap"]["StartVisualFlag"] ).setChecked( True )
        #self.bgEndWrapVisualFlag.button( myConfig["Wrap"]["EndVisualFlag"] ).setChecked( True )
        sWrappedLineIndentWidth.setValue( myConfig["Wrap"]["LineIndentWidth"] )
        
        # Source APIs
        for ( i = 0; i < self.cbSourceAPIsLanguages.count(); i++ )
            self.cbSourceAPIsLanguages.setItemData( i, s.value( "SourceAPIs/" +cbSourceAPIsLanguages.itemText( i ) ).toStringList() )
        if  self.cbSourceAPIsLanguages.count() > 0 :
            self.cbSourceAPIsLanguages.setCurrentIndex( 0 )
        #  Lexers Associations
        QMap<QString, l = MonkeyCore.fileManager().associations()
        for k in l.keys():
            foreach ( QString e, l.value( k ) )
                it = QTreeWidgetItem( self.twLexersAssociations )
                it.setText( 0, e )
                it.setText( 1, k )


        #  Lexers Highlighting
        for l in mLexers:
            l.readSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )

        if  self.cbLexersHighlightingLanguages.count() :
            on_cbLexersHighlightingLanguages_currentIndexChanged( self.cbLexersHighlightingLanguages.itemText( 0 ) )

        #  Abbreviations
        for a in MonkeyCore.abbreviationsManager().abbreviations():
            it = QTreeWidgetItem( self.twAbbreviations )
            it.setText( 0, a.Macro )
            it.setText( 1, a.Description )
            it.setText( 2, a.Language )
            it.setData( 0, Qt.UserRole, a.Snippet )

        
        # environment variables editor
        eveVariables.setVariables( MonkeyCore.consoleManager().environmentVariablesManager().variables(), True )
        

------------------------------------------------------------
        
        
        setSaveSessionOnClose( self.cbSaveSession.isChecked() )
        setRestoreSessionOnStartup( self.cbRestoreSession.isChecked() )
        # Editor
        #  General
        # TODO setAutoSyntaxCheck( self.cbAutoSyntaxCheck.isChecked() )
        myConfig["Indentation"]["ConvertUponOpen"] = self.cbConvertTabsUponOpen.isChecked()
        myConfig["CreateBackupUponOpen"] = self.cbCreateBackupUponOpen.isChecked()
        # TODO setDefaultCodec( self.cbDefaultCodec.currentText() )
        myConfig["SelectionBackgroundColor"] = self.tbSelectionBackground.color().name()
        myConfig["SelectionForegroundColor"] = self.tbSelectionForeground.color().name()
        myConfig["DefaultDocumentColours"] = self.gbDefaultDocumentColours.isChecked()
        myConfig["DefaultDocumentPen"] = self.tbDefaultDocumentPen.color().name()
        myConfig["DefaultDocumentPaper"] = self.tbDefaultDocumentPaper.color().name()
        myConfig["DefaultFont"] = lDefaultDocumentFont.font().family()
        myConfig["DefaultFontSize"] = lDefaultDocumentFont.font().size()
        #  Auto Completion
        myConfig["AutoCompletion"]["Source"] = _AUTOCOMPLETION_SOURCE[bgAutoCompletionSource.checkedId()]
        myConfig["AutoCompletion"]["CaseSensitivity"] = self.cbAutoCompletionCaseSensitivity.isChecked()
        myConfig["AutoCompletion"]["ReplaceWord"] = self.cbAutoCompletionReplaceWord.isChecked()
        myConfig["AutoCompletion"]["ShowSingle"] = self.cbAutoCompletionShowSingle.isChecked()
        myConfig["AutoCompletion"]["Threshold"] = sAutoCompletionThreshold.value()
        #  Call Tips
        myConfig["CallTips"]["Style"] = _CALL_TIPS_STYLE[bgCallTipsStyle.checkedId()]
        myConfig["CallTips"]["Visible"] = sCallTipsVisible.value()
        myConfig["CallTips"]["BackgroundColor"] = self.tbCalltipsBackground.color().name()
        myConfig["CallTips"]["ForegroundColor"] = self.tbCalltipsForeground.color().name()
        myConfig["CallTips"]["HighlightColor"] = self.tbCalltipsHighlight.color().name()
        #  Indentation
        myConfig["Indentation"]["AutoIndent"] = self.cbAutoIndent.isChecked()
        myConfig["Indentation"]["BackspaceUnindents"] = self.cbBackspaceUnindents.isChecked()
        myConfig["Indentation"]["Guides"] = self.cbIndentationGuides.isChecked()
        myConfig["Indentation"]["UseTabs"] = self.cbIndentationUseTabs.isChecked()
        myConfig["Indentation"]["TabIndents"] = self.cbTabIndents.isChecked()
        myConfig["Indentation"]["AutoDetect"] = self.cbAutodetectIndent.isChecked()
        myConfig["Indentation"]["TabWidth"] = sIndentationTabWidth.value()
        myConfig["Indentation"]["Width"] = sIndentationWidth.value()
        myConfig["Indentation"]["GuidesBackgroundColor"] = self.tbIndentationGuidesBackground.color().name()
        myConfig["Indentation"]["GuidesForegroundColor"] = self.tbIndentationGuidesForeground.color().name()
        #  Brace Matching
        myConfig["BraceMatching"]["Mode"] = _BRACE_MATCHING[bgBraceMatch.checkedId()]
        myConfig["BraceMatching"]["MatchedForegroundColor"] = self.tbMatchedBraceBackground.color().name()
        myConfig["BraceMatching"]["MatchedBackgroundColor"] = self.tbMatchedBraceForeground.color().name()
        myConfig["BraceMatching"]["UnmatchedBackgroundColor"] = self.tbUnmatchedBraceBackground.color().name()
        myConfig["BraceMatching"]["UnmatchedForegroundColor"] = self.tbUnmatchedBraceForeground.color().name()
        #  Edge Mode
        myConfig["Edge"]["Mode"] = _EDGE_MODE[bgEdgeMode.checkedId()]
        myConfig["Edge"]["Column"] = sEdgeColumnNumber.value()
        myConfig["Edge"]["Color"].name()
        #  Caret
        myConfig["Caret"]["LineVisible"] = self.gbCaretLineVisible.isChecked()
        myConfig["Caret"]["LineBackgroundColor"] = self.tbCaretLineBackground.color().name()
        myConfig["Caret"]["ForegroundColor"] = self.tbCaretForeground.color().name()
        myConfig["Caret"]["Width"] = sCaretWidth.value()
        
        #  Margins
        setLineNumbersMarginEnabled( self.gbLineNumbersMarginEnabled.isChecked() )
        setLineNumbersMarginWidth( sLineNumbersMarginWidth.value() )
        setLineNumbersMarginAutoWidth( self.cbLineNumbersMarginAutoWidth.isChecked() )
        setFolding( QsciScintilla.NoFoldStyle )
        if  self.gbFoldMarginEnabled.isChecked() :
            setFolding( (QsciScintilla.FoldStyle)bgFoldStyle.checkedId() )
        setFoldMarginForegroundColor( self.tbFoldMarginForeground.color() )
        setFoldMarginBackgroundColor( self.tbFoldMarginBackground.color() )
        setMarginsEnabled( self.gbMarginsEnabled.isChecked() )
        setMarginsForegroundColor( self.tbMarginsForeground.color() )
        setMarginsBackgroundColor( self.tbMarginsBackground.color() )
        setMarginsFont( self.tbMarginsFont.font() )
        
        #  Special Characters
        myConfig["EOL"]["Mode"] = _EOL_MODE[self.bgEolMode.checkedId()]
        myConfig["EOL"]["Visibility"] = self.cbEolVisibility.isChecked()
        myConfig["EOL"]["AutoDetect"] = self.cbAutoDetectEol.isChecked()
        myConfig["EOL"]["AutoConvert"] = self.cbAutoEolConversion.isChecked()
        myConfig["WhitespaceVisibility"] = _WHITESPACE_MODE[bgWhitespaceVisibility.checkedId()]
        myConfig["Wrap"]["Mode"] = _WRAP_MODE[bgWrapMode.checkedId()]
        myConfig["Wrap"]["StartVisualFlag"] = _WRAP_FLAG[bgStartWrapVisualFlag.checkedId()]
        myConfig["Wrap"]["EndVisualFlag"] = _WRAP_FLAG[bgEndWrapVisualFlag.checkedId()]
        myConfig["Wrap"]["LineIndentWidth"] = sWrappedLineIndentWidth.value()
        # Source APIs
        
        sp = "SourceAPIs/"
        for ( i = 0; i < self.cbSourceAPIsLanguages.count(); i++ )
            s.setValue( sp +cbSourceAPIsLanguages.itemText( i ), self.cbSourceAPIsLanguages.itemData( i ).toStringList() )

        #  Lexers Associations
        QMap<QString, suffixes

        for ( i = 0; i < self.twLexersAssociations.topLevelItemCount(); i++ )
            it = self.twLexersAssociations.topLevelItem( i )

            suffixes[ it.text( 1 ) ] << it.text( 0 )


        for type in suffixes.keys():
            MonkeyCore.fileManager().setCommand( type, suffixes[ type ] )


        MonkeyCore.fileManager().generateScript()

        #  Lexers Highlighting
        for l in mLexers:
            l.setDefaultPaper( self.tbDefaultDocumentPaper.color() )
            l.setDefaultColor( self.tbDefaultDocumentPen.color() )
            l.writeSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )


        #  Abbreviations
        pAbbreviationList abbreviations
        for ( i = 0; i < self.twAbbreviations.topLevelItemCount(); i++ )
            it = self.twAbbreviations.topLevelItem( i )

            pAbbreviation abbreviation
            abbreviation.Macro = it.text( 0 )
            abbreviation.Description = it.text( 1 )
            abbreviation.Language = it.text( 2 )
            abbreviation.Snippet = it.data( 0, Qt.UserRole ).toString()

            abbreviations << abbreviation


        MonkeyCore.abbreviationsManager().set( abbreviations )
        MonkeyCore.abbreviationsManager().generateScript()
        
        # environment variables editor
        MonkeyCore.consoleManager().environmentVariablesManager().setVariables( eveVariables.variables() )
        MonkeyCore.consoleManager().environmentVariablesManager().save()

        # flush settings to disk
        s.sync()
        

    def on_twMenu_itemSelectionChanged(self):
        # get item
        it = self.twMenu.selectedItems()[0]

        if  it :
            lInformations.setText( it.text( 0 ) )
            i = self.twMenu.indexOfTopLevelItem( it )
            if  not it.parent() :
                if i in (0, 1, 2):
                    swPages.setCurrentIndex( i )
                else:
                    swPages.setCurrentIndex( i +11 )
            else:
                swPages.setCurrentIndex( it.parent().indexOfChild( it ) +2 )

    def on_pbDefaultDocumentFont_clicked(self):
        font = lDefaultDocumentFont.font()
        
        font, ok = QFontDialog.getFont( font, self, self.tr( "Choose the default document font" ), QFontDialog.DontUseNativeDialog )
        
        if ok:
            lDefaultDocumentFont.setFont( font )
            lDefaultDocumentFont.setToolTip( font.toString() )

    def on_gbAutoCompletionEnabled_clicked(self, checked ):
        if  checked and self.bgAutoCompletionSource.checkedId() == -1 :
            mode = autoCompletionSource()
            
            if  mode == QsciScintilla.AcsNone :
                mode = QsciScintilla.AcsAll

            self.bgAutoCompletionSource.button( mode ).setChecked( True )

    def on_tbFonts_clicked(self):
        toolButton = self.sender()
        f, b = QFontDialog.getFont(toolButton.font(), self.window() )
        if  b:
            self.tb.setFont( f )

    def on_cbSourceAPIsLanguages_beforeChanged(self, i ):
        if  i == self.cbSourceAPIsLanguages.currentIndex() :
            l = [lwSourceAPIs.item( j ).text() for j in range(lwSourceAPIs.count())]
            self.cbSourceAPIsLanguages.setItemData( i, l )

    def on_cbSourceAPIsLanguages_currentIndexChanged(self, i ):
        lwSourceAPIs.clear()
        lwSourceAPIs.addItems( self.cbSourceAPIsLanguages.itemData( i ).toStringList() )

    def on_pbSourceAPIsDelete_clicked(self):
        # get selected item
        it = lwSourceAPIs.selectedItems()[0]
        if  it :
            del it
            self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )

    def on_pbSourceAPIsAdd_clicked(self):
        # get files
        files = leSourceAPIs.text().split(";")
        # add them recursively
        for fn in files:
            if  lwSourceAPIs.findItems( fn, Qt.MatchFixedString ).count() == 0 :
                lwSourceAPIs.addItem( fn )
        # clear input
        leSourceAPIs.clear()
        # save datas
        self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )

    def on_pbSourceAPIsBrowse_clicked(self):
        files = QFileDialog.getOpenFileNames( self.window(), self.tr( "Select API files" ), QString.null, self.tr( "API Files (*.api);;All Files (*)" ) )
        if files:
            leSourceAPIs.setText( ';'.join(files))

    def on_twLexersAssociations_itemSelectionChanged(self):
        it = self.twLexersAssociations.selectedItems()[0]
        if  it :
            leLexersAssociationsFilenamePattern.setText( it.text( 0 ) )
            self.cbLexersAssociationsLanguages.setCurrentIndex( self.cbLexersAssociationsLanguages.findText( it.text( 1 ) ) )

    def on_pbLexersAssociationsAddChange_clicked(self):
        f = leLexersAssociationsFilenamePattern.text()
        l = self.cbLexersAssociationsLanguages.currentText()
        if  f.isEmpty() or l.isEmpty() :
            return
        it = self.twLexersAssociations.selectedItems()[0]
        if  not it or it.text[0] != f :
            # check if item with same parameters already exists
            l = self.twLexersAssociations.findItems( f, Qt.MatchFixedString )
            if  l.count() :
                it = l.at( 0 )
            else:
                it = QTreeWidgetItem( self.twLexersAssociations )

        it.setText( 0, f )
        it.setText( 1, l )
        self.twLexersAssociations.setCurrentItem( 0 )
        self.twLexersAssociations.selectionModel().clear()
        leLexersAssociationsFilenamePattern.clear()
        self.cbLexersAssociationsLanguages.setCurrentIndex( -1 )

    def on_pbLexersAssociationsDelete_clicked(self):
        it = self.twLexersAssociations.selectedItems()[0]
        if  it :
            del it
            self.twLexersAssociations.setCurrentItem( 0 )
            self.twLexersAssociations.selectionModel().clear()
            leLexersAssociationsFilenamePattern.clear()
            self.cbLexersAssociationsLanguages.setCurrentIndex( -1 )

    def on_cbLexersHighlightingLanguages_currentIndexChanged(self, s ):
        l = mLexers[s]
        lwLexersHighlightingElements.clear()
        for i in range(128):
            n = l.description( i )
            if n:
                it = QListWidgetItem( lwLexersHighlightingElements )
                it.setText( n )
                it.setForeground( l.color( i ) )
                it.setBackground( l.paper( i ) )
                it.setFont( l.font( i ) )
                it.setData( Qt.UserRole, i )
        
        # fold comments
        v = lexerProperty( "foldComments", l )
        self.cbLexersHighlightingFoldComments.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldComments.setChecked( v.toBool() )
        # fold compact
        v = lexerProperty( "foldCompact", l )
        self.cbLexersHighlightingFoldCompact.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldCompact.setChecked( v.toBool() )
        # fold quotes
        v = lexerProperty( "foldQuotes", l )
        self.cbLexersHighlightingFoldQuotes.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldQuotes.setChecked( v.toBool() )
        # fold directives
        v = lexerProperty( "foldDirectives", l )
        self.cbLexersHighlightingFoldDirectives.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldDirectives.setChecked( v.toBool() )
        # fold at begin
        v = lexerProperty( "foldAtBegin", l )
        self.cbLexersHighlightingFoldAtBegin.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldAtBegin.setChecked( v.toBool() )
        # fold at parenthesis
        v = lexerProperty( "foldAtParenthesis", l )
        self.cbLexersHighlightingFoldAtParenthesis.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldAtParenthesis.setChecked( v.toBool() )
        # fold at else:
        v = lexerProperty( "foldAtElse", l )
        self.cbLexersHighlightingFoldAtElse.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldAtElse.setChecked( v.toBool() )
        # fold at module
        v = lexerProperty( "foldAtModule", l )
        self.cbLexersHighlightingFoldAtModule.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldAtModule.setChecked( v.toBool() )
        # fold preprocessor
        v = lexerProperty( "foldPreprocessor", l )
        self.cbLexersHighlightingFoldPreprocessor.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingFoldPreprocessor.setChecked( v.toBool() )
        # style preprocessor
        v = lexerProperty( "stylePreprocessor", l )
        self.cbLexersHighlightingStylePreprocessor.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingStylePreprocessor.setChecked( v.toBool() )
        # indent opening brace
        self.cbLexersHighlightingIndentOpeningBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiOpening )
        # indent closing brace
        self.cbLexersHighlightingIndentClosingBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiClosing )
        # case sensitive tags
        v = lexerProperty( "caseSensitiveTags", l )
        self.cbLexersHighlightingCaseSensitiveTags.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingCaseSensitiveTags.setChecked( v.toBool() )
        # backslash escapes
        v = lexerProperty( "backslashEscapes", l )
        self.cbLexersHighlightingBackslashEscapes.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexersHighlightingBackslashEscapes.setChecked( v.toBool() )
        # indentation warning
        v = lexerProperty( "indentationWarning", l )
        lLexersHighlightingIndentationWarning.setVisible( v.isValid() )
        self.cbLexersHighlightingIndentationWarning.setVisible( lLexersHighlightingIndentationWarning.isVisible() )
        if  v.isValid() :
            self.cbLexersHighlightingIndentationWarning.setCurrentIndex( self.cbLexersHighlightingIndentationWarning.findData( v.toInt() ) )


    def on_lwLexersHighlightingElements_itemSelectionChanged(self):
        it = lwLexersHighlightingElements.selectedItems()[0]
        if  it :
            self.cbLexersHighlightingFillEol.setChecked( mLexers.value[self.cbLexersHighlightingLanguages.currentText()].eolFill( it.data( Qt.UserRole ).toInt() ) )

    def lexersHighlightingColour_clicked(self):
        # get self.sender
        o = self.sender()
        # color
        # element colour
        if  o == self.pbLexersHighlightingForeground or o == self.pbLexersHighlightingBackground :
            # get item
            it = lwLexersHighlightingElements.selectedItems()[0]
            # cancel if no item
            if  not it :
                return
            # get color
            if o == self.pbLexersHighlightingForeground:
                p = it.foreground().color()
            else:
                p = it.background().color
            c = QColorDialog.getColor(p, self.window() )
            # apply color
            if  c.isValid() :
                if  o == self.pbLexersHighlightingForeground :
                    it.setForeground( c )
                    mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).setColor( c, it.data( Qt.UserRole ).toInt() )
                elif  o == self.pbLexersHighlightingBackground :
                    it.setBackground( c )
                    mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).setPaper( c, it.data( Qt.UserRole ).toInt() )
        # gobal color
        elif  o == self.pbLexersHighlightingAllForeground or o == self.pbLexersHighlightingAllBackground :
            # get lexer
            l = mLexers.value( self.cbLexersHighlightingLanguages.currentText() )
            # get color
            c = QColorDialog.getColor( o == self.pbLexersHighlightingAllForeground ? l.color( -1 ) : l.paper( -1 ), self.window() )
            # apply
            if  c.isValid() :
                if  o == self.pbLexersHighlightingAllForeground :
                    l.setColor( c, -1 )
                elif  o == self.pbLexersHighlightingAllBackground :
                    l.setPaper( c, -1 )
                # refresh
                on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )

    def lexersHighlightingFont_clicked(self):
        # get self.sender
        o = self.sender()
        # values
        # element font
        if  o == self.pbLexersHighlightingFont :
            # get item
            it = lwLexersHighlightingElements.selectedItems()[0]
            # cancel if no item
            if  not it :
                return
            # get font
            f, b = QFontDialog.getFont( &b, it.font(), self.window() )
            # apply
            if  b :
                it.setFont( f )
                mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).setFont( f, it.data( Qt.UserRole ).toInt() )
        # global font
        elif  o == self.pbLexersHighlightingAllFont :
            # get lexer
            l = mLexers[self.cbLexersHighlightingLanguages.currentText()]
            # get font
            f, b = QFontDialog.getFont(l.font( -1 ), self.window() )
            # apply
            if  b :
                l.setFont( f, -1 )
                on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )

    def on_cbLexersHighlightingFillEol_clicked(self, b ):
        it = lwLexersHighlightingElements.selectedItems()[0]
        if  it :
            mLexers[self.cbLexersHighlightingLanguages.currentText()].setEolFill( b, it.data( Qt.UserRole ).toInt() )

    def on_cbLexersHighlightingProperties_clicked(self, b ):
        # get check box
        checkBox = self.sender()
        # get lexer
        l = mLexers[self.cbLexersHighlightingLanguages.currentText()]
        # set lexer properties
        if  checkBox == self.cbLexersHighlightingIndentOpeningBrace or checkBox == self.cbLexersHighlightingIndentClosingBrace :
            if  self.cbLexersHighlightingIndentOpeningBrace.isChecked() and self.cbLexersHighlightingIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening | QsciScintilla.AiClosing )
            elif  self.cbLexersHighlightingIndentOpeningBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening )
            elif  self.cbLexersHighlightingIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiClosing )
            else:
                l.setAutoIndentStyle( QsciScintilla.AiMaintain )
        else:
            setLexerProperty( checkBox.statusTip(), l, b )

    def on_cbLexersHighlightingIndentationWarning_currentIndexChanged(self, i ):
        # get lexer
        l = mLexers[self.cbLexersHighlightingLanguages.currentText()]
        # set lexer properties
        setLexerProperty( self.cbLexersHighlightingIndentationWarning.statusTip(), l, self.cbLexersHighlightingIndentationWarning.itemData( i ) )

    def on_pbLexersHighlightingReset_clicked(self):
        # get lexer
        l = mLexers[self.cbLexersHighlightingLanguages.currentText()]
        # reset and refresh
        if  l :
            resetLexer( l )
            on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )

    def on_pbLexersApplyDefaultFont_clicked(self):
        settings = MonkeyCore.settings()
        font = lDefaultDocumentFont.font()
        language = self.cbLexersHighlightingLanguages.currentText()
        
        settings.setDefaultLexerProperties( font, False )
        on_cbLexersHighlightingLanguages_currentIndexChanged( language )

    def on_twAbbreviations_itemSelectionChanged(self):
        # get item
        it = self.twAbbreviations.selectedItems()[0]
        if  it :
            teAbbreviationsCode.setPlainText( it.data( 0, Qt.UserRole ).toString() )
        # enable/disable according to selection
        teAbbreviationsCode.setEnabled( it )

    def on_pbAbbreviationsAdd_clicked(self):
        UIAddAbbreviation.edit( self.twAbbreviations );

    def on_pbAbbreviationsRemove_clicked(self):
        del self.twAbbreviations.selectedItems()[0]
        teAbbreviationsCode.clear()

    def on_teAbbreviationsCode_textChanged(self):
        # get item
        it = self.twAbbreviations.selectedItems()[0]
        if  it :
            it.setData( 0, Qt.UserRole, teAbbreviationsCode.toPlainText() )

    def reject(self):
        
        settings = MonkeyCore.settings()        
        for lexer in mLexers:
            lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )
        
        QDialog.reject(self)

    def accept(self):
        self.saveSettings()
        self.applyProperties()
        MonkeyCore.workspace().loadSettings()
        self.apply()
        QDialog.accept(self)
"""
