

#include "UIIrcStatus.h"

IrcStatus.IrcStatus(QWidget *parent) : QWidget(parent)
    setupUi(self)

    pbJoin.clicked.connect(self.onJoin)
    pbConnect.clicked.connect(self.onConnect)

    pbJoin.setEnabled(False)
    bConnected = False




def onConnect(self):
    if not bConnected:
        bConnected = True
        ircConnect.emit(leNickServerPort.text(), bConnected)
        pbConnect.setText("Disconnect")
        pbJoin.setEnabled(True)

    else:
        bConnected = False
        ircConnect.emit(leNickServerPort.text(), bConnected)
        pbConnect.setText("Connect")
        pbJoin.setEnabled(False)




def onJoin(self):
    ircJoinChannel.emit(leChannelName.text())


def appendLog(self, s):
    teStatus.append(s)

