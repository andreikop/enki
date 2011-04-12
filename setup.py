#!/usr/bin/env python

from distutils.core import setup

setup(name='mksv3',
            version='1.0',
            packages=['mks', 'mks/core', 'mks/plugins', 'mks/_3rdparty', 'mks/resources'],
            package_data={'mks' : ['ui/*.ui', 'config/*.cfg']},
            scripts=['./mksv3']
            )
