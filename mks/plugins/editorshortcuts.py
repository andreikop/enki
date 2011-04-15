"""
editorshortcuts --- Manages QScintilla shortcuts
================================================

Contains editor dialog and functionality for load and save the shortcuts
"""

import os.path

from PyQt4 import uic
from PyQt4.QtCore import QAbstractItemModel, QModelIndex, Qt, QObject, QVariant
from PyQt4.QtGui import QDialog, QDialogButtonBox, QHeaderView

from PyQt4.Qsci import QsciScintilla

from mks.core.core import core, DATA_FILES_PATH

def tr(s):
    # FIXME add translation
    return s

_SHORTCUTS = ((QsciScintilla.SCI_LINEDOWNEXTEND, tr("Extend selection down one line")),  
              (QsciScintilla.SCI_LINEDOWNRECTEXTEND, tr("Extend rectangular selection down one line")),  
              (QsciScintilla.SCI_LINESCROLLDOWN, tr("Scroll view down one line")),  
              (QsciScintilla.SCI_LINEUPEXTEND, tr("Extend selection up")),  
              (QsciScintilla.SCI_LINEUPRECTEXTEND, tr("Extend selection up one line")),  
              (QsciScintilla.SCI_LINESCROLLUP, tr("Scroll view up one line")),  
              (QsciScintilla.SCI_PARADOWN, tr("Move down one paragraph")),  
              (QsciScintilla.SCI_PARADOWNEXTEND, tr("Extend selection up one paragraph")),  
              (QsciScintilla.SCI_PARAUP, tr("Move down one paragraph")),  
              (QsciScintilla.SCI_PARAUPEXTEND, tr("Extend selection down one paragraph")),  
              (QsciScintilla.SCI_CHARLEFTEXTEND, tr("Extend selection left one character")),  
              (QsciScintilla.SCI_CHARLEFTRECTEXTEND, tr("Extend rectangular selection left one character")),  
              (QsciScintilla.SCI_CHARRIGHTEXTEND, tr("Extend selection right one character")),  
              (QsciScintilla.SCI_CHARRIGHTRECTEXTEND, tr("Extend rectangular selection right one character")),  
              (QsciScintilla.SCI_WORDLEFT, tr("Move left one word")),  
              (QsciScintilla.SCI_WORDLEFTEXTEND, tr("Extend selection left one word")),  
              (QsciScintilla.SCI_WORDRIGHT, tr("Move right one word")),  
              (QsciScintilla.SCI_WORDRIGHTEXTEND, tr("Extend selection right one word")),  
              (QsciScintilla.SCI_WORDLEFTEND, tr("Move left one word end")),  
              (QsciScintilla.SCI_WORDLEFTENDEXTEND, tr("Extend selection left one word left")),  
              (QsciScintilla.SCI_WORDRIGHTEND, tr("Move right one word end")),  
              (QsciScintilla.SCI_WORDRIGHTENDEXTEND, tr("Extend selection right one word end")),  
              (QsciScintilla.SCI_WORDPARTLEFT, tr("Move left one word part")),  
              (QsciScintilla.SCI_WORDPARTLEFTEXTEND, tr("Extend selection left one word part ")),  
              (QsciScintilla.SCI_WORDPARTRIGHT, tr("Move right one word part")),  
              (QsciScintilla.SCI_WORDPARTRIGHTEXTEND, tr("Extend selection right one word part")),  
              (QsciScintilla.SCI_HOME, tr("Move to line start")),  
              (QsciScintilla.SCI_HOMEEXTEND, tr("Extend selection to line start")),  
              (QsciScintilla.SCI_HOMERECTEXTEND, tr("Extend rectangular selection to line start")),  
              (QsciScintilla.SCI_HOMEDISPLAY, tr("Move to start of displayed line")),  
              (QsciScintilla.SCI_HOMEDISPLAYEXTEND, tr("Extend selection start of displayed line")),  
              (QsciScintilla.SCI_HOMEWRAP, tr("Home wrap")),  
              (QsciScintilla.SCI_HOMEWRAPEXTEND, tr("Extend selection on home wrap")),  
              (QsciScintilla.SCI_VCHOME, tr("Move to firsst VC in line")),  
              (QsciScintilla.SCI_VCHOMEEXTEND, tr("Extend selection to first VC in line")),  
              (QsciScintilla.SCI_VCHOMERECTEXTEND, tr("Extend rectangular selection to firts VC in line")),  
              (QsciScintilla.SCI_VCHOMEWRAP, tr("VC Home wrap")),  
              (QsciScintilla.SCI_VCHOMEWRAPEXTEND, tr("Extend selection VC Home wrap")),  
              (QsciScintilla.SCI_LINEEND, tr("Move to end of line")),  
              (QsciScintilla.SCI_LINEENDEXTEND, tr("Extend selection to end of line")),  
              (QsciScintilla.SCI_LINEENDRECTEXTEND, tr("Extend rectangular selection to end of line")),  
              (QsciScintilla.SCI_LINEENDDISPLAY, tr("Move to end displayed line")),  
              (QsciScintilla.SCI_LINEENDDISPLAYEXTEND, tr("Extend selection to end of displayed line")),  
              (QsciScintilla.SCI_LINEENDWRAP, tr("Move to line end wrap")),  
              (QsciScintilla.SCI_LINEENDWRAPEXTEND, tr("Extend selection to line end wrap")),  
              (QsciScintilla.SCI_DOCUMENTSTART, tr("Move to document start")),  
              (QsciScintilla.SCI_DOCUMENTSTARTEXTEND, tr("Extend selection to document start")),  
              (QsciScintilla.SCI_DOCUMENTEND, tr("Move to document end")),  
              (QsciScintilla.SCI_DOCUMENTENDEXTEND, tr("Extend selection to document end")),  
              (QsciScintilla.SCI_PAGEUP, tr("Move up one page")),  
              (QsciScintilla.SCI_PAGEUPEXTEND, tr("Extend selection up one page")),  
              (QsciScintilla.SCI_PAGEUPRECTEXTEND, tr("Extend rectangular selection up one page")),  
              (QsciScintilla.SCI_PAGEDOWN, tr("Move down one page")),  
              (QsciScintilla.SCI_PAGEDOWNEXTEND, tr("Extend selection down one page")),  
              (QsciScintilla.SCI_PAGEDOWNRECTEXTEND, tr("Extend rectangular selection down one page")),  
              (QsciScintilla.SCI_STUTTEREDPAGEUP, tr("Move up one page stuttered")),  
              (QsciScintilla.SCI_STUTTEREDPAGEUPEXTEND, tr("Extend selection up one page stuttered")),  
              (QsciScintilla.SCI_STUTTEREDPAGEDOWN, tr("Move down one page stuttered")),  
              (QsciScintilla.SCI_STUTTEREDPAGEDOWNEXTEND, tr("Extend selection down one page stuttered")),  
              (QsciScintilla.SCI_DELETEBACKNOTLINE, tr("Backspace not a line")),  
              (QsciScintilla.SCI_DELWORDLEFT, tr("Delete previous word")),  
              (QsciScintilla.SCI_DELWORDRIGHT, tr("Delete next word")),  
              (QsciScintilla.SCI_DELLINELEFT, tr("Delete line tp left")),  
              (QsciScintilla.SCI_DELLINERIGHT, tr("Delete line to right")),  
              (QsciScintilla.SCI_LINEDELETE, tr("Delete line")),  
              (QsciScintilla.SCI_LINECUT, tr("Cut line")),  
              (QsciScintilla.SCI_LINECOPY, tr("Copy line")),  
              (QsciScintilla.SCI_LINETRANSPOSE, tr("Swap current and previous line")),  
              (QsciScintilla.SCI_LINEDUPLICATE, tr("Duplicate line")),  
              (QsciScintilla.SCI_LOWERCASE, tr("To lower case")),  
              (QsciScintilla.SCI_UPPERCASE, tr("To upper case")),  
              (QsciScintilla.SCI_EDITTOGGLEOVERTYPE, tr("Edit toggle over type")),  
              (QsciScintilla.SCI_FORMFEED, tr("Formfeed")),  
              (QsciScintilla.SCI_BACKTAB, tr("Delete one indent")),  
              (QsciScintilla.SCI_SELECTIONDUPLICATE, tr("Duplicate selection")),  
              (QsciScintilla.SCI_CLEAR, tr("Delete")),  
              (QsciScintilla.SCI_SELECTALL, tr("Select All")),  
              (QsciScintilla.SCI_ZOOMIN, tr("Zoom In")),  
              (QsciScintilla.SCI_ZOOMOUT, tr("Zoom Out")),  
              (QsciScintilla.SCI_SETZOOM, tr("Set Zoom")),  
              (QsciScintilla.SCI_MARKERADD, tr("Set bookmark")),  
              (QsciScintilla.SCI_MARKERDELETEALL, tr( "Delete all bookmarks" )), 
              (QsciScintilla.SCI_MARKERPREVIOUS, tr( "Previous bookmark" )), 
              (QsciScintilla.SCI_MARKERNEXT, tr( "Next bookmark" )))

