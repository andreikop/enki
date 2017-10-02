"""
Constants for pluginmanager plugin
"""

import os
from enki.core.defines import CONFIG_DIR

# use userplugins to differentiate from plugins namespace that come with enki
PLUGIN_DIR_PATH = os.path.join(CONFIG_DIR, 'userplugins')
ICON_PATH = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'icon.svg')
