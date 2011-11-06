#!/usr/bin/env python

import os
import sys
from mks.core.defines import PACKAGE_NAME, PACKAGE_VERSION 

from distutils.core import setup

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

setup(name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description='Next generation Unix code editor',
        long_description='TODO write long description',
        author='Andrei Kopats',
        author_email='hlamer@tut.by',
        url='www.monkeystudio.org',
        download_url='TODO write download URL',
        packages=['mks', 'mks/core', 'mks/plugins', 'mks/resources'],
        package_data={'mks' : ['ui/*.ui', 'config/*.cfg']},
        scripts=['./mksv3'],
        data_files=data_files,
        command_packages='stdeb.command'
        )
# TODO classifiers!
