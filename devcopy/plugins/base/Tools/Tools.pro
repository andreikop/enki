TARGET    = Tools

include( ../../plugins.pri )
DESTDIR    = $$MONKEY_PLUGINS_DIR/base

INCLUDEPATH    *= src

RESOURCES    *= src/resources/Tools.qrc

FORMS    *= src/ui/UIDesktopTools.ui \
    src/ui/UIToolsEdit.ui

HEADERS    *= src/Tools.h \
    src/ToolsManager.h \
    src/DesktopApplications.h \
    src/ui/UIDesktopTools.h \
    src/ui/UIToolsEdit.h

SOURCES    *= src/Tools.cpp \
    src/ToolsManager.cpp \
    src/DesktopApplications.cpp \
    src/ui/UIDesktopTools.cpp \
    src/ui/UIToolsEdit.cpp

mac:SOURCES    *= src/DesktopApplications_mac.cpp
else:unix:SOURCES    *= src/DesktopApplications_unix.cpp
win32:SOURCES    *= src/DesktopApplications_win.cpp