"""
colorbutton --- Button, which is used for configuring colors
============================================================

Button shows selected color as own icon and opens QColorDialog when clicked
"""
from PyQt4.QtCore import pyqtSignal, QSize
from PyQt4.QtGui import QColor, QColorDialog, QIcon, QPixmap, QToolButton

def tr(text):
    """Dummy tr() implementation
    """
    return text

class ColorButton(QToolButton):
    """Button, which is used for configuring colors
    """

    colorChanged = pyqtSignal(QColor)
    """
    colorChanged(color)

    **Signal** emitted, after current color has changed
    """

    def __init__(self, colorOrParent, *args):
        if isinstance(colorOrParent, QColor):
            QToolButton.__init__(self, *args)
            self.setColor( colorOrParent )
        else:
            QToolButton.__init__(self, colorOrParent, *args)
            self.setColor(QColor())

        self.clicked.connect(self._onClicked)
        self.setIconSize( QSize( 16, 16 ) )

    def color(self):
        """Currently selected color
        """
        return self._color

    def setColor(self, color ):
        """Set color. Update button icon
        """
        self._color = color

        c = self._color
        texts = ["RGBA #%02x%02x%02x%02x" % (c.red(), c.green(), c.blue(), c.alpha()),
                 "RGBA %d, %d, %d, %d" % (c.red(), c.green(), c.blue(), c.alpha())]

        self.setText( texts[0] )
        self.setToolTip( '\n'.join(texts))

        pixmap = QPixmap(self.iconSize())
        pixmap.fill(self._color)

        self.setIcon( QIcon(pixmap) )

        self.colorChanged.emit( self._color )

    def _onClicked(self):
        """Button has been clicked.
        Show dialog and update color
        """
        color = QColorDialog.getColor( self._color,
                                       self.window(),
                                       tr( "Choose a color" ),
                                       QColorDialog.ShowAlphaChannel)

        if  color.isValid():
            self.setColor( color )
