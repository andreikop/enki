"""
editorshortcuts --- Manages QScintilla shortcuts
================================================

Contains editor dialog and functionality for load and save the shortcuts
"""

import os.path

from PyQt4 import uic
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QObject
from PyQt4.QtGui import QDialog, QDialogButtonBox, QHeaderView, QIcon, QKeySequence

from PyQt4.Qsci import QsciScintilla as qsci
from PyQt4.Qsci import QsciScintillaBase as qscib

from PyQt4.fresh import pRecursiveSortFilterProxyModel

from mks.core.core import core, DATA_FILES_PATH

def tr(s):
    # FIXME add translation
    return s

#define SCI_SHIFT SCMOD_SHIFT
#define SCI_CTRL SCMOD_CTRL
#define SCI_ALT SCMOD_ALT
#define SCI_CSHIFT (SCI_CTRL | SCI_SHIFT)
#define SCI_ASHIFT (SCI_ALT | SCI_SHIFT)

# Copy-pasted from QScintilla/src/KeyMap.cpp
_DEFAULT_KEYMAP = {
                    qsci.SCI_LINEDOWN:              (qsci.SCK_DOWN,         qsci.SCI_NORM),
                    qsci.SCI_LINEDOWNEXTEND:        (qsci.SCK_DOWN,         qsci.SCI_SHIFT),
                    qsci.SCI_LINESCROLLDOWN:        (qsci.SCK_DOWN,         qsci.SCI_CTRL),
                    qsci.SCI_LINEDOWNRECTEXTEND:    (qsci.SCK_DOWN,         qsci.SCI_ASHIFT),
                    qsci.SCI_LINEUP:                (qsci.SCK_UP,           qsci.SCI_NORM),
                    qsci.SCI_LINEUPEXTEND:          (qsci.SCK_UP,           qsci.SCI_SHIFT),
                    qsci.SCI_LINESCROLLUP:          (qsci.SCK_UP,           qsci.SCI_CTRL),
                    qsci.SCI_LINEUPRECTEXTEND:      (qsci.SCK_UP,           qsci.SCI_ASHIFT),
                    qsci.SCI_PARAUP:                (ord('['),              qsci.SCI_CTRL),
                    qsci.SCI_PARAUPEXTEND:          (ord('['),              qsci.SCI_CSHIFT),
                    qsci.SCI_PARADOWN:              (ord(']'),              qsci.SCI_CTRL),
                    qsci.SCI_PARADOWNEXTEND:        (ord(']'),              qsci.SCI_CSHIFT),
                    qsci.SCI_CHARLEFT:              (qsci.SCK_LEFT,         qsci.SCI_NORM),
                    qsci.SCI_CHARLEFTEXTEND:        (qsci.SCK_LEFT,         qsci.SCI_SHIFT),
                    qsci.SCI_WORDLEFT:              (qsci.SCK_LEFT,         qsci.SCI_CTRL),
                    qsci.SCI_WORDLEFTEXTEND:        (qsci.SCK_LEFT,         qsci.SCI_CSHIFT),
                    qsci.SCI_CHARLEFTRECTEXTEND:    (qsci.SCK_LEFT,         qsci.SCI_ASHIFT),
                    qsci.SCI_CHARRIGHT:             (qsci.SCK_RIGHT,        qsci.SCI_NORM),
                    qsci.SCI_CHARRIGHTEXTEND:       (qsci.SCK_RIGHT,        qsci.SCI_SHIFT),
                    qsci.SCI_WORDRIGHT:             (qsci.SCK_RIGHT,        qsci.SCI_CTRL),
                    qsci.SCI_WORDRIGHTEXTEND:       (qsci.SCK_RIGHT,        qsci.SCI_CSHIFT),
                    qsci.SCI_CHARRIGHTRECTEXTEND:   (qsci.SCK_RIGHT,        qsci.SCI_ASHIFT),
                    qsci.SCI_WORDPARTLEFT:          (ord('/'),              qsci.SCI_CTRL),
                    qsci.SCI_WORDPARTLEFTEXTEND:    (ord('/'),              qsci.SCI_CSHIFT),
                    qsci.SCI_WORDPARTRIGHT:         (ord('\\'),             qsci.SCI_CTRL),
                    qsci.SCI_WORDPARTRIGHTEXTEND:   (ord('\\'),             qsci.SCI_CSHIFT),
                    qsci.SCI_VCHOME:                (qsci.SCK_HOME,         qsci.SCI_NORM),
                    qsci.SCI_VCHOMEEXTEND:          (qsci.SCK_HOME,         qsci.SCI_SHIFT),
                    qsci.SCI_DOCUMENTSTART:         (qsci.SCK_HOME,         qsci.SCI_CTRL),
                    qsci.SCI_DOCUMENTSTARTEXTEND:   (qsci.SCK_HOME,         qsci.SCI_CSHIFT),
                    qsci.SCI_HOMEDISPLAY:           (qsci.SCK_HOME,         qsci.SCI_ALT),
                    qsci.SCI_VCHOMERECTEXTEND:      (qsci.SCK_HOME,         qsci.SCI_ASHIFT),
                    qsci.SCI_LINEEND:               (qsci.SCK_END,          qsci.SCI_NORM),
                    qsci.SCI_LINEENDEXTEND:         (qsci.SCK_END,          qsci.SCI_SHIFT),
                    qsci.SCI_DOCUMENTEND:           (qsci.SCK_END,          qsci.SCI_CTRL),
                    qsci.SCI_DOCUMENTENDEXTEND:     (qsci.SCK_END,          qsci.SCI_CSHIFT),
                    qsci.SCI_LINEENDDISPLAY:        (qsci.SCK_END,          qsci.SCI_ALT),
                    qsci.SCI_LINEENDRECTEXTEND:     (qsci.SCK_END,          qsci.SCI_ASHIFT),
                    qsci.SCI_PAGEUP:                (qsci.SCK_PRIOR,        qsci.SCI_NORM),
                    qsci.SCI_PAGEUPEXTEND:          (qsci.SCK_PRIOR,        qsci.SCI_SHIFT),
                    qsci.SCI_PAGEUPRECTEXTEND:      (qsci.SCK_PRIOR,        qsci.SCI_ASHIFT),
                    qsci.SCI_PAGEDOWN:              (qsci.SCK_NEXT,         qsci.SCI_NORM),
                    qsci.SCI_PAGEDOWNEXTEND:        (qsci.SCK_NEXT,         qsci.SCI_SHIFT),
                    qsci.SCI_PAGEDOWNRECTEXTEND:    (qsci.SCK_NEXT,         qsci.SCI_ASHIFT),
                    qsci.SCI_CLEAR:                 (qsci.SCK_DELETE,       qsci.SCI_NORM),
                    qsci.SCI_CUT:                   (qsci.SCK_DELETE,       qsci.SCI_SHIFT),
                    qsci.SCI_DELWORDRIGHT:          (qsci.SCK_DELETE,       qsci.SCI_CTRL),
                    qsci.SCI_DELLINERIGHT:          (qsci.SCK_DELETE,       qsci.SCI_CSHIFT),
                    qsci.SCI_EDITTOGGLEOVERTYPE:    (qsci.SCK_INSERT,       qsci.SCI_NORM),
                    qsci.SCI_PASTE:                 (qsci.SCK_INSERT,       qsci.SCI_SHIFT),
                    qsci.SCI_COPY:                  (qsci.SCK_INSERT,       qsci.SCI_CTRL),
                    qsci.SCI_CANCEL:                (qsci.SCK_ESCAPE,       qsci.SCI_NORM),
                    qsci.SCI_DELETEBACK:            (qsci.SCK_BACK,         qsci.SCI_NORM),
                    qsci.SCI_DELETEBACK:            (qsci.SCK_BACK,         qsci.SCI_SHIFT),
                    qsci.SCI_DELWORDLEFT:           (qsci.SCK_BACK,         qsci.SCI_CTRL),
                    qsci.SCI_UNDO:                  (qsci.SCK_BACK,         qsci.SCI_ALT),
                    qsci.SCI_DELLINELEFT:           (qsci.SCK_BACK,         qsci.SCI_CSHIFT),
                    qsci.SCI_UNDO:                  (ord('Z'),               qsci.SCI_CTRL),
                    qsci.SCI_REDO:                  (ord('Y'),               qsci.SCI_CTRL),
                    qsci.SCI_CUT:                   (ord('X'),               qsci.SCI_CTRL),
                    qsci.SCI_COPY:                  (ord('C'),               qsci.SCI_CTRL),
                    qsci.SCI_PASTE:                 (ord('V'),               qsci.SCI_CTRL),
                    qsci.SCI_SELECTALL:             (ord('A'),               qsci.SCI_CTRL),
                    qsci.SCI_TAB:                   (qsci.SCK_TAB,          qsci.SCI_NORM),
                    qsci.SCI_BACKTAB:               (qsci.SCK_TAB,          qsci.SCI_SHIFT),
                    qsci.SCI_NEWLINE:               (qsci.SCK_RETURN,       qsci.SCI_NORM),
                    qsci.SCI_NEWLINE:               (qsci.SCK_RETURN,       qsci.SCI_SHIFT),
                    qsci.SCI_ZOOMIN:                (qsci.SCK_ADD,          qsci.SCI_CTRL),
                    qsci.SCI_ZOOMOUT:               (qsci.SCK_SUBTRACT,     qsci.SCI_CTRL),
                    qsci.SCI_SETZOOM:               (qsci.SCK_DIVIDE,       qsci.SCI_CTRL),
                    qsci.SCI_LINECUT:               (ord('L'),              qsci.SCI_CTRL),
                    qsci.SCI_LINEDELETE:            (ord('L'),              qsci.SCI_CSHIFT),
                    qsci.SCI_LINECOPY:              (ord('T'),              qsci.SCI_CSHIFT),
                    qsci.SCI_LINETRANSPOSE:         (ord('T'),              qsci.SCI_CTRL),
                    qsci.SCI_SELECTIONDUPLICATE:    (ord('D'),              qsci.SCI_CTRL),
                    qsci.SCI_LOWERCASE:             (ord('U'),              qsci.SCI_CTRL),
                    qsci.SCI_UPPERCASE:             (ord('U'),              qsci.SCI_CSHIFT),
                  }

