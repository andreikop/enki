'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UISettings.cpp
** Date      : 2008-01-14T00:36:54
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
**
    Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "UISettings.h"
#include "abbreviationsmanager/ui/UIAddAbbreviation.h"
#include "workspace/pFileManager.h"
#include "templatesmanager/pTemplatesManager.h"
#include "abbreviationsmanager/pAbbreviationsManager.h"
#include "pMonkeyStudio.h"
#include "workspace/pWorkspace.h"
#include "coremanager/MonkeyCore.h"
#include "settingsmanager/Settings.h"
#include "consolemanager/pConsoleManager.h"
#include "consolemanager/EnvironmentVariablesManager.h"

#include <qscilexerpython.h>

#include <QButtonGroup>
#include <QFileDialog>
#include <QColorDialog>
#include <QFontDialog>
#include <QTextCodec>
#include <QDir>

using namespace pMonkeyStudio

 SettingsPath = "Settings"

UISettings.UISettings( QWidget* p )
        : QDialog( p )
    setupUi( self )

#ifdef Q_WS_MAC
    layout().setMargin( 9 )
    layout().setSpacing( 9 )
#endif

    setAttribute( Qt.WA_DeleteOnClose )
    twMenu.topLevelItem( 2 ).setExpanded( True )
    twMenu.setCurrentItem( twMenu.topLevelItem( 0 ) )

    foreach ( pColorButton* b, findChildren<pColorButton*>() )
        b.setColorNameHidden( True )
#ifdef Q_WS_MAC
        b.setIconSize( QSize( 32, 12 ) )
#else:
        b.setIconSize( QSize( 32, 16 ) )
