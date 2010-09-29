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
#ifndef QDESIGNEROBJECTINSPECTOR_H
#define QDESIGNEROBJECTINSPECTOR_H

#include <widgets/pDockWidget.h>

class QDesignerFormEditorInterface
class QDesignerObjectInspectorInterface

class QDesignerObjectInspector : public pDockWidget
public:
    QDesignerObjectInspector( QDesignerFormEditorInterface* core )
    inline QDesignerObjectInspectorInterface* interface()  { return mInterface;
    
private:
    QDesignerObjectInspectorInterface* mInterface


#endif # QDESIGNEROBJECTINSPECTOR_H
