mksv3
=====
.. image:: https://images-ssl.sourceforge.net/images/project-support.jpg
   :alt: Support this project
   :target: https://sourceforge.net/donate/index.php?group_id=163493 

About
"""""

**Simple programmers text editor.**

The goal of the project is making code editing as comfort as possible. Major principles:

* User friendly interface. You don't need to read a lot of docs to understand it.
* Keyboard friendly interface. Minimize your mouse usage and work quicker.
* Minimalistic interface. Screen is left for code, not for bells and whistles.

This project is Python port and new generation of `Monkey Studio <http://monkeystudio.org>`_

**Features**:

 * Syntax highlighting for more than 30 languages
 * Bookmarks
 * Search and replace functionality for files and directories. Regular expressions are supported
 * File browser
 * Autocompletion, based on document contents
 * Hightly configurable

Project is going to be **crossplatform**, and, will probably work on all platforms, but, currently has been tested only on Ubuntu. Team will be appreciate you, if you shared your experience about other platforms.

Screenshots:

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


Project is licelsed under `GNU GPL v2 license <http://www.gnu.org/licenses/gpl-2.0.html>`_

Download and install
""""""""""""""""""""

Ubuntu 11.10
^^^^^^^^^^^^

#. Add `P@sNox's PPA <https://launchpad.net/~pasnox/+archive/ppa>`_
#. Add `Monkey studio PPA <https://launchpad.net/~monkeystudio/+archive/ppa>`_
#. Install **mksv3** package

All 3 steps::

    sudo add-apt-repository ppa:pasnox/ppa
    sudo add-apt-repository ppa:monkeystudio/ppa
    sudo apt-get install mksv3

Other Ubuntus and Debians
^^^^^^^^^^^^^^^^^^^^^^^^^
#. Download *libfresh1* and *python-qt4-fresh1* packages from `P@sNox's PPA <https://launchpad.net/~pasnox/+archive/ppa/+packages>`_
#. Download *mksv3* package from `Monkey Studio PPA <https://launchpad.net/~monkeystudio/+archive/ppa/+packages>`_
#. Install packages with ::
    
    sudo dpkg --install libfresh1*.deb
    sudo dpkg --install python-qt4-fresh1*.deb
    sudo dpkg --install mksv3*.deb

This method not tested yet, but, should be working. Team will be appreciate you, if you shared your experience

Source package
^^^^^^^^^^^^^^
The latest release are `here <https://github.com/hlamer/mksv3/tags>`_.

You should install all dependencies manually.

Dependencies
^^^^^^^^^^^^
#. Qt4 library
#. PyQt4 bindings
#. QScintilla 2 library and Python bindings. http://www.riverbankcomputing.co.uk/software/qscintilla/download)
#. Python. http://python.org
#. ConfigObj config file reader and writer. http://pypi.python.org/pypi/configobj/ http://www.voidspace.org.uk/python/configobj.html
#. Fresh framework, including Python bindings. https://github.com/pasnox/fresh

Support
"""""""

User manual
^^^^^^^^^^^
Documentation for users is :doc:`here <userindex>`

Ask question
^^^^^^^^^^^^
* IRC room *#monkeystudio* on *irc.freenode.net*. `Web interface <http://monkeystudio.org/irc>`_
* `Discussion and support Google group <http://groups.google.com/group/mksv3>`_

Report bug
^^^^^^^^^^
There are 3 ways to report a bug

#. Fork https://github.com/hlamer/mksv3 and fix the bug
#. Open an issue at https://github.com/hlamer/mksv3/issues
#. Send bug report to mksv3-bugs@googlegroups.com

Hacking
"""""""
Documentation for developers is :doc:`here <devindex>`

Source code is `here <https://github.com/hlamer/mksv3>`_

Authors
"""""""
* **Filipe Azevedo** (aka **P@sNox**) and `Monkey Studio v1 team <http://monkeystudio.org/node/17>`_ developed *Monkey Studio v1*
* **Filipe Azevedo**, **Andrei Kopats** (aka **hlamer**) and `Monkey Studio v2 team <http://monkeystudio.org/team>`_ developed *Monkey Studio v2*
* **Andrei Kopats** ported core and some plugins to Python, reworked it and released the result as *mksv3*

Use mksv3@googlegroups.com or hlamer@tut.by as contact email.
