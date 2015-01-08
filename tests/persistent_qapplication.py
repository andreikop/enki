# Create a persistent QApplication instance.
import sys

import sip
sip.setapi('QString', 2)
sip.setapi('QVariant', 2)
from PyQt4.QtGui import QApplication

papp = QApplication(sys.argv)
