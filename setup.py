#!/usr/bin/env python

from distutils.core import setup

setup(name='mksv3',
            version='1.0',
            packages=['mks'],
            data_files=[('share/mksv3', ['mks/pOpenedFileExplorer.ui', 'mks/SearchWidget.ui'])],
            scripts=['./mksv3']
            )