_QSCI_TO_QT_KEY = {
                    SCK_ADD         : Qt.Key_Plus,
                    SCK_BACK        : Qt.Key_Backspace,
                    SCK_DELETE      : Qt.Key_Delete,
                    SCK_DIVIDE      : Qt.Key_Slash,
                    SCK_DOWN        : Qt.Key_Down,
                    SCK_END         : Qt.Key_End,
                    SCK_ESCAPE      : Qt.Key_Escape,
                    SCK_HOME        : Qt.Key_Home,
                    SCK_INSERT      : Qt.Key_Insert,
                    SCK_LEFT        : Qt.Key_Left,
                    SCK_MENU        : Qt.Key_Menu,
                    SCK_NEXT        : Qt.Key_PageDown,
                    SCK_PRIOR       : Qt.Key_PageUp,
                    SCK_RETURN      : Qt.Key_Enter,
                    SCK_RIGHT       : Qt.Key_Right,
                    SCK_RWIN        : 0,
                    SCK_SUBTRACT    : Qt.Key_Minus,
                    SCK_TAB         : Qt.KeyTab,
                    SCK_UP          : Qt.Key_Up,
                    SCK_WIN         : 0,
                    ord('/')        : Qt.Key_Slash,
                    ord('[')        : Qt.Bracket_Left,
                    ord(']')        : Qt.Bracket_Right,
                    ord('\\')       : Qt.Key_Backslash,
                  }
