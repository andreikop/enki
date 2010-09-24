#include "XUPItem.h"
#include "XUPProjectItem.h"
#include "XUPProjectModel.h"

#include <QDebug>

XUPItem.XUPItem(  QDomElement& node, parent )
    mModel = 0
    mDomElement = node
    mParentItem = parent


XUPItem.~XUPItem()
    qDeleteAll( mChildItems )
    mChildItems.clear()


def sameTypeLess(self, other ):
    switch ( other.type() )
    case XUPItem.Variable:
        pItem = project()
        filteredVariables = pItem.projectInfos().filteredVariables( pItem.projectType() )
        return filteredVariables.indexOf( attribute( "name" ) ) < filteredVariables.indexOf( other.attribute( "name" ) )
        break

    case XUPItem.Comment:
        return row() < other.row()
        break
    case XUPItem.EmptyLine:
        return attribute( "count" ).toInt() < other.attribute( "count" ).toInt()
        break
    case XUPItem.Project:
    case XUPItem.Value:
    case XUPItem.Function:
    case XUPItem.Scope:
    case XUPItem.DynamicFolder:
    case XUPItem.Folder:
    case XUPItem.File:
    case XUPItem.Path:
    default:
        break


    return displayText().toLower() < other.displayText().toLower()


bool XUPItem.operator<(  XUPItem& other )
    if  type() == other.type() :
        return sameTypeLess( other )

    else:
        switch ( type() )
        case XUPItem.Project:
            return False
            break
        default:
            return True
            break



    return displayText().toLower() < other.displayText().toLower()


def node(self):
    return mDomElement


def project(self):
    if  type() == XUPItem.Project :
        return static_cast<XUPProjectItem*>( const_cast<XUPItem*>( self ) )
    else:
        return mParentItem.project()


def parent(self):
    return mParentItem


def setParent(self, parentItem ):
    mParentItem = parentItem


def child(self, i ):
    if  mChildItems.contains( i ) :
        return mChildItems[ i ]

    if  i >= 0 and i < mDomElement.childNodes().count() :
        childElement = mDomElement.childNodes().item( i ).toElement()
        childItem = XUPItem( childElement, const_cast<XUPItem*>( self ) )
        mChildItems[ i ] = childItem
        return childItem

    return 0


def childrenList(self):
    # create all child if needed before returning list
    for ( i = 0; i < childCount(); i++ )
        child( i )


    # return children
    return mChildItems.values()


def childIndex(self, child ):
    return mChildItems.key( child, -1 )


def addChild(self, item ):
    row = childCount()
    m = model()

    # inform begin insert
    if  m :
        m.beginInsertRows( index(), row, row )


    mChildItems[ row ] = item
    item.setParent( self )

    # inform end insert
    if  m :
        m.endInsertRows()



def row(self):
    if  mParentItem :
        return mParentItem.childIndex( const_cast<XUPItem*>( self ) )

    else:
        return 0



def childCount(self):
    count = mDomElement.childNodes().count()
    if  not mChildItems.isEmpty() :
        count = qMax( count, mChildItems.keys().last() +1 )

    return count


def removeChild(self, item ):
    id = childIndex( item )
    if  id != -1 :
        # inform model of remove
        m = model()
        if  m :
            # begin remove
            m.beginRemoveRows( index(), id, id )

            # remove
            isDirectChild = item.mDomElement.parentNode() == mDomElement

            if  isDirectChild :
                for key in mChildItems.keys():
                    if  key == id :
                        node = item.mDomElement
                        mDomElement.removeChild( node )
                        mChildItems.remove( key )
                        delete item

                    elif  key > id :
                        mChildItems[ key -1 ] = mChildItems[ key ]
                        mChildItems.remove( key )



            else:
                delete mChildItems.take( id )


            # end remove
            m.endRemoveRows()

        else:
            delete mChildItems.take( id )




