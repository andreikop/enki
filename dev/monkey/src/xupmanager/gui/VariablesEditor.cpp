#include "VariablesEditor.h"
#include "xupmanager/core/XUPProjectItem.h"
#include "xupmanager/core/XUPProjectItemHelper.h"
#include "pMonkeyStudio.h"

#include <QMenu>
#include <QInputDialog>
#include <QMessageBox>
#include <QFileDialog>

VariablesEditor::VariablesEditor( QWidget* parent )
	: QFrame( parent )
{
	mProject = 0;
	
	setupUi( this );
	
	// tbOthersValuesAdd actions
	QMenu* addMenu = new QMenu( tbOthersValuesAdd );
	aOthersValuesAddValue = addMenu->addAction( tr( "As Value..." ) );
	aOthersValuesAddFile = addMenu->addAction( tr( "As File..." ) );
	aOthersValuesAddPath = addMenu->addAction( tr( "As Path..." ) );
	tbOthersValuesAdd->setMenu( addMenu );
	
	// tbOthersValuesEdit actions
	QMenu* editMenu = new QMenu( tbOthersValuesEdit );
	aOthersValuesEditValue = editMenu->addAction( tr( "As Value..." ) );
	aOthersValuesEditFile = editMenu->addAction( tr( "As File..." ) );
	aOthersValuesEditPath = editMenu->addAction( tr( "As Path..." ) );
	tbOthersValuesEdit->setMenu( editMenu );
}

VariablesEditor::~VariablesEditor()
{
}

void VariablesEditor::init( XUPProjectItem* project )
{
	mProject = project;
	
	int pType = mProject->projectType();
	mFileVariables = mProject->projectInfos()->fileVariables( pType );
	mPathVariables = mProject->projectInfos()->pathVariables( pType );
	mManagedVariables << mFileVariables << XUPProjectItemHelper::DynamicFolderName << XUPProjectItemHelper::DynamicFolderSettingsName;
	
	// loading datas from variable of root scope having operator =, += or *= only
	foreach ( XUPItem* child, mProject->childrenList() )
	{
		if ( child->type() == XUPItem::Variable )
		{
			QString variableName = child->attribute( "name" );
			QString op = child->attribute( "operator", "=" );
			
			if ( op != "=" && op != "+=" && op != "*=" )
			{
				continue;
			}
			
			if ( variableName == XUPProjectItemHelper::DynamicFolderSettingsName ||
				variableName == XUPProjectItemHelper::DynamicFolderName )
			{
				continue;
			}
			
			foreach ( XUPItem* value, child->childrenList() )
			{
				XUPItem::Type type = value->type();
				QString val;
				
				if ( type != XUPItem::Value && type != XUPItem::File && type != XUPItem::Path )
				{
					continue;
				}
				
				val += mValues[ variableName ].trimmed();
				val += " " +value->attribute( "content" );
				mValues[ variableName ] = val.trimmed();
			}
		}
	}
	
	updateValuesEditorVariables();
}

