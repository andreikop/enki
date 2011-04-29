"""
editorshortcuts --- Manages QScintilla shortcuts
================================================

Contains editor dialog and functionality for load and save the shortcuts
"""

import os.path
import copy

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

SCI_NORM = 0
SCI_SHIFT = qsci.SCMOD_SHIFT << 16
SCI_CTRL = qsci.SCMOD_CTRL << 16
SCI_ALT = qsci.SCMOD_ALT << 16
SCI_CSHIFT = SCI_CTRL | SCI_SHIFT
SCI_ASHIFT = SCI_ALT | SCI_SHIFT
SCI_ACSHIFT = SCI_ALT | SCI_SHIFT | SCI_CTRL

# Copy-pasted from QScintilla/src/KeyMap.cpp
_DEFAULT_KEYMAP = {
                    qsci.SCI_LINEDOWN:              qsci.SCK_DOWN     | SCI_NORM,
                    qsci.SCI_LINEDOWNEXTEND:        qsci.SCK_DOWN     | SCI_SHIFT,
                    qsci.SCI_LINESCROLLDOWN:        qsci.SCK_DOWN     | SCI_CTRL,
                    qsci.SCI_LINEDOWNRECTEXTEND:    qsci.SCK_DOWN     | SCI_ASHIFT,
                    qsci.SCI_LINEUP:                qsci.SCK_UP       | SCI_NORM,
                    qsci.SCI_LINEUPEXTEND:          qsci.SCK_UP       | SCI_SHIFT,
                    qsci.SCI_LINESCROLLUP:          qsci.SCK_UP       | SCI_CTRL,
                    qsci.SCI_LINEUPRECTEXTEND:      qsci.SCK_UP       | SCI_ASHIFT,
                    qsci.SCI_PARAUP:                ord('[')          | SCI_CTRL,
                    qsci.SCI_PARAUPEXTEND:          ord('[')          | SCI_CSHIFT,
                    qsci.SCI_PARADOWN:              ord(']')          | SCI_CTRL,
                    qsci.SCI_PARADOWNEXTEND:        ord(']')          | SCI_CSHIFT,
                    qsci.SCI_CHARLEFT:              qsci.SCK_LEFT     | SCI_NORM,
                    qsci.SCI_CHARLEFTEXTEND:        qsci.SCK_LEFT     | SCI_SHIFT,
                    qsci.SCI_WORDLEFT:              qsci.SCK_LEFT     | SCI_CTRL,
                    qsci.SCI_WORDLEFTEXTEND:        qsci.SCK_LEFT     | SCI_CSHIFT,
                    qsci.SCI_CHARLEFTRECTEXTEND:    qsci.SCK_LEFT     | SCI_ASHIFT,
                    qsci.SCI_CHARRIGHT:             qsci.SCK_RIGHT    | SCI_NORM,
                    qsci.SCI_CHARRIGHTEXTEND:       qsci.SCK_RIGHT    | SCI_SHIFT,
                    qsci.SCI_WORDRIGHT:             qsci.SCK_RIGHT    | SCI_CTRL,
                    qsci.SCI_WORDRIGHTEXTEND:       qsci.SCK_RIGHT    | SCI_CSHIFT,
                    qsci.SCI_CHARRIGHTRECTEXTEND:   qsci.SCK_RIGHT    | SCI_ASHIFT,
                    qsci.SCI_WORDPARTLEFT:          ord('/')          | SCI_CTRL,
                    qsci.SCI_WORDPARTLEFTEXTEND:    ord('/')          | SCI_CSHIFT,
                    qsci.SCI_WORDPARTRIGHT:         ord('\\')         | SCI_CTRL,
                    qsci.SCI_WORDPARTRIGHTEXTEND:   ord('\\')         | SCI_CSHIFT,
                    qsci.SCI_VCHOME:                qsci.SCK_HOME     | SCI_NORM,
                    qsci.SCI_VCHOMEEXTEND:          qsci.SCK_HOME     | SCI_SHIFT,
                    qsci.SCI_DOCUMENTSTART:         qsci.SCK_HOME     | SCI_CTRL,
                    qsci.SCI_DOCUMENTSTARTEXTEND:   qsci.SCK_HOME     | SCI_CSHIFT,
                    qsci.SCI_HOMEDISPLAY:           qsci.SCK_HOME     | SCI_ALT,
                    qsci.SCI_VCHOMERECTEXTEND:      qsci.SCK_HOME     | SCI_ASHIFT,
                    qsci.SCI_LINEEND:               qsci.SCK_END      | SCI_NORM,
                    qsci.SCI_LINEENDEXTEND:         qsci.SCK_END      | SCI_SHIFT,
                    qsci.SCI_DOCUMENTEND:           qsci.SCK_END      | SCI_CTRL,
                    qsci.SCI_DOCUMENTENDEXTEND:     qsci.SCK_END      | SCI_CSHIFT,
                    qsci.SCI_LINEENDDISPLAY:        qsci.SCK_END      | SCI_ALT,
                    qsci.SCI_LINEENDRECTEXTEND:     qsci.SCK_END      | SCI_ASHIFT,
                    qsci.SCI_PAGEUP:                qsci.SCK_PRIOR    | SCI_NORM,
                    qsci.SCI_PAGEUPEXTEND:          qsci.SCK_PRIOR    | SCI_SHIFT,
                    qsci.SCI_PAGEUPRECTEXTEND:      qsci.SCK_PRIOR    | SCI_ASHIFT,
                    qsci.SCI_PAGEDOWN:              qsci.SCK_NEXT     | SCI_NORM,
                    qsci.SCI_PAGEDOWNEXTEND:        qsci.SCK_NEXT     | SCI_SHIFT,
                    qsci.SCI_PAGEDOWNRECTEXTEND:    qsci.SCK_NEXT     | SCI_ASHIFT,
                    qsci.SCI_CLEAR:                 qsci.SCK_DELETE   | SCI_NORM,
                    qsci.SCI_CUT:                   qsci.SCK_DELETE   | SCI_SHIFT,
                    qsci.SCI_DELWORDRIGHT:          qsci.SCK_DELETE   | SCI_CTRL,
                    qsci.SCI_DELLINERIGHT:          qsci.SCK_DELETE   | SCI_CSHIFT,
                    qsci.SCI_EDITTOGGLEOVERTYPE:    qsci.SCK_INSERT   | SCI_NORM,
                    qsci.SCI_PASTE:                 qsci.SCK_INSERT   | SCI_SHIFT,
                    qsci.SCI_COPY:                  qsci.SCK_INSERT   | SCI_CTRL,
                    qsci.SCI_CANCEL:                qsci.SCK_ESCAPE   | SCI_NORM,
                    qsci.SCI_DELETEBACK:            qsci.SCK_BACK     | SCI_NORM,
                    qsci.SCI_DELETEBACK:            qsci.SCK_BACK     | SCI_SHIFT,
                    qsci.SCI_DELWORDLEFT:           qsci.SCK_BACK     | SCI_CTRL,
                    qsci.SCI_UNDO:                  qsci.SCK_BACK     | SCI_ALT,
                    qsci.SCI_DELLINELEFT:           qsci.SCK_BACK     | SCI_CSHIFT,
                    qsci.SCI_UNDO:                  ord('Z')          | SCI_CTRL,
                    qsci.SCI_REDO:                  ord('Y')          | SCI_CTRL,
                    qsci.SCI_CUT:                   ord('X')          | SCI_CTRL,
                    qsci.SCI_COPY:                  ord('C')          | SCI_CTRL,
                    qsci.SCI_PASTE:                 ord('V')          | SCI_CTRL,
                    qsci.SCI_SELECTALL:             ord('A')          | SCI_CTRL,
                    qsci.SCI_TAB:                   qsci.SCK_TAB      | SCI_NORM,
                    qsci.SCI_BACKTAB:               qsci.SCK_TAB      | SCI_SHIFT,
                    qsci.SCI_NEWLINE:               qsci.SCK_RETURN   | SCI_NORM,
                    qsci.SCI_NEWLINE:               qsci.SCK_RETURN   | SCI_SHIFT,
                    qsci.SCI_ZOOMIN:                qsci.SCK_ADD      | SCI_CTRL,
                    qsci.SCI_ZOOMOUT:               qsci.SCK_SUBTRACT | SCI_CTRL,
                    qsci.SCI_SETZOOM:               qsci.SCK_DIVIDE   | SCI_CTRL,
                    qsci.SCI_LINECUT:               ord('L')          | SCI_CTRL,
                    qsci.SCI_LINEDELETE:            ord('L')          | SCI_CSHIFT,
                    qsci.SCI_LINECOPY:              ord('T')          | SCI_CSHIFT,
                    qsci.SCI_LINETRANSPOSE:         ord('T')          | SCI_CTRL,
                    qsci.SCI_SELECTIONDUPLICATE:    ord('D')          | SCI_CTRL,
                    qsci.SCI_LOWERCASE:             ord('U')          | SCI_CTRL,
                    qsci.SCI_UPPERCASE:             ord('U')          | SCI_CSHIFT,
                  }

