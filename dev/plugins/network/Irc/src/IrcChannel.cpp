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
	\file IrcChannel.cpp
	\date 14/08/08
	\author Xiantia
	\version 1.0.0
	\brief This class contains only irc channel
*/

#include "IrcChannel.h"


/*!
	\details Constructor.
	Create the widget container of channel
	\param parent of this widget
*/
IrcChannel::IrcChannel(QWidget * parent) : QWidget(parent)
{
	// create container
	QHBoxLayout *editAndListLayout = new QHBoxLayout();
	QHBoxLayout *editAndPartLayout = new QHBoxLayout();
	QVBoxLayout *mainLayout = new QVBoxLayout(this);
	QSplitter *splitter = new QSplitter(this);

	
	// un-comments this if you want see topic 
//	mTopic = new QLabel(this);
//	mainLayout->addWidget(mTopic);
	
	mainLayout->addLayout(editAndListLayout);

	// create widget
//	mTextEdit = new QTextEdit();
	mTextEdit = new QPlainTextEdit();
	mTextEdit->setReadOnly(true);
//	mTextEdit->setAcceptRichText(true);

	mMemberList = new QListWidget(this);
	mMemberList->setSortingEnabled (true);

	mLineEdit = new QLineEdit();
	mPart = new QPushButton(tr("Part"));
	editAndPartLayout->addWidget(mLineEdit);
	editAndPartLayout->addWidget(mPart);
	mainLayout->addLayout(editAndPartLayout);

	// add widget to container
	editAndListLayout->addWidget(splitter);
	splitter->addWidget(mTextEdit);
	splitter->addWidget(mMemberList);

	mMemberList->clear();

	connect(mPart, SIGNAL(clicked()), this, SLOT(onPart()));
}

/*!
	\details Local user send message to this channel
	\param l is the string from Irc server
*/
void IrcChannel::keyPressEvent ( QKeyEvent * event )
{
	if(event->key() == Qt::Key_Return)
	{
		// PRIVMSG #testmonkeystudio :coucou de monkey
		QString m = mLineEdit->text();
		mTextEdit->appendHtml("<font color=\"#000000\"><b>&lt;" + userName() + "&gt; </b>" + Qt::escape(m) + "</font>");

		emit sendData("PRIVMSG " + name() + " :" + m );
		mLineEdit->clear();
	}
}

/*!
	\details An user join this channel
	\param l is the string from Irc server
*/
void IrcChannel::userJoin(QString l)
{
	// 	:xiantia_!n=xiantia_@lse83-2-88-173-202-124.fbx.proxad.net JOIN :#testmonkeystudio
	QRegExp r (":([^!]+).*\\sJOIN\\s:([^ ]+)");
	if(r.exactMatch(l))
	{
		QStringList t = r.capturedTexts();
		if(t.at(2).toLower() == name())
		{
			if(userName() != t.at(1))
			{
				QListWidgetItem *newItem = new QListWidgetItem;
				newItem->setText(t.at(1));
				mMemberList->addItem(newItem);

				mTextEdit->appendHtml("<font color=\"#00ff00\">* "  + t.at(1) + " has joined " + name()  + "</font>");
			}
			else 
			{
				// this user is me :)
				mTextEdit->appendHtml("<font color=\"#ff0000\">Now talking in " + name() + "</font>");
			}

		}
	}
}

/*!
	\details An user quit this channel
	\param l is the string from Irc server
*/
void IrcChannel::userPart(QString l)
{
	// :xiantia!n=xiantia@lse83-2-88-173-202-124.fbx.proxad.net PART #testmonkeystudio :quit message
	QRegExp r (":([^!]+).*\\sPART\\s([^ ]+)\\s:(.*)");
	if(r.exactMatch(l))
	{
		QStringList t = r.capturedTexts();
		if(t.at(2).toLower() == name())
		{
			QListWidgetItem *it = findUser(t.at(1));
			if( it )
			{	
				mMemberList->removeItemWidget( it ); 
				delete it;
				mTextEdit->appendHtml("<font color=\"#0000ff\">* " + t.at(1) + " has left " + name() + " " + t.at(3) + "</font>");
			}
		}
	}
}

