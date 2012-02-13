"""
editorshortcuts --- Manages QScintilla shortcuts
================================================

Creates QActions, which represent QScintilla actions.

Sends commands to the current editor, when action was triggered
"""

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QAction, QApplication, QIcon
from PyQt4.Qsci import QsciScintilla as qsci

from mks.core.core import core

def tr(text):  # pylint: disable=C0103
    """ Stub for translation procedure
    """
    return text

MKS_TOGGLE_BOOKMARK = -1
MKS_NEXT_BOOKMARK = -2
MKS_PREV_BOOKMARK = -3

MKS_PASTE = -4

_ACTIONS = (\
(qsci.SCI_SELECTALL, 'mEdit/mSelection/aSelectAll', tr('Select All'), 'Ctrl+A', ''),
(qsci.SCI_LINEDOWNEXTEND, 'mEdit/mSelection/aDownOneLine', tr('Extend Down'), 'Shift+Down', ''),
(qsci.SCI_LINEUPEXTEND, 'mEdit/mSelection/aUp', tr('Extend Up'), 'Shift+Up', ''),
(qsci.SCI_CHARLEFTEXTEND, 'mEdit/mSelection/aLeft', tr('Extend Left'), 'Shift+Left', ''),
(qsci.SCI_CHARRIGHTEXTEND, 'mEdit/mSelection/aRight', tr('Extend Right'), 'Shift+Right', ''),
\
(qsci.SCI_DOCUMENTSTARTEXTEND, 'mEdit/mSelection/mDocument/aToStart', tr('Extend to start'), 'Ctrl+Alt+Home', ''),
(qsci.SCI_DOCUMENTENDEXTEND, 'mEdit/mSelection/mDocument/aToEnd', tr('Extend to end'), 'Ctrl+Alt+End', ''),
\
(qsci.SCI_PAGEDOWNEXTEND, 'mEdit/mSelection/mPage/aDownOnePage', tr('Down'), 'Shift+PgDown', ''),
(qsci.SCI_STUTTEREDPAGEUPEXTEND, 'mEdit/mSelection/mPage/aUpOnePageStuttered', tr('Up stuttered'), '', ''),
(qsci.SCI_PAGEUPEXTEND, 'mEdit/mSelection/mPage/aUpOnePage', tr('Up'), 'Shift+PgUp', ''),
(qsci.SCI_STUTTEREDPAGEDOWNEXTEND, 'mEdit/mSelection/mPage/aDownOnePageStuttered', tr('Down stuttered'), '', ''),
\
(qsci.SCI_HOMEEXTEND, 'mEdit/mSelection/mLine/aStart', tr('To start'), '', ''),
(qsci.SCI_HOMEDISPLAYEXTEND, 'mEdit/mSelection/mLine/aStartOfDisplayed', tr('To start of displayed'), '', ''),
(qsci.SCI_HOMEWRAPEXTEND, 'mEdit/mSelection/mLine/aOnHomeWrap', tr('Home wrap'), '', ''),
(qsci.SCI_VCHOMEWRAPEXTEND, 'mEdit/mSelection/mLine/aVCHomeWrap', tr('Visible character Home wrap'), '', ''),
(qsci.SCI_VCHOMEEXTEND, 'mEdit/mSelection/mLine/aToFirstVC', tr('First visible character'), 'Shift+Home', ''),
(qsci.SCI_LINEENDEXTEND, 'mEdit/mSelection/mLine/aToEnd', tr('End'), 'Shift+End', ''),
(qsci.SCI_LINEENDDISPLAYEXTEND, 'mEdit/mSelection/mLine/aToEndOfDisplayed', tr('End of displayed'), '', ''),
(qsci.SCI_LINEENDWRAPEXTEND, 'mEdit/mSelection/mLine/aEndWrap', tr('End wrap'), '', ''),
\
(qsci.SCI_PARAUPEXTEND, 'mEdit/mSelection/mParagraph/aUp', tr('Up'), 'Ctrl+Alt+[', ''),
(qsci.SCI_PARADOWNEXTEND, 'mEdit/mSelection/mParagraph/aDown', tr('Down'), 'Ctrl+Alt+]', ''),
\
(qsci.SCI_WORDLEFTEXTEND, 'mEdit/mSelection/mWord/aLeft', tr('Left'), 'Ctrl+Shift+Left', ''),
(qsci.SCI_WORDRIGHTEXTEND, 'mEdit/mSelection/mWord/aRight', tr('Right'), 'Ctrl+Shift+Right', ''),
(qsci.SCI_WORDLEFTENDEXTEND, 'mEdit/mSelection/mWord/aLeftEnd', tr('Left end'), '', ''),
(qsci.SCI_WORDRIGHTENDEXTEND, 'mEdit/mSelection/mWord/aRightEnd', tr('Right end'), '', ''),
(qsci.SCI_WORDPARTLEFTEXTEND, 'mEdit/mSelection/mWord/aLeftPart', tr('Left part '), 'Ctrl+Alt+/', ''),
(qsci.SCI_WORDPARTRIGHTEXTEND, 'mEdit/mSelection/mWord/aRightPart', tr('Right part'), 'Ctrl+Alt+\\', ''),
\
(qsci.SCI_LINEDOWNRECTEXTEND, 'mEdit/mSelection/mRectangular/aDownOneLine', tr('Down one line'), 'Alt+Shift+Down', ''),
(qsci.SCI_CHARLEFTRECTEXTEND, 'mEdit/mSelection/mRectangular/aLeftOneCharacter', 
                                                    tr('Left one character'), 'Alt+Shift+Left', ''),
(qsci.SCI_CHARRIGHTRECTEXTEND, 'mEdit/mSelection/mRectangular/aRightOneCharacter',
                                                    tr('Right one character'), 'Alt+Shift+Right', ''),
(qsci.SCI_HOMERECTEXTEND, 'mEdit/mSelection/mRectangular/aToLineStart', tr('Line start'), '', ''),
(qsci.SCI_VCHOMERECTEXTEND, 'mEdit/mSelection/mRectangular/aToFirtsVCInLine',
                                                    tr('First visible character in line'), 'Alt+Shift+Home', ''),
(qsci.SCI_LINEENDRECTEXTEND, 'mEdit/mSelection/mRectangular/aToEndOfLine', tr('End of line'), 'Alt+Shift+End', ''),
(qsci.SCI_PAGEDOWNRECTEXTEND, 'mEdit/mSelection/mRectangular/aDownOnePage',
                                                    tr('Down one page'), 'Alt+Shift+PgDown', ''),
(qsci.SCI_PAGEUPRECTEXTEND, 'mEdit/mSelection/mRectangular/aUpOnePage', tr('Up one page'), 'Alt+Shift+PgUp', ''),
\
(qsci.SCI_LINEDOWN, 'mNavigation/mMove/aLineDown', tr('Down'), '', ''),
(qsci.SCI_LINEUP, 'mNavigation/mMove/aLineUp', tr('Up'), '', ''),
(qsci.SCI_CHARRIGHT, 'mNavigation/mMove/aRight', tr('Right'), '', ''),
(qsci.SCI_CHARLEFT, 'mNavigation/mMove/aLeft', tr('Left'), '', ''),
\
(qsci.SCI_HOME, 'mNavigation/mMove/mLine/aStart', tr('Start'), '', ''),
(qsci.SCI_HOMEDISPLAY, 'mNavigation/mMove/mLine/aStartOfDisplayed', tr('Start of displayed'), 'Alt+Home', ''),
(qsci.SCI_HOMEWRAP, 'mNavigation/mMove/mLine/aHomeWrap', tr('Home wrap'), '', ''),
(qsci.SCI_VCHOME, 'mNavigation/mMove/mLine/aFirsstVCInLine', tr('First visible character'), '', ''),
(qsci.SCI_VCHOMEWRAP, 'mNavigation/mMove/mLine/aVCHomeWrap', tr('Visible character home wrap'), '', ''),
(qsci.SCI_LINEEND, 'mNavigation/mMove/mLine/aToEndOfLine', tr('End'), '', ''),
(qsci.SCI_LINEENDDISPLAY, 'mNavigation/mMove/mLine/aToEndDisplayedLine', tr('End of displayed'), 'Alt+End', ''),
(qsci.SCI_LINEENDWRAP, 'mNavigation/mMove/mLine/aEndWrap', tr('End wrap'), '', ''),
\
(qsci.SCI_DOCUMENTSTART, 'mNavigation/mMove/mDocument/aStart', tr('Start'), 'Ctrl+Home', ''),
(qsci.SCI_DOCUMENTEND, 'mNavigation/mMove/mDocument/aEnd', tr('End'), 'Ctrl+End', ''),
\
(qsci.SCI_PAGEUP, 'mNavigation/mMove/mPage/aUp', tr('Up'), '', ''),
(qsci.SCI_PAGEDOWN, 'mNavigation/mMove/mPage/aDown', tr('Down'), '', ''),
(qsci.SCI_STUTTEREDPAGEUP, 'mNavigation/mMove/mPage/aUpStuttered', tr('Up stuttered'), '', ''),
(qsci.SCI_STUTTEREDPAGEDOWN, 'mNavigation/mMove/mPage/aDownStuttered', tr('Down stuttered'), '', ''),
\
(qsci.SCI_PARAUP, 'mNavigation/mMove/mParagraph/aUp', tr('Up'), 'Ctrl+[', ''),
(qsci.SCI_PARADOWN, 'mNavigation/mMove/mParagraph/aDown', tr('Down'), 'Ctrl+]', ''),
\
(qsci.SCI_WORDLEFT, 'mNavigation/mMove/mWord/aLeft', tr('Left'), 'Ctrl+Left', ''),
(qsci.SCI_WORDRIGHT, 'mNavigation/mMove/mWord/aRight', tr('Right'), 'Ctrl+Right', ''),
(qsci.SCI_WORDLEFTEND, 'mNavigation/mMove/mWord/aLeftEnd', tr('Left end'), '', ''),
(qsci.SCI_WORDRIGHTEND, 'mNavigation/mMove/mWord/aRightEnd', tr('Right end'), '', ''),
(qsci.SCI_WORDPARTLEFT, 'mNavigation/mMove/mWord/aLeftPart', tr('Left part'), 'Ctrl+/', ''),
(qsci.SCI_WORDPARTRIGHT, 'mNavigation/mMove/mWord/aRightPart', tr('Right part'), 'Ctrl+\\', ''),
\
(qsci.SCI_UNDO, 'mEdit/mHistory/aUndo', tr('Undo'), 'Ctrl+Z', 'undo.png'),
(qsci.SCI_REDO, 'mEdit/mHistory/aRedo', tr('Redo'), 'Ctrl+Y', 'redo.png'),
\
(qsci.SCI_LOWERCASE, 'mEdit/mCase/aToLower', tr('To lower'), 'Ctrl+U', ''),
(qsci.SCI_UPPERCASE, 'mEdit/mCase/aToUpper', tr('To upper'), 'Ctrl+Alt+U', ''),
\
(qsci.SCI_LINETRANSPOSE, 'mEdit/aSwapCurrentAndPreviousLine', tr('Swap current and previous line'), 'Ctrl+T', ''),
(qsci.SCI_EDITTOGGLEOVERTYPE, 'mEdit/aEditToggleOverType', tr('Toggle over type'), 'Ins', ''),
\
(qsci.SCI_TAB, 'mEdit/mInsert/aIndent', tr('Indent'), '', ''),
\
(qsci.SCI_CLEAR, 'mEdit/mDelete/aDelete', tr('Delete'), 'Del', ''),
(qsci.SCI_DELETEBACK, 'mEdit/mDelete/aBackspace', tr('Backspace'), '', ''),
(qsci.SCI_BACKTAB, 'mEdit/mDelete/aOneIndent', tr('Delete one indent'), 'Shift+Tab', ''),
(qsci.SCI_DELWORDLEFT, 'mEdit/mDelete/aPreviousWord', tr('Previous word'), 'Ctrl+Backspace', ''),
(qsci.SCI_DELWORDRIGHT, 'mEdit/mDelete/aNextWord', tr('Next word'), 'Ctrl+Del', ''),
(qsci.SCI_LINEDELETE, 'mEdit/mDelete/aLine', tr('Line'), 'Ctrl+Alt+L', ''),
(qsci.SCI_DELLINELEFT, 'mEdit/mDelete/aLineTpLeft', tr('Line to left'), 'Ctrl+Alt+Backspace', ''),
(qsci.SCI_DELLINERIGHT, 'mEdit/mDelete/aLineToRight', tr('Line to right'), 'Ctrl+Alt+Del', ''),
\
(qsci.SCI_COPY, 'mEdit/mCopyPaste/aCopy', tr('Copy'), 'Ctrl+C', 'copy.png'),
(MKS_PASTE, 'mEdit/mCopyPaste/aPaste', tr('Paste'), 'Ctrl+V', 'paste.png'),
(qsci.SCI_CUT, 'mEdit/mCopyPaste/aCut', tr('Cut'), 'Ctrl+X', 'cut.png'),
(qsci.SCI_LINECUT, 'mEdit/mCopyPaste/aCutLine', tr('Cut line'), 'Ctrl+L', 'cut.png'),
(qsci.SCI_LINECOPY, 'mEdit/mCopyPaste/aCopyLine', tr('Copy line'), 'Ctrl+Alt+T', 'copy.png'),
(qsci.SCI_SELECTIONDUPLICATE, 'mEdit/mCopyPaste/aDuplicateSelection', tr('Duplicate selection'), 'Ctrl+D', ''),
\
(qsci.SCI_ZOOMIN, 'mView/mZoom/aZoomIn', tr('Zoom In'), 'Ctrl++', ''),
(qsci.SCI_ZOOMOUT, 'mView/mZoom/aZoomOut', tr('Zoom Out'), 'Ctrl+-', ''),
(qsci.SCI_SETZOOM, 'mView/mZoom/aSetZoom', tr('Reset Zoom'), 'Ctrl+/', ''),
(MKS_TOGGLE_BOOKMARK, 'mNavigation/mBookmarks/aSetBookmark', tr('Set bookmark'), 'Ctrl+B', ''),
(MKS_NEXT_BOOKMARK, 'mNavigation/mBookmarks/aPreviousBookmark', tr('Next bookmark'), 'Alt+Down', ''),
(MKS_PREV_BOOKMARK, 'mNavigation/mBookmarks/aNextBookmark', tr('Previous bookmark'), 'Alt+Up', ''),
\
(qsci.SCI_LINESCROLLDOWN, 'mNavigation/mScroll/aDownOneLine', tr('Down one line'), 'Ctrl+Down', ''),
(qsci.SCI_LINESCROLLUP, 'mNavigation/mScroll/aUpOneLine', tr('Up one line'), 'Ctrl+Up', ''),
)

