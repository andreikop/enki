#include "UISettingsQMake.h"
#include "QMake.h"
#include "QtVersionManager.h"

#include <pMonkeyStudio.h>

#include <QPushButton>
#include <QDir>
#include <QWhatsThis>
#include <QFileSystemModel>
#include <QDirModel>
#include <QCompleter>
#include <QMessageBox>
#include <QDebug>

UISettingsQMake::UISettingsQMake( QWidget* parent )
	: QWidget( parent )
{
	// set up dialog
	setupUi( this );
	
	mQtManager = QMake::versionManager();
	
	// completer of paths
#ifdef Q_CC_GNU
	#warning *** USING QDirModel is deprecated but QCompleter does not handle QFileSystemModel... please fix me when possible.
#endif
	QCompleter* completer = new QCompleter( leQtVersionPath );
	QDirModel* model = new QDirModel( completer );
	
	model->setFilter( QDir::AllDirs | QDir::NoDotAndDotDot | QDir::Hidden | QDir::Readable );
	completer->setModel( model );
	leQtVersionPath->setCompleter( completer );
	
	lwPages->setCurrentRow( 0 );
	dbbButtons->button( QDialogButtonBox::Help )->setIcon( QIcon( ":/help/icons/help/keyword.png" ) );
	dbbButtons->button( QDialogButtonBox::Save )->setIcon( QIcon( ":/file/icons/file/save.png" ) );
	
	// load settings
	loadSettings();
	
	// connections
	connect( lwQtVersions, SIGNAL( currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ), this, SLOT( lw_currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ) );
	connect( lwQtModules, SIGNAL( currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ), this, SLOT( lw_currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ) );
	connect( lwQtConfigurations, SIGNAL( currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ), this, SLOT( lw_currentItemChanged( QListWidgetItem*, QListWidgetItem* ) ) );
	foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbAdd*" ) ) )
		connect( tb, SIGNAL( clicked() ), this, SLOT( tbAdd_clicked() ) );
	foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbRemove*" ) ) )
		connect( tb, SIGNAL( clicked() ), this, SLOT( tbRemove_clicked() ) );
	foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbClear*" ) ) )
		connect( tb, SIGNAL( clicked() ), this, SLOT( tbClear_clicked() ) );
	foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbUp*" ) ) )
		connect( tb, SIGNAL( clicked() ), this, SLOT( tbUp_clicked() ) );
	foreach ( QToolButton* tb, findChildren<QToolButton*>( QRegExp( "tbDown*" ) ) )
		connect( tb, SIGNAL( clicked() ), this, SLOT( tbDown_clicked() ) );
	connect( leQtVersionVersion, SIGNAL( editingFinished() ), this, SLOT( qtVersionChanged() ) );
	connect( leQtVersionVersion, SIGNAL( textChanged( const QString& ) ), this, SLOT( qtVersionChanged() ) );
	connect( leQtVersionPath, SIGNAL( editingFinished() ), this, SLOT( qtVersionChanged() ) );
	connect( cbQtVersionQMakeSpec->lineEdit(), SIGNAL( editingFinished() ), this, SLOT( qtVersionChanged() ) );
	connect( leQtVersionQMakeParameters, SIGNAL( editingFinished() ), this, SLOT( qtVersionChanged() ) );
	connect( cbQtVersionHasSuffix, SIGNAL( toggled( bool ) ), this, SLOT( qtVersionChanged() ) );
}

void UISettingsQMake::tbAdd_clicked()
{
	QListWidget* lw = 0;
	if ( sender() == tbAddQtVersion )
		lw = lwQtVersions;
	else if ( sender() == tbAddQtModule )
		lw = lwQtModules;
	else if ( sender() == tbAddQtConfiguration )
		lw = lwQtConfigurations;
	if ( lw )
	{
		lw->addItem( tr( "New value" ) );
		lw->setCurrentItem( lw->item( lw->count() -1 ) );
		lw->scrollToItem( lw->item( lw->count() -1 ) );
		lw->currentItem()->setFlags( lw->currentItem()->flags() | Qt::ItemIsEditable );
	}
}

void UISettingsQMake::tbRemove_clicked()
{
	if ( sender() == tbRemoveQtVersion )
		delete lwQtVersions->selectedItems().value( 0 );
	else if ( sender() == tbRemoveQtModule )
		delete lwQtModules->selectedItems().value( 0 );
	else if ( sender() == tbRemoveQtConfiguration )
		delete lwQtConfigurations->selectedItems().value( 0 );
}

