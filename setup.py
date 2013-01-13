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

import distutils.ccompiler
from distutils.core import setup, Extension

from enki.core.defines import PACKAGE_NAME, PACKAGE_VERSION, PACKAGE_URL

# probably will add flags later. Always True now
installQutepart = True

def _checkDependencies():
    """Check if 3rdparty software is installed in the system.
    Notify user, how to install it
    """
    _SEE_SITE_PLAIN = 'See http://enki-editor.org/install-sources.html'
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
    
    if installQutepart:
        compiler = distutils.ccompiler.new_compiler()
        if not compiler.has_function('pcre_version', includes = ['pcre.h'], libraries = ['pcre']):
            print "Failed to find pcre library."
            print "\tTry to install libpcre{version}-dev package, or go to http://pcre.org"
            print "\tIf not standard directories are used, set CFLAGS and LDFLAGS environment variables"
            ok = False

    if not ok:
        print 'See http://enki-editor.org/install-sources.html'

    return ok


"""Install .desktop and .xpm and .desktop only on linux. (Shall we do it on 
hlamer: We should use relative pathes here, without /usr/, so it will be installed to
/usr/local/share with setup.py and to /usr/share with Debian packages.
BUT KDE4 on Suse 12.02 ignores data in /usr/local/share, and, probably, some other systems do
Therefore Enki always installs its .desktop and icons to /usr/share
"""

if sys.platform.startswith('linux2') or \
   'sdist' in sys.argv or \
   'upload' in sys.argv:
    data_files=[('/usr/share/applications/', ['enki.desktop']),
                ('/usr/share/pixmaps/', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/32x32/apps', ['icons/logo/32x32/enki.png']),
                ('/usr/share/icons/hicolor/48x48/apps', ['icons/logo/48x48/enki.png']),
                ('/usr/share/icons/hicolor/scalable/apps', ['icons/logo/enki.svg'])
                ]
else:
    data_files = []

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

ext_modules = []

if installQutepart:
    packages += ['qutepart',
                 'qutepart/syntax']

    package_dir.update({'qutepart': 'qutepart/qutepart',
                        'qutepart/syntax': 'qutepart/qutepart/syntax'})
    
    package_data.update({ 'qutepart/qutepart/syntax' : ['data/*.xml',
                                                        'data/syntax_db.json']})
    
    ext_modules.append(Extension('qutepart.syntax.cParser',
                                 sources = ['qutepart/qutepart/syntax/cParser.c'],
                                 libraries = ['pcre']))

if __name__ == '__main__':
    if 'install' in sys.argv or 'build' in sys.argv or 'build_ext' in sys.argv:
        if not '--force' in sys.argv and not '--help' in sys.argv:
            if not _checkDependencies():
                sys.exit(-1)

    if not '--force' in sys.argv and not '--help' in sys.argv:
        if not os.listdir('qutepart'):
            print "qutepart directory is empty. It seems like you haven't not fetched its contents. Run"
            print "    git submodule init"
            print "    git submodule update"
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
            scripts=['bin/enki'],
            data_files=data_files,
            classifiers=classifiers,
            license='gpl2',
            requires=['pyparsing'],
            ext_modules = ext_modules
         )
