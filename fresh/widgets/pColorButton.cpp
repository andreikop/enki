#include "pColorButton.h"

#include <QColorDialog>

pColorButton::pColorButton( QWidget* parent )
	: QPushButton( parent )
{
	init( QColor( Qt::black ) );
}

pColorButton::pColorButton( const QColor& color, QWidget* parent )
	: QPushButton( parent )
{
	init( color );
}

pColorButton::~pColorButton()
{
}

void pColorButton::init( const QColor& color )
{
	connect( this, SIGNAL( clicked() ), this, SLOT( onClicked() ) );
	
	mColorNameHidden = false;
	
	setColor( color );
}

void pColorButton::updateColorName()
{
	setToolTip( mColor.name().replace( "#", QString::number( mColor.alpha(), 16 ).prepend( "#" ) ) );
	
	if ( mColorNameHidden )
	{
		setText( QString::null );
	}
	else
	{
		setText( toolTip() );
	}
}

bool pColorButton::isColorNameHidden() const
{
	return mColorNameHidden;
}

void pColorButton::setColorNameHidden( bool hidden )
{
	mColorNameHidden = hidden;
	
	updateColorName();
}

const QColor& pColorButton::color() const
{
	return mColor;
}

void pColorButton::setColor( const QColor& color )
{
	mColor = color;
	
	QPixmap pixmap( iconSize() );
	pixmap.fill( mColor );
	
	setIcon( QIcon( pixmap ) );
	updateColorName();
}

void pColorButton::onClicked()
{
	bool ok;
	const QRgb rgb = QColorDialog::getRgba( mColor.rgba(), &ok, window() );
	
	if ( ok )
	{
		QColor color = QColor::fromRgba( rgb );
		setColor( color );
	}
}