#endif


    QStringList l

    for s in availableLanguages():
    mLexers[s] = lexerForLanguage( s )

    # sorting mode
    cbSortingMode.addItem( tr( "Opening order" ), pOpenedFileModel.OpeningOrder )
    cbSortingMode.addItem( tr( "File name" ), pOpenedFileModel.FileName )
    cbSortingMode.addItem( tr( "Url" ), pOpenedFileModel.URL )
    cbSortingMode.addItem( tr( "Suffixes" ), pOpenedFileModel.Suffixes )
    cbSortingMode.addItem( tr( "Custom" ), pOpenedFileModel.Custom )

    # tab mode
    cbTabModes.addItem( tr( "No Tabs" ), pWorkspace.NoTabs )
    cbTabModes.addItem( tr( "Tabs at Top" ), pWorkspace.TopTabs )
    cbTabModes.addItem( tr( "Tabs at Bottom" ), pWorkspace.BottomTabs )
    cbTabModes.addItem( tr( "Tabs at Left" ), pWorkspace.LeftTabs )
    cbTabModes.addItem( tr( "Tabs at Right" ), pWorkspace.RightTabs )

    # loads text codecs
    cbDefaultCodec.addItems( availableTextCodecs() )

    # auto completion source
    bgAutoCompletionSource = QButtonGroup( gbAutoCompletionSource )
    bgAutoCompletionSource.addButton( rbAcsDocument, QsciScintilla.AcsDocument )
    bgAutoCompletionSource.addButton( rbAcsAPIs, QsciScintilla.AcsAPIs )
    bgAutoCompletionSource.addButton( rbAcsAll, QsciScintilla.AcsAll )

    # calltips style
    bgCallTipsStyle = QButtonGroup( gbCalltipsEnabled )
    bgCallTipsStyle.addButton( rbCallTipsNoContext, QsciScintilla.CallTipsNoContext )
    bgCallTipsStyle.addButton( rbCallTipsNoAutoCompletionContext, QsciScintilla.CallTipsNoAutoCompletionContext )
    bgCallTipsStyle.addButton( rbCallTipsContext, QsciScintilla.CallTipsContext )

    # brace match
    bgBraceMatch = QButtonGroup( gbBraceMatchingEnabled )
    bgBraceMatch.addButton( rbStrictBraceMatch, QsciScintilla.StrictBraceMatch )
    bgBraceMatch.addButton( rbSloppyBraceMatch, QsciScintilla.SloppyBraceMatch )

    # edge mode
    bgEdgeMode = QButtonGroup( gbEdgeModeEnabled )
    bgEdgeMode.addButton( rbEdgeLine, QsciScintilla.EdgeLine )
    bgEdgeMode.addButton( rbEdgeBackground, QsciScintilla.EdgeBackground )

    # fold style
    bgFoldStyle = QButtonGroup( gbFoldMarginEnabled )
    bgFoldStyle.addButton( rbPlainFoldStyle, QsciScintilla.PlainFoldStyle )
    bgFoldStyle.addButton( rbCircledTreeFoldStyle, QsciScintilla.CircledTreeFoldStyle )
    bgFoldStyle.addButton( rbCircledFoldStyle, QsciScintilla.CircledFoldStyle )
    bgFoldStyle.addButton( rbBoxedFoldStyle, QsciScintilla.BoxedFoldStyle )
    bgFoldStyle.addButton( rbBoxedTreeFoldStyle, QsciScintilla.BoxedTreeFoldStyle )

    # eol mode
    bgEolMode = QButtonGroup( gbEolMode )
    bgEolMode.addButton( rbEolUnix, QsciScintilla.EolUnix )
    bgEolMode.addButton( rbEolMac, QsciScintilla.EolMac )
    bgEolMode.addButton( rbEolWindows, QsciScintilla.EolWindows )

    # whitespace visibility
    bgWhitespaceVisibility = QButtonGroup( gbWhitespaceVisibilityEnabled )
    bgWhitespaceVisibility.addButton( rbWsVisible, QsciScintilla.WsVisible )
    bgWhitespaceVisibility.addButton( rbWsVisibleAfterIndent, QsciScintilla.WsVisibleAfterIndent )

    # wrap mode
    bgWrapMode = QButtonGroup( gbWrapModeEnabled )
    bgWrapMode.addButton( rbWrapWord, QsciScintilla.WrapWord )
    bgWrapMode.addButton( rbWrapCharacter, QsciScintilla.WrapCharacter )

    # wrap visual flag
    bgStartWrapVisualFlag = QButtonGroup( wStartWrapVisualFlags )
    bgStartWrapVisualFlag.addButton( rbStartWrapFlagByText, QsciScintilla.WrapFlagByText )
    bgStartWrapVisualFlag.addButton( rbStartWrapFlagByBorder, QsciScintilla.WrapFlagByBorder )
    bgEndWrapVisualFlag = QButtonGroup( wEndWrapVisualFlags )
    bgEndWrapVisualFlag.addButton( rbEndWrapFlagByText, QsciScintilla.WrapFlagByText )
    bgEndWrapVisualFlag.addButton( rbEndWrapFlagByBorder, QsciScintilla.WrapFlagByBorder )

    # fill lexers combo
    cbSourceAPIsLanguages.addItems( availableLanguages() )
    cbLexersAssociationsLanguages.addItems( availableLanguages() )
    cbLexersHighlightingLanguages.addItems( availableLanguages() )

    # resize column
    twLexersAssociations.setColumnWidth( 0, 200 )

    # python indentation warning
    cbLexersHighlightingIndentationWarning.addItem( tr( "No warning" ), QsciLexerPython.NoWarning )
    cbLexersHighlightingIndentationWarning.addItem( tr( "Inconsistent" ), QsciLexerPython.Inconsistent )
    cbLexersHighlightingIndentationWarning.addItem( tr( "Tabs after spaces" ), QsciLexerPython.TabsAfterSpaces )
    cbLexersHighlightingIndentationWarning.addItem( tr( "Spaces" ), QsciLexerPython.Spaces )
    cbLexersHighlightingIndentationWarning.addItem( tr( "Tabs" ), QsciLexerPython.Tabs )

    # resize column
    twAbbreviations.setColumnWidth( 0, 100 )
    twAbbreviations.setColumnWidth( 1, 180 )

    # read settings
    loadSettings()

    # connections
    # event filter
    # margin font
    tbMarginsFont.clicked.connect(self.tbFonts_clicked)
    # lexer elements highlighting
    pbLexersHighlightingForeground.clicked.connect(self.lexersHighlightingColour_clicked)
    pbLexersHighlightingBackground.clicked.connect(self.lexersHighlightingColour_clicked)
    pbLexersHighlightingFont.clicked.connect(self.lexersHighlightingFont_clicked)
    pbLexersHighlightingAllForeground.clicked.connect(self.lexersHighlightingColour_clicked)
    pbLexersHighlightingAllBackground.clicked.connect(self.lexersHighlightingColour_clicked)
    pbLexersHighlightingAllFont.clicked.connect(self.lexersHighlightingFont_clicked)
    foreach ( QCheckBox* cb, gbLexersHighlightingElements.findChildren<QCheckBox*>() )
    if  cb != cbLexersHighlightingFillEol :
        cb.clicked.connect(self.cbLexersHighlightingProperties_clicked)
    # apply button
    connect( dbbButtons.button( QDialogButtonBox.Apply ), SIGNAL( clicked() ), self, SLOT( apply() ) )

    foreach ( QWidget* widget, findChildren<QWidget*>() )
        widget.setAttribute( Qt.WA_MacSmallSize, True )
        widget.setAttribute( Qt.WA_MacShowFocusRect, False )


    # resize to minimum size
    resize( minimumSizeHint() )


