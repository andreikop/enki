#include "StatusBar.h"

#include <QLabel>
#include <QHBoxLayout>
#include <QIcon>

StatusBar.StatusBar( QWidget* parent )
    : QStatusBar( parent )
    # create labels
    QLabel* label
    
    label = ( mLabels[ltCursorPosition] = QLabel( self ) )
    label.setToolTip( tr( "Cursor position" ) )
    
    label = ( mLabels[ltSaveState] = QLabel( self ) )
    label.setToolTip( tr( "Modification state of file" ) )
    
    label = ( mLabels[ltEOLMode] = QLabel( self ) )
    label.setToolTip( tr( "EOL mode" ) )
    
    label = ( mLabels[ltIndentMode] = QLabel( self ) )
    label.setToolTip( tr( "Indentation mode" ) )
    
    # add labels
    for ( i = ltCursorPosition; i < ltIndentMode +1; i++ )
        label = mLabels[ i ]
        addPermanentWidget( label )
        label.setMargin( 2 )
        label.setFrameStyle( QFrame.NoFrame )
        label.setAttribute( Qt.WA_MacSmallSize )

    
    # force remove statusbar label frame
    setStyleSheet( "QStatusBar.item { border: 0px; }" )
    
    # connections
    self.messageChanged.connect(self.setMessage)


def label(self, type ):
    return mLabels[type]


def setMessage(self, message ):
    showMessage( message )
    setToolTip( message )


def setModified(self, modified ):
    label( ltSaveState ).setPixmap( QIcon( QPixmap( ":/file/icons/file/save.png" ) ).pixmap( QSize( 16, 16 ), modified ? QIcon.Normal : QIcon.Disabled ) )


def setEOLMode(self, mode ):
    switch ( mode )
        case QsciScintilla.EolWindows:
            label( ltEOLMode ).setText("Windows")
            break
        case QsciScintilla.EolUnix:
            label( ltEOLMode ).setText("Unix")
            break
        case QsciScintilla.EolMac:
            label( ltEOLMode ).setText("Mac")
            break
        default:
            label( ltEOLMode ).setText("-")
            break



def setIndentMode(self, mode ):
    switch ( mode )
        case 0:
            label( ltIndentMode ).setText("Spaces" )
            break
        case 1:
            label( ltIndentMode ).setText("Tabs" )
            break
        default:
            label( ltIndentMode ).setText("-")
            break



def setCursorPosition(self, pos ):
    s = tr( "Line: %1 Column: %2" )
    label( ltCursorPosition ).setText( pos == QPoint( -1, -1 ) ? s.arg( "-" ).arg( "-" ) : s.arg( pos.y() ).arg( pos.x() ) )

