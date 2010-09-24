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
#include "pTabbedWorkspaceCornerButton.h"

#include <QPaintEvent>
#include <QMouseEvent>
#include <QStyleOptionToolButton>
#include <QToolBar>
#include <QMenu>
#include <QPainter>
#include <QApplication>

pTabbedWorkspaceCornerButton::pTabbedWorkspaceCornerButton( QWidget* p, QBoxLayout::Direction d )
	: QToolButton( p ), mMenuDown( false )
{
	/*
	QBoxLayout::LeftToRight
	QBoxLayout::RightToLeft
	QBoxLayout::TopToBottom
	QBoxLayout::BottomToTop
	*/

	setDirection( d );
}

void pTabbedWorkspaceCornerButton::paintEvent( QPaintEvent* )
{
	// calcul angle rotation
	QSize s = QToolButton::sizeHint();
	int r = 0;
	QPoint p = QPoint();
	switch ( mDirection )
	{
	case QBoxLayout::TopToBottom:
		r = 90;
		p = QPoint( 0, -s.height() );
		break;
	case QBoxLayout::BottomToTop:
		r = -90;
		p = QPoint( -s.width(), 0 );
		break;
	default:
		break;
	}

	// do rotated button
	QPixmap pixmap( s );
	pixmap.fill( QColor( 0, 0, 0, 0 ) );

	// get style options
	QStyleOptionToolButton o;
	setStyleOption( &o );

	// force to do horizontal paint
	o.rect.setSize( s );

	// fix backport bugs :|
	switch ( cursorArea() )
	{
	case pTabbedWorkspaceCornerButton::caArrow:
		break;
	case pTabbedWorkspaceCornerButton::caButton:
		break;
	case pTabbedWorkspaceCornerButton::caArrowClicked:
		break;
	case pTabbedWorkspaceCornerButton::caButtonClicked:
		o.activeSubControls |= QStyle::SC_ToolButton;
		if ( popupMode() == QToolButton::MenuButtonPopup )
		{
			o.state |= QStyle::State_MouseOver;
			o.activeSubControls |= QStyle::SC_ToolButtonMenu;
		}
		break;
	case pTabbedWorkspaceCornerButton::caNone:
	default:
		break;
	}

	// draw button to pixmap
	QPainter pixpainter( &pixmap );
	style()->drawComplexControl( QStyle::CC_ToolButton, &o, &pixpainter, this );

	// draw pixmap on button
	QPainter painter( this );
	painter.rotate( r );
	painter.drawPixmap( p, pixmap );
}

void pTabbedWorkspaceCornerButton::mousePressEvent( QMouseEvent* e )
{
	switch ( cursorArea( e->pos() ) )
	{
	case pTabbedWorkspaceCornerButton::caArrowClicked:
		mMenuDown = true;
		showMenu();
		mMenuDown = false;
		break;
	case pTabbedWorkspaceCornerButton::caButtonClicked:
		break;
	case pTabbedWorkspaceCornerButton::caNone:
		break;
	default:
		QAbstractButton::mousePressEvent( e );
		break;
	}

	// update button
	update();
}

void pTabbedWorkspaceCornerButton::mouseReleaseEvent( QMouseEvent* e )
{
	mMenuDown = false;

	switch ( cursorArea( e->pos() ) )
	{
	case pTabbedWorkspaceCornerButton::caArrow:
		break;
	case pTabbedWorkspaceCornerButton::caButton:
		click();
		break;
	case pTabbedWorkspaceCornerButton::caNone:
		break;
	default:
		QAbstractButton::mouseReleaseEvent( e );
		break;
	}

	// update button
	update();
}

pTabbedWorkspaceCornerButton::CursorArea pTabbedWorkspaceCornerButton::cursorArea( const QPoint& pos ) const
{
	// cursor pos
	const QPoint p = pos.isNull() ? mapFromGlobal( QCursor::pos() ) : pos;

	// if not contain is button return none
	if ( !hitButton( p ) )
		return pTabbedWorkspaceCornerButton::caNone;

	// is arrow type
	bool a = popupMode() == QToolButton::MenuButtonPopup;

	// is mouse pressed ?!
	bool m = QApplication::mouseButtons() & Qt::LeftButton;

	// check if we are a arrow button
	if ( a )
	{
		// get bounding rectangle
		QRect r = rect();
	
		// get style options
		QStyleOptionToolButton opt;
		setStyleOption( &opt );
	
		// force to do horizontal calcul
		opt.rect.setSize( QToolButton::sizeHint() );

		// get arraow bounding rectangle
		QSize s = style()->subControlRect( QStyle::CC_ToolButton, &opt, QStyle::SC_ToolButtonMenu, this ).size();

		switch ( mDirection )
		{
		case QBoxLayout::BottomToTop:
			s.transpose();
			break;
		case QBoxLayout::TopToBottom:
			s.transpose();
			r.setY( r.height() -s.height() );
			break;
		default:
			r.setX( r.width() -s.width() );
			break;
		}
	
		// get valid bounding rectangle size
		r.setSize( s );

		// in arrow bounding rect
		if ( r.isValid() && r.contains( p ) )
			return m ? pTabbedWorkspaceCornerButton::caArrowClicked : pTabbedWorkspaceCornerButton::caArrow;
	}

	// in button
	return m ? pTabbedWorkspaceCornerButton::caButtonClicked : pTabbedWorkspaceCornerButton::caButton;
}