void VariablesEditor::finalize()
{
	QListWidgetItem* curItem = lwOthersVariables->currentItem();
	on_lwOthersVariables_currentItemChanged( curItem, curItem );
	
	// tell about variables to remove
	foreach ( const QString& variable, mVariablesToRemove )
	{
		mValues[ variable ] = QString::null;
	}
	
	// update project
	foreach ( const QString& variable, mValues.keys() )
	{
		bool isEmpty = mValues[ variable ].trimmed().isEmpty();
		XUPItem* variableItem = getUniqueVariableItem( variable, !isEmpty );
		if ( !variableItem )
		{
			continue;
		}
		
		if ( !isEmpty )
		{
			if ( mFileVariables.contains( variable ) || mPathVariables.contains( variable ) )
			{
				// get child type
				XUPItem::Type type = mFileVariables.contains( variable ) ? XUPItem::File : XUPItem::Path;
				// get values
				QStringList values = mProject->splitMultiLineValue( mValues[ variable ] );
				
				// update variable
				variableItem->setAttribute( "operator", "=" );
				variableItem->setAttribute( "multiline", "true" );
				
				// remove all child
				foreach ( XUPItem* child, variableItem->childrenList() )
				{
					if ( child->type() == type )
					{
						QString value = child->attribute( "content" );
						if ( values.contains( value ) )
						{
							values.removeAll( value );
						}
						else if ( !values.contains( value ) )
						{
							variableItem->removeChild( child );
						}
					}
				}
				
				// add new ones
				foreach ( const QString& v, values )
				{
					XUPItem* value = variableItem->addChild( type );
					value->setAttribute( "content", v );
				}
			}
			else if ( variable == "CONFIG" )
			{
				// update variable
				variableItem->setAttribute( "operator", "+=" );
				variableItem->setAttribute( "multiline", "false" );
				
				// remove all child values
				foreach ( XUPItem* child, variableItem->childrenList() )
				{
					if ( child->type() == XUPItem::Value )
					{
						variableItem->removeChild( child );
					}
				}
				
				// add new one
				XUPItem* value = variableItem->addChild( XUPItem::Value );
				value->setAttribute( "content", mValues[ variable ] );
			}
			else
			{
				// update variable
				variableItem->setAttribute( "operator", "=" );
				variableItem->setAttribute( "multiline", "false" );
				
				// remove all child values
				foreach ( XUPItem* child, variableItem->childrenList() )
				{
					if ( child->type() == XUPItem::Value )
					{
						variableItem->removeChild( child );
					}
				}
				
				// add new one
				XUPItem* value = variableItem->addChild( XUPItem::Value );
				value->setAttribute( "content", mValues[ variable ] );
			}
		}
		else if ( isEmpty && variableItem && variableItem->childCount() > 0 )
		{
			// remove all child values
			foreach ( XUPItem* child, variableItem->childrenList() )
			{
				if ( child->type() == XUPItem::Value || child->type() == XUPItem::File || child->type() == XUPItem::Path )
				{
					variableItem->removeChild( child );
				}
			}
		}
		
		// remove empty variable
		if ( variableItem->childCount() == 0 )
		{
			variableItem->parent()->removeChild( variableItem );
		}
	}
}

XUPItem* VariablesEditor::getUniqueVariableItem( const QString& variableName, bool create )
{
	const QStringList mOperators = QStringList() << "=" << "+=" << "*=";
	XUPItemList variables = mProject->getVariables( mProject, variableName, 0, false );
	XUPItem* variableItem = 0;
	
	// remove duplicate variables
	foreach ( XUPItem* variable, variables )
	{
		QString op = variable->attribute( "operator", "=" );
		
		if ( !variableItem && mOperators.contains( op ) )
		{
			variableItem = variable;
		}
		else if ( mOperators.contains( op ) )
		{
			variable->parent()->removeChild( variable );
		}
	}
	
	// create it if needed
	if ( !variableItem && create )
	{
		variableItem = mProject->addChild( XUPItem::Variable );
		variableItem->setAttribute( "name", variableName );
	}
	
	// return item
	return variableItem;
}

void VariablesEditor::updateValuesEditorVariables()
{
	QListWidgetItem* curItem = lwOthersVariables->selectedItems().value( 0 );
	const QString curVariable = curItem ? curItem->text() : QString::null;
	curItem = 0;
	
	lwOthersVariables->clear();
	lwOthersValues->clear();
	
	foreach ( const QString& variable, mValues.keys() )
	{
		if ( !mManagedVariables.contains( variable ) )
		{
			lwOthersVariables->addItem( variable );
			
			if ( variable == curVariable )
			{
				curItem = lwOthersVariables->item( lwOthersVariables->count() -1 );
				curItem->setSelected( true );
			}
		}
	}
}

void VariablesEditor::updateValuesEditorValues( const QString& variable )
{
	const QStringList values = XUPProjectItem::splitMultiLineValue( mValues[ variable ] );
	
	lwOthersValues->clear();
	lwOthersValues->addItems( values );
}

