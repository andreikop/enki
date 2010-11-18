#include "pOpenedFileExplorer.h"
#include "pWorkspace.h"
#include "coremanager/MonkeyCore.h"
#include "maininterface/UIMain.h"

#include <objects/pIconManager.h>
#include <widgets/pDockWidgetTitleBar.h>
#include <widgets/pMenuBar.h>

#include <QWidgetAction>
#include <QComboBox>
#include <QMenu>
#include <QDebug>

class pOpenedFileAction : public QWidgetAction
{
	Q_OBJECT

public:
	pOpenedFileAction( pOpenedFileExplorer* parent, QAbstractItemModel* model )
		: QWidgetAction( parent )
	{
		mOpenedFileExplorer = parent;
		mModel = model;
	}
	
	~pOpenedFileAction()
	{
		qDeleteAll( mCombos );
	}
	
	void syncViewIndex( const QModelIndex& index )
	{
		foreach ( QComboBox* combo, mCombos )
		{
			const bool aSMLocked = combo->view()->selectionModel()->blockSignals( true );
			const bool aLocked = combo->blockSignals( true );
			combo->setCurrentIndex( index.row() );
			combo->view()->selectionModel()->blockSignals( aSMLocked );
			combo->blockSignals( aLocked );
		}
	}

protected:
	pOpenedFileExplorer* mOpenedFileExplorer;
	QAbstractItemModel* mModel;
	QHash<QWidget*,QComboBox*> mCombos;
	
	virtual QWidget* createWidget( QWidget* parent )
	{
		QComboBox* combo = mCombos.value( parent );
		
		if ( combo )
		{
			//Q_ASSERT( 0 );
			return combo;
		}
		
		combo = new QComboBox( parent );
		combo->setMaxVisibleItems( 25 );
		combo->setSizeAdjustPolicy( QComboBox::AdjustToContents );
		combo->setAttribute( Qt::WA_MacSmallSize );
		combo->setModel( mModel );
		
		connect( combo, SIGNAL( activated( int ) ), this, SLOT( comboBox_activated( int ) ) );
		connect( combo, SIGNAL( destroyed( QObject* ) ), this, SLOT( object_destroyed( QObject* ) ) );
		
		mCombos[ parent ] = combo;
		
		return combo;
	}

protected slots:
	void comboBox_activated( int row )
	{
		const QModelIndex& index = mModel->index( row, 0 );
		emit currentIndexChanged( index );
	}
	
	void object_destroyed( QObject* object )
	{
		mCombos.remove( ((QWidget*)object)->parentWidget() );
	}

signals:
	void currentIndexChanged( const QModelIndex& index );
};

pOpenedFileExplorer::pOpenedFileExplorer( pWorkspace* workspace )
	: pDockWidget( workspace )
{
	Q_ASSERT( workspace );
	mWorkspace = workspace;
	mModel = new pOpenedFileModel( workspace );
	aComboBox = new pOpenedFileAction( this, mModel );
	setupUi( this );
	setAllowedAreas( Qt::LeftDockWidgetArea | Qt::RightDockWidgetArea );
	tvFiles->setModel( mModel );
	tvFiles->setAttribute( Qt::WA_MacShowFocusRect, false );
	tvFiles->setAttribute( Qt::WA_MacSmallSize );
	
	// sort menu
	mSortMenu = new QMenu( this );
	QActionGroup* group = new QActionGroup( mSortMenu );
	
	group->addAction( tr( "Opening order" ) );
	group->addAction( tr( "File name" ) );
	group->addAction( tr( "URL" ) );
	group->addAction( tr( "Suffixes" ) );
	group->addAction( tr( "Custom" ) );
	mSortMenu->addActions( group->actions() );
	
	for ( int i = pOpenedFileModel::OpeningOrder; i < pOpenedFileModel::Custom +1; i++ )
	{
		QAction* action = group->actions().at( i );
		action->setData( (pOpenedFileModel::SortMode)i );
		action->setCheckable( true );
		
		if ( i == pOpenedFileModel::OpeningOrder )
		{
			action->setChecked( true );
		}
	}
	
	QAction* aSortMenu = new QAction( tr( "Sorting" ), this );
	aSortMenu->setMenu( mSortMenu );
	aSortMenu->setIcon( pIconManager::icon( "sort.png" ) );
	aSortMenu->setToolTip( aSortMenu->text() );
	/*
	QToolButton* tb = qobject_cast<QToolButton*>( titleBar()->addAction( aSortMenu, 0 ) );
	tb->setPopupMode( QToolButton::InstantPopup );
	titleBar()->addSeparator( 1 );
	*/
	tvFiles->viewport()->setAcceptDrops( true );
	
	connect( group, SIGNAL( triggered ( QAction* ) ), this, SLOT( sortTriggered ( QAction* ) ) );
	connect( workspace, SIGNAL( documentChanged( pAbstractChild* ) ), this, SLOT( documentChanged( pAbstractChild* ) ) );
	connect( workspace, SIGNAL( currentDocumentChanged( pAbstractChild* ) ), this, SLOT( currentDocumentChanged( pAbstractChild* ) ) );
	connect( mModel, SIGNAL( sortModeChanged( pOpenedFileModel::SortMode ) ), this, SLOT( sortModeChanged( pOpenedFileModel::SortMode ) ) );
	connect( mModel, SIGNAL( documentsSorted() ), this, SLOT( documentsSorted() ) );
	connect( tvFiles->selectionModel(), SIGNAL( selectionChanged( const QItemSelection&, const QItemSelection& ) ), this, SLOT( selectionModel_selectionChanged( const QItemSelection&, const QItemSelection& ) ) );
	connect( aComboBox, SIGNAL( currentIndexChanged( const QModelIndex& ) ), this, SLOT( syncViewsIndex( const QModelIndex& ) ) );
}

