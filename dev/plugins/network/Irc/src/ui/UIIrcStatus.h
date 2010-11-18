
#ifndef UIIRCMAIN_H
#define UIIRCMAIN_H

#include "ui_UIIrcMain.h"


class IrcStatus : public QWidget, public Ui::UIIrcMain
{
	Q_OBJECT

public:

	IrcStatus(QWidget *p=0);
	void appendLog(QString);

public slots :

	void onConnect();
	void onJoin();

private :
	bool bConnected;

signals:
	void ircConnect(QString ,bool);
	void ircJoinChannel(QString);


};

#endif
