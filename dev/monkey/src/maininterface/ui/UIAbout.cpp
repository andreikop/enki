/****************************************************************************
**
** 		Created using Monkey Studio v1.8.1.0
** Authors    : Filipe AZEVEDO aka Nox P@sNox <pasnox@gmail.com>
** Project   : Monkey Studio IDE
** FileName  : UIAbout.cpp
** Date      : 2008-01-14T00:36:54
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
#include "UIAbout.h"
#include "ui_UIAbout.h"
#include "main.h"

#include <objects/pIconManager.h>

#include <QDate>

struct pData
{
	pData( const QString& _name, const QString& _nick, const QString& _country, const QString& _email, const QString& _comment )
		: name( _name ), nick( _nick ), country( _country ), email( _email ), comment( _comment )
	{
	}
	
	bool operator==( const pData& other ) const
	{
		return name == other.name
			&& nick == other.nick
			&& country == other.country
			&& email == other.email
			&& comment == other.comment;
	}
	
	bool operator!=( const pData& other ) const
	{
		return !operator==( other );
	}

	QString name;
	QString nick;
	QString country;
	QString email;
	QString comment;
};

UIAbout::UIAbout( QWidget* parent )
	: QDialog( parent )
{
	const QString tabString = "&nbsp;&nbsp;&nbsp;";
	
	const QString teamatesMask =
	"\t<tr>"
	"\t\t<td>%1 aka %2 (%3)<br />" +tabString +"<a href=\"mailto:%4\">%4</a><br />" +tabString +"%5</td>"
	"\t</tr>";
	
	const QString linksMask =
	"\t<tr>"
	"\t\t<td>%1<br />" +tabString +"<a href=\"%2\">%2</a></td>"
	"\t</tr>";
	
	const QString donationsMask =
	"\t<tr>"
	"\t\t<td>%1 aka %2 (%3)<br />" +tabString +"<a href=\"mailto:%4\">%4</a><br />" +tabString +"%5</td>"
	"\t</tr>";
	
	const QList<pData> teamates = QList<pData>()
		<< pData( "Filipe Azevedo", "Nox P@sNox", QObject::tr( "France" ), "pasnox@gmail.com", QObject::tr( "Creator & Principal Developer" ) )
		<< pData( "Kopats Andrei", "hlamer", QObject::tr( "Belarus" ), "hlamer@tut.by", QObject::tr( "Principal Developer, Class Browser, Beloruss translator" ) )
		<< pData( "Yannick", "xiantia", QObject::tr( "France" ), "xiantia@gmail.com", QObject::tr( "GNU Debugger Plugin" ) )
		<< pData( "Roper Alexander", "Minirop", QObject::tr( "France" ), "minirop@peyj.com", QObject::tr( "Qt Pro Parser, Some Features/Help" ) )
		<< pData( "Mashin Evgeniy", "evgenM", QObject::tr( "Russia" ), "mashin.zhenya@gmail.com", QObject::tr( "Many shared code between our IDEs" ) )
		<< pData( "Manuel Schmidt", "oversize", QObject::tr( "Germany" ), "manuel@schmidtman.de", QObject::tr( "Web Developer & Web Designer" ) )
		<< pData( "Julien Decologne", "Judd", QObject::tr( "France" ), "judd@hotmail.com", QObject::tr( "Splashscreen & Icons Designer" ) )
		<< pData( "Plano Marc", "Marc31", QObject::tr( "France" ), "marc31boss@gmail.com", QObject::tr( "French Translator" ) )
		<< pData( "Lukic Djordje", "rumpl", QObject::tr( "Serbia" ), "rumplstiltzkin@gmail.com", QObject::tr( "SDK Script Generator" ) )
		<< pData( QString::fromUtf8( "Aurélien MICHON" ), "aurelien", QObject::tr( "France" ), "aurelien.french@gmail.com", QObject::tr( "Winter Splashscreen Designer" ) );
	
	const QList<pData> links = QList<pData>()
		<< pData( QString::null, QString::null, QString::null, QString( "http://%1" ).arg( PACKAGE_DOMAIN ), QObject::tr( "%1 homepage" ).arg( PACKAGE_NAME ) )
		<< pData( QString::null, QString::null, QString::null, "https://launchpad.net/monkeystudio", QObject::tr( "Bug tracker" ) )
		<< pData( QString::null, QString::null, QString::null, "http://monkeystudio.org/forum", QObject::tr( "Forums" ) )
		<< pData( QString::null, QString::null, QString::null, "http://monkeystudio.org/rss.xml", QObject::tr( "News feed" ) )
		<< pData( QString::null, QString::null, QString::null, "http://monkeystudio.org/team", QObject::tr( "MkS Team" ) )
		<< pData( QString::null, QString::null, QString::null, "http://qt.nokia.com", QObject::tr( "Nokia's Qt homepage" ) )
		<< pData( QString::null, QString::null, QString::null, "http://webissues.mimec.org", QObject::tr( "WebIssues" ) )
		<< pData( QString::null, QString::null, QString::null, "http://webissues.monkeystudio.org", QObject::tr( "Our WebIssues Server (login/password: anonymous)" ) );
	
	const QList<pData> donations = QList<pData>()
		<< pData( "Filipe Azevedo", "Nox P@sNox", QObject::tr( "France" ), "pasnox@gmail.com", QObject::tr( "No donations for now, you can use this <a href=\"%1\">link</a> to make donation. Donations will help paying host/domain, and relatives things about the project." ).arg( PACKAGE_DONATION_LINK ) );
	
	setAttribute( Qt::WA_DeleteOnClose );
	setWindowTitle( tr( "About : %1" ).arg( PACKAGE_NAME ) );
	
	ui = new Ui::UIAbout;
	ui->setupUi( this );
	ui->lTitle->setText( PACKAGE_NAME );
	ui->lVersion->setText( tr( "Version %1 (%2)" ).arg( PACKAGE_VERSION ).arg( PACKAGE_VERSION_STR ) );
	ui->tbTeamates->setHtml( generateTeamatesTable( teamates, teamatesMask ) );
	ui->tbLinks->setHtml( generateLinksTable( links, linksMask ) );
	ui->tbDonations->setHtml( generateDonationsTable( donations, donationsMask ) );
	ui->lCopyrights->setText( PACKAGE_COPYRIGHTS );
}

UIAbout::~UIAbout()
{
	delete ui;
}

QString UIAbout::makeTable( const QString& contents ) const
{
	QString table =
	"<table width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\">"
	+contents +
	"</table>";
	return table;
}

QString UIAbout::generateTeamatesTable( const QList<pData>& data, const QString& mask ) const
{
	QString contents;
	
	foreach ( const pData& d, data ) {
		contents += mask
								.arg( d.name )
								.arg( d.nick )
								.arg( d.country )
								.arg( d.email )
								.arg( d.comment );
		
		if ( d != data.last() ) {
			contents += "<tr><td></td></tr>";
		}
	}
	
	return makeTable( contents );
}

QString UIAbout::generateLinksTable( const QList<pData>& data, const QString& mask ) const
{
	QString contents;
	
	foreach ( const pData& d, data ) {
		contents += mask
								.arg( d.comment )
								.arg( d.email );
		
		if ( d != data.last() ) {
			contents += "<tr><td></td></tr>";
		}
	}
	
	return makeTable( contents );
}

QString UIAbout::generateDonationsTable( const QList<pData>& data, const QString& mask ) const
{
	QString contents;
	
	foreach ( const pData& d, data ) {
		contents += mask
								.arg( d.name )
								.arg( d.nick )
								.arg( d.country )
								.arg( d.email )
								.arg( d.comment );
		
		if ( d != data.last() ) {
			contents += "<tr><td></td></tr>";
		}
	}
	
	return makeTable( contents );
}
