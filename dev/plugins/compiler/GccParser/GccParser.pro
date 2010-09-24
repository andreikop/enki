TARGET	= GccParser

include( ../../plugins.pri )
DESTDIR	= $$MONKEY_PLUGINS_DIR/compiler

HEADERS	*= src/GccParser.h \
	src/Parser.h

SOURCES	*= src/GccParser.cpp