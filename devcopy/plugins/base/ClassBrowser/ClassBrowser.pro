TARGET    = ClassBrowser

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/base

HEADERS    *= src/ClassBrowser.h \
    src/pDockClassBrowser.h \
    src/ClassBrowserSettings.h

SOURCES    *= src/ClassBrowser.cpp \
    src/pDockClassBrowser.cpp \
    src/ClassBrowserSettings.cpp