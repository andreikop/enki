TARGET	= MkSShell

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

RESOURCES	*= src/resources/MkSShell.qrc

HEADERS	*= src/MkSShell.h

SOURCES	*= src/MkSShell.cpp