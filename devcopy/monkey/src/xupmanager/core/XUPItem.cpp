#include "XUPItem.h"
#include "XUPProjectItem.h"
#include "XUPProjectModel.h"

#include <QDebug>

XUPItem::XUPItem( const QDomElement& node, XUPItem* parent )
{
    mModel = 0;
    mDomElement = node;
    mParentItem = parent;
}

XUPItem::~XUPItem()
{
    qDeleteAll( mChildItems );
    mChildItems.clear();
}

bool XUPItem::sameTypeLess( const XUPItem& other ) const
{    
    switch ( other.type() )
    {
        case XUPItem::Variable:
        {
            XUPProjectItem* pItem = project();
            QStringList filteredVariables = pItem->projectInfos()->filteredVariables( pItem->projectType() );
            return filteredVariables.indexOf( attribute( "name" ) ) < filteredVariables.indexOf( other.attribute( "name" ) );
            break;
        }
        case XUPItem::Comment:
            return row() < other.row();
            break;
        case XUPItem::EmptyLine:
            return attribute( "count" ).toInt() < other.attribute( "count" ).toInt();
            break;
        case XUPItem::Project:
        case XUPItem::Value:
        case XUPItem::Function:
        case XUPItem::Scope:
        case XUPItem::DynamicFolder:
        case XUPItem::Folder:
        case XUPItem::File:
        case XUPItem::Path:
        default:
            break;
    }
    
    return displayText().toLower() < other.displayText().toLower();
}

bool XUPItem::operator<( const XUPItem& other ) const
{
    if ( type() == other.type() )
    {
        return sameTypeLess( other );
    }
    else
    {
        switch ( type() )
        {
            case XUPItem::Project:
                return false;
                break;
            default:
                return true;
                break;
        }
    }

    return displayText().toLower() < other.displayText().toLower();
}

QDomElement XUPItem::node() const
{
    return mDomElement;
}

XUPProjectItem* XUPItem::project() const
{
    if ( type() == XUPItem::Project )
        return static_cast<XUPProjectItem*>( const_cast<XUPItem*>( this ) );
    else
        return mParentItem->project();
}

XUPItem* XUPItem::parent() const
{
    return mParentItem;
}

void XUPItem::setParent( XUPItem* parentItem )
{
    mParentItem = parentItem;
}

XUPItem* XUPItem::child( int i ) const
{
    if ( mChildItems.contains( i ) )
        return mChildItems[ i ];

    if ( i >= 0 && i < mDomElement.childNodes().count() )
    {
        QDomElement childElement = mDomElement.childNodes().item( i ).toElement();
        XUPItem* childItem = new XUPItem( childElement, const_cast<XUPItem*>( this ) );
        mChildItems[ i ] = childItem;
        return childItem;
    }
    return 0;
}

XUPItemList XUPItem::childrenList() const
{
    // create all child if needed before returning list
    for ( int i = 0; i < childCount(); i++ )
    {
        child( i );
    }
    
    // return children
    return mChildItems.values();
}

int XUPItem::childIndex( XUPItem* child ) const
{
    return mChildItems.key( child, -1 );
}

void XUPItem::addChild( XUPItem* item )
{
    int row = childCount();
    XUPProjectModel* m = model();
    
    // inform begin insert
    if ( m )
    {
        m->beginInsertRows( index(), row, row );
    }
    
    mChildItems[ row ] = item;
    item->setParent( this );
    
    // inform end insert
    if ( m )
    {
        m->endInsertRows();
    }
}

int XUPItem::row() const
{
    if ( mParentItem )
    {
        return mParentItem->childIndex( const_cast<XUPItem*>( this ) );
    }
    else
    {
        return 0;
    }
}

int XUPItem::childCount() const
{
    int count = mDomElement.childNodes().count();
    if ( !mChildItems.isEmpty() )
    {
        count = qMax( count, mChildItems.keys().last() +1 );
    }
    return count;
}

void XUPItem::removeChild( XUPItem* item )
{
    int id = childIndex( item );
    if ( id != -1 )
    {
        // inform model of remove
        XUPProjectModel* m = model();
        if ( m )
        {
            // begin remove
            m->beginRemoveRows( index(), id, id );
            
            // remove
            bool isDirectChild = item->mDomElement.parentNode() == mDomElement;
            
            if ( isDirectChild )
            {
                foreach ( const int& key, mChildItems.keys() )
                {
                    if ( key == id )
                    {
                        QDomNode node = item->mDomElement;
                        mDomElement.removeChild( node );
                        mChildItems.remove( key );
                        delete item;
                    }
                    else if ( key > id )
                    {
                        mChildItems[ key -1 ] = mChildItems[ key ];
                        mChildItems.remove( key );
                    }
                }
            }
            else
            {
                delete mChildItems.take( id );
            }
            
            // end remove
            m->endRemoveRows();
        }
        else
        {
            delete mChildItems.take( id );
        }
    }
}

