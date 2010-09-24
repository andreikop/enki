TARGET    = Irc

include( ../../plugins.pri )
QT    *=  xml network gui
DESTDIR    = $$MONKEY_PLUGINS_DIR/network

RESOURCES    *= src/resources/irc.qrc

FORMS *= src/ui/UIIrcMain.ui

HEADERS    *= src/IrcDock.h \
    src/Irc.h \
    src/IrcChannel.h \
    src/ui/UIIrcStatus.h

SOURCES    *= src/IrcDock.cpp \
    src/Irc.cpp \
    src/IrcChannel.cpp \
    src/ui/UIIrcStatus.cpp