_MENUS = (\
('mEdit/mSelection', tr('Selection'), ''),
('mEdit/mSelection/mRectangular', tr('Rectangular'), ''),
('mEdit/mSelection/mDocument', tr('Document'), ''),
('mEdit/mSelection/mPage', tr('Extend by Page'), ''),
('mEdit/mSelection/mParagraph', tr('Extend by Paragraph'), ''),
('mEdit/mSelection/mLine', tr('Extend by Line'), ''),
('mEdit/mSelection/mWord', tr('Extend by Word'), ''),
('mNavigation/mMove', tr('Move'), ''),
('mNavigation/mMove/mDocument', tr('Document'), ''),
('mNavigation/mMove/mPage', tr('Page'), ''),
('mNavigation/mMove/mParagraph', tr('Paragraph'), ''),
('mNavigation/mMove/mLine', tr('Line'), ''),
('mNavigation/mMove/mWord', tr('Word'), ''),
('mEdit/mInsert', tr('Insert'), ''),
('mEdit/mDelete', tr('Delete'), 'deleted.png'),
('mEdit/mCopyPaste', tr('Copy-pasting'), 'cut.png'),
('mEdit/mHistory', tr('History'), 'undo.png'),
('mEdit/mCase', tr('Change case'), 'abbreviation.png'),
('mNavigation/mScroll', tr('Scroll'), ''),
)

