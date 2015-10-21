# Enki: A text editor for programmers

[Official site](http://enki-editor.org/)


## Installation

### 1. Install dependencies
Mandatory:

* [Python 2.7](http://python.org/download)
* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [Qutepart](https://github.com/hlamer/qutepart)

Optional:

* [Python-Markdown](http://packages.python.org/Markdown/install.html). For Markdown preview
* [python-docutils](http://docutils.sourceforge.net/). For reStructuredText preview
* [ctags](http://ctags.sourceforge.net/). For navigation in file
* [regex](https://pypi.python.org/pypi/regex). For preview synchronization
* [CodeChat](https://bitbucket.org/bjones/documentation/overview). For source code to HTML translation (literate programming)

#### Debian and Debian based

   `apt-get install python python-qt4 python-markdown python-docutils ctags`

Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other Unixes
Find and install listed packages with your package manager.
Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other systems

Go to official pages of the projects, download packages and install according to instructions.

### 2. Get the sources

[Download](https://github.com/hlamer/enki/releases) source archive


### 3. Install Enki
    python setup.py install

### 4. Fix python interpreter version
If your default python version is python3 (i.e. in **Gentoo**), open file /usr/local/bin/enki with your text editor and replace
`#!/usr/bin/env python`
with
`#!/usr/bin/env python2.7

### 5. Enjoy
Don't forget to send a bug report if you are having some problems


## Running from the source tree
    python bin/enki

## License
[GPL v2](LICENSE.GPL2.html)

## Authors

* **Andrei Kopats** (aka **hlamer**) ported core and some plugins to Python, reworked it and released the result as *Enki*
* **Filipe Azevedo**, **Andrei Kopats** and [Monkey Studio v2 team](http://monkeystudio.org/team) developed *Monkey Studio v2*

[The Team](http://enki-editor.org/team.html)

## Contacts
[enki-editor@googlegroups.com](mailto:enki-editor@googlegroups.com)

[hlamer@tut.by](mailto:hlamer@tut.by)