def loadSettings(self):
    s = MonkeyCore.settings()
    QString sp

    # General
    cbSaveFiles.setChecked( saveFilesOnCustomAction() )
    cbTabModes.setCurrentIndex( cbTabModes.findData( documentMode() ) )
    cbSaveSession.setChecked( saveSessionOnClose() )
    cbRestoreSession.setChecked( restoreSessionOnStartup() )
    cbQuickFileAccess.setChecked( showQuickFileAccess() )
    cbSortingMode.setCurrentIndex( cbSortingMode.findData( openedFileSortingMode() ) )

    # Paths
    pleTemplatesPaths.setValues( s.storagePaths( Settings.SP_TEMPLATES ) )
    pleTranslationsPaths.setValues( s.storagePaths( Settings.SP_TRANSLATIONS ) )
    plePluginsPaths.setValues( s.storagePaths( Settings.SP_PLUGINS ) )

    # Editor
    #  General
    cbAutoSyntaxCheck.setChecked( autoSyntaxCheck() )
    cbConvertTabsUponOpen.setChecked( convertTabsUponOpen() )
    cbCreateBackupUponOpen.setChecked( createBackupUponOpen() )
    cbDefaultCodec.setCurrentIndex( cbDefaultCodec.findText( defaultCodec() ) )
    tbSelectionBackground.setColor( selectionBackgroundColor() )
    tbSelectionForeground.setColor( selectionForegroundColor() )
    gbDefaultDocumentColours.setChecked( defaultDocumentColours() )
    tbDefaultDocumentPen.setColor( defaultDocumentPen() )
    tbDefaultDocumentPaper.setColor( defaultDocumentPaper() )
    lDefaultDocumentFont.setFont( defaultDocumentFont() )
    lDefaultDocumentFont.setToolTip( defaultDocumentFont().toString() )
    #  Auto Completion
    gbAutoCompletionEnabled.setChecked( autoCompletionSource() != QsciScintilla.AcsNone )
    cbAutoCompletionCaseSensitivity.setChecked( autoCompletionCaseSensitivity() )
    cbAutoCompletionReplaceWord.setChecked( autoCompletionReplaceWord() )
    cbAutoCompletionShowSingle.setChecked( autoCompletionShowSingle() )
    sAutoCompletionThreshold.setValue( autoCompletionThreshold() )
    if  bgAutoCompletionSource.button( autoCompletionSource() ) :
        bgAutoCompletionSource.button( autoCompletionSource() ).setChecked( True )
    #  Call Tips
    gbCalltipsEnabled.setChecked( callTipsStyle() != QsciScintilla.CallTipsNone )
    sCallTipsVisible.setValue( callTipsVisible() )
    if  bgCallTipsStyle.button( callTipsStyle() ) :
        bgCallTipsStyle.button( callTipsStyle() ).setChecked( True )
    tbCalltipsBackground.setColor( callTipsBackgroundColor() )
    tbCalltipsForeground.setColor( callTipsForegroundColor() )
    tbCalltipsHighlight.setColor( callTipsHighlightColor() )
    #  Indentation
    cbAutoIndent.setChecked( autoIndent() )
    cbBackspaceUnindents.setChecked( backspaceUnindents() )
    cbIndentationGuides.setChecked( indentationGuides() )
    cbIndentationUseTabs.setChecked( indentationsUseTabs() )
    cbAutodetectIndent.setChecked( autoDetectIndent() )
    cbTabIndents.setChecked( tabIndents() )
    sIndentationTabWidth.setValue( tabWidth() )
    sIndentationWidth.setValue( indentationWidth() )
    tbIndentationGuidesBackground.setColor( indentationGuidesBackgroundColor() )
    tbIndentationGuidesForeground.setColor( indentationGuidesForegroundColor() )
    #  Brace Matching
    gbBraceMatchingEnabled.setChecked( braceMatching() != QsciScintilla.NoBraceMatch )
    if  bgBraceMatch.button( braceMatching() ) :
        bgBraceMatch.button( braceMatching() ).setChecked( True )
    tbMatchedBraceForeground.setColor( matchedBraceForegroundColor() )
    tbMatchedBraceBackground.setColor( matchedBraceBackgroundColor() )
    tbUnmatchedBraceBackground.setColor( unmatchedBraceBackgroundColor() )
    tbUnmatchedBraceForeground.setColor( unmatchedBraceForegroundColor() )
    #  Edge Mode
    gbEdgeModeEnabled.setChecked( edgeMode() != QsciScintilla.EdgeNone )
    if  bgEdgeMode.button( edgeMode() ) :
        bgEdgeMode.button( edgeMode() ).setChecked( True )
    sEdgeColumnNumber.setValue( edgeColumn() )
    tbEdgeColor.setColor( edgeColor() )
    #  Caret
    gbCaretLineVisible.setChecked( caretLineVisible() )
    tbCaretLineBackground.setColor( caretLineBackgroundColor() )
    tbCaretForeground.setColor( caretForegroundColor() )
    sCaretWidth.setValue( caretWidth() )
    #  Margins
    gbLineNumbersMarginEnabled.setChecked( lineNumbersMarginEnabled() )
    sLineNumbersMarginWidth.setValue( lineNumbersMarginWidth() )
    cbLineNumbersMarginAutoWidth.setChecked( lineNumbersMarginAutoWidth() )
    gbFoldMarginEnabled.setChecked( folding() != QsciScintilla.NoFoldStyle )
    if  bgFoldStyle.button( folding() ) :
        bgFoldStyle.button( folding() ).setChecked( True )
    tbFoldMarginForeground.setColor( foldMarginForegroundColor() )
    tbFoldMarginBackground.setColor( foldMarginBackgroundColor() )
    gbMarginsEnabled.setChecked( marginsEnabled() )
    tbMarginsForeground.setColor( marginsForegroundColor() )
    tbMarginsBackground.setColor( marginsBackgroundColor() )
    tbMarginsFont.setFont( marginsFont() )
    #  Special Characters
    bgEolMode.button( eolMode() ).setChecked( True )
    cbEolVisibility.setChecked( eolVisibility() )
    cbAutoDetectEol.setChecked( autoDetectEol() )
    cbAutoEolConversion.setChecked( autoEolConversion() )
    gbWhitespaceVisibilityEnabled.setChecked( whitespaceVisibility() != QsciScintilla.WsInvisible )
    if  bgWhitespaceVisibility.button( whitespaceVisibility() ) :
        bgWhitespaceVisibility.button( whitespaceVisibility() ).setChecked( True )
    gbWrapModeEnabled.setChecked( wrapMode() != QsciScintilla.WrapNone )
    if  bgWrapMode.button( wrapMode() ) :
        bgWrapMode.button( wrapMode() ).setChecked( True )
    gbWrapVisualFlagsEnabled.setChecked( wrapVisualFlagsEnabled() )
    if  bgStartWrapVisualFlag.button( startWrapVisualFlag() ) :
        bgStartWrapVisualFlag.button( startWrapVisualFlag() ).setChecked( True )
    if  bgEndWrapVisualFlag.button( endWrapVisualFlag() ) :
        bgEndWrapVisualFlag.button( endWrapVisualFlag() ).setChecked( True )
    sWrappedLineIndentWidth.setValue( wrappedLineIndentWidth() )
    # Source APIs
    for ( i = 0; i < cbSourceAPIsLanguages.count(); i++ )
        cbSourceAPIsLanguages.setItemData( i, s.value( "SourceAPIs/" +cbSourceAPIsLanguages.itemText( i ) ).toStringList() )
    if  cbSourceAPIsLanguages.count() > 0 :
        cbSourceAPIsLanguages.setCurrentIndex( 0 )
    #  Lexers Associations
    QMap<QString, l = MonkeyCore.fileManager().associations()
    for k in l.keys():
        foreach ( QString e, l.value( k ) )
            it = QTreeWidgetItem( twLexersAssociations )
            it.setText( 0, e )
            it.setText( 1, k )


    #  Lexers Highlighting
    for l in mLexers:
    l.readSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )

    if  cbLexersHighlightingLanguages.count() :
        on_cbLexersHighlightingLanguages_currentIndexChanged( cbLexersHighlightingLanguages.itemText( 0 ) )

    #  Abbreviations
    for a in MonkeyCore.abbreviationsManager().abbreviations():
        it = QTreeWidgetItem( twAbbreviations )
        it.setText( 0, a.Macro )
        it.setText( 1, a.Description )
        it.setText( 2, a.Language )
        it.setData( 0, Qt.UserRole, a.Snippet )


    # environment variables editor
    eveVariables.setVariables( MonkeyCore.consoleManager().environmentVariablesManager().variables(), True )


