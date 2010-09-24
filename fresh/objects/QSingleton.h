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
	\file QSingleton.h
	\date 2008-01-14T00:27:37
	\author Filipe AZEVEDO aka Nox P\@sNox <pasnox@gmail.com>
	\brief Singletonize your QObject class
*/
#ifndef QSINGLETON_H
#define QSINGLETON_H

#include "MonkeyExport.h"

#include <QHash>
#include <QMetaObject>
#include <QApplication>

/*!
	\brief Internal hash of instances
	\details This class contains unique instance pointer of singletonized classes
*/
class Q_MONKEY_EXPORT QSingletonExpose
{
protected:
	static QHash<const QMetaObject*, QObject*> mInstances;
};

/*!
	\brief Singletonize your QObject class
	\details When heriting this template, you self made your class singletonizable ( unique instance ) ( ie: call like youclass::instance() )
*/
template <class T>
class QSingleton : public QSingletonExpose
{
protected:
	QSingleton() {};
	virtual ~QSingleton()
	{ mInstances.remove( &T::staticMetaObject ); }

public:
	template <typename P>
	static T* instance( P* pointer );
	static T* instance();
	static bool instanceAvailable();
	static void cleanInstance();
};

/*!
	\details Return an unique instance of the class
	\param pointer A pointer that is given to constructor of the class
*/
template <class T>
template <typename P>
T* QSingleton<T>::instance( P* pointer )
{
	T* t = qobject_cast<T*>( mInstances.value( &T::staticMetaObject ) );
	if ( !t )
		mInstances[&T::staticMetaObject] = ( t = new T( pointer ) );
	return t;
}

/*!
	\details Return an unique instance of the class
*/
template <class T>
T* QSingleton<T>::instance()
{
	T* t = qobject_cast<T*>( mInstances.value( &T::staticMetaObject ) );
	if ( !t )
#ifdef Q_CC_GNU
		mInstances[&T::staticMetaObject] = ( t = new T );
#else
		mInstances[&T::staticMetaObject] = ( t = new T( 0 ) );
#endif
	return t;
}

/*!
	\details Return true if an instance of the class already exists, else return false
*/
template <class T>
bool QSingleton<T>::instanceAvailable()
{ return mInstances.contains( &T::staticMetaObject ); }

/*!
	\details Clear the instance if instance is available
*/
template <class T>
void QSingleton<T>::cleanInstance()
{
	if ( instanceAvailable() )
		delete mInstances[ &T::staticMetaObject ];
}

#endif // QSINGLETON_H
