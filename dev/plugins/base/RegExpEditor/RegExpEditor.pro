TARGET	= RegExpEditor

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH	*= src src/ui

RESOURCES	*= src/resources/RegExpEditor.qrc

FORMS	*= src/ui/UIRegExpEditor.ui

HEADERS	*= src/RegExpEditor.h \
	src/ui/UIRegExpEditor.h

SOURCES	*= src/RegExpEditor.cpp \
	src/ui/UIRegExpEditor.cpp