pOpenedFileModel* pOpenedFileExplorer::model() const
{
	return mModel;
}

QAction* pOpenedFileExplorer::comboBoxAction() const
{
	return aComboBox;
}

pOpenedFileModel::SortMode pOpenedFileExplorer::sortMode() const
{
	return mModel->sortMode();
}

void pOpenedFileExplorer::setSortMode( pOpenedFileModel::SortMode mode )
{
	mModel->setSortMode( mode );
}

void pOpenedFileExplorer::syncViewsIndex( const QModelIndex& index, bool syncOnly )
{
	// sync action combobox
	aComboBox->syncViewIndex( index );
	
	// sync listview
	const bool vLocked = tvFiles->blockSignals( true );
	tvFiles->setCurrentIndex( index );
	tvFiles->blockSignals( vLocked );
	
	// scroll the view
	tvFiles->scrollTo( index );
	
	if ( syncOnly )
	{
		return;
	}
	
	// backup/restore current focused widget as setting active mdi window will steal it
	QWidget* focusWidget = window()->focusWidget();
	
	// set current document
	pAbstractChild* document = mModel->document( index );
	mWorkspace->setCurrentDocument( document );
	
	// restore focus widget
	if ( focusWidget )
	{
		focusWidget->setFocus();
	}
}

void pOpenedFileExplorer::sortTriggered( QAction* action )
{
	pOpenedFileModel::SortMode mode = (pOpenedFileModel::SortMode)action->data().toInt();
	setSortMode( mode );
}

void pOpenedFileExplorer::documentChanged( pAbstractChild* document )
{
	Q_UNUSED( document );
}

void pOpenedFileExplorer::currentDocumentChanged( pAbstractChild* document )
{
	const QModelIndex index = mModel->index( document );
	syncViewsIndex( index, true );
}

void pOpenedFileExplorer::sortModeChanged( pOpenedFileModel::SortMode mode )
{
	foreach ( QAction* action, mSortMenu->actions() )
	{
		if ( action->data().toInt() == mode )
		{
			if ( !action->isChecked() )
			{
				action->setChecked( true );
			}
			
			return;
		}
	}
}

void pOpenedFileExplorer::documentsSorted()
{
	// scroll the view
	tvFiles->scrollTo( tvFiles->selectionModel()->selectedIndexes().value( 0 ) );
}

void pOpenedFileExplorer::selectionModel_selectionChanged( const QItemSelection& selected, const QItemSelection& deselected )
{
	Q_UNUSED( deselected );
	const QModelIndex index = selected.indexes().value( 0 );
	syncViewsIndex( index, false );
}

void pOpenedFileExplorer::on_tvFiles_customContextMenuRequested( const QPoint& pos )
{
	QMenu menu;
	menu.addAction( MonkeyCore::menuBar()->action( "mFile/mClose/aCurrent" ) );
	menu.addAction( MonkeyCore::menuBar()->action( "mFile/mSave/aCurrent" ) );
	menu.addAction( MonkeyCore::menuBar()->action( "mFile/aReload" ) );
	menu.addSeparator();
	menu.addAction( mSortMenu->menuAction() );
	menu.exec( tvFiles->mapToGlobal( pos ) );
}

#include "pOpenedFileExplorer.moc"
