#include "pOpenedFileModel.h"
#include "pWorkspace.h"
#include "pAbstractChild.h"

#include <objects/pIconManager.h>

#include <QMimeData>
#include <QDebug>

struct OpeningOrderSorter
{
	OpeningOrderSorter( const QList<pAbstractChild*>& documents )
	{
		originalDocuments = documents;
	}
	
	bool operator()( pAbstractChild* left, pAbstractChild* right ) const
	{
		return originalDocuments.indexOf( left ) < originalDocuments.indexOf( right );
	}
	
	QList<pAbstractChild*> originalDocuments;
};

struct FileNameSorter
{
	bool operator()( pAbstractChild* left, pAbstractChild* right ) const
	{
		return left->fileName().toLower() < right->fileName().toLower();
	}
};

struct URLSorter
{
	bool operator()( pAbstractChild* left, pAbstractChild* right ) const
	{
		return left->filePath().toLower() < right->filePath().toLower();
	}
};

struct SuffixesSorter
{
	bool operator()( pAbstractChild* left, pAbstractChild* right ) const
	{
		const QFileInfo leftInfos( left->filePath() );
		const QString leftBaseName = leftInfos.baseName().toLower();
		const QString leftSuffix = leftInfos.completeSuffix().toLower();
		const QFileInfo rightInfos( right->filePath() );
		const QString rightBaseName = rightInfos.baseName().toLower();
		const QString rightSuffix = rightInfos.completeSuffix().toLower();
		
		if ( leftSuffix == rightSuffix )
		{
			return leftBaseName < rightBaseName;
		}
		
		return leftSuffix < rightSuffix;
	}
};

pOpenedFileModel::pOpenedFileModel( pWorkspace* workspace )
	: QAbstractItemModel( workspace )
{
	Q_ASSERT( workspace );
	mWorkspace = workspace;
	mSortMode = pOpenedFileModel::OpeningOrder;
	mSortDocumentsTimer = new QTimer( this );
	mSortDocumentsTimeout = 150;
	mTransparentIcon = pIconManager::icon( "transparent.png" );
	mModifiedIcon = pIconManager::icon( "save.png" );
	
	connect( mSortDocumentsTimer, SIGNAL( timeout() ), this, SLOT( sortDocuments_timeout() ) );
	connect( workspace, SIGNAL( documentOpened( pAbstractChild* ) ), this, SLOT( documentOpened( pAbstractChild* ) ) );
	connect( workspace, SIGNAL( documentModifiedChanged( pAbstractChild*, bool ) ), this, SLOT( documentModifiedChanged( pAbstractChild*, bool ) ) );
	connect( workspace, SIGNAL( documentClosed( pAbstractChild* ) ), this, SLOT( documentClosed( pAbstractChild* ) ) );
}

pOpenedFileModel::~pOpenedFileModel()
{
}

int pOpenedFileModel::columnCount( const QModelIndex& parent ) const
{
	Q_UNUSED( parent );
	return 1;
}

int pOpenedFileModel::rowCount( const QModelIndex& parent ) const
{
	return parent.isValid() ? 0 : mDocuments.count();
}

bool pOpenedFileModel::hasChildren( const QModelIndex& parent ) const
{
	return parent.isValid() ? false : !mDocuments.isEmpty();
}

QVariant pOpenedFileModel::headerData( int section, Qt::Orientation orientation, int role ) const
{
	if ( section == 0 && orientation == Qt::Horizontal )
	{
		switch ( role )
		{
			case Qt::DecorationRole:
				break;
			case Qt::DisplayRole:
				return tr( "Opened Files" );
				break;
			default:
				break;
		}
	}
	
	return QVariant();
}