currentShortcuts = copy.copy(_DEFAULT_KEYMAP)

_QSCI_TO_QT_KEY = {
                    qsci.SCK_ADD         : Qt.Key_Plus,
                    qsci.SCK_BACK        : Qt.Key_Backspace,
                    qsci.SCK_DELETE      : Qt.Key_Delete,
                    qsci.SCK_DIVIDE      : Qt.Key_Slash,
                    qsci.SCK_DOWN        : Qt.Key_Down,
                    qsci.SCK_END         : Qt.Key_End,
                    qsci.SCK_ESCAPE      : Qt.Key_Escape,
                    qsci.SCK_HOME        : Qt.Key_Home,
                    qsci.SCK_INSERT      : Qt.Key_Insert,
                    qsci.SCK_LEFT        : Qt.Key_Left,
                    qsci.SCK_MENU        : Qt.Key_Menu,
                    qsci.SCK_NEXT        : Qt.Key_PageDown,
                    qsci.SCK_PRIOR       : Qt.Key_PageUp,
                    qsci.SCK_RETURN      : Qt.Key_Enter,
                    qsci.SCK_RIGHT       : Qt.Key_Right,
                    qsci.SCK_RWIN        : 0,
                    qsci.SCK_SUBTRACT    : Qt.Key_Minus,
                    qsci.SCK_TAB         : Qt.Key_Tab,
                    qsci.SCK_UP          : Qt.Key_Up,
                    qsci.SCK_WIN         : 0,
                    ord('/')             : Qt.Key_Slash,
                    ord('[')             : Qt.Key_BracketLeft,
                    ord(']')             : Qt.Key_BracketRight,
                    ord('\\')            : Qt.Key_Backslash,
                    0                    : 0,
                  }
