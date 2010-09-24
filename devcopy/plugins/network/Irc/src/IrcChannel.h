'''***************************************************************************
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
***************************************************************************'''
'''!
    \file IrcChannel.h
    \date 14/08/08
    \author Xiantia
    \version 1.0.0
    \brief This class contains only irc channel
'''


#ifndef IRCCHANNEL_H
#define IRCCHANNEL_H

#include <workspace/pWorkspace.h>
#include <coremanager/MonkeyCore.h>

#include <QWidget>
#include <QKeyEvent>
#include <QPushButton>
#include <QPlainTextEdit>
#include <QLineEdit>
#include <QListWidget>
#include <QHBoxLayout>
#include <QSplitter>

class QLabel

'''!
    \brief This class contains only irc channel
    \details This class manage only one irc channel.

'''

class IrcChannel : public QWidget
    Q_OBJECT

public:

    IrcChannel(QWidget *p=0)
    void userJoin(QString)
    void userPart(QString)
    void userQuit(QString)
    void message(QString)
    void userList(QString)
    void userNickChange(QString)

    void setUserPrivilege(QString)
    void setUserPrivilegePrefix(QHash<QString, QString>)

    QString name()
    void setName(QString)

    QString userName()
    void setUserName(QString)

    QString partMessage()
    void setPartMessage(QString)

    void setTopic(QString)

    int getUsersCount()

public slots :

    void onPart()

private:

#    QTextEdit * mTextEdit
    QPlainTextEdit * mTextEdit

    QListWidget * mMemberList
    QPushButton *mPart
    QLineEdit * mLineEdit
    QLabel *mTopic

    QString mName
    QString mUserName
    QString mPartMessage

    QListWidgetItem * findUser(QString)
    QString hasPrivilege(QString)

    QHash<QString, userPrefix

protected :

    void keyPressEvent ( QKeyEvent * event )

signals:

    void sendData(QString)
    void channelClosed(QString)


#endif
