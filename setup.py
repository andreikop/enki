#!/usr/bin/env python

import os
import sys
import pkgutil

""" setuptools ignores my .desktop and .cfg files
try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup
"""
from distutils.core import setup

from mks.core.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_URL

"""hlamer: A bit hacky way to exclude desktop files from distribution,
but, I don't know how to do it better in crossplatform way
"""
def isWinDist():
    for arg in sys.argv:
        if arg.startswith('--format') and \
           ('wininst' in arg or \
            'msi' in arg):
               return True
    return False

if (('install' in sys.argv or \
     'install_data' in sys.argv) and \
        os.name != 'posix') or \
    'bdist' in sys.argv and isWinDist() or \
    'bdist_winints' in sys.argv or \
    'bdist_msi' in sys.argv:
        data_files = []
else:
    data_files=[('/usr/share/applications/', ['mksv3.desktop']),
                ('/usr/share/pixmaps/', ['icons/xpm/mksv3.xpm'])]

classifiers = ['Development Status :: 3 - Alpha',
               'Environment :: X11 Applications :: Qt',
               'Intended Audience :: Developers',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Natural Language :: English',
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Topic :: Software Development',
               'Topic :: Text Editors :: Integrated Development Environments (IDE)'
               ]

long_description = \
"""Some of features:

 * Syntax highlighting for more than 30 languages
 * Bookmarks
 * Search and replace functionality for files and directories. Regular expressions are supported
 * File browser
 * Autocompletion, based on document contents
 * Hightly configurable
"""

packages=['mks',
          'mks/core',
          'mks/lib',
          'mks/fresh',
          'mks/fresh/actionmanager',
          'mks/fresh/dockwidget',
          'mks/fresh/models',
          'mks/fresh/queuedmessage',
          'mks/plugins',
          'mks/resources']

package_data={'mks' : ['ui/*.ui',
                       'ui/plugins/*.ui',
                       'fresh/actionmanager/*.ui',
                       'config/*.json']
             }


for loader, name, ispkg in pkgutil.iter_modules(['mks/plugins']):
    if ispkg:
        packages.append('mks/plugins/' + name)
        package_data['mks'].append('plugins/%s/*.ui' % name)

setup(name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description='Simple programmers text editor',
        long_description=long_description,
        author='Andrei Kopats',
        author_email='hlamer@tut.by',
        url=PACKAGE_URL,
        download_url='https://github.com/hlamer/mksv3/tags',
        packages=packages,
        package_data=package_data,
        scripts=['./mksv3'],
        data_files=data_files,
        classifiers=classifiers,
        license='gpl2',
        requires=['pyparsing']
        )
