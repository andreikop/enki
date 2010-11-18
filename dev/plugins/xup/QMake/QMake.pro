TARGET	= QMake

include( ../../plugins.pri )
CONFIG	*= exceptions
DESTDIR	= $$MONKEY_PLUGINS_DIR/xup

INCLUDEPATH	*= src/gui

RESOURCES	*= src/resources/QMake.qrc

FORMS	*= src/gui/UISimpleQMakeEditor.ui \
	src/gui/UISettingsQMake.ui

HEADERS *= src/QMake.h \
	src/QMake2XUP.h \
	src/QMakeProjectItem.h \
	src/gui/UISimpleQMakeEditor.h \
	src/gui/UISettingsQMake.h \
	src/QtVersionManager.h

SOURCES	*= src/QMake.cpp \
	src/QMake2XUP.cpp \
	src/QMakeProjectItem.cpp \
	src/gui/UISimpleQMakeEditor.cpp \
	src/gui/UISettingsQMake.cpp \
	src/QtVersionManager.cpp