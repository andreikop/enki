TARGET	= SearchAndReplace

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH	*= src

RESOURCES	*= src/resources/SearchAndReplace.qrc

FORMS	*= src/SearchWidget.ui \
	src/SearchAndReplaceSettings.ui

HEADERS	*= src/SearchAndReplace.h \
	src/SearchThread.h \
	src/ReplaceThread.h \
	src/SearchWidget.h \
	src/SearchResultsDock.h \
	src/SearchResultsModel.h \
	src/SearchAndReplaceSettings.h

SOURCES	*= src/SearchAndReplace.cpp \
	src/SearchThread.cpp \
	src/ReplaceThread.cpp \
	src/SearchWidget.cpp \
	src/SearchResultsDock.cpp \
	src/SearchResultsModel.cpp \
	src/SearchAndReplaceSettings.cpp