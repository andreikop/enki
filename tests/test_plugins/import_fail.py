# .. -*- coding: utf-8 -*-
#
# ************************************************************************
# import_fail.py - A module to cause the import of a given module to fail.
# ************************************************************************
# Typically for use in unit tests.
#
# Imports
# =======
# Library imports
# ---------------
# Allow us to `replace
# <https://docs.python.org/2/library/functions.html#__import__>`_ the built-in
# import statement / __import__ function.
import __builtin__

# ImportFail class
# ================
# This `context manager
# <https://docs.python.org/2.7/reference/datamodel.html#context-managers>`_
# class returns an ImportError when a given module is imported, allowing
# everything else to import normally. Typical usage:
#
#  .. Note: This and the :: cause the following code to be indented, so it's
#     clearly not part of the program in the HTML version of this file.
#
#  ::
#
#   with ImportFail('PythonModule'):
#     import PythonModule # Raises ImportError.
#
# Implementation notes: Coding this using `contextmanager
# <https://docs.python.org/2.7/library/contextlib.html>`_ works, but
# requires messier code (specifially, a try/finally that feels
# unnecessary). A trial implementation:
#
#  .. Note: This and the :: cause the following code to be indented, so it's
#     clearly not part of the program in the HTML version of this file.
#
#  ::
#
#   from contextlib import contextmanager
#
#   @contextmanager
#   def import_fail(fail_name):
#       def import_mock(name, *args):
#           if name == fail_name:
#               raise ImportError
#           return orig_import(name, *args)
#
#       # Store original __import__
#       orig_import = __builtin__.__import__
#       __builtin__.__import__ = import_mock
#       # Run code which produces and ImportError on import fail_name.
#       # Make sure our cleanup gets run.
#       try:
#           yield
#       finally:
#           __builtin__.__import__ = orig_import
#
# This is what I consider a cleaner implementation.
class ImportFail(object):

    def __init__(self,
      # Strings, giving the name of the module whose import will
      # fail.
      *fail_names):
        self.fail_names = fail_names

    # When entering the ``with`` clause, store the original ``__import__``
    # function, replacing it with a ``import_hook`` below which fails when
    # importing ``self.fail_names``.
    def __enter__(self):
        self.orig_import = __builtin__.__import__
        __builtin__.__import__ = self.import_hook

    # Act like ``__import__``, except raise *ImportError* if
    # ``self.fail_names`` is imported.
    def import_hook(self, name, *args, **kwargs):
        if name in self.fail_names:
            raise ImportError
        return self.orig_import(name, *args, **kwargs)

    # Restore the original import function when leaving the context
    # manager.
    def __exit__(self, *args):
        __builtin__.__import__ = self.orig_import
