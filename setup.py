#!/usr/bin/env python

import os
import sys
import pkgutil
import platform
from distutils.core import setup


from enki.core.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_URL

# NOTE setuptools ignores Enki .desktop and .cfg files


def _checkDependencies():
    """Check if 3rdparty software is installed in the system.
    Notify user, how to install it
    """
    _SEE_SITE_PLAIN = 'See http://enki-editor.org/install-sources.html'
    ok = True
    try:
        import PyQt4
    except ImportError as ex:
        print 'Failed to import Qt4 python bindings:'
        print '\t' + str(ex)
        ok = False

    try:
        import pyparsing
    except ImportError as ex:
        print "Failed to import pyparsing:"
        print '\t' + str(ex)
        ok = False

    try:
        import qutepart
    except ImportError as ex:
        print "Failed to import qutepart:"
        print '\t' + str(ex)
        ok = False

    if not ok:
        print 'See http://enki-editor.org/install-sources.html'

    return ok


def _inVenv():
    """Check if the installation is running inside a Virutalenv or Venv.
    # See http://stackoverflow.com/q/1871549/1468388
    """
    return hasattr(sys, 'real_prefix') or getattr(sys, 'base_prefix', sys.prefix) != sys.prefix


""" hlamer: We should use relative pathes here, without /usr/, so it will be installed to
/usr/local/share with setup.py and to /usr/share with Debian packages.
BUT KDE4 on Suse 12.02 ignores data in /usr/local/share, and, probably, some other systems do
Therefore Enki always installs its .desktop and icons to /usr/share
"""

if (sys.platform.startswith('linux2') and not _inVenv()) or \
   'sdist' in sys.argv or \
   'upload' in sys.argv:
    data_files=[('/usr/share/applications/', ['install/enki.desktop']),
                ('/usr/share/pixmaps/', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/32x32/apps', ['icons/logo/32x32/enki.png']),
                ('/usr/share/icons/hicolor/48x48/apps', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/scalable/apps', ['icons/logo/enki.svg'])
                ]
else:
    data_files = []

classifiers = ['Development Status :: 5 - Production/Stable',
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

packages=['enki',
          'enki/core',
          'enki/lib',
          'enki/widgets',
          'enki/plugins',
          'enki/resources',
         ]

package_dir = {}

package_data={'enki' : ['ui/*.ui',
                        'config/*.json'],
             }

for loader, name, ispkg in pkgutil.iter_modules(['enki/plugins']):
    if ispkg:
        packages.append('enki/plugins/' + name)
        package_data['enki'].append('plugins/%s/*.ui' % name)
        package_data['enki'].append('plugins/%s/*.png' % name)
        package_data['enki'].append('plugins/%s/templates/*' % name)

script = 'bin/enki.py' if platform.system() == 'Windows' else 'bin/enki'

if __name__ == '__main__':
    if 'install' in sys.argv:
        if not '--force' in sys.argv and not '--help' in sys.argv:
            if not _checkDependencies():
                sys.exit(-1)

    setup(  name=PACKAGE_NAME.lower(),
            version=PACKAGE_VERSION,
            description='Simple programmers text editor',
            long_description=long_description,
            author='Andrei Kopats',
            author_email='hlamer@tut.by',
            url=PACKAGE_URL,
            download_url='https://github.com/hlamer/enki/tags',
            packages=packages,
            package_dir = package_dir,
            package_data=package_data,
            scripts=[script],
            data_files=data_files,
            classifiers=classifiers,
            license='gpl2',
            requires=['pyparsing'],
         )
