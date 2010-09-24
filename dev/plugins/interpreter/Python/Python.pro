TARGET	= Python

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/interpreter

RESOURCES	*= src/resources/Python.qrc

HEADERS	*= src/Python.h

SOURCES	*= src/Python.cpp