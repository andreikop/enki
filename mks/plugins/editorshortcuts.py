"""
editorshortcuts --- Manages QScintilla shortcuts
================================================

Contains editor dialog and functionality for load and save the shortcuts
"""
from PyQt4.QtCore import QObject
from PyQt4.Qsci import QsciScintilla as qsci

from mks.core.core import core

def tr(s):
    return s

ACTIONS = (\
(qsci.SCI_SELECTALL, 'mEdit/mSelection/aSelectAll', tr('Select All'), 'Ctrl+A'),
(qsci.SCI_LINEDOWNEXTEND, 'mEdit/mSelection/aExtendSelectionDownOneLine', tr('Extend selection down one line'), 'Shift+Down'),
(qsci.SCI_LINEDOWNRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionDownOneLine', tr('Extend rectangular selection down one line'), 'Alt+Shift+Down'),
(qsci.SCI_LINEUPEXTEND, 'mEdit/mSelection/aExtendSelectionUp', tr('Extend selection up'), 'Shift+Up'),
(qsci.SCI_LINEUPRECTEXTEND, 'mEdit/mSelection/aExtendSelectionUpOneLine', tr('Extend selection up one line'), 'Alt+Shift+Up'),
(qsci.SCI_PARADOWNEXTEND, 'mEdit/mSelection/aExtendSelectionUpOneParagraph', tr('Extend selection up one paragraph'), 'Ctrl+Alt+]'),
(qsci.SCI_CHARLEFTEXTEND, 'mEdit/mSelection/aExtendSelectionLeftOneCharacter', tr('Extend selection left one character'), 'Shift+Left'),
(qsci.SCI_CHARLEFTRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionLeftOneCharacter', tr('Extend rectangular selection left one character'), 'Alt+Shift+Left'),
(qsci.SCI_CHARRIGHTEXTEND, 'mEdit/mSelection/aExtendSelectionRightOneCharacter', tr('Extend selection right one character'), 'Shift+Right'),
(qsci.SCI_CHARRIGHTRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionRightOneCharacter', tr('Extend rectangular selection right one character'), 'Alt+Shift+Right'),
(qsci.SCI_PARAUPEXTEND, 'mEdit/mSelection/aExtendSelectionDownOneParagraph', tr('Extend selection down one paragraph'), 'Ctrl+Alt+['),
(qsci.SCI_WORDLEFTEXTEND, 'mEdit/mSelection/aExtendSelectionLeftOneWord', tr('Extend selection left one word'), 'Ctrl+Alt+Left'),
(qsci.SCI_WORDRIGHTEXTEND, 'mEdit/mSelection/aExtendSelectionRightOneWord', tr('Extend selection right one word'), 'Ctrl+Alt+Right'),
(qsci.SCI_WORDLEFTENDEXTEND, 'mEdit/mSelection/aExtendSelectionLeftOneWordLeft', tr('Extend selection left one word left'), ''),
(qsci.SCI_WORDRIGHTENDEXTEND, 'mEdit/mSelection/aExtendSelectionRightOneWordEnd', tr('Extend selection right one word end'), ''),
(qsci.SCI_WORDPARTLEFTEXTEND, 'mEdit/mSelection/aExtendSelectionLeftOneWordPart', tr('Extend selection left one word part '), 'Ctrl+Alt+/'),
(qsci.SCI_WORDPARTRIGHTEXTEND, 'mEdit/mSelection/aExtendSelectionRightOneWordPart', tr('Extend selection right one word part'), 'Ctrl+Alt+\\'),
(qsci.SCI_HOMEEXTEND, 'mEdit/mSelection/aExtendSelectionToLineStart', tr('Extend selection to line start'), ''),
(qsci.SCI_HOMERECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionToLineStart', tr('Extend rectangular selection to line start'), ''),
(qsci.SCI_HOMEDISPLAYEXTEND, 'mEdit/mSelection/aExtendSelectionStartOfDisplayedLine', tr('Extend selection start of displayed line'), ''),
(qsci.SCI_HOMEWRAPEXTEND, 'mEdit/mSelection/aExtendSelectionOnHomeWrap', tr('Extend selection on home wrap'), ''),
(qsci.SCI_VCHOMERECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionToFirtsVCInLine', tr('Extend rectangular selection to firts VC in line'), 'Alt+Shift+Home'),
(qsci.SCI_VCHOMEWRAPEXTEND, 'mEdit/mSelection/aExtendSelectionVCHomeWrap', tr('Extend selection VC Home wrap'), ''),
(qsci.SCI_LINEENDEXTEND, 'mEdit/mSelection/aExtendSelectionToEndOfLine', tr('Extend selection to end of line'), 'Shift+End'),
(qsci.SCI_LINEENDRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionToEndOfLine', tr('Extend rectangular selection to end of line'), 'Alt+Shift+End'),
(qsci.SCI_LINEENDDISPLAYEXTEND, 'mEdit/mSelection/aExtendSelectionToEndOfDisplayedLine', tr('Extend selection to end of displayed line'), ''),
(qsci.SCI_LINEENDWRAPEXTEND, 'mEdit/mSelection/aExtendSelectionToLineEndWrap', tr('Extend selection to line end wrap'), ''),
(qsci.SCI_DOCUMENTSTARTEXTEND, 'mEdit/mSelection/aExtendSelectionToDocumentStart', tr('Extend selection to document start'), 'Ctrl+Alt+Home'),
(qsci.SCI_DOCUMENTENDEXTEND, 'mEdit/mSelection/aExtendSelectionToDocumentEnd', tr('Extend selection to document end'), 'Ctrl+Alt+End'),
(qsci.SCI_PAGEDOWNEXTEND, 'mEdit/mSelection/aExtendSelectionDownOnePage', tr('Extend selection down one page'), 'Shift+PgDown'),
(qsci.SCI_PAGEDOWNRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionDownOnePage', tr('Extend rectangular selection down one page'), 'Alt+Shift+PgDown'),
(qsci.SCI_STUTTEREDPAGEUPEXTEND, 'mEdit/mSelection/aExtendSelectionUpOnePageStuttered', tr('Extend selection up one page stuttered'), ''),
(qsci.SCI_PAGEUPEXTEND, 'mEdit/mSelection/aExtendSelectionUpOnePage', tr('Extend selection up one page'), 'Shift+PgUp'),
(qsci.SCI_PAGEUPRECTEXTEND, 'mEdit/mSelection/aExtendRectangularSelectionUpOnePage', tr('Extend rectangular selection up one page'), 'Alt+Shift+PgUp'),
(qsci.SCI_STUTTEREDPAGEDOWNEXTEND, 'mEdit/mSelection/aExtendSelectionDownOnePageStuttered', tr('Extend selection down one page stuttered'), ''),
\
(qsci.SCI_LINEDOWN, 'mEdit/mNavigation/aLineDown', tr('Down'), ''),
(qsci.SCI_LINEUP, 'mEdit/mNavigation/aLineUp', tr('Up'), ''),
(qsci.SCI_CHARRIGHT, 'mEdit/mNavigation/aRight', tr('Right'), ''),
(qsci.SCI_CHARRIGHT, 'mEdit/mNavigation/aLeft', tr('Left'), ''),
(qsci.SCI_PAGEUP, 'mEdit/mNavigation/aPageUp', tr('Page Up'), ''),
(qsci.SCI_PAGEDOWN, 'mEdit/mNavigation/aPageDown', tr('Page Down'), ''),
(qsci.SCI_LINESCROLLDOWN, 'mEdit/mNavigation/aScrollViewDownOneLine', tr('Scroll view down one line'), 'Ctrl+Down'),
(qsci.SCI_LINESCROLLUP, 'mEdit/mNavigation/aScrollViewUpOneLine', tr('Scroll view up one line'), 'Ctrl+Up'),
(qsci.SCI_PARADOWN, 'mEdit/mNavigation/aMoveDownOneParagraph', tr('Move down one paragraph'), 'Ctrl+]'),
(qsci.SCI_PARAUP, 'mEdit/mNavigation/aMoveDownOneParagraph', tr('Move down one paragraph'), 'Ctrl+['),
(qsci.SCI_WORDLEFT, 'mEdit/mNavigation/aMoveLeftOneWord', tr('Move left one word'), 'Ctrl+Left'),
(qsci.SCI_WORDRIGHT, 'mEdit/mNavigation/aMoveRightOneWord', tr('Move right one word'), 'Ctrl+Right'),
(qsci.SCI_WORDLEFTEND, 'mEdit/mNavigation/aMoveLeftOneWordEnd', tr('Move left one word end'), ''),
(qsci.SCI_WORDRIGHTEND, 'mEdit/mNavigation/aMoveRightOneWordEnd', tr('Move right one word end'), ''),
(qsci.SCI_WORDPARTLEFT, 'mEdit/mNavigation/aMoveLeftOneWordPart', tr('Move left one word part'), 'Ctrl+/'),
(qsci.SCI_WORDPARTRIGHT, 'mEdit/mNavigation/aMoveRightOneWordPart', tr('Move right one word part'), 'Ctrl+\\'),
(qsci.SCI_HOME, 'mEdit/mNavigation/aMoveToLineStart', tr('Move to line start'), ''),
(qsci.SCI_HOMEDISPLAY, 'mEdit/mNavigation/aMoveToStartOfDisplayedLine', tr('Move to start of displayed line'), 'Alt+Home'),
(qsci.SCI_HOMEWRAP, 'mEdit/mNavigation/aHomeWrap', tr('Home wrap'), ''),
(qsci.SCI_VCHOME, 'mEdit/mNavigation/aMoveToFirsstVCInLine', tr('Move to first VC in line'), ''),
(qsci.SCI_VCHOMEEXTEND, 'mEdit/mNavigation/aExtendSelectionToFirstVCInLine', tr('Extend selection to first VC in line'), 'Shift+Home'),
(qsci.SCI_VCHOMEWRAP, 'mEdit/mNavigation/aVCHomeWrap', tr('VC Home wrap'), ''),
(qsci.SCI_LINEEND, 'mEdit/mNavigation/aMoveToEndOfLine', tr('Move to end of line'), ''),
(qsci.SCI_LINEENDDISPLAY, 'mEdit/mNavigation/aMoveToEndDisplayedLine', tr('Move to end displayed line'), 'Alt+End'),
(qsci.SCI_LINEENDWRAP, 'mEdit/mNavigation/aMoveToLineEndWrap', tr('Move to line end wrap'), ''),
(qsci.SCI_DOCUMENTSTART, 'mEdit/mNavigation/aMoveToDocumentStart', tr('Move to document start'), 'Ctrl+Home'),
(qsci.SCI_DOCUMENTEND, 'mEdit/mNavigation/aMoveToDocumentEnd', tr('Move to document end'), 'Ctrl+End'),
(qsci.SCI_PAGEUP, 'mEdit/mNavigation/aMoveUpOnePage', tr('Move up one page'), 'PgUp'),
(qsci.SCI_PAGEDOWN, 'mEdit/mNavigation/aMoveDownOnePage', tr('Move down one page'), 'PgDown'),
(qsci.SCI_STUTTEREDPAGEUP, 'mEdit/mNavigation/aMoveUpOnePageStuttered', tr('Move up one page stuttered'), ''),
(qsci.SCI_STUTTEREDPAGEDOWN, 'mEdit/mNavigation/aMoveDownOnePageStuttered', tr('Move down one page stuttered'), ''),
(qsci.SCI_UNDO, 'mEdit/mEdit/aUndo', tr('Undo'), 'Ctrl+Z'),
(qsci.SCI_REDO, 'mEdit/mEdit/aRedo', tr('Redo'), 'Ctrl+Y'),
(qsci.SCI_DELETEBACK, 'mEdit/mEdit/aBackspace', tr('Backspace'), ''),
(qsci.SCI_DELETEBACKNOTLINE, 'mEdit/mEdit/aBackspaceNotALine', tr('Backspace not a line'), ''),
(qsci.SCI_DELWORDLEFT, 'mEdit/mEdit/aDeletePreviousWord', tr('Delete previous word'), 'Ctrl+Backspace'),
(qsci.SCI_DELWORDRIGHT, 'mEdit/mEdit/aDeleteNextWord', tr('Delete next word'), 'Ctrl+Del'),
(qsci.SCI_DELLINELEFT, 'mEdit/mEdit/aDeleteLineTpLeft', tr('Delete line tp left'), 'Ctrl+Alt+Backspace'),
(qsci.SCI_DELLINERIGHT, 'mEdit/mEdit/aDeleteLineToRight', tr('Delete line to right'), 'Ctrl+Alt+Del'),
(qsci.SCI_LINEDELETE, 'mEdit/mEdit/aDeleteLine', tr('Delete line'), 'Ctrl+Alt+L'),
(qsci.SCI_LINECUT, 'mEdit/mEdit/aCutLine', tr('Cut line'), 'Ctrl+L'),
(qsci.SCI_LINECOPY, 'mEdit/mEdit/aCopyLine', tr('Copy line'), 'Ctrl+Alt+T'),
(qsci.SCI_LINETRANSPOSE, 'mEdit/mEdit/aSwapCurrentAndPreviousLine', tr('Swap current and previous line'), 'Ctrl+T'),
(qsci.SCI_LINEDUPLICATE, 'mEdit/mEdit/aDuplicateLine', tr('Duplicate line'), ''),
(qsci.SCI_LOWERCASE, 'mEdit/mEdit/aToLowerCase', tr('To lower case'), 'Ctrl+U'),
(qsci.SCI_UPPERCASE, 'mEdit/mEdit/aToUpperCase', tr('To upper case'), 'Ctrl+Alt+U'),
(qsci.SCI_EDITTOGGLEOVERTYPE, 'mEdit/mEdit/aEditToggleOverType', tr('Edit toggle over type'), 'Ins'),
(qsci.SCI_FORMFEED, 'mEdit/mEdit/aFormfeed', tr('Formfeed'), ''),
(qsci.SCI_TAB, 'mEdit/mEdit/aIndent', tr('Indent'), ''),
(qsci.SCI_BACKTAB, 'mEdit/mEdit/aDeleteOneIndent', tr('Delete one indent'), 'Shift+Tab'),
(qsci.SCI_SELECTIONDUPLICATE, 'mEdit/mEdit/aDuplicateSelection', tr('Duplicate selection'), 'Ctrl+D'),
(qsci.SCI_CLEAR, 'mEdit/mEdit/aDelete', tr('Delete'), 'Del'),
(qsci.SCI_NEWLINE, 'mEdit/mEdit/aNewLine', tr('New line'), ''),
(qsci.SCI_ZOOMIN, 'mView/mZoom/aZoomIn', tr('Zoom In'), 'Ctrl++'),
(qsci.SCI_ZOOMOUT, 'mView/mZoom/aZoomOut', tr('Zoom Out'), 'Ctrl+-'),
(qsci.SCI_SETZOOM, 'mView/mZoom/aSetZoom', tr('Set Zoom'), 'Ctrl+/'),
(qsci.SCI_MARKERADD, 'mEdit/mBookmarks/aSetBookmark', tr('Set bookmark'), ''),
(qsci.SCI_MARKERDELETEALL, 'mEdit/mBookmarks/aDeleteAllBookmarks', tr('Delete all bookmarks'), ''),
(qsci.SCI_MARKERPREVIOUS, 'mEdit/mBookmarks/aPreviousBookmark', tr('Previous bookmark'), ''),
(qsci.SCI_MARKERNEXT, 'mEdit/mBookmarks/aNextBookmark', tr('Next bookmark'), ''),
)

_MENUS = (\
('mEdit/mBookmarks', tr('Bookmarks')),
('mEdit/mSelection', tr('Selection')),
('mEdit/mNavigation', tr('Navigation')),
('mEdit/mEdit', tr('Edit')),
('mView/mZoom', tr('Zoom')),
)

class EditorShortcuts:
    def __init__(self):
        self._createdActions = []
        self._createdMenus = []
        model = core.actionModel()
        
        for menu in _MENUS:
            menuObj = model.addMenu(menu[0], menu[1])
            menuObj.setEnabled(False)
            self._createdMenus.append(menuObj)
        
        for action in ACTIONS:
            actObject = model.addAction(action[1], action[2])
            if action[3]:
                model.setDefaultShortcut(actObject, action[3])
            actObject.setData(action[0])
            actObject.setEnabled(False)
            actObject.triggered.connect(self.onAction)
            self._createdActions.append(actObject)
        
        core.workspace().currentDocumentChanged.connect(self.onCurrentDocumentChanged)

    def __del__(self):
        model = core.actionModel()
        for actObject in self._createdActions:
            model.removeAction(actObject)

        for menuObj in self._createdMenus:
            model.removeMenu(menuObj)

    def onCurrentDocumentChanged(self, oldDocument, document):
        for actObject in self._createdActions:
            actObject.setEnabled(document is not None)
        for menuObject in self._createdMenus:
            menuObject.setEnabled(document is not None)
        self._currentDocument = document
    
    def onAction(self):
        action = self._currentDocument.sender()
        self._currentDocument.qscintilla.SendScintilla(action.data().toInt()[0])
