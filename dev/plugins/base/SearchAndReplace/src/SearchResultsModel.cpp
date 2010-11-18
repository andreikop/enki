#include "SearchResultsModel.h"
#include "SearchThread.h"

SearchResultsModel::SearchResultsModel( SearchThread* searchThread, QObject* parent )
	: QAbstractItemModel( parent )
{
	Q_ASSERT( searchThread );
	mRowCount = 0;
	mSearchThread = searchThread;

	// connections
	connect( mSearchThread, SIGNAL( reset() ), this, SLOT( thread_reset() ) );
	connect( mSearchThread, SIGNAL( resultsAvailable( const QString&, const SearchResultsModel::ResultList& ) ), this, SLOT( thread_resultsAvailable( const QString&, const SearchResultsModel::ResultList& ) ) );
}

int SearchResultsModel::columnCount( const QModelIndex& parent ) const
{
	Q_UNUSED( parent );
	return 1;
}

QVariant SearchResultsModel::data( const QModelIndex& index, int role ) const
{
	if ( !index.isValid() )
	{
		return QVariant();
	}

	SearchResultsModel::Result* result = this->result( index );

	Q_ASSERT( result );

	switch ( role )
	{
		case Qt::DisplayRole:
		{
			QString text;

			// index is a root parent
			if ( mParentsList.value( index.row() ) == result )
			{
				const int count = rowCount( index );
				text = mSearchDir.relativeFilePath( result->fileName );
				text.append( QString( " (%1)" ).arg( count ) );
			}
			// index is a root parent child
			else
			{
				text = tr( "Line: %1, Column: %2: %3" ).arg( result->position.y() +1 ).arg( result->position.x() ).arg( result->capture );
			}

			return text;
		}
		case Qt::ToolTipRole:
		{
			return data( index, Qt::DisplayRole );
		}
		case Qt::CheckStateRole:
		{
			if ( flags( index ) & Qt::ItemIsUserCheckable )
			{
				return result->checkState;
			}

			break;
		}
	}

	return QVariant();
}

QModelIndex SearchResultsModel::index( int row, int column, const QModelIndex& parent ) const
{
	if ( row >= rowCount( parent ) || column >= columnCount( parent ) )
	{
		return QModelIndex();
	}

	SearchResultsModel::Result* result = this->result( parent );

	// parent is a root parent
	if ( result && mParentsList.value( parent.row() ) == result )
	{
		result = mResults.at( parent.row() ).at( row );
		return createIndex( row, column, result );
	}

	Q_ASSERT( !parent.isValid() );

	// parent is invalid
	return createIndex( row, column, mParentsList[ row ] );
}

QModelIndex SearchResultsModel::parent( const QModelIndex& index ) const
{
	if ( !index.isValid() )
	{
		return QModelIndex();
	}

	SearchResultsModel::Result* result = this->result( index );

	// index is a root parent
	if ( result && mParentsList.value( index.row() ) == result )
	{
		return QModelIndex();
	}

	Q_ASSERT( index.isValid() );

	result = mParents[ result->fileName ];
	const int row = mParentsList.indexOf( result );

	// index is a root parent child
	return createIndex( row, index.column(), result );
}

int SearchResultsModel::rowCount( const QModelIndex& parent ) const
{
	// root parents
	if ( !parent.isValid() )
	{
		return mRowCount;
	}

	return parent.parent().isValid() ? 0 : mResults.at( parent.row() ).count();
}

Qt::ItemFlags SearchResultsModel::flags( const QModelIndex& index ) const
{
	Qt::ItemFlags flags = QAbstractItemModel::flags( index );
	SearchAndReplace::Properties* properties = mSearchThread->properties();

	if ( properties->mode & SearchAndReplace::ModeFlagReplace )
	{
		flags |= Qt::ItemIsUserCheckable;
	}

	SearchResultsModel::Result* result = this->result( index );

	if ( result )
	{
		if ( !result->enabled )
		{
			flags &= ~Qt::ItemIsEnabled;
			flags &= ~Qt::ItemIsSelectable;
		}
	}

	return flags;
}

bool SearchResultsModel::hasChildren( const QModelIndex& parent ) const
{
	// root parents
	if ( !parent.isValid() )
	{
		return mRowCount != 0;
	}

	return parent.parent().isValid() ? false : !mResults.at( parent.row() ).isEmpty();
}

