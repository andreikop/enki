"""
Constants for pluginmanager plugin
"""

import os
from enki.core.defines import CONFIG_DIR

# use userplugins to differentiate from plugins namespace that come with enki
PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')
PLUGINS_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'icon.svg')
INSTALL_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'plus.svg')
DOWNLOAD_ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'download.svg')
REPO = "https://raw.githubusercontent.com/rockiger/enki-plugin-repository/master/repository.json"
