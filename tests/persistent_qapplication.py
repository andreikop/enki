# Create a persistent QApplication instance. Call this before running **any** unit tests.
import sys
import sip
sip.setapi('QString', 2)
from PyQt4.QtGui import QApplication

app = QApplication(sys.argv)
