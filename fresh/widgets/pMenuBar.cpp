/****************************************************************************
	Copyright (C) 2005 - 2008  Filipe AZEVEDO & The Monkey Studio Team

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
****************************************************************************/
#include "pMenuBar.h"

#include <QDebug>

/*!
	\brief Create a new pMenuBar object
	\param parent The parent widget
*/
pMenuBar::pMenuBar( QWidget* parent )
	: QMenuBar( parent )
{
	mDefaultShortcutContext = Qt::WindowShortcut;
	mActionsManager = new pActionsManager( "Menu Bar", this );
}

pMenuBar::~pMenuBar()
{
	qDebug() << "menubar cpp object deleted";
}


/*!
	\details Return a full path of path
	\param path The path to make full
*/
QString pMenuBar::absoluteScope( const QString& path )
{
	QString fPath = QString( path ).prepend( groupPrefix );
	
	return mActionsManager->fixedPath( fPath );
}

QString pMenuBar::relativeScope( const QString& path )
{
	QString mPath = mActionsManager->fixedPath( path );
	
	if ( mPath.startsWith( groupPrefix ) )
	{
		return mPath.mid( groupPrefix.length() );
	}
	
	QString prf = groupPrefix.left( groupPrefix.length() -1 );
	
	if ( mPath.startsWith( prf ) )
	{
		return mPath.mid( prf.length() );
	}
	
	return mPath;
}

QString pMenuBar::normalizedKey( const QString& key )
{
	QString r = key;
	int i = 0;
	
	while ( i < r.size() )
	{
		while ( r.at( i ) == QLatin1Char( '/' ) )
		{
			r.remove( i, 1 );
			
			if ( i == r.size() )
			{
				goto after_loop;
			}
		}
		while ( r.at( i ) != QLatin1Char( '/' ) )
		{
			++i;
			
			if ( i == r.size() )
			{
				return r;
			}
		}
		
		++i; // leave the slash alone
	}

after_loop:
	if ( !r.isEmpty() )
	{
		r.truncate( i -1 ); // remove the trailing slash
	}
	
	return r;
}

void pMenuBar::beginGroupOrArray( const pGroupPath& group )
{
	groupStack.push( group );
	
	if ( !group.name().isEmpty() )
	{
		groupPrefix += group.name();
		groupPrefix += QLatin1Char( '/' );
	}
}

/*!
	\details Begin a \c group
	\see QSettings::beginGroup()
*/
void pMenuBar::beginGroup( const QString& group )
{
	beginGroupOrArray( pGroupPath( normalizedKey( group ) ) );
}

/*!
	\details Return the current group
	\see QSettings::group()
*/
QString pMenuBar::group() const
{
	return groupPrefix.left( groupPrefix.size() -1 );
}

/*!
	\details End a group
	\see QSettings::endGroup()
*/
void pMenuBar::endGroup()
{
	if ( groupStack.isEmpty() )
	{
		qWarning( "pMenuBar::endGroup: No matching beginGroup()" );
		return;
	}

	pGroupPath g = groupStack.pop();
	int len = g.toString().size();
	
	if ( len > 0 )
	{
		groupPrefix.truncate( groupPrefix.size() -( len +1 ) );
	}

	if ( g.isArray() )
	{
		qWarning( "pMenuBar::endGroup: Expected endArray() instead" );
	}
}

/*!
	\details Return the default ShortcutContext used by actions created by the class
*/
Qt::ShortcutContext pMenuBar::defaultShortcutContext() const
{
	return mDefaultShortcutContext;
}

/*!
	\details Set the default ShortcutContext used by actions created by the class
	\param context The default ShortcutContext
*/
void pMenuBar::setDefaultShortcutContext( Qt::ShortcutContext context )
{
	mDefaultShortcutContext = context;
}

/*!
	\details Return the pActionsManager used by this pMenuBar
*/
pActionsManager* pMenuBar::actionsManager() const
{
	return mActionsManager;
}

