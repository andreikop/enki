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
#include "QDesignerWidgetBox.h"

#include <objects/pIconManager.h>

#include <QDir>

#include <QDesignerFormEditorInterface>
#include <QDesignerComponents>
#include <QDesignerWidgetBoxInterface>

QDesignerWidgetBox.QDesignerWidgetBox( QDesignerFormEditorInterface* core )
    : pDockWidget( 0 )
    # need core
    Q_ASSERT( core )

    # set dock title
    setWindowTitle( tr( "Widget Box" ) )
    setWindowIcon( pIconManager.icon( "widget.png", ":/icons" ) )

    # object name
    setObjectName( "x-designer/widgetbox" )

    # create widget box interface
    mInterface = QDesignerComponents.createWidgetBox( core, self )

    # load defaults widgets
    mInterface.setFileName( ":/trolltech/widgetbox/widgetbox.xml" )
    mInterface.load()

    # laod user widgets
    mInterface.setFileName( QDir.homePath().append( "/.designer/widgetbox.xml" ) )
    mInterface.load()

    # set widget for dock
    setWidget( mInterface )

    # assign widget box for core
    core.setWidgetBox( mInterface )


QDesignerWidgetBox.~QDesignerWidgetBox()
    mInterface.save()