class Shortcuts(QObject):
    """Class creates all actions and sends events commands to the editor
    """
    def __init__(self):
        QObject.__init__(self)
        self._createdActions = []
        self._createdMenus = []
        self._currentDocument = core.workspace().currentDocument()  # probably None
        model = core.actionModel()
        
        for menu in _MENUS:
            if menu[2]:
                menuObj = model.addMenu(menu[0], menu[1], QIcon(':/mksicons/' + menu[2]))
            else:
                menuObj = model.addMenu(menu[0], menu[1])
            menuObj.setEnabled(False)
            self._createdMenus.append(menuObj)
        
        for command, path, text, shortcut, icon in _ACTIONS:
            actObject = QAction(text, self)
            if shortcut:
                actObject.setShortcut(shortcut)
            if icon:
                actObject.setIcon(QIcon(':/mksicons/' + icon))
            actObject.setData(command)
            actObject.setEnabled(False)
            actObject.triggered.connect(self.onAction)
            model.addAction(path, actObject)
            self._createdActions.append(actObject)
        
        core.workspace().currentDocumentChanged.connect(self.onCurrentDocumentChanged)

    def del_(self):
        model = core.actionModel()
        for actObject in self._createdActions:
            model.removeAction(actObject)

        for menuObj in self._createdMenus[::-1]:
            model.removeMenu(menuObj)

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings

    def onCurrentDocumentChanged(self, oldDocument, document):  # pylint: disable=W0613
        """Current document changed slot handler
        """
        for actObject in self._createdActions:
            actObject.setEnabled(document is not None)
        for menuObject in self._createdMenus:
            menuObject.setEnabled(document is not None)
        self._currentDocument = document
    
    def onAction(self):
        """Action action triggered handler
        """
        action = self.sender()
        code = action.data().toInt()[0]
        
        focusWidget = QApplication.focusWidget()
        if focusWidget is not None and isinstance(focusWidget, qsci):
            editor = focusWidget
        else:
            editor = self._currentDocument.qscintilla
        
        if code > 0:
            editor.SendScintilla(code)
        elif MKS_TOGGLE_BOOKMARK == code:
            editor.parent().toggleBookmark()
        elif MKS_NEXT_BOOKMARK == code:
            editor.parent().nextBookmark()
        elif MKS_PREV_BOOKMARK == code:
            editor.parent().prevBookmark()
        elif MKS_PASTE == code:  # Paste via method, to fix EOL
            editor.paste()
        else:
            assert 0