_QT_TO_QSCI_KEY = dict((v,k) for k, v in _QSCI_TO_QT_KEY.iteritems())

_QSCI_TO_QT_MODIFIER = {
                        SCI_NORM    : 0,
                        SCI_ALT     : Qt.AltModifier,
                        SCI_CTRL    : Qt.ControlModifier,
                        SCI_SHIFT   : Qt.ShiftModifier,
                        SCI_CSHIFT  : Qt.ControlModifier | Qt.AltModifier,
                        SCI_ASHIFT  : Qt.AltModifier | Qt.ShiftModifier,
                       }
_QT_TO_QSCI_MODIFIER = dict((v,k) for k, v in _QSCI_TO_QT_MODIFIER.iteritems())

def sciToQt(key):
    modifier = key >> 16
    code = key & 0xffff0000
    if code in range(ord('A'), ord('Z')):
        qtCode = Qt.Key_A + (ord(code) - ord('A'))
    else:
        qtCode = _QSCI_TO_QT_KEY[code]
    qtModifier = _QSCI_TO_QT_MODIFIER[modifier]
    return QKeySequence(qtCode, qtModifier)

def qtToQsci(key):
    elements = filter([key[i] for i in range(0, 3)])
    code = elements[-1]
    modifiers = elements[:-1]
    modifier = reduce(lambda a, b: a * b, modifiers)
    if code in range(Qt.Key_A, Qt.Key_Z):
        qsciCode = ord('A') + (code - Qt.Key_A)
    else:
        qsciCode = _QT_TO_QSCI_KEY[code]
    qsciModifier = _QT_TO_QSCI_MODIFIER[modifier]
    return (qsciModifier << 16) | qsciCode