def saveSettings(self):
    s = MonkeyCore.settings()
    QString sp

    # General
    setSaveFilesOnCustomAction( cbSaveFiles.isChecked() )
    setDocumentMode( (pWorkspace.ViewMode)cbTabModes.itemData( cbTabModes.currentIndex() ).toInt() )
    setSaveSessionOnClose( cbSaveSession.isChecked() )
    setRestoreSessionOnStartup( cbRestoreSession.isChecked() )
    setShowQuickFileAccess( cbQuickFileAccess.isChecked() )
    setOpenedFileSortingMode( (pOpenedFileModel.SortMode)cbSortingMode.itemData( cbSortingMode.currentIndex() ).toInt() )

    # Paths
    s.setStoragePaths( Settings.SP_TEMPLATES, pleTemplatesPaths.values() )
    s.setStoragePaths( Settings.SP_TRANSLATIONS, pleTranslationsPaths.values() )
    s.setStoragePaths( Settings.SP_PLUGINS, plePluginsPaths.values() )

    # Editor
    #  General
    setAutoSyntaxCheck( cbAutoSyntaxCheck.isChecked() )
    setConvertTabsUponOpen( cbConvertTabsUponOpen.isChecked() )
    setCreateBackupUponOpen( cbCreateBackupUponOpen.isChecked() ) 
    setDefaultCodec( cbDefaultCodec.currentText() )
    setSelectionBackgroundColor( tbSelectionBackground.color() )
    setSelectionForegroundColor( tbSelectionForeground.color() )
    setDefaultDocumentColours( gbDefaultDocumentColours.isChecked() )
    setDefaultDocumentPen( tbDefaultDocumentPen.color() )
    setDefaultDocumentPaper( tbDefaultDocumentPaper.color() )
    setDefaultDocumentFont( lDefaultDocumentFont.font() )
    #  Auto Completion
    setAutoCompletionSource( QsciScintilla.AcsNone )
    if  gbAutoCompletionEnabled.isChecked() :
        setAutoCompletionSource( (QsciScintilla.AutoCompletionSource)bgAutoCompletionSource.checkedId() )
    setAutoCompletionCaseSensitivity( cbAutoCompletionCaseSensitivity.isChecked() )
    setAutoCompletionReplaceWord( cbAutoCompletionReplaceWord.isChecked() )
    setAutoCompletionShowSingle( cbAutoCompletionShowSingle.isChecked() )
    setAutoCompletionThreshold( sAutoCompletionThreshold.value() )
    #  Call Tips
    setCallTipsStyle( QsciScintilla.CallTipsNone )
    if  gbCalltipsEnabled.isChecked() :
        setCallTipsStyle( (QsciScintilla.CallTipsStyle)bgCallTipsStyle.checkedId() )
    setCallTipsVisible( sCallTipsVisible.value() )
    setCallTipsBackgroundColor( tbCalltipsBackground.color() )
    setCallTipsForegroundColor( tbCalltipsForeground.color() )
    setCallTipsHighlightColor( tbCalltipsHighlight.color() )
    #  Indentation
    setAutoIndent( cbAutoIndent.isChecked()  )
    setBackspaceUnindents( cbBackspaceUnindents.isChecked() )
    setIndentationGuides( cbIndentationGuides.isChecked() )
    setIndentationsUseTabs( cbIndentationUseTabs.isChecked() )
    setTabIndents( cbTabIndents.isChecked() )
    setAutoDetectIndent( cbAutodetectIndent.isChecked() )
    setTabWidth( sIndentationTabWidth.value() )
    setIndentationWidth( sIndentationWidth.value() )
    setIndentationGuidesBackgroundColor( tbIndentationGuidesBackground.color() )
    setIndentationGuidesForegroundColor( tbIndentationGuidesForeground.color() )
    #  Brace Matching
    setBraceMatching( QsciScintilla.NoBraceMatch )
    if  gbBraceMatchingEnabled.isChecked() :
        setBraceMatching( (QsciScintilla.BraceMatch)bgBraceMatch.checkedId() )
    setMatchedBraceBackgroundColor( tbMatchedBraceBackground.color() )
    setMatchedBraceForegroundColor( tbMatchedBraceForeground.color() )
    setUnmatchedBraceBackgroundColor( tbUnmatchedBraceBackground.color() )
    setUnmatchedBraceForegroundColor( tbUnmatchedBraceForeground.color() )
    #  Edge Mode
    setEdgeMode( QsciScintilla.EdgeNone )
    if  gbEdgeModeEnabled.isChecked() :
        setEdgeMode( (QsciScintilla.EdgeMode)bgEdgeMode.checkedId() )
    setEdgeColumn( sEdgeColumnNumber.value() )
    setEdgeColor( tbEdgeColor.color() )
    #  Caret
    setCaretLineVisible( gbCaretLineVisible.isChecked() )
    setCaretLineBackgroundColor( tbCaretLineBackground.color() )
    setCaretForegroundColor( tbCaretForeground.color() )
    setCaretWidth( sCaretWidth.value() )
    #  Margins
    setLineNumbersMarginEnabled( gbLineNumbersMarginEnabled.isChecked() )
    setLineNumbersMarginWidth( sLineNumbersMarginWidth.value() )
    setLineNumbersMarginAutoWidth( cbLineNumbersMarginAutoWidth.isChecked() )
    setFolding( QsciScintilla.NoFoldStyle )
    if  gbFoldMarginEnabled.isChecked() :
        setFolding( (QsciScintilla.FoldStyle)bgFoldStyle.checkedId() )
    setFoldMarginForegroundColor( tbFoldMarginForeground.color() )
    setFoldMarginBackgroundColor( tbFoldMarginBackground.color() )
    setMarginsEnabled( gbMarginsEnabled.isChecked() )
    setMarginsForegroundColor( tbMarginsForeground.color() )
    setMarginsBackgroundColor( tbMarginsBackground.color() )
    setMarginsFont( tbMarginsFont.font() )
    #  Special Characters
    setEolMode( (QsciScintilla.EolMode)bgEolMode.checkedId() )
    setEolVisibility( cbEolVisibility.isChecked() )
    setAutoDetectEol( cbAutoDetectEol.isChecked() )
    setAutoEolConversion( cbAutoEolConversion.isChecked() )
    setWhitespaceVisibility( QsciScintilla.WsInvisible )
    if  gbWhitespaceVisibilityEnabled.isChecked() :
        setWhitespaceVisibility( (QsciScintilla.WhitespaceVisibility)bgWhitespaceVisibility.checkedId() )
    setWrapMode( QsciScintilla.WrapNone )
    if  gbWrapModeEnabled.isChecked() :
        setWrapMode( (QsciScintilla.WrapMode)bgWrapMode.checkedId() )
    setWrapVisualFlagsEnabled( gbWrapVisualFlagsEnabled.isChecked() )
    setStartWrapVisualFlag( QsciScintilla.WrapFlagNone )
    if  gbWrapVisualFlagsEnabled.isChecked() :
        setStartWrapVisualFlag( (QsciScintilla.WrapVisualFlag)bgStartWrapVisualFlag.checkedId() )
    setEndWrapVisualFlag( QsciScintilla.WrapFlagNone )
    if  gbWrapVisualFlagsEnabled.isChecked() :
        setEndWrapVisualFlag( (QsciScintilla.WrapVisualFlag)bgEndWrapVisualFlag.checkedId() )
    setWrappedLineIndentWidth( sWrappedLineIndentWidth.value() )
    # Source APIs
    sp = "SourceAPIs/"
    for ( i = 0; i < cbSourceAPIsLanguages.count(); i++ )
        s.setValue( sp +cbSourceAPIsLanguages.itemText( i ), cbSourceAPIsLanguages.itemData( i ).toStringList() )

    #  Lexers Associations
    QMap<QString, suffixes

    for ( i = 0; i < twLexersAssociations.topLevelItemCount(); i++ )
        it = twLexersAssociations.topLevelItem( i )

        suffixes[ it.text( 1 ) ] << it.text( 0 )


    for type in suffixes.keys():
        MonkeyCore.fileManager().setCommand( type, suffixes[ type ] )


    MonkeyCore.fileManager().generateScript()

    #  Lexers Highlighting
    for l in mLexers:
        l.setDefaultPaper( tbDefaultDocumentPaper.color() )
        l.setDefaultColor( tbDefaultDocumentPen.color() )
        l.writeSettings( *s, scintillaSettingsPath().toLocal8Bit().constData() )


    #  Abbreviations
    pAbbreviationList abbreviations
    for ( i = 0; i < twAbbreviations.topLevelItemCount(); i++ )
        it = twAbbreviations.topLevelItem( i )

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
    it = twMenu.selectedItems().value( 0 )

    if  it :
        lInformations.setText( it.text( 0 ) )
        i = twMenu.indexOfTopLevelItem( it )
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

    font = QFontDialog.getFont( &ok, font, self, tr( "Choose the default document font" ), QFontDialog.DontUseNativeDialog )

    if  ok :
        lDefaultDocumentFont.setFont( font )
        lDefaultDocumentFont.setToolTip( font.toString() )



