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
    \file IrcDock.h
    \date 14/08/08
    \author Xiantia
    \version 1.0.0
    \brief This class contains only irc channel
'''


#include "IrcDock.h"

#include <QTextCodec>

#define USER_TAG "|MkS"

IrcDock.IrcDock( QWidget * w )
    : pDockWidget( w )
    mUiIrcMain = IrcStatus(self)
    mUiIrcMain.ircConnect.connect(self .onIrcConnect)
    mUiIrcMain.ircJoinChannel.connect(self .onIrcJoinChannel)


    mTabWidget = QTabWidget(self)
    mTabWidget.addTab(mUiIrcMain,"log Irc")
    
    # create tcp socket
    mTcpSocket = QTcpSocket(self)
    
    mTcpSocket.hostFound.connect(self .onHostFound)
    mTcpSocket.connected.connect(self .onConnected)
    mTcpSocket.disconnected.connect(self .onDisconnected)

    mTcpSocket.readyRead.connect(self .onReadyRead)
    mTcpSocket.error.connect(self.onTcpError)

    # set widget in Dock
    setWidget(mTabWidget)



'''!
    \details Errors from QTcpSocket
'''
def onTcpError(self, socketError):
    switch (socketError) 
    case QAbstractSocket.RemoteHostClosedError:
        break
        case QAbstractSocket.HostNotFoundError:
        mUiIrcMain.appendLog("The host was not found. Please check the host name and port settings.")
        break
        case QAbstractSocket.ConnectionRefusedError:
        mUiIrcMain.appendLog("The connection was refused by the peer. Make sure the fortune server is running, check that the host name and port settings are correct.")
        break
        default:
        mUiIrcMain.appendLog("The following error occurred")



'''!
    \details Host found
'''
void IrcDock.onHostFound ()
    mUiIrcMain.appendLog("V1 : Host found")


'''!
    \details Connected to host
'''
def onConnected(self):
    mUiIrcMain.appendLog("Connected")

    onSend("NICK " + mUserName.toLocal8Bit())
    onSend("USER " + mUserName.toLocal8Bit() + " 0 * :Monkey studio irc")


'''!
    \details Disconnect to host
'''
def onDisconnected(self):
    mUiIrcMain.appendLog("DisConnected")



'''!
    \details Local user want connect or not
''' 
def onIrcConnect(self, s, b):
    # connect to server
    if b:
        QRegExp r("(.*)@(.*):(\\d+)")
        if r.exactMatch(s):
            l = r.capturedTexts()
            mUserName = l.at(1) + USER_TAG 
            mTcpSocket.connectToHost(l.at(2), l.at(3).toInt())


    else:
        #delete all tab channel
        for(int i=0; i<mChannelList.count(); i++)
            delete mChannelList.at(i)
            mChannelList.removeAt(i)

        onSend("QUIT")
        mTcpSocket.close()



'''!
    \details Local user want join channel
'''
def onIrcJoinChannel(self, channelName):

    # find if channel is already opened
    for(int i=0; i< mChannelList.count(); i++)
        if mChannelList.at(i).name() == channelName:
            return


    IrcChannel channel = IrcChannel(self);    
    channel.setName(channelName)
    channel.setUserName(mUserName)
    channel.setPartMessage("Irc plugin for Monkey Studio")
    channel.setUserPrivilegePrefix(userPrefix)

    channel.sendData.connect(self .onSend)
    channel.channelClosed.connect(self .onIrcCloseChannel)

    mTabWidget.addTab(channel, channel.name())
    onSend("JOIN "+ channelName.toLocal8Bit())

    mChannelList << channel


'''!
    \details Local user want part channel
'''
def onIrcCloseChannel(self, channelName):
    for(int i=0; i< mChannelList.count(); i++)
        if mChannelList.at(i).name() == channelName:
            delete mChannelList.at(i)
            mChannelList.removeAt(i)
            return




'''!
    \details Datas from QTcpSocket
'''
def onReadyRead(self):
    buffer += QTextCodec.codecForLocale().toUnicode( mTcpSocket.readAll())

    if buffer.endsWith("\r\n"):
        l = buffer.split("\r\n", QString.SkipEmptyParts)
        
        for( int i=0 ; i< l.count() ; i++)
            s = l.at(i)
            mUiIrcMain.appendLog(s)
            
            # notify all opened channels
            for(int j=0; j< mChannelList.count(); j++)
                mChannelList.at(j).userJoin(s);        
                mChannelList.at(j).userPart(s)
                mChannelList.at(j).userQuit(s)
                mChannelList.at(j).userList(s)
                mChannelList.at(j).message(s)
                mChannelList.at(j).userNickChange(s);                
                mChannelList.at(j).setTopic(s)
                mChannelList.at(j).setUserPrivilege(s)

            ping(s)
            setUserPrivilegePrefix(s)

        upDateUsersCount()
        buffer.clear()




'''!
    \details Auto ping reply
'''
def ping(self, s):
    # PING :niven.freenode.net
    QRegExp r ("PING\\s:(.*)")
    if(r.exactMatch(s))    
        l = r.capturedTexts()
        mUiIrcMain.appendLog("PONG reply ")
        onSend("PONG " + l.at(1).toLocal8Bit())




'''!
    \details Send data to server
'''
def onSend(self, s):
    mTcpSocket.write(QTextCodec.codecForLocale().fromUnicode( s + "\r\n" ) )


'''!
    \details Update in the tabWidget the number of users present on self channels
'''
def upDateUsersCount(self):
    for(int i=0; i< mChannelList.count(); i++)
        mTabWidget.setTabText(i+1, mChannelList.at(i).name() + " (" + QString.number(mChannelList.at(i).getUsersCount()) + ")")



def setUserPrivilegePrefix(self, s):
    # :.*\s005\s.*PREFIX=\((.*)\)([^ ]+).*
    #... PREFIX=(ov)@+ ...
    # o = @ . @ircbot , operator
    # v = + . +userName , operator
    QRegExp r(":.*\\s005\\s.*PREFIX=\\((.*)\\)([^ ]+).*")
    if r.exactMatch(s):
        l = r.capturedTexts()
        for(int i=0; i< l.at(1).length(); i++)
            userPrefix[QString("+") + l.at(1).at(i)] = l.at(2).at(i)
            userPrefix[QString("-") + l.at(1).at(i)] = ""




'''!
    \details Quit Irc
'''
IrcDock.~IrcDock()
    onSend("QUIT")
    mTcpSocket.close()

    
#    delete mTcpSocket
#    delete mUiIrcMain

    # Qt delete for me


