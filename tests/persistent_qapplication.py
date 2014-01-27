# Create a persistent QApplication instance.
import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)

from PyQt4.QtGui import QApplication

class NotifyApplication(QApplication):
    """ This class can assert if any events are emitted.
    
    Its purpose is to check that, after a PyQt class is closed,
    there are no timer/other callback leaks.
    
    """
    def __init__(self, *args):
        QApplication.__init__(self, *args)
        self.assertOnEvents = False
        
    def notify(self, receiver, event):
        """ Pass the event on, printing diagnostics if enabled. """
        
        if self.assertOnEvents:
            print('Post-termination event: receiver = %s, event = %s' % (receiver, event))
        return QApplication.notify(self, receiver, event)
        

papp = QApplication(sys.argv)
