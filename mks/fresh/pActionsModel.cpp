'''***************************************************************************
**
** 		Created using Monkey Studio IDE v1.8.4.0 (1.8.4.0)
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Fresh Library
** FileName  : pActionsModel.cpp
** Date      : 2011-02-20T00:41:09
** License   : LGPL v3
** Home Page : https:#github.com/pasnox/fresh
** Comment   : Fresh Library is a Qt 4 extension library providing set of core & gui classes.
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU Leser General Public License as published by
** the Free Software Foundation, version 3 of the License, or
** (at your option) any later version.
**
** This package is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
** GNU Lesser General Public License for more details.
**
** You should have received a copy of the GNU Lesser General Public License
** along with self program. If not, see <http:#www.gnu.org/licenses/>.
**
***************************************************************************'''
#include "pActionsModel.h"

#include <QMenu>
#include <QAction>
#include <QDir>
#include <QDebug>

#define DEFAULT_SHORTCUT_PROPERTY "Default Shortcut"

int pActionsModel.mColumnCount = 3

pActionsModel.pActionsModel( QObject* parent )
	: QAbstractItemModel( parent )
#ifndef QT_NO_DEBUG
	mDebugging = False
#endif


pActionsModel.~pActionsModel()
	clear()


def columnCount(self, parent ):
	Q_UNUSED( parent )
	return mColumnCount


def data(self, index, role ):
	action = self.action( index )
	
	if  not action :		return QVariant()

	
	switch ( role )		case Qt.DecorationRole:
			switch ( index.column() )				case 0:
					return action.icon()
				default:
					break

			
			break
		case Qt.DisplayRole:
		case Qt.ToolTipRole:
			switch ( index.column() )				case pActionsModel.Action:
					return cleanText( action.text() )
				case pActionsModel.Shortcut:
					return action.shortcut().toString( QKeySequence.NativeText )
				case pActionsModel.DefaultShortcut:
					return defaultShortcut( action ).toString( QKeySequence.NativeText )

			
			break
		
		case Qt.FontRole:			font = action.font()
			
			if  action.menu() :				font.setBold( True )

			
			return font

		
		'''case Qt.BackgroundRole:
			return action.menu() ? QBrush( QColor( 0, 0, 255, 20 ) ) : QVariant();'''
		
		case pActionsModel.MenuRole:
			return QVariant.fromValue( action.menu() )
		case pActionsModel.ActionRole:
			return QVariant.fromValue( action )

	
	return QVariant()


def index(self, row, column, parent ):
	action = self.action( parent )
	QList<QAction*> actions = children( action )
	
	if  row < 0 or row >= actions.count(:
		or column < 0 or column >= mColumnCount
		or ( parent.column() != 0 and parent.isValid() ) )		return QModelIndex()

	
	return createIndex( row, column, actions.at( row ) )


def parent(self, index ):
	action = self.action( index )
	parentAction = parent( action )
	parentParentAction = parent( parentAction )
	 row = children( parentParentAction ).indexOf( parentAction )
	return row != -1 ? createIndex( row, 0, parentAction ) : QModelIndex()


def rowCount(self, parent ):
	action = self.action( parent )
	return ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex()
		? children( action ).count()
		: 0


def hasChildren(self, parent ):
	action = self.action( parent )
	return ( parent.isValid() and parent.column() == 0 ) or parent == QModelIndex()
		? hasChildren( action )
		: False


def headerData(self, section, orientation, role ):
	switch ( orientation )		case Qt.Horizontal:			if  role == Qt.DisplayRole or role == Qt.ToolTipRole :				switch ( section )					case pActionsModel.Action:
						return tr( "Action" )
					case pActionsModel.Shortcut:
						return tr( "Shortcut" )
					case pActionsModel.DefaultShortcut:
						return tr( "Default Shortcut" )


			
			break

		
		default:
			break

	
	return QAbstractItemModel.headerData( section, orientation, role )


