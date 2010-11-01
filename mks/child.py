"""Text editor widget. Uses QScintilla internally"""

import os.path
import shutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from PyQt4.Qsci import *

import mks.monkeystudio
import mks.abstractchild
import mks.settings

"""TODO move this code to the pChild class
class _pEditor(QsciScintilla):
    
        self.mPixSize = QSize( 16, 16 )
        # register image for bookmarks
        self.markerDefine( QPixmap( ":/editor/bookmark.png" ).scaled( self.mPixSize ), mdBookmark )
        
        # init qscishortcutsmanager if needed
        self.SendScintilla( QsciScintillaBase.SCI_CLEARALLCMDKEYS )
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_TAB, SCI_TAB)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_ESCAPE, SCI_CANCEL)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_RETURN, SCI_NEWLINE)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_DOWN, SCI_LINEDOWN)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_UP, SCI_LINEUP)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_RIGHT, SCI_CHARRIGHT)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_LEFT, SCI_CHARLEFT)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_BACK, SCI_DELETEBACK)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_PRIOR, SCI_PAGEUP)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_NEXT, SCI_PAGEDOWN)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_HOME, SCI_VCHOME)
        self.SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_END, SCI_LINEEND)

        # By default control characters don't do anything (rather than insert the
        # control character into the text). (c) Phil
        for k in range(ord('A'), ord('Z') + 1):
            self.SendScintilla(QsciScintillaBase.SCI_ASSIGNCMDKEY,
                    k + (QsciScintillaBase.SCMOD_CTRL << 16),
                        QsciScintillaBase.SCI_NULL)

        # Create shortcuts manager, not created
        qSciShortcutsManager.instance()
    
    def findFirst(self, expr, re, cs, wo, wrap, forward, line, index, show ):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        return QsciScintilla.findFirst( expr, re, cs, wo, wrap, forward, line, index, show )
    #else:
        mSearchState.inProgress = False

        if  expr.isEmpty() :        return False


        mSearchState.expr = expr
        mSearchState.wrap = wrap
        mSearchState.forward = forward

        mSearchState.flags = ( cs ? SCFIND_MATCHCASE : 0 ) | ( wo ? SCFIND_WHOLEWORD : 0 ) | ( re ? SCFIND_REGEXP : 0 )

        if  line < 0 or index < 0 :        mSearchState.startpos = SendScintilla( SCI_GETCURRENTPOS )

        else:
            mSearchState.startpos = positionFromLineIndex( line, index )


        if  forward :        mSearchState.endpos = SendScintilla( SCI_GETLENGTH )

        else:
            mSearchState.endpos = 0


        mSearchState.show = show

        return search()
    #endif


    def findNext(self):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        return QsciScintilla.findNext()
    #else:
        if  not mSearchState.inProgress :        return False


        return search()
    #endif


    def replace(self, replaceStr ):
    #if USE_QSCINTILLA_SEARCH_ENGINE == 1
        QsciScintilla.replace( replaceStr )
    #else:
        if  not mSearchState.inProgress :        return


        static QRegExp rxd( "\\$(\\d+)" )
        rxd.setMinimal( True )
         isRE = mSearchState.flags & SCFIND_REGEXP
        rx = mSearchState.rx
         captures = rx.capturedTexts()
        text = replaceStr
         start = SendScintilla( SCI_GETSELECTIONSTART )

        SendScintilla( SCI_TARGETFROMSELECTION )
        
        # remove selection
        removeSelectedText()
        
        # compute replace text
        if  isRE and captures.count() > 1 :        pos = 0
            
            while ( ( pos = rxd.indexIn( text, pos ) ) != -1 )             id = rxd.cap( 1 ).toInt()
                
                if  id < 0 or id >= captures.count() :                pos += rxd.matchedLength()
                    continue

                
                # update replace text with partial occurrences
                text.replace( pos, rxd.matchedLength(), captures.at( id ) )
                
                # next
                pos += captures.at( id ).length()


        
        # insert replace text
         len = text.toUtf8().length(); # scintilla position are count from qbytearray data: ie: non ascii leter are 2 or more bits.
        insert( text )

        # Reset the selection.
        SendScintilla( SCI_SETSELECTIONSTART, start )
        SendScintilla( SCI_SETSELECTIONEND, start +len )

        if  mSearchState.forward :        mSearchState.startpos = start +len

    #endif


    def keyPressEvent(self, e ):
        if  not e.isAutoRepeat() and e.modifiers() & Qt.ControlModifier and e.key() == Qt.Key_Space :
            switch ( autoCompletionSource() )
                case QsciScintilla.AcsAll:
                    autoCompleteFromAll()
                    break
                case QsciScintilla.AcsAPIs:
                    autoCompleteFromAPIs()
                    break
                case QsciScintilla.AcsDocument:
                    autoCompleteFromDocument()
                    break
                default:
                    break

            return

        QsciScintilla.keyPressEvent( e )


    def search(self):
        SendScintilla( SCI_SETSEARCHFLAGS, mSearchState.flags )

        pos = simpleSearch()

        # See if it was found.  If not and wraparound is wanted, again.
        if  pos == -1 and mSearchState.wrap :        if  mSearchState.forward :            mSearchState.startpos = 0
                mSearchState.endpos = SendScintilla( SCI_GETLENGTH )

            else:
                mSearchState.startpos = SendScintilla( SCI_GETLENGTH )
                mSearchState.endpos = 0


            pos = simpleSearch()


        if  pos == -1 :        mSearchState.inProgress = False
            return False


        # It was found.
        targstart = SendScintilla( SCI_GETTARGETSTART )
        targend = SendScintilla( SCI_GETTARGETEND )

        # Ensure the text found is visible if required.
        if  mSearchState.show :        startLine = SendScintilla( SCI_LINEFROMPOSITION, targstart )
            endLine = SendScintilla( SCI_LINEFROMPOSITION, targend )

            for ( i = startLine; i <= endLine; ++i )            SendScintilla( SCI_ENSUREVISIBLEENFORCEPOLICY, i )



        # Now set the selection.
        SendScintilla( SCI_SETSEL, targstart, targend )

        # Finally adjust the start position so that we don't find the same one
        # again.
        if  mSearchState.forward :        mSearchState.startpos = targend

        elif  ( mSearchState.startpos = targstart -1 ) < 0 :        mSearchState.startpos = 0


        mSearchState.inProgress = True
        return True


    def simpleSearch(self):
        if  mSearchState.startpos == mSearchState.endpos :        return -1


        SendScintilla( SCI_SETTARGETSTART, mSearchState.startpos )
        SendScintilla( SCI_SETTARGETEND, mSearchState.endpos )
        
         isCS = mSearchState.flags & SCFIND_MATCHCASE
         isWW = mSearchState.flags & SCFIND_WHOLEWORD
         isRE = mSearchState.flags & SCFIND_REGEXP
         from = qMin( mSearchState.startpos, mSearchState.endpos )
         to = qMax( mSearchState.startpos, mSearchState.endpos )
         data = self.text().toUtf8().mid( from, to -from ); # scintilla position are from qbytearray size, non ascii letter are 2 or more bits.
         text = QString.fromUtf8( data )
        pattern = isRE ? mSearchState.expr : QRegExp.escape( mSearchState.expr )
        rx = mSearchState.rx
        
        if  isWW :        pattern.prepend( "\\b" ).append( "\\b" )

        
        rx.setMinimal( True )
        rx.setPattern( pattern )
        rx.setCaseSensitivity( isCS ? Qt.CaseSensitive : Qt.CaseInsensitive )
        
        pos = mSearchState.forward ? rx.indexIn( text, from -from ) : rx.lastIndexIn( text, to -from )
        
        if  pos != -1 :         start = from +text.left( pos ).toUtf8().length()
             end = start +text.mid( pos, rx.matchedLength() ).toUtf8().length()
            SendScintilla( SCI_SETTARGETSTART, start )
            SendScintilla( SCI_SETTARGETEND, end )

        
        return pos


    def lineNumbersMarginEnabled(self):
        return marginLineNumbers( 0 )


    void pEditor.autoDetectIndent ()
        currText = "\n" + text(); # \n for more simple RegExp
        tabRe = QRegExp ("\n\\t")
        int matchIntex
        matchIntex = tabRe.indexIn (currText)
        if (matchIntex != -1) # Use tabs
            setIndentationsUseTabs (True)
            return

        
        spaceRe = QRegExp ("\n( +)")
        matchIntex = spaceRe.indexIn (currText)
        if (matchIntex != -1) # Use spaces
            setIndentationsUseTabs (False)
            return



    void pEditor.autoDetectEol ()
        currText = text()
        if text().indexOf("\r\n") != -1:
            setEolMode (QsciScintilla.EolWindows)
            return

        if text().indexOf("\n") != -1:
            setEolMode (QsciScintilla.EolUnix)
            return



    def lineNumbersMarginWidth(self):
        return property( "LineNumbersMarginWidth" ).toInt()


    def lineNumbersMarginAutoWidth(self):
        return property( "LineNumbersMarginAutoWidth" ).toBool()


    def setLineNumbersMarginEnabled(self, b ):
        setMarginLineNumbers( 0, b )

    def setLineNumbersMarginAutoWidth(self, b ):
        setProperty( "LineNumbersMarginAutoWidth", b )
        linesChanged.emit()


    def currentLineText(self):
        int line
        int index
        
        getCursorPosition( &line, &index )
        
        return text( line )


    def markerAtLine(self, line, markerId ):
        return QsciScintilla.markersAtLine( line ) & ( 1 << markerId )


    def markerFindPrevious(self, line, markerId ):
        line = QsciScintilla.markerFindPrevious( line, 1 << markerId )
        if  line == -1 :
            line = QsciScintilla.markerFindPrevious( lines() -1, 1 << markerId )
        return line


    def markerFindNext(self, line, markerId ):
        line = QsciScintilla.markerFindNext( line, 1 << markerId )
        if  line == -1 :
            line = QsciScintilla.markerFindNext( 0, 1 << markerId )
        return line

    def convertTabs(self):
        # get original text
        originalText = text()
        # all modifications must believe as only one action
        beginUndoAction()
        # get indent width
         indentWidth = indentationWidth() != 0 ? indentationWidth() : tabWidth()
        # iterate each line
        for ( i = 0; i < lines(); i++ )
            # remember if last line was troncate
            static lastLineWasTroncate = False
            # get current line indent width
            lineIndent = indentation( i )
            # check if need troncate
            t = lineIndent /indentWidth
            r = lineIndent %indentWidth
            if  r != 0 and r != indentWidth :
                r += indentWidth -r
                lineIndent = ( t *indentWidth) +r
                lastLineWasTroncate = True

            elif  lastLineWasTroncate and lineIndent != 0 :
                lastLineW
                
                
                asTroncate = indentation( i +1 ) == lineIndent
                lineIndent    += indentWidth

            # remove indentation
            setIndentation( i, 0 )
            # restore it with possible troncate indentation
            setIndentation( i, lineIndent )

        # end global undo action
        endUndoAction()
        # compare original and newer text
        if  originalText == text() :
            # clear undo buffer
            SendScintilla( SCI_EMPTYUNDOBUFFER )
            # set unmodified
            setModified( False )

    """

