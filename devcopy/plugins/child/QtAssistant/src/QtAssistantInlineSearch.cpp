#include "QtAssistantInlineSearch.h"

#include <objects/pIconManager.h>

#include <QLineEdit>
#include <QCheckBox>
#include <QLabel>
#include <QToolButton>
#include <QHBoxLayout>
#include <QKeyEvent>

QtAssistantInlineSearch::QtAssistantInlineSearch( QWidget* parent )
    : QWidget( parent )
{
    QHBoxLayout* hboxLayout = new QHBoxLayout(this);
#ifndef Q_OS_MAC
    hboxLayout->setSpacing( 6 );
    hboxLayout->setMargin( 0 );
#endif

    toolClose = new QToolButton( this );
    toolClose->setIcon( pIconManager::icon( "closetab.png", ":/assistant-icons" ) );
    toolClose->setAutoRaise( true );
    connect( toolClose, SIGNAL( clicked() ), this, SLOT( hide() ) );
    hboxLayout->addWidget( toolClose );

    editFind = new QLineEdit( this );
    editFind->setMinimumSize( QSize( 150, 0 ) );
    connect( editFind, SIGNAL( textChanged( const QString& ) ), this, SLOT( updateButtons() ) );
    hboxLayout->addWidget (editFind );
    
    labelWrapped = new QLabel( this );
    labelWrapped->setSizePolicy( QSizePolicy( QSizePolicy::Maximum, QSizePolicy::Preferred ) );
    labelWrapped->setTextFormat( Qt::RichText );
    labelWrapped->setScaledContents( true );
    labelWrapped->setAlignment( Qt::AlignLeading | Qt::AlignLeft | Qt::AlignVCenter );
    labelWrapped->setText( tr( "<img src=\":/assistant-icons/wrap.png\">&nbsp;Search wrapped" ) );
    labelWrapped->setVisible( false );
    hboxLayout->addWidget( labelWrapped );

    toolPrevious = new QToolButton( this );
    toolPrevious->setAutoRaise( true );
    toolPrevious->setText( tr( "Previous" ) );
    toolPrevious->setToolButtonStyle( Qt::ToolButtonTextBesideIcon );
    toolPrevious->setIcon( pIconManager::icon( "previous.png", ":/assistant-icons" ) );
    hboxLayout->addWidget( toolPrevious );

    toolNext = new QToolButton( this );
    toolNext->setAutoRaise( true );
    toolNext->setText( tr( "Next" ) );
    toolNext->setToolButtonStyle( Qt::ToolButtonTextBesideIcon );
    toolNext->setIcon( pIconManager::icon( "next.png", ":/assistant-icons" ) );
    hboxLayout->addWidget( toolNext );

    checkCase = new QCheckBox( tr( "Case Sensitive" ), this );
    hboxLayout->addWidget( checkCase );

    checkWholeWords = new QCheckBox( tr( "Whole words" ), this );
    hboxLayout->addWidget( checkWholeWords );
    checkWholeWords->hide();

    updateButtons();
}

void QtAssistantInlineSearch::keyPressEvent( QKeyEvent* event )
{
    if ( event->key() == Qt::Key_Escape )
    {
        hide();
    }
}

void QtAssistantInlineSearch::updateButtons()
{
    if ( editFind->text().isEmpty() )
    {
        toolPrevious->setEnabled( false );
        toolNext->setEnabled( false );
    }
    else
    {
        toolPrevious->setEnabled( true );
        toolNext->setEnabled( true );
    }
}
