#include "MkSDesignerIntegration.h"

#include <QWidget>

MkSDesignerIntegration::MkSDesignerIntegration( QDesignerFormEditorInterface* core, QObject* parent )
	: qdesigner_internal::QDesignerIntegration( core, parent )
{
}

/*
	This fix the bug that resize the MkS mainwindow
	when editing geometry of toplevel form in the property editor.
*/
QWidget* MkSDesignerIntegration::containerWindow( QWidget* widget ) const
{
	// Find the parent window to apply a geometry to.
	while ( widget )
	{
		if ( widget->isWindow() )
		{
			break;
		}
		
		if ( !qstrcmp( widget->metaObject()->className(), "SharedTools::Internal::FormResizer" ) )
		{
			break;
		}
		
		widget = widget->parentWidget();
	}

	return widget;
}