_lexerForLanguage = {
"Bash" : QsciLexerBash,
"Batch" : QsciLexerBatch,
"C#" : QsciLexerCSharp,
"C++" : QsciLexerCPP,
"CMake" : QsciLexerCMake,
"CSS" : QsciLexerCSS,
"D" : QsciLexerD,
"Diff" : QsciLexerDiff,
"HTML" : QsciLexerHTML,
"IDL" : QsciLexerIDL,
"Java" : QsciLexerJava,
"Javascript" : QsciLexerJavaScript,
"Lua" : QsciLexerLua,
"Makefile" : QsciLexerMakefile,
"POV" : QsciLexerPOV,
"Perl" : QsciLexerPerl,
"Properties" : QsciLexerProperties,
"Python" : QsciLexerPython,
"Ruby" : QsciLexerRuby,
"SQL" : QsciLexerSQL,
"TeX" : QsciLexerTeX,
"VHDL" : QsciLexerVHDL,
"TCL" : QsciLexerTCL,
"Fortran" : QsciLexerFortran,
"Fortran77" : QsciLexerFortran77,
"Pascal" : QsciLexerPascal,
"PostScript" : QsciLexerPostScript,
"XML" : QsciLexerXML,
"YAML" : QsciLexerYAML,
"Verilog" : QsciLexerVerilog,
"Spice" : QsciLexerSpice,
}

