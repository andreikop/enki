TARGET    = PyQt

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/xup

INCLUDEPATH    *= src/gui .

RESOURCES    *= src/resources/PyQt.qrc

FORMS    *= ../XUP/src/gui/UIXUPEditor.ui

HEADERS    *= src/PyQt.h \
    src/PyQtProjectItem.h \
    ../XUP/src/gui/UIXUPEditor.h

SOURCES    *= src/PyQt.cpp \
    src/PyQtProjectItem.cpp \
    ../XUP/src/gui/UIXUPEditor.cpp