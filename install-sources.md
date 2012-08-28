---
layout: default
title: Install enki from sources
baseurl: .
---

# Install from sources

On **Windows**, [this link](https://github.com/hlamer/enki/issues/19) might be helpful.

## 1. Install dependencies
* Python 2. Tested on v2.6.6 and v2.7.2
* PyQt4
* QScintilla 2 and Python bindings. v2.4.1 or newer
* pyparsing
* pygments. (Optional, for highlighting Scheme files)
* markdown. (Optional, for Markdown preview)

#### Debian and Debian based

   `apt-get install python python-qt4 python-qscintilla2 python-pyparsing python-pygments python-markdown`
#### Other Unixes
   Find and install listed packages with your package manager
#### Other systems

* [http://python.org/download](http://python.org/download)
* [http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [http://www.riverbankcomputing.co.uk/software/qscintilla/download](http://www.riverbankcomputing.co.uk/software/qscintilla/download)
* [http://pyparsing.wikispaces.com/Download+and+Installation](http://pyparsing.wikispaces.com/Download+and+Installation)
* [http://pygments.org/download](http://pygments.org/download) (Optional, for highlighting Scheme files)
* [http://packages.python.org/Markdown/install.html](http://packages.python.org/Markdown/install.html) (Optional, for Markdown preview)

## 2. Get the sources

[Download](https://github.com/hlamer/enki/tags) source archive

## 3. Setup
    
`./setup.py install`

## 4. Enjoy
Don't forget to send a bug report, if you are having some problems