def on_gbAutoCompletionEnabled_clicked(self, checked ):
    if  checked and bgAutoCompletionSource.checkedId() == -1 :
        mode = autoCompletionSource()

        if  mode == QsciScintilla.AcsNone :
            mode = QsciScintilla.AcsAll


        bgAutoCompletionSource.button( mode ).setChecked( True )



def tbFonts_clicked(self):
    tb = qobject_cast<QToolButton*>( sender() )
    bool b
    f = QFontDialog.getFont( &b, tb.font(), window() )
    if  b :
        tb.setFont( f )


def cbSourceAPIsLanguages_beforeChanged(self, i ):
    if  i == cbSourceAPIsLanguages.currentIndex() :
        QStringList l
        for ( j = 0; j < lwSourceAPIs.count(); j++ )
            l << lwSourceAPIs.item( j ).text()
        cbSourceAPIsLanguages.setItemData( i, l )



def on_cbSourceAPIsLanguages_currentIndexChanged(self, i ):
    lwSourceAPIs.clear()
    lwSourceAPIs.addItems( cbSourceAPIsLanguages.itemData( i ).toStringList() )


def on_pbSourceAPIsDelete_clicked(self):
    # get selected item
    it = lwSourceAPIs.selectedItems().value( 0 )
    if  it :
        delete it
        cbSourceAPIsLanguages_beforeChanged( cbSourceAPIsLanguages.currentIndex() )



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
    cbSourceAPIsLanguages_beforeChanged( cbSourceAPIsLanguages.currentIndex() )


