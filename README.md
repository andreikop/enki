# Enki: A text editor for programmers

[Official site](http://enki-editor.org/)


## Installation

For most Linux (CentOS, Debian, Fedora, openSUSE, RHEL, and Ubuntu) and Windows users: use the pre-built binaries from the [official site](http://enki-editor.org/). Otherwise, follow the instructions below.

For Linux developers, the [install script](https://github.com/hlamer/enki/blob/master/win/enki_install.sh) provides a quick install. For all others, follow the instructions below.

### 1. Install dependencies
Mandatory:

* [Python 3](http://python.org/download)
* [PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/download). With SVG support.
* [Qutepart](https://github.com/hlamer/qutepart)

Optional:

* [Python-Markdown](http://packages.python.org/Markdown/install.html) for Markdown preview.
* [python-docutils](http://docutils.sourceforge.net/) for reStructuredText preview.
* [ctags](http://ctags.sourceforge.net/) for navigation in files.
* [regex](https://pypi.python.org/pypi/regex) for preview synchronization.
* [CodeChat](https://bitbucket.org/bjones/documentation/overview) for source code to HTML translation (literate programming).
* [Sphinx](http://sphinx-doc.org/) for documentation generation.
* [Flake8](https://pypi.python.org/pypi/flake8) for Python source code checking.
* [Markdown mathjax](https://github.com/mayoff/python-markdown-mathjax) for Python-Markdown math support.
* [Mock](https://pypi.python.org/pypi/mock) (developers only) for unit test support.

### 2. Get the sources

[Download](https://github.com/hlamer/enki/releases) the source archive.

### 3. Install Enki
    python3 setup.py install

### 4. Enjoy
Don't forget to send a bug report if you are having some problems


## Running from the source tree
    python3 bin/enki

## License
[GPL v2](LICENSE.GPL2.html)

## Authors

* **Andrei Kopats** (aka **hlamer**) ported core and some plugins to Python, reworked it and released the result as *Enki*.
* **Filipe Azevedo**, **Andrei Kopats** and [Monkey Studio v2 team](http://monkeystudio.org/team) developed *Monkey Studio v2*.

[The Team](http://enki-editor.org/team.html)

## Contacts
[enki-editor@googlegroups.com](mailto:enki-editor@googlegroups.com)

[hlamer@tut.by](mailto:hlamer@tut.by)
