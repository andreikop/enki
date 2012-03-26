"""
searchresultsdock --- Search results dock widget
================================================

Shows results with SearchResultsModel
"""

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QHBoxLayout, QIcon, \
                        QTreeView, QWidget
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

    def del_(self):
        core.actionManager().removeAction("mDocks/aSearchResults")

    def _onResultActivated(self, index ):
        """Item doubleclicked in the model, opening file
        """
        result = index.internalPointer()
        if isinstance(result, searchresultsmodel.Result):
            core.workspace().goTo( result.fileName,
                                   line=result.line,
                                   column=result.column,
                                   selectionLength=len(result.match.group(0)))
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