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
/*!
	\file IrcDock.h
	\date 14/08/08
	\author Xiantia
	\version 1.0.0
	\brief This class contains only irc channel
*/


#include "IrcDock.h"

#include <QTextCodec>

#define USER_TAG "|MkS"

IrcDock::IrcDock( QWidget * w )
	: pDockWidget( w )
{
	mUiIrcMain = new IrcStatus(this);
	connect(mUiIrcMain, SIGNAL(ircConnect(QString, bool)), this , SLOT(onIrcConnect(QString, bool)));
	connect(mUiIrcMain, SIGNAL(ircJoinChannel(QString)), this , SLOT(onIrcJoinChannel(QString)));


	mTabWidget = new QTabWidget(this);
	mTabWidget->addTab(mUiIrcMain,"log Irc");
	
	// create tcp socket
	mTcpSocket = new QTcpSocket(this);
	
	connect(mTcpSocket,SIGNAL(hostFound ()), this , SLOT(onHostFound ()));
	connect(mTcpSocket,SIGNAL(connected()), this , SLOT(onConnected()));
	connect(mTcpSocket,SIGNAL(disconnected()), this , SLOT(onDisconnected()));

	connect(mTcpSocket,SIGNAL(readyRead()), this , SLOT(onReadyRead()));
	connect(mTcpSocket,SIGNAL(error(QAbstractSocket::SocketError)),this, SLOT(onTcpError(QAbstractSocket::SocketError)));

	// set widget in Dock
	setWidget(mTabWidget);
}


/*!
	\details Errors from QTcpSocket
*/
void IrcDock::onTcpError(QAbstractSocket::SocketError socketError)
{
	switch (socketError) 
	{
	case QAbstractSocket::RemoteHostClosedError:
		break;
		case QAbstractSocket::HostNotFoundError:
		mUiIrcMain->appendLog("The host was not found. Please check the host name and port settings.");
		break;
		case QAbstractSocket::ConnectionRefusedError:
		mUiIrcMain->appendLog("The connection was refused by the peer. Make sure the fortune server is running, and check that the host name and port settings are correct.");
		break;
		default:
		mUiIrcMain->appendLog("The following error occurred");
	}
}

/*!
	\details Host found
*/
void IrcDock::onHostFound ()
{
	mUiIrcMain->appendLog("V1 : Host found");
}

/*!
	\details Connected to host
*/
void IrcDock::onConnected()
{
	mUiIrcMain->appendLog("Connected");

	onSend("NICK " + mUserName.toLocal8Bit());
	onSend("USER " + mUserName.toLocal8Bit() + " 0 * :Monkey studio irc");
}

/*!
	\details Disconnect to host
*/
void IrcDock::onDisconnected()
{
	mUiIrcMain->appendLog("DisConnected");
}


/*!
	\details Local user want connect or not
*/ 
void IrcDock::onIrcConnect(QString s, bool b)
{
	// connect to server
	if(b)
	{
		QRegExp r("(.*)@(.*):(\\d+)");
		if(r.exactMatch(s))
		{
			QStringList l = r.capturedTexts();
			mUserName = l.at(1) + USER_TAG ;
			mTcpSocket->connectToHost(l.at(2), l.at(3).toInt());
		}
	}
	else
	{
		//delete all tab channel
		for(int i=0; i<mChannelList.count(); i++)
		{
			delete mChannelList.at(i);
			mChannelList.removeAt(i);
		}
		onSend("QUIT");
		mTcpSocket->close();
	}
}

