#include "pEnvironmentVariableEditor.h"

pEnvironmentVariableEditor::pEnvironmentVariableEditor( QWidget* parent, const QString& name, const QString& value )
	: QDialog( parent )
{
	setupUi( this );
	leName->setReadOnly( !name.isEmpty() );
	leName->setText( name );
	leValue->setText( value );

	if ( name.isEmpty() )
	{
		leName->setFocus();
	}
	else
	{
		leValue->setFocus();
	}
}

QString pEnvironmentVariableEditor::name() const
{
	return leName->text();
}

QString pEnvironmentVariableEditor::value() const
{
	return leValue->text();
}