def on_pbSourceAPIsBrowse_clicked(self):
    files = QFileDialog.getOpenFileNames( window(), tr( "Select API files" ), QString.null, tr( "API Files (*.api);;All Files (*)" ) )
    if  not files.isEmpty() :
        leSourceAPIs.setText( files.join( ";" ) )


def on_twLexersAssociations_itemSelectionChanged(self):
    it = twLexersAssociations.selectedItems().value( 0 )
    if  it :
        leLexersAssociationsFilenamePattern.setText( it.text( 0 ) )
        cbLexersAssociationsLanguages.setCurrentIndex( cbLexersAssociationsLanguages.findText( it.text( 1 ) ) )



def on_pbLexersAssociationsAddChange_clicked(self):
    f = leLexersAssociationsFilenamePattern.text()
    l = cbLexersAssociationsLanguages.currentText()
    if  f.isEmpty() or l.isEmpty() :
        return
    it = twLexersAssociations.selectedItems().value( 0 )
    if  not it or it.text( 0 ) != f :
        # check if item with same parameters already exists
        QList<QTreeWidgetItem*> l = twLexersAssociations.findItems( f, Qt.MatchFixedString )
        if  l.count() :
            it = l.at( 0 )
        else:
            it = QTreeWidgetItem( twLexersAssociations )

    it.setText( 0, f )
    it.setText( 1, l )
    twLexersAssociations.setCurrentItem( 0 )
    twLexersAssociations.selectionModel().clear()
    leLexersAssociationsFilenamePattern.clear()
    cbLexersAssociationsLanguages.setCurrentIndex( -1 )


