---
layout: default
title: Install enki from sources
baseurl: .
---

# Install from sources

On **Windows**, [this link](https://github.com/hlamer/enki/issues/19) might be helpful.

## 1. Install dependencies
* Python 2.7
* PyQt4
* [Qutepart](https://github.com/hlamer/qutepart)
* pyparsing
* markdown. (Optional, for Markdown preview)

#### Debian and Debian based

   `apt-get install python python-qt4 python-pyparsing python-markdown`
#### Other Unixes
   Find and install listed packages with your package manager
#### Other systems

* [http://python.org/download](http://python.org/download)
* [http://www.riverbankcomputing.co.uk/software/pyqt/download](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [https://github.com/hlamer/qutepart](https://github.com/hlamer/qutepart)
* [http://pyparsing.wikispaces.com/Download+and+Installation](http://pyparsing.wikispaces.com/Download+and+Installation)
* [http://packages.python.org/Markdown/install.html](http://packages.python.org/Markdown/install.html) (Optional, for Markdown preview)

## 2. Get the sources

[Download](https://github.com/hlamer/enki/tags) source archive

## 3. Setup
    
`./setup.py install`

## 4. Fix python interpreter version
If your default python version is python3 (i.e. in **Gentoo**), open file /usr/local/bin/enki with your text editor and replace
`#!/usr/bin/env python`
with
`#!/usr/bin/env python{your 2.x version}`

## 5. Enjoy
Don't forget to send a bug report, if you are having some problems
