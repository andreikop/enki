Developer documentation
=======================
MkS is divided onto 2 parts: core and plugins.

Core

* creates basic user interface
* provides basic functionality for user
* contains plugin API for extend functionality

Plugin

* provides additional useful functionality for user. Example - File Manager plugin
* extends core functionality (adds additional patterns for parse console output to the console manager in the core
* provides some API for other plugins. NOT DESIRED. It's better to try to avoid plugin to plugin dependencies

Main difference of core and plugins - plugin definitely knows about core API, architecture, functionality, but
core must not know anything about a plugin.

Plugin API documentation
------------------------

.. toctree::

   monkeycore.rst
   workspace.rst
   settings.rst
   mainwindow.rst

Plugins documentation
---------------------
.. toctree::

   appshortcuts.rst