def index(self, action, column ):
	 path = self.path( action )
	
	if  not mActions.contains( path ) :		return QModelIndex()

	
	parentAction = parent( action )
	 row = children( parentAction ).indexOf( action )
	return row != -1 ? createIndex( row, column, mActions[ path ] ) : QModelIndex()


def action(self, index ):
	return isValid( index ) ? static_cast<QAction*>( index.internalPointer() ) : 0


def path(self, action ):
	return mActions.key( action )


def action(self, path ):
	return mActions.value( cleanPath( path ) )


def clear(self):
	 count = rowCount()
	
	if  count == 0 :		return

	
	beginRemoveRows( QModelIndex(), 0, count -1 )
	qDeleteAll( mChildren.value( 0 ) )
	mChildren.clear()
	mActions.clear()
	endRemoveRows()
	
	actionsCleared.emit()


def addAction(self, _path, action ):
	Q_ASSERT( action )
	
	if  not action or not path( action ).isEmpty() or self.action( _path ) :		return False

	
	 path = cleanPath( _path )
	 subPath = path.section( '/', 0, -2 )
	parentAction = createCompletePathNode( subPath )
	
	if  not parentAction :		return False

	
	 row = children( parentAction ).count()
	insertAction( path, action, parentAction, row )
	return True


def addAction(self, path, text, icon ):
	action = QAction( icon, text, self )
	
	if  not addAction( path, action ) :		delete action
		return 0

	
	return action


def addMenu(self, path, text, icon ):
	action = createCompletePathNode( path )
	
	if  action :		action.setIcon( icon )
		
		if  not text.isEmpty() :			action.setText( text )


	
	return action


def removeAction(self, path, removeEmptyPath ):
	return removeMenu( path, removeEmptyPath )


def removeAction(self, action, removeEmptyPath ):
	return removeMenu( action, removeEmptyPath )


def removeMenu(self, path, removeEmptyPath ):
	return removeMenu( action( path ), removeEmptyPath )


def removeMenu(self, action, removeEmptyPath ):
	if  not action :		return False

	
	parentAction = parent( action )
	 row = children( parentAction ).indexOf( action )
	
	removeAction( action, parentAction, row )
	
	if  removeEmptyPath :		removeCompleteEmptyPathNode( parentAction )

	
	return True


def parent(self, action ):
	return mActions.value( path( action ).section( '/', 0, -2 ) )


def hasChildren(self, action ):
	return not mChildren.value( action ).isEmpty()


def children(self, action ):
	return mChildren.value( action )


def defaultShortcut(self, action ):
	return action ? action.property( DEFAULT_SHORTCUT_PROPERTY ).value<QKeySequence>() : QKeySequence()


def defaultShortcut(self, path ):
	return defaultShortcut( action( path ) )


def setDefaultShortcut(self, action, shortcut ):
	if  action :		action.setProperty( DEFAULT_SHORTCUT_PROPERTY, shortcut )
		
		if  action.shortcut().isEmpty() :			setShortcut( action, shortcut )




def setDefaultShortcut(self, path, shortcut ):
	setDefaultShortcut( action( path ), shortcut )


def setShortcut(self, action, shortcut, error ):
	for a in mActions.values():		if  a != action :			if  not a.shortcut().isEmpty() :				if  a.shortcut() == shortcut :					if  error :						*error = tr( "Can't set shortcut, it's already used by action '%1'." ).arg( cleanText( a.text() ) )

					
					return False




	
	action.setShortcut( shortcut )
	return True


def setShortcut(self, path, shortcut, error ):
	return setShortcut( action( path ), shortcut, error )


def cleanPath(self, path ):
	data = QDir.cleanPath( path )
		.replace( '\\', '/' )
		#.remove( ' ' )
		.trimmed()
		
	
	while ( data.startsWith( '/' ) )		data.remove( 0, 1 )

	
	while ( data.endsWith( '/' ) )		data.chop( 1 )

	
	return data


