---
layout: default
title: Install enki from sources
baseurl: .
---

# Install from sources

On **Windows**, [this link](https://github.com/hlamer/enki/issues/19) might be helpful.

## 1. Install dependencies
Mandatory:

* [Python 2.7](http://python.org/download)
* [PyQt4](http://www.riverbankcomputing.co.uk/software/pyqt/download)
* [Qutepart](https://github.com/hlamer/qutepart)

Optional:

* [Python-Markdown](http://packages.python.org/Markdown/install.html). For Markdown preview
* [python-docutils](http://docutils.sourceforge.net/). For reStructuredText preview
* [ctags](http://ctags.sourceforge.net/). For navigation in file
* [tre](http://hackerboss.com/approximate-regex-matching-in-python/). For preview synchronization; see [this page](https://github.com/bjones1/tre/blob/master/INSTALL.rst) for build instructions
* [CodeChat](https://bitbucket.org/bjones/documentation/overview). For source code to HTML translation (literate programming)

#### Debian and Debian based

   `apt-get install python python-qt4 python-markdown python-docutils ctags`

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