def addChild(self, pType, row ):
    # calculate row if needed
    if  row == -1 :
        row = mDomElement.childNodes().count()


    QString stringType
    switch ( pType )
    case XUPItem.Project:
        stringType = "project"
        break
    case XUPItem.Comment:
        stringType = "comment"
        break
    case XUPItem.EmptyLine:
        stringType = "emptyline"
        break
    case XUPItem.Variable:
        stringType = "variable"
        break
    case XUPItem.Value:
        stringType = "value"
        break
    case XUPItem.Function:
        stringType = "function"
        break
    case XUPItem.Scope:
        stringType = "scope"
        break
    case XUPItem.DynamicFolder:
        stringType = "dynamicfolder"
        break
    case XUPItem.Folder:
        stringType = "folder"
        break
    case XUPItem.File:
        stringType = "file"
        break
    case XUPItem.Path:
        stringType = "path"
        break
    case XUPItem.Unknow:
        break


    # inform model of add
    m = model()
    if  not stringType.isEmpty() and row <= childCount() and m :
        # begin insert
        m.beginInsertRows( index(), row, row )

        # re inde existing items
        QList<int> rows = mChildItems.keys()
        qSort( rows.begin(), rows.end(), qGreater<int>() )
        for key in rows:
            if  key >= row :
                mChildItems[ key +1 ] = mChildItems[ key ]



        # add one
        mChildItems.remove( row )
        element = mDomElement.ownerDocument().createElement( stringType )
        if  childCount() == 0 :
            mDomElement.appendChild( element )

        else:
            if  row == 0 :
                mDomElement.insertBefore( element, child( 1 ).node() )

            else:
                mDomElement.insertAfter( element, child( row -1 ).node() )



        # end insert
        m.endInsertRows()

        # update scope nested property
        if  type() == XUPItem.Scope :
            setAttribute( "nested", "False" )


        return child( row )


    return 0


def model(self):
    if  mParentItem :
        return mParentItem.model()

    return mModel


def index(self):
    m = model()
    if  m :
        return m.indexFromItem( const_cast<XUPItem*>( self ) )

    return QModelIndex()


def type(self):
     mType = mDomElement.nodeName()
    if  mType == "project" :
        return XUPItem.Project
    elif  mType == "comment" :
        return XUPItem.Comment
    elif  mType == "emptyline" :
        return XUPItem.EmptyLine
    elif  mType == "variable" :
        return XUPItem.Variable
    elif  mType == "value" :
        return XUPItem.Value
    elif  mType == "function" :
        return XUPItem.Function
    elif  mType == "scope" :
        return XUPItem.Scope
    elif  mType == "dynamicfolder" :
        return XUPItem.DynamicFolder
    elif  mType == "folder" :
        return XUPItem.Folder
    elif  mType == "file" :
        return XUPItem.File
    elif  mType == "path" :
        return XUPItem.Path
    return XUPItem.Unknow


def displayText(self):
    return project().itemDisplayText( const_cast<XUPItem*>( self ) )


def displayIcon(self):
    return project().itemDisplayIcon( const_cast<XUPItem*>( self ) )


def attribute(self, name, defaultValue ):
    return mDomElement.attribute( name, defaultValue )


def setAttribute(self, name, value ):
    if  mDomElement.attribute( name ) == value :
        return


    mDomElement.setAttribute( name, value )

    # update model if needed
    m = model()
    if  m :
        #m.itemChanged( self )
        setTemporaryValue( "hasDisplayText", False )
        setTemporaryValue( "hasDisplayIcon", False )

        idx = index()
        m.emit.dataChanged( idx, idx )



def temporaryValue(self, key, defaultValue ):
    return mTemporaryValues.value( key, defaultValue )


def setTemporaryValue(self, key, value ):
    mTemporaryValues[ key ] = value


def clearTemporaryValue(self, key ):
    mTemporaryValues.remove( key )


def cacheValue(self, key, defaultValue ):
    return temporaryValue( "cache-" +key, defaultValue ).toString()


def setCacheValue(self, key, value ):
    setTemporaryValue( "cache-" +key, value )


def clearCacheValue(self, key ):
    clearTemporaryValue( "cache-" +key )

