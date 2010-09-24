#include "pMultiToolBar.h"

#include <QToolBar>
#include <QVariant>

#define PMULTITOOLBAR_CONTEXT "multiToolBarContext"

pMultiToolBar::pMultiToolBar( QWidget* parent )
	: QStackedWidget( parent )
{
	setSizePolicy( QSizePolicy( QSizePolicy::Expanding, QSizePolicy::Maximum ) );
	
	connect( this, SIGNAL( currentChanged( int ) ), this, SLOT( _q_currentChanged( int ) ) );
	connect( this, SIGNAL( widgetRemoved( int ) ), this, SLOT( _q_widgetRemoved( int ) ) );
}

pMultiToolBar::~pMultiToolBar()
{
}

QString pMultiToolBar::currentContext() const
{
	QToolBar* tb = qobject_cast<QToolBar*>( currentWidget() );
	
	return tb ? tb->property( PMULTITOOLBAR_CONTEXT ).toString() : QString::null;
}

void pMultiToolBar::setCurrentContext( const QString& context )
{
	foreach ( QToolBar* tb, mToolBars )
	{
		if ( tb->property( PMULTITOOLBAR_CONTEXT ).toString() == context )
		{
			setCurrentWidget( tb );
		}
	}
}

void pMultiToolBar::removeContext( const QString& context, bool del )
{
	foreach ( QToolBar* tb, mToolBars )
	{
		if ( tb->property( PMULTITOOLBAR_CONTEXT ).toString() == context )
		{
			removeWidget( tb );
			
			if ( del )
			{
				delete tb;
			}
		}
	}
}

QStringList pMultiToolBar::contexts() const
{
	QStringList contexts;
	
	foreach ( QToolBar* tb, mToolBars )
	{
		contexts << tb->property( PMULTITOOLBAR_CONTEXT ).toString();
	}
	
	return contexts;
}

QToolBar* pMultiToolBar::toolBar( const QString& context ) const
{
	Q_ASSERT( !context.isEmpty() );
	
	foreach ( QToolBar* tb, mToolBars )
	{
		const QString tbContext = tb->property( PMULTITOOLBAR_CONTEXT ).toString();
		
		if ( tbContext == context )
		{
			return tb;
		}
	}
	
	pMultiToolBar* mtb = const_cast<pMultiToolBar*>( this );
	
	QToolBar* tb = new QToolBar( mtb );
	tb->setObjectName( QString( "pMultiToolBar_%1" ).arg( context ) );
	tb->setIconSize( QSize( 14, 14 ) );
	tb->setProperty( PMULTITOOLBAR_CONTEXT, context );
	
	int index = mtb->addWidget( tb );
	
	mToolBars[ index ] = tb;
	
	return tb;
}

QToolBar* pMultiToolBar::currentToolBar() const
{
	const QString curContext = currentContext();
	
	return curContext.isEmpty() ? 0 : toolBar( curContext );
}

void pMultiToolBar::updateMaps()
{
	mToolBars.clear();
	
	for ( int i = 0; i < count(); i++ )
	{
		QToolBar* tb = qobject_cast<QToolBar*>( widget( i ) );
		
		if ( tb )
		{
			mToolBars[ i ] = tb;
		}
	}
}

void pMultiToolBar::_q_currentChanged( int index )
{
	QToolBar* tb = mToolBars.value( index );
	
	if ( tb )
	{
		emit currentContextChanged( tb->property( PMULTITOOLBAR_CONTEXT ).toString() );
	}
	else
	{
		emit currentContextChanged( QString::null );
	}
}

void pMultiToolBar::_q_widgetRemoved( int index )
{
	QToolBar* tb = mToolBars.value( index );
	
	updateMaps();
	
	if ( tb )
	{
		emit contextRemoved( tb->property( PMULTITOOLBAR_CONTEXT ).toString() );
	}
	
	emit currentChanged( currentIndex() );
}
