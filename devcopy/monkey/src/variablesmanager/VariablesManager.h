'''***************************************************************************
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
***************************************************************************'''
'''!
    \file VariablesManager.h
    \date 2008-01-14T00:37:18
    \author Andrei KOPATS
    \brief Header for VariablesManager class
'''

#ifndef VARIABLESMANAGER_H
#define VARIABLESMANAGER_H

#include <objects/MonkeyExport.h>
#include <objects/QSingleton.h>

#include <QApplication>
#include <QHash>

'''!
    \brief Implementation of Variables Manager
    Variables Manager allowing you to replace names of some variables
    in the string with according values.
'''
class Q_MONKEY_EXPORT VariablesManager : public QObject, QSingleton<VariablesManager>
    Q_OBJECT
    friend class QSingleton<VariablesManager>

private:
    VariablesManager( QObject* = QApplication.instance() )

public:
    typedef QHash<QString, Dictionary
    #Returns variable.
    #value = QString.null used, variable is not set
    QString getVariable( QString name, locals )

    #Is variable set
    bool isSet( QString name, locals )

    #Will replace all variables in the string with values
    #If locals are presented, will be searched there too
    QString replaceAllVariables( QString str, locals = Dictionary() )

private:
    #Hash for storing global constand variables. (Kernel version for example)
    Dictionary globals


#endif #VARIABLESMANAGER_H
