"""
Enki: a text editor for programmers.
This is the Windows entry point. See also enki.
"""

import sys

"""
When this script is executed from the source tree, it should first
try to import the enki package, which is one level higher. If that
fails, assume it's being run as a standalong script, so import
the enki package from the standard library.
"""
try:
    # Look one directory up for the enki package by using a relative import.
    from ..enki.main import main
    # One failure mode: "ValueError: Attempted relative import in non-package".
    # Can't seem to trigger an ImportError, but leaving it in to be safe.
except (ImportError, ValueError):
    # In this case, we're running from the standard library. DON'T use allow the
    # working directory in the Python path, since enki.py will be searched for
    # main, rather than the enki package. To do this, drop the first entry of
    # the system path, which is '', telling python to first look in the current
    # directory when doing an import.
    sys.path.pop(0)
    from enki.main import main

if __name__ == '__main__':
    sys.exit(main())
