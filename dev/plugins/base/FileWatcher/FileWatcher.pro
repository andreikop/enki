TARGET	= FileWatcher

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/base

RESOURCES	*= src/resources/FileWatcher.qrc

HEADERS	*= src/FileWatcher.h

SOURCES	*= src/FileWatcher.cpp