void VariablesEditor::on_lwOthersVariables_currentItemChanged( QListWidgetItem* current, QListWidgetItem* previous )
{
	// enable/disable actions
	gbOthersValues->setEnabled( current );
	tbOthersVariablesEdit->setEnabled( current );
	tbOthersVariablesRemove->setEnabled( current );
	
	// save previous variable datas
	if ( previous )
	{
		const QString variable = previous->text();
		QStringList values;
		
		for ( int i = 0; i < lwOthersValues->count(); i++ )
		{
			values << lwOthersValues->item( i )->text();
		}
		
		mValues[ variable ] = values.join( " " );;
	}
	
	// update values view
	const QString variable = current ? current->text() : QString::null;
	updateValuesEditorValues( variable );
}

void VariablesEditor::on_tbOthersVariablesAdd_clicked()
{
	bool ok;
	const QStringList variables = mProject->projectInfos()->knowVariables( mProject->projectType() );
	const QString variable = QInputDialog::getItem( window(), tr( "Add variable..." ), tr( "Select a variable name or enter a new one" ), variables, 0, true, &ok );
	
	if ( !variable.isEmpty() && ok )
	{
		if ( !mValues.keys().contains( variable ) && !mManagedVariables.contains( variable ) )
		{
			QListWidgetItem* item = new QListWidgetItem( variable, lwOthersVariables );
			lwOthersVariables->setCurrentItem( item );
			
			mValues[ variable ] = QString::null;
			mVariablesToRemove.removeAll( variable );
		}
		else
		{
			QMessageBox::information( window(), tr( "Information..." ), tr( "This variable already exists or is filtered out." ) );
		}
	}
}

void VariablesEditor::on_tbOthersVariablesEdit_clicked()
{
	QListWidgetItem* item = lwOthersVariables->currentItem();
	
	if ( !item )
	{
		return;
	}
	
	bool ok;
	QString oldVariable = item->text();
	QString variable = QInputDialog::getText( window(), tr( "Edit variable..." ), tr( "Enter a new name for this variable" ), QLineEdit::Normal, oldVariable, &ok );
	
	if ( !variable.isEmpty() && ok )
	{
		if ( !mValues.keys().contains( variable ) && !mManagedVariables.contains( variable ) )
		{
			item->setText( variable );
			
			mValues.remove( oldVariable );
			if ( !mVariablesToRemove.contains( oldVariable ) )
			{
				mVariablesToRemove << oldVariable;
			}
		}
		else
		{
			QMessageBox::information( QApplication::activeWindow(), tr( "Information..." ), tr( "This variable already exists or is filtered out." ) );
		}
	}
}

