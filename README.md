[![Build Status](https://travis-ci.org/andreikop/enki.svg?branch=master)](https://travis-ci.org/andreikop/enki)


# Enki: A text editor for programmers

[Official site](http://enki-editor.org/)


## Installation
For most Linux and Windows users: use the pre-built binaries from the [official site](http://enki-editor.org/). But if you feel brave..

**master branch can be unstable or even broken. Use releases if you are not going to hack Enki**

### 1. Install dependencies
Mandatory:

* [Python 3](http://python.org/download)
* [PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/download). With SVG support.
* [Qutepart](https://github.com/andreikop/qutepart)
* [Qt Console](https://github.com/jupyter/qtconsole)
* [PyQt5 QtWebEngine bindings]. `python3-pyqt5.qtwebengine` or `python3-qt5-webengine` package.

Optional:

* [Python-Markdown](https://github.com/Python-Markdown/markdown). For Markdown preview
* [Docutils](http://docutils.sourceforge.net/). For reStructuredText preview
* [ctags](http://ctags.sourceforge.net/). For navigation in file
* [regex](https://pypi.python.org/pypi/regex). For preview synchronization
* [CodeChat](https://bitbucket.org/bjones/documentation/overview). For source code to HTML translation (literate programming)
* [Sphinx](http://sphinx-doc.org/). To build Sphinx documentation.
* [Flake8](https://flake8.readthedocs.org/en/latest/). To lint your Python code.

#### Debian and Debian based

```
   apt-get install python3 libqt5svg5 python3-pyqt5 python3-pyqt5.qtwebengine python3-qtconsole python3-markdown python3-docutils ctags
   pip3 install -r requirements.txt

```
   *If your repo doesn't contain **python3-pyqt5.qtwebengine**, remove **python3-pyqt5**, **python3-sip**, and do* `pip3 install PyQt5`

Install Qutepart from [sources](https://github.com/andreikop/qutepart).
#### Other Unixes
Find and install listed packages with your package manager.
Install Qutepart from [sources](https://github.com/andreikop/qutepart).
#### Other systems

Go to official pages of the projects, download packages and install according to instructions.

### 2. Get the sources

[Download](https://github.com/andreikop/enki/releases) source archive


### 3. Install Enki
    python3 setup.py install

### 4. Enjoy
Don't forget to send a bug report if you are having some problems


## Running from the source tree

    python3 enki


## Releasing new version
```
    make bump-version  # Set next version number. Commit the changes
    make changelog-update  # Edit and commit 3 changelog files
    git tag vx.x.x
    git push
    git push --tags
    make push-obs  # upload the version to Open Suse build service
    # make pip release TODO document this step
```


## License
[GPL v2](LICENSE.GPL2.html)

## Authors

* **Andrei Kopats** (aka **andreikop**) ported core and some plugins to Python, reworked it and released the result as *Enki*
* **Filipe Azevedo**, **Andrei Kopats** and [Monkey Studio v2 team](http://monkeystudio.org/team) developed *Monkey Studio v2*

[The Team](http://enki-editor.org/team.html)

## Contacts
[enki-editor@googlegroups.com](mailto:enki-editor@googlegroups.com)

[andrei.kopats@gmail.com](mailto:andrei.kopats@gmail.com)
