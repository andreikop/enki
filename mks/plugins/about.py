
from mks.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_COPYRIGHTS
class UIAbout:
    """About dialogue
    """
    def __init__(self, parentWindow):
        self.setWindowTitle( self.tr( "About : %1" PACKAGE_NAME ) )
    
        self.setupUi( self )
        
        self.lTitle.setText( PACKAGE_NAME )
        self.lVersion.setText( self.tr( "Version %1" % PACKAGE_VERSION ))
        self.lCopyrights.setText( PACKAGE_COPYRIGHTS )
