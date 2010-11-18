

#include "UIIrcStatus.h"

IrcStatus::IrcStatus(QWidget *parent) : QWidget(parent)
{
	setupUi(this);

	connect(pbJoin, SIGNAL(clicked()), this, SLOT(onJoin()));
	connect(pbConnect, SIGNAL(clicked()), this, SLOT(onConnect()));

	pbJoin->setEnabled(false);
	bConnected = false;

}


void IrcStatus::onConnect()
{
	if(!bConnected)
	{
		bConnected = true;
		emit ircConnect(leNickServerPort->text(), bConnected);
		pbConnect->setText("Disconnect");
		pbJoin->setEnabled(true);
	}
	else
	{
		bConnected = false;
		emit ircConnect(leNickServerPort->text(), bConnected);
		pbConnect->setText("Connect");
		pbJoin->setEnabled(false);
	}

}

void IrcStatus::onJoin()
{
	emit ircJoinChannel(leChannelName->text());
}

void IrcStatus::appendLog(QString s)
{
	teStatus->append(s);
}
