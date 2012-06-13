`mksv3 home page <http://hlamer.github.com/mksv3/>`_.

Plugin API documentation
========================
This is API documentation. It lists all modules, which may be used by mksv3 plugins.

To create your own plugins, at first read tutorial at the `wiki <https://github.com/hlamer/mksv3/wiki/Plugins-tutorial>`_.


mks.core
--------
Core creates basic user interface, provides basic functionality for user, contains plugin API.

.. toctree::

   core/core.rst
   core/mainwindow.rst
   core/actionmanager.rst
   core/workspace.rst
   core/abstractdocument.rst
   core/config.rst
   core/uisettings.rst
   core/filefilter.rst
   core/locator.rst

mks.lib
-------
Code (but not widgets), which is not used by core, but, may be used by more than one plugin.

.. toctree::

    lib/buffpopen.rst
    lib/htmldelegate.rst
    lib/pathcompleter.rst

mks.widgets
-----------
Set of reusable widgets.

.. toctree::

    widgets/dockwidget.rst
    widgets/lineedit.rst
    widgets/colorbutton.rst
    widgets/termwidget.rst

mks.plugins
-----------
This package contains plugins, which extend the core with additional functionality.

Plugins do not export any public API and are not included to this docs. But code consists docstrings.

Every plugin is optional, therefore, no other modules are allowed to depend on plugin.
