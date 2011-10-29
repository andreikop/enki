"""
helpmenu --- Manage Help main menu items
========================================

Module contains about and help dialogues
"""

import os.path

from PyQt4 import uic
from PyQt4.QtCore import QObject
from PyQt4.QtGui import qApp, QDialog, QIcon

from mks.core.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_COPYRIGHTS
from mks.core.core import core, DATA_FILES_PATH

class Plugin(QObject):
    """Module implementation
    """
    def __init__(self):
        QObject.__init__(self)
        
        def createAction(menuItem, text, icon, tab):
            action = core.actionModel().addAction("mHelp/%s" % menuItem, text, QIcon(':mksicons/' + icon))
            slot = lambda : UIAbout(core.mainWindow(), tab).exec_()
            action.triggered.connect(slot)
        
        createAction('aAbout', self.tr('&About...'), 'monkey2.png', 'about')
        createAction('aHelp', self.tr('&Help...'), 'help.png', 'help')
        createAction('aReportBug', self.tr('Report &Bug...'), 'debugger.png', 'bug')
        createAction('aDonate', self.tr('&Donate...'), 'add.png', 'donate')

        self._aAboutQt = core.actionModel().addAction( "mHelp/aAboutQt", self.tr('About &Qt...'), QIcon(':mksicons/qt.png'))
        self._aAboutQt.triggered.connect(qApp.aboutQt)

    def __term__(self):
        pass

    def moduleConfiguratorClass(self):
        """ ::class:`mks.core.uisettings.ModuleConfigurator` used to configure plugin with UISettings dialogue
        """
        return None  # No any settings

class UIAbout(QDialog):
    """About dialogue
    """
    def __init__(self, parentWindow, tab):
        QDialog.__init__(self, parentWindow)
        uic.loadUi(os.path.join(DATA_FILES_PATH, 'ui/UIAbout.ui'), self)
        self.setWindowTitle( self.tr( "About : %s" % PACKAGE_NAME ) )
        
        self.lTitle.setText( PACKAGE_NAME )
        self.lVersion.setText( self.tr( "Version %s" % PACKAGE_VERSION ))
        self.lCopyrights.setText( PACKAGE_COPYRIGHTS )
        
        d = {'about': self.wLogo,
             'help': self.tbHelp,
             'bug': self.tbReportBug,
             'donate': self.tbDonations}        
        self.twAbout.setCurrentWidget(d[tab])