class pChild(mks.abstractchild.pAbstractChild):
    """Text editor widget. Uses QScintilla internally
    TODO rename this class
    """
    def __init__(self, parentObject, filePath):
        mks.abstractchild.pAbstractChild.__init__(self, parentObject, filePath)
        
        # Configure editor
        self.mEditor = QsciScintilla(self)
        self.mEditor.setUtf8( True ) # deal with utf8
        
        self.mEditor.setAttribute( Qt.WA_MacSmallSize )
        self.mEditor.setFrameStyle( QFrame.NoFrame | QFrame.Plain )

        self.setWidget( self.mEditor )
        self.setFocusProxy( self.mEditor )
        """TODO
        # connections
        self.mEditor.cursorPositionChanged.connect(self.cursorPositionChanged)
        """
        self.mEditor.copyAvailable.connect(self.copyAvailableChanged)
        """TODO
        self.mEditor.modificationChanged.connect(self.setWindowModified)
        """
        self.mEditor.modificationChanged.connect(self.modifiedChanged)
        """TODO
        self.mEditor.textChanged.connect(self.contentChanged)
        """
        self.mEditor.textChanged.connect(self._onTextChanged)
        self.mEditor.linesChanged.connect(self._onLinesChanged)
        
        QApplication.clipboard().dataChanged.connect(self._onClipboardDataChanged)
        
        # Load settings
        self.mEditor.setSelectionBackgroundColor( mks.settings.value("Editor/SelectionBackgroundColor"))
        self.mEditor.setSelectionForegroundColor( mks.settings.value("Editor/SelectionForegroundColor"))
        if  mks.settings.value("Editor/DefaultDocumentColours") :
            # set scintilla default colors
            self.mEditor.setColor( mks.settings.value("Editor/DefaultDocumentPen" ))
            self.mEditor.setPaper( mks.settings.value("Editor/DefaultDocumentPaper" ))

        self.mEditor.setFont( mks.settings.value("Editor/DefaultDocumentFont" ))
        # Auto Completion
        self.mEditor.setAutoCompletionCaseSensitivity( mks.settings.value("Editor/AutoCompletionCaseSensitivity"))
        self.mEditor.setAutoCompletionReplaceWord( mks.settings.value("Editor/AutoCompletionReplaceWord" ))
        self.mEditor.setAutoCompletionShowSingle( mks.settings.value("Editor/AutoCompletionShowSingle" ))
        self.mEditor.setAutoCompletionSource( mks.settings.value("Editor/AutoCompletionSource") )
        self.mEditor.setAutoCompletionThreshold( mks.settings.value("Editor/AutoCompletionThreshold") )
        # CallTips
        self.mEditor.setCallTipsBackgroundColor( mks.settings.value("Editor/CallTipsBackgroundColor") )
        self.mEditor.setCallTipsForegroundColor( mks.settings.value("Editor/CallTipsForegroundColor") )
        self.mEditor.setCallTipsHighlightColor( mks.settings.value("Editor/CallTipsHighlightColor") )
        self.mEditor.setCallTipsStyle( mks.settings.value("Editor/CallTipsStyle") )
        self.mEditor.setCallTipsVisible( mks.settings.value("Editor/CallTipsVisible") )
        # Indentation
        self.mEditor.setAutoIndent( mks.settings.value("Editor/AutoIndent") )
        self.mEditor.setBackspaceUnindents( mks.settings.value("Editor/BackspaceUnindents") )
        self.mEditor.setIndentationGuides( mks.settings.value("Editor/IndentationGuides") )
        self.mEditor.setIndentationsUseTabs( mks.settings.value("Editor/IndentationsUseTabs") )
        self.mEditor.setIndentationWidth( mks.settings.value("Editor/IndentationWidth") )
        self.mEditor.setTabIndents( mks.settings.value("Editor/TabIndents") )
        self.mEditor.setTabWidth( mks.settings.value("Editor/TabWidth") )
        self.mEditor.setIndentationGuidesBackgroundColor( mks.settings.value("Editor/IndentationGuidesBackgroundColor") )
        self.mEditor.setIndentationGuidesForegroundColor( mks.settings.value("Editor/IndentationGuidesForegroundColor") )
        # Brace Matching
        self.mEditor.setBraceMatching( mks.settings.value("Editor/BraceMatching") )
        self.mEditor.setMatchedBraceBackgroundColor( mks.settings.value("Editor/MatchedBraceBackgroundColor") )
        self.mEditor.setMatchedBraceForegroundColor( mks.settings.value("Editor/MatchedBraceForegroundColor") )
        self.mEditor.setUnmatchedBraceBackgroundColor( mks.settings.value("Editor/UnmatchedBraceBackgroundColor") )
        self.mEditor.setUnmatchedBraceForegroundColor( mks.settings.value("Editor/UnmatchedBraceForegroundColor") )
        # Edge Mode
        self.mEditor.setEdgeMode( mks.settings.value("Editor/EdgeMode") )
        self.mEditor.setEdgeColor( mks.settings.value("Editor/EdgeColor") )
        self.mEditor.setEdgeColumn( mks.settings.value("Editor/EdgeColumn") )
        # Caret
        self.mEditor.setCaretLineVisible( mks.settings.value("Editor/CaretLineVisible") )
        self.mEditor.setCaretLineBackgroundColor( mks.settings.value("Editor/CaretLineBackgroundColor") )
        self.mEditor.setCaretForegroundColor( mks.settings.value("Editor/CaretForegroundColor") )
        self.mEditor.setCaretWidth( mks.settings.value("Editor/CaretWidth") )
        """
        # Margins
        if  mks.settings.value("Editor/MarginsEnabled") :
            self.mEditor.setMarginsBackgroundColor( mks.settings.value("Editor/MarginsBackgroundColor") )
            self.mEditor.setMarginsForegroundColor( mks.settings.value("Editor/MarginsForegroundColor") )
            self.mEditor.setMarginsFont( mks.settings.value("Editor/MarginsFont") )

        self.mEditor.setMarginLineNumbers( mks.settings.value("Editor/LineNumbersMarginEnabled") )
        self.mEditor.setLineNumbersMarginWidth( mks.settings.value("Editor/LineNumbersMarginWidth") )
        self.mEditor.setLineNumbersMarginAutoWidth( mks.settings.value("Editor/LineNumbersMarginAutoWidth") )
        self.mEditor.setFolding( mks.settings.value("Editor/Folding") )
        self.mEditor.setFoldMarginColors( mks.settings.value("Editor/FoldMarginForegroundColor"), mks.settings.value("Editor/FoldMarginBackgroundColor") )
        """
        
        # Special Characters
        eolConvertor = {'\n': QsciScintilla.EolUnix, '\r\n' : QsciScintilla.EolWindows}
        self.mEditor.setEolMode( eolConvertor[mks.settings.value("Editor/EolMode")] )
        self.mEditor.setEolVisibility( mks.settings.value("Editor/EolVisibility") )
        self.mEditor.setWhitespaceVisibility( mks.settings.value("Editor/WhitespaceVisibility") )
        self.mEditor.setWrapMode( mks.settings.value("Editor/WrapMode") )
        self.mEditor.setWrapVisualFlags( mks.settings.value("Editor/EndWrapVisualFlag"), mks.settings.value("Editor/StartWrapVisualFlag"), mks.settings.value("Editor/WrappedLineIndentWidth") )
        
        self.mEditor.setLexer( self._lexerForFileName( filePath ) )

        # open file
        #locked = self.blockSignals( True )
        try:
            with open(filePath, 'r') as f:
                self._setFilePath(filePath)
                
                self.mEditor.setText( f.read() )
                self._onLinesChanged()
                self.mEditor.setModified( False )
                
                """TODO
                # convert tabs if needed
                if  mks.monkeystudio.convertTabsUponOpen() :
                    convertTabs()
                #autodetect indent, need
                if  mks.monkeystudio.autoDetectIndent() :
                    autoDetectIndent ()
                #autodetect eol, need
                if  mks.monkeystudio.autoDetectEol() :
                    autoDetectEol()
                # make backup if needed
                if  mks.monkeystudio.createBackupUponOpen() :
                    shutil.copyfileobj(self.filePath(), self.filePath() + '.bak')
                # convert eol
                if  mks.monkeystudio.autoEolConversion() :
                    convertEols( eolMode() )
                """
        except IOError, ex:  # exception in constructor
            self.deleteLater()  # make sure C++ object deleted
            raise ex
        
        #TODO self.fileOpened.emit()

    def _onTextChanged(self):
        self.undoAvailableChanged.emit( self.mEditor.isUndoAvailable() )
        self.redoAvailableChanged.emit( self.mEditor.isRedoAvailable() )

    def _onLinesChanged(self):
        l = len(str(self.mEditor.lines()))
        if l != 0:
            l += 1
        self.mEditor.setMarginWidth( 0, '0' * l )
    
    def _onClipboardDataChanged(self):
        self.pasteAvailableChanged.emit( self.isPasteAvailable() )
    
    def _lexerForFileName(self, fileName ):
        for language in _lexerForLanguage.keys():
            if  QDir.match( mks.settings.value("Editor/Assotiations/" + language), fileName ) :
                lexerClass =  _lexerForLanguage[language]
                return lexerClass()
        else:
            return None
    
    """TODO
    def language(self):
        # return the editor language
        if  self.mEditor.lexer() :
            return self.mEditor.lexer().language()

        # return nothing
        return ''
    
    def fileBuffer(self):
        return self.mEditor.text()
    
    def cursorPosition(self):
        row, col = self.mEditor.getCursorPosition()
        return QPoint(row + 1, col)
    
    def editor(self):
        return self.mEditor
    """
    
    def isModified(self):
        return self.mEditor.isModified()
    
    """
    def invokeSearch ():
        '''MonkeyCore.searchWidget().showSearchFile ();'''
        #TODO resolve
        pass
    """
    def isUndoAvailable(self):
        return self.mEditor.isUndoAvailable()

    def undo(self):
        self.mEditor.undo()

    def isRedoAvailable(self):
        return self.mEditor.isRedoAvailable()

    def redo(self):
        self.mEditor.redo()

    def cut(self):
        self.mEditor.cut()

    def copy(self):
        self.mEditor.copy()

    def isCopyAvailable(self):
        lineFrom, indexFrom, lineTo, indexTo = self.mEditor.getSelection()
        return lineFrom != lineTo or indexFrom != indexTo
    
    def paste(self):
        self.mEditor.paste()
    
    def isPasteAvailable(self):
        return bool(QApplication.clipboard().text())
    
    """TODO
    def goTo(self):
        assert(0) # TODO resolve name conflict
        line, col = self.getCursorPosition()
        gotoLine, ok = QInputDialog.getInteger( self, self.tr( "Go To Line..." ), self.tr( "Enter the line you want to go:" ), line +1, 1, self.lines(), 1)
        
        if  ok :
            self.setCursorPosition( gotoLine -1, 0 )
            self.setFocus()
    
    def goTo(self, pos, selectionLength ):
        assert(0) # TODO resolve name conflict
        column = pos.x()
        line = pos.y()
        
        self.mEditor.setCursorPosition( line, column )
        self.mEditor.setSelection( line, column, line, column +selectionLength )
        self.mEditor.ensureLineVisible( line )
        self.mEditor.setFocus()
    """
    """TODO
    def isGoToAvailable(self):
        return True

    def isPrintAvailable(self):
        return True
    """
    
    def saveFile(self):
        if  not self.isModified() :
            return True
        
        dirPath = os.path.dirname(self.filePath())
        if  not os.path.exists(dirPath):
            try:
                os.mkdir(dirPath)
            except OSError:
                mks.monkeystudio.messageManager().appendMessage( \
                        self.tr( "Cannot create directory '%s'. Error '%s'" % (dirPath, error))) # todo fix
                return False
        
        try:
            f = open(self.filePath(), 'w')
        except IOError:
            mks.monkeystudio.messageManager().appendMessage( \
                    self.tr( "Cannot write to file '%s'. Error '%s'" % (dirPath, error))) # todo fix
            return False
        
        try:
            f.write(self.mEditor.text())
        finally:
            f.close()
        
        self.mEditor.setModified(False)
    
    """TODO
    def backupFileAs(self, filePath ):
        shutil.copyfileobj(self.filePath(), fileName)
    
    def closeFile(self):
        self.mEditor.clear()
        self.mEditor.setModified( False )
        self.setFilePath( '' )
        self.fileClosed.emit()
    
    def reload(self):
        self.openFile(self.filePath())
        self.fileReloaded.emit()
    
    def print_(self, quickPrint):
        # get printer
        p = QsciPrinter()
        
        # set wrapmode
        p.setWrapMode( PyQt4.Qsci.WrapWord )

        if  quickPrint:
            # check if default printer is set
            if  p.printerName().isEmpty() :
                mks.monkeycore.messageManager().appendMessage( \
                    tr( "There is no default printer, set one before trying quick print" ) )
                return
            
            # print and return
            p.printRange( self.mEditor )
            return
        
        d = QPrintDialog (p) # printer dialog

        if d.exec_(): # if ok
            # print
            f = -1
            t = -1
            if  d.printRange() == QPrintDialog.Selection:
                f, unused, t, unused1 = getSelection()
            p.printRange( self.mEditor, f, t )
    
    def printFile(self):
        self.print_(False)

    def quickPrintFile(self):
        self.print_(True)
"""