/*!
	\details An user quit Irc server
	\param l is the string from Irc server
*/
void IrcChannel::userQuit(QString l)
{
	//:ThomasGHenry!n=tghenry@nat/ibm/x-e360141219a099ca QUIT :"Leaving."
	QRegExp r (":([^!]+).*\\sQUIT\\s:(.*)");
	if(r.exactMatch(l))
	{
		QStringList t = r.capturedTexts();
		QListWidgetItem *it = findUser(t.at(1));
		if(	it )
		{
			mMemberList->removeItemWidget( it );
			delete it;
			mTextEdit->appendHtml("<font color=\"#0000ff\">* " + t.at(1) + " has quit " + name() + " " + t.at(2) + "</font>");
		}
	}
}

/*!
	\details An user as changed a nick
	\param s is the string from Irc server
*/
void IrcChannel::userNickChange(QString s)
{
	// :xiantia_!n=xiantia@lse83-2-88-173-202-124.fbx.proxad.net NICK :dddtre
	QRegExp r (":([^!]+).*\\sNICK\\s:(.*)");
	if(r.exactMatch(s))	
	{
		QStringList l = r.capturedTexts();
		QListWidgetItem *it = findUser(l.at(1));
		if(it)
		{
			it->setText( hasPrivilege(it->text()) + l.at(2));
			mTextEdit->appendHtml("<font color=\"#ff0000\">User " + l.at(1) + " is now know as " + l.at(2) + "</font>");
		}
	}
}

/*!
	\details Receive user list present in this channel
	\param l is the string from Irc server
*/
void IrcChannel::userList(QString l)
{
	//:zelazny.freenode.net 353 xiantia_ @ #testmonkeystudio :@xiantia_ 
	QRegExp r (":.*\\s353\\s.*\\s.\\s([^ ]+)\\s:(.*)");
	if(r.exactMatch(l))
	{
		QStringList t = r.capturedTexts();
		if(t.at(1).toLower() == name())
		{
			QStringList u = t.at(2).split(" ");

			for(int i=0; i< u.count(); i++)
			{
				if(!u.at(i).isEmpty())
				{
					QListWidgetItem *newItem = new QListWidgetItem;
					newItem->setText(u.at(i));
					mMemberList->addItem(newItem);
				}
			}
		}
	}
}


/*!
	\details User send an action to this channel
	\param l is the string from Irc server
*/
/*void IrcChannel::userAction(QString l)
{
	//:fyrestrtr!n=Burhan@pdpc/supporter/student/fyrestrtr PRIVMSG #ubuntu :.ACTION is having dinner.

	QRegExp r (".ACTION\\s.*");
	if(r.exactMatch(l))
		return true;
	return false;
}
*/

/*!
	\details Message from other user to this channel
	\param l is the string from Irc server
*/
void IrcChannel::message(QString l)
{
	QRegExp r (":([^!]+).*\\sPRIVMSG\\s([^ ]+)\\s:(.*)");
	if(r.exactMatch(l))
	{
		QStringList t = r.capturedTexts();
		if(t.at(2).toLower() == name())
//			if( !userAction(t.at(3)))
				mTextEdit->appendHtml("<font color=\"#000000\"><b>&lt;" + t.at(1) + "&gt; </b>" + Qt::escape(t.at(3)) + "</font>");
//			else
//				mTextEdit->append("<font color=\"#ffff00\">* " + t.at(1) + " " + t.at(3).remove(".ACTION ") + "</font>");
	}
}

/*!
	\details Get the current name of channel
	\retval The name of this channel
*/
QString IrcChannel::name()
{
	return mName;
}

/*!
	\details Set the current channel name
	\param name is the channelName
*/
void IrcChannel::setName(QString name)
{
	mName = name.toLower();
}

/*!
	\details Set the local user name
	\param n is the name of user
*/
void IrcChannel::setUserName(QString n)
{
	mUserName = n;
}

/*!
	\details Return the current local name (userName)
	\retval The current userName
*/
QString IrcChannel::userName()
{
	return mUserName;
}

