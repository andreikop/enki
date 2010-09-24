TARGET	= ProjectHeaders

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH	*= src/ui

RESOURCES	*= src/resources/ProjectHeaders.qrc

FORMS	*= src/ui/UIProjectHeaders.ui

HEADERS	*= src/ProjectHeaders.h \
	src/ui/UIProjectHeaders.h

SOURCES	*= src/ProjectHeaders.cpp \
	src/ui/UIProjectHeaders.cpp