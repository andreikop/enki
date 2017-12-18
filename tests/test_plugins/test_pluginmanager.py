#!/usr/bin/env python3
import unittest
import os.path
import sys
import codecs
import shutil

sys.path.insert(0,
    os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

import base

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QPlainTextEdit, QStyle, QApplication

from enki.core.core import core
from enki.core.defines import CONFIG_DIR
from enki.plugins.pluginmanager import helper

PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')
sys.path.append(CONFIG_DIR)
sys.path.append(PLUGIN_DIR_PATH)

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
_EMPTY_FILETEXT = """"""
REPO = "https://raw.githubusercontent.com/rockiger/enki-plugin-repository/master/test-repository.json"
CONFIG = {"PluginManager": {
            "Plugins": {
                "testplugin0": {
                    "Enabled": True
                },
                "testplugin1": {
                    "Enabled": True
                },
                "testplugin3": {
                    "Enabled": True
                    }
                }
            }
        }




class _BaseTestCase(base.TestCase):

    def setUp(self):
        super().setUp()


class TestHelperCase(_BaseTestCase):
    """Test the PluginsPage if plugins really suffies the requirements in the userplugins directory."""

    def tearDown(self):
        deleteTmpUserplugins()

    @base.inMainLoop
    def testGetPluginsNoPlugin(self):
        """Test if bad plugin get's not loaded if it is copied to
        ~/.config/enki/userplugins after the enki is started"""
        pluginCountBefore = helper.getPlugins(PLUGIN_DIR_PATH)
        self.assertEqual(pluginCountBefore, [])

    @base.inMainLoop
    def testGetPluginsBadPlugin(self):
        """Test if bad plugin get's not loaded if it is copied to
        ~/.config/enki/userplugins after the enki is started"""
        pluginCountBefore = helper.getPlugins(PLUGIN_DIR_PATH)
        createPlugin(filetext=_EMPTY_FILETEXT)
        self.assertEqual(pluginCountBefore, [])

    @base.inMainLoop
    def testGetPluginsOnePlugin(self):
        """Test if bad plugin get's not loaded if it is copied to
    ~/.config/enki/userplugins after the enki is started"""
        createPlugin()
        pluginCountBefore = helper.getPlugins(PLUGIN_DIR_PATH)
        self.assertEqual(len(pluginCountBefore), 1)

    @base.inMainLoop
    def testGetPLuginsTwoPlugins(self):
        """Test if bad plugin get's not loaded if it is copied to
        ~/.config/enki/userplugins after the enki is started"""
        createPlugin(num=0)
        createPlugin(num=1)
        pluginCountBefore = helper.getPlugins(PLUGIN_DIR_PATH)
        self.assertEqual(len(pluginCountBefore), 2)

    def testGetRepo(self):
        repo = helper.getRepo(REPO)
        self.assertEqual(repo, {'plugins': [{'name': 'Autosave', 'description': 'Saves all files when Enki loses focus.', 'details': 'https://github.com/rockiger/enkiautosave', 'download': 'https://github.com/rockiger/enkiautosave/archive/0.0.1.zip', 'author': 'Marco Laspe', 'version': '0.0.1', 'labels': ['theme', 'file', 'icons']}, {'name': 'Bracket Matcher', 'description': 'Autocompletes open brackets like [], (), {}, "", \'\', “”, ‘’, «», ‹›, and ``.', 'details': 'https://github.com/rockiger/enkibracketmatcher', 'download': 'https://github.com/rockiger/enkibracketmatcher/archive/0.0.1.zip', 'author': 'Marco Laspe', 'version': '0.0.1', 'labels': ['theme', 'file', 'icons']}, {'name': 'Fileswitcher', 'description': 'Switch through your files in the style of the Opera web browser.', 'details': 'https://github.com/rockiger/enkifileswitcher', 'download': 'https://github.com/rockiger/enkifileswitcher/archive/0.0.1.zip', 'author': 'Marco Laspe', 'version': '0.0.1', 'labels': ['theme', 'file', 'icons']}, {'name': 'Test Plugin', 'description': 'Test the plugin for enki pluginmanager install functionality', 'details': 'https://github.com/rockiger/enkitestplugin', 'download': 'https://github.com/rockiger/enkitestplugin/archive/0.1.1.zip', 'author': 'Test Programmer', 'version': '0.1.1', 'labels': ['theme', 'file', 'icons']}]})

    def testDownloadPlugin(self):
        path = os.path.join(CONFIG_DIR, "testdownload1.zip")
        testpath = helper.downloadPlugin("https://github.com/rockiger/enkitestplugin/archive/0.1.1.zip", path)
        self.assertEqual(path, testpath)
        os.remove(path)
        testpath = helper.downloadPlugin("http://nelnirslghen.vnghclnr", path)
        self.assertFalse(testpath)


class EmptyPluginsPage(_BaseTestCase):
    """Test the PluginsPage if no plugin is in the userplugins directory."""

    def setUp(self):
        self._EMPTY_USERPLUGINS = []
        super().setUp()

    def tearDown(self):
        deleteTmpUserplugins()
        super().tearDown()

    def testOpenPage(self):
        """Test if information on Pluginspage is present"""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            page.update(self._EMPTY_USERPLUGINS)
            introLabel = \
                page.children()[0].children()[0].children()[0].children()[1]
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
        createPlugin()
        import testplugin0
        print (testplugin0.Plugin)
        self._ONE_USERPLUGINS = [{'module': testplugin0,
                                  'plugin': None,
                                  'isLoaded': False,
                                  'modulename': 'testplugin0',
                                  'pluginname': 'Testplugin',
                                  'author': 'Test Author',
                                  'version': '0.0.0',
                                  'doc': 'Docstring of Testplugin'}]
        super().setUp()

    def tearDown(self):
        deleteTmpUserplugins()
        super().tearDown() # otherwise we get an ValueError in core.term()

    def testOpenPage(self):
        """Test if information on Pluginspage is present"""
        def continueFunc(dialog):
            page = dialog._pageForItem["Plugins"]
            item = dialog._itemByPath(["Plugins"])
            item.setSelected(True)
            page.update(self._ONE_USERPLUGINS)
            introLabel = \
                page.children()[0].children()[0].children()[0].children()[1]

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

            page.update(self._ONE_USERPLUGINS)
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
            self.assertEqual(
                "testplugin0",
                core.loadedPlugins()[-1].__module__,
                'Last module name should be userplugins.testplugin0')

            lenBeforeClick = len(core.loadedPlugins())
            QTest.mouseClick(enableBtn, Qt.LeftButton)
            self.assertEqual("Enable", enableBtn.text(),
                             "Buttontext differs from Enable")
            self.assertFalse(enableBtn.isDown(), 'Button should not be down')
            self.assertEqual(
                lenBeforeClick - 1,
                len(core.loadedPlugins()),
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

            page.update(self._ONE_USERPLUGINS)
            titleCard = \
                page.children()[0].children()[0].children()[0].children()[2]
            enableBtn = titleCard.children()[2].children()[2].buttons()[0]
            cancelButton = dialog.children()[3].children()[2]

            QTest.mouseClick(enableBtn, Qt.LeftButton)
            lenBeforeDelete = len(core.loadedPlugins())
            titleCard._uninstallPlugin()
            self.assertEqual(
                lenBeforeDelete - 1,
                len(core.loadedPlugins()),
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

def get_pluginmanager():
    for plugin in core.loadedPlugins():
        if "pluginmanager" in str(plugin):
            return plugin

def createPlugin(num=0, filetext=_FILETEXT):
    """Delete the testplugin directory, optional parameter for different naming
    """
    dirpath = os.path.join(PLUGIN_DIR_PATH, 'testplugin%i' % num)
    filepath = os.path.join(dirpath, "__init__.py")

    if not os.path.exists(filepath):
        os.makedirs(dirpath)
    with codecs.open(filepath, 'wb', encoding='utf8') as file_:
        file_.write(filetext)


def deletePlugin(num=0):
    """Delete the testplugin directory, optional parameter for different naming
    """
    pluginname = 'testplugin%i' % num
    dirpath = os.path.join(PLUGIN_DIR_PATH, pluginname)
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    else:
        print("Could not find module %s. Did not delete anything."
              % pluginname)

def deleteTmpUserplugins():
    if os.path.isdir(PLUGIN_DIR_PATH):
        shutil.rmtree(PLUGIN_DIR_PATH)

if __name__ == '__main__':
    unittest.main()
    deleteTmpUserplugins()
