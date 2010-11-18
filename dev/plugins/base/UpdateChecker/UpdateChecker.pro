TARGET	= UpdateChecker

include( ../../plugins.pri )
QT	*= network
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH	*= src/ui

RESOURCES	*= src/resources/UpdateChecker.qrc

FORMS	*= src/ui/UIUpdateChecker.ui

HEADERS	*= src/UpdateChecker.h \
	src/ui/UIUpdateChecker.h

SOURCES	*= src/UpdateChecker.cpp \
	src/ui/UIUpdateChecker.cpp