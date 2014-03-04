"""
Enki: a text editor for programmers.
This is the Windows entry point. See also enki.
"""

import sys
import os.path

"""
When this script is executed from the source tree, it should first
try to import the enki package, which is one level higher. If that
fails, assume it's being run as a standalong script, so import
the enki package from the standard library.
"""

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Look one directory up for the enki package by using a relative import.
    from enki.main import main
    # One failure mode: "ValueError: Attempted relative import in non-package".
    # Can't seem to trigger an ImportError, but leaving it in to be safe.
except (ImportError, ValueError):
    # In this case, we're running from the standard library. DON'T allow the
    # working directory in the Python path, since enki.py will be searched for
    # main, rather than the enki package. To do this, drop the
    # '' entry, which tells python to first look in the current
    # directory when doing an import.
    #
    try:
        sys.path.remove('')
    except ValueError:
        pass


if __name__ == '__main__':
    sys.exit(main())
