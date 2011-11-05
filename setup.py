#!/usr/bin/env python

from mks.core.defines import PACKAGE_NAME, PACKAGE_VERSION 

from distutils.core import setup

setup(name=PACKAGE_NAME,
        version=PACKAGE_VERSION,
        description='Next generation Unix code editor',
        long_description='TODO write long description',
        author='Andrei Kopats, Filipe Azevedo',
        author_email='hlamer@tut.by',
        url='www.monkeystudio.org',
        download_url='TODO write download URL',
        packages=['mks', 'mks/core', 'mks/plugins', 'mks/resources'],
        package_data={'mks' : ['ui/*.ui', 'config/*.cfg']},
        scripts=['./mksv3']
        )
# TODO classifiers!
