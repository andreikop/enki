# .. -*- coding: utf-8 -*-
#
# ************************************************************************
# import_fail.py - A module to cause the import of a given module to fail.
# ************************************************************************
# Typically for use in unit tests.

# Imports
# =======
# Library imports
# ---------------
# Allow us to replace the built-in import statement / __import__ function.
import __builtin__
# For testing
import unittest


# ImportFail class
# ================
# This context manager class returns an ImportError when a given
# module is imported, allowing everything else to import normally.
# Typical usage::
#
#  with ImportFail('PythonModule'):
#    import PythonModule # Raises ImportError.
#
# Implementation notes: Coding this using contextmanager works, but
# requires messier code (specifially, a try/finally that feels
# unnecessary). A trial implementation::
#
#    from contextlib import contextmanager
#
#    @contextmanager
#    def import_fail(fail_name):
#        def import_mock(name, *args):
#            if name == fail_name:
#                raise ImportError
#            return orig_import(name, *args)
#
#        # Store original __import__
#        orig_import = __builtin__.__import__
#        __builtin__.__import__ = import_mock
#        # Run code which produces and ImportError on import fail_name.
#        # Make sure our cleanup gets run.
#        try:
#            yield
#        finally:
#            __builtin__.__import__ = orig_import
class ImportFail(object):

    def __init__(self,
      # A string, giving the name of the module whose import will
      # fail.
      fail_name):
        self.fail_name = fail_name

    # Store the original ``__import__`` function, replacing it with
    # a mock which fails on import ``self.fail_name``.
    def __enter__(self):
        self.orig_import = __builtin__.__import__
        __builtin__.__import__ = self.import_mock

    # Act like ``__import__``, except raise *ImportError* if
    # ``self.fail_name`` is imported.
    def import_mock(self, name, *args, **kwargs):
        if name == self.fail_name:
            raise ImportError
        return self.orig_import(name, *args, **kwargs)

    # Restore the origianl import function when leaving the context
    # manager.
    def __exit__(self, *args):
        __builtin__.__import__ = self.orig_import