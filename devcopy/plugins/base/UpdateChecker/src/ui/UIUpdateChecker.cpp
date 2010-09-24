'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors   : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio Base Plugins
** FileName  : UIUpdateChecker.cpp
** Date      : 2008-01-14T00:39:51
** License   : GPL
** Comment   : This header has been automatically generated, you are the original author, co-author, free to replace/append with your informations.
** Home Page : http:#www.monkeystudio.org
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
    along with self program; if not, to the Free Software
    Foundation, Inc., Franklin St, Floor, Boston, 02110-1301  USA
**
***************************************************************************'''
#include "UIUpdateChecker.h"
#include "UpdateChecker.h"

#include <main.h>

#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QPushButton>
#include <QDesktopServices>
#include <QDebug>

 QString UIUpdateChecker.mDownloadsUrl = PACKAGE_DOWNLOAD_FEED

# UpdateItem

UpdateItem.UpdateItem(  QDomElement& element )
    nodes = element.childNodes()

    for ( i = 0; i < nodes.count(); i++ )
         el = nodes.at( i ).toElement()
         name = el.tagName()

        if  name == "updated" :
            mDatas[ UpdateItem.Updated ] = el.firstChild().toText().data()

        elif  name == "id" :
            mDatas[ UpdateItem.Id ] = el.firstChild().toText().data()

        elif  name == "link" :
            mDatas[ UpdateItem.Link ] = el.attribute( "href" )

        elif  name == "title" :
            mDatas[ UpdateItem.Title ] = el.firstChild().toText().data().trimmed()

        elif  name == "author" :
            mDatas[ UpdateItem.Author ] = el.firstChild().firstChild().toText().data()

        elif  name == "content" :
            mDatas[ UpdateItem.Content ] = el.firstChild().toText().data().trimmed()




bool UpdateItem.operator<(  UpdateItem& other )
    return pVersion( version() ) < pVersion( other.version() )


bool UpdateItem.operator>(  UpdateItem& other )
    return pVersion( version() ) > pVersion( other.version() )


bool UpdateItem.operator<(  pVersion& other )
    return pVersion( version() ) < other


bool UpdateItem.operator>(  pVersion& other )
    return pVersion( version() ) > other


def updated(self):
    return QDateTime.fromString( mDatas.value( UpdateItem.Updated ), Qt.ISODate )


def id(self):
    return mDatas.value( UpdateItem.Id )


def link(self):
    return QUrl( mDatas.value( UpdateItem.Link ) )


def title(self):
    return mDatas.value( UpdateItem.Title )


def author(self):
    return mDatas.value( UpdateItem.Author )


def content(self):
    return mDatas.value( UpdateItem.Content )


def toolTip(self):
    return content().replace(
               QRegExp( "<a.*</a>" ), QString( "Update on %1 by %2" )
               .arg( updated().toString( Qt.DefaultLocaleLongDate ) )
               .arg( author() )
           )


def isFeatured(self):
    return content().contains( "Featured", Qt.CaseInsensitive )


def displayText(self):
    return content().split( "\n" ).value( 1 ).trimmed().append( " ( " ).append( title() ).append( " ) " )


def versionString(self):
     text = title()
    QRegExp rx( ".*mks_([\\d\\.\\d\\.\\d\\.\\d]{1,}[\\w]*)-svn.*" )

    if  rx.exactMatch( text ) :
        return rx.cap( 1 )


    return QString.null


def version(self):
    return pVersion( versionString() )


def isValid(self):
    return not mDatas.isEmpty()


# UIUpdateChecker

UIUpdateChecker.UIUpdateChecker( UpdateChecker* plugin, w )
        : QDialog( w )
    Q_ASSERT( plugin )

    mPlugin = plugin

    setupUi( self )
    setAttribute( Qt.WA_DeleteOnClose )
    setAttribute( Qt.WA_MacSmallSize )
    lVersion.setText( tr( "You are using version <b>%1</b> (%2)." ).arg( PACKAGE_VERSION ).arg( PACKAGE_VERSION_STR ) )
    dbbButtons.button( QDialogButtonBox.Yes ).setText( tr( "Download" ) )
    dbbButtons.button( QDialogButtonBox.Yes ).setEnabled( False )

    foreach ( QWidget* widget, findChildren<QWidget*>() )
        widget.setAttribute( Qt.WA_MacSmallSize )


    mAccessManager = QNetworkAccessManager( self )

    mAccessManager.finished.connect(self.accessManager_finished)

    mAccessManager.get( QNetworkRequest( QUrl( mDownloadsUrl ) ) )


UIUpdateChecker.~UIUpdateChecker()


def accessManager_finished(self, reply ):
     pVersion currentVersion( PACKAGE_VERSION )
     lastUpdated = mPlugin.settingsValue( "LastUpdated" ).toDateTime()
     lastCheck = mPlugin.settingsValue( "LastCheck" ).toDateTime()

    if  reply.error() != QNetworkReply.NoError :
        lwVersions.addItem( QListWidgetItem( tr( "An error occur\n%1" ).arg( reply.errorString() ) ) )

    else:
        QDomDocument document

        if  document.setContent( reply.readAll() ) :
             updatedText = document.elementsByTagName( "updated" ).at( 0 ).firstChild().toText().data()
             updated = QDateTime.fromString( updatedText, Qt.ISODate )
             entries = document.elementsByTagName( "entry" )

            for ( i = 0; i < entries.count(); i++ )
                 element = entries.at( i ).toElement()

                 UpdateItem updateItem( element )

                if  updateItem.isFeatured() and updateItem > currentVersion :
                    item = QListWidgetItem( updateItem.displayText() )

                    item.setToolTip( updateItem.toolTip() )
                    item.setData( Qt.UserRole, QVariant.fromValue( updateItem ) )
                    lwVersions.addItem( item )



            mPlugin.setSettingsValue( "LastUpdated", updated )

            if  lwVersions.count() > 0 :
                if  not isVisible() and lastUpdated < updated :
                    open()


            else:
                item = QListWidgetItem( tr( "You are running the last available version." ) )

                item.setFlags( Qt.NoItemFlags )
                lwVersions.addItem( item )

                if  not isVisible() :
                    close()



        else:
            lwVersions.addItem( QListWidgetItem( tr( "An error occur while parsing xml, later." ) ) )



    mPlugin.setSettingsValue( "LastCheck", QDateTime.currentDateTime() )


def on_lwVersions_itemSelectionChanged(self):
    item = lwVersions.selectedItems().value( 0 )
     updateItem = item ? item.data( Qt.UserRole ).value<UpdateItem>() : UpdateItem()

    dbbButtons.button( QDialogButtonBox.Yes ).setEnabled( updateItem.isValid() )


def accept(self):
    item = lwVersions.selectedItems().value( 0 )
     updateItem = item.data( Qt.UserRole ).value<UpdateItem>()

    QDesktopServices.openUrl( updateItem.link() )
    QDialog.accept()

