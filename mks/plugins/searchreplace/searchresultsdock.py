"""
searchresultsdock --- Search results dock widget
================================================

Shows results with SearchResultsModel
"""

from PyQt4.QtCore import Qt, pyqtSignal, QModelIndex
from PyQt4.QtGui import QFontMetrics, QHBoxLayout, QIcon, \
                        QTreeView, QWidget, QPushButton
from mks.fresh.dockwidget.pDockWidget import pDockWidget
from mks.core.core import core

import searchresultsmodel


from PyQt4 import QtGui
from PyQt4 import QtCore
class HTMLDelegate(QtGui.QStyledItemDelegate):
    #http://stackoverflow.com/questions/1956542/how-to-make-item-view-render-rich-html-text-in-qt/1956781#1956781
    def paint(self, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)

        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()

        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(1)
        doc.setHtml(options.text)

        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter);

        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()

        # Highlighting text if item is selected
        #if (optionV4.state & QStyle::State_Selected)
            #ctx.palette.setColor(QPalette::Text, optionV4.palette.color(QPalette::Active, QPalette::HighlightedText));

        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)

        painter.restore()

    def sizeHint(self, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)

        doc = QtGui.QTextDocument()
        doc.setDocumentMargin(1)
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        return QtCore.QSize(doc.idealWidth(), doc.size().height())

class ExpandCollapseAllButton(QPushButton):
    """Expand all/Collapse all button and functionality
    """
    def __init__(self, toolBar, view, model):
        QPushButton.__init__(self, QIcon(':mksicons/scope.png'), "<to be set>", toolBar)
        toolBar.insertWidget(toolBar.actions()[0], self)
        self.setMinimumWidth(QFontMetrics(self.font()).width("Colla&pse all)") + 36)
        self.setStyleSheet("padding: 0")
        self.setFlat(True)
        self._view = view
        self._model = model
        self.clicked.connect(self._onTriggered)
        self._view.expanded.connect(self._updateText)
        self._view.collapsed.connect(self._updateText)
        self._model.rowsInserted.connect(self._updateText)
        self._updateText()
    
    def _updateText(self):
        """Update action text according to expanded state of the first item
        """
        if self._isFirstFileExpanded():
            self.setText("Colla&pse all")
        else:
            self.setText("Ex&pand all")
            
    def _onTriggered(self):
        """Expand or colapse all search results
        """
        self._view.expanded.disconnect(self._updateText)
        self._view.collapsed.disconnect(self._updateText)

        if self._isFirstFileExpanded():
            self._view.collapseAll()
        else:
            self._view.expandAll()
        self._updateText()
        self._view.setFocus()
        
        self._view.expanded.connect(self._updateText)
        self._view.collapsed.connect(self._updateText)

    def _isFirstFileExpanded(self):
        """Check if first file in the search results is expanded
        """
        return self._view.isExpanded(self._model.index(0, 0, QModelIndex()))


class CheckUncheckAllButton(QPushButton):
    """Check/Uncheck all matches button for replace mode
    """
    def __init__(self, toolBar, view, model):
        QPushButton.__init__(self, QIcon(':mksicons/button-ok.png'), "<to be set>", toolBar)
        self._action = toolBar.insertWidget(toolBar.actions()[1], self)
        self.setMinimumWidth(QFontMetrics(self.font()).width("Uncheck all)") + 36)
        self.setStyleSheet("padding: 0")
        self.setFlat(True)
        self._view = view
        self._model = model
        self.clicked.connect(self._onTriggered)
        self._model.dataChanged.connect(self._updateText)
        self._model.rowsInserted.connect(self._updateText)
        self._updateText()
    
    def _updateText(self):
        """Update action text according to expanded state of the first item
        """
        if self._model.isFirstMatchChecked():
            self.setText("Unc&heck all")
        else:
            self.setText("C&heck all")
    
    def _onTriggered(self):
        """Expand or colapse all search results
        """
        self._model.dataChanged.disconnect(self._updateText)
        if self._model.isFirstMatchChecked():
            self._model.setCheckStateForAll(Qt.Unchecked)
        else:
            self._model.setCheckStateForAll(Qt.Checked)
        self._updateText()
        self._view.setFocus()
        self._model.dataChanged.connect(self._updateText)
    
    def show(self):
        """Show on tool bar
        """
        self._action.setVisible(True)

    def hide(self):
        """Hide on tool bar
        """
        self._action.setVisible(False)