/*!
	\details Return a QMenu at \c path.
	\details If the path don't exists, the menu is created and
	\details title and icon are used as meu properties.
	\param path The QMenu path to get
	\param title The menu title
	\param icon The menu icon
*/
QMenu* pMenuBar::menu( const QString& path, const QString& title, const QIcon& icon )
{
	QString fPath = absoluteScope( path );
	
	if ( !mMenus.contains( fPath ) )
	{
		QStringList parts = fPath.split( "/" );
		QString curPath;
		
		for ( int i = 0; i < parts.count(); i++ )
		{
			curPath += "/" +parts.at( i );
			
			if ( curPath[ 0 ] == '/' )
			{
				curPath.remove( 0, 1 );
			}
			
			if ( !mMenus.contains( curPath ) )
			{
				QMenu* mnu = 0;
				
				if ( curPath.contains( '/' ) )
				{
					const QString parentPath = curPath.left( curPath.lastIndexOf( '/' ) );
					mnu = mMenus[ parentPath ]->addMenu( parts.at( i ) );
				}
				else
				{
					mnu = addMenu( parts.at( i ) );
				}
				
				mMenus[ curPath ] = mnu;
				mMenus[ curPath ]->setObjectName( parts.at( i ) );
				mMenus[ curPath ]->setTitle( parts.at( i ) );
			}
		}
	}
	
	QMenu* mnu = mMenus[ fPath ];
	
	if ( !title.isEmpty() && mnu->title() != title )
	{
		mnu->setTitle( title );
		
		fPath = mActionsManager->fixedPath( path );
		if (!fPath.contains( '/' ) )
		{
			mActionsManager->setPathPartTranslation( fPath, title );
		}
	}
	
	if ( !icon.isNull() && mnu->icon().cacheKey() != icon.cacheKey() )
	{
		mnu->setIcon( icon );
	}
	
	return mnu;
}

QAction* pMenuBar::action( const QString& path, const QString& text, const QIcon& icon, const QString& shortcut, const QString& toolTip )
{
	QString fPath = absoluteScope( path );
	QString aName = fPath.mid( fPath.lastIndexOf( '/' ) +1 );
	QString mPath;

	if ( fPath.contains( '/' ) )
	{
		mPath = fPath.mid( 0, fPath.lastIndexOf( '/' ) );
	}
	
	// get action
	QAction* action = mActionsManager->action( mPath, aName );

	// create action if needed
	if ( !action )
	{
		// create actions
		action = mActionsManager->newAction( mPath, shortcut, aName );
		
		// check for separator
		if ( aName.contains( QRegExp( "^aseparator\\d{1,2}$", Qt::CaseInsensitive ) ) )
		{
			action->setSeparator( true );
		}
		
		// setup action
		action->setShortcutContext( mDefaultShortcutContext );
		
		if ( !text.isEmpty() )
		{
			action->setText( text );
		}
		
		if ( !icon.isNull() )
		{
			action->setIcon( icon );
		}
		
		if ( !toolTip.isEmpty() )
		{
			action->setStatusTip( toolTip );
		}

		if ( !toolTip.isEmpty() )
		{
			action->setToolTip( toolTip );
		}
		
		// add action to menu
		menu( relativeScope( mPath ) )->addAction( action );
	}

	// return action
	return action;
}

void pMenuBar::addAction( const QString& path, QAction* action )
{
	Q_ASSERT( action );
	
	if ( mActionsManager->actions().contains( action ) )
	{
		return;
	}
	
	QMenu* mnu = menu( path );
	
	action->setShortcutContext( mDefaultShortcutContext );
	pActionsManager::setActionPath( action, absoluteScope( path ) );
	pActionsManager::setActionsManager( action, mActionsManager );
	
	mnu->addAction( action );
}

void pMenuBar::clearMenu( const QString& path )
{
	const QString fPath = absoluteScope( path );
	QMenu* mnu = mMenus.value( fPath );
	
	if ( mnu )
	{
		mnu->clear();
		
		foreach ( QAction* action, mActionsManager->actions( fPath ) )
		{
			if ( action->associatedWidgets().isEmpty() )
			{
				delete action;
			}
		}
	}
}

void pMenuBar::deleteMenu( const QString& _path )
{
	const QString fPath = absoluteScope( _path );
	QMenu* mnu = mMenus.value( fPath );
	
	if ( mnu )
	{
		QStringList paths;
		
		// get menu and sub menus
		foreach ( const QString& path, mMenus.keys() ) {
			if ( path.startsWith( fPath ) ) {
				paths << path;
			}
		}
		
		// sort so sub menu are deleted before parent menu
		qSort( paths.begin(), paths.end(), qGreater<QString>() );
		
		// delete menus
		foreach ( const QString& path, paths ) {
			clearMenu( path );
			delete mMenus.take( path );
		}
	}
}

void pMenuBar::setMenuEnabled( QMenu* mnu, bool enabled )
{
	if ( mnu )
	{
		foreach ( QAction* action, mnu->actions() )
		{
			action->setEnabled( enabled );
			
			if ( action->menu() )
			{
				setMenuEnabled( action->menu(), enabled );
			}
		}
		
		//mnu->menuAction()->setEnabled( enabled );
	}
}
