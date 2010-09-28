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
    \brief Main Irc container 
*/

#ifndef IRCDOCKS_H
#define IRCDOCKS_H

#include <workspace/pWorkspace.h>
#include <coremanager/MonkeyCore.h>
#include <widgets/pDockWidget.h>
#include <objects/QSingleton.h>

#include <QHBoxLayout>
#include <QTabWidget>
#include <QTcpSocket>


#include "IrcChannel.h"
#include "./ui/UIIrcStatus.h"

/*!
    \brief Main Irc container 
    \details This class manage all channel, read / write data to server.
*/
class IrcDock : public pDockWidget, public QSingleton<IrcDock>
{
    Q_OBJECT
    friend class Irc;
    friend class QSingleton<IrcDock>;

    
public:
    IrcDock( QWidget * w = 0 );
    ~IrcDock();


public slots:

    void onHostFound();
    void onConnected();
    void onDisconnected();
    void onReadyRead();
    void onSend(QString );
    void onTcpError(QAbstractSocket::SocketError);
    void ping(QString);

    void onIrcJoinChannel(QString);
    void onIrcCloseChannel(QString);
    void onIrcConnect(QString, bool);

    void upDateUsersCount();
    
private:

    QTabWidget * mTabWidget;
    QTcpSocket * mTcpSocket;
    QTextEdit * mTextEdit;

    QList<IrcChannel *> mChannelList;
    QString mUserName;

    IrcStatus  * mUiIrcMain;
    QString buffer;
    QHash<QString, QString> userPrefix;
    void setUserPrivilegePrefix(QString);
};

#endif 