def on_pbLexersAssociationsDelete_clicked(self):
    it = twLexersAssociations.selectedItems().value( 0 )
    if  it :
        delete it
        twLexersAssociations.setCurrentItem( 0 )
        twLexersAssociations.selectionModel().clear()
        leLexersAssociationsFilenamePattern.clear()
        cbLexersAssociationsLanguages.setCurrentIndex( -1 )



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
    cbLexersHighlightingFoldComments.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldComments.setChecked( v.toBool() )
    # fold compact
    v = lexerProperty( "foldCompact", l )
    cbLexersHighlightingFoldCompact.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldCompact.setChecked( v.toBool() )
    # fold quotes
    v = lexerProperty( "foldQuotes", l )
    cbLexersHighlightingFoldQuotes.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldQuotes.setChecked( v.toBool() )
    # fold directives
    v = lexerProperty( "foldDirectives", l )
    cbLexersHighlightingFoldDirectives.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldDirectives.setChecked( v.toBool() )
    # fold at begin
    v = lexerProperty( "foldAtBegin", l )
    cbLexersHighlightingFoldAtBegin.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldAtBegin.setChecked( v.toBool() )
    # fold at parenthesis
    v = lexerProperty( "foldAtParenthesis", l )
    cbLexersHighlightingFoldAtParenthesis.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldAtParenthesis.setChecked( v.toBool() )
    # fold at else:
    v = lexerProperty( "foldAtElse", l )
    cbLexersHighlightingFoldAtElse.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldAtElse.setChecked( v.toBool() )
    # fold at module
    v = lexerProperty( "foldAtModule", l )
    cbLexersHighlightingFoldAtModule.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldAtModule.setChecked( v.toBool() )
    # fold preprocessor
    v = lexerProperty( "foldPreprocessor", l )
    cbLexersHighlightingFoldPreprocessor.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingFoldPreprocessor.setChecked( v.toBool() )
    # style preprocessor
    v = lexerProperty( "stylePreprocessor", l )
    cbLexersHighlightingStylePreprocessor.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingStylePreprocessor.setChecked( v.toBool() )
    # indent opening brace
    cbLexersHighlightingIndentOpeningBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiOpening )
    # indent closing brace
    cbLexersHighlightingIndentClosingBrace.setChecked( l.autoIndentStyle() & QsciScintilla.AiClosing )
    # case sensitive tags
    v = lexerProperty( "caseSensitiveTags", l )
    cbLexersHighlightingCaseSensitiveTags.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingCaseSensitiveTags.setChecked( v.toBool() )
    # backslash escapes
    v = lexerProperty( "backslashEscapes", l )
    cbLexersHighlightingBackslashEscapes.setVisible( v.isValid() )
    if  v.isValid() :
        cbLexersHighlightingBackslashEscapes.setChecked( v.toBool() )
    # indentation warning
    v = lexerProperty( "indentationWarning", l )
    lLexersHighlightingIndentationWarning.setVisible( v.isValid() )
    cbLexersHighlightingIndentationWarning.setVisible( lLexersHighlightingIndentationWarning.isVisible() )
    if  v.isValid() :
        cbLexersHighlightingIndentationWarning.setCurrentIndex( cbLexersHighlightingIndentationWarning.findData( v.toInt() ) )


def on_lwLexersHighlightingElements_itemSelectionChanged(self):
    it = lwLexersHighlightingElements.selectedItems().value( 0 )
    if  it :
        cbLexersHighlightingFillEol.setChecked( mLexers.value( cbLexersHighlightingLanguages.currentText() ).eolFill( it.data( Qt.UserRole ).toInt() ) )


