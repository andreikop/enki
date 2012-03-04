"""
searchresultsdock --- Search results dock widget
================================================

Shows results with SearchResultsModel
"""

from PyQt4.QtGui import QHBoxLayout, QIcon, \
                        QTreeView, QWidget
from mks.fresh.dockwidget.pDockWidget import pDockWidget
from mks.core.core import core

import searchresultsmodel

class SearchResultsDock(pDockWidget):
    """Dock with search results
    """
    def __init__(self, searchThread, parent=None):
        pDockWidget.__init__( self, parent )
        self.setObjectName("SearchResultsDock")
        assert(searchThread)

        self.searchThread = searchThread

        self.setObjectName( self.metaObject().className() )
        self.setWindowTitle( self.tr( "&Search Results" ) )
        self.setWindowIcon( QIcon(":/mksicons/search.png") )
        
        # actions
        widget = QWidget( self )
        self.model = searchresultsmodel.SearchResultsModel( searchThread, self )
        self._view = QTreeView( self )
        self._view.setHeaderHidden( True )
        self._view.setUniformRowHeights( True )
        self._view.setModel( self.model )
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
        self.model.firstResultsAvailable.connect(self.show)
        self._view.activated.connect(self.view_activated)
        
        self.showAction().setShortcut("Alt+S")
        core.actionManager().addAction("mDocks/aSearchResults", self.showAction())

    def del_(self):
        core.actionManager().removeAction("mDocks/aSearchResults")

    def view_activated(self, index ):
        """Item doubleclicked in the model, opening file
        """
        result = index.internalPointer()
        if isinstance(result, searchresultsmodel.Result):
            core.workspace().goTo( result.fileName,
                                   result.line,
                                   result.column,
                                   len(result.match.group(0)))
