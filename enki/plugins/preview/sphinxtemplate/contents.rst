Template for a project using CodeChat
=====================================
This file provides a template for your new CodeChat project and gives directions on how to use the application, and provides examples of its use. A quick start:

#. Begin typing in the left (code) view; as you type, CodeChat will convert the program to HTML then show the characters you've typed and their surroundings highlighed in the browser view. Status messages from the build appear in the bottom pane. For a more accurate rendering of the web page, select ``View | In browser``.
#. If you find a change to make while reading through the web view, simply double-click on the text you'd like to edit. This will move to the corresponding location in the code view, where you may now perform the desired edits. The syntax you see is `reST markup <https://dl.dropbox.com/u/2337351/rst-cheatsheet.html>`_ by `Sphinx <http://sphinx-doc.org/>`_. The items on the ``Help`` menu provide a convenient reference.

Now, you're ready to document some code. Open :doc:`conf.py` for an example of this process. When you're ready to document your own code:

#. Add your source files to the table of contents below, after ``conf.py``.
#. Open one of your source files and begin documenting; all comments [#]_ are processed as reST/Sphinx, while source code will be syntax hilighted [#]_.

.. [#] Currently, only single-line comments in C/C++, Python, reST, assembly (.s), BASH scripts, PHP, MATLAB scripts, DOS batch (.bat) files, .ini, and .iss files are supported.

.. [#] The :doc:`conf.py` provided with this template assmes Python source files. To change this, edit the line ``highlight_language = 'python3'`` in :doc:`conf.py` or add a `highlight directive <http://sphinx-doc.org/markup/code.html#code-examples>`_ such as ``// .. highlight:: c`` to each source flie.

Table of Contents
-----------------
.. toctree::
   :maxdepth: 2

   conf.py

Indices and tables
------------------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
