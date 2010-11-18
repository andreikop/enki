TARGET	= FileBrowser

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

RESOURCES	*= src/resources/FileBrowser.qrc

HEADERS	*= src/FileBrowser.h \
	src/pDockFileBrowser.h \
	src/FileBrowserSettings.h

SOURCES	*= src/FileBrowser.cpp \
	src/pDockFileBrowser.cpp \
	src/FileBrowserSettings.cpp