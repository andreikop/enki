'''***************************************************************************
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
***************************************************************************'''
'''!
    \file pMonkeyStudio.cpp
    \date 2008-01-14T00:37:22
    \author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
    \brief A global namespace for various options and usefull functions
'''
#ifndef PMONKEYSTUDIO_H
#define PMONKEYSTUDIO_H

#include "workspace/pWorkspace.h"
#include "workspace/pOpenedFileModel.h"

#include <qsciscintilla.h>

#include <QApplication>
#include <QDir>

class pEditor
class QsciAPIs

namespace pMonkeyStudio
enum OSVariant
    UnixOS, # not mac
    MacOS,
    WindowsOS,
#if defined( Q_OS_WIN )
    CurrentOS = WindowsOS
#elif defined( Q_OS_MAC )
    CurrentOS = MacOS
#else:
    CurrentOS = UnixOS
#endif


Q_MONKEY_EXPORT bool isSameFile(  QString& left, right )

Q_MONKEY_EXPORT QStringList availableTextCodecs()
Q_MONKEY_EXPORT QStringList availableImageFormats()
Q_MONKEY_EXPORT QStringList availableLanguages()

Q_MONKEY_EXPORT QFileInfoList getFolders( QDir fromDir, filters, recursive = True )
Q_MONKEY_EXPORT QFileInfoList getFiles( QDir fromDir, filters, recursive = True )
Q_MONKEY_EXPORT QFileInfoList getFiles( QDir fromDir, filters = QString.null, recursive = True )

Q_MONKEY_EXPORT QStringList getImageFileNames(  QString& title, filename, parent = QApplication.activeWindow() )
Q_MONKEY_EXPORT QString getImageFileName(  QString& title, filename, parent = QApplication.activeWindow() )

Q_MONKEY_EXPORT QStringList getOpenFileNames(  QString& title, filename, filters = QString(), parent = QApplication.activeWindow() )
Q_MONKEY_EXPORT QString getOpenFileName(  QString& title, filename, filters = QString(), parent = QApplication.activeWindow() )

Q_MONKEY_EXPORT QString getSaveFileName(  QString& title, filename, filters = QString(), parent = QApplication.activeWindow() )

Q_MONKEY_EXPORT QString getExistingDirectory(  QString& title, path, parent = QApplication.activeWindow() )

Q_MONKEY_EXPORT QString tokenizeHome(  QString& string )
Q_MONKEY_EXPORT QString unTokenizeHome(  QString& string )

Q_MONKEY_EXPORT QMap<QString, availableLanguagesSuffixes()
Q_MONKEY_EXPORT QMap<QString, availableFilesSuffixes()
Q_MONKEY_EXPORT QString availableLanguagesFilters()
Q_MONKEY_EXPORT QString availableFilesFilters()

Q_MONKEY_EXPORT QString settingsPath()
Q_MONKEY_EXPORT QString scintillaSettingsPath()
Q_MONKEY_EXPORT void prepareAPIs()
Q_MONKEY_EXPORT QsciAPIs* apisForLexer( QsciLexer* lexer )
Q_MONKEY_EXPORT QString languageForFileName(  QString& fileName )
Q_MONKEY_EXPORT QsciLexer* lexerForFileName(  QString& fileName )
Q_MONKEY_EXPORT QsciLexer* lexerForLanguage(  QString& language )
Q_MONKEY_EXPORT bool setLexerProperty(  QString& property, lexer, value )
Q_MONKEY_EXPORT QVariant lexerProperty(  QString& property, lexer )
Q_MONKEY_EXPORT void resetLexer( QsciLexer* lexer )
Q_MONKEY_EXPORT void applyProperties()
Q_MONKEY_EXPORT void setEditorProperties( pEditor* editor )

Q_MONKEY_EXPORT void showMacFocusRect( QWidget* widget, show, recursive )
Q_MONKEY_EXPORT void setMacSmallSize( QWidget* widget, small, recursive )

'''**** GENERAL ****'''
Q_MONKEY_EXPORT void setSaveFilesOnCustomAction( bool save )
Q_MONKEY_EXPORT bool saveFilesOnCustomAction()
Q_MONKEY_EXPORT void setTabsHaveCloseButton( bool have )
Q_MONKEY_EXPORT bool tabsHaveCloseButton()
Q_MONKEY_EXPORT void setTabsHaveShortcut( bool have )
Q_MONKEY_EXPORT bool tabsHaveShortcut()
Q_MONKEY_EXPORT void setTabsElided( bool elided )
Q_MONKEY_EXPORT bool tabsElided()
Q_MONKEY_EXPORT void setTabsTextColor(  QColor& color )
Q_MONKEY_EXPORT QColor tabsTextColor()
Q_MONKEY_EXPORT void setCurrentTabTextColor(  QColor& color )
Q_MONKEY_EXPORT QColor currentTabTextColor()
Q_MONKEY_EXPORT void setDocumentMode( pWorkspace.ViewMode mode )
Q_MONKEY_EXPORT pWorkspace.ViewMode documentMode()
Q_MONKEY_EXPORT void setSaveSessionOnClose( bool save )
Q_MONKEY_EXPORT bool saveSessionOnClose()
Q_MONKEY_EXPORT void setRestoreSessionOnStartup( bool restore )
Q_MONKEY_EXPORT bool restoreSessionOnStartup()
Q_MONKEY_EXPORT void setShowQuickFileAccess( bool show )
Q_MONKEY_EXPORT bool showQuickFileAccess()
Q_MONKEY_EXPORT void setOpenedFileSortingMode( pOpenedFileModel.SortMode mode )
Q_MONKEY_EXPORT pOpenedFileModel.SortMode openedFileSortingMode()

'''*****    EDITOR *****'''
# General
Q_MONKEY_EXPORT void setAutoSyntaxCheck( bool check )
Q_MONKEY_EXPORT bool autoSyntaxCheck()
Q_MONKEY_EXPORT void setConvertTabsUponOpen( bool convert )
Q_MONKEY_EXPORT bool convertTabsUponOpen()
Q_MONKEY_EXPORT void setCreateBackupUponOpen( bool backup )
Q_MONKEY_EXPORT bool createBackupUponOpen()
Q_MONKEY_EXPORT void setAutoEolConversion( bool convert )
Q_MONKEY_EXPORT bool autoEolConversion()
Q_MONKEY_EXPORT void setDefaultCodec(  QString& codec )
Q_MONKEY_EXPORT QString defaultCodec()
Q_MONKEY_EXPORT void setSelectionBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor selectionBackgroundColor()
Q_MONKEY_EXPORT void setSelectionForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor selectionForegroundColor()
Q_MONKEY_EXPORT void setDefaultDocumentColours( bool defaultColors )
Q_MONKEY_EXPORT bool defaultDocumentColours()
Q_MONKEY_EXPORT void setDefaultDocumentPen(  QColor& defaultPen )
Q_MONKEY_EXPORT QColor defaultDocumentPen()
Q_MONKEY_EXPORT void setDefaultDocumentPaper(  QColor& defaultPaper )
Q_MONKEY_EXPORT QColor defaultDocumentPaper()
Q_MONKEY_EXPORT void setDefaultDocumentFont(  QFont& defaultFont )
Q_MONKEY_EXPORT QFont defaultDocumentFont()
# Auto Completion
Q_MONKEY_EXPORT void setAutoCompletionCaseSensitivity( bool caseSensitive )
Q_MONKEY_EXPORT bool autoCompletionCaseSensitivity()
Q_MONKEY_EXPORT void setAutoCompletionReplaceWord( bool replace )
Q_MONKEY_EXPORT bool autoCompletionReplaceWord()
Q_MONKEY_EXPORT void setAutoCompletionShowSingle( bool showSingle )
Q_MONKEY_EXPORT bool autoCompletionShowSingle()
Q_MONKEY_EXPORT void setAutoCompletionSource( QsciScintilla.AutoCompletionSource source )
Q_MONKEY_EXPORT QsciScintilla.AutoCompletionSource autoCompletionSource()
Q_MONKEY_EXPORT void setAutoCompletionThreshold( int count )
Q_MONKEY_EXPORT int autoCompletionThreshold()
# CallTips
Q_MONKEY_EXPORT void setCallTipsBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor callTipsBackgroundColor()
Q_MONKEY_EXPORT void setCallTipsForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor callTipsForegroundColor()
Q_MONKEY_EXPORT void setCallTipsHighlightColor(  QColor& highlight )
Q_MONKEY_EXPORT QColor callTipsHighlightColor()
Q_MONKEY_EXPORT void setCallTipsStyle( QsciScintilla.CallTipsStyle style )
Q_MONKEY_EXPORT QsciScintilla.CallTipsStyle callTipsStyle()
Q_MONKEY_EXPORT void setCallTipsVisible( int count )
Q_MONKEY_EXPORT int callTipsVisible()
# Indentation
Q_MONKEY_EXPORT void setAutoIndent( bool indent )
Q_MONKEY_EXPORT bool autoIndent()
Q_MONKEY_EXPORT void setBackspaceUnindents( bool unindents )
Q_MONKEY_EXPORT bool backspaceUnindents()
Q_MONKEY_EXPORT void setIndentationGuides( bool guides )
Q_MONKEY_EXPORT bool indentationGuides()
Q_MONKEY_EXPORT void setIndentationsUseTabs( bool tabs )
Q_MONKEY_EXPORT bool indentationsUseTabs()
Q_MONKEY_EXPORT void setAutoDetectIndent( bool detect )
Q_MONKEY_EXPORT bool autoDetectIndent()
Q_MONKEY_EXPORT void setIndentationWidth( int width )
Q_MONKEY_EXPORT int indentationWidth()
Q_MONKEY_EXPORT void setTabIndents( bool indents )
Q_MONKEY_EXPORT bool tabIndents()
Q_MONKEY_EXPORT void setTabWidth( int width )
Q_MONKEY_EXPORT int tabWidth()
Q_MONKEY_EXPORT void setIndentationGuidesBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor indentationGuidesBackgroundColor()
Q_MONKEY_EXPORT void setIndentationGuidesForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor indentationGuidesForegroundColor()
# Brace Matching
Q_MONKEY_EXPORT void setBraceMatching( QsciScintilla.BraceMatch mode )
Q_MONKEY_EXPORT QsciScintilla.BraceMatch braceMatching()
Q_MONKEY_EXPORT void setMatchedBraceBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor matchedBraceBackgroundColor()
Q_MONKEY_EXPORT void setMatchedBraceForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor matchedBraceForegroundColor()
Q_MONKEY_EXPORT void setUnmatchedBraceBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor unmatchedBraceBackgroundColor()
Q_MONKEY_EXPORT void setUnmatchedBraceForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor unmatchedBraceForegroundColor()
# Edge Mode
Q_MONKEY_EXPORT void setEdgeMode( QsciScintilla.EdgeMode mode )
Q_MONKEY_EXPORT QsciScintilla.EdgeMode edgeMode()
Q_MONKEY_EXPORT void setEdgeColor(  QColor& color )
Q_MONKEY_EXPORT QColor edgeColor()
Q_MONKEY_EXPORT void setEdgeColumn( int columns )
Q_MONKEY_EXPORT int edgeColumn()
# Caret
Q_MONKEY_EXPORT void setCaretLineVisible( bool visible )
Q_MONKEY_EXPORT bool caretLineVisible()
Q_MONKEY_EXPORT void setCaretLineBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor caretLineBackgroundColor()
Q_MONKEY_EXPORT void setCaretForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor caretForegroundColor()
Q_MONKEY_EXPORT void setCaretWidth( int width )
Q_MONKEY_EXPORT int caretWidth()
# Margins
Q_MONKEY_EXPORT void setLineNumbersMarginEnabled( bool enabled )
Q_MONKEY_EXPORT bool lineNumbersMarginEnabled()
Q_MONKEY_EXPORT void setLineNumbersMarginWidth( int width )
Q_MONKEY_EXPORT int lineNumbersMarginWidth()
Q_MONKEY_EXPORT void setLineNumbersMarginAutoWidth( bool width )
Q_MONKEY_EXPORT bool lineNumbersMarginAutoWidth()
Q_MONKEY_EXPORT void setFolding( QsciScintilla.FoldStyle style )
Q_MONKEY_EXPORT QsciScintilla.FoldStyle folding()
Q_MONKEY_EXPORT void setFoldMarginBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor foldMarginBackgroundColor()
Q_MONKEY_EXPORT void setFoldMarginForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor foldMarginForegroundColor()
Q_MONKEY_EXPORT void setMarginsEnabled( bool enabled )
Q_MONKEY_EXPORT bool marginsEnabled()
Q_MONKEY_EXPORT void setMarginsBackgroundColor(  QColor& background )
Q_MONKEY_EXPORT QColor marginsBackgroundColor()
Q_MONKEY_EXPORT void setMarginsForegroundColor(  QColor& foreground )
Q_MONKEY_EXPORT QColor marginsForegroundColor()
Q_MONKEY_EXPORT void setMarginsFont(  QFont& font )
Q_MONKEY_EXPORT QFont marginsFont()
# Special Characters
Q_MONKEY_EXPORT void setEolMode( QsciScintilla.EolMode mode )
Q_MONKEY_EXPORT QsciScintilla.EolMode eolMode( os = pMonkeyStudio.CurrentOS )
Q_MONKEY_EXPORT QString getEol( mode = pMonkeyStudio.eolMode() )
Q_MONKEY_EXPORT void setEolVisibility( bool visible )
Q_MONKEY_EXPORT bool eolVisibility()
Q_MONKEY_EXPORT void setAutoDetectEol( bool detect )
Q_MONKEY_EXPORT bool autoDetectEol()
Q_MONKEY_EXPORT void setWhitespaceVisibility( QsciScintilla.WhitespaceVisibility visibility )
Q_MONKEY_EXPORT QsciScintilla.WhitespaceVisibility whitespaceVisibility()
Q_MONKEY_EXPORT void setWrapMode( QsciScintilla.WrapMode mode )
Q_MONKEY_EXPORT QsciScintilla.WrapMode wrapMode()
Q_MONKEY_EXPORT void setWrapVisualFlagsEnabled( bool enabled )
Q_MONKEY_EXPORT bool wrapVisualFlagsEnabled()
Q_MONKEY_EXPORT void setStartWrapVisualFlag( QsciScintilla.WrapVisualFlag flag )
Q_MONKEY_EXPORT QsciScintilla.WrapVisualFlag startWrapVisualFlag()
Q_MONKEY_EXPORT void setEndWrapVisualFlag( QsciScintilla.WrapVisualFlag flag )
Q_MONKEY_EXPORT QsciScintilla.WrapVisualFlag endWrapVisualFlag()
Q_MONKEY_EXPORT void setWrappedLineIndentWidth( int witdh )
Q_MONKEY_EXPORT int wrappedLineIndentWidth()


#endif # PMONKEYSTUDIO_H