XUPItem* XUPItem::addChild( XUPItem::Type pType, int row )
{
    // calculate row if needed
    if ( row == -1 )
    {
        row = mDomElement.childNodes().count();
    }
    
    QString stringType;
    switch ( pType )
    {
        case XUPItem::Project:
            stringType = "project";
            break;
        case XUPItem::Comment:
            stringType = "comment";
            break;
        case XUPItem::EmptyLine:
            stringType = "emptyline";
            break;
        case XUPItem::Variable:
            stringType = "variable";
            break;
        case XUPItem::Value:
            stringType = "value";
            break;
        case XUPItem::Function:
            stringType = "function";
            break;
        case XUPItem::Scope:
            stringType = "scope";
            break;
        case XUPItem::DynamicFolder:
            stringType = "dynamicfolder";
            break;
        case XUPItem::Folder:
            stringType = "folder";
            break;
        case XUPItem::File:
            stringType = "file";
            break;
        case XUPItem::Path:
            stringType = "path";
            break;
        case XUPItem::Unknow:
            break;
    }
    
    // inform model of add
    XUPProjectModel* m = model();
    if ( !stringType.isEmpty() && row <= childCount() && m )
    {
        // begin insert
        m->beginInsertRows( index(), row, row );
        
        // re inde existing items
        QList<int> rows = mChildItems.keys();
        qSort( rows.begin(), rows.end(), qGreater<int>() );
        foreach ( const int& key, rows )
        {
            if ( key >= row )
            {
                mChildItems[ key +1 ] = mChildItems[ key ];
            }
        }
        
        // add new one
        mChildItems.remove( row );
        QDomElement element = mDomElement.ownerDocument().createElement( stringType );
        if ( childCount() == 0 )
        {
            mDomElement.appendChild( element );
        }
        else
        {
            if ( row == 0 )
            {
                mDomElement.insertBefore( element, child( 1 )->node() );
            }
            else
            {
                mDomElement.insertAfter( element, child( row -1 )->node() );
            }
        }
        
        // end insert
        m->endInsertRows();
        
        // update scope nested property
        if ( type() == XUPItem::Scope )
        {
            setAttribute( "nested", "false" );
        }
        
        return child( row );
    }
    
    return 0;
}

XUPProjectModel* XUPItem::model() const
{
    if ( mParentItem )
    {
        return mParentItem->model();
    }
    return mModel;
}

QModelIndex XUPItem::index() const
{
    XUPProjectModel* m = model();
    if ( m )
    {
        return m->indexFromItem( const_cast<XUPItem*>( this ) );
    }
    return QModelIndex();
}

XUPItem::Type XUPItem::type() const
{
    const QString mType = mDomElement.nodeName();
    if ( mType == "project" )
        return XUPItem::Project;
    else if ( mType == "comment" )
        return XUPItem::Comment;
    else if ( mType == "emptyline" )
        return XUPItem::EmptyLine;
    else if ( mType == "variable" )
        return XUPItem::Variable;
    else if ( mType == "value" )
        return XUPItem::Value;
    else if ( mType == "function" )
        return XUPItem::Function;
    else if ( mType == "scope" )
        return XUPItem::Scope;
    else if ( mType == "dynamicfolder" )
        return XUPItem::DynamicFolder;
    else if ( mType == "folder" )
        return XUPItem::Folder;
    else if ( mType == "file" )
        return XUPItem::File;
    else if ( mType == "path" )
        return XUPItem::Path;
    return XUPItem::Unknow;
}

QString XUPItem::displayText() const
{
    return project()->itemDisplayText( const_cast<XUPItem*>( this ) );
}

QIcon XUPItem::displayIcon() const
{
    return project()->itemDisplayIcon( const_cast<XUPItem*>( this ) );
}

QString XUPItem::attribute( const QString& name, const QString& defaultValue ) const
{
    return mDomElement.attribute( name, defaultValue );
}

void XUPItem::setAttribute( const QString& name, const QString& value )
{
    if ( mDomElement.attribute( name ) == value )
    {
        return;
    }
    
    mDomElement.setAttribute( name, value );
    
    // update model if needed
    XUPProjectModel* m = model();
    if ( m )
    {
        //m->itemChanged( this );
        setTemporaryValue( "hasDisplayText", false );
        setTemporaryValue( "hasDisplayIcon", false );
        
        QModelIndex idx = index();
        emit m->dataChanged( idx, idx );
    }
}

QVariant XUPItem::temporaryValue( const QString& key, const QVariant& defaultValue ) const
{
    return mTemporaryValues.value( key, defaultValue );
}

void XUPItem::setTemporaryValue( const QString& key, const QVariant& value )
{
    mTemporaryValues[ key ] = value;
}

void XUPItem::clearTemporaryValue( const QString& key )
{
    mTemporaryValues.remove( key );
}

QString XUPItem::cacheValue( const QString& key, const QString& defaultValue ) const
{
    return temporaryValue( "cache-" +key, defaultValue ).toString();
}

void XUPItem::setCacheValue( const QString& key, const QString& value )
{
    setTemporaryValue( "cache-" +key, value );
}

void XUPItem::clearCacheValue( const QString& key )
{
    clearTemporaryValue( "cache-" +key );
}
