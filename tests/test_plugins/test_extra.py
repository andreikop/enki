# Imports
# =======
# Library imports
# ---------------
import unittest
import os.path
import sys
from multiprocessing import Process, Queue

# Local application imports
# -------------------------
# Do this before PyQt imports so that base will set up sip API correctly.
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))


from import_fail import ImportFail


with ImportFail('CodeChat'):
    import base
    from enki.plugins.preview import SettingsWidget


class Test(base.TestCase):
    def setUp(self):
        base.TestCase.setUp(self)

    def test_uiCheck3(self):
        # Run the actual test in a "clean" Python interpreter
        q = Queue()
        p = Process(target=do_uiCheck3, args=(q,))
        p.start()
        enabled = q.get()
        p.join()
        self.assertFalse(enabled)


def do_uiCheck3(q):
    sw = SettingsWidget()
    q.put(sw.cbEnable.isEnabled())


# Main
# ====
# Run the unit tests in this file.
if __name__ == '__main__':
    unittest.main()
