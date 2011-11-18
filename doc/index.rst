mksv3
=====
Simple programmers text editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The goal of the project is making text editing as comfort as possible. Major principles:

* User friendly interface. You don't need to read a lot of docs to understand it.
* Keyboard friendly interface. Minimize your mouse usage and work quicker.
* Minimalistic interface. Screen is left for code, not for bells and whistles.

mksv3 is Python port and new generation of `Monkey Studio <http://monkeystudio.org>`_

It is licelsed under `GNU GPL v2 license <http://www.gnu.org/licenses/gpl-2.0.html>`_

Features
""""""""

 * Syntax highlighting for more than 30 languages
 * Bookmarks
 * Search and replace functionality for files and directories. Regular expressions are supported
 * File browser
 * Autocompletion, based on document contents
 * Hightly configurable

Screenshots
"""""""""""

.. raw:: html

        <table width="50%"><tr>
        <td>
            <a href="screenshots/main-ui.png"><img src="screenshots/main-ui-preview.png"/></a>
        </td>
        <td>
            <a href="screenshots/minimal.png"><img src="screenshots/minimal-preview.png"/></a>
        </td>
        <td>
            <a href="screenshots/search-replace.png"><img src="screenshots/search-replace-preview.png"/></a>
        </td>
        </tr></table>

Download and install
^^^^^^^^^^^^^^^^^^^^
Ubuntu 11.10
""""""""""""

#. Add `P@sNox's PPA <https://launchpad.net/~pasnox/+archive/ppa>`_
#. Add `Monkey studio PPA <https://launchpad.net/~monkeystudio/+archive/ppa>`_
#. Install **mksv3** package ::

    sudo add-apt-repository ppa:pasnox/ppa
    sudo add-apt-repository ppa:monkeystudio/ppa
    sudo apt-get install mksv3

Other Ubuntus and Debians
"""""""""""""""""""""""""
Download the latest `fresh library and python bindings <https://launchpad.net/~pasnox/+archive/ppa>`_, `mksv3  <https://launchpad.net/~monkeystudio/+archive/ppa>`_, and install .deb packages manually

This method not tested yet, but, should be working. Team will be appreciate you, if you shared your experience

Python package index
""""""""""""""""""""
TODO

You should install all dependencies manually.

Source package
""""""""""""""
Sources are hosted `here <https://github.com/hlamer/mksv3/downloads>`_.

You should install all dependencies manually.

Dependencies
""""""""""""
#. Qt4 library
#. PyQt4 bindings
#. QScintilla 2 library and Python bindings. http://www.riverbankcomputing.co.uk/software/qscintilla/download)
#. Python. http://python.org
#. ConfigObj config file reader and writer. http://pypi.python.org/pypi/configobj/ http://www.voidspace.org.uk/python/configobj.html
#. Fresh framework, including Python bindings. https://github.com/pasnox/fresh

Documentation
^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1
   
   userindex.rst
   devindex.rst
