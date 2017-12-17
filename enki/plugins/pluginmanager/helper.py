"""Helper functions for the pluginmanager plugin"""

import os
import shutil
import urllib.request
import json
import zipfile
import pkgutil
import importlib
import logging

from enki.core.core import core
from .constants import PLUGIN_DIR_PATH, REPO

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
        logging.warning("Could not find module %s. Did not delete anything." %
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


def isPluginInstalled(name, lope):
    """String ListOfUserpluginEntry -> Bool
    Consumes a plugin name and a list of pluginEntrys
    returns the plugin if ListOfUserpluginEntry has PluginEntry
            with pluginname name
    """
    for pluginEntry in lope:
        if pluginEntry["pluginname"] == name:
            return pluginEntry
    return False


def getRepo():
    """Void -> Dictionary
    Loads the repo from https://github.com/rockiger/enki-plugin-repository/
    and returns it as a dictionary"""
    url = urllib.request.urlopen(REPO)
    rawData = url.read().decode()
    repo = json.loads(rawData)
    logging.debug(repo)
    return repo


def downloadPlugin(url, tmpPath):
    """String String -> bool
    Consumes the url of a plugin archive and the path to save it
    return True if download succeeded, else False"""
    try:
        request = urllib.request.urlretrieve(url, tmpPath)
        logging.debug(request)
    except Exception as e:
        logging.exception("The download could not finish.")
        return False
    else:
        logging.info("The plugin has been downloaded")
        return tmpPath


def extractPlugin(filePath):
    """String -> Bool
    Consumes the filePath of a plugin archive and extracts it to the
    userplugins-directory, return True if extract succeeded, els False"""
    try:
        zipref = zipfile.ZipFile(filePath, 'r')
        zipref.extractall(PLUGIN_DIR_PATH)
        zipref.close()
    except Exception as e:
        logging.exception("Could not extract plugin")
        os.remove(filePath)
        return False
    else:
        logging.info("Plugin extracted")
        os.remove(filePath)
        logging.info("Plugin deleted")
        return True


def renamePluginFolder(oldName, newName):
    """String String -> Bool
    Consumes the oldName and NewName of a plugin folder and renames it in the
    userplugins-directory, return True if rename succeeded, else False"""
    try:
        os.rename(os.path.join(PLUGIN_DIR_PATH, oldName),
                  os.path.join(PLUGIN_DIR_PATH, newName))
    except Exception as e:
        logging.exception("Could not rename plugin directory")
        return False
    else:
        logging.info("Plugin directory renamed to %s." % newName)
        return True


def getPlugins():
    """Loads all userplugins and returns them as a ListOfUserpluginEntry"""
    userPlugins = []
    for loader, name, isPackage in pkgutil.iter_modules([PLUGIN_DIR_PATH]):
        if not inUserPlugins(name, userPlugins):
            userPlugin = getPlugin(name)
            if userPlugin:
                userPlugins.append(userPlugin)
    return userPlugins


def getPlugin(name):
    """ get plugin by it's module name and returns userpluginEntry
    """
    module = importlib.import_module('userplugins.%s' % name)
    try:
        pluginEntry = create_UE(
            module,
            shouldPluginLoad(name),
            name,
            module.__pluginname__,
            module.__author__,
            module.__version__,
            module.__doc__)
        return pluginEntry
    except AttributeError:
        logging.exception("Plugin %s misses required attributes." % name)
        return False


def initPlugins():
    """Loads all userplugins and returns them as a ListOfUserpluginEntry"""
    userPlugins = getPlugins()
    for up in userPlugins:
        loadPlugin(up)
    return userPlugins


def initPlugin(name):
    """Load plugin by it's module name
    returns userpluginEntry
    """
    return loadPlugin(getPlugin(name))


def shouldPluginLoad(name):
    """Consumes a name of a plugin and checks in the settings if it should
    be loaded.
    If no setting is available for the plugin, it gets created.
    Returns the setting (Bool)
    """
    if name not in core.config()["PluginManager"]["Plugins"]:
        core.config()["PluginManager"]["Plugins"][name] = {}
    if "Enabled" not in core.config()["PluginManager"]["Plugins"][name]:
        core.config()["PluginManager"]["Plugins"][name]["Enabled"] = False
    return core.config()["PluginManager"]["Plugins"][name]["Enabled"]
