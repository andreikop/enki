"""
Constants for pluginmanager plugin
"""

import os
from enki.core.defines import CONFIG_DIR

# use userplugins to differentiate from plugins namespace that come with enki
PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')
PLUGINS_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'plugins.svg')
INSTALL_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'document-new.svg')
DOWNLOAD_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'run-install.svg')
SPINNER_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'spinner.gif')
REPO = "https://raw.githubusercontent.com/rockiger/enki-plugin-repository/master/repository.json"
TMP = "/tmp" #TODO make platformindependent
