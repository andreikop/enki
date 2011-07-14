import os.path
from PyQt4 import uic
from PyQt4.QtCore import QObject, Qt, QVariant
from PyQt4.QtGui import QButtonGroup, \
                        QCheckBox, \
                        QColor, \
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
                                                    tr( "Settings.."), 
                                                    QIcon(':/mksicons/settings.png'))
        self._action.setStatusTip(tr( "Edit settigns.."))
        self._action.triggered.connect(self._onEditSettings)
        #self._onEditSettings()
    
    def __term__(self):
        core.actionModel().removeAction(self._action)

    def _onEditSettings(self):
        UISettings(core.mainWindow()).exec_()


class Option:
    def __init__(self, optionName, controlName):
        self.optionName = optionName
        self.controlName = controlName
    
    def setDialog(self, dialog):
        self.dialog = dialog
    
    def control(self):
        return self.dialog.__getattribute__(self.controlName)

class CheckableOption(Option):
    def load(self):
        self.control().setChecked(core.config().get(self.optionName))
    
    def save(self):
        core.config().set(self.optionName, self.control().isChecked())

class NumericOption(Option):
    def load(self):
        self.control().setValue(core.config().get(self.optionName))
    
    def save(self):
        core.config().set(self.optionName, self.control().value())

class ColorOption(Option):
    def load(self):
        self.control().setColor(QColor(core.config().get(self.optionName)))
    
    def save(self):
        core.config().set(self.optionName, self.control().color().name())

class FontOption(Option):
    def __init__(self, familyOptionName, sizeOptionName, editControl, buttonControl):
        self.familyOptionName = familyOptionName
        self.sizeOptionName = sizeOptionName
        self.editControlName = editControl
        self.buttonControlName = buttonControl
    
    def editControl(self):
        return self.dialog.__getattribute__(self.editControlName)
    
    def buttonControl(self):
        return self.dialog.__getattribute__(self.buttonControlName)
    
    def load(self):
        font = QFont(core.config().get(self.familyOptionName), core.config().get(self.sizeOptionName))
        self.editControl().setFont( font )
        self.editControl().setToolTip( font.toString() )
        self.buttonControl().clicked.connect(self.onClicked)
    
    def save(self):
        font = self.editControl().font()
        core.config().set(self.familyOptionName, font.family())
        core.config().set(self.sizeOptionName, font.pointSize())
    
    def onClicked(self):
        f, b = QFontDialog.getFont(self.editControl().font(), core.mainWindow() )
        if  b:
            self.editControl().setFont( f )