/*!
	\details Local user quit this channel	
*/
void IrcChannel::onPart()
{
	emit sendData("PART " + name() + " :" + mPartMessage);
	emit channelClosed( name() );
}

/*!
	\details Set the quit message
	\param s is the message
*/
void IrcChannel::setPartMessage(QString s)
{
	mPartMessage = s;
}

/*!
	\details Return the current quit message
	\retval Current message
*/
QString IrcChannel::partMessage()
{
	return mPartMessage;
}


/*!
	\details Set the current topic for this channel
	\note Use if you un-comment mTopic in constructor
	\param l is the string from Irc server
*/
void IrcChannel::setTopic(QString l)
{
	// :brown.freenode.net 332 xiantia #ubuntu :Official Ubuntu Support Channel | 
	// Important, please type /msg ubottu etiquette | Be patient and read https://wiki.ubuntu.com/FAQ | Support options: 
	// http://www.ubuntu.com/support | IRC info: https://wiki.ubuntu.com/IRC | Pastes 
	// to http://paste.ubuntu.com | Install Ubuntu: http://www.ubuntu.com/getubuntu/download | Firefox 3.0 Final is now in Hardy
	QRegExp r (":.*\\s332\\s.*\\s([^ ]+)\\s:(.*)");
	if(r.exactMatch(l))
	{
/*		QStringList t = r.capturedTexts();
		if(t.at(1).toLower() == name())
			mTopic->setText(t.at(2));
*/	}
}

/*!
	\details Find user in this channel
	\param n is the user name that you find in this channel
	\retval QListWidgetItem pointer to this user.

*/
QListWidgetItem * IrcChannel::findUser(QString n)
{	
	n = QRegExp::escape(n);

	QRegExp r("[@,+]*" + n);
	for(int i=0; i< mMemberList->count(); i++)
	{
		QListWidgetItem *it = mMemberList->item(i);
		if(r.exactMatch(it->text()))
			return it;
	}
	return NULL;	
}


/*!
	\details Find if this user has privilege.
	\param s is the name of user sush as @Chanbot
	\retval The current privilege @, + or QString::Null() if this user haven't privilege
*/
QString IrcChannel::hasPrivilege(QString s)
{
	QRegExp r("([@,+]).*");
	if(r.exactMatch(s))
	{
		QStringList t = r.capturedTexts();
		return t.at(1);
	}
	return QString::Null();
}

/*!
	\details Modify the current privilege for one user in this channel.
	\param s is the string from Irc server
*/
void IrcChannel::setUserPrivilege(QString s)
{
	// :after!n=xiantia@lse83-2-88-173-202-124.fbx.proxad.net MODE #testmonkeystudio +o xiantia
	// * after sets mode: +o xiantia
	QRegExp r (":([^!]+).*\\sMODE\\s([^ ]+)\\s([^ ]+)\\s([^ ]+).*");
	if(r.exactMatch(s))
	{
		QStringList t = r.capturedTexts();
		if(t.at(2).toLower() == name())
		{
			QListWidgetItem *it = findUser(t.at(4));
			if(it)
			{
				mTextEdit->appendHtml("<font color=\"#00ff00\">* " + t.at(1) + " sets mode : " + t.at(3) + " " + t.at(4) + "</font>");
				QString n = userPrefix.value(t.at(3)); // get the corresponding tag og privilege
				QString u = it->text();
				if(hasPrivilege(u).isEmpty()) // user haven't privilege, add this 
					it->setText( n + u);
				else 
					it->setText( u.replace(0,1, n) ); // user have privilege, modify this
			}
		}
	}
}

/*!
	\details Set the current prefix of privilege
	Receive prefix for the privilege using by the server, +o == @
	\param s is the string from Irc server
*/
void IrcChannel::setUserPrivilegePrefix(QHash<QString, QString > s)
{
	userPrefix = s;
}

/*!
	\details Get the number of users in this channel.
	\retval The current number of users in this channel 
*/
int IrcChannel::getUsersCount()
{
	return mMemberList->count();
}
