'''***************************************************************************
**
** 		Created using Monkey Studio IDE v1.8.4.0 (1.8.4.0)
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Fresh Library
** FileName  : pActionsMenuBar.cpp
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
#include "pActionsMenuBar.h"
#include "pActionsModel.h"

pActionsMenuBar.pActionsMenuBar( QWidget* parent )
	: QMenuBar( parent )
	mModel = 0


def setModel(self, model ):
	if  mModel :		dismModel.actionInserted.connect(self.model_actionInserted)
		dismModel.actionsCleared.connect(self.model_actionsCleared)
		clear()
		mModel = 0

	
	mModel = model
	
	if  mModel :		for ( i = 0; i < mModel.rowCount(); i++ )			action = mModel.action( mModel.index( i, 0 ) )
			model_actionInserted( action )


	
	if  mModel :		mModel.actionInserted.connect(self.model_actionInserted)
		mModel.actionsCleared.connect(self.model_actionsCleared)



def model(self):
	if  not mModel :		mb = const_cast<pActionsMenuBar*>( self )
		mb.setModel( pActionsModel( mb ) )

	
	return mModel


def model_actionInserted(self, action ):
	parent = mModel.parent( action )
	
	if  not parent and action.menu() :		addMenu( action.menu() )



def model_actionsCleared(self):
	clear()

