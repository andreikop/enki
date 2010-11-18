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

SearchResultsDock::SearchResultsDock( SearchThread* searchThread, QWidget* parent )
	: pDockWidget( parent )
{
	Q_ASSERT( searchThread );

	mSearchThread = searchThread;

	setObjectName( metaObject()->className() );
	setWindowTitle( tr( "Search Results" ) );
	setWindowIcon( pIconManager::icon( "SearchAndReplace.png", ":/icons" ) );
	
	// actions
	// clear action
	QAction* aClear = new QAction( tr( "Clear results list" ), this );
	aClear->setIcon( pIconManager::icon( "clear-list.png", ":/icons" ) );
	aClear->setToolTip( aClear->text() );
	titleBar()->addAction( aClear, 0 );
	
	// add separator
	titleBar()->addSeparator( 1 );

	QWidget* widget = new QWidget( this );
	mModel = new SearchResultsModel( searchThread, this );
	mView = new QTreeView( this );
	mView->setHeaderHidden( true );
	mView->setUniformRowHeights( true );
	mView->setModel( mModel );
	mLayout = new QHBoxLayout( widget );
	mLayout->setMargin( 5 );
	mLayout->setSpacing( 5 );
	mLayout->addWidget( mView );

	setWidget( widget );

	// mac
	pMonkeyStudio::showMacFocusRect( this, false, true );
	pMonkeyStudio::setMacSmallSize( this, true, true );

	// connections
	connect( aClear, SIGNAL( triggered() ), mModel, SLOT( clear() ) );
	connect( mModel, SIGNAL( firstResultsAvailable() ), this, SLOT( show() ) );
	connect( mView, SIGNAL( activated( const QModelIndex& ) ), this, SLOT( view_activated( const QModelIndex& ) ) );
}

SearchResultsModel* SearchResultsDock::model() const
{
	return mModel;
}

void SearchResultsDock::view_activated( const QModelIndex& index )
{
	SearchResultsModel::Result* result = static_cast<SearchResultsModel::Result*>( index.internalPointer() );
	MonkeyCore::fileManager()->goToLine( result->fileName, result->position, mSearchThread->properties()->codec, result->offset == -1 ? 0 : result->length );
}