_QT_TO_QSCI_KEY = dict((v,k) for k, v in _QSCI_TO_QT_KEY.iteritems())

_QSCI_TO_QT_MODIFIER = {
                        SCI_NORM    : 0,
                        SCI_ALT     : Qt.AltModifier,
                        SCI_CTRL    : Qt.ControlModifier,
                        SCI_SHIFT   : Qt.ShiftModifier,
                        SCI_CSHIFT  : int (Qt.ControlModifier | Qt.AltModifier),
                        SCI_ASHIFT  : int (Qt.AltModifier | Qt.ShiftModifier),
                        SCI_ACSHIFT : int (Qt.AltModifier | Qt.ShiftModifier | Qt.ControlModifier),
                       }
_QT_TO_QSCI_MODIFIER = dict((v,k) for k, v in _QSCI_TO_QT_MODIFIER.iteritems())


class QsciAction:
    def __init__(self, actionCode, text):
        self.actionCode = actionCode
        self.text = text
        self.menu = None
    
    def shortcut(self):
        if self.actionCode in currentShortcuts:
            qsciKey = currentShortcuts[self.actionCode]
            qtSeq = sciToQt(qsciKey)
            return qtSeq.toString()
        else:
            return ''

    def defaultShortcut(self):
        if self.actionCode in _DEFAULT_KEYMAP:
            qsciKey = _DEFAULT_KEYMAP[self.actionCode]
            qtSeq = sciToQt(qsciKey)
            return qtSeq.toString()
        else:
            return ''

    def setShortcut(self, shortcut):
        """Set shortcut for the action, identified by the index
        """
        qtKeySeq = QKeySequence(shortcut)
        qtKey = qtKeySeq[0]
        qsciCode = qtToQsci(qtKey)
        currentShortcuts[self.actionCode] = qsciCode
    
    def isDefaultShortcut(self):
        """Check if shortcut for action is default
        """
        return self.shortcut() == self.defaultShortcut()

