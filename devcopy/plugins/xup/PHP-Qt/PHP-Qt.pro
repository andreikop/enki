TARGET    = PHP-Qt

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/xup

INCLUDEPATH    *= src/gui .

RESOURCES    *= src/resources/PHP-Qt.qrc

FORMS    *= ../XUP/src/gui/UIXUPEditor.ui

HEADERS    *= src/PHPQt.h \
    src/PHPQtProjectItem.h \
    ../XUP/src/gui/UIXUPEditor.h

SOURCES    *= src/PHPQt.cpp \
    src/PHPQtProjectItem.cpp \
    ../XUP/src/gui/UIXUPEditor.cpp