'''***************************************************************************
**
**         Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIAbout.cpp
** Date      : 2008-01-14T00:36:54
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
#include "UIAbout.h"
#include "ui_UIAbout.h"
#include "main.h"

#include <objects/pIconManager.h>

#include <QDate>

struct pData
    pData(  QString& _name, _nick, _country, _email, _comment )
            : name( _name ), nick( _nick ), country( _country ), email( _email ), comment( _comment )


    bool operator==(  pData& other )
        return name == other.name
               and nick == other.nick
               and country == other.country
               and email == other.email
               and comment == other.comment


    bool operator!=(  pData& other )
        return not operator==( other )


    QString name
    QString nick
    QString country
    QString email
    QString comment


UIAbout.UIAbout( QWidget* parent )
        : QDialog( parent )
     tabString = "&nbsp;&nbsp;&nbsp;"

     QString teamatesMask =
        "\t<tr>"
        "\t\t<td>%1 aka %2 (%3)<br />" +tabString +"<a href=\"mailto:%4\">%4</a><br />" +tabString +"%5</td>"
        "\t</tr>"

     QString linksMask =
        "\t<tr>"
        "\t\t<td>%1<br />" +tabString +"<a href=\"%2\">%2</a></td>"
        "\t</tr>"

     QString donationsMask =
        "\t<tr>"
        "\t\t<td>%1 aka %2 (%3)<br />" +tabString +"<a href=\"mailto:%4\">%4</a><br />" +tabString +"%5</td>"
        "\t</tr>"

     QList<pData> teamates = QList<pData>()
                                  << pData( "Filipe Azevedo", "Nox P@sNox", QObject.tr( "France" ), "pasnox@gmail.com", QObject.tr( "Creator & Principal Developer" ) )
                                  << pData( "Kopats Andrei", "hlamer", QObject.tr( "Belarus" ), "hlamer@tut.by", QObject.tr( "Principal Developer, Browser, translator" ) )
                                  << pData( "Yannick", "xiantia", QObject.tr( "France" ), "xiantia@gmail.com", QObject.tr( "GNU Debugger Plugin" ) )
                                  << pData( "Roper Alexander", "Minirop", QObject.tr( "France" ), "minirop@peyj.com", QObject.tr( "Qt Pro Parser, Features/Help" ) )
                                  << pData( "Mashin Evgeniy", "evgenM", QObject.tr( "Russia" ), "mashin.zhenya@gmail.com", QObject.tr( "Many shared code between our IDEs" ) )
                                  << pData( "Manuel Schmidt", "oversize", QObject.tr( "Germany" ), "manuel@schmidtman.de", QObject.tr( "Web Developer & Web Designer" ) )
                                  << pData( "Julien Decologne", "Judd", QObject.tr( "France" ), "judd@hotmail.com", QObject.tr( "Splashscreen & Icons Designer" ) )
                                  << pData( "Plano Marc", "Marc31", QObject.tr( "France" ), "marc31boss@gmail.com", QObject.tr( "French Translator" ) )
                                  << pData( "Lukic Djordje", "rumpl", QObject.tr( "Serbia" ), "rumplstiltzkin@gmail.com", QObject.tr( "SDK Script Generator" ) )
                                  << pData( QString.fromUtf8( "Aurélien MICHON" ), "aurelien", QObject.tr( "France" ), "aurelien.french@gmail.com", QObject.tr( "Winter Splashscreen Designer" ) )

     QList<pData> links = QList<pData>()
                               << pData( QString.null, QString.null, QString.null, QString( "http:#%1" ).arg( PACKAGE_DOMAIN ), QObject.tr( "%1 homepage" ).arg( PACKAGE_NAME ) )
                               << pData( QString.null, QString.null, QString.null, "https:#launchpad.net/monkeystudio", QObject.tr( "Bug tracker" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#monkeystudio.org/forum", QObject.tr( "Forums" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#monkeystudio.org/rss.xml", QObject.tr( "News feed" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#monkeystudio.org/team", QObject.tr( "MkS Team" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#qt.nokia.com", QObject.tr( "Nokia's Qt homepage" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#webissues.mimec.org", QObject.tr( "WebIssues" ) )
                               << pData( QString.null, QString.null, QString.null, "http:#webissues.monkeystudio.org", QObject.tr( "Our WebIssues Server (login/password: anonymous)" ) )

     QList<pData> donations = QList<pData>()
                                   << pData( "Filipe Azevedo", "Nox P@sNox", QObject.tr( "France" ), "pasnox@gmail.com", QObject.tr( "No donations for now, can use self <a href=\"%1\">link</a> to make donation. Donations will help paying host/domain, relatives things about the project." ).arg( PACKAGE_DONATION_LINK ) )

    setAttribute( Qt.WA_DeleteOnClose )
    setWindowTitle( tr( "About : %1" ).arg( PACKAGE_NAME ) )

    ui = Ui.UIAbout
    ui.setupUi( self )
    ui.lTitle.setText( PACKAGE_NAME )
    ui.lVersion.setText( tr( "Version %1 (%2)" ).arg( PACKAGE_VERSION ).arg( PACKAGE_VERSION_STR ) )
    ui.tbTeamates.setHtml( generateTeamatesTable( teamates, teamatesMask ) )
    ui.tbLinks.setHtml( generateLinksTable( links, linksMask ) )
    ui.tbDonations.setHtml( generateDonationsTable( donations, donationsMask ) )
    ui.lCopyrights.setText( PACKAGE_COPYRIGHTS )


UIAbout.~UIAbout()
    delete ui


def makeTable(self, contents ):
    QString table =
        "<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\">"
        +contents +
        "</table>"
    return table


def generateTeamatesTable(self, data, mask ):
    QString contents

    for d in data:
        contents += mask
                    .arg( d.name )
                    .arg( d.nick )
                    .arg( d.country )
                    .arg( d.email )
                    .arg( d.comment )

        if  d != data.last() :
            contents += "<tr><td></td></tr>"



    return makeTable( contents )


def generateLinksTable(self, data, mask ):
    QString contents

    for d in data:
        contents += mask
                    .arg( d.comment )
                    .arg( d.email )

        if  d != data.last() :
            contents += "<tr><td></td></tr>"



    return makeTable( contents )


def generateDonationsTable(self, data, mask ):
    QString contents

    for d in data:
        contents += mask
                    .arg( d.name )
                    .arg( d.nick )
                    .arg( d.country )
                    .arg( d.email )
                    .arg( d.comment )

        if  d != data.last() :
            contents += "<tr><td></td></tr>"



    return makeTable( contents )