ACTION_TYPE = True

class QsciMenu:
    def __init__(self, text, actions):
        self.text = text
        self.actions = actions

MENU_TYPE = False

_SHORTCUTS = (
                QsciMenu(tr("Selection"), (
                                    QsciAction(qsci.SCI_LINEDOWNEXTEND, tr("Extend selection down one line")),
                                    QsciAction(qsci.SCI_LINEDOWNRECTEXTEND, tr("Extend rectangular selection down one line")),
                                    QsciAction(qsci.SCI_LINESCROLLDOWN, tr("Scroll view down one line")),
                                    QsciAction(qsci.SCI_LINEUPEXTEND, tr("Extend selection up")),
                                    QsciAction(qsci.SCI_LINEUPRECTEXTEND, tr("Extend selection up one line")),
                                    QsciAction(qsci.SCI_PARADOWNEXTEND, tr("Extend selection up one paragraph")),
                                    QsciAction(qsci.SCI_CHARLEFTEXTEND, tr("Extend selection left one character")),
                                    QsciAction(qsci.SCI_CHARLEFTRECTEXTEND, tr("Extend rectangular selection left one character")),
                                    QsciAction(qsci.SCI_CHARRIGHTEXTEND, tr("Extend selection right one character")),
                                    QsciAction(qsci.SCI_CHARRIGHTRECTEXTEND, tr("Extend rectangular selection right one character")),
                                    QsciAction(qsci.SCI_PARAUPEXTEND, tr("Extend selection down one paragraph")),
                                    QsciAction(qsci.SCI_WORDLEFTEXTEND, tr("Extend selection left one word")),
                                    QsciAction(qsci.SCI_WORDRIGHTEXTEND, tr("Extend selection right one word")),
                                    QsciAction(qsci.SCI_WORDLEFTENDEXTEND, tr("Extend selection left one word left")),
                                    QsciAction(qsci.SCI_WORDRIGHTENDEXTEND, tr("Extend selection right one word end")),
                                    QsciAction(qsci.SCI_WORDPARTLEFTEXTEND, tr("Extend selection left one word part ")),
                                    QsciAction(qsci.SCI_WORDPARTRIGHTEXTEND, tr("Extend selection right one word part")),
                                    QsciAction(qsci.SCI_HOMEEXTEND, tr("Extend selection to line start")),
                                    QsciAction(qsci.SCI_HOMERECTEXTEND, tr("Extend rectangular selection to line start")),
                                    QsciAction(qsci.SCI_HOMEDISPLAYEXTEND, tr("Extend selection start of displayed line")),
                                    QsciAction(qsci.SCI_HOMEWRAPEXTEND, tr("Extend selection on home wrap")),
                                    QsciAction(qsci.SCI_VCHOMERECTEXTEND, tr("Extend rectangular selection to firts VC in line")),
                                    QsciAction(qsci.SCI_VCHOMEWRAPEXTEND, tr("Extend selection VC Home wrap")),
                                    QsciAction(qsci.SCI_LINEENDEXTEND, tr("Extend selection to end of line")),
                                    QsciAction(qsci.SCI_LINEENDRECTEXTEND, tr("Extend rectangular selection to end of line")),
                                    QsciAction(qsci.SCI_LINEENDDISPLAYEXTEND, tr("Extend selection to end of displayed line")),
                                    QsciAction(qsci.SCI_LINEENDWRAPEXTEND, tr("Extend selection to line end wrap")),
                                    QsciAction(qsci.SCI_DOCUMENTSTARTEXTEND, tr("Extend selection to document start")),
                                    QsciAction(qsci.SCI_DOCUMENTENDEXTEND, tr("Extend selection to document end")),
                                    QsciAction(qsci.SCI_PAGEDOWNEXTEND, tr("Extend selection down one page")),
                                    QsciAction(qsci.SCI_PAGEDOWNRECTEXTEND, tr("Extend rectangular selection down one page")),
                                    QsciAction(qsci.SCI_STUTTEREDPAGEUPEXTEND, tr("Extend selection up one page stuttered")),
                                    QsciAction(qsci.SCI_PAGEUPEXTEND, tr("Extend selection up one page")),
                                    QsciAction(qsci.SCI_PAGEUPRECTEXTEND, tr("Extend rectangular selection up one page")),
                                    QsciAction(qsci.SCI_STUTTEREDPAGEDOWNEXTEND, tr("Extend selection down one page stuttered")),
                                  ),
                ),
                QsciMenu(tr("Navigation"), (
                                    QsciAction(qsci.SCI_LINESCROLLUP, tr("Scroll view up one line")),
                                    QsciAction(qsci.SCI_PARADOWN, tr("Move down one paragraph")),
                                    QsciAction(qsci.SCI_PARAUP, tr("Move down one paragraph")),
                                    QsciAction(qsci.SCI_WORDLEFT, tr("Move left one word")),
                                    QsciAction(qsci.SCI_WORDRIGHT, tr("Move right one word")),
                                    QsciAction(qsci.SCI_WORDLEFTEND, tr("Move left one word end")),
                                    QsciAction(qsci.SCI_WORDRIGHTEND, tr("Move right one word end")),
                                    QsciAction(qsci.SCI_WORDPARTLEFT, tr("Move left one word part")),
                                    QsciAction(qsci.SCI_WORDPARTRIGHT, tr("Move right one word part")),
                                    QsciAction(qsci.SCI_HOME, tr("Move to line start")),
                                    QsciAction(qsci.SCI_HOMEDISPLAY, tr("Move to start of displayed line")),
                                    QsciAction(qsci.SCI_HOMEWRAP, tr("Home wrap")),
                                    QsciAction(qsci.SCI_VCHOME, tr("Move to firsst VC in line")),
                                    QsciAction(qsci.SCI_VCHOMEEXTEND, tr("Extend selection to first VC in line")),
                                    QsciAction(qsci.SCI_VCHOMEWRAP, tr("VC Home wrap")),
                                    QsciAction(qsci.SCI_LINEEND, tr("Move to end of line")),
                                    QsciAction(qsci.SCI_LINEENDDISPLAY, tr("Move to end displayed line")),
                                    QsciAction(qsci.SCI_LINEENDWRAP, tr("Move to line end wrap")),
                                    QsciAction(qsci.SCI_DOCUMENTSTART, tr("Move to document start")),
                                    QsciAction(qsci.SCI_DOCUMENTEND, tr("Move to document end")),
                                    QsciAction(qsci.SCI_PAGEUP, tr("Move up one page")),
                                    QsciAction(qsci.SCI_PAGEDOWN, tr("Move down one page")),
                                    QsciAction(qsci.SCI_STUTTEREDPAGEUP, tr("Move up one page stuttered")),
                                    QsciAction(qsci.SCI_STUTTEREDPAGEDOWN, tr("Move down one page stuttered")),
                                  ),
                ),
                QsciMenu(tr("Edit"), (
                              QsciAction(qsci.SCI_DELETEBACKNOTLINE, tr("Backspace not a line")),
                              QsciAction(qsci.SCI_DELWORDLEFT, tr("Delete previous word")),
                              QsciAction(qsci.SCI_DELWORDRIGHT, tr("Delete next word")),
                              QsciAction(qsci.SCI_DELLINELEFT, tr("Delete line tp left")),
                              QsciAction(qsci.SCI_DELLINERIGHT, tr("Delete line to right")),
                              QsciAction(qsci.SCI_LINEDELETE, tr("Delete line")),
                              QsciAction(qsci.SCI_LINECUT, tr("Cut line")),
                              QsciAction(qsci.SCI_LINECOPY, tr("Copy line")),
                              QsciAction(qsci.SCI_LINETRANSPOSE, tr("Swap current and previous line")),
                              QsciAction(qsci.SCI_LINEDUPLICATE, tr("Duplicate line")),
                              QsciAction(qsci.SCI_LOWERCASE, tr("To lower case")),
                              QsciAction(qsci.SCI_UPPERCASE, tr("To upper case")),
                              QsciAction(qsci.SCI_EDITTOGGLEOVERTYPE, tr("Edit toggle over type")),
                              QsciAction(qsci.SCI_FORMFEED, tr("Formfeed")),
                              QsciAction(qsci.SCI_BACKTAB, tr("Delete one indent")),
                              QsciAction(qsci.SCI_SELECTIONDUPLICATE, tr("Duplicate selection")),
                              QsciAction(qsci.SCI_CLEAR, tr("Delete")),
                              QsciAction(qsci.SCI_SELECTALL, tr("Select All")),
                             ),
                ),
                QsciMenu(tr("Zoom"), (
                              QsciAction(qsci.SCI_ZOOMIN, tr("Zoom In")),
                              QsciAction(qsci.SCI_ZOOMOUT, tr("Zoom Out")),
                              QsciAction(qsci.SCI_SETZOOM, tr("Set Zoom")),
                             ),
                ),
                QsciMenu(tr("Bookmarks"),
                             (
                              QsciAction(qsci.SCI_MARKERADD, tr("Set bookmark")),
                              QsciAction(qsci.SCI_MARKERDELETEALL, tr( "Delete all bookmarks" )),
                              QsciAction(qsci.SCI_MARKERPREVIOUS, tr( "Previous bookmark" )),
                              QsciAction(qsci.SCI_MARKERNEXT, tr( "Next bookmark")),
                             ),
                            ),
             )