QVariant pOpenedFileModel::data( const QModelIndex& index, int role ) const
{
	if ( !index.isValid() )
	{
		return QVariant();
	}
	
	pAbstractChild* document = this->document( index );
	
	if ( !document )
	{
		qWarning() << Q_FUNC_INFO << index << mDocuments;
		Q_ASSERT( document );
		return QVariant();
	}
	
	switch ( role )
	{
		case Qt::DecorationRole:
		{
			QIcon icon = document->windowIcon();
			
			if ( !mDocumentsIcons.value( document ).isNull() )
			{
				icon = mDocumentsIcons[ document ];
			}
			else if ( document->isModified() )
			{
				icon = mModifiedIcon;
			}
			
			if ( icon.isNull() )
			{
				icon = mTransparentIcon;
			}
			
			return icon;
			break;
		}
		case Qt::DisplayRole:
			return document->fileName();
			break;
		case Qt::ToolTipRole:
		{
			const QString customToolTip = mDocumentsToolTips.value( document );
			const QString toolTip = document->filePath();
			return customToolTip.isEmpty() ? toolTip : customToolTip;
			break;
		}
		default:
			break;
	}
	
	return QVariant();
}

Qt::ItemFlags pOpenedFileModel::flags( const QModelIndex& index ) const
{
	if ( index.isValid() )
	{
		return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsDragEnabled;
	}
	else
	{
		return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsDropEnabled;
	}
}

QModelIndex pOpenedFileModel::index( int row, int column, const QModelIndex& parent ) const
{
	if ( parent.isValid() || column > 0 || column < 0 || row < 0 || row >= mDocuments.count() )
	{
		return QModelIndex();
	}
	
	return createIndex( row, column, mDocuments.at( row ) );
}

QModelIndex pOpenedFileModel::parent( const QModelIndex& index ) const
{
	Q_UNUSED( index );
	return QModelIndex();
}

QStringList pOpenedFileModel::mimeTypes() const
{
	return QStringList( "application/x-modelindexrow" );
}

QMimeData* pOpenedFileModel::mimeData( const QModelIndexList& indexes ) const
{
	if ( indexes.count() != 1 )
	{
		return 0;
	}
	
	QMimeData* data = new QMimeData();
	data->setData( mimeTypes().first(), QByteArray::number( indexes.first().row() ) );
	return data;
}

Qt::DropActions pOpenedFileModel::supportedDropActions() const
{
	return Qt::MoveAction;
}

bool pOpenedFileModel::dropMimeData( const QMimeData* data, Qt::DropAction action, int row, int column, const QModelIndex& parent )
{
	if ( parent.isValid() || ( row == -1 && column == -1 ) || action != Qt::MoveAction || !data || !data->hasFormat( mimeTypes().first() ) )
	{
		return false;
	}
	
	const int fromRow = data->data( mimeTypes().first() ).toInt();
	
	if ( row >= mDocuments.count() )
	{
		row--;
	}
	else if ( fromRow < row )
	{
		row--;
	}
	
	QList<pAbstractChild*> newDocuments = mDocuments;
	
	newDocuments.move( fromRow, row );
	rebuildMapping( mDocuments, newDocuments );
	
	if ( mSortMode != pOpenedFileModel::Custom )
	{
		setSortMode( pOpenedFileModel::Custom );
	}
	
	return true;
}

pAbstractChild* pOpenedFileModel::document( const QModelIndex& index ) const
{
	if ( !index.isValid() )
	{
		return 0;
	}
	
	return static_cast<pAbstractChild*>( index.internalPointer() );
}

QModelIndex pOpenedFileModel::index( pAbstractChild* document ) const
{
	const int row = mDocuments.indexOf( document );
	
	if ( row != -1 )
	{
		return createIndex( row, 0, document );
	}
	
	return QModelIndex();
}

pOpenedFileModel::SortMode pOpenedFileModel::sortMode() const
{
	return mSortMode;
}

void pOpenedFileModel::setSortMode( pOpenedFileModel::SortMode mode )
{
	if ( mSortMode != mode )
	{
		mSortMode = mode;
		emit sortModeChanged( mSortMode );
		sortDocuments();
	}
}

void pOpenedFileModel::setDocumentIcon( pAbstractChild* document, const QIcon& icon )
{
	mDocumentsIcons[ document ] = icon;
	const QModelIndex index = this->index( document );
	emit dataChanged( index, index );
}

void pOpenedFileModel::setDocumentToolTip( pAbstractChild* document, const QString& toolTip )
{
	mDocumentsToolTips[ document ] = toolTip;
	const QModelIndex index = this->index( document );
	emit dataChanged( index, index );
}

