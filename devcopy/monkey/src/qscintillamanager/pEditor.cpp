#include "pEditor.h"
#include "pMonkeyStudio.h"
#include "qscintillamanager/qSciShortcutsManager.h"
#include "coremanager/MonkeyCore.h"

#include <widgets/pQueuedMessageToolBar.h>
#include <qsciprinter.h>

#include <QKeyEvent>
#include <QApplication>
#include <QClipboard>
#include <QFileInfo>
#include <QTextStream>
#include <QInputDialog>
#include <QPrintDialog>
#include <QDir>
#include <QDateTime>
#include <QTextCodec>
#include <QRegExp>
#include <QDebug>

#define USE_QSCINTILLA_SEARCH_ENGINE 0

bool pEditor.mPasteAvailableInit = False
bool pEditor.mPasteAvailable = False

pEditor.pEditor( QWidget* p )
    : QsciScintilla( p )
     mPixSize = QSize( 16, 16 )
    # register image for bookmarks
    markerDefine( QPixmap( ":/editor/bookmark.png" ).scaled( mPixSize ), mdBookmark )
    
    # deal with utf8
    setUtf8( True )

    # connection
    self.linesChanged.connect(self.linesChanged)
    self.copyAvailable.connect(self.setCopyAvailable)
    self.cursorPositionChanged.connect(self.cursorPositionChanged)
    self.textChanged.connect(self.textChanged)
    QApplication.clipboard().dataChanged.connect(self.clipboardDataChanged)

    # init pasteAvailable
    if  not mPasteAvailableInit :
        mPasteAvailableInit = True
        mPasteAvailable = not QApplication.clipboard().text().isEmpty()

    
    # init qscishortcutsmanager if needed
    SendScintilla( QsciScintillaBase.SCI_CLEARALLCMDKEYS )
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_TAB, SCI_TAB)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_ESCAPE, SCI_CANCEL)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_RETURN, SCI_NEWLINE)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_DOWN, SCI_LINEDOWN)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_UP, SCI_LINEUP)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_RIGHT, SCI_CHARRIGHT)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_LEFT, SCI_CHARLEFT)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_BACK, SCI_DELETEBACK)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_PRIOR, SCI_PAGEUP)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_NEXT, SCI_PAGEDOWN)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_HOME, SCI_VCHOME)
    SendScintilla( QsciScintillaBase.SCI_ASSIGNCMDKEY, SCK_END, SCI_LINEEND)

    # By default control characters don't do anything (rather than insert the
    # control character into the text). (c) Phil
    for (k = 'A'; k <= 'Z'; ++k)
    SendScintilla(QsciScintillaBase.SCI_ASSIGNCMDKEY,
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


def setLineNumbersMarginWidth(self, i ):
    j = i
    if  i != 0 :
        j++

    setProperty( "LineNumbersMarginWidth", i )
    setMarginWidth( 0, QString().fill( '0', j ) )


def setLineNumbersMarginAutoWidth(self, b ):
    setProperty( "LineNumbersMarginAutoWidth", b )
    linesChanged.emit()


def linesChanged(self):
    if  lineNumbersMarginAutoWidth() :
        setLineNumbersMarginWidth( QString.number( lines() ).length() )


def copyAvailable(self):
    return mCopyAvailable


def canPaste(self):
    return mPasteAvailable


def cursorPosition(self):
    return mCursorPosition


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


def setCopyAvailable(self, b ):
    mCopyAvailable = b


def cursorPositionChanged(self, l, p ):
    mCursorPosition = QPoint( p, l )
    cursorPositionChanged.emit( mCursorPosition )


def textChanged(self):
    undoAvailable.emit( isUndoAvailable() )
    redoAvailable.emit( isRedoAvailable() )


def clipboardDataChanged(self):
    mPasteAvailable = not QApplication.clipboard().text().isEmpty()
    pasteAvailable.emit( canPaste() )


def openFile(self, fileName, codec ):
    '''if  isModified() :
        return False;'''

    QApplication.setOverrideCursor( Qt.WaitCursor )
    
    # open file
    QFile f( fileName )
    if  not f.open( QFile.ReadOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Cannot read file %1:\n%2." ).arg( fileName ).arg( f.errorString() ) )
        QApplication.restoreOverrideCursor()
        return False


    # remember filename
    setProperty( "fileName", fileName )
    setProperty( "codec", codec )

    # set lexer and apis
    setLexer( pMonkeyStudio.lexerForFileName( fileName ) )

    # set properties
    pMonkeyStudio.setEditorProperties( self )

    # load file
    c = QTextCodec.codecForName( codec.toUtf8() )
    datas = c.toUnicode( f.readAll() )
    setText( datas )
    setModified( False )

    # convert tabs if needed
    if  pMonkeyStudio.convertTabsUponOpen() :
        convertTabs()
    
    #autodetect indent, need
    if  pMonkeyStudio.autoDetectIndent() :
        autoDetectIndent ()

    
    #autodetect eol, need
    if  pMonkeyStudio.autoDetectEol() :
        autoDetectEol()

    
    # make backup if needed
    if  pMonkeyStudio.createBackupUponOpen() :
        makeBackup()

    # convert eol
    if  pMonkeyStudio.autoEolConversion() :
        convertEols( eolMode() )
    
    QApplication.restoreOverrideCursor()
    
    return True


def saveFile(self, s ):
    if  not isModified() :
        return True

    # get filename
    fn = s
    if  s.isEmpty() :
        fn = property( "fileName" ).toString()
    # get path
    fp = QFileInfo( fn ).path()

    # filename
    QFile f( fn )
    # filename dir
    QDir d
    # create bak folder
    if  not d.exists( fp ) :
        if  not d.mkpath( fp ) :
            return False

    # set correct path
    d.setPath( fp )
    # try open file to write in
    if  not f.open( QFile.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Cannot write file %1:\n%2." ).arg( fn ).arg( f.errorString() ) )
        return False


    # writing file
    QApplication.setOverrideCursor( Qt.WaitCursor )
    
    f.resize( 0 )
    c = QTextCodec.codecForName( property( "codec" ).toString().toUtf8() )
    ok = f.write( c.fromUnicode( text() ) ) != -1

    if  ok :
        setModified( False )
        setProperty( "fileName", fn )

    
    QApplication.restoreOverrideCursor()

    return ok


def saveBackup(self, s ):
    # if not filename, cancel
    if  s.isEmpty() :
        return False

    
    # get path
    fp = QFileInfo( s ).path()

    # file
    QFile f( s )
    
    # filename dir
    QDir d
    # create bak folder
    if  not d.exists( fp ) :
        if  not d.mkpath( fp ) :
            return False


    
    QApplication.setOverrideCursor( Qt.WaitCursor )
    
    # set correct path
    d.setPath( fp )
    
    # try open file to write in
    if  not f.open( QFile.WriteOnly ) :
        MonkeyCore.messageManager().appendMessage( tr( "Cannot write file %1:\n%2." ).arg( s ).arg( f.errorString() ) )
        QApplication.restoreOverrideCursor()
        return False

    
    f.resize( 0 )
    c = QTextCodec.codecForName( property( "codec" ).toString().toUtf8() )
    ok = f.write( c.fromUnicode( text() ) ) != -1
    
    QApplication.restoreOverrideCursor()

    return ok


def closeFile(self):
    clear()
    setModified( False )

    # clear filename
    setProperty( "fileName", QVariant() )


def print(self, b ):
    # get printer
    QsciPrinter p

    # set wrapmode
    p.setWrapMode( WrapWord )

    # if quick print
    if  b :
        # check if default printer is set
        if  p.printerName().isEmpty() :
            MonkeyCore.messageManager().appendMessage( tr( "There is no default printer, set one before trying quick print" ) )
            return

        
        # print and return
        p.printRange( self )
        return


    # printer dialog
    QPrintDialog d( &p )

    # if ok
    if  d.exec() :
        # print
        f = -1, t = -1, i
        if  d.printRange() == QPrintDialog.Selection :
            getSelection( &f, &i, &t, &i )
        p.printRange( self, f, t )



def quickPrint(self):
    print( True )


def selectNone(self):
    selectAll( False )


def invokeGoToLine(self):
    bool ok
    int line, column, gotoLine
    
    getCursorPosition( &line, &column )
    gotoLine = QInputDialog.getInteger( self, tr( "Go To Line..." ), tr( "Enter the line you want to go:" ), line +1, 1, lines(), 1, &ok )
    
    if  ok :
        setCursorPosition( gotoLine -1, 0 )
        setFocus()



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
            lastLineWasTroncate = indentation( i +1 ) == lineIndent
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



def makeBackup(self):
    # get filename
     dn = ".bak"
    QFileInfo f( property( "fileName" ).toString() )
     s = f.path().append( "/" ).append( dn ).append( "/" ).append( f.fileName() ).append( "." ).append( QDateTime.currentDateTime().toString( "yyyyMMdd_hhmmss" ) )

    # cancel if filename doesn't exists
    if  not f.exists() :
        return

    # filename dir
    QDir d( f.path() )

    # create bak folder
    if  not d.exists( ".bak" ) :
        if  not d.mkdir( ".bak" ) :
            return

    QFile.copy( f.absoluteFilePath(), s )

