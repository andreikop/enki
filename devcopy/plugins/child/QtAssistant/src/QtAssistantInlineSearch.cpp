#include "QtAssistantInlineSearch.h"

#include <objects/pIconManager.h>

#include <QLineEdit>
#include <QCheckBox>
#include <QLabel>
#include <QToolButton>
#include <QHBoxLayout>
#include <QKeyEvent>

QtAssistantInlineSearch.QtAssistantInlineSearch( QWidget* parent )
    : QWidget( parent )
    hboxLayout = QHBoxLayout(self)
#ifndef Q_OS_MAC
    hboxLayout.setSpacing( 6 )
    hboxLayout.setMargin( 0 )
#endif

    toolClose = QToolButton( self )
    toolClose.setIcon( pIconManager.icon( "closetab.png", ":/assistant-icons" ) )
    toolClose.setAutoRaise( True )
    toolClose.clicked.connect(self.hide)
    hboxLayout.addWidget( toolClose )

    editFind = QLineEdit( self )
    editFind.setMinimumSize( QSize( 150, 0 ) )
    editFind.textChanged.connect(self.updateButtons)
    hboxLayout.addWidget (editFind )
    
    labelWrapped = QLabel( self )
    labelWrapped.setSizePolicy( QSizePolicy( QSizePolicy.Maximum, QSizePolicy.Preferred ) )
    labelWrapped.setTextFormat( Qt.RichText )
    labelWrapped.setScaledContents( True )
    labelWrapped.setAlignment( Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter )
    labelWrapped.setText( tr( "<img src=\":/assistant-icons/wrap.png\">&nbsp;Search wrapped" ) )
    labelWrapped.setVisible( False )
    hboxLayout.addWidget( labelWrapped )

    toolPrevious = QToolButton( self )
    toolPrevious.setAutoRaise( True )
    toolPrevious.setText( tr( "Previous" ) )
    toolPrevious.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
    toolPrevious.setIcon( pIconManager.icon( "previous.png", ":/assistant-icons" ) )
    hboxLayout.addWidget( toolPrevious )

    toolNext = QToolButton( self )
    toolNext.setAutoRaise( True )
    toolNext.setText( tr( "Next" ) )
    toolNext.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
    toolNext.setIcon( pIconManager.icon( "next.png", ":/assistant-icons" ) )
    hboxLayout.addWidget( toolNext )

    checkCase = QCheckBox( tr( "Case Sensitive" ), self )
    hboxLayout.addWidget( checkCase )

    checkWholeWords = QCheckBox( tr( "Whole words" ), self )
    hboxLayout.addWidget( checkWholeWords )
    checkWholeWords.hide()

    updateButtons()


def keyPressEvent(self, event ):
    if  event.key() == Qt.Key_Escape :
        hide()



def updateButtons(self):
    if  editFind.text().isEmpty() :
        toolPrevious.setEnabled( False )
        toolNext.setEnabled( False )

    else:
        toolPrevious.setEnabled( True )
        toolNext.setEnabled( True )