/*!
	\details Local user want join channel
*/
void IrcDock::onIrcJoinChannel(QString channelName)
{

	// find if channel is already opened
	for(int i=0; i< mChannelList.count(); i++)
	{
		if(mChannelList.at(i)->name() == channelName)
			return;
	}

	IrcChannel * channel = new IrcChannel(this);	
	channel->setName(channelName);
	channel->setUserName(mUserName);
	channel->setPartMessage("Irc plugin for Monkey Studio");
	channel->setUserPrivilegePrefix(userPrefix);

	connect(channel, SIGNAL(sendData(QString)), this , SLOT(onSend(QString)));
	connect(channel, SIGNAL(channelClosed(QString)), this , SLOT(onIrcCloseChannel(QString)));

	mTabWidget->addTab(channel, channel->name());
	onSend("JOIN "+ channelName.toLocal8Bit());

	mChannelList << channel;
}

/*!
	\details Local user want part channel
*/
void IrcDock::onIrcCloseChannel(QString channelName)
{
	for(int i=0; i< mChannelList.count(); i++)
	{
		if(mChannelList.at(i)->name() == channelName)
		{
			delete mChannelList.at(i);
			mChannelList.removeAt(i);
			return;
		}
	}
}

/*!
	\details Datas from QTcpSocket
*/
void IrcDock::onReadyRead()
{
	buffer += QTextCodec::codecForLocale()->toUnicode( mTcpSocket->readAll());

	if(buffer.endsWith("\r\n"))
	{
		QStringList l = buffer.split("\r\n", QString::SkipEmptyParts);
		
		for( int i=0 ; i< l.count() ; i++)
		{
			QString s = l.at(i);
			mUiIrcMain->appendLog(s);
			
			// notify all opened channels
			for(int j=0; j< mChannelList.count(); j++)
			{
				mChannelList.at(j)->userJoin(s);		
				mChannelList.at(j)->userPart(s);
				mChannelList.at(j)->userQuit(s);
				mChannelList.at(j)->userList(s);
				mChannelList.at(j)->message(s);
				mChannelList.at(j)->userNickChange(s);				
				mChannelList.at(j)->setTopic(s);
				mChannelList.at(j)->setUserPrivilege(s);
			}
			ping(s);
			setUserPrivilegePrefix(s);
		}
		upDateUsersCount();
		buffer.clear();
	}
}


/*!
	\details Auto ping reply
*/
void IrcDock::ping(QString s)
{
	// PING :niven.freenode.net
	QRegExp r ("PING\\s:(.*)");
	if(r.exactMatch(s))	
	{
		QStringList l = r.capturedTexts();
		mUiIrcMain->appendLog("PONG reply ");
		onSend("PONG " + l.at(1).toLocal8Bit());
	}
}


/*!
	\details Send data to server
*/
void IrcDock::onSend(QString s)
{
	mTcpSocket->write(QTextCodec::codecForLocale()->fromUnicode( s + "\r\n" ) );
}

/*!
	\details Update in the tabWidget the number of users present on this channels
*/
void IrcDock::upDateUsersCount()
{
	for(int i=0; i< mChannelList.count(); i++)
	{
		mTabWidget->setTabText(i+1, mChannelList.at(i)->name() + " (" + QString::number(mChannelList.at(i)->getUsersCount()) + ")");
	}
}

void IrcDock::setUserPrivilegePrefix(QString s)
{
	// :.*\s005\s.*PREFIX=\((.*)\)([^ ]+).*
	//... PREFIX=(ov)@+ ...
	// o = @ -> @ircbot , channel operator
	// v = + -> +userName , voice operator
	QRegExp r(":.*\\s005\\s.*PREFIX=\\((.*)\\)([^ ]+).*");
	if(r.exactMatch(s))
	{
		QStringList l = r.capturedTexts();
		for(int i=0; i< l.at(1).length(); i++)
		{
			userPrefix[QString("+") + l.at(1).at(i)] = l.at(2).at(i);
			userPrefix[QString("-") + l.at(1).at(i)] = "";
		}
	}
}

/*!
	\details Quit Irc
*/
IrcDock::~IrcDock()
{
	onSend("QUIT");
	mTcpSocket->close();

	
//	delete mTcpSocket;
//	delete mUiIrcMain;

	// Qt delete for me
}

