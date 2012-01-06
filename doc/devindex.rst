Developer (internal) documentation
==================================
MkS is divided onto 3 parts: **core** **lib** and **plugins**

Core

* creates basic user interface
* provides basic functionality for user
* contains plugin API for extend functionality

Lib

* Consists of code, which is not used by core, but, may be used by more than one plugin. I.e. common widgets.

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
   core/uisettings.rst

Not API core modules
--------------------

.. toctree::

    core/openedfilemodel.rst

Library modules
---------------

.. toctree::

    lib/highlighter.rst
    lib/termwidget.rst
    lib/buffpopen.rst

Plugins documentation
---------------------
.. toctree::

   plugins/appshortcuts.rst
   plugins/editor.rst
   plugins/editortoolbar.rst
   plugins/editorshortcuts.rst
   plugins/filebrowser.rst
   plugins/helpmenu.rst
   plugins/searchreplace.rst
   plugins/associations.rst