void pOpenedFileModel::sortDocuments()
{
	mSortDocumentsTimer->start( mSortDocumentsTimeout );
}

void pOpenedFileModel::insertDocument( pAbstractChild* document, int index )
{
	Q_ASSERT( !mDocuments.contains( document ) );
	beginInsertRows( QModelIndex(), index, index );
	mDocuments.insert( index, document );
	endInsertRows();
	sortDocuments();
}


void pOpenedFileModel::rebuildMapping( const QList<pAbstractChild*>& oldList, const QList<pAbstractChild*>& newList )
{
	emit layoutAboutToBeChanged();
	const QModelIndexList pOldIndexes = persistentIndexList();
	QModelIndexList pIndexes;
	QMap<int, pAbstractChild*> documentsMapping;
	QMap<int, int> mapping;
	
	// build old mapping
	for ( int i = 0; i < pOldIndexes.count(); i++ )
	{
		const QModelIndex& index = pOldIndexes.at( i );
		const int row = index.row();
		documentsMapping[ row ] = oldList.at( row );
		mapping[ row ] = row;
	}
	
	mDocuments = newList;
	
	// build new mapping
	for ( int i = 0; i < pOldIndexes.count(); i++ )
	{
		const QModelIndex& pIndex = pOldIndexes.at( i );
		const int row = pIndex.row();
		pAbstractChild* document = documentsMapping[ row ];
		const int index = mDocuments.indexOf( document );
		mapping[ row ] = index;
	}
	
	for ( int i = 0; i < pOldIndexes.count(); i++ )
	{
		const QModelIndex& pIndex = pOldIndexes.at( i );
		const int row = pIndex.row();
		const int index = mapping[ row ];
		
		if ( pOldIndexes.at( i ).isValid() )
			pIndexes << createIndex( index, pIndex.column(), mDocuments.at( index ) );
		else
			pIndexes << QModelIndex();
	}
	
	changePersistentIndexList( pOldIndexes, pIndexes );
	emit layoutChanged();
}

void pOpenedFileModel::sortDocuments_timeout()
{
	mSortDocumentsTimer->stop();
	
	QList<pAbstractChild*> newDocuments = mDocuments;
	
	switch ( mSortMode )
	{
		case pOpenedFileModel::OpeningOrder:
		{
			OpeningOrderSorter functor( mWorkspace->documents() );
			qSort( newDocuments.begin(), newDocuments.end(), functor );
			break;
		}
		case pOpenedFileModel::FileName:
		{
			FileNameSorter functor;
			qSort( newDocuments.begin(), newDocuments.end(), functor );
			break;
		}
		case pOpenedFileModel::URL:
		{
			URLSorter functor;
			qSort( newDocuments.begin(), newDocuments.end(), functor );
			break;
		}
		case pOpenedFileModel::Suffixes:
		{
			SuffixesSorter functor;
			qSort( newDocuments.begin(), newDocuments.end(), functor );
			break;
		}
		case pOpenedFileModel::Custom:
			break;
	}
	
	rebuildMapping( mDocuments, newDocuments );
	emit documentsSorted();
}

void pOpenedFileModel::documentOpened( pAbstractChild* document )
{
	if ( mDocuments.contains( document ) )
	{
		sortDocuments();
	}
	else
	{
		if ( !document || mDocuments.contains( document ) )
		{
			return;
		}
		
		const int index = mDocuments.count();
		insertDocument( document, index );
	}
}

void pOpenedFileModel::documentModifiedChanged( pAbstractChild* document, bool modified )
{
	Q_UNUSED( modified );
	const QModelIndex index = this->index( document );
	emit dataChanged( index, index );
}

void pOpenedFileModel::documentClosed( pAbstractChild* document )
{
	const int index = mDocuments.indexOf( document );
	
	if ( index == -1 )
	{
		return;
	}
	
	beginRemoveRows( QModelIndex(), index, index );
	mDocuments.removeOne( document );
	mDocumentsIcons.remove( document );
	mDocumentsToolTips.remove( document );
	endRemoveRows();
	sortDocuments();
}
