#include "pEnvironmentVariablesEditor.h"
#include "pEnvironmentVariableEditor.h"

#include <QProcess>
#include <QMessageBox>
#include <QDebug>

pEnvironmentVariablesEditor::pEnvironmentVariablesEditor( QWidget* parent )
	: QWidget( parent )
{
	setupUi( this );
	verticalLayout->setMenuBar( tbActions );

	mModel = new pEnvironmentVariablesModel( this );
	tvVariables->setModel( mModel );
	tvVariables->header()->setResizeMode( 0, QHeaderView::ResizeToContents );

	model_view_changed();

	connect( mModel, SIGNAL( defaultVariablesChanged() ), this, SLOT( model_view_changed() ) );
	connect( mModel, SIGNAL( rowsInserted( const QModelIndex&, int, int ) ), this, SLOT( model_view_changed() ) );
	connect( mModel, SIGNAL( rowsRemoved( const QModelIndex&, int, int ) ), this, SLOT( model_view_changed() ) );
	connect( mModel, SIGNAL( layoutChanged() ), this, SLOT( model_view_changed() ) );
	connect( tvVariables->selectionModel(), SIGNAL( selectionChanged( const QItemSelection&, const QItemSelection& ) ), this, SLOT( model_view_changed() ) );
}

pEnvironmentVariablesModel::Variables pEnvironmentVariablesEditor::variables() const
{
	return mModel->variables();
}

pEnvironmentVariablesModel::Variables pEnvironmentVariablesEditor::defaultVariables() const
{
	return mModel->defaultVariables();
}

QStringList pEnvironmentVariablesEditor::variables( bool keepDisabled ) const
{
	return mModel->variables( keepDisabled );
}

pEnvironmentVariablesModel::Variable pEnvironmentVariablesEditor::variable( const QString& name ) const
{
	return mModel->variable( name );
}

bool pEnvironmentVariablesEditor::contains( const QString& name ) const
{
	return mModel->contains( name );
}

bool pEnvironmentVariablesEditor::isEmpty() const
{
	return mModel->isEmpty();
}

void pEnvironmentVariablesEditor::setVariables( const pEnvironmentVariablesModel::Variables& variables, bool setDefault )
{
	mModel->setVariables( variables, setDefault );
}

void pEnvironmentVariablesEditor::setDefaultVariables( const pEnvironmentVariablesModel::Variables& variables )
{
	mModel->setDefaultVariables( variables );
}

void pEnvironmentVariablesEditor::setVariables( const QStringList& variables, bool setDefault )
{
	mModel->setVariables( variables, setDefault );
}

void pEnvironmentVariablesEditor::setVariable( const QString& name, const pEnvironmentVariablesModel::Variable& variable )
{
	mModel->setVariable( name, variable );
}

void pEnvironmentVariablesEditor::removeVariable( const QString& name )
{
	mModel->removeVariable( name );
}

void pEnvironmentVariablesEditor::clearVariables()
{
	mModel->clearVariables();
}

void pEnvironmentVariablesEditor::resetVariablesToDefault()
{
	mModel->resetVariablesToDefault();
}

void pEnvironmentVariablesEditor::resetVariablesToSystem( bool setDefault )
{
	mModel->resetVariablesToSystem( setDefault );
}

void pEnvironmentVariablesEditor::model_view_changed()
{
	const bool hasSelection = tvVariables->selectionModel()->hasSelection();

	aEdit->setEnabled( hasSelection );
	aRemove->setEnabled( hasSelection );
	aClear->setEnabled( mModel->hasChildren() );
	aResetDefault->setEnabled( !mModel->defaultVariables().isEmpty() );
}

void pEnvironmentVariablesEditor::on_aAdd_triggered()
{
	pEnvironmentVariableEditor dlg( this );
	dlg.setWindowTitle( tr( "Add a new variable..." ) );

	if ( dlg.exec() == QDialog::Rejected )
	{
		return;
	}

	if ( dlg.name().isEmpty() )
	{
		return;
	}

	pEnvironmentVariablesModel::Variable variable;

	if ( mModel->contains( dlg.name() ) )
	{
		const QMessageBox::StandardButton result = QMessageBox::question( this, QString::null, tr( "The variable '%1' already exists, update it?" ).arg( dlg.name() ), QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes );

		if ( result == QMessageBox::Yes )
		{
			variable = mModel->variable( dlg.name() );
		}
		else
		{
			return;
		}
	}

	variable.name = dlg.name();
	variable.value = dlg.value();
	mModel->setVariable( dlg.name(), variable );

	const QModelIndex index = mModel->index( dlg.name() );
	tvVariables->setCurrentIndex( index );
}

void pEnvironmentVariablesEditor::on_aEdit_triggered()
{
	const QModelIndex index = tvVariables->selectionModel()->selectedIndexes().value( 0 );
	pEnvironmentVariablesModel::Variable variable = mModel->variable( index );

	pEnvironmentVariableEditor dlg( this, variable.name, variable.value );
	dlg.setWindowTitle( tr( "Edit a variable..." ) );

	if ( dlg.exec() == QDialog::Rejected )
	{
		return;
	}

	variable.value = dlg.value();
	mModel->setVariable( dlg.name(), variable );
}

void pEnvironmentVariablesEditor::on_aRemove_triggered()
{
	const QModelIndex index = tvVariables->selectionModel()->selectedIndexes().value( 0 );
	const pEnvironmentVariablesModel::Variable variable = mModel->variable( index );

	const QMessageBox::StandardButton result = QMessageBox::question( this, QString::null, tr( "Are you sure you want to remove the variable '%1' ?" ).arg( variable.name ), QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes );

	if ( result == QMessageBox::No )
	{
		return;
	}

	mModel->removeVariable( variable.name );
}

void pEnvironmentVariablesEditor::on_aClear_triggered()
{
	const QMessageBox::StandardButton result = QMessageBox::question( this, QString::null, tr( "Are you sure you want to clear all variables?" ), QMessageBox::Yes | QMessageBox::No, QMessageBox::Yes );

	if ( result == QMessageBox::No )
	{
		return;
	}

	mModel->clearVariables();
}

void pEnvironmentVariablesEditor::on_aResetDefault_triggered()
{
	mModel->resetVariablesToDefault();
}

void pEnvironmentVariablesEditor::on_aResetSystem_triggered()
{
	mModel->resetVariablesToSystem( false );
}

void pEnvironmentVariablesEditor::on_tvVariables_activated( const QModelIndex& index )
{
	if ( index.column() == 1 )
	{
		on_aEdit_triggered();
	}
}
