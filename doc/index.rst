`Back to site <http://hlamer.github.com/mksv3/>`_.

Internal documentation
======================

To create your own plugins for mksv3, at first read tutorial at the `wiki <https://github.com/hlamer/mksv3/wiki/Plugins-tutorial>`_.

MkS consists of 4 major packages:

mks.core

* creates basic user interface
* provides basic functionality for user
* contains plugin API for extend functionality

mks.lib

* Code, which is not used by core, but, may be used by more than one plugin. I.e. common widgets.

mks.plugins

* provides additional useful functionality for user. Example - File Browser
* extends core functionality
* provides some API for other plugins. NOT DESIRED. It's better to try to avoid plugin to plugin dependencies

Plugins do not export any public API and are not included to this docs. But are documented with docstrings in the code.

mks.fresh

* Few GUI widgets. Ported from https://github.com/pasnox/fresh. Documented `here <http://api.monkeystudio.org/fresh/>`_.

Modules documentation
=====================

Plugin API documentation
------------------------

.. toctree::

   core/core.rst
   core/mainwindow.rst
   core/workspace.rst
   core/abstractdocument.rst
   core/config.rst
   core/uisettings.rst
   core/filefilter.rst
   core/locator.rst

Not API core modules
--------------------

.. toctree::

    core/openedfilemodel.rst

Library modules
---------------

.. toctree::

    lib/termwidget.rst
    lib/buffpopen.rst
    lib/htmldelegate.rst
    lib/pathcompleter.rst
