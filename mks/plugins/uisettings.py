from PyQt4 import uic
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QButtonGroup,
                        QCheckBox,
                        QDialog,
                        QDialogButtonBox

from PyQt4.Qsci import QsciScintilla

class UISettings(QDialog):
    """Settings dialog
    """
    
    _AUTOCOMPLETION_SOURCE = ("None", "All", "Document", "APIs")
    _CALL_TIPS_STYLE = ("None", "NoContext", "NoAutoCompletionContext", "Context")
    
    def __init__(self, **kwargs):
        QDialog.__init__(self, kwargs)
        
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISaveSettings.ui'), self)

        self.setAttribute( Qt.WA_DeleteOnClose )
        self.twMenu.topLevelItem( 2 ).setExpanded( True )
        self.twMenu.setCurrentItem( self.twMenu.topLevelItem( 0 ) )

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

        # sorting mode
        self.cbSortingMode.addItem( self.tr( "Opening order" ), "OpeningOrder" )
        self.cbSortingMode.addItem( self.tr( "File name" ), "FileName" )
        self.cbSortingMode.addItem( self.tr( "Url" ), "URL" )
        self.cbSortingMode.addItem( self.tr( "Suffixes" ), "Suffixes" )
        self.cbSortingMode.addItem( self.tr( "Custom" ), "Custom" )

        """
        # loads text codecs
        self.cbDefaultCodec.addItems( availableTextCodecs() )
        """

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


    def loadSettings(self):
        config = core.config()

        # General
        """TODO
        self.cbSaveSession.setChecked( saveSessionOnClose() )
        self.cbRestoreSession.setChecked( restoreSessionOnStartup() )
        """
        self.cbSortingMode.setCurrentIndex( self.cbSortingMode.findData( config["Workspace"]["FileSortMode"] ) )

        # Editor
        editorConfig = core.config()["Editor"]
        #  General
        """TODO
        self.cbAutoSyntaxCheck.setChecked( autoSyntaxCheck() )
        """
        self.cbConvertTabsUponOpen.setChecked( myConfig["Indentation"]["ConvertUponOpen"] )
        self.cbCreateBackupUponOpen.setChecked( myConfig["CreateBackupUponOpen"] )
        """TODO
        self.cbDefaultCodec.setCurrentIndex( self.cbDefaultCodec.findText( defaultCodec() ) )
        """
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
        """
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
        """
        #  Special Characters
        self.bgEolMode.button( myConfig["EOL"]["Mode"] ).setChecked( True )
        self.cbEolVisibility.setChecked( myConfig["EOL"]["Visibility"] )
        self.cbAutoDetectEol.setChecked( myConfig["EOL"]["AutoDetect"] )
        self.cbAutoEolConversion.setChecked( myConfig["EOL"]["AutoConvert"] )
        self.gbWhitespaceVisibilityEnabled.setChecked( myConfig["WhitespaceVisibility"] != "Invisible")
        self.bgWhitespaceVisibility.button( myConfig["WhitespaceVisibility"] ).setChecked( True )
        self.gbWrapModeEnabled.setChecked( myConfig["Wrap"]["Mode"] != 'None' )
        self.bgWrapMode.button( myConfig["Wrap"]["Mode"] ).setChecked( True )
        self.gbWrapVisualFlagsEnabled.setChecked( wrapVisualFlagsEnabled() )
        self.bgStartWrapVisualFlag.button( myConfig["Wrap"]["StartVisualFlag"] ).setChecked( True )
        self.bgEndWrapVisualFlag.button( myConfig["Wrap"]["EndVisualFlag"] ).setChecked( True )
        sWrappedLineIndentWidth.setValue( myConfig["Wrap"]["LineIndentWidth"] )
        """TODO
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
        """
        

    def saveSettings(self):
        # General
        """TODO
        setSaveSessionOnClose( self.cbSaveSession.isChecked() )
        setRestoreSessionOnStartup( self.cbRestoreSession.isChecked() )
        """
        config["Workspace"]["FileSortMode"] = cbSortingMode.itemData( self.cbSortingMode.currentIndex() ).toString()

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
            self.gbCalltipsEnabled.setChecked( myConfig["CallTips"]["Style"] != "None" )
        sCallTipsVisible.setValue( myConfig["CallTips"]["Visible"] )
        self.bgCallTipsStyle.button( myConfig["CallTips"]["Style"] ).setChecked( True )
        self.tbCalltipsBackground.setColor( QColor(myConfig["CallTips"]["BackgroundColor"]) )
        self.tbCalltipsForeground.setColor( QColor(myConfig["CallTips"]["ForegroundColor"]) )
        self.tbCalltipsHighlight.setColor( QColor(myConfig["CallTips"]["HighlightColor"]) )

        myConfig["CallTips"]["Style"] = _CALL_TIPS_STYLE[bgCallTipsStyle.checkedId()]
        setCallTipsVisible( sCallTipsVisible.value() )
        setCallTipsBackgroundColor( self.tbCalltipsBackground.color() )
        setCallTipsForegroundColor( self.tbCalltipsForeground.color() )
        setCallTipsHighlightColor( self.tbCalltipsHighlight.color() )
        #  Indentation
        setAutoIndent( self.cbAutoIndent.isChecked()  )
        setBackspaceUnindents( self.cbBackspaceUnindents.isChecked() )
        setIndentationGuides( self.cbIndentationGuides.isChecked() )
        setIndentationsUseTabs( self.cbIndentationUseTabs.isChecked() )
        setTabIndents( self.cbTabIndents.isChecked() )
        setAutoDetectIndent( self.cbAutodetectIndent.isChecked() )
        setTabWidth( sIndentationTabWidth.value() )
        setIndentationWidth( sIndentationWidth.value() )
        setIndentationGuidesBackgroundColor( self.tbIndentationGuidesBackground.color() )
        setIndentationGuidesForegroundColor( self.tbIndentationGuidesForeground.color() )
        #  Brace Matching
        setBraceMatching( QsciScintilla.NoBraceMatch )
        if  self.gbBraceMatchingEnabled.isChecked() :
            setBraceMatching( (QsciScintilla.BraceMatch)bgBraceMatch.checkedId() )
        setMatchedBraceBackgroundColor( self.tbMatchedBraceBackground.color() )
        setMatchedBraceForegroundColor( self.tbMatchedBraceForeground.color() )
        setUnmatchedBraceBackgroundColor( self.tbUnmatchedBraceBackground.color() )
        setUnmatchedBraceForegroundColor( self.tbUnmatchedBraceForeground.color() )
        #  Edge Mode
        setEdgeMode( QsciScintilla.EdgeNone )
        if  self.gbEdgeModeEnabled.isChecked() :
            setEdgeMode( (QsciScintilla.EdgeMode)bgEdgeMode.checkedId() )
        setEdgeColumn( sEdgeColumnNumber.value() )
        setEdgeColor( self.tbEdgeColor.color() )
        #  Caret
        setCaretLineVisible( self.gbCaretLineVisible.isChecked() )
        setCaretLineBackgroundColor( self.tbCaretLineBackground.color() )
        setCaretForegroundColor( self.tbCaretForeground.color() )
        setCaretWidth( sCaretWidth.value() )
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
        setEolMode( (QsciScintilla.EolMode)bgEolMode.checkedId() )
        setEolVisibility( self.cbEolVisibility.isChecked() )
        setAutoDetectEol( self.cbAutoDetectEol.isChecked() )
        setAutoEolConversion( self.cbAutoEolConversion.isChecked() )
        setWhitespaceVisibility( QsciScintilla.WsInvisible )
        if  self.gbWhitespaceVisibilityEnabled.isChecked() :
            setWhitespaceVisibility( (QsciScintilla.WhitespaceVisibility)bgWhitespaceVisibility.checkedId() )
        setWrapMode( QsciScintilla.WrapNone )
        if  self.gbWrapModeEnabled.isChecked() :
            setWrapMode( (QsciScintilla.WrapMode)bgWrapMode.checkedId() )
        setWrapVisualFlagsEnabled( self.gbWrapVisualFlagsEnabled.isChecked() )
        setStartWrapVisualFlag( QsciScintilla.WrapFlagNone )
        if  self.gbWrapVisualFlagsEnabled.isChecked() :
            setStartWrapVisualFlag( (QsciScintilla.WrapVisualFlag)bgStartWrapVisualFlag.checkedId() )
        setEndWrapVisualFlag( QsciScintilla.WrapFlagNone )
        if  self.gbWrapVisualFlagsEnabled.isChecked() :
            setEndWrapVisualFlag( (QsciScintilla.WrapVisualFlag)bgEndWrapVisualFlag.checkedId() )
        setWrappedLineIndentWidth( sWrappedLineIndentWidth.value() )
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
        it = self.twMenu.selectedItems().value( 0 )

        if  it :
            lInformations.setText( it.text( 0 ) )
            i = self.twMenu.indexOfTopLevelItem( it )
            if  not it.parent() :
                switch ( i )
                    case 0:
                    case 1:
                    case 2:
                        swPages.setCurrentIndex( i )
                        break
                    default:
                        swPages.setCurrentIndex( i +11 )
                        break


            else:
                swPages.setCurrentIndex( it.parent().indexOfChild( it ) +2 )



    def on_pbDefaultDocumentFont_clicked(self):
        font = lDefaultDocumentFont.font()
        bool ok
        
        font = QFontDialog.getFont( &ok, font, self, self.tr( "Choose the default document font" ), QFontDialog.DontUseNativeDialog )
        
        if  ok :
            lDefaultDocumentFont.setFont( font )
            lDefaultDocumentFont.setToolTip( font.toString() )



    def on_gbAutoCompletionEnabled_clicked(self, checked ):
        if  checked and self.bgAutoCompletionSource.checkedId() == -1 :
            mode = autoCompletionSource()
            
            if  mode == QsciScintilla.AcsNone :
                mode = QsciScintilla.AcsAll

            
            self.bgAutoCompletionSource.button( mode ).setChecked( True )



    def self.tbFonts_clicked(self):
        self.tb = qobject_cast<QToolButton*>( sender() )
        bool b
        f = QFontDialog.getFont( &b, self.tb.font(), window() )
        if  b :
            self.tb.setFont( f )


    def self.cbSourceAPIsLanguages_beforeChanged(self, i ):
        if  i == self.cbSourceAPIsLanguages.currentIndex() :
            QStringList l
            for ( j = 0; j < lwSourceAPIs.count(); j++ )
                l << lwSourceAPIs.item( j ).text()
            self.cbSourceAPIsLanguages.setItemData( i, l )



    def on_cbSourceAPIsLanguages_currentIndexChanged(self, i ):
        lwSourceAPIs.clear()
        lwSourceAPIs.addItems( self.cbSourceAPIsLanguages.itemData( i ).toStringList() )


    def on_pbSourceAPIsDelete_clicked(self):
        # get selected item
        it = lwSourceAPIs.selectedItems().value( 0 )
        if  it :
            delete it
            self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )



    def on_pbSourceAPIsAdd_clicked(self):
        # get files
        files = leSourceAPIs.text().split( ";", QString.SkipEmptyParts )
        # add them recursively
        for fn in files:
            if  lwSourceAPIs.findItems( fn, Qt.MatchFixedString ).count() == 0 :
                lwSourceAPIs.addItem( fn )
        # clear input
        leSourceAPIs.clear()
        # save datas
        self.cbSourceAPIsLanguages_beforeChanged( self.cbSourceAPIsLanguages.currentIndex() )


    def on_pbSourceAPIsBrowse_clicked(self):
        files = QFileDialog.getOpenFileNames( window(), self.tr( "Select API files" ), QString.null, self.tr( "API Files (*.api);;All Files (*)" ) )
        if  not files.isEmpty() :
            leSourceAPIs.setText( files.join( ";" ) )


    def on_twLexersAssociations_itemSelectionChanged(self):
        it = self.twLexersAssociations.selectedItems().value( 0 )
        if  it :
            leLexersAssociationsFilenamePattern.setText( it.text( 0 ) )
            self.cbLexersAssociationsLanguages.setCurrentIndex( self.cbLexersAssociationsLanguages.findText( it.text( 1 ) ) )



    def on_pbLexersAssociationsAddChange_clicked(self):
        f = leLexersAssociationsFilenamePattern.text()
        l = self.cbLexersAssociationsLanguages.currentText()
        if  f.isEmpty() or l.isEmpty() :
            return
        it = self.twLexersAssociations.selectedItems().value( 0 )
        if  not it or it.text( 0 ) != f :
            # check if item with same parameters already exists
            QList<QTreeWidgetItem*> l = self.twLexersAssociations.findItems( f, Qt.MatchFixedString )
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
        it = self.twLexersAssociations.selectedItems().value( 0 )
        if  it :
            delete it
            self.twLexersAssociations.setCurrentItem( 0 )
            self.twLexersAssociations.selectionModel().clear()
            leLexersAssociationsFilenamePattern.clear()
            self.cbLexersAssociationsLanguages.setCurrentIndex( -1 )



    def on_cbLexersHighlightingLanguages_currentIndexChanged(self, s ):
        l = mLexers.value( s )
        lwLexersHighlightingElements.clear()
        for ( i = 0; i < 128; i++ )
            n = l.description( i )
            if  not n.isEmpty() :
                it = QListWidgetItem( lwLexersHighlightingElements )
                it.setText( n )
                it.setForeground( l.color( i ) )
                it.setBackground( l.paper( i ) )
                it.setFont( l.font( i ) )
                it.setData( Qt.UserRole, i )


        # value
        QVariant v
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
        it = lwLexersHighlightingElements.selectedItems().value( 0 )
        if  it :
            self.cbLexersHighlightingFillEol.setChecked( mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).eolFill( it.data( Qt.UserRole ).toInt() ) )


    def lexersHighlightingColour_clicked(self):
        # get sender
        o = sender()
        # color
        QColor c
        # element colour
        if  o == self.pbLexersHighlightingForeground or o == self.pbLexersHighlightingBackground :
            # get item
            it = lwLexersHighlightingElements.selectedItems().value( 0 )
            # cancel if no item
            if  not it :
                return
            # get color
            c = QColorDialog.getColor( o == self.pbLexersHighlightingForeground ? it.foreground().color() : it.background().color(), window() )
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
            c = QColorDialog.getColor( o == self.pbLexersHighlightingAllForeground ? l.color( -1 ) : l.paper( -1 ), window() )
            # apply
            if  c.isValid() :
                if  o == self.pbLexersHighlightingAllForeground :
                    l.setColor( c, -1 )
                elif  o == self.pbLexersHighlightingAllBackground :
                    l.setPaper( c, -1 )
                # refresh
                on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )




    def lexersHighlightingFont_clicked(self):
        # get sender
        o = sender()
        # values
        bool b
        QFont f
        # element font
        if  o == self.pbLexersHighlightingFont :
            # get item
            it = lwLexersHighlightingElements.selectedItems().value( 0 )
            # cancel if no item
            if  not it :
                return
            # get font
            f = QFontDialog.getFont( &b, it.font(), window() )
            # apply
            if  b :
                it.setFont( f )
                mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).setFont( f, it.data( Qt.UserRole ).toInt() )


        # global font
        elif  o == self.pbLexersHighlightingAllFont :
            # get lexer
            l = mLexers.value( self.cbLexersHighlightingLanguages.currentText() )
            # get font
            f = QFontDialog.getFont( &b, l.font( -1 ), window() )
            # apply
            if  b :
                l.setFont( f, -1 )
                on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )




    def on_cbLexersHighlightingFillEol_clicked(self, b ):
        it = lwLexersHighlightingElements.selectedItems().value( 0 )
        if  it :
            mLexers.value( self.cbLexersHighlightingLanguages.currentText() ).setEolFill( b, it.data( Qt.UserRole ).toInt() )


    def self.cbLexersHighlightingProperties_clicked(self, b ):
        # get check box
        self.cb = qobject_cast<QCheckBox*>( sender() )
        if  not self.cb :
            return
        # get lexer
        l = mLexers.value( self.cbLexersHighlightingLanguages.currentText() )
        # set lexer properties
        if  self.cb == self.cbLexersHighlightingIndentOpeningBrace or self.cb == self.cbLexersHighlightingIndentClosingBrace :
            if  self.cbLexersHighlightingIndentOpeningBrace.isChecked() and self.cbLexersHighlightingIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening | QsciScintilla.AiClosing )
            elif  self.cbLexersHighlightingIndentOpeningBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening )
            elif  self.cbLexersHighlightingIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiClosing )
            else:
                l.setAutoIndentStyle( QsciScintilla.AiMaintain )

        else:
            setLexerProperty( self.cb.statusTip(), l, b )


    def on_cbLexersHighlightingIndentationWarning_currentIndexChanged(self, i ):
        # get lexer
        l = mLexers.value( self.cbLexersHighlightingLanguages.currentText() )
        # set lexer properties
        setLexerProperty( self.cbLexersHighlightingIndentationWarning.statusTip(), l, self.cbLexersHighlightingIndentationWarning.itemData( i ) )


    def on_pbLexersHighlightingReset_clicked(self):
        # get lexer
        l = mLexers.value( self.cbLexersHighlightingLanguages.currentText() )
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
        it = self.twAbbreviations.selectedItems().value( 0 )
        if  it :
            teAbbreviationsCode.setPlainText( it.data( 0, Qt.UserRole ).toString() )
        # enable/disable according to selection
        teAbbreviationsCode.setEnabled( it )


    def on_pbAbbreviationsAdd_clicked(self):
    { UIAddAbbreviation.edit( self.twAbbreviations );

    def on_pbAbbreviationsRemove_clicked(self):
        delete self.twAbbreviations.selectedItems().value( 0 )
        teAbbreviationsCode.clear()


    def on_teAbbreviationsCode_textChanged(self):
        # get item
        it = self.twAbbreviations.selectedItems().value( 0 )
        if  it :
            it.setData( 0, Qt.UserRole, teAbbreviationsCode.toPlainText() )


    def reject(self):
        settings = MonkeyCore.settings()
        
        for lexer in mLexers:        lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )

        
        QDialog.reject()


    def accept(self):
        apply()
        QDialog.accept()


    def apply(self):
        saveSettings()
        applyProperties()
        MonkeyCore.workspace().loadSettings()

