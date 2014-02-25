"""
Enki. A text editor for programmers
Windows entry point. See also enki.py
"""

import sys
import os.path

"""
When script is executed from the source tree, it shall import enki package, which is one level higher.
First item in sys.path points to script location
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import enki.main

if __name__ == '__main__':
    sys.exit(enki.main.main())