void UISettingsQMake::tbClear_clicked()
{
	if ( sender() == tbClearQtVersions )
		lwQtVersions->clear();
	else if ( sender() == tbClearQtModules )
		lwQtModules->clear();
	else if ( sender() == tbClearQtConfiguration )
		lwQtConfigurations->clear();
}

void UISettingsQMake::tbUp_clicked()
{
	QToolButton* tb = qobject_cast<QToolButton*>( sender() );
	if ( !tb )
		return;
	QListWidget* lw = 0;
	if ( tb == tbUpQtVersion )
		lw = lwQtVersions;
	else if ( tb == tbUpQtModule )
		lw = lwQtModules;
	else if ( tb == tbUpQtConfiguration )
		lw = lwQtConfigurations;
	if ( !lw )
		return;
	if ( QListWidgetItem* it = lw->selectedItems().value( 0 ) )
	{
		int i = lw->row( it );
		if ( i != 0 )
			lw->insertItem( i -1, lw->takeItem( i ) );
		lw->setCurrentItem( it );
	}
}

void UISettingsQMake::tbDown_clicked()
{
	QToolButton* tb = qobject_cast<QToolButton*>( sender() );
	if ( !tb )
		return;
	QListWidget* lw = 0;
	if ( tb == tbDownQtVersion )
		lw = lwQtVersions;
	else if ( tb == tbDownQtModule )
		lw = lwQtModules;
	else if ( tb == tbDownQtConfiguration )
		lw = lwQtConfigurations;
	if ( !lw )
		return;
	if ( QListWidgetItem* it = lw->selectedItems().value( 0 ) )
	{
		int i = lw->row( it );
		if ( i != lw->count() -1 )
			lw->insertItem( i +1, lw->takeItem( i ) );
		lw->setCurrentItem( it );
	}
}

void UISettingsQMake::on_tbDefaultQtVersion_clicked()
{
	if ( QListWidgetItem* it = lwQtVersions->selectedItems().value( 0 ) )
	{
		for ( int i = 0; i < lwQtVersions->count(); i++ )
		{
			QListWidgetItem* cit = lwQtVersions->item( i );
			QtVersion v = cit->data( Qt::UserRole ).value<QtVersion>();
			v.Default = it == cit;
			cit->setData( Qt::UserRole, QVariant::fromValue( v ) );
			cit->setBackground( QBrush( v.Default ? Qt::green : Qt::transparent ) );
		}
	}
}

void UISettingsQMake::qtVersionChanged()
{ lw_currentItemChanged( lwQtVersions->currentItem(), lwQtVersions->currentItem() ); }

void UISettingsQMake::on_tbQtVersionPath_clicked()
{
	const QString s = pMonkeyStudio::getExistingDirectory( tr( "Locate your qt installation directory" ), leQtVersionPath->text(), window() );
	if ( !s.isNull() )
	{
		leQtVersionPath->setText( s );
		qtVersionChanged();
	}
}

void UISettingsQMake::on_tbQtVersionQMakeSpec_clicked()
{
	const QString s = pMonkeyStudio::getExistingDirectory( tr( "Locate the mk spec folder to use" ), leQtVersionPath->text(), window() );
	if ( !s.isNull() )
	{
		if ( cbQtVersionQMakeSpec->findText( s ) == -1 )
			cbQtVersionQMakeSpec->addItem( s );
		cbQtVersionQMakeSpec->setCurrentIndex( cbQtVersionQMakeSpec->findText( s ) );
		qtVersionChanged();
	}
}

