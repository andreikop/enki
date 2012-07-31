---
layout: default
title: Scheme REPL integration
baseurl: .
---

## Scheme REPL integration

enki supports MIT Scheme interpreter integration. It allows 
you to quickly execute code, which is contained in your current opened file, and to evaluate expressions interactively with REPL.

### Activating scheme mode
* Make sure **pygments** (`python-pygments`) python package is installed
* Make sure **MIT Scheme** (`mit-scheme`) package is installed
* Open any Scheme file (`*.scm`, `*.ss`). Scheme mode will be loaded. You will have `MIT Scheme` item in your main menu. Alternatively you can go to `Settings -> Settings -> Modes -> Scheme` and choose option *Enable MIT Scheme always*

### Evaluating your file
Press *Ctrl+E* to evaluate whole file, or select some text and press *Ctrl+E* to evaluate only this text.

### REPL
In the MIT Scheme dock you can evaluate your expressions. If you don't see the dock.
Remember that you can use *F8* to jump to dock, and *Ctrl+Enter* to return back to the code

### Debugging
enki does not support GUI debugging. But, you can use MIT Scheme interpreter functionality. See http://www.gnu.org/software/mit-scheme/

### Indentation
By default, enki indents Scheme files according to http://community.schemewiki.org/?scheme-style. If you want to disable smart indentation, edit ''SchemeIndentHelper'' option in your ${HOME}/.enki/enki.json

### Make enki Scheme mode better
hlamer: I created this mode for my SICP exercises (When I'm writing this post, I'm near to finish 3rd chapter). I'm not an experienced schemer, and not an emacs guru. If you know, how to enhance the mode, say me.

<iframe width="720" height="540" src="http://www.youtube.com/embed/yr66IRF4__M" frameborder="0" allowfullscreen="true"></iframe>

