from PyQt4.QtCore import QPoint, QSize, Qt
from PyQt4.QtGui import QApplication, QBoxLayout, QCursor, \
                        QPainter, QStyle, QStyleOptionToolButton, QTransform, QToolButton

class pToolButton(QToolButton):
    
    caNone, caArrow, caButton, caArrowClicked, caButtonClicked = range(5)

    def __init__(self, parent, direction = QBoxLayout.LeftToRight):
        QToolButton.__init__(self, parent)
        self._menuDown = False
        self._direction = None
    
        self.setDirection( direction )

    def internalSize(self, orientation ):
        size = QToolButton.size(self)
        buttonOrientation = Qt.Horizontal
        
        if self._direction in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop):
            buttonOrientation = Qt.Vertical
        
        if  buttonOrientation != orientation :
            size.transpose()

        return size

    def paint(self, option ):
        painter = QPainter ( self )
        transform = QTransform()
        
        # fix some properties due to rotation not handled by Qt
        if self.cursorArea() == pToolButton.caButtonClicked:
            option.activeSubControls |= QStyle.SC_ToolButton
            
            if  self.popupMode() == QToolButton.MenuButtonPopup :
                option.state |= QStyle.State_MouseOver
                option.activeSubControls |= QStyle.SC_ToolButtonMenu
        
        if self._direction == QBoxLayout.TopToBottom:
            option.rect.setSize( self.internalSize( Qt.Horizontal ) )
            transform.rotate( 90 )
            transform.translate( 0, -option.rect.height() +1 )
        elif self._direction == QBoxLayout.BottomToTop:
            option.rect.setSize( self.internalSize( Qt.Horizontal ) )
            transform.rotate( -90 )
            transform.translate( -option.rect.width() +1, 0 )
        
        painter.setTransform( transform )
        
        self.style().drawComplexControl( QStyle.CC_ToolButton, option, painter, self )

    def paintEvent(self, event ):
        option = QStyleOptionToolButton()
        self.initStyleOption( option )
        
        self.paint( option )

    def mousePressEvent(self, event ):
        if self.cursorArea( event.pos() ) ==  pToolButton.caArrowClicked:
            self._menuDown = True
            self.showMenu()
            self._menuDown = False
        elif self.cursorArea( event.pos() ) ==  pToolButton.caButtonClicked:
            self.setDown( not self.isDown() )
        elif self.cursorArea( event.pos() ) ==  pToolButton.caNone:
            pass
        else:
            QAbstractButton.mousePressEvent( self, event )
        # update button
        self.update()

    def mouseMoveEvent(self, event ):
        QToolButton.mouseMoveEvent( self, event )

        if  event.buttons() != Qt.NoButton :
            self.setDown( self.hitButton( event.pos() ) )

    def mouseReleaseEvent(self, event ):
        self._menuDown = False

        if self.cursorArea( event.pos()) == pToolButton.caButton:
            self.click()
        elif  self.cursorArea( event.pos()) in (pToolButton.caArrow, pToolButton.caNone):
            pass
        else:
            QAbstractButton.mouseReleaseEvent( self, event )

        # update button
        self.update()

    def cursorArea(self, _pos=QPoint()):
        # cursor pos
        if _pos.isNull():
            pos = self.mapFromGlobal( QCursor.pos() )
        else:
           pos = _pos

        # if not contain is button return none
        if  not self.hitButton( pos ) :
            return pToolButton.caNone

        # is arrow type
        arrowType = self.popupMode() == QToolButton.MenuButtonPopup

        # is mouse pressed ?!
        mousePressed = QApplication.mouseButtons() & Qt.LeftButton

        # check if we are a arrow button
        if  arrowType :        # get bounding rectangle
            rect = self.rect()
        
            # get style options
            opt = QStyleOptionToolButton 
            self.initStyleOption( opt )
        
            # force to do horizontal calcul
            opt.rect.setSize( self.internalSize( Qt.Horizontal ) )

            # get arraow bounding rectangle
            size = self.style().subControlRect( QStyle.CC_ToolButton, opt, QStyle.SC_ToolButtonMenu, self ).size()

            if self._direction == QBoxLayout.BottomToTop:
                size.transpose()
            elif self._direction == QBoxLayout.TopToBottom:
                size.transpose()
                rect.setY( rect.height() -size.height() )
            else:
                rect.setX( rect.width() -size.width() )

            # get valid bounding rectangle size
            rect.setSize( size )

            # in arrow bounding rect
            if  rect.isValid() and rect.contains( pos ) :
                if mousePressed:
                    return pToolButton.caArrowClicked
                else:
                    return pToolButton.caArrow

        # in button
        if mousePressed:
            return pToolButton.caButtonClicked
        else:
           return pToolButton.caButton

    def hasMenu(self):
        menu = self.menu()
        
        if menu is None and self.defaultAction():
            menu = self.defaultAction().menu()

        return menu

    def menuButtonDown(self):
        return self.hasMenu() and self._menuDown

    def minimumSizeHint(self):
        return QSize()

    def sizeHint(self):
        #get default size
        size = QToolButton.sizeHint(self)

        # calcul size hint
        if self._direction in (QBoxLayout.LeftToRight, QBoxLayout.RightToLeft):
            pass
        elif self._direction in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop):
            size.transpose()

        # return size hint
        return size

    def direction(self):
        return self._direction

    def setDirection(self, direction ):
        if  self._direction == direction :
            return

        self._direction = direction
        self.updateGeometry()


    def userData(self):
        return self._userData

    def setUserData(self, data ):
        self._userData = data
