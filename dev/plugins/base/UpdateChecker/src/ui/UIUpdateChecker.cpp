/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UIUpdateChecker.cpp
** Date      : 2008-01-14T00:39:51
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
#include "UIUpdateChecker.h"
#include "UpdateChecker.h"

#include <main.h>

#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QPushButton>
#include <QDesktopServices>
#include <QDebug>

const QString UIUpdateChecker::mDownloadsUrl = PACKAGE_DOWNLOAD_FEED;

// UpdateItem

UpdateItem::UpdateItem( const QDomElement& element )
{
	QDomNodeList nodes = element.childNodes();
	
	for ( int i = 0; i < nodes.count(); i++ )
	{
		const QDomElement el = nodes.at( i ).toElement();
		const QString name = el.tagName();
		
		if ( name == "updated" )
		{
			mDatas[ UpdateItem::Updated ] = el.firstChild().toText().data();
		}
		else if ( name == "id" )
		{
			mDatas[ UpdateItem::Id ] = el.firstChild().toText().data();
		}
		else if ( name == "link" )
		{
			mDatas[ UpdateItem::Link ] = el.attribute( "href" );
		}
		else if ( name == "title" )
		{
			mDatas[ UpdateItem::Title ] = el.firstChild().toText().data().trimmed();
		}
		else if ( name == "author" )
		{
			mDatas[ UpdateItem::Author ] = el.firstChild().firstChild().toText().data();
		}
		else if ( name == "content" )
		{
			mDatas[ UpdateItem::Content ] = el.firstChild().toText().data().trimmed();
		}
	}
}

bool UpdateItem::operator<( const UpdateItem& other ) const
{
	return pVersion( version() ) < pVersion( other.version() );
}

bool UpdateItem::operator>( const UpdateItem& other ) const
{
	return pVersion( version() ) > pVersion( other.version() );
}

bool UpdateItem::operator<( const pVersion& other ) const
{
	return pVersion( version() ) < other;
}

bool UpdateItem::operator>( const pVersion& other ) const
{
	return pVersion( version() ) > other;
}

QDateTime UpdateItem::updated() const
{
	return QDateTime::fromString( mDatas.value( UpdateItem::Updated ), Qt::ISODate );
}

QString UpdateItem::id() const
{
	return mDatas.value( UpdateItem::Id );
}

QUrl UpdateItem::link() const
{
	return QUrl( mDatas.value( UpdateItem::Link ) );
}

QString UpdateItem::title() const
{
	return mDatas.value( UpdateItem::Title );
}

QString UpdateItem::author() const
{
	return mDatas.value( UpdateItem::Author );
}

QString UpdateItem::content() const
{
	return mDatas.value( UpdateItem::Content );
}

QString UpdateItem::toolTip() const
{
	return content().replace(
		QRegExp( "<a.*</a>" ), QString( "Update on %1 by %2" )
			.arg( updated().toString( Qt::DefaultLocaleLongDate ) )
			.arg( author() )
	);
}

bool UpdateItem::isFeatured() const
{
	return content().contains( "Featured", Qt::CaseInsensitive );
}

QString UpdateItem::displayText() const
{
	return content().split( "\n" ).value( 1 ).trimmed().append( " ( " ).append( title() ).append( " ) " );
}

QString UpdateItem::versionString() const
{
	const QString text = title();
	QRegExp rx( ".*mks_([\\d\\.\\d\\.\\d\\.\\d]{1,}[\\w]*)-svn.*" );
	
	if ( rx.exactMatch( text ) )
	{
		return rx.cap( 1 );
	}
	
	return QString::null;
}

pVersion UpdateItem::version() const
{
	return pVersion( versionString() );
}

bool UpdateItem::isValid() const
{
	return !mDatas.isEmpty();
}

// UIUpdateChecker