void UISettingsQMake::lw_currentItemChanged( QListWidgetItem* c, QListWidgetItem* p )
{
	if ( c != p )
	{
		foreach ( QWidget* widget, findChildren<QWidget*>() )
		{
			widget->blockSignals( true );
		}
	}
	
	if ( p )
	{
		if ( p->listWidget() == lwQtVersions )
		{
			QtVersion v = p->data( Qt::UserRole ).value<QtVersion>();
			v.Version = leQtVersionVersion->text();
			v.Path = leQtVersionPath->text();
			v.QMakeSpec = cbQtVersionQMakeSpec->currentText();
			v.QMakeParameters = leQtVersionQMakeParameters->text();
			v.HasQt4Suffix = cbQtVersionHasSuffix->isChecked();
			p->setData( Qt::UserRole, QVariant::fromValue( v ) );
			p->setText( v.Version );
		}
		else if ( p->listWidget() == lwQtModules )
		{
			QtItem it = p->data( Qt::UserRole ).value<QtItem>();
			it.Text = leCaptionQtModule->text();
			it.Value = leValueQtModule->text();
			if ( it.Variable.isEmpty() )
				it.Variable = "QT";
			it.Help = pteHelpQtModule->toPlainText();
			p->setData( Qt::UserRole, QVariant::fromValue( it ) );
			p->setText( it.Text );
		}
		else if ( p->listWidget() == lwQtConfigurations )
		{
			QtItem it = p->data( Qt::UserRole ).value<QtItem>();
			it.Text = leCaptionQtConfiguration->text();
			it.Value = leValueQtConfiguration->text();
			if ( it.Variable.isEmpty() )
				it.Variable = "CONFIG";
			it.Help = pteHelpQtConfiguration->toPlainText();
			p->setData( Qt::UserRole, QVariant::fromValue( it ) );
			p->setText( it.Text );
		}
	}
	if ( c )
	{
		if ( c->listWidget() == lwQtVersions )
		{
			QtVersion v = c->data( Qt::UserRole ).value<QtVersion>();
			leQtVersionVersion->setText( v.Version );
			leQtVersionPath->setText( v.Path );
			// need to get all mkspecs for this qt versions
			cbQtVersionQMakeSpec->clear();
			QDir mkspecs( QString( v.Path ).append( "/mkspecs" ) );
			if ( mkspecs.exists() )
			{
				foreach ( const QFileInfo& fi, mkspecs.entryInfoList( QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name ) )
				{
					if ( fi.fileName() != "common" && fi.fileName() != "features" )
						cbQtVersionQMakeSpec->addItem( fi.fileName() );
				}
			}
			if ( cbQtVersionQMakeSpec->findText( v.QMakeSpec ) == -1 )
				cbQtVersionQMakeSpec->addItem( v.QMakeSpec );
			cbQtVersionQMakeSpec->setCurrentIndex( cbQtVersionQMakeSpec->findText( v.QMakeSpec ) );
			leQtVersionQMakeParameters->setText( v.QMakeParameters );
			cbQtVersionHasSuffix->setChecked( v.HasQt4Suffix );
			wQtVersion->setEnabled( true );
		}
		else if ( c->listWidget() == lwQtModules )
		{
			QtItem it = c->data( Qt::UserRole ).value<QtItem>();
			leCaptionQtModule->setText( it.Text );
			leValueQtModule->setText( it.Value );
			pteHelpQtModule->setPlainText( it.Help );
			wQtModule->setEnabled( true );
		}
		else if ( c->listWidget() == lwQtConfigurations )
		{
			QtItem it = c->data( Qt::UserRole ).value<QtItem>();
			leCaptionQtConfiguration->setText( it.Text );
			leValueQtConfiguration->setText( it.Value );
			pteHelpQtConfiguration->setPlainText( it.Help );
			wQtConfiguration->setEnabled( true );
		}
	}
	else if ( sender() == lwQtVersions )
	{
		wQtVersion->setEnabled( false );
		leQtVersionVersion->clear();
		leQtVersionPath->clear();
		cbQtVersionQMakeSpec->clear();
		cbQtVersionHasSuffix->setChecked( false );
	}
	else if ( sender() == lwQtModules )
	{
		wQtModule->setEnabled( false );
		leCaptionQtModule->clear();
		leValueQtModule->clear();
		pteHelpQtModule->clear();
	}
	else if ( sender() == lwQtConfigurations )
	{
		wQtConfiguration->setEnabled( false );
		leCaptionQtConfiguration->clear();
		leValueQtConfiguration->clear();
		pteHelpQtConfiguration->clear();
	}
	
	if ( c != p )
	{
		foreach ( QWidget* widget, findChildren<QWidget*>() )
		{
			widget->blockSignals( false );
		}
	}
}

