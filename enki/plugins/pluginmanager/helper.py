"""Helper functions for the pluginmanager plugin"""

import os
import shutil
from enki.core.core import core
from .constants import PLUGIN_DIR_PATH

# Data Definitions
# ==================
# userpluginEntry consist of
# {'module': Module
#  'plugin': Plugin or None,
#  'isloaded': Bool,
#  'name': String,
#  'author': String,
#  'version': String,
#  'doc': String}
#
# ListOfUserpluginEntry is one of:
# - []
# - lou.append(userpluginEntry)


def create_UE(module, isLoaded, modulename, pluginname,
              author, version, doc, plugin=None):
    """Create a new userpluginEntry"""
    return {'module': module,
            'plugin': plugin,
            'isLoaded': isLoaded,
            'modulename': modulename,
            'pluginname': pluginname,
            'author': author,
            'version': version,
            'doc': doc}


def loadPlugin(pluginEntry):
    """Consume a pluginEntry and load the plugin into core._loadedPlugins,
    based on it's 'isLoaded' property
    return pluginEntry
    """
    if pluginEntry['isLoaded'] is True:
        pluginEntry['plugin'] = pluginEntry['module'].Plugin()
        core.loadedPlugins().append(pluginEntry['plugin'])
    return pluginEntry


def unloadPlugin(pluginEntry):
    """Consume a pluginEntry and unload the plugin from core._loadedPlugins,
    based on it's 'isLoaded' property
    return pluginEntry
    """
    if pluginEntry['isLoaded'] is False and \
       pluginEntry['plugin'] is not None:
        idx = core.loadedPlugins().index(pluginEntry['plugin'])
        plugin = core.loadedPlugins().pop(idx)
        plugin.terminate()
        pluginEntry['plugin'] = None
    return pluginEntry


def deletePlugin(pluginEntry):
    """Consume a pluginEntry and delete the plugin directory or file"""
    unloadPlugin(pluginEntry)
    dirpath = os.path.join(PLUGIN_DIR_PATH, pluginEntry["modulename"])
    filepath = os.path.join(PLUGIN_DIR_PATH, pluginEntry["modulename"] + '.py')
    if os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
    elif os.path.exists(filepath):
        os.remove(filepath)
    else:
        print("Could not find module %s. Did not delete anything." %
              pluginEntry["modulename"])


def inUserPlugins(modulename, lope):
    """String ListOfUserpluginEntry -> Bool
    Consumes a modulename and a list of pluginEntrys
    return True if ListOfUserpluginEntry has PluginEntry with modulename
    """
    for pluginEntry in lope:
        if pluginEntry["modulename"] == modulename:
            return True
    return False
