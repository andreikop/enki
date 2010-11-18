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
#include "QtDesignerChild.h"
#include "QtDesignerManager.h"

#include "widgethost.h"

#include <objects/pIconManager.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pQueuedMessageToolBar.h>
#include <objects/pStylesActionGroup.h>

#include <QDesignerFormWindowManagerInterface>
#include <QDesignerFormWindowInterface>
#include <QDesignerFormEditorInterface>
#include <QDesignerPropertyEditorInterface>
#include <QDesignerPropertySheetExtension>
#include <QExtensionManager>

#include <QPainter>
#include <QPrintDialog>
#include <QInputDialog>
#include <QStyleFactory>
#include <QPrinter>

QtDesignerChild::QtDesignerChild( QtDesignerManager* manager )
	: pAbstractChild()
{
	Q_ASSERT( manager );
	mDesignerManager = manager;

	// set up ui
	setWindowIcon( pIconManager::icon( "designer.png", ":/icons" ) );

	// create form host widget
	QDesignerFormWindowInterface* form = mDesignerManager->createNewForm( this );
	mDesignerManager->addFormWindow( form );

	mHostWidget = new SharedTools::WidgetHost( this, form );
	mHostWidget->setFrameStyle( QFrame::NoFrame | QFrame::Plain );
	mHostWidget->setFocusProxy( form );

	setWidget( mHostWidget );

	connect( mHostWidget->formWindow(), SIGNAL( changed() ), this, SLOT( formChanged() ) );
	connect( mHostWidget->formWindow(), SIGNAL( selectionChanged() ), this, SLOT( formSelectionChanged() ) );
	connect( mHostWidget->formWindow(), SIGNAL( geometryChanged() ), this, SLOT( formGeometryChanged() ) );
	connect( mHostWidget->formWindow(), SIGNAL( mainContainerChanged( QWidget* ) ), this, SLOT( formMainContainerChanged( QWidget* ) ) );
}

void QtDesignerChild::showEvent( QShowEvent* event )
{
	pAbstractChild::showEvent( event );

	mDesignerManager->setActiveFormWindow( mHostWidget->formWindow() );
}

void QtDesignerChild::formChanged()
{
	setWindowModified( mHostWidget->formWindow()->isDirty() );
	emit modifiedChanged( mHostWidget->formWindow()->isDirty() );
	emit contentChanged();
}

void QtDesignerChild::formSelectionChanged()
{
	mHostWidget->updateFormWindowSelectionHandles( true );
}

void QtDesignerChild::formGeometryChanged()
{
	// set modified state
	bool loading = property( "loadingFile" ).toBool();
	bool modified = !loading;

	// update property
	QDesignerPropertySheetExtension* sheet = qt_extension<QDesignerPropertySheetExtension*>( mDesignerManager->core()->extensionManager(), mHostWidget->formWindow() );
	QRect geo = sheet->property( sheet->indexOf( "geometry" ) ).toRect();
	geo.moveTopLeft( QPoint( 0, 0 ) );

	// update property
	mDesignerManager->core()->propertyEditor()->setPropertyValue( "geometry", geo, modified );

	// update state
	mHostWidget->formWindow()->setDirty( modified );
	setWindowModified( modified );
	setProperty( "loadingFile", false );

	// emit modified state
	emit modifiedChanged( modified );
	emit contentChanged();
}

void QtDesignerChild::formMainContainerChanged( QWidget* widget )
{
	Q_UNUSED( widget );
	setProperty( "loadingFile", true );
}

bool QtDesignerChild::openFile( const QString& fileName, const QString& codec )
{
	Q_UNUSED( codec );

	if ( QFile::exists( fileName ) )
	{
		// set content
		QFile file( fileName );

		if ( !file.open( QIODevice::ReadOnly ) )
		{
			return false;
		}

		setFilePath( fileName );
		mHostWidget->formWindow()->setFileName( fileName );
		mHostWidget->formWindow()->setContents( &file );

		if ( mHostWidget->formWindow()->mainContainer() )
		{
			// set clean
			mHostWidget->formWindow()->setDirty( false );

			setWindowModified( false );

			emit fileOpened();
			return true;
		}
		else
		{
			setFilePath( QString::null );
			mHostWidget->formWindow()->setFileName( QString::null );
		}
	}

	return false;
}

void QtDesignerChild::closeFile()
{
	setFilePath( QString::null );
	emit fileClosed();
}

void QtDesignerChild::reload()
{
	openFile( mHostWidget->formWindow()->fileName(), QString::null );
	
	emit fileReloaded();
}

QString QtDesignerChild::fileBuffer() const
{
	if ( mHostWidget->formWindow()->mainContainer() )
	{
		return mHostWidget->formWindow()->contents();
	}

	return QString::null;
}

QString QtDesignerChild::context() const
{
	return PLUGIN_NAME;
}

