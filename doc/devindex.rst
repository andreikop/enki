Developer documentation
=======================
MkS is divided onto 2 parts: core and plugins.

Core

* creates basic user interface
* provides basic functionality for user
* contains plugin API for extend functionality

Plugin

* provides additional useful functionality for user. Example - File Browser
* extends core functionality
* provides some API for other plugins. NOT DESIRED. It's better to try to avoid plugin to plugin dependencies

Main difference of core and plugins - plugin definitely knows about core API, architecture, functionality, but
core must not know anything about a plugin.

Plugin API documentation
------------------------

.. toctree::

   core/core.rst
   core/mainwindow.rst
   core/workspace.rst
   core/abstractdocument.rst
   core/config.rst

Plugins documentation
---------------------
.. toctree::

   plugins/appshortcuts.rst
   plugins/editor.rst
   plugins/editortoolbar.rst
   plugins/editorshortcuts.rst
   plugins/filebrowser.rst
   plugins/searchreplace.rst
