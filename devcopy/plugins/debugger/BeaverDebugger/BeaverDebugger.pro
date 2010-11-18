TARGET    = BeaverDebugger

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/debugger

RESOURCES    *= resources/BeaverDebugger.qrc

HEADERS    *= BeaverDebugger.h \
    BeaverDebuggerSettings.h

SOURCES    *= BeaverDebugger.cpp \
    BeaverDebuggerSettings.cpp