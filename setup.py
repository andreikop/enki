#!/usr/bin/env python

from distutils.core import setup

setup(name='mksv3',
            version='1.0',
            packages=['mks'],
            package_data={'mks' : ['mks/*.ui']},
            scripts=['./mksv3']
            )
