/****************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIAddAbbreviation.cpp
** Date      : 2008-01-14T00:36:47
** License   : GPL
** Comment   : This header has been automatically generated, if you are the original author, or co-author, fill free to replace/append with your informations.
** Home Page : http://www.monkeystudio.org
**
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
**
****************************************************************************/
#include "UIAddAbbreviation.h"
#include "pMonkeyStudio.h"

#include <QTreeWidget>
#include <QMessageBox>

void UIAddAbbreviation::edit( QTreeWidget* t )
{
    // create dialog
    UIAddAbbreviation d( t->window(), t );
    // execute dialog
    d.exec();
}

UIAddAbbreviation::UIAddAbbreviation( QWidget* w, QTreeWidget* t )
    : QDialog( w ), mTree( t )
{
    setupUi( this );
    // fill combo with language
    cbLanguages->addItems( pMonkeyStudio::availableLanguages() );
    // set focus on template lineedit
    leTemplate->setFocus();
}

UIAddAbbreviation::~UIAddAbbreviation()
{
}

void UIAddAbbreviation::accept()
{
    // check if item already exists for same name
    QTreeWidgetItem* it = mTree->findItems( leTemplate->text(), Qt::MatchFixedString ).value( 0 );
    // if not or differente language
    if ( !it || it->text( 2 ) != cbLanguages->currentText() )
    {
        // create item
        it = new QTreeWidgetItem( mTree );
        // fill it
        it->setText( 0, leTemplate->text() );
        it->setText( 1, leDescription->text() );
        it->setText( 2, cbLanguages->currentText() );
        it->setData( 0, Qt::UserRole, QString() );
        // set current item new one
        mTree->setCurrentItem( it );
        // accept
        QDialog::accept();
    }
    else
        QMessageBox::warning( window(), tr( "Warning..." ), tr( "This template already exists for this language." ) );
}