class ChoiseOption(Option):
    """Radio button group, QComboBox
    """
    def __init__(self, optionName, controlsList, textValuesList):
        Option.__init__(self, optionName, None)
        self.controlNameList = controlsList
        self.textValuesList = textValuesList
    
    def control(self, index):
        return self.dialog.__getattribute__(self.controlNameList[index])
    
    def load(self):
        value = core.config().get(self.optionName)
        buttonIndex = self.textValuesList.index(value)
        self.control(buttonIndex).setChecked(True)
    
    def save(self):
        for index in range(len(self.controlNameList)):
            if self.control(index).isChecked():
                core.config().set(self.optionName, self.textValuesList[index])

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
        self.initTopLevelItems()
        self.createOptions()
        self.loadSettings()

    def initTopLevelItems(self):
        """Generate list of all tree items. Used for switch pages
        """
        def allItems(twItem):
            """Item itself and all children (reqursive)
            """
            yield twItem
            for childIndex in range(twItem.childCount()):
                for item in allItems(twItem.child(childIndex)):
                    yield item

        topLevelItems = [self.twMenu.topLevelItem(index) for index in range(self.twMenu.topLevelItemCount())]
        self._allTwItems = []
        
        for topLevelItem in topLevelItems:
            self._allTwItems.extend(allItems(topLevelItem))
        
        # Expand all items
        for topLevelItem in topLevelItems:
            topLevelItem.setExpanded(True)


    def createOptions(self):
        self._opions = \
        (   ChoiseOption("Workspace/FileSortMode", ("rbOpeningOrder", "rbFileName", "rbUri", "rbSuffix"), self._SORT_MODE),
            CheckableOption("Editor/Indentation/ConvertUponOpen", "cbConvertIndentationUponOpen"),
            CheckableOption("Editor/CreateBackupUponOpen", "cbCreateBackupUponOpen"),
            ColorOption("Editor/SelectionBackgroundColor", "tbSelectionBackground"),
            ColorOption("Editor/SelectionForegroundColor", "tbSelectionForeground"),
            CheckableOption("Editor/DefaultDocumentColours", "gbDefaultDocumentColours"),
            ColorOption("Editor/DefaultDocumentPen", "tbDefaultDocumentPen"),
            ColorOption("Editor/DefaultDocumentPaper", "tbDefaultDocumentPaper"),
            FontOption("Editor/DefaultFont", "Editor/DefaultFontSize", "lDefaultDocumentFont", "pbDefaultDocumentFont"),
            
            CheckableOption("Editor/AutoCompletion/Enabled", "gbAutoCompletion"),
            ChoiseOption("Editor/AutoCompletion/Source",
                         ("rbDocument", "rbApi", "rbFromBoth"),
                         self._AUTOCOMPLETION_SOURCE),
            CheckableOption("Editor/AutoCompletion/CaseSensitivity", "cbAutoCompletionCaseSensitivity"),
            CheckableOption("Editor/AutoCompletion/ReplaceWord", "cbAutoCompletionReplaceWord"),
            CheckableOption("Editor/AutoCompletion/ShowSingle", "cbAutoCompletionShowSingle"),
            NumericOption("Editor/AutoCompletion/Threshold", "sAutoCompletionThreshold"),
            
            CheckableOption("Editor/CallTips/Enabled", "gbCalltips"),
            NumericOption("Editor/CallTips/VisibleCount", "sCallTipsVisible"),
            ChoiseOption("Editor/CallTips/Style",
                         ("rbCallTipsNoContext", "rbCallTipsContext", "rbCallTipsNoAutoCompletionContext"),
                         self._CALL_TIPS_STYLE),
            ColorOption("Editor/CallTips/BackgroundColor", "tbCalltipsBackground"),
            ColorOption("Editor/CallTips/ForegroundColor", "tbCalltipsForeground"),
            ColorOption("Editor/CallTips/HighlightColor", "tbCalltipsHighlight"),
            
            CheckableOption("Editor/Indentation/AutoIndent", "cbAutoIndent"),
            CheckableOption("Editor/Indentation/BackspaceUnindents", "cbBackspaceUnindents"),
            CheckableOption("Editor/Indentation/Guides", "gbIndentationGuides"),
            ChoiseOption("Editor/Indentation/UseTabs",
                         ("rbIndentationSpaces", "rbIndentationTabs"),
                         (False, True)),
            CheckableOption("Editor/Indentation/AutoDetect", "cbAutodetectIndent"),
            NumericOption("Editor/Indentation/Width", "sIndentationWidth"),
            ColorOption("Editor/Indentation/GuidesBackgroundColor", "tbIndentationGuidesBackground"),
            ColorOption("Editor/Indentation/GuidesForegroundColor", "tbIndentationGuidesForeground"),
            
            CheckableOption("Editor/BraceMatching/Enabled", "gbBraceMatchingEnabled"),
            ChoiseOption("Editor/BraceMatching/Mode",
                         ("rbStrictBraceMatch", "rbSloppyBraceMatch"),
                         self._BRACE_MATCHING),
            ColorOption("Editor/BraceMatching/MatchedForegroundColor", "tbMatchedBraceForeground"),
            ColorOption("Editor/BraceMatching/MatchedBackgroundColor", "tbMatchedBraceBackground"),
            ColorOption("Editor/BraceMatching/UnmatchedBackgroundColor", "tbUnmatchedBraceBackground"),
            ColorOption("Editor/BraceMatching/UnmatchedForegroundColor", "tbUnmatchedBraceForeground"),
            
            CheckableOption("Editor/Edge/Enabled", "gbEdgeModeEnabled"),
            ChoiseOption("Editor/Edge/Mode",
                         ("rbEdgeLine", "rbEdgeBackground"),
                         self._EDGE_MODE),
            NumericOption("Editor/Edge/Column", "sEdgeColumnNumber"),
            ColorOption("Editor/Edge/Color", "tbEdgeColor"),

            CheckableOption("Editor/Caret/LineVisible", "gbCaretLineVisible"),
            ColorOption("Editor/Caret/LineBackgroundColor", "tbCaretLineBackground"),
            ColorOption("Editor/Caret/ForegroundColor", "tbCaretForeground"),
            NumericOption("Editor/Caret/Width", "sCaretWidth"),

        )
        
        for option in self._opions:
            option.setDialog(self)

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
        for option in self._opions:
            option.load()

    def saveSettings(self):
        for option in self._opions:
            option.save()
        
        core.config().flush()

    def on_twMenu_itemSelectionChanged(self):
        # get item
        selectedItem = self.twMenu.selectedItems()[0]
        self.lInformations.setText( selectedItem.text( 0 ) )
        self.swPages.setCurrentIndex(self._allTwItems.index(selectedItem))
        
        """
----------------------------------------------------------- constructor
        
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

--------------------------------------------------------  loadSettings

        # General
        self.cbSaveSession.setChecked( saveSessionOnClose() )
        self.cbRestoreSession.setChecked( restoreSessionOnStartup() )

        #  General
        
        self.cbDefaultCodec.setCurrentIndex( self.cbDefaultCodec.findText( defaultCodec() ) )
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
        self.bgEolMode.button( "Editor/EOL/Mod").setChecked( True )
        CheckableOption("Editor/EOL/Visibility", "cbEolVisibility")
        CheckableOption("Editor/EOL/AutoDetect", "cbAutoDetectEol")
        CheckableOption("Editor/EOL/AutoConvert", "cbAutoEolConversion")
        self.gbWhitespaceVisibilityEnabled.setChecked( "Editor/WhitespaceVisibility"] != "Invisibl")
        self.bgWhitespaceVisibility.button( "Editor/WhitespaceVisibilit").setChecked( True )
        self.gbWrapModeEnabled.setChecked( "Editor/Wrap/Mode"] != 'None' )
        self.bgWrapMode.button( "Editor/Wrap/Mod").setChecked( True )
        #self.bgStartWrapVisualFlag.button( "Editor/Wrap/StartVisualFla").setChecked( True )
        #self.bgEndWrapVisualFlag.button( "Editor/Wrap/EndVisualFla").setChecked( True )
        NumericOption("Editor/Wrap/LineIndentWidth", "sWrappedLineIndentWidth")
        
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
        # TODO setDefaultCodec( self.cbDefaultCodec.currentText() )
        
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
        "Editor/EOL/Mode"] = _EOL_MODE[self.bgEolMode.checkedId()]
        "Editor/EOL/Visibility"] = self.cbEolVisibility.isChecked()
        "Editor/EOL/AutoDetect"] = self.cbAutoDetectEol.isChecked()
        "Editor/EOL/AutoConvert"] = self.cbAutoEolConversion.isChecked()
        "Editor/WhitespaceVisibility"] = _WHITESPACE_MODE[bgWhitespaceVisibility.checkedId()]
        "Editor/Wrap/Mode"] = _WRAP_MODE[bgWrapMode.checkedId()]
        "Editor/Wrap/StartVisualFlag"] = _WRAP_FLAG[bgStartWrapVisualFlag.checkedId()]
        "Editor/Wrap/EndVisualFlag"] = _WRAP_FLAG[bgEndWrapVisualFlag.checkedId()]
        "Editor/Wrap/LineIndentWidth"] = sWrappedLineIndentWidth.value()
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
            MonkeyCore.fileManager().setCommand( type, suffixes[ type )


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
        
    def on_pbDefaultDocumentFont_clicked(self):
        font = self.lDefaultDocumentFont.font()
        
        font, ok = QFontDialog.getFont( font, self, self.tr( "Choose the default document font" ), QFontDialog.DontUseNativeDialog )
        
        if ok:
            self.lDefaultDocumentFont.setFont( font )
            self.lDefaultDocumentFont.setToolTip( font.toString() )

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
        files = leSourceAPIs.text().split("")
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
        font = self.lDefaultDocumentFont.font()
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