void UISettingsQMake::loadSettings()
{
	// general
	foreach ( const QtVersion& v, mQtManager->versions() )
	{
		QListWidgetItem* it = new QListWidgetItem( v.Version, lwQtVersions );
		it->setData( Qt::UserRole, QVariant::fromValue( v ) );
		if ( v.Default )
			it->setBackground( QBrush( Qt::green ) );
	}
	
	// qt modules
	foreach ( QtItem i, mQtManager->modules() )
	{
		QListWidgetItem* it = new QListWidgetItem( i.Text, lwQtModules );
		it->setData( Qt::UserRole, QVariant::fromValue( i ) );
	}
	
	// configuration
	foreach ( QtItem i, mQtManager->configurations() )
	{
		QListWidgetItem* it = new QListWidgetItem( i.Text, lwQtConfigurations );
		it->setData( Qt::UserRole, QVariant::fromValue( i ) );
	}
}

void UISettingsQMake::on_dbbButtons_helpRequested()
{
	QString help;
	
	switch ( swPages->currentIndex() )
	{
		case 0:
		{
			help = tr( "You can register one or more Qt Version to use in your Qt projects, so you can easily select the one to use in project settings.<br /><br />"
						"The green item is the default Qt Version used. if there is no green item, the default Qt Version used will be the first one available. You can explicitely set the default Qt Version selecting an item and clicking the set default button.<br /><br />"
						"To add a new Qt version, simply click the <b>Add a new Qt Version</b> button at top and fill needed fields.<br /><br />"
						"The minimum required fields are:<br />"
						"- <b>Version</b>: it define a human label across a Qt version.<br />"
						"- <b>Path</b>: it define the path where is located your Qt installation (the path from where you can see bin/qmake).<br /><br />"
						"You can get more help about fields reading there tooltips." );
			break;
		}
		case 1:
		{
			help = tr( "You can register one or more Qt Modules for your Qt projects, so you can easily use them in the project settings dialog.<br />"
						"Qt Modules are components available by your Qt installation, like QtCore, GtGui...<br />"
						"This editor allow you to edit the available modules in case of by example a new Qt version is released and MkS did not yet support the new modules in the project settings.<br />"
						"A concrete example is the release of Qt 4.6.0 that has added QtMultimedia, you had notified that this module was not available in the project settings, so you can't use it.<br />"
						"By adding a new module by clicking <b>Add a new module</b> button, you can define the module caption and its associated value, this will make it available in the project settings !<br />"
						"The minimum required fields are <b>caption</b> and <b>value</b>, while <b>help</b> is an optional description of the module and will be shown as tooltip in the project settings.<br />"
						"Typically, the module value goes into the QT variable of your project file."	);
			break;
		}
		case 2:
		{
			help = tr( "Qt Configuration works like <b>Qt Modules</b> except that the content is shown in the <b>Others Modules</b> list and that values goes into the CONFIG variable of your project.<br /><br />"
						"Configurations having the word '<b>only</b>' as caption will be considerated as group separators and must have no value associated (they will be ignored).");
			break;
		}
	}
	
	if ( !help.isEmpty() )
	{
		QPoint point = rect().center();
		point.setY( 35 );
		QWhatsThis::showText( mapToGlobal( point ), help );
	}
}

void UISettingsQMake::on_dbbButtons_clicked( QAbstractButton* b )
{
	// only accept save button
	if ( dbbButtons->standardButton( b )  != QDialogButtonBox::Save )
	{
		return;
	}
	
	// save qt versions
	QtVersionList versions;
	
	for ( int i = 0; i < lwQtVersions->count(); i++ )
	{
		QListWidgetItem* item = lwQtVersions->item( i );
		
		const QtVersion& version = item->data( Qt::UserRole ).value<QtVersion>();
		
		if ( !version.isValid() )
		{
			lwQtVersions->setCurrentItem( item );
			QMessageBox::warning( this, tr( "Error..." ), tr( "A Qt Version is not valid and has been selected, please correct it and save again." ) );
			lwQtVersions->setFocus();
			return;
		}
		
		versions << version;
	}
	
	mQtManager->setVersions( versions );
	
	// save modules
	QtItemList modules;
	
	for ( int i = 0; i < lwQtModules->count(); i++ )
	{
		modules << lwQtModules->item( i )->data( Qt::UserRole ).value<QtItem>();
	}
	
	mQtManager->setModules( modules );
	
	// save configurations
	QtItemList configurations;
	
	for ( int i = 0; i < lwQtConfigurations->count(); i++ )
	{
		configurations << lwQtConfigurations->item( i )->data( Qt::UserRole ).value<QtItem>();
	}
	
	mQtManager->setConfigurations( configurations );
	
	// save content on disk
	mQtManager->sync();
}
