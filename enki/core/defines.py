"""
File contains some volatile info, such as version, release date and authors
"""
import sys
import os.path

PACKAGE_NAME = "Enki"
PACKAGE_ORGANISATION = "Andrei Kopats"
PACKAGE_URL = "https://enki-editor.org"
PACKAGE_VERSION = "13.11.1"
PACKAGE_COPYRIGHTS = "(C) 2013 Andrei KOPATS"

QUTEPART_SUPPORTED_MAJOR = 1
QUTEPART_SUPPORTED_MINOR = 2

# Choose base config dir according to http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
if os.environ.get('XDG_CONFIG_HOME', ''):  # if set and not empty
    xdg_config_home = os.environ['XDG_CONFIG_HOME']
else:
    xdg_config_home = os.path.expanduser('~/.config/')

if os.path.isdir(xdg_config_home):
    CONFIG_DIR = os.path.join(xdg_config_home, 'enki')
else:
    CONFIG_DIR = os.path.expanduser('~/.enki/')
