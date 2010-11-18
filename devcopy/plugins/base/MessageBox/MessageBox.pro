TARGET    = MessageBox

include( ../../plugins.pri )
QT    *= xml
DESTDIR    = $$MONKEY_PLUGINS_DIR/base

RESOURCES    *= src/resources/MessageBox.qrc

FORMS    *= src/ui/UIBuildStep.ui \
    src/ui/UIOutput.ui \
    src/ui/UICommand.ui \
     src/ui/UIMessageBoxSettings.ui

HEADERS    *= src/ui/UIMessageBoxSettings.h \
    src/ui/MessageBoxDocks.h \
    src/MessageBox.h

SOURCES    *= src/ui/UIMessageBoxSettings.cpp \
    src/ui/MessageBoxDocks.cpp \
    src/MessageBox.cpp