_SHORTCUTS = (
                (tr("Selection"), (
                                    (qsci.SCI_LINEDOWNEXTEND, tr("Extend selection down one line")),
                                    (qsci.SCI_LINEDOWNRECTEXTEND, tr("Extend rectangular selection down one line")),
                                    (qsci.SCI_LINESCROLLDOWN, tr("Scroll view down one line")),
                                    (qsci.SCI_LINEUPEXTEND, tr("Extend selection up")),
                                    (qsci.SCI_LINEUPRECTEXTEND, tr("Extend selection up one line")),
                                    (qsci.SCI_PARADOWNEXTEND, tr("Extend selection up one paragraph")),
                                    (qsci.SCI_CHARLEFTEXTEND, tr("Extend selection left one character")),
                                    (qsci.SCI_CHARLEFTRECTEXTEND, tr("Extend rectangular selection left one character")),
                                    (qsci.SCI_CHARRIGHTEXTEND, tr("Extend selection right one character")),
                                    (qsci.SCI_CHARRIGHTRECTEXTEND, tr("Extend rectangular selection right one character")),
                                    (qsci.SCI_PARAUPEXTEND, tr("Extend selection down one paragraph")),
                                    (qsci.SCI_WORDLEFTEXTEND, tr("Extend selection left one word")),
                                    (qsci.SCI_WORDRIGHTEXTEND, tr("Extend selection right one word")),
                                    (qsci.SCI_WORDLEFTENDEXTEND, tr("Extend selection left one word left")),
                                    (qsci.SCI_WORDRIGHTENDEXTEND, tr("Extend selection right one word end")),
                                    (qsci.SCI_WORDPARTLEFTEXTEND, tr("Extend selection left one word part ")),
                                    (qsci.SCI_WORDPARTRIGHTEXTEND, tr("Extend selection right one word part")),
                                    (qsci.SCI_HOMEEXTEND, tr("Extend selection to line start")),                  
                                    (qsci.SCI_HOMERECTEXTEND, tr("Extend rectangular selection to line start")),
                                    (qsci.SCI_HOMEDISPLAYEXTEND, tr("Extend selection start of displayed line")),
                                    (qsci.SCI_HOMEWRAPEXTEND, tr("Extend selection on home wrap")),
                                    (qsci.SCI_VCHOMERECTEXTEND, tr("Extend rectangular selection to firts VC in line")),
                                    (qsci.SCI_VCHOMEWRAPEXTEND, tr("Extend selection VC Home wrap")),
                                    (qsci.SCI_LINEENDEXTEND, tr("Extend selection to end of line")),
                                    (qsci.SCI_LINEENDRECTEXTEND, tr("Extend rectangular selection to end of line")),
                                    (qsci.SCI_LINEENDDISPLAYEXTEND, tr("Extend selection to end of displayed line")),
                                    (qsci.SCI_LINEENDWRAPEXTEND, tr("Extend selection to line end wrap")),
                                    (qsci.SCI_DOCUMENTSTARTEXTEND, tr("Extend selection to document start")),
                                    (qsci.SCI_DOCUMENTENDEXTEND, tr("Extend selection to document end")),
                                    (qsci.SCI_PAGEDOWNEXTEND, tr("Extend selection down one page")),
                                    (qsci.SCI_PAGEDOWNRECTEXTEND, tr("Extend rectangular selection down one page")),
                                    (qsci.SCI_STUTTEREDPAGEUPEXTEND, tr("Extend selection up one page stuttered")),
                                    (qsci.SCI_PAGEUPEXTEND, tr("Extend selection up one page")),
                                    (qsci.SCI_PAGEUPRECTEXTEND, tr("Extend rectangular selection up one page")),
                                    (qsci.SCI_STUTTEREDPAGEDOWNEXTEND, tr("Extend selection down one page stuttered")),
                                  ),
                ),
                (tr("Navigation"), (
                                    (qsci.SCI_LINESCROLLUP, tr("Scroll view up one line")),
                                    (qsci.SCI_PARADOWN, tr("Move down one paragraph")),
                                    (qsci.SCI_PARAUP, tr("Move down one paragraph")),
                                    (qsci.SCI_WORDLEFT, tr("Move left one word")),
                                    (qsci.SCI_WORDRIGHT, tr("Move right one word")),
                                    (qsci.SCI_WORDLEFTEND, tr("Move left one word end")),
                                    (qsci.SCI_WORDRIGHTEND, tr("Move right one word end")),
                                    (qsci.SCI_WORDPARTLEFT, tr("Move left one word part")),
                                    (qsci.SCI_WORDPARTRIGHT, tr("Move right one word part")),
                                    (qsci.SCI_HOME, tr("Move to line start")),
                                    (qsci.SCI_HOMEDISPLAY, tr("Move to start of displayed line")),
                                    (qsci.SCI_HOMEWRAP, tr("Home wrap")),
                                    (qsci.SCI_VCHOME, tr("Move to firsst VC in line")),
                                    (qsci.SCI_VCHOMEEXTEND, tr("Extend selection to first VC in line")),
                                    (qsci.SCI_VCHOMEWRAP, tr("VC Home wrap")),
                                    (qsci.SCI_LINEEND, tr("Move to end of line")),
                                    (qsci.SCI_LINEENDDISPLAY, tr("Move to end displayed line")),
                                    (qsci.SCI_LINEENDWRAP, tr("Move to line end wrap")),
                                    (qsci.SCI_DOCUMENTSTART, tr("Move to document start")),
                                    (qsci.SCI_DOCUMENTEND, tr("Move to document end")),
                                    (qsci.SCI_PAGEUP, tr("Move up one page")),
                                    (qsci.SCI_PAGEDOWN, tr("Move down one page")),
                                    (qsci.SCI_STUTTEREDPAGEUP, tr("Move up one page stuttered")),
                                    (qsci.SCI_STUTTEREDPAGEDOWN, tr("Move down one page stuttered")),
                                  ),
                ),
                (tr("Edit"), (
                              (qsci.SCI_DELETEBACKNOTLINE, tr("Backspace not a line")),
                              (qsci.SCI_DELWORDLEFT, tr("Delete previous word")),
                              (qsci.SCI_DELWORDRIGHT, tr("Delete next word")),
                              (qsci.SCI_DELLINELEFT, tr("Delete line tp left")),
                              (qsci.SCI_DELLINERIGHT, tr("Delete line to right")),
                              (qsci.SCI_LINEDELETE, tr("Delete line")),
                              (qsci.SCI_LINECUT, tr("Cut line")),
                              (qsci.SCI_LINECOPY, tr("Copy line")),
                              (qsci.SCI_LINETRANSPOSE, tr("Swap current and previous line")),
                              (qsci.SCI_LINEDUPLICATE, tr("Duplicate line")),
                              (qsci.SCI_LOWERCASE, tr("To lower case")),
                              (qsci.SCI_UPPERCASE, tr("To upper case")),
                              (qsci.SCI_EDITTOGGLEOVERTYPE, tr("Edit toggle over type")),
                              (qsci.SCI_FORMFEED, tr("Formfeed")),
                              (qsci.SCI_BACKTAB, tr("Delete one indent")),
                              (qsci.SCI_SELECTIONDUPLICATE, tr("Duplicate selection")),
                              (qsci.SCI_CLEAR, tr("Delete")),
                              (qsci.SCI_SELECTALL, tr("Select All")),
                             ),
                ),
                (tr("Zoom"), (
                              (qsci.SCI_ZOOMIN, tr("Zoom In")),
                              (qsci.SCI_ZOOMOUT, tr("Zoom Out")),
                              (qsci.SCI_SETZOOM, tr("Set Zoom")),
                             ),
                ),
                (tr("Bookmarks"),
                 (
                  (qsci.SCI_MARKERADD, tr("Set bookmark")),
                  (qsci.SCI_MARKERDELETEALL, tr( "Delete all bookmarks" )),
                  (qsci.SCI_MARKERPREVIOUS, tr( "Previous bookmark" )),
                  (qsci.SCI_MARKERNEXT, tr( "Next bookmark")),
                 ),
                ),
             )