void QtDesignerChild::initializeContext( QToolBar* tb )
{
	QDesignerFormWindowManagerInterface* fwm = mDesignerManager->core()->formWindowManager();

	// add actions to toolbar
	tb->addAction( fwm->actionUndo() );
	tb->addAction( fwm->actionRedo() );
	tb->addAction( fwm->actionCut() );
	tb->addAction( fwm->actionCopy() );
	tb->addAction( fwm->actionPaste() );
	tb->addAction( fwm->actionLower() );
	tb->addAction( fwm->actionRaise() );
	tb->addAction( fwm->actionDelete() );
	tb->addAction( fwm->actionSelectAll() );
	tb->addSeparator();

	// tools
	tb->addActions( mDesignerManager->modesActions() );
	tb->addSeparator();

	// form
	tb->addAction( fwm->actionHorizontalLayout() );
	tb->addAction( fwm->actionVerticalLayout() );
	tb->addAction( fwm->actionSplitHorizontal() );
	tb->addAction( fwm->actionSplitVertical() );
	tb->addAction( fwm->actionGridLayout() );
	tb->addAction( fwm->actionFormLayout() );
	tb->addAction( fwm->actionSimplifyLayout() );
	tb->addAction( fwm->actionBreakLayout() );
	tb->addAction( fwm->actionAdjustSize() );

	// preview
	tb->addSeparator();
	tb->addAction( mDesignerManager->previewFormAction() );
}

QPoint QtDesignerChild::cursorPosition() const
{
	return QPoint( -1, -1 );
}

bool QtDesignerChild::isModified() const
{
	return mHostWidget->formWindow()->isDirty();
}

bool QtDesignerChild::isUndoAvailable() const
{
	return false;
}

bool QtDesignerChild::isRedoAvailable() const
{
	return false;
}

bool QtDesignerChild::isPasteAvailable() const
{
	return false;
}

bool QtDesignerChild::isCopyAvailable() const
{
	return false;
}


void QtDesignerChild::saveFile()
{
	// cancel if not modified
	if ( !mHostWidget->formWindow()->isDirty() )
	{
		return;
	}

	// write file
	QFile file( mHostWidget->formWindow()->fileName() );

	if ( file.open( QIODevice::WriteOnly ) )
	{
		file.resize( 0 );
		file.write( mHostWidget->formWindow()->contents().toUtf8() );
		file.close();

		mHostWidget->formWindow()->setDirty( false );
		setWindowModified( false );

		emit modifiedChanged( false );
	}
	else
	{
		MonkeyCore::messageManager()->appendMessage( tr( "An error occurs when saving :\n%1" ).arg( mHostWidget->formWindow()->fileName() ) );
	}

	return;
}

void QtDesignerChild::printFormHelper( QDesignerFormWindowInterface* form, bool quick )
{
	bool ok;
	const QStringList styles = QStyleFactory::keys();
	const int id = styles.indexOf( pStylesActionGroup::systemStyle() );
	QString style = QInputDialog::getItem( this, tr( "Choose a style..." ), tr( "Choose a style to render the form:" ), styles, id, false, &ok );

	if ( !ok )
	{
		return;
	}

	// get printer
	QPrinter printer;

	// if quick print
	if ( quick )
	{
		// check if default printer is set
		if ( printer.printerName().isEmpty() )
		{
			MonkeyCore::messageManager()->appendMessage( tr( "There is no default printer, please set one before trying quick print" ) );
			return;
		}

		// print and return
		QPainter painter( &printer );
		painter.drawPixmap( 0, 0, mDesignerManager->previewPixmap( form, style ) );
	}
	else
	{
		// printer dialog
		QPrintDialog printDialog( &printer );

		// if ok
		if ( printDialog.exec() )
		{
			// print and return
			QPainter painter( &printer );
			painter.drawPixmap( 0, 0, mDesignerManager->previewPixmap( form, style ) );
		}
	}
}

void QtDesignerChild::printFile()
{
	printFormHelper( mHostWidget->formWindow(), false );
}

void QtDesignerChild::quickPrintFile()
{
	printFormHelper( mHostWidget->formWindow(), true );
}

void QtDesignerChild::undo() {}

void QtDesignerChild::redo() {}

void QtDesignerChild::cut() {}

void QtDesignerChild::copy() {}

void QtDesignerChild::paste() {}

void QtDesignerChild::searchReplace() {}

void QtDesignerChild::goTo() {}

void QtDesignerChild::goTo( const QPoint& pos, int selectionLength )
{
	Q_UNUSED( pos );
	Q_UNUSED( selectionLength );
}

void QtDesignerChild::backupFileAs( const QString& fileName )
{
	QFile file( fileName );

	if ( file.open( QIODevice::WriteOnly ) )
	{
		file.resize( 0 );
		file.write( mHostWidget->formWindow()->contents().toUtf8() );
		file.close();
	}
	else
	{
		MonkeyCore::messageManager()->appendMessage( tr( "An error occurs when backuping: %1" ).arg( fileName ) );
	}
}

bool QtDesignerChild::isSearchReplaceAvailable() const
{
	return false;
}

bool QtDesignerChild::isGoToAvailable() const
{
	return false;
}

bool QtDesignerChild::isPrintAvailable() const
{
	return true;
}
