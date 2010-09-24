TARGET	= AStyle

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base
DEFINES	*= NDEBUG

INCLUDEPATH	*= src src/ui src/3rdparty/astyle

RESOURCES	*= src/resources/AStyle.qrc

FORMS	*= src/ui/UISettingsAStyle.ui

HEADERS	*= src/3rdparty/astyle/compiler_defines.h \
	src/3rdparty/astyle/astyle.h \
	src/ui/UISettingsAStyle.h \
	src/pFormatterSettings.h \
	src/pAStyle.h

SOURCES	*= src/3rdparty/astyle/ASBeautifier.cpp \
	src/3rdparty/astyle/ASFormatter.cpp \
	src/ui/UISettingsAStyle.cpp \
	src/pFormatterSettings.cpp \
	src/pAStyle.cpp