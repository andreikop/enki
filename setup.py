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

def _checkDepencencies():
    """Check if 3rdparty software is installed in the system.
    Notify user, how to install it
    """
    _SEE_SITE_PLAIN = 'See https://github.com/hlamer/mksv3/wiki/source-installation-instructions'
    ok = True
    try:
        import PyQt4
    except ImportError, ex:
        print 'Failed to import Qt4 python bindings:'
        print '\t' + str(ex)
        ok = False

    try:
        import PyQt4.Qsci
    except ImportError, ex:
        print "Failed to import QScintilla 2 python bindings:"
        print '\t' + str(ex)
        ok = False

    try:
        import pyparsing
    except ImportError, ex:
        print "Failed to import pyparsing:"
        print '\t' + str(ex)
        ok = False
    
    if not ok:
        print 'See https://github.com/hlamer/mksv3/wiki/source-installation-instructions'

    return ok

"""hlamer: A bit hacky way to exclude desktop files from distribution,
but, I don't know how to do it better in crossplatform way
"""
def _isWinDist():
    for arg in sys.argv:
        if arg.startswith('--format') and \
           ('wininst' in arg or \
            'msi' in arg):
               return True
    return False

#  Install .desktop and .xpm and .desktop only on unixes
if (('install' in sys.argv or \
     'install_data' in sys.argv) and \
        os.name != 'posix') or \
    'bdist' in sys.argv and _isWinDist() or \
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

if 'install' in sys.argv and \
    not '--force' in sys.argv:
        if not _checkDepencencies():
            sys.exit(-1)

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
