# ***************
# sphinx-build.py
# ***************
# A short script to create a Sphinx binary using Pyinstaller. See
# ``enki-sphinx.spec`` for more details.
#
# This code was copied from the last line of ``sphinx.__init__``.
import sys, sphinx
sys.exit(sphinx.main(sys.argv))
