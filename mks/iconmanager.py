from PyQt4.QtGui import *

def pixmap(fileName, prefix=':/'):
    """TODO it is just a stub
    """
    return QPixmap('/home/a/code/mks/v2/branches/dev/monkey/src/resources/icons/application/' + fileName)

def icon(fileName, prefix=':/'):
    """TODO it is just a stub
    """
    return QIcon( pixmap( fileName, prefix ) )

