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
/*!
	\file pMenuBar.h
	\date 2008-01-14T00:27:47
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief An extended QMenuBar
*/
#ifndef PMENUBAR_H
#define PMENUBAR_H

#include "objects/MonkeyExport.h"
#include "pGroupPath.h"
#include "pActionsManager.h"

#include <QMenuBar>
#include <QHash>
#include <QStack>
#include <QMenu>
#include <QAction>
#include <QIcon>

/*!
	\brief An extended QMenuBar
	\details This menu bar is working like a QSettings, you can get action/menu on the fly
	\details with call like this : menu->action( "mFile/aSave" );
	\details If the path is not existing then the complete action path is created.
*/
class Q_MONKEY_EXPORT pMenuBar : public QMenuBar
{
	Q_OBJECT

public:
	pMenuBar( QWidget* parent = 0 );
	~pMenuBar();

	QString absoluteScope( const QString& path );
	QString relativeScope( const QString& path );
	static QString normalizedKey( const QString& key );
	void beginGroupOrArray( const pGroupPath& group );
	void beginGroup( const QString& group );
	QString group() const;
	void endGroup();
	
	Qt::ShortcutContext defaultShortcutContext() const;
	void setDefaultShortcutContext( Qt::ShortcutContext context );
	
	pActionsManager* actionsManager() const;
	
	QMenu* menu( const QString& path = QString::null, const QString& title = QString::null, const QIcon& icon = QIcon() );
	QAction* action( const QString& path, const QString& text = QString::null, const QIcon& icon = QIcon(), const QString& shortcut = QString::null, const QString& toolTip = QString::null );
	void addAction( const QString& path, QAction* action );
	
	void clearMenu( const QString& path );
	void deleteMenu( const QString& path );
	void setMenuEnabled( QMenu* menu, bool enabled );
	
private:
	pActionsManager* mActionsManager;
	QHash<QString, QMenu*> mMenus;
	QStack<pGroupPath> groupStack;
	QString groupPrefix;
	Qt::ShortcutContext mDefaultShortcutContext;
};

#endif // PMENUBAR_H