class EditorShortcutsModel(QAbstractItemModel):
    """Class implements list of actions, visible in the tree view
    """
    def __init__(self, dialog, *args):
        QAbstractItemModel.__init__(self, *args)
        self._dialog = dialog

    def isRoot(self, index):
        return not index.isValid()
    
    def isMenu(self, index):
        return index.isValid() and \
               not index.internalPointer()
    
    def isAction(self, index):
        return index.isValid() and \
               index.internalPointer()
    
    def menu(self, index):
        assert(self.isMenu(index))
        return _SHORTCUTS[index.row()]

    def action(self, index):
        assert(self.isAction(index))
        menu = index.internalPointer()
        return menu[1][index.row()]
    
    def columnCount(self, parent):
        return 3

    def data(self, index, role ):
        if not index.isValid():
            return None
        
        if self.isAction(index):  # action
            action = self.action(index)
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if index.column() == 0:  # name
                    return action[1]
                elif index.column() == 1:  # shortcut
                    return self._dialog.shortcut(action[0])
                elif index.column() == 2: # default shortcut
                    return self._dialog.defaultShortcut(action[0])
            else:  # not supported role
                return None
        else:
            assert(self.isMenu(index))
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if index.column() == 0:
                    return self.menu(index)[0]
                else:
                    return None

    def index(self, row, column, parent):
        if self.isMenu(parent):
            index = self.createIndex(row, column, _SHORTCUTS[parent.row()])
        else:
            assert(self.isRoot(parent))
            index = self.createIndex(row, column)
        assert(index.isValid())
        return index

    def parent(self, index):
        if self.isAction(index):
            menu = index.internalPointer()
            return self.createIndex(_SHORTCUTS.index(menu), 0)
        else:
            return QModelIndex()

    def rowCount(self, parent):
        if self.isAction(parent):
            return 0
        elif self.isMenu(parent):
            menu = self.menu(parent)
            return len(menu[1])
        else:
            assert(self.isRoot(parent))
            return len(_SHORTCUTS)

    def hasChildren(self, parent):
        if self.isAction(parent):
            return False
        else:  # menu or root
            return True

    def headerData(self, section, orientation, role ):
        if orientation == Qt.Horizontal:
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if section == 0:
                    return self.tr( "Action" )
                elif section == 1:
                    return self.tr( "Shortcut" )
                elif section == 2:
                    return self.tr( "Default Shortcut" )
        return QAbstractItemModel.headerData( self, section, orientation, role )


