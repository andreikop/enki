# Enki: A text editor for programmers

[Official site](http://enki-editor.org/)


## Installation
For most Linux and Windows users: use the pre-built binaries from the [official site](http://enki-editor.org/). But if you feel brave..

**master branch can be unstable or even broken. Use releases if you are not going to hack Enki**

### 1. Install dependencies
Mandatory:

* [Python 3](http://python.org/download)
* [PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/download). With SVG support.
* [Qutepart](https://github.com/hlamer/qutepart)

Optional:

* [Python-Markdown](http://packages.python.org/Markdown/install.html). For Markdown preview
* [python-docutils](http://docutils.sourceforge.net/). For reStructuredText preview
* [ctags](http://ctags.sourceforge.net/). For navigation in file
* [regex](https://pypi.python.org/pypi/regex). For preview synchronization
* [CodeChat](https://bitbucket.org/bjones/documentation/overview). For source code to HTML translation (literate programming)
* [Sphinx](http://sphinx-doc.org/). To build Sphinx documentation.
* [Flake8](https://flake8.readthedocs.org/en/latest/). To lint your Python code.

#### Debian and Debian based

```
   apt-get install python3 libqt5svg5 python3-pyqt5 python3-markdown python3-docutils ctags
   pip3 install -r requirements.txt
```

Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other Unixes
Find and install listed packages with your package manager.
Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other systems

Go to official pages of the projects, download packages and install according to instructions.

### 2. Get the sources

[Download](https://github.com/hlamer/enki/releases) source archive


### 3. Install Enki
    python3 setup.py install

### 4. Enjoy
Don't forget to send a bug report if you are having some problems


## Running from the source tree
    python3 bin/enki

## License
[GPL v2](LICENSE.GPL2.html)

## Authors

* **Andrei Kopats** (aka **hlamer**) ported core and some plugins to Python, reworked it and released the result as *Enki*
* **Filipe Azevedo**, **Andrei Kopats** and [Monkey Studio v2 team](http://monkeystudio.org/team) developed *Monkey Studio v2*

[The Team](http://enki-editor.org/team.html)

## Contacts
[enki-editor@googlegroups.com](mailto:enki-editor@googlegroups.com)

[hlamer@tut.by](mailto:hlamer@tut.by)

