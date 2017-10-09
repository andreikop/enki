#!/usr/bin/env python3
import unittest
import os.path
import sys
import codecs
import shutil

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QPlainTextEdit, QStyle, QApplication

from enki.core.core import core
from enki.core.defines import CONFIG_DIR

PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')

class _BaseTestCase(base.TestCase):

    def setUp(self):
        super().setUp()

class EmptyPluginsPage(_BaseTestCase):
    """Test the PluginsPage if no plugin is in the userplugins directory."""

    def testOpenPage(self):
        """Test if information on Pluginspage is present"""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            introLabel = page.children()[0].children()[0].children()[0].children()[1]
            userPlugins =  page._userPlugins
            self.assertEqual(len(userPlugins), 0)
            self.assertNotEqual(
                introLabel.text().find("<code>0</code>"),
                -1)
            self.assertNotEqual(
                introLabel.text().find(PLUGIN_DIR_PATH),
                -1)
            QTest.keyClick(dialog, Qt.Key_Enter)
        self.openSettings(continueFunc)


class OnePluginPluginsPage(_BaseTestCase):
    """Test the PluginsPage if one plugin is in the userplugins directory."""

    def setUp(self):
        self._createPlugin()
        super().setUp()

    def _createPlugin(self, num=0):
        """Delete the testplugin directory, optional parameter for different naming
        """
        dirpath = os.path.join(PLUGIN_DIR_PATH, 'testplugin%i' % num)
        filepath = os.path.join(dirpath, "__init__.py")

        if not os.path.exists(filepath):
            os.makedirs(dirpath)
        with codecs.open(filepath, 'wb', encoding='utf8') as file_:
            file_.write(_FILETEXT)

    def tearDown(self):
        self._deletePlugin()
        #super().tearDown()

    def _deletePlugin(self, num=0):
        """Delete the testplugin directory, optional parameter for different naming
        """
        pluginname = 'testplugin%i' % num
        dirpath = os.path.join(PLUGIN_DIR_PATH, pluginname)
        if os.path.isdir(dirpath):
            shutil.rmtree(dirpath)
        else:
            print("Could not find module %s. Did not delete anything."
                  % pluginname)

    def testOpenPage(self):
        """Test if information on Pluginspage with one plugin is present"""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            introLabel = \
                page.children()[0].children()[0].children()[0].children()[1]
            userPlugins = page._userPlugins
            self.assertEqual(len(userPlugins), 1)
            self.assertNotEqual(
                introLabel.text().find("<code>1</code>"),
                -1)
            self.assertNotEqual(
                introLabel.text().find(PLUGIN_DIR_PATH),
                -1)
            QTest.keyClick(dialog, Qt.Key_Enter)

        self.openSettings(continueFunc)

    def testPluginEnables(self):
        """Test if the plugin get's loaded after the user clicks on
        the Enable button of the test plugin and unloaded again after
        the next click"""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            titleCard = \
                page.children()[0].children()[0].children()[0].children()[2]
            enableBtn = titleCard.children()[2].children()[2].buttons()[0]
            self.assertEqual("Enable", enableBtn.text(),
                "Buttontext differs from Enable")
            self.assertFalse(enableBtn.isDown(), 'Button should not be down')

            QTest.mouseClick(enableBtn, Qt.LeftButton)
            self.assertEqual("Disable", enableBtn.text(),
                "Buttontext differs from Disable")
            self.assertTrue(enableBtn.isDown(), 'Button should be down')
            self.assertEqual("userplugins.testplugin0",
                core.loadedPlugins()[-1].__module__,
                'Last module name should be userplugins.testplugin0')

            lenBeforeClick = len(core.loadedPlugins())
            QTest.mouseClick(enableBtn, Qt.LeftButton)
            self.assertEqual("Enable", enableBtn.text(),
                "Buttontext differs from Enable")
            self.assertFalse(enableBtn.isDown(), 'Button should not be down')
            self.assertEqual(lenBeforeClick - 1, len(core.loadedPlugins()),
                "Length of loaded plugins should be one fewer after undload.")

            QTest.keyClick(dialog, Qt.Key_Escape)
        self.openSettings(continueFunc)

    def testPluginDelete(self):
        """Test if the plugin get's unloaded after the user clicks on
        the Delete button of the test plugin and deleted."""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            titleCard = \
                page.children()[0].children()[0].children()[0].children()[2]
            enableBtn = titleCard.children()[2].children()[2].buttons()[0]
            uninstallBtn = titleCard.children()[2].children()[2].buttons()[1]
            cancelButton = dialog.children()[3].children()[2]

            QTest.mouseClick(enableBtn, Qt.LeftButton)
            lenBeforeDelete = len(core.loadedPlugins())
            titleCard._uninstallPlugin()
            self.assertEqual(lenBeforeDelete - 1, len(core.loadedPlugins()),
                'Plugins should be one fewer after uninstall.')
            self.assertFalse(titleCard._pluginEntry['isLoaded'],
                'Plugin should not be loaded anymore')
            name = titleCard._pluginEntry['modulename']
            self.assertFalse(
                core.config()["PluginManager"]["Plugins"][name]["Enabled"],
                'Plugin should not be enabled in enki config')
            dirpath = os.path.join(PLUGIN_DIR_PATH, 'testplugin0')
            self.assertFalse(os.path.exists(dirpath),
                'Plugin directory should not exist')
            QTest.mouseClick(cancelButton, Qt.LeftButton)

        self.openSettings(continueFunc)


_FILETEXT = """
\"\"\"Docstring of Testplugin\"\"\"
__author__ = "Test Author"
__pluginname__ = "Testplugin"
__copyright__ = "Copyright Yoar"
__credits__ = ["Test Author", "Test Author1", "Test Author2"]
__license__ = "GPL3"
__version__ = "0.0.0"
__maintainer__ = "Test Maintainer"
__email__ = "test@test.com"
__status__ = "Testing"

class Plugin:
    def __init__(self):
        pass
    def terminate(self):
        pass
"""

if __name__ == '__main__':
    unittest.main()
