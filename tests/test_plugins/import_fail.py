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
import builtins
import importlib

# ImportFail class
# ================
# This `context manager
# <https://docs.python.org/2.7/reference/datamodel.html#context-managers>`_
# class returns an ImportError when a given module is imported, allowing
# everything else to import normally. Basic usage:
#
#  .. Note: This and the :: cause the following code to be indented, so it's
#     clearly not part of the program in the HTML version of this file.
#
#  ::
#
#   with ImportFail(['PythonModule']):
#     import PythonModule # Raises ImportError.
#
# Test methods
# ------------
# This class is typically used during unit testing to check that the effects of a
# failed import are handled correctly. A naive test::
#
#  def test_sync_broken(self):
#      with ImportFail(['tre']):
#          # Reload preview_sync, which should handle a missing ``tre`` import.
#          reload(enki.plugins.preview.preview_sync)
#          # Check that preview_sync handles the missing import.
#          self.assertIsNone(enki.plugins.preview.preview_sync.findApproxTextInTarget)
#
# However, this will cause all future tests to fail, since preview_sync is now
# missing its tre import and cannot therefore run its tests. We must reload
# ``preview_sync`` again, outside the context manager. So, the assertion must be
# moved outside as well. If there are any excpetions before the reload, all the
# remaining unit tests will crash and burn::
#
#  def test_sync_ugly(self):
#      with ImportFail(['tre']):
#          # Reload preview_sync, which should handle a missing ``tre`` import.
#          reload(enki.plugins.preview.preview_sync)
#          # WE HOPE THERE ARE NO EXCEPTIONS FROM HERE UNTIL THE NEXT RELOAD!!!
#          # Check that preview_sync handles the missing import.
#          fatit = enki.plugins.preview.preview_sync.findApproxTextInTarget
#      reload(enki.plugins.preview.preview_sync)
#      self.assertIsNone(enki.plugins.preview.preview_sync.findApproxTextInTarget)
#
# **This is ugly.** So, ImportFail will do both reloads, guaranteeing that they
# happen (via context manager magic) even in the presence of exceptions, by
# passing it a set of modules to reload with the ImportFail in force, then (on
# exit) reload them again without the ImportFail in force::
#
#  def test_sync_correct(self):
#      with ImportFail(['tre'], [enki.plugins.preview.preview_sync]):
#          # Check that preview_sync handles the missing import.
#          self.assertIsNone(enki.plugins.preview.preview_sync.findApproxTextInTarget)
#
# **Caveat:** If, on the second reload of a list of modules, a module raises an
# exception, then the rest of the modules **will not be reloaded**, since I
# can't think of any good way to handle this case (store, then re-raise on the
# first exception? All the excpetions? Sounds complex and ugly).
#
# Implementation notes
# --------------------
# Coding this using `contextmanager
# <https://docs.python.org/2.7/library/contextlib.html>`_ works, but
# requires messier code (specifially, a try/finally that feels
# unnecessary). An older trial implementation:
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
                 fail_names,
                 # A list of modules to reload when this ImportFail is in force. They will
                 # be reloaded without the ImportFail in force on __exit__. See `test
                 # methods`_.
                 reload_modules=None):
        self.fail_names = fail_names
        self.reload_modules = reload_modules

    # When entering the ``with`` clause, store the original ``__import__``
    # function, replacing it with a ``import_hook`` below which fails when
    # importing ``self.fail_names``.
    def __enter__(self):
        self.orig_import = builtins.__import__
        builtins.__import__ = self.import_hook
        # Reload the requested modules now that the ImportFail is in force.
        self._reload_modules()

    # Reload requested modules, if provided.
    def _reload_modules(self):
        if self.reload_modules:
            for mod in self.reload_modules:
                importlib.reload(mod)

    # Act like ``__import__``, except raise *ImportError* if
    # ``self.fail_names`` is imported.
    def import_hook(self, name, *args, **kwargs):
        if name in self.fail_names:
            raise ImportError
        return self.orig_import(name, *args, **kwargs)

    # Restore the original import function when leaving the context
    # manager.
    def __exit__(self, *args):
        builtins.__import__ = self.orig_import
        self._reload_modules()