QMenu* pTabbedWorkspaceCornerButton::hasMenu() const
{
	QMenu* m = menu();
	if ( !m && defaultAction() )
		m = defaultAction()->menu();
	return m;
}

bool pTabbedWorkspaceCornerButton::menuButtonDown() const
{
#ifndef QT_NO_MENU
	return hasMenu() && mMenuDown;
#else
	return false;
#endif
}

void pTabbedWorkspaceCornerButton::setStyleOption( QStyleOptionToolButton* option ) const
{
	if ( !option )
		return;

#if QT_VERSION >= 0x040300
	initStyleOption( option );
#else
	// backported from Qt 4.3
	option->initFrom( this );
	bool forceNoText = false;
	
#ifndef QT_NO_TOOLBAR
		if ( parentWidget() )
		{
#ifdef QT3_SUPPORT
		if ( parentWidget()->inherits( "Q3ToolBar" ) )
		{
			int iconSize = style()->pixelMetric( QStyle::PM_ToolBarIconSize, option, this );
			option->iconSize = icon().actualSize( QSize( iconSize, iconSize ) );
			forceNoText = toolButtonStyle() == Qt::ToolButtonIconOnly;
		}
		else
#endif
		if ( QToolBar* toolBar = qobject_cast<QToolBar*>( parentWidget() ) )
		{
			option->iconSize = toolBar->iconSize();
		}
		else
		{
			option->iconSize = iconSize();
		}
	}
#endif // QT_NO_TOOLBAR
	
		if ( !forceNoText )
		option->text = text();
	option->icon = icon();
	option->arrowType = arrowType();
	if ( isDown() )
		option->state |= QStyle::State_Sunken;

	if ( isChecked() )
		option->state |= QStyle::State_On;
	if ( autoRaise() )
		option->state |= QStyle::State_AutoRaise;
	if ( !isChecked() && !isDown() )
		option->state |= QStyle::State_Raised;
	
		option->subControls = QStyle::SC_ToolButton;
		option->activeSubControls = QStyle::SC_None;
		//if ( isDown() && !menuButtonDown() )
		//option->activeSubControls |= QStyle::SC_ToolButton;
	
		option->features = QStyleOptionToolButton::None;
		if ( popupMode() == QToolButton::MenuButtonPopup )
		{
		option->subControls |= QStyle::SC_ToolButtonMenu;
#if QT_VERSION >= 0x040300
		option->features |= QStyleOptionToolButton::MenuButtonPopup;
#endif
		if ( menuButtonDown() || isDown() )
		{
			option->state |= QStyle::State_MouseOver;
			option->activeSubControls |= QStyle::SC_ToolButtonMenu;
		}
	}
	else
	{
		if ( menuButtonDown() )
			option->state  |= QStyle::State_Sunken;
	}
	if ( arrowType() != Qt::NoArrow )
		option->features |= QStyleOptionToolButton::Arrow;
	if ( popupMode() == QToolButton::DelayedPopup )
		option->features |= QStyleOptionToolButton::PopupDelay;
#ifndef QT_NO_MENU
	if ( hasMenu() )
#if QT_VERSION >= 0x040300
		option->features |= QStyleOptionToolButton::HasMenu;
#else
		option->features |= QStyleOptionToolButton::Menu;
#endif
#endif
	option->toolButtonStyle = toolButtonStyle();
	if ( icon().isNull() && arrowType() == Qt::NoArrow && !forceNoText)
	{
		if ( !text().isEmpty() )
			option->toolButtonStyle = Qt::ToolButtonTextOnly;
		else if ( option->toolButtonStyle != Qt::ToolButtonTextOnly )
			option->toolButtonStyle = Qt::ToolButtonIconOnly;
	}
	else
	{
		if ( text().isEmpty() && option->toolButtonStyle != Qt::ToolButtonIconOnly )
			option->toolButtonStyle = Qt::ToolButtonIconOnly;
	}

	option->pos = pos();
	option->font = font();
#endif // QT_VERSION >= 0x040300
}

QSize pTabbedWorkspaceCornerButton::sizeHint() const
{
	//get default size
	QSize s = QToolButton::sizeHint();

	// calcul new size hint
	switch ( mDirection )
	{
	case QBoxLayout::LeftToRight:
	case QBoxLayout::RightToLeft:
		break;
	case QBoxLayout::TopToBottom:
	case QBoxLayout::BottomToTop:
		s.transpose();
		break;
	}

	// return new size hint;
	return s;
}

QBoxLayout::Direction pTabbedWorkspaceCornerButton::direction() const
{
	return mDirection;
}

void pTabbedWorkspaceCornerButton::setDirection( QBoxLayout::Direction d )
{
	if ( mDirection == d )
		return;
	mDirection = d;
	update();
}
