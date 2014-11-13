# .. -*- coding: utf-8 -*-
#
# *****************************************************************
# rthook_sys_file_encoding.py - Supply a valid system file encoding
# *****************************************************************
#
# On Linux, PyInstaller mis-detects the system file encoding, producing
# a value of None. This confuses docutils. Supply something reasonable
# instead.
#
# This is a bug: see
# https://github.com/pyinstaller/pyinstaller/issues/446 and
# https://www.mail-archive.com/pyinstaller@googlegroups.com/msg06497.html.
# It occurs under PyInstaller 2.1 dev, revision
# 5566202849dac86ac5deb3366bf152d0245e65ac

import sys


if not sys.getfilesystemencoding():
    sys.getfilesystemencoding = lambda: 'UTF-8'
    