class EditorShortcutsModel(QAbstractItemModel):
    """Class implements list of actions, visible in the tree view
    """
    def __init__(self, dialog, *args):
        QAbstractItemModel.__init__(self, *args)
        self._dialog = dialog

    def columnCount(self, parent ):
        return 3

    def data(self, index, role ):
        if role in (Qt.DisplayRole, Qt.ToolTipRole):
            if index.column() == 0:  # name
                return _SHORTCUTS[index.row()][1]
            elif index.column() == 1:  # shortcut
                return self._dialog.shortcut(index)
            elif index.column() == 2: # default shortcut
                return self._dialog.defaultShortcut(index)
        return QVariant()

    def index(self, row, column, parent ):
        if (not row in range(0, len(_SHORTCUTS))) or \
           (not column in range(0, 3)) or \
           parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, parent ):
        if parent.isValid():
            return 0
        return len(_SHORTCUTS)

    def hasChildren(self, parent ):
        if parent.isValid():
            return False
        else:
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
    def __init__(self, *args):
        QDialog.__init__(self, *args)
        self._model = EditorShortcutsModel(self)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/EditorShortcutsDialog.ui'), self)
        self.leFilter.setSearchButtonVisible( False )
        self.leFilter.setPromptText( self.tr( "Text filter..." ) )
        self.tvActions.setModel( self._model )
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
        mProxy.setFilterWildcard( text )
        self.tvActions.expandAll()
