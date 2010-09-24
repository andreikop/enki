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
#include "pTreeComboBox.h"

#include <QVBoxLayout>
#include <QTreeView>
#include <QAbstractItemModel>
#include <QComboBox>
#include <QHeaderView>
#include <QStyleOptionComboBox>
#include <QStylePainter>
#include <QMouseEvent>
#include <QApplication>
#include <QDesktopWidget>
#include <QStatusBar>

int recursiveCount( const QModelIndex& it )
{
	int j = 0;
	if ( !it.parent().isValid() )
		j++;
	for ( int i = 0; i < it.model()->rowCount( it ); i++ )
	{
		j++;
		if ( it.model()->rowCount( it.child( i, 0 ) ) )
			j += recursiveCount( it.child( i, 0 ) );
	}
	return j;
}

/*!
	\details Create a new pTreeComboBox object
	\param parent The parent widget
*/
pTreeComboBox::pTreeComboBox( QWidget* parent )
	: QWidget( parent ), mFrame( new QFrame( this ) ), mView( 0 ), mModel( 0 ), mForce( false )
{
	mFrame->setWindowFlags( Qt::Dialog | Qt::FramelessWindowHint );
	QVBoxLayout* vl = new QVBoxLayout( mFrame );
	vl->setSpacing( 0 );
	vl->setMargin( 3 );
	
	mIconSize = QSize( 16, 16 );
	mSizeHint = QComboBox().sizeHint();
	setSizePolicy( QSizePolicy( QSizePolicy::Preferred, QSizePolicy::Fixed ) );
	setView( new QTreeView );
	mView->header()->hide();
	mView->resize( mView->viewport()->size() );
	mFrame->installEventFilter( this );
}

pTreeComboBox::~pTreeComboBox()
{ delete mView; }

bool pTreeComboBox::eventFilter( QObject* object, QEvent* event )
{
	if ( object == mFrame )
	{
		if ( event->type() == QEvent::WindowDeactivate )
			if ( !rect().contains( mapFromGlobal( QCursor::pos() ) ) )
				hidePopup();
		return QWidget::eventFilter( object, event );
	}

	QEvent::Type t = event->type();
	if ( t == QEvent::Hide )
	{
		if ( currentIndex() != mIndex )
		{
			mForce = false;
			mView->clearSelection();
			mView->setCurrentIndex( mIndex );
			mForce = true;
		}
		update();
	}
	else if ( t == QEvent::MouseMove )
	{
		if ( QMouseEvent* me = static_cast<QMouseEvent*>( event ) )
		{
			QModelIndex i = mView->indexAt( mView->mapFromGlobal( me->globalPos() ) );
			if ( mView->currentIndex() != i )
			{
				emit highlighted( i );
				mForce = false;
				mView->clearSelection();
				mView->setCurrentIndex( i );
				mForce = true;
			}
		}
	}
	return QWidget::eventFilter( object, event );
}

/*!
	\details Return the widget size hint
*/
QSize pTreeComboBox::sizeHint() const
{ return mSizeHint; }

/*!
	\details Return the number of row in the model
*/
int pTreeComboBox::count() const
{ return recursiveCount( mModel->index( 0, 0 ) ); }

/*!
	\details Return the iconSize
*/
QSize pTreeComboBox::iconSize() const
{ return mIconSize; }

/*!
	\details Set the icon size
*/
void pTreeComboBox::setIconSize( const QSize& s )
{
	if ( mIconSize != s )
	{
		mIconSize = s;
		update();
	}
}

void pTreeComboBox::paintEvent( QPaintEvent* /*event*/ )
{
	QStyleOptionComboBox o;

	// QStyleOption
	o.initFrom( this );
	
	// QStyleOptionComplex
	o.activeSubControls = 0;
	o.subControls = QStyle::SC_ComboBoxEditField | QStyle::SC_ComboBoxArrow | QStyle::SC_ComboBoxFrame;

	// QStyleOptionComboBox
	QModelIndex i = currentIndex();
	o.currentIcon = i.data( Qt::DecorationRole ).value<QIcon>();
	o.iconSize = mView && mView->iconSize() != QSize( -1, -1 ) ? mView->iconSize() : iconSize();
	o.currentText = i.data( Qt::DisplayRole ).toString();
	o.editable = false;
	o.frame = true;
	o.popupRect = QRect();
	
	if ( !mFrame->isVisible() && rect().contains( mapFromGlobal( QCursor::pos() ) ) )
		o.state |= QStyle::State_MouseOver;
	
	if ( mFrame->isVisible() )
		o.state |= QStyle::State_On;
	
	QStylePainter p( this );
	p.drawComplexControl( QStyle::CC_ComboBox, o );
	p.drawControl( QStyle::CE_ComboBoxLabel, o );
}

void pTreeComboBox::hideEvent( QHideEvent* /*event*/ )
{ hidePopup(); }

void pTreeComboBox::enterEvent( QEvent* /*event*/ )
{ update(); }

void pTreeComboBox::leaveEvent( QEvent* /*event*/ )
{ update(); }

void pTreeComboBox::mousePressEvent( QMouseEvent* /*event*/ )
{
	if ( !mView )
		return;
	mFrame->isVisible() ? hidePopup() : showPopup();
}

/*!
	\details Hide the popup
*/
void pTreeComboBox::hidePopup()
{
	if ( mFrame->isVisible() )
		mFrame->hide();
}

void pTreeComboBox::calculPopupGeometry()
// code copied from QComboBox  original class from Trolltech, arrange to feet my needs
{
	//int itemHeight = mView->sizeHintForIndex( mModel->index( 0, 0 ) ).height();
	QRect listRect( rect() );
	//listRect.setHeight(itemHeight * count() +( 2 *mFrame->layout()->spacing() ) +( 2 *mFrame->frameWidth() ) );
	QRect screen = QApplication::desktop()->screenGeometry(this);
	QPoint below = mapToGlobal(listRect.bottomLeft());
	int belowHeight = screen.bottom() - below.y();
	QPoint above = mapToGlobal(listRect.topLeft());
	int aboveHeight = above.y() - screen.y();
	
	// make sure the widget fits on screen
		if (listRect.width() > screen.width() )
		listRect.setWidth(screen.width());
	if (mapToGlobal(listRect.bottomRight()).x() > screen.right()) {
		below.setX(screen.x() + screen.width() - listRect.width());
		above.setX(screen.x() + screen.width() - listRect.width());
	}
	if (mapToGlobal(listRect.topLeft()).x() < screen.x() ) {
		below.setX(screen.x());
		above.setX(screen.x());
	}
		
	if (listRect.height() <= belowHeight) {
		listRect.moveTopLeft(below);
	} else if (listRect.height() <= aboveHeight) {
		listRect.moveBottomLeft(above);
	} else if (belowHeight >= aboveHeight) {
		listRect.setHeight(belowHeight);
		listRect.moveTopLeft(below);
	} else {
		listRect.setHeight(aboveHeight);
		listRect.moveBottomLeft(above);
	}

	mFrame->setGeometry( listRect );
}

/*!
	\details Show the popup
*/
void pTreeComboBox::showPopup()
{
	if ( !mFrame->isVisible() && mView )
	{
		mIndex = currentIndex();
		calculPopupGeometry();
		mFrame->show();
		update();
	}
}

/*!
	\details Return the view widget
*/
QTreeView* pTreeComboBox::view() const
{ return mView; }

/*!
	\details Set the view widget
*/
void pTreeComboBox::setView( QTreeView* view )
{
	if ( mView == view )
		return;
	delete mView;
	mView = view;
	if ( mView )
	{
		if ( mFrame->layout()->count() )
			qobject_cast<QVBoxLayout*>( mFrame->layout() )->insertWidget( 0, mView );
		else
		{
			mFrame->layout()->addWidget( mView );
			QStatusBar* sb = new QStatusBar( mFrame );
			sb->setFixedHeight( 16 );
			mFrame->layout()->addWidget( sb );
		}
		mView->setEditTriggers( QAbstractItemView::NoEditTriggers );
		mView->setMouseTracking( true );
		mView->viewport()->installEventFilter( this );
		setModel( mModel );
		connect( mView, SIGNAL( activated( const QModelIndex& ) ), this, SLOT( internal_activated( const QModelIndex& ) ) );
		connect( mView, SIGNAL( clicked( const QModelIndex& ) ), this, SLOT( internal_clicked( const QModelIndex& ) ) );
	}
}

/*!
	\details Return the used model
*/
QAbstractItemModel* pTreeComboBox::model() const
{ return mModel; }

/*!
	\details Set the model
*/
void pTreeComboBox::setModel( QAbstractItemModel* model )
{
	if ( mModel != model )
		mModel = model;
	if ( mView && mView->model() != mModel )
	{
		mView->setModel( mModel );
		connect( mView->selectionModel(), SIGNAL( currentChanged( const QModelIndex&, const QModelIndex& ) ), this, SLOT( internal_currentChanged( const QModelIndex&, const QModelIndex& ) ) );
	}
}

/*!
	\details Return the root index
*/
QModelIndex pTreeComboBox::rootIndex() const
{ return mView ? mView->rootIndex() : QModelIndex(); }

/*!
	\details Set the root index
*/
void pTreeComboBox::setRootIndex( const QModelIndex& index )
{ if ( mView ) mView->setRootIndex( index ); }

/*!
	\details Return the current index
*/
QModelIndex pTreeComboBox::currentIndex() const
{
	if ( mView )
		return mFrame->isVisible() ? mIndex : mView->currentIndex();
	return QModelIndex();
}

/*!
	\details Set the current index
*/
void pTreeComboBox::setCurrentIndex( const QModelIndex& index )
{
	if ( mView && ( currentIndex() != index || !index.isValid() ) )
	{
		mIndex = index;
		mForce = true;
		mView->clearSelection();
		mView->setCurrentIndex( index );
		mForce = false;
		update();
	}
}

/*!
	\details Expand all rows
*/
void pTreeComboBox::expandAll()
{ if ( mView ) mView->expandAll(); }

void pTreeComboBox::internal_activated( const QModelIndex& index )
{
	if ( !( index.flags() & Qt::ItemIsEnabled ) || !( index.flags() & Qt::ItemIsSelectable ) )
	{
		return;
	}
	
	if ( mIndex != index )
	{
		mIndex = index;
		emit currentChanged( index );
	}
	emit activated( index );
	hidePopup();
}

void pTreeComboBox::internal_clicked( const QModelIndex& index )
{
	if ( !( index.flags() & Qt::ItemIsEnabled ) || !( index.flags() & Qt::ItemIsSelectable ) )
	{
		return;
	}
	
	if ( mIndex != index )
	{
		mIndex = index;
		emit currentChanged( index );
	}
	emit clicked( index );
	hidePopup();
}

void pTreeComboBox::internal_currentChanged( const QModelIndex& current, const QModelIndex& )
{
	if ( mForce )
		emit currentChanged( current );
}
