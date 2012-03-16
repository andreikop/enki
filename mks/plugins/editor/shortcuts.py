"""
shortcuts --- Manages QScintilla shortcuts
==========================================

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
MKS_PASTE_LINE = -5

_ACTIONS = (\
(qsci.SCI_PARAUPEXTEND, 'mEdit/mSelection/mParagraph/aUp', tr('Up'), 'Ctrl+Shift+[', ''),
(qsci.SCI_PARADOWNEXTEND, 'mEdit/mSelection/mParagraph/aDown', tr('Down'), 'Ctrl+Shift+]', ''),
\
(qsci.SCI_LINEDOWNRECTEXTEND, 'mEdit/mSelection/mRectangular/aDownOneLine', tr('Down one line'), 'Alt+Shift+Down', ''),
(qsci.SCI_CHARLEFTRECTEXTEND, 'mEdit/mSelection/mRectangular/aLeftOneCharacter', 
                                                    tr('Left one character'), 'Alt+Shift+Left', ''),
(qsci.SCI_CHARRIGHTRECTEXTEND, 'mEdit/mSelection/mRectangular/aRightOneCharacter',
                                                    tr('Right one character'), 'Alt+Shift+Right', ''),
(qsci.SCI_HOMERECTEXTEND, 'mEdit/mSelection/mRectangular/aToLineStart', tr('Line start'), 'Alt+Shift+Home', ''),
(qsci.SCI_LINEENDRECTEXTEND, 'mEdit/mSelection/mRectangular/aToEndOfLine', tr('End of line'), 'Alt+Shift+End', ''),
(qsci.SCI_PAGEDOWNRECTEXTEND, 'mEdit/mSelection/mRectangular/aDownOnePage',
                                                    tr('Down one page'), 'Alt+Shift+PgDown', ''),
(qsci.SCI_PAGEUPRECTEXTEND, 'mEdit/mSelection/mRectangular/aUpOnePage', tr('Up one page'), 'Alt+Shift+PgUp', ''),
\
(qsci.SCI_PARAUP, 'mNavigation/mMove/aUp', tr('Paragraph Up'), 'Ctrl+[', ''),
(qsci.SCI_PARADOWN, 'mNavigation/mMove/aDown', tr('Paragraph Down'), 'Ctrl+]', ''),
\
(qsci.SCI_UNDO, 'mEdit/mHistory/aUndo', tr('Undo'), 'Ctrl+Z', 'undo.png'),
(qsci.SCI_REDO, 'mEdit/mHistory/aRedo', tr('Redo'), 'Ctrl+Y', 'redo.png'),
\
(qsci.SCI_LOWERCASE, 'mEdit/mCase/aToLower', tr('To lower'), 'Ctrl+U', ''),
(qsci.SCI_UPPERCASE, 'mEdit/mCase/aToUpper', tr('To upper'), 'Ctrl+Alt+U', ''),
\
(qsci.SCI_LINETRANSPOSE, 'mEdit/aSwapCurrentAndPreviousLine', tr('Swap current and previous line'), 'Ctrl+T', ''),
(qsci.SCI_EDITTOGGLEOVERTYPE, 'mEdit/aEditToggleOverType', tr('Toggle over type'), 'Ins', ''),
(qsci.SCI_LINEDELETE, 'mEdit/aDeleteLine', tr('Delete line'), 'Alt+Del', 'deleted.png'),
\
(qsci.SCI_COPY, 'mEdit/mCopyPaste/aCopy', tr('Copy'), 'Ctrl+C', 'copy.png'),
(MKS_PASTE, 'mEdit/mCopyPaste/aPaste', tr('Paste'), 'Ctrl+V', 'paste.png'),
(qsci.SCI_CUT, 'mEdit/mCopyPaste/aCut', tr('Cut'), 'Ctrl+X', 'cut.png'),
(qsci.SCI_LINECOPY, 'mEdit/mCopyPaste/aCopyLine', tr('Copy line'), 'Alt+C', 'copy.png'),
(qsci.SCI_LINECUT, 'mEdit/mCopyPaste/aCutLine', tr('Cut line'), 'Alt+X', 'cut.png'),
(MKS_PASTE_LINE, 'mEdit/mCopyPaste/aPasteLine', tr('Paste line'), 'Alt+V', 'paste.png'),
(qsci.SCI_SELECTIONDUPLICATE, 'mEdit/mCopyPaste/aDuplicateSelection', tr('Duplicate selection'), 'Ctrl+D', ''),
\
(qsci.SCI_ZOOMIN, 'mView/mZoom/aZoomIn', tr('Zoom In'), 'Ctrl++', ''),
(qsci.SCI_ZOOMOUT, 'mView/mZoom/aZoomOut', tr('Zoom Out'), 'Ctrl+-', ''),
\
(MKS_TOGGLE_BOOKMARK, 'mNavigation/mBookmarks/aSetBookmark', tr('Set (clear) bookmark'), 'Ctrl+B', ''),
(MKS_NEXT_BOOKMARK, 'mNavigation/mBookmarks/aPreviousBookmark', tr('Next bookmark'), 'Alt+Down', ''),
(MKS_PREV_BOOKMARK, 'mNavigation/mBookmarks/aNextBookmark', tr('Previous bookmark'), 'Alt+Up', ''),
\
(qsci.SCI_LINESCROLLDOWN, 'mNavigation/mScroll/aDownOneLine', tr('Down one line'), 'Ctrl+Down', ''),
(qsci.SCI_LINESCROLLUP, 'mNavigation/mScroll/aUpOneLine', tr('Up one line'), 'Ctrl+Up', ''),
)

_MENUS = (\
('mEdit/mSelection', tr('Selection'), ''),
('mEdit/mSelection/mRectangular', tr('Rectangular'), ''),
('mEdit/mSelection/mParagraph', tr('Extend by Paragraph'), ''),
('mNavigation/mMove', tr('Move'), ''),
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
        model = core.actionManager()
        
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
        model = core.actionManager()
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
        elif MKS_PASTE_LINE == code:  # Own method
            editor.pasteLine()
        else:
            assert 0
