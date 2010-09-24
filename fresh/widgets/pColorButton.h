#ifndef PCOLORBUTTON_H
#define PCOLORBUTTON_H

#include "objects/MonkeyExport.h"

#include <QPushButton>

class Q_MONKEY_EXPORT pColorButton : public QPushButton
{
	Q_OBJECT
	Q_PROPERTY( bool colorNameHidden READ isColorNameHidden WRITE setColorNameHidden )
	Q_PROPERTY( QColor color READ color WRITE setColor )
	
public:
	pColorButton( QWidget* parent = 0 );
	pColorButton( const QColor& color, QWidget* parent = 0 );
	virtual ~pColorButton();
	
	bool isColorNameHidden() const;
	const QColor& color() const;

protected:
	bool mColorNameHidden;
	QColor mColor;
	
	void init( const QColor& color );
	void updateColorName();

public slots:
	void setColorNameHidden( bool hidden );
	void setColor( const QColor& color );

protected slots:
	void onClicked();
};

#endif // PCOLORBUTTON_H
