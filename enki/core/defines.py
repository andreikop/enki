"""
File contains some volatile info, such as version, release date and authors
"""
import os.path

PACKAGE_NAME = "Enki"
PACKAGE_ORGANISATION = "Andrei Kopats"
PACKAGE_URL = "https://enki-editor.org"
PACKAGE_VERSION = "21.11.0"
PACKAGE_COPYRIGHTS = "(C) 2021 Andrei KOPATS"

QUTEPART_SUPPORTED_MAJOR = 3
QUTEPART_SUPPORTED_MINOR = 0

# Choose base config dir according to http://standards.freedesktop.org/basedir-spec/basedir-spec-latest.html
if os.environ.get('XDG_CONFIG_HOME', ''):  # if set and not empty
    xdgConfigHome = os.environ['XDG_CONFIG_HOME']
else:
    xdgConfigHome = os.path.expanduser('~/.config/')

if os.path.isdir(xdgConfigHome):
    CONFIG_DIR = os.path.join(xdgConfigHome, 'enki')
else:
    CONFIG_DIR = os.path.expanduser('~/.enki/')
