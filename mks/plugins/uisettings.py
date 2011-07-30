import os.path
from PyQt4 import uic
from PyQt4.QtCore import QObject, QStringList, Qt, QVariant
from PyQt4.QtGui import QButtonGroup, \
                        QCheckBox, \
                        QColor, \
                        QDialog, \
                        QDialogButtonBox, \
                        QFont, \
                        QFontDialog, \
                        QIcon, \
                        QListWidgetItem, \
                        QRadioButton, \
                        QTreeWidgetItem, \
                        QWidget


from PyQt4.Qsci import QsciScintilla

from mks.core.core import core, DATA_FILES_PATH
from mks.plugins.editor import Editor, _Lexer
import mks.plugins.editor  # FIXME for lexer settings. Remove it

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
    def __init__(self, dialog, config, optionName, control):
        self.config = config
        self.optionName = optionName
        self.control = control
        dialog.accepted.connect(self.save)
        self.load()

class CheckableOption(Option):
    def load(self):
        self.control.setChecked(self.config.get(self.optionName))
    
    def save(self):
        self.config.set(self.optionName, self.control.isChecked())

class NumericOption(Option):
    def load(self):
        self.control.setValue(self.config.get(self.optionName))
    
    def save(self):
        self.config.set(self.optionName, self.control.value())

class ColorOption(Option):
    def load(self):
        self.control.setColor(QColor(self.config.get(self.optionName)))
    
    def save(self):
        self.config.set(self.optionName, self.control.color().name())

class FontOption(Option):
    def __init__(self, dialog, config, familyOptionName, sizeOptionName, editControl, buttonControl):
        self.familyOptionName = familyOptionName
        self.sizeOptionName = sizeOptionName
        self.editControl = editControl
        self.buttonControl = buttonControl
        Option.__init__(self, dialog, config, None, None)
    
    def load(self):
        font = QFont(self.config.get(self.familyOptionName), self.config.get(self.sizeOptionName))
        self.editControl.setFont( font )
        self.editControl.setToolTip( font.toString() )
        self.buttonControl.clicked.connect(self.onClicked)
    
    def save(self):
        font = self.editControl.font()
        self.config.set(self.familyOptionName, font.family())
        self.config.set(self.sizeOptionName, font.pointSize())
    
    def onClicked(self):
        f, b = QFontDialog.getFont(self.editControl.font(), core.mainWindow() )
        if  b:
            self.editControl.setFont( f )


