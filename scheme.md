---
layout: default
title: Scheme REPL
baseurl: .
---

## Scheme REPL integration

*Update: Standard ML (SML) REPL also is supported!*

Enki supports MIT Scheme interpreter integration. It allows you to quickly execute code contained in your current opened file and to easily evaluate expressions interactively with REPL.

### Activating scheme mode
* Make sure the **MIT Scheme** (*mit-scheme*) package is installed.
* Open any Scheme file (*.scm, *.ss). The Scheme mode will automatically be loaded. You will have an *MIT Scheme* item in your main menu.
Alternatively you may go to *Settings -> Settings -> Modes -> Scheme* and choose the option *Enable MIT Scheme always*.

### Evaluating your file
Press Ctrl+E to evaluate the whole file, or select some text and press Ctrl+E to evaluate only this text.

### REPL
In the MIT Scheme dock you can evaluate your expressions. If you don't see the dock, remember that you can use *F8* to jump to dock, then Ctrl+Enter to return back to the code.

### Debugging
Enki does not support GUI debugging. But, you can use MIT Scheme's interpreter functionality. See http://www.gnu.org/software/mit-scheme/

### Indentation
By default, Enki indents Scheme files according to the  http://community.schemewiki.org/?scheme-style. If you want to disable smart indentation, edit the ''SchemeIndentHelper'' option in your ${HOME}/.enki/enki.json

### Make Enki Scheme mode better
andreikop: I created this mode for my SICP exercises (When I'm writing this post, I've almost finished the 3rd chapter). I'm not an experienced schemer, nor an emacs guru. **If you know how to enhance the mode, tell me!**



<iframe width="960" height="720" src="http://www.youtube.com/embed/yr66IRF4__M?rel=0" frameborder="0"></iframe>
