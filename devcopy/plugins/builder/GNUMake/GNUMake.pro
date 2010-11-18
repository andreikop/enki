TARGET    = GNUMake

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/builder

HEADERS    *= src/GNUMake.h

SOURCES    *= src/GNUMake.cpp