UIUpdateChecker::UIUpdateChecker( UpdateChecker* plugin, QWidget* w )
	: QDialog( w )
{
	Q_ASSERT( plugin );
	
	mPlugin = plugin;
	
	setupUi( this );
	setAttribute( Qt::WA_DeleteOnClose );
	setAttribute( Qt::WA_MacSmallSize );
	lVersion->setText( tr( "You are using version <b>%1</b> (%2)." ).arg( PACKAGE_VERSION ).arg( PACKAGE_VERSION_STR ) );
	dbbButtons->button( QDialogButtonBox::Yes )->setText( tr( "Download" ) );
	dbbButtons->button( QDialogButtonBox::Yes )->setEnabled( false );
	
	foreach ( QWidget* widget, findChildren<QWidget*>() )
	{
		widget->setAttribute( Qt::WA_MacSmallSize );
	}
	
	mAccessManager = new QNetworkAccessManager( this );
	
	connect( mAccessManager, SIGNAL( finished( QNetworkReply* ) ), this, SLOT( accessManager_finished( QNetworkReply* ) ) );
	
	mAccessManager->get( QNetworkRequest( QUrl( mDownloadsUrl ) ) );
}

UIUpdateChecker::~UIUpdateChecker()
{
}

void UIUpdateChecker::accessManager_finished( QNetworkReply* reply )
{
	const pVersion currentVersion( PACKAGE_VERSION );
	const QDateTime lastUpdated = mPlugin->settingsValue( "LastUpdated" ).toDateTime();
	const QDateTime lastCheck = mPlugin->settingsValue( "LastCheck" ).toDateTime();
	
	if ( reply->error() != QNetworkReply::NoError )
	{
		lwVersions->addItem( new QListWidgetItem( tr( "An error occur\n%1" ).arg( reply->errorString() ) ) );
	}
	else
	{
		QDomDocument document;
		
		if ( document.setContent( reply->readAll() ) )
		{
			const QString updatedText = document.elementsByTagName( "updated" ).at( 0 ).firstChild().toText().data();
			const QDateTime updated = QDateTime::fromString( updatedText, Qt::ISODate );
			const QDomNodeList entries = document.elementsByTagName( "entry" );
			
			for ( int i = 0; i < entries.count(); i++ )
			{
				const QDomElement element = entries.at( i ).toElement();
				
				const UpdateItem updateItem( element );
				
				if ( updateItem.isFeatured() && updateItem > currentVersion )
				{
					QListWidgetItem* item = new QListWidgetItem( updateItem.displayText() );
					
					item->setToolTip( updateItem.toolTip() );
					item->setData( Qt::UserRole, QVariant::fromValue( updateItem ) );
					lwVersions->addItem( item );
				}
			}
			
			mPlugin->setSettingsValue( "LastUpdated", updated );
			
			if ( lwVersions->count() > 0 )
			{				
				if ( !isVisible() && lastUpdated < updated )
				{
					open();
				}
			}
			else
			{
				QListWidgetItem* item = new QListWidgetItem( tr( "You are running the last available version." ) );
				
				item->setFlags( Qt::NoItemFlags );
				lwVersions->addItem( item );
				
				if ( !isVisible() )
				{
					close();
				}
			}
		}
		else
		{
			lwVersions->addItem( new QListWidgetItem( tr( "An error occur while parsing xml, retry later." ) ) );
		}
	}
	
	mPlugin->setSettingsValue( "LastCheck", QDateTime::currentDateTime() );
}

void UIUpdateChecker::on_lwVersions_itemSelectionChanged()
{
	QListWidgetItem* item = lwVersions->selectedItems().value( 0 );
	const UpdateItem updateItem = item ? item->data( Qt::UserRole ).value<UpdateItem>() : UpdateItem();
	
	dbbButtons->button( QDialogButtonBox::Yes )->setEnabled( updateItem.isValid() );
}

void UIUpdateChecker::accept()
{
	QListWidgetItem* item = lwVersions->selectedItems().value( 0 );
	const UpdateItem updateItem = item->data( Qt::UserRole ).value<UpdateItem>();
	
	QDesktopServices::openUrl( updateItem.link() );
	QDialog::accept();
}