#ifndef QT_NO_DEBUG
def debugInternals(self):
	for parent in mChildren.keys():		qWarning() << ( parent ? parent.text() : "ROOT" ).toAscii().constData() << parent
		qWarning() << QString( 1, '\t' ).toAscii().constData() << mChildren.value( parent )

	
	qWarning() << mActions.keys()


def isDebugging(self):
	return mDebugging


def setDebugging(self, debugging ):
	mDebugging = debugging

#endif

def isValid(self, index ):
	if  not index.isValid() or index.row() < 0 or index.column() < 0 or index.column() >= mColumnCount :		return False

	
	action = static_cast<QAction*>( index.internalPointer() )
	parentAction = parent( action )
	
	if  not action :		return False

	
	if  index.row() >= children( parentAction ).count() :		return False

	
	return True


def cleanText(self, text ):
	 sep = "\001"
	return QString( text )
		.replace( "and", sep )
		.remove( "&" )
		.replace( sep, "and" )


def insertAction(self, path, action, parent, row ):
	Q_ASSERT( row != -1 )
	
	p = parent
	
	if  not p :		p = self

	
#ifndef QT_NO_DEBUG
	if  mDebugging :		qWarning() << path << action << parent << row << index( parent ) << index( rowCount() -1, 0 )
		qWarning() << index( parent ).data() << index( rowCount() -1, 0 ).data()

#endif
	
	beginInsertRows( index( parent ), row, row )
	action.setObjectName( QString( path ).replace( "/", "_" ) )
	action.setParent( p )
	if  parent :		parent.menu().addAction( action )

	if  action.text().isEmpty() :		action.setText( path.section( '/', -1, -1 ) )

	mChildren[ parent ] << action
	mActions[ path ] = action
	action.changed.connect(self.actionChanged)
	action.destroyed.connect(self.actionDestroyed)
	endInsertRows()
	
	actionInserted.emit( action )


def cleanTree(self, action, parent ):
	foreach ( QAction* a, mChildren.value( action  ) )		cleanTree( a, action )

	
	QList<QAction*>parentChildren = mChildren[ parent ]
	parentChildren.removeAt( parentChildren.indexOf( action ) )
	mChildren.remove( action )
	mActions.remove( path( action ) )


def removeAction(self, action, parent, row ):
	Q_ASSERT( row != -1 )
	
	beginRemoveRows( index( parent ), row, row )
	if  parent :		parent.menu().removeAction( action )

	cleanTree( action, parent )
	endRemoveRows()
	
	actionRemoved.emit( action )
	
	action.deleteLater()


def createCompletePathNode(self, path ):
	action = mActions.value( path )
	
	if  action :		return action.menu() ? action : 0

	
	 separatorCount = path.count( "/" ) +1
	parentAction = 0
	QString subPath
	
	for ( i = 0; i < separatorCount; i++ )		subPath = path.section( '/', 0, i )
		action = mActions.value( subPath )
		
		if  action :			if  path != subPath :				continue

			
			return action.menu() ? action : 0

		
		parentAction = mActions.value( i == 0 ? QString.null : path.section( '/', 0, i -1 ) )
		 row = children( parentAction ).count()
		action = (new QMenu).menuAction()
		action.setText( path.section( '/', i, i ) )
		insertAction( subPath, action, parentAction, row )

	
	return action


def removeCompleteEmptyPathNode(self, action ):
	if  not action or not mActions.contains( path( action ) ) :		return

	
	if  not hasChildren( action ) :		parentAction = parent( action )
		 row = children( parentAction ).indexOf( action )
		
		removeAction( action, parentAction, row )
		removeCompleteEmptyPathNode( parentAction )



def actionChanged(self):
	action = qobject_cast<QAction*>( sender() )
	
	if  action :		dataChanged.emit( index( action, 0 ), index( action, mColumnCount -1 ) )
		actionChanged.emit( action )



def actionDestroyed(self, object ):
	action = (QAction*)object
	path = self.path( action )
	
	if  mActions.contains( path ) :		removeAction( path )