class EditorShortcutsDialog(QDialog):
    """Dialog for editor shortcuts
    """
    _defaultShortcuts = {}
    
    def __init__(self, editor, *args):
        QDialog.__init__(self, *args)
        self._editor = editor

        self._model = EditorShortcutsModel(self)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/EditorShortcutsDialog.ui'), self)
        self.leFilter.setSearchButtonVisible( False )
        self.leFilter.setPromptText( self.tr( "Text filter..." ) )
        
        self._proxy = pRecursiveSortFilterProxyModel( self )
        self._proxy.setSourceModel( self._model )
        self._proxy.setFilterCaseSensitivity( Qt.CaseInsensitive )
        self._proxy.setSortCaseSensitivity( Qt.CaseInsensitive )

        self.tvActions.setModel( self._proxy )
        self.tvActions.header().setResizeMode( 0, QHeaderView.Stretch )
        self.tvActions.header().setResizeMode( 1, QHeaderView.ResizeToContents )
        self.tvActions.header().setResizeMode( 2, QHeaderView.ResizeToContents )
        self.tvActions.expandAll()

        # connections
        self.tvActions.selectionModel().selectionChanged.connect(self.tvActions_selectionModel_selectionChanged)
        
        self.tvActions_selectionModel_selectionChanged()

    def selectedIndex(self):
        """Get index of the selected item
        """
        indexes = self.tvActions.selectionModel().selectedIndexes()
        if indexes:
            return indexes[0]
        return QModelIndex()

    def setShortcut(self, index, shortcut):
        """Set shortcut for the action, identified by the index
        """
        # TODO implement
        pass

    def shortcut(self, index):
        """Get shortcut for the action, identified by the index
        """    
        # TODO implement
        return 'short'
    
    def defaultShortcut(self, index):
        """Get default shortcut for the action, identified by the index
        """
        # TODO implement
        return 'def'
    
    def isDefaultShortcut(self, index):
        """Check if shortcut for action is default
        """
        return index.isValid() and \
               self.shortcut(index) != self.defaultShortcut(index)

    def tvActions_selectionModel_selectionChanged(self):
        """Selection changed in the list
        """
        index = self.selectedIndex()
        if index.isValid():
            self.kseShortcut.setText(self.shortcut(index))
        else:
            self.kseShortcut.clear()
        
        self.kseShortcut.setEnabled(index.isValid())
        self.tbSet.setEnabled(False)
        self.tbClear.setEnabled( index.isValid() and bool(self.shortcut(index)) )
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( False )
        self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not self.isDefaultShortcut(index))
        self.kseShortcut.setFocus()

    def on_kseShortcut_textChanged(self, text):
        """Text has been changed in the shortcut input
        """
        index = self.selectedIndex()
        self.tbSet.setEnabled( index.isValid() and bool(self.kseShortcut.text()) )
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( True )
        self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not self.isDefaultShortcut(index))

    def on_tbSet_clicked(self):
        """*Set* button has been clicked
        """
        index = self.selectedIndex()
        if index.isValid() and not self.kseShortcut.text().isEmpty():
            self.setShortcut(index, self.kseShortcut.text())

    def on_tbClear_clicked(self):
        """*Clear* button has been clicked
        """
        index = self.selectedIndex()
        if index.isValid():
            self.setShortcut( index, None)

    def on_dbbButtons_clicked(self, button ):
        """One of dialog button box buttons has been clicked
        """
        stButton = self.dbbButtons.standardButton( button )
        if stButton == QDialogButtonBox.Reset:
            self.tvActions_selectionModel_selectionChanged()
        elif stButton == QDialogButtonBox.RestoreDefaults:
            index = self.selectedIndex()
            if index.isValid():
                self.setShortcut(index, self.defaultShortcut(index))
        elif stButton == QDialogButtonBox.Ok:
            self.accept()

    def on_leFilter_textChanged(self, text ):
        self._proxy.setFilterWildcard( text )
        self.tvActions.expandAll()

class EditorShortcuts:
    def __init__(self):
        action = core.actionModel().addAction("mEdit/aEditorShortcuts",
                                              tr( "Editor shortcuts..."),
                                              QIcon(':/mksicons/shortcuts.png'))
        action.triggered.connect(lambda : EditorShortcutsDialog().exec_())
    
    def __term__(self):
        core.actionModel().removeAction("mEdit/aEditorShortcuts")

    def exec_():
        document = core.workspace().currentDocument()
        if document:
            editor = document.qscintilla
            EditorShortcutsDialog(editor).exec_()
