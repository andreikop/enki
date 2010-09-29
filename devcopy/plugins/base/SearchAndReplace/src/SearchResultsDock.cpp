#include "SearchResultsDock.h"
#include "SearchThread.h"
#include "SearchResultsModel.h"

#include <objects/pIconManager.h>
#include <pMonkeyStudio.h>
#include <coremanager/MonkeyCore.h>
#include <workspace/pFileManager.h>
#include <widgets/pDockWidgetTitleBar.h>

#include <QHBoxLayout>
#include <QTreeView>

SearchResultsDock.SearchResultsDock( SearchThread* searchThread, parent )
    : pDockWidget( parent )
    Q_ASSERT( searchThread )

    mSearchThread = searchThread

    setObjectName( metaObject().className() )
    setWindowTitle( tr( "Search Results" ) )
    setWindowIcon( pIconManager.icon( "SearchAndReplace.png", ":/icons" ) )
    
    # actions
    # clear action
    aClear = QAction( tr( "Clear results list" ), self )
    aClear.setIcon( pIconManager.icon( "clear-list.png", ":/icons" ) )
    aClear.setToolTip( aClear.text() )
    titleBar().addAction( aClear, 0 )
    
    # add separator
    titleBar().addSeparator( 1 )

    widget = QWidget( self )
    mModel = SearchResultsModel( searchThread, self )
    mView = QTreeView( self )
    mView.setHeaderHidden( True )
    mView.setUniformRowHeights( True )
    mView.setModel( mModel )
    mLayout = QHBoxLayout( widget )
    mLayout.setMargin( 5 )
    mLayout.setSpacing( 5 )
    mLayout.addWidget( mView )

    setWidget( widget )

    # mac
    pMonkeyStudio.showMacFocusRect( self, False, True )
    pMonkeyStudio.setMacSmallSize( self, True, True )

    # connections
    aClear.triggered.connect(mModel.clear)
    mModel.firstResultsAvailable.connect(self.show)
    mView.activated.connect(self.view_activated)


def model(self):
    return mModel


def view_activated(self, index ):
    result = static_cast<SearchResultsModel.Result*>( index.internalPointer() )
    MonkeyCore.fileManager().goToLine( result.fileName, result.position, mSearchThread.properties().codec, result.offset == -1 ? 0 : result.length )

