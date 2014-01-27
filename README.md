# Enki: A text editor for programmers

[Official site](http://enki-editor.org/)


## Installation
[Full instructions](http://enki-editor.org/install-sources.html)

#### Install dependencies
* [Python 2.7](http://python.org/download)
* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
* [Qutepart](https://github.com/hlamer/qutepart)
* [Python-Markdown](http://packages.python.org/Markdown/install.html). (Optional, for Markdown preview)
* [python-docutils](http://docutils.sourceforge.net/). (Optional, for reStructuredText preview)
* [ctags](http://ctags.sourceforge.net/). (Optional, for navigation in file)
* [tre](http://hackerboss.com/approximate-regex-matching-in-python/)

#### Build tre
First, download the source:

    git clone git://github.com/bjones1/tre

##### Unix
    sudo apt-get install python-dev autoconf gettext libtool autopoint
    cd <tre directory>
    utils/autogen.sh
    ./configure
    make
    sudo make install
    cd python
    python setup.py build_ext
    sudo python setup.py install

Then add `/usr/local/lib` to your `LD_LIBRARY_PATH`. For example, `export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH`.

##### Windows
- Build a Release version of the TRE library using Visual Studio 2008 express (or the full version) based on the solution file ``tre/win32/tre.sln``.
- From a command line in ``tre/python``, run ``python setup.py build_ext -I../include install``.

#### Install Enki
    ./setup.py install


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