class ChoiseOption(Option):
    """Radio button group, QComboBox
    """
    def __init__(self, dialog, config, optionName, controlsList, textValuesList):
        self.controls = controlsList
        self.textValuesList = textValuesList
        Option.__init__(self, dialog, config, optionName, None)
        
    def load(self):
        value = self.config.get(self.optionName)
        buttonIndex = self.textValuesList.index(value)
        self.controls[buttonIndex].setChecked(True)
    
    def save(self):
        for index, control in enumerate(self.controls):
            if control.isChecked():
                self.config.set(self.optionName, self.textValuesList[index])


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
    _INDENT_WARNING = _Lexer._PYTHON_INDENTATION_WARNING_TO_QSCI.keys()
    _SORT_MODE = ["OpeningOrder", "FileName", "URL", "Suffixes"]
    
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self._createdObjects = []

        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UISettings.ui'), self)
        
        self.setAttribute( Qt.WA_DeleteOnClose )
        self.createOptions()
        self.accepted.connect(self.saveSettings)
        self.accepted.connect(self.applySettings)

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

    def createOptions(self):
        cfg = core.config()
        self._options = \
        [   ChoiseOption(self, cfg, "Workspace/FileSortMode",
                         (self.rbOpeningOrder, self.rbFileName, self.rbUri, self.rbSuffix),
                         self._SORT_MODE),
            CheckableOption(self, cfg, "Editor/Indentation/ConvertUponOpen", self.cbConvertIndentationUponOpen),
            CheckableOption(self, cfg, "Editor/CreateBackupUponOpen", self.cbCreateBackupUponOpen),
            ColorOption(self, cfg, "Editor/SelectionBackgroundColor", self.tbSelectionBackground),
            ColorOption(self, cfg, "Editor/SelectionForegroundColor", self.tbSelectionForeground),
            CheckableOption(self, cfg, "Editor/DefaultDocumentColours", self.gbDefaultDocumentColours),
            ColorOption(self, cfg, "Editor/DefaultDocumentPen", self.tbDefaultDocumentPen),
            ColorOption(self, cfg, "Editor/DefaultDocumentPaper", self.tbDefaultDocumentPaper),
            FontOption(self, cfg, "Editor/DefaultFont", "Editor/DefaultFontSize",
                        self.lDefaultDocumentFont, self.pbDefaultDocumentFont),
            
            CheckableOption(self, cfg, "Editor/AutoCompletion/Enabled", self.gbAutoCompletion),
            ChoiseOption(self, cfg, "Editor/AutoCompletion/Source",
                         (self.rbDocument, self.rbApi, self.rbFromBoth),
                          self._AUTOCOMPLETION_SOURCE),
            CheckableOption(self, cfg, "Editor/AutoCompletion/CaseSensitivity", self.cbAutoCompletionCaseSensitivity),
            CheckableOption(self, cfg, "Editor/AutoCompletion/ReplaceWord", self.cbAutoCompletionReplaceWord),
            CheckableOption(self, cfg, "Editor/AutoCompletion/ShowSingle", self.cbAutoCompletionShowSingle),
            NumericOption(self, cfg, "Editor/AutoCompletion/Threshold", self.sAutoCompletionThreshold),
            
            CheckableOption(self, cfg, "Editor/CallTips/Enabled", self.gbCalltips),
            NumericOption(self, cfg, "Editor/CallTips/VisibleCount", self.sCallTipsVisible),
            ChoiseOption(self, cfg, "Editor/CallTips/Style",
                         (self.rbCallTipsNoContext, self.rbCallTipsContext, self.rbCallTipsNoAutoCompletionContext),
                         self._CALL_TIPS_STYLE),
            ColorOption(self, cfg, "Editor/CallTips/BackgroundColor", self.tbCalltipsBackground),
            ColorOption(self, cfg, "Editor/CallTips/ForegroundColor", self.tbCalltipsForeground),
            ColorOption(self, cfg, "Editor/CallTips/HighlightColor", self.tbCalltipsHighlight),
            
            CheckableOption(self, cfg, "Editor/Indentation/AutoIndent", self.cbAutoIndent),
            CheckableOption(self, cfg, "Editor/Indentation/BackspaceUnindents", self.cbBackspaceUnindents),
            CheckableOption(self, cfg, "Editor/Indentation/Guides", self.gbIndentationGuides),
            ChoiseOption(self, cfg, "Editor/Indentation/UseTabs",
                         (self.rbIndentationSpaces, self.rbIndentationTabs),
                         (False, True)),
            CheckableOption(self, cfg, "Editor/Indentation/AutoDetect", self.cbAutodetectIndent),
            NumericOption(self, cfg, "Editor/Indentation/Width", self.sIndentationWidth),
            ColorOption(self, cfg, "Editor/Indentation/GuidesBackgroundColor", self.tbIndentationGuidesBackground),
            ColorOption(self, cfg, "Editor/Indentation/GuidesForegroundColor", self.tbIndentationGuidesForeground),
            
            CheckableOption(self, cfg, "Editor/BraceMatching/Enabled", self.gbBraceMatchingEnabled),
            ChoiseOption(self, cfg, "Editor/BraceMatching/Mode",
                         (self.rbStrictBraceMatch, self.rbSloppyBraceMatch),
                         self._BRACE_MATCHING),
            ColorOption(self, cfg, "Editor/BraceMatching/MatchedForegroundColor", self.tbMatchedBraceForeground),
            ColorOption(self, cfg, "Editor/BraceMatching/MatchedBackgroundColor", self.tbMatchedBraceBackground),
            ColorOption(self, cfg, "Editor/BraceMatching/UnmatchedBackgroundColor", self.tbUnmatchedBraceBackground),
            ColorOption(self, cfg, "Editor/BraceMatching/UnmatchedForegroundColor", self.tbUnmatchedBraceForeground),
            
            CheckableOption(self, cfg, "Editor/Edge/Enabled", self.gbEdgeModeEnabled),
            ChoiseOption(self, cfg, "Editor/Edge/Mode", (self.rbEdgeLine, self.rbEdgeBackground), self._EDGE_MODE),
            NumericOption(self, cfg, "Editor/Edge/Column", self.sEdgeColumnNumber),
            ColorOption(self, cfg, "Editor/Edge/Color", self.tbEdgeColor),

            CheckableOption(self, cfg, "Editor/Caret/LineVisible", self.gbCaretLineVisible),
            ColorOption(self, cfg, "Editor/Caret/LineBackgroundColor", self.tbCaretLineBackground),
            ColorOption(self, cfg, "Editor/Caret/ForegroundColor", self.tbCaretForeground),
            NumericOption(self, cfg, "Editor/Caret/Width", self.sCaretWidth),

            ChoiseOption(self, cfg, "Editor/EOL/Mode", (self.rbEolUnix, self.rbEolWindows, self.rbEolMac), self._EOL_MODE),
            CheckableOption(self, cfg, "Editor/EOL/Visibility", self.cbEolVisibility),
            CheckableOption(self, cfg, "Editor/EOL/AutoDetect", self.cbAutoDetectEol),
            CheckableOption(self, cfg, "Editor/EOL/AutoConvert", self.cbAutoEolConversion),
            ChoiseOption(self, cfg, "Editor/WhitespaceVisibility",
                            (self.rbWsInvisible, self.rbWsVisible, self.rbWsVisibleAfterIndent), self._WHITE_MODE),
            
            CheckableOption(self, cfg, "Editor/Wrap/Enabled", self.gbWrapModeEnabled),
            ChoiseOption(self, cfg, "Editor/Wrap/Mode", (self.rbWrapCharacter, self.rbWrapWord), self._WRAP_MODE),
            ChoiseOption(self, cfg, "Editor/Wrap/StartVisualFlag",
                         (self.rbStartWrapFlagNone, self.rbStartWrapFlagByText, self.rbStartWrapFlagByBorder),
                         self._WRAP_FLAG),
            ChoiseOption(self, cfg, "Editor/Wrap/EndVisualFlag",
                         (self.rbEndWrapFlagNone, self.rbEndWrapFlagByText, self.rbEndWrapFlagByBorder),
                         self._WRAP_FLAG),
            NumericOption(self, cfg, "Editor/Wrap/LineIndentWidth", self.sWrappedLineIndentWidth)
        ]
        
        lexerCfg = mks.plugins.editor.Plugin.instance.lexerConfig._config  # FIXME
        lexerItem = self.twMenu.findItems("Language", Qt.MatchExactly | Qt.MatchRecursive)[0]
        if core.workspace().currentDocument() is not None and \
           core.workspace().currentDocument()._lexer._currentLanguage is not None:
            language = core.workspace().currentDocument()._lexer._currentLanguage  # FIXME
            lexerItem.setText(0, language)
            lexer = core.workspace().currentDocument().qscintilla.lexer()
            beginning = "%s/" % language
            
            if hasattr(lexer, "foldComments"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldComments", self.cbLexerFoldComments))
            else:
                self.cbLexerFoldComments.hide()
            
            if hasattr(lexer, "foldCompact"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldCompact", self.cbLexerFoldCompact))
            else:
                self.cbLexerFoldCompact.hide()
            
            if hasattr(lexer, "foldQuotes"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldQuotes", self.cbLexerFoldQuotes))
            else:
                self.cbLexerFoldQuotes.hide()
            
            if hasattr(lexer, "foldDirectives"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldDirectives", self.cbLexerFoldDirectives))
            else:
                self.cbLexerFoldDirectives.hide()
            
            if hasattr(lexer, "foldAtBegin"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldAtBegin", self.cbLexerFoldAtBegin))
            else:
                self.cbLexerFoldAtBegin.hide()
            
            if hasattr(lexer, "foldAtParenthesis"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldAtParenthesis", self.cbLexerFoldAtParenthesis))
            else:
                self.cbLexerFoldAtParenthesis.hide()
            
            if hasattr(lexer, "foldAtElse"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldAtElse", self.cbLexerFoldAtElse))
            else:
                self.cbLexerFoldAtElse.hide()
            
            if hasattr(lexer, "foldAtModule"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldAtModule", self.cbLexerFoldAtModule))
            else:
                self.cbLexerFoldAtModule.hide()
            
            if hasattr(lexer, "foldPreprocessor"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "foldPreprocessor", self.cbLexerFoldPreprocessor))
            else:
                self.cbLexerFoldPreprocessor.hide()
            
            if hasattr(lexer, "stylePreprocessor"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "stylePreprocessor", self.cbLexerStylePreprocessor))
            else:
                self.cbLexerStylePreprocessor.hide()
            
            self._options.append(CheckableOption(self, lexerCfg, beginning + "indentOpeningBrace", self.cbLexerIndentOpeningBrace))
            self._options.append(CheckableOption(self, lexerCfg, beginning + "indentClosingBrace", self.cbLexerIndentClosingBrace))
            
            if hasattr(lexer, "caseSensitiveTags"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "caseSensetiveTags", self.cbLexerCaseSensitiveTags))
            else:
                self.cbLexerCaseSensitiveTags.hide()
            
            if hasattr(lexer, "backslashEscapes"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "backslashEscapes", self.cbLexerBackslashEscapes))
            else:
                self.cbLexerBackslashEscapes.hide()
            
            if hasattr(lexer, "indentationWarning"):
                self._options.append(CheckableOption(self, lexerCfg, beginning + "indentationWarning", self.gbLexerHighlightingIndentationWarning))
                self._options.append(ChoiseOption(self, lexerCfg, beginning + "indentationWarningReason", 
                    (self.cbIndentationWarningInconsistent, self.cbIndentationWarningTabsAfterSpaces, self.cbIndentationWarningTabs, self.cbIndentationWarningSpaces),
                    self._INDENT_WARNING))
            else:
                self.gbLexerHighlightingIndentationWarning.hide()
        else:
            lexerItem.setDisabled(True)

        # Expand all items
        self.initTopLevelItems()
        for topLevelItem in self._allTwItems:  # except Languages
            topLevelItem.setExpanded(True)
        
        # resize to minimum size
        self.resize( self.minimumSizeHint() )

    def reject(self):
        """ TODO
        settings = MonkeyCore.settings()        
        for lexer in mLexers:
            lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )
        """
        QDialog.reject(self)

    def applySettings(self):
        core.workspace()._openedFileExplorer.mModel.setSortMode(core.config()["Workspace"]["FileSortMode"])
        for document in core.workspace().openedDocuments():
            document.applySettings()
            document._lexer._applySettings()

    def saveSettings(self):
        core.config().flush()
        mks.plugins.editor.Plugin.instance.lexerConfig._config.flush()

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

        # fill lexers combo
        self.cbSourceAPIsLanguages.addItems( availableLanguages() )
        self.cbLexersAssociationsLanguages.addItems( availableLanguages() )
        self.cbLexerLanguages.addItems( availableLanguages() )

        # resize column
        self.twLexersAssociations.setColumnWidth( 0, 200 )

        # resize column
        self.twAbbreviations.setColumnWidth( 0, 100 )
        self.twAbbreviations.setColumnWidth( 1, 180 )

        # connections
        # event filter
        # lexer elements highlighting
        self.pbLexersHighlightingForeground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingBackground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingFont.clicked.connect(self.lexersHighlightingFont_clicked)
        self.pbLexersHighlightingAllForeground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingAllBackground.clicked.connect(self.lexersHighlightingColour_clicked)
        self.pbLexersHighlightingAllFont.clicked.connect(self.lexersHighlightingFont_clicked)
        for cb in self.gbLexersHighlightingElements.findChildren(QCheckBox):
            if  self.cb != self.cbLexerFillEol :
                self.cb.clicked.connect(self.cbLexerProperties_clicked)

        for widget in  self.findChildren(QWidget):
            widget.setAttribute( Qt.WA_MacSmallSize, True )
            widget.setAttribute( Qt.WA_MacShowFocusRect, False )

--------------------------------------------------------  loadSettings

        # General
        self.cbSaveSession.setChecked( saveSessionOnClose() )
        self.cbRestoreSession.setChecked( restoreSessionOnStartup() )

        #  General
        
        self.cbDefaultCodec.setCurrentIndex( self.cbDefaultCodec.findText( defaultCodec() ) )

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

        if  self.cbLexerLanguages.count() :
            on_cbLexerLanguages_currentIndexChanged( self.cbLexerLanguages.itemText( 0 ) )

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

    def on_cbLexerLanguages_currentIndexChanged(self, s ):
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
        self.cbLexerFoldComments.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldComments.setChecked( v.toBool() )
        # fold compact
        v = lexerProperty( "foldCompact", l )
        self.cbLexerFoldCompact.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldCompact.setChecked( v.toBool() )
        # fold quotes
        v = lexerProperty( "foldQuotes", l )
        self.cbLexerFoldQuotes.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldQuotes.setChecked( v.toBool() )
        # fold directives
        v = lexerProperty( "foldDirectives", l )
        self.cbLexerFoldDirectives.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldDirectives.setChecked( v.toBool() )
        # fold at begin
        v = lexerProperty( "foldAtBegin", l )
        self.cbLexerFoldAtBegin.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldAtBegin.setChecked( v.toBool() )
        # fold at parenthesis
        v = lexerProperty( "foldAtParenthesis", l )
        self.cbLexerFoldAtParenthesis.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldAtParenthesis.setChecked( v.toBool() )
        # fold at else:
        v = lexerProperty( "foldAtElse", l )
        self.cbLexerFoldAtElse.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldAtElse.setChecked( v.toBool() )
        # fold at module
        v = lexerProperty( "foldAtModule", l )
        self.cbLexerFoldAtModule.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldAtModule.setChecked( v.toBool() )
        # fold preprocessor
        v = lexerProperty( "foldPreprocessor", l )
        self.cbLexerFoldPreprocessor.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerFoldPreprocessor.setChecked( v.toBool() )
        # style preprocessor
        v = lexerProperty( "stylePreprocessor", l )
        self.cbLexerStylePreprocessor.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerStylePreprocessor.setChecked( v.toBool() )
        # indent opening brace
        self.cbLexerIndentOpeningBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiOpening )
        # indent closing brace
        self.cbLexerIndentClosingBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiClosing )
        # case sensitive tags
        v = lexerProperty( "caseSensitiveTags", l )
        self.cbLexerCaseSensitiveTags.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerCaseSensitiveTags.setChecked( v.toBool() )
        # backslash escapes
        v = lexerProperty( "backslashEscapes", l )
        self.cbLexerBackslashEscapes.setVisible( v.isValid() )
        if  v.isValid() :
            self.cbLexerBackslashEscapes.setChecked( v.toBool() )
        # indentation warning
        v = lexerProperty( "indentationWarning", l )
        lLexersHighlightingIndentationWarning.setVisible( v.isValid() )
        self.cbLexerIndentationWarning.setVisible( lLexersHighlightingIndentationWarning.isVisible() )
        if  v.isValid() :
            self.cbLexerIndentationWarning.setCurrentIndex( self.cbLexerIndentationWarning.findData( v.toInt() ) )


    def on_lwLexersHighlightingElements_itemSelectionChanged(self):
        it = lwLexersHighlightingElements.selectedItems()[0]
        if  it :
            self.cbLexerFillEol.setChecked( mLexers.value[self.cbLexerLanguages.currentText()].eolFill( it.data( Qt.UserRole ).toInt() ) )

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
                    mLexers.value( self.cbLexerLanguages.currentText() ).setColor( c, it.data( Qt.UserRole ).toInt() )
                elif  o == self.pbLexersHighlightingBackground :
                    it.setBackground( c )
                    mLexers.value( self.cbLexerLanguages.currentText() ).setPaper( c, it.data( Qt.UserRole ).toInt() )
        # gobal color
        elif  o == self.pbLexersHighlightingAllForeground or o == self.pbLexersHighlightingAllBackground :
            # get lexer
            l = mLexers.value( self.cbLexerLanguages.currentText() )
            # get color
            c = QColorDialog.getColor( o == self.pbLexersHighlightingAllForeground ? l.color( -1 ) : l.paper( -1 ), self.window() )
            # apply
            if  c.isValid() :
                if  o == self.pbLexersHighlightingAllForeground :
                    l.setColor( c, -1 )
                elif  o == self.pbLexersHighlightingAllBackground :
                    l.setPaper( c, -1 )
                # refresh
                on_cbLexerLanguages_currentIndexChanged( l.language() )

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
                mLexers.value( self.cbLexerLanguages.currentText() ).setFont( f, it.data( Qt.UserRole ).toInt() )
        # global font
        elif  o == self.pbLexersHighlightingAllFont :
            # get lexer
            l = mLexers[self.cbLexerLanguages.currentText()]
            # get font
            f, b = QFontDialog.getFont(l.font( -1 ), self.window() )
            # apply
            if  b :
                l.setFont( f, -1 )
                on_cbLexerLanguages_currentIndexChanged( l.language() )

    def on_cbLexerFillEol_clicked(self, b ):
        it = lwLexersHighlightingElements.selectedItems()[0]
        if  it :
            mLexers[self.cbLexerLanguages.currentText()].setEolFill( b, it.data( Qt.UserRole ).toInt() )

    def on_cbLexerProperties_clicked(self, b ):
        # get check box
        checkBox = self.sender()
        # get lexer
        l = mLexers[self.cbLexerLanguages.currentText()]
        # set lexer properties
        if  checkBox == self.cbLexerIndentOpeningBrace or checkBox == self.cbLexerIndentClosingBrace :
            if  self.cbLexerIndentOpeningBrace.isChecked() and self.cbLexerIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening | QsciScintilla.AiClosing )
            elif  self.cbLexerIndentOpeningBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiOpening )
            elif  self.cbLexerIndentClosingBrace.isChecked() :
                l.setAutoIndentStyle( QsciScintilla.AiClosing )
            else:
                l.setAutoIndentStyle( QsciScintilla.AiMaintain )
        else:
            setLexerProperty( checkBox.statusTip(), l, b )

    def on_cbLexerIndentationWarning_currentIndexChanged(self, i ):
        # get lexer
        l = mLexers[self.cbLexerLanguages.currentText()]
        # set lexer properties
        setLexerProperty( self.cbLexerIndentationWarning.statusTip(), l, self.cbLexerIndentationWarning.itemData( i ) )

    def on_pbLexersHighlightingReset_clicked(self):
        # get lexer
        l = mLexers[self.cbLexerLanguages.currentText()]
        # reset and refresh
        if  l :
            resetLexer( l )
            on_cbLexerLanguages_currentIndexChanged( l.language() )

    def on_pbLexersApplyDefaultFont_clicked(self):
        settings = MonkeyCore.settings()
        font = self.lDefaultDocumentFont.font()
        language = self.cbLexerLanguages.currentText()
        
        settings.setDefaultLexerProperties( font, False )
        on_cbLexerLanguages_currentIndexChanged( language )

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
"""
