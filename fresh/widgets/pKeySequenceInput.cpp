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
#include "pKeySequenceInput.h"

#include <QKeySequence>
#include <QKeyEvent>

/*!
	\details Create a new pKeySequenceInput object
	\param parent The parent widget
*/
pKeySequenceInput::pKeySequenceInput( QWidget* parent )
	: QLineEdit( parent )
{}

void pKeySequenceInput::keyPressEvent( QKeyEvent* event )
{	
	// return if auto repeat
	if ( event->isAutoRepeat() )
		return;
	
	// if user press something, sequence is not finished
	setProperty( "Finished", false );
	
	// show current sequence
	setText( checkKeyEvent( event ) );
}

void pKeySequenceInput::keyReleaseEvent( QKeyEvent* event )
{
	// return if auto repeat
	if ( event->isAutoRepeat() )
		return;
	
	// check if sequence is finished or not
	if ( property( "Finished" ).toBool() )
		return;
	
	// show current sequence
	setText( checkKeyEvent( event ) );
}

/*!
	\details Check a QKeyEvent event
	\param event The QKeyEvent to check
	\return The QString shortcut generate from the QKeyEvent
*/
QString pKeySequenceInput::checkKeyEvent( QKeyEvent* event )
{
// is key pressed or key released ?
	const bool keyPressed = event->type() == QEvent::KeyPress;
	
	// or-ed keys
	int mKeys = 0;
	
	// check modifiers pressed
	if ( event->modifiers() & Qt::ControlModifier )
		mKeys |= Qt::ControlModifier;
	if ( event->modifiers() & Qt::AltModifier )
		mKeys |= Qt::AltModifier;
	if ( event->modifiers() & Qt::ShiftModifier )
		mKeys |= Qt::ShiftModifier;
	if ( event->modifiers() & Qt::MetaModifier )
		mKeys |= Qt::MetaModifier;
	
	if ( keyPressed )
	{
		// get press key
		switch( event->key() )
		{
			// this keys can't be used
			case Qt::Key_Shift:
			case Qt::Key_Control:
			case Qt::Key_Meta:
			case Qt::Key_Alt:
			case Qt::Key_AltGr:
			case Qt::Key_Super_L:
			case Qt::Key_Super_R:
			case Qt::Key_Menu:
			case Qt::Key_Hyper_L:
			case Qt::Key_Hyper_R:
			case Qt::Key_Help:
			case Qt::Key_Direction_L:
			case Qt::Key_Direction_R:
				break;
			default:
				// add pressed key
				mKeys |= event->key();
				
				// set sequence finished
				setProperty( "Finished", true );
				break;
		}
	}
	
	// return human readable key sequence
	return QKeySequence( mKeys ).toString();
}
