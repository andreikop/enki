---
layout: default
title: Install enki from sources
baseurl: .
---

# Install from sources

On **Windows**, [this link](https://github.com/hlamer/enki/issues/19) might be helpful.

## 1. Install dependencies
* [Python 2.7](http://python.org/download)
* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
* [Qutepart](https://github.com/hlamer/qutepart)
* [Python-Markdown](http://packages.python.org/Markdown/install.html). (Optional, for Markdown preview)
* [python-docutils](http://docutils.sourceforge.net/). (Optional, for reStructuredText preview)
* [ctags](http://ctags.sourceforge.net/). (Optional, for navigation in file)

#### Debian and Debian based

   `apt-get install python python-qt4 python-pyparsing python-markdown python-docutils ctags`

Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other Unixes
Find and install listed packages with your package manager.
Install Qutepart from [sources](https://github.com/hlamer/qutepart).
#### Other systems

Go to official pages of the projects, download packages and install according to instructions.
## 2. Get the sources

[Download](https://github.com/hlamer/enki/releases) source archive

## 3. Setup
    
`./setup.py install`

## 4. Fix python interpreter version
If your default python version is python3 (i.e. in **Gentoo**), open file /usr/local/bin/enki with your text editor and replace
`#!/usr/bin/env python`
with
`#!/usr/bin/env python{your 2.x version}`

## 5. Enjoy
Don't forget to send a bug report, if you are having some problems
