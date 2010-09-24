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
#include "pDockWidgetTitleBar.h"

#include <QHBoxLayout>
#include <QWidgetAction>
#include <QEvent>
#include <QStylePainter>
#include <QStyleOptionToolBar>
#include <QDebug>

pDockWidgetTitleBar::pDockWidgetTitleBar( pDockWidget* parent )
	: QToolBar( parent )
{
	Q_ASSERT( parent );
	mDock = parent;
	
	// a fake spacer widget
	QWidget* widget = new QWidget( this );
	QHBoxLayout* hlayout = new QHBoxLayout( widget );
	hlayout->setMargin( 0 );
	hlayout->setSpacing( 0 );
	hlayout->addStretch();
	
	// fake spacer item
	mSpacer = new QWidgetAction( this );
	mSpacer->setDefaultWidget( widget );
	
	setMovable( false );
	setFloatable( false );
	setIconSize( QSize( 12, 12 ) );
	layout()->setSpacing( 0 );
	layout()->setMargin( 2 );
	
	aOrientation = new QAction( this );
	aFloat = new QAction( this );
	aClose = new QAction( this );
	
	addAction( mSpacer );
	addAction( aOrientation );
	addAction( aFloat );
	addAction( aClose );
	
	updateStandardIcons();
	dockWidget_featuresChanged( mDock->features() );
	
	connect( mDock, SIGNAL( featuresChanged( QDockWidget::DockWidgetFeatures ) ), this, SLOT( dockWidget_featuresChanged( QDockWidget::DockWidgetFeatures ) ) );
	connect( aOrientation, SIGNAL( triggered() ), this, SLOT( aOrientation_triggered() ) );
	connect( aFloat, SIGNAL( triggered() ), this, SLOT( aFloat_triggered() ) );
	connect( aClose, SIGNAL( triggered() ), mDock, SLOT( close() ) );
}

void pDockWidgetTitleBar::paintEvent( QPaintEvent* event )
{
	Q_UNUSED( event );
	
	QStylePainter painter( this );
	
	// init style options
	QStyleOptionToolBar options;
	
	options.initFrom( mDock );
	options.rect = rect();
	QRect textRect = rect().adjusted( 3, 0, 0, 0 );
	QSize msh = minimumSizeHint();
	
	// need to rotate if vertical state
	if ( mDock->features() & QDockWidget::DockWidgetVerticalTitleBar )
	{
		painter.rotate( -90 );
		painter.translate( QPoint( -rect().height(), 0 ) );
		transposeSize( options.rect );
		transposeSize( textRect );
		msh.transpose();
	}
	
	// draw toolbar
	painter.drawControl( QStyle::CE_ToolBar, options );
	
	// draw dock title
	textRect.setWidth( qBound( 0, options.rect.width() -msh.width(), textRect.width() ) );
	const QString text = painter.fontMetrics().elidedText( mDock->windowTitle(), Qt::ElideRight, textRect.width() );
	painter.drawText( textRect, Qt::AlignLeft | Qt::AlignVCenter, text );
	
	// restore rotation
	if ( mDock->features() & QDockWidget::DockWidgetVerticalTitleBar )
	{
		painter.rotate( 90 );
	}
}

void pDockWidgetTitleBar::transposeSize( QRect& rect )
{
	QSize size = rect.size();
	size.transpose();
	rect.setSize( size );
}

void pDockWidgetTitleBar::updateStandardIcons()
{
	const QSize size( 16, 16 );
	QPixmap pixmap;
	QRect rect( QPoint(), iconSize() );
	
	QTransform transform;
	transform.rotate( 90 );
	
	pixmap = style()->standardIcon( QStyle::SP_ToolBarHorizontalExtensionButton, 0, widgetForAction( aOrientation ) ).pixmap( size );
	rect.moveCenter( pixmap.rect().center() );
	pixmap = pixmap.copy( rect );
	pixmap = pixmap.transformed( transform, Qt::SmoothTransformation );
	aOrientation->setIcon( pixmap );
	
	pixmap = style()->standardIcon( QStyle::SP_TitleBarNormalButton, 0, widgetForAction( aFloat ) ).pixmap( size );
	rect.moveCenter( pixmap.rect().center() );
	pixmap = pixmap.copy( rect );
	aFloat->setIcon( pixmap );
	
	pixmap = style()->standardIcon( QStyle::SP_TitleBarCloseButton, 0, widgetForAction( aClose ) ).pixmap( size );
	rect.moveCenter( pixmap.rect().center() );
	pixmap = pixmap.copy( rect );
	aClose->setIcon( pixmap );
}

bool pDockWidgetTitleBar::event( QEvent* event )
{
	if ( event->type() == QEvent::StyleChange ) {
		updateStandardIcons();
	}
	
	return QToolBar::event( event );
}

QSize pDockWidgetTitleBar::minimumSizeHint() const
{
	return QToolBar::sizeHint();
}

QSize pDockWidgetTitleBar::sizeHint() const
{
	QSize size = QToolBar::sizeHint();
	QFontMetrics fm( font() );

	if ( mDock->features() & QDockWidget::DockWidgetVerticalTitleBar ) {
		size.rheight() += fm.width( mDock->windowTitle() );
	}
	else {
		size.rwidth() += fm.width( mDock->windowTitle() );
	}

	return size;
}

QWidget* pDockWidgetTitleBar::addAction( QAction* action, int index )
{
	if ( index != -1 ) {
		index++;
	}
	
	if ( index >= 0 && index < actions().count() ) {
		QToolBar::insertAction( actions().value( index ), action );
	}
	else {
		QToolBar::addAction( action );
	}
	
	return widgetForAction( action );
}

void pDockWidgetTitleBar::addSeparator( int index )
{
	if ( index != -1 ) {
		index++;
	}
	
	if ( index >= 0 && index < actions().count() ) {
		QToolBar::insertSeparator( actions().value( index ) );
	}
	else {
		QToolBar::addSeparator();
	}
}

void pDockWidgetTitleBar::aOrientation_triggered()
{
	const QDockWidget::DockWidgetFeatures features = mDock->features();
	
	if ( features & QDockWidget::DockWidgetVerticalTitleBar )
	{
		mDock->setFeatures( features ^ QDockWidget::DockWidgetVerticalTitleBar );
	}
	else
	{
		mDock->setFeatures( features | QDockWidget::DockWidgetVerticalTitleBar );
	}
}

void pDockWidgetTitleBar::aFloat_triggered()
{
	mDock->setFloating( !mDock->isFloating() );
}

void pDockWidgetTitleBar::dockWidget_featuresChanged( QDockWidget::DockWidgetFeatures features )
{
	aFloat->setVisible( features & QDockWidget::DockWidgetFloatable );
	aClose->setVisible( features & QDockWidget::DockWidgetClosable );
	
	// update toolbar orientation
	if ( features & QDockWidget::DockWidgetVerticalTitleBar ) {
		if ( orientation() == Qt::Vertical ) {
			return;
		}
		
		setOrientation( Qt::Vertical );
	}
	else {
		if ( orientation() == Qt::Horizontal ) {
			return;
		}
		
		setOrientation( Qt::Horizontal );
	}
	
	// re-order the actions
	QList<QAction*> items;
	
	for ( int i = actions().count() -1; i > -1; i-- ) {
		items << actions().at( i );
	}
	
	clear();
	addActions( items );
}