bool SearchResultsModel::setData( const QModelIndex& index, const QVariant& value, int role )
{
	SearchResultsModel::Result* result = this->result( index );
	bool ok = false;

	switch ( role )
	{
		case Qt::CheckStateRole:
		{
			ok = true;
			break;
		}
		case SearchResultsModel::EnabledRole:
		{
			result->enabled = value.toBool();
			ok = true;
			break;
		}
	}

	if ( role != Qt::CheckStateRole )
	{
		if ( ok )
		{
			emit dataChanged( index, index );
		}

		return ok;
	}

	const Qt::CheckState state = Qt::CheckState( value.toInt() );
	const QModelIndex pIndex = index.parent();
	const bool isParent = !pIndex.isValid();
	SearchResultsModel::Result* pResult = this->result( pIndex );

	Q_ASSERT( result );

	if ( isParent )
	{
		const int pRow = mParentsList.indexOf( result );
		int checkedCount = 0;

		// update all children to same state as parent
		foreach ( SearchResultsModel::Result* r, mResults.at( pRow ) )
		{
			if ( r->enabled )
			{
				r->checkState = state;
				checkedCount++;
			}
		}

		const QModelIndex left = index.child( 0, 0 );
		const QModelIndex right = index.child( rowCount( index ) -1, columnCount( index ) -1 );
		// update root parent children
		emit dataChanged( left, right );

		if ( state == Qt::Unchecked )
		{
			checkedCount = 0;
		}

		if ( ( checkedCount == 0 && state == Qt::Checked ) || result->checkState == state )
		{
			ok = false;
		}

		if ( ok )
		{
			result->checkState = state;
		}
	}
	else
	{
		const int pRow = mParentsList.indexOf( pResult );
		int count = 0;
		int checkedCount = 0;

		foreach ( SearchResultsModel::Result* r, mResults.at( pRow ) )
		{
			count++;

			if ( r->checkState == Qt::Checked )
			{
				checkedCount++;
			}
		}

		if ( state == Qt::Checked )
		{
			checkedCount++;
		}
		else
		{
			checkedCount--;
		}

		result->checkState = state;

		// update parent
		if ( checkedCount == 0 )
		{
			pResult->checkState = Qt::Unchecked;
		}
		else if ( checkedCount == count )
		{
			pResult->checkState = Qt::Checked;
		}
		else
		{
			pResult->checkState = Qt::PartiallyChecked;
		}

		// update root parent index
		emit dataChanged( pIndex, pIndex );
	}

	// update clicked index
	emit dataChanged( index, index );

	return ok;
}

QModelIndex SearchResultsModel::index( SearchResultsModel::Result* result ) const
{
	const QModelIndex index;
	int row = mParentsList.indexOf( result );

	if ( row != -1 )
	{
		return createIndex( row, 0, result );
	}
	else if ( result )
	{
		SearchResultsModel::Result* pResult = mParents.value( result->fileName );

		if ( pResult )
		{
			row = mParentsList.indexOf( pResult );

			if ( row != -1 )
			{
				row = mResults.at( row ).indexOf( result );
				return createIndex( row, 0, result );
			}
		}
	}

	return index;
}

SearchResultsModel::Result* SearchResultsModel::result( const QModelIndex& index ) const
{
	return index.isValid() ? static_cast<SearchResultsModel::Result*>( index.internalPointer() ) : 0;
}

const QList<SearchResultsModel::ResultList>& SearchResultsModel::results() const
{
	return mResults;
}

void SearchResultsModel::clear()
{
	if ( mRowCount == 0 )
	{
		return;
	}
	
	beginRemoveRows( QModelIndex(), 0, mRowCount -1 );
	
	foreach ( const SearchResultsModel::ResultList& results, mResults )
	{
		qDeleteAll( results );
	}
	
	mResults.clear();
	qDeleteAll( mParents );
	mParents.clear();
	mParentsList.clear();
	mRowCount = 0;
	
	endRemoveRows();
}

void SearchResultsModel::thread_reset()
{
	clear();
}

void SearchResultsModel::thread_resultsAvailable( const QString& fileName, const SearchResultsModel::ResultList& results )
{
	if ( mRowCount == 0 )
	{
		emit firstResultsAvailable();
	}
	
	SearchResultsModel::Result* result = mParents[ fileName ];
	SearchAndReplace::Properties* properties = mSearchThread->properties();
	
	if ( mRowCount == 0 )
	{
		mSearchDir.setPath( properties->searchPath );
	}

	if ( !result )
	{
		result = new SearchResultsModel::Result( fileName );
		result->checkable = properties->mode & SearchAndReplace::ModeFlagReplace;
		result->checkState = result->checkable ? Qt::Checked : Qt::Unchecked;

		beginInsertRows( QModelIndex(), mRowCount, mRowCount );
		mParents[ fileName ] = result;
		mParentsList << result;
		mRowCount++;
		mResults << results;
		endInsertRows();
	}
	else
	{
		const int pRow = mParentsList.indexOf( result );
		const int count = mResults.at( pRow ).count();
		const QModelIndex index = createIndex( pRow, 0, result );

		beginInsertRows( index, count, count +results.count() -1 );
		mResults[ pRow ] << results;
		endInsertRows();

		emit dataChanged( index, index );
	}
}

void SearchResultsModel::thread_resultsHandled( const QString& fileName, const SearchResultsModel::ResultList& results )
{
	SearchResultsModel::Result* pResult = mParents.value( fileName );

	Q_ASSERT( pResult );

	const int pRow = mParentsList.indexOf( pResult );
	SearchResultsModel::ResultList& children = mResults[ pRow ];
	const QModelIndex pIndex = createIndex( pRow, 0, pResult );

	// remove root parent children
	foreach ( SearchResultsModel::Result* result, results )
	{
		const int index = children.indexOf( result );
		beginRemoveRows( pIndex, index, index );
		delete children.takeAt( index );
		endRemoveRows();
	}

	// remove root parent
	if ( children.isEmpty() )
	{
		beginRemoveRows( QModelIndex(), pRow, pRow );
		mResults.removeAt( pRow );
		mParentsList.removeAt( pRow );
		delete mParents.take( fileName );
		mRowCount--;
		endRemoveRows();
	}
	else
	{
		pResult->checkState = Qt::Unchecked;
		emit dataChanged( pIndex, pIndex );
	}
}