for menu in _SHORTCUTS:
    for action in menu.actions:
        action.menu = menu

def sciToQt(key):
    modifier = key & 0xffff0000
    code = key & 0x0000ffff
    if code in range(ord('A'), ord('Z')):
        qtCode = Qt.Key_A + (code - ord('A'))
    else:
        qtCode = _QSCI_TO_QT_KEY[code]
    qtModifier = _QSCI_TO_QT_MODIFIER[modifier]
    return QKeySequence(qtModifier + qtCode)

def qtToQsci(key):
    code = key & 0x1ffffff
    modifier = key & 0xfe000000
    if code in range(Qt.Key_A, Qt.Key_Z):
        qsciCode = ord('A') + (code - Qt.Key_A)
    else:
        qsciCode = _QT_TO_QSCI_KEY[code]
    qsciModifier = _QT_TO_QSCI_MODIFIER[modifier]
    return qsciModifier + qsciCode

class EditorShortcutsModel(QAbstractItemModel):
    """Class implements list of actions, visible in the tree view
    """
    def __init__(self, dialog, *args):
        QAbstractItemModel.__init__(self, *args)
        self._dialog = dialog

    def isRoot(self, index):
        return not index.isValid()
    
    def isMenu(self, index):
        return index.internalPointer() == MENU_TYPE
    
    def isAction(self, index):
        return index.internalPointer() == ACTION_TYPE
    
    def menu(self, index):
        return _SHORTCUTS[index.row()]

    def action(self, index):
        menu = self.menu(index.parent())
        return menu.actions[index.row()]
    
    def columnCount(self, parent):
        return 3

    def data(self, index, role ):
        if not index.isValid():
            return None
        
        if self.isAction(index):  # action
            action = self.action(index)
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if index.column() == 0:  # name
                    return action.text
                elif index.column() == 1:  # shortcut
                    return action.shortcut()
                elif index.column() == 2: # default shortcut
                    return action.defaultShortcut()
            else:  # not supported role
                return None
        else:
            assert(self.isMenu(index))
            if role in (Qt.DisplayRole, Qt.ToolTipRole):
                if index.column() == 0:
                    return self.menu(index).text
                else:
                    return None

    def index(self, row, column, parent):
        if self.isMenu(parent):  # create index for an action
            menu = self.menu(parent)
            index = self.createIndex(row, column, MENU_TYPE)
            assert(self.isAction(index))
        else:  # create index for a menu
            assert(self.isRoot(parent))
            index = self.createIndex(row, column, ACTION_TYPE)
            print 'xx'
            print index.internalPointer()
            print 'yy'
            assert(self.isMenu(index))
        assert(index.isValid())
        return index

    def parent(self, index):
        if self.isAction(index):
            menu = self.action(index).menu
            return self.createIndex(_SHORTCUTS.index(menu), 0)
        else:
            return QModelIndex()

    def rowCount(self, parent):
        if self.isAction(parent):
            return 0
        elif self.isMenu(parent):
            menu = self.menu(parent)
            return len(menu.actions)
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
    
    def __init__(self, *args):
        QDialog.__init__(self, *args)
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


    def selectedAction(self):
        """Get currently selected action
        """
        indexes = self.tvActions.selectionModel().selectedIndexes()
        if indexes:
            index = indexes[0]
            if self._model.isAction(index):
                return self._model.action(index)
        return None

    def tvActions_selectionModel_selectionChanged(self):
        """Selection changed in the list
        """
        action = self.selectedAction()
        if action is not None:
            self.kseShortcut.setText(action.shortcut())
            self.kseShortcut.setEnabled(True)
            self.tbClear.setEnabled(self.shortcut(index))
            self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not action.isDefaultShortcut())
        else:
            self.kseShortcut.clear()
            self.tbClear.setEnabled(False)
            self.dbbButtons.button(False)
        
        self.tbSet.setEnabled(False)        
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( False )
        self.kseShortcut.setFocus()

    def on_kseShortcut_textChanged(self, text):
        """Text has been changed in the shortcut input
        """
        action = self.selectedAction()
        self.tbSet.setEnabled( bool(self.kseShortcut.text()) )
        self.dbbButtons.button( QDialogButtonBox.Reset ).setEnabled( True )
        self.dbbButtons.button( QDialogButtonBox.RestoreDefaults ).setEnabled(not action.isDefaultShortcut())

    def on_tbSet_clicked(self):
        """*Set* button has been clicked
        """
        action = self.selectedAction()
        if self.kseShortcut.text():
            self.setShortcut(action[0], self.kseShortcut.text())

    def on_tbClear_clicked(self):
        """*Clear* button has been clicked
        """
        action = self.selectedAction()
        action.setShortcut('')

    def on_dbbButtons_clicked(self, button ):
        """One of dialog button box buttons has been clicked
        """
        stButton = self.dbbButtons.standardButton( button )
        if stButton == QDialogButtonBox.Reset:
            self.tvActions_selectionModel_selectionChanged()
        elif stButton == QDialogButtonBox.RestoreDefaults:
            action = self.selectedAction()
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
        action.triggered.connect(self.exec_)
    
    def __term__(self):
        core.actionModel().removeAction("mEdit/aEditorShortcuts")

    def exec_(self):
        EditorShortcutsDialog(core.mainWindow()).exec_()
