#include "MkSShellConsole.h"

#include "MkSShellInterpreter.h"

MkSShellConsole.MkSShellConsole( QWidget* parent )
        : pConsole( parent )
    setWindowTitle( "MkS Shell" )

    setColor( ctCommand, Qt.white )
    setColor( ctError, Qt.red )
    setColor( ctOutput, Qt.green )
    setColor( ctCompletion, Qt.gray )

    clear()
    setPrompt( "MkS:/> " )

    addAvailableCommand( MkSShellInterpreter.instance( self ) )


MkSShellConsole.~MkSShellConsole()


def sizeHint(self):
    return QSize( 640, 240 )