class SearchResultsDock(pDockWidget):
    """Dock with search results
    """
    
    onResultsHandledByReplaceThread = pyqtSignal(str, list)

    def __init__(self, parent=None):
        pDockWidget.__init__( self, parent )
        self.setObjectName("SearchResultsDock")

        self.setObjectName( self.metaObject().className() )
        self.setWindowTitle( self.tr( "&Search Results" ) )
        self.setWindowIcon( QIcon(":/mksicons/search.png") )
        
        # actions
        widget = QWidget( self )
        
        self._model = searchresultsmodel.SearchResultsModel(self)
        self.onResultsHandledByReplaceThread.connect(self._model.onResultsHandledByReplaceThread)

        self._view = QTreeView( self )
        self._view.setHeaderHidden( True )
        self._view.setUniformRowHeights( True )
        self._view.setModel( self._model )
        self._delegate = HTMLDelegate()
        self._view.setItemDelegate(self._delegate)
        
        self._layout = QHBoxLayout( widget )
        self._layout.setMargin( 5 )
        self._layout.setSpacing( 5 )
        self._layout.addWidget( self._view )

        self.setWidget( widget )
        self.setFocusProxy(self._view)
        
        # TODO PasNox, check if we need it on mac
        # mac
        #self.pMonkeyStudio.showMacFocusRect( self, False, True )
        #pMonkeyStudio.setMacSmallSize( self, True, True )

        # connections
        self._model.firstResultsAvailable.connect(self.show)
        self._view.activated.connect(self._onResultActivated)
        
        self.showAction().setShortcut("Alt+S")
        core.actionManager().addAction("mDocks/aSearchResults", self.showAction())
        
        self._expandCollapseAll = ExpandCollapseAllButton(self.titleBar(), self._view, self._model)
        self._checkUncheckAll = None

    def del_(self):
        core.actionManager().removeAction("mDocks/aSearchResults")

    def _onResultActivated(self, index ):
        """Item doubleclicked in the model, opening file
        """
        result = index.internalPointer()
        if isinstance(result, searchresultsmodel.Result):
            fileResults = index.parent().internalPointer()
            core.workspace().goTo( result.fileName,
                                   line=result.line,
                                   column=result.column,
                                   selectionLength=len(result.match.group(0)))
            core.mainWindow().statusBar().showMessage('Match %d of %d' % \
                                                      (fileResults.results.index(result) + 1,
                                                       len(fileResults.results)), 1000)
            self.setFocus()

    def clear(self):
        """Clear themselves
        """
        self._model.clear()
    
    def appendResults(self, fileResultList):
        """Append results. Handler for signal from the search thread
        """
        self._model.appendResults(fileResultList)

    def getCheckedItems(self):
        """Get items, which must be replaced, as dictionary {file name : list of items}
        """
        items = {}

        for fileRes in self._model.fileResults:
            for row, result in enumerate(fileRes.results):
                if result.checkState == Qt.Checked :
                    if not result.fileName in items: 
                        items[result.fileName] = []
                    items[ result.fileName ].append(result)
        return items

    def setReplaceMode(self, enabled):
        """When replace mode is enabled, dock shows checkbox near every item
        """
        self._model.setReplaceMode(enabled)
        self._view.update()  # redraw the model
        if enabled:
            if self._checkUncheckAll is None:
                self._checkUncheckAll = CheckUncheckAllButton(self.titleBar(), self._view, self._model)
            self._checkUncheckAll.show()
        else:
            if self._checkUncheckAll is not None:
                self._checkUncheckAll.hide()
    
    def matchesCount(self):
        """Get count of matches, stored by the model
        """
        return self._model.matchesCount()