def lexersHighlightingColour_clicked(self):
    # get sender
    o = sender()
    # color
    QColor c
    # element colour
    if  o == pbLexersHighlightingForeground or o == pbLexersHighlightingBackground :
        # get item
        it = lwLexersHighlightingElements.selectedItems().value( 0 )
        # cancel if no item
        if  not it :
            return
        # get color
        c = QColorDialog.getColor( o == pbLexersHighlightingForeground ? it.foreground().color() : it.background().color(), window() )
        # apply color
        if  c.isValid() :
            if  o == pbLexersHighlightingForeground :
                it.setForeground( c )
                mLexers.value( cbLexersHighlightingLanguages.currentText() ).setColor( c, it.data( Qt.UserRole ).toInt() )

            elif  o == pbLexersHighlightingBackground :
                it.setBackground( c )
                mLexers.value( cbLexersHighlightingLanguages.currentText() ).setPaper( c, it.data( Qt.UserRole ).toInt() )



    # gobal color
    elif  o == pbLexersHighlightingAllForeground or o == pbLexersHighlightingAllBackground :
        # get lexer
        l = mLexers.value( cbLexersHighlightingLanguages.currentText() )
        # get color
        c = QColorDialog.getColor( o == pbLexersHighlightingAllForeground ? l.color( -1 ) : l.paper( -1 ), window() )
        # apply
        if  c.isValid() :
            if  o == pbLexersHighlightingAllForeground :
                l.setColor( c, -1 )
            elif  o == pbLexersHighlightingAllBackground :
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
    if  o == pbLexersHighlightingFont :
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
            mLexers.value( cbLexersHighlightingLanguages.currentText() ).setFont( f, it.data( Qt.UserRole ).toInt() )


    # global font
    elif  o == pbLexersHighlightingAllFont :
        # get lexer
        l = mLexers.value( cbLexersHighlightingLanguages.currentText() )
        # get font
        f = QFontDialog.getFont( &b, l.font( -1 ), window() )
        # apply
        if  b :
            l.setFont( f, -1 )
            on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )




def on_cbLexersHighlightingFillEol_clicked(self, b ):
    it = lwLexersHighlightingElements.selectedItems().value( 0 )
    if  it :
        mLexers.value( cbLexersHighlightingLanguages.currentText() ).setEolFill( b, it.data( Qt.UserRole ).toInt() )


def cbLexersHighlightingProperties_clicked(self, b ):
    # get check box
    cb = qobject_cast<QCheckBox*>( sender() )
    if  not cb :
        return
    # get lexer
    l = mLexers.value( cbLexersHighlightingLanguages.currentText() )
    # set lexer properties
    if  cb == cbLexersHighlightingIndentOpeningBrace or cb == cbLexersHighlightingIndentClosingBrace :
        if  cbLexersHighlightingIndentOpeningBrace.isChecked() and cbLexersHighlightingIndentClosingBrace.isChecked() :
            l.setAutoIndentStyle( QsciScintilla.AiOpening | QsciScintilla.AiClosing )
        elif  cbLexersHighlightingIndentOpeningBrace.isChecked() :
            l.setAutoIndentStyle( QsciScintilla.AiOpening )
        elif  cbLexersHighlightingIndentClosingBrace.isChecked() :
            l.setAutoIndentStyle( QsciScintilla.AiClosing )
        else:
            l.setAutoIndentStyle( QsciScintilla.AiMaintain )

    else:
        setLexerProperty( cb.statusTip(), l, b )


def on_cbLexersHighlightingIndentationWarning_currentIndexChanged(self, i ):
    # get lexer
    l = mLexers.value( cbLexersHighlightingLanguages.currentText() )
    # set lexer properties
    setLexerProperty( cbLexersHighlightingIndentationWarning.statusTip(), l, cbLexersHighlightingIndentationWarning.itemData( i ) )


def on_pbLexersHighlightingReset_clicked(self):
    # get lexer
    l = mLexers.value( cbLexersHighlightingLanguages.currentText() )
    # reset and refresh
    if  l :
        resetLexer( l )
        on_cbLexersHighlightingLanguages_currentIndexChanged( l.language() )



def on_pbLexersApplyDefaultFont_clicked(self):
    settings = MonkeyCore.settings()
     font = lDefaultDocumentFont.font()
     language = cbLexersHighlightingLanguages.currentText()

    settings.setDefaultLexerProperties( font, False )
    on_cbLexersHighlightingLanguages_currentIndexChanged( language )


def on_twAbbreviations_itemSelectionChanged(self):
    # get item
    it = twAbbreviations.selectedItems().value( 0 )
    if  it :
        teAbbreviationsCode.setPlainText( it.data( 0, Qt.UserRole ).toString() )
    # enable/disable according to selection
    teAbbreviationsCode.setEnabled( it )


def on_pbAbbreviationsAdd_clicked(self):
    UIAddAbbreviation.edit( twAbbreviations )


def on_pbAbbreviationsRemove_clicked(self):
    delete twAbbreviations.selectedItems().value( 0 )
    teAbbreviationsCode.clear()


def on_teAbbreviationsCode_textChanged(self):
    # get item
    it = twAbbreviations.selectedItems().value( 0 )
    if  it :
        it.setData( 0, Qt.UserRole, teAbbreviationsCode.toPlainText() )


def reject(self):
    settings = MonkeyCore.settings()

    for lexer in mLexers:
        lexer.readSettings( *settings, scintillaSettingsPath().toLocal8Bit().constData() )


    QDialog.reject()


def accept(self):
    apply()
    QDialog.accept()


def apply(self):
    saveSettings()
    applyProperties()
    MonkeyCore.workspace().loadSettings()