void VariablesEditor::on_tbOthersVariablesRemove_clicked()
{
	QListWidgetItem* item = lwOthersVariables->currentItem();
	
	if ( !item )
	{
		return;
	}
	
	// confirm user request
	if ( QMessageBox::question( QApplication::activeWindow(), tr( "Remove a variable..." ), tr( "A you sure you want to remove this variable and all its content ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::Yes )
	{
		QString variable = item->text();
		
		lwOthersValues->clear();
		delete item;
		
		mValues.remove( variable );
		if ( !mVariablesToRemove.contains( variable ) )
		{
			mVariablesToRemove << variable;
		}
	}
}

void VariablesEditor::on_lwOthersValues_currentItemChanged( QListWidgetItem* current, QListWidgetItem* previous )
{
	// enable button according to item validity
	tbOthersValuesEdit->setEnabled( current );
	tbOthersValuesRemove->setEnabled( current );
	Q_UNUSED( previous );
}

void VariablesEditor::on_tbOthersValuesAdd_clicked()
{
	on_tbOthersValuesAdd_triggered( aOthersValuesAddValue );
}

void VariablesEditor::on_tbOthersValuesAdd_triggered( QAction* action )
{
	QListWidgetItem* variableItem = lwOthersVariables->currentItem();
	
	if ( variableItem )
	{
		const QString title = tr( "Add a value..." );
		bool ok = true;
		QString val;
		
		if ( action == aOthersValuesAddValue )
		{
			val	= QInputDialog::getText( window(), title, tr( "Enter the value :" ), QLineEdit::Normal, QString(), &ok );
			if ( !ok )
			{
				val.clear();
			}
		}
		else if ( action == aOthersValuesAddFile )
		{
			val = QFileDialog::getOpenFileName( window(), tr( "Choose a file" ), mProject->path() );
			if ( !val.isEmpty() )
			{
				val = mProject->relativeFilePath( val );
			}
		}
		else if ( action == aOthersValuesAddPath )
		{
			val = QFileDialog::getExistingDirectory( window(), tr( "Choose a path" ), mProject->path() );
			if ( !val.isEmpty() )
			{
				val = mProject->relativeFilePath( val );
			}
		}
		
		if ( !val.isEmpty() )
		{
			// quote value if needed
			if ( val.contains( " " ) && !val.startsWith( '"' ) && !val.endsWith( '"' ) )
			{
				val.prepend( '"' ).append( '"' );
			}
			
			// check if value exists
			for ( int i = 0; i < lwOthersValues->count(); i++ )
			{
				QListWidgetItem* valueItem = lwOthersValues->item( i );
				
				if ( valueItem->text() == val )
				{
					lwOthersValues->setCurrentItem( valueItem );
					return;
				}
			}
			
			// create value item
			QListWidgetItem* valueItem = new QListWidgetItem( val, lwOthersValues );
			lwOthersValues->setCurrentItem( valueItem );
		}
	}
}

void VariablesEditor::on_tbOthersValuesEdit_clicked()
{
	on_tbOthersValuesEdit_triggered( aOthersValuesEditValue );
}

void VariablesEditor::on_tbOthersValuesEdit_triggered( QAction* action )
{
	QListWidgetItem* valueItem = lwOthersValues->currentItem();
	
	if ( valueItem )
	{
		const QString title = tr( "Edit a value..." );
		bool ok = true;
		QString oldValue = valueItem->text();
		QString val;
		
		if ( action == aOthersValuesEditValue )
		{
			val	= QInputDialog::getText( window(), title, tr( "Edit the value :" ), QLineEdit::Normal, oldValue, &ok );
			if ( !ok )
			{
				val.clear();
			}
		}
		else if ( action == aOthersValuesEditFile )
		{
			val = QFileDialog::getOpenFileName( window(), tr( "Choose a file" ), oldValue );
			if ( !val.isEmpty() )
			{
				val = mProject->relativeFilePath( val );
			}
		}
		else if ( action == aOthersValuesEditPath )
		{
			val = QFileDialog::getExistingDirectory( window(), tr( "Choose a path" ), oldValue );
			if ( !val.isEmpty() )
			{
				val = mProject->relativeFilePath( val );
			}
		}
		
		if ( !val.isEmpty() )
		{
			// quote value if needed
			if ( val.contains( " " ) && !val.startsWith( '"' ) && !val.endsWith( '"' ) )
			{
				val.prepend( '"' ).append( '"' );
			}
			
			// check if value exists
			for ( int i = 0; i < lwOthersValues->count(); i++ )
			{
				QListWidgetItem* item = lwOthersValues->item( i );
				
				if ( item->text() == val )
				{
					lwOthersValues->setCurrentItem( item );
					return;
				}
			}
			
			// update item
			valueItem->setText( val );
		}
	}
}

void VariablesEditor::on_tbOthersValuesRemove_clicked()
{
	QListWidgetItem* valueItem = lwOthersValues->currentItem();
	
	if ( valueItem )
	{
		// confirm user request
		if ( QMessageBox::question( QApplication::activeWindow(), tr( "Remove a value..." ), tr( "A you sure you want to remove this value ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::No )
		{
			return;
		}
		
		// remove value
		delete valueItem;
	}
}

void VariablesEditor::on_tbOthersValuesClear_clicked()
{
	QListWidgetItem* variableItem = lwOthersVariables->currentItem();
	
	if ( variableItem )
	{
		// request user confirm
		if ( QMessageBox::question( QApplication::activeWindow(), tr( "Clear values..." ), tr( "A you sure you want to clear these values ?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::No ) == QMessageBox::Yes )
		{
			lwOthersValues->clear();
		}
	}
}
