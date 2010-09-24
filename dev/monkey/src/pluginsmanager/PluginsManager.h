/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : PluginsManager.h
** Date      : 2008-01-14T00:37:01
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
**
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
**
****************************************************************************/
#ifndef PLUGINSMANAGER_H
#define PLUGINSMANAGER_H

#include <objects/MonkeyExport.h>

#include "BasePlugin.h"
#include "ChildPlugin.h"
#include "BuilderPlugin.h"
#include "DebuggerPlugin.h"
#include "InterpreterPlugin.h"

class XUPItem;
class pAbstractChild;
class PluginsMenu;

class Q_MONKEY_EXPORT PluginsManager : public QObject
{
	Q_OBJECT
	friend class MonkeyCore;
	
public:
	enum StateType { stAll = -1, stDisabled, stEnabled };

	void loadsPlugins();
	
	QList<BasePlugin*> plugins() const;
	template <class T>
	QList<T> plugins( PluginsManager::StateType t, const QString& n = QString::null, const QString& v = QString::null )
	{
		// temporary list
		QList<T> l;
		// for each plugin
		foreach ( BasePlugin* bp, mPlugins )
			// plugin state
			if ( t == stAll || ( !bp->isEnabled() && t == stDisabled ) || ( bp->isEnabled() && t == stEnabled ) )
				// empty or good name
				if ( n.isEmpty() || bp->infos().Name == n )
					// no version or good version
					if ( v.isEmpty() || bp->infos().Version == v )
						// good cast
						if ( T p = qobject_cast<T>( bp ) )
							l << p;
		// return list
		return l;
	}
	template <class T>
	T plugin( PluginsManager::StateType type, const QString& name,  const QString& version = QString::null )
	{
		if ( name.isEmpty() )
			return 0;
		return plugins<T>( type, name, version ).value( 0 );
	}
	
	pAbstractChild* documentForFileName( const QString& fileName );
	QMap<QString, QStringList> childSuffixes() const;
	QString childFilters() const;
	
	void setCurrentBuilder( BuilderPlugin* );
	BuilderPlugin* currentBuilder();
	
	void setCurrentDebugger( DebuggerPlugin* );
	DebuggerPlugin* currentDebugger();
	
	void setCurrentInterpreter( InterpreterPlugin* );
	InterpreterPlugin* currentInterpreter();
	
	inline PluginsMenu* menuHandler() const { return mMenuHandler; }
	
protected:
	PluginsMenu* mMenuHandler;
	QList<BasePlugin*> mPlugins;
	BuilderPlugin* mBuilder;
	DebuggerPlugin* mDebugger;
	InterpreterPlugin* mInterpreter;

	PluginsManager( QObject* = 0 );
	bool addPlugin( QObject* );
	void enableUserPlugins();
	
public slots:
	void manageRequested();
	void clearPlugins();
};

#endif // PLUGINSMANAGER_H
