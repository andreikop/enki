#ifndef XUPITEM_H
#define XUPITEM_H

#include <objects/MonkeyExport.h>

#include <QDomElement>
#include <QMap>
#include <QIcon>
#include <QVariant>
#include <QModelIndex>

class XUPProjectItem
class XUPProjectModel

typedef QList<class XUPItem*> XUPItemList

class Q_MONKEY_EXPORT XUPItem
    friend class XUPProjectModel
    friend class XUPProjectItem
    
public:
    # possible types for a node
    enum Type        Unknow = -1,
        Project, # a project node
        Comment, # a comment node
        EmptyLine, # a empty line node
        Variable, # a variabel node
        Value, # a value node
        Function, # a function node
        Scope, # a scope node
        #
        DynamicFolder, # a dynamic folder node (ie: children are populate by the folder path dynamically)
        Folder, # a folder node
        File, # a value that is a file node
        Path # a value that is a path node

    
    # dtor
    virtual ~XUPItem()
    
    # the < operator for sorting items in tree
    virtual bool sameTypeLess(  XUPItem& other )
    virtual bool operator<(  XUPItem& other )
    
    # project item
    XUPProjectItem* project()
    # return the i child item
    XUPItem* child( int i )
    # return children list
    XUPItemList childrenList()
    # index of a child
    int childIndex( XUPItem* child )
    # set a child item for row i
    void addChild( XUPItem* item )
    # return the parent item
    XUPItem* parent()
    # return the item row. If item hasn't parent -1 will be return
    int row()
    # return child count
    int childCount()
    # remove a child and inform the model if possible
    void removeChild( XUPItem* item )
    # create a child of type at given row, row is -1 the item is append to the end
    XUPItem* addChild( XUPItem.Type type, row = -1 )
    # return the model associated with the item or null if item is not yet in a model
    XUPProjectModel* model()
    # return the QModelIndex of the item if it's in a model, an invalid qmodelindex
    QModelIndex index()
    
    # the type enum of self item
    XUPItem.Type type()

    # return the content of attribute name or defaultValue if null/invalid
    QString attribute(  QString& name, defaultValue = QString.null )
    # set the attribute value for name
    void setAttribute(  QString& name, value )
    
    # return the stored temporary value for key or defaultValue
    QVariant temporaryValue(  QString& key, defaultValue = QVariant() )
    # set the temporary value for key
    void setTemporaryValue(  QString& key, value )
    # clear temporary data represented by key
    void clearTemporaryValue(  QString& key )
    
    # return the stored cache value for key or defaultValue
    QString cacheValue(  QString& key, defaultValue = QString.null )
    # set the cache value for key
    void setCacheValue(  QString& key, value )
    # clear cache data represented by key
    void clearCacheValue(  QString& key )
    
    # view text, text to shown in the item view
    QString displayText()
    # view icon, icon to shown in the item view
    QIcon displayIcon()

protected:
    XUPProjectModel* mModel
    QDomElement mDomElement
    mutable QMap<int, mChildItems
    XUPItem* mParentItem
    QMap<QString, mTemporaryValues
    
    # developer must not be able to create/instanciate items itself, must be done by the model
    XUPItem(  QDomElement& node, parent = 0 )
    # set the parent item. Call automaticaly from parent's addChild
    void setParent( XUPItem* parentItem )

    # return the node element associate with self item
    QDomElement node()


Q_DECLARE_METATYPE( XUPItem* )

#endif # XUPITEM_H
