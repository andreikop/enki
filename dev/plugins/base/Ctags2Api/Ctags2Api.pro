TARGET	= Ctags2Api

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH	*= src/ui

RESOURCES	*= src/resources/Ctags2Api.qrc

FORMS	*= src/ui/UICtags2Api.ui

HEADERS	*= src/Ctags2Api.h \
	src/ui/UICtags2Api.h

SOURCES	*= src/Ctags2Api.cpp \
	src/ui/UICtags2Api.cpp