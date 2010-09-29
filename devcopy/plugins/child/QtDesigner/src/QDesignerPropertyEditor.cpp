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
#include "QDesignerPropertyEditor.h"

#include <objects/pIconManager.h>

#include <QDesignerFormEditorInterface>
#include <QDesignerComponents>
#include <QDesignerPropertyEditorInterface>

QDesignerPropertyEditor.QDesignerPropertyEditor( QDesignerFormEditorInterface* core )
    : pDockWidget( 0 )
    # need core
    Q_ASSERT( core )

    # dock title
    setWindowTitle( tr( "Property Editor" ) )
    setWindowIcon( pIconManager.icon( "property.png", ":/icons" ) )

    # object name 
    setObjectName( "x-designer/propertyeditor" )

    # create interface
    mInterface = QDesignerComponents.createPropertyEditor( core, self )

    # et dock widget
    setWidget( mInterface )

    # assign property editor to core
    core.setPropertyEditor( mInterface )

