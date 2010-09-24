# monkey includes path to include in plugins/core project

# include path
INCLUDEPATH	*= $${PWD}/src #$$getFolders( $${PWD}/src, resources )

# dependency
PRE_TARGETDEPS	*= $${PWD}

# library integration
LIBS	*= -L$${PACKAGE_BUILD_PATH}
win32:LIBS	*= -l$${PACKAGE_TARGET}
