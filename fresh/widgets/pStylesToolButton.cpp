#include "pStylesToolButton.h"
#include "objects/pStylesActionGroup.h"

#include <QMenu>

pStylesToolButton::pStylesToolButton( const QString& textFormat, QWidget* parent )
	: QToolButton( parent )
{
	setPopupMode( QToolButton::MenuButtonPopup );
	
	mActions = new pStylesActionGroup( textFormat, this );
	mMenu = new QMenu( this );
	
	refreshActions();
	
	connect( mActions, SIGNAL( styleSelected(const QString& ) ), this, SIGNAL( styleSelected(const QString& ) ) );
}

QStringList pStylesToolButton::availableStyles() const
{
	return mActions->availableStyles();
}

QString pStylesToolButton::systemStyle() const
{
	return mActions->systemStyle();
}

QAction* pStylesToolButton::systemAction() const
{
	return mActions->systemAction();
}

QString pStylesToolButton::applicationStyle() const
{
	return mActions->applicationStyle();
}

QAction* pStylesToolButton::applicationAction() const
{
	return mActions->applicationAction();
}

bool pStylesToolButton::isCheckableActions() const
{
	return mActions->isCheckable();
}

QString pStylesToolButton::currentStyle() const
{
	return mActions->currentStyle();
}

void pStylesToolButton::refreshActions()
{
	mActions->refreshActions();
	mMenu->addActions( mActions->actions() );
	
	setMenu( mMenu );
	setDefaultAction( mActions->systemAction() );
}

void pStylesToolButton::setCheckableActions( bool checkable )
{
	mActions->setCheckable( checkable );
}

void pStylesToolButton::setCurrentStyle( const QString& style )
{
	mActions->setCurrentStyle( style );
}
