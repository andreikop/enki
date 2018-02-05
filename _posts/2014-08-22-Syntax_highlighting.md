---
layout: post
title: How syntax highlighting works
baseurl: ../../../
---


## How syntax highlighting works
<img src="http://habrastorage.org/storage2/6bb/381/e8c/6bb381e8c73e13c35a2a536affdb8206.png"/>

*This article was written 1 year ago. I finally found the time to translate it to English*

If you are a programmer, you spend a significant amount of your time coding. It doesn't matter how many buttons or menus or IDE or editor has, the core is a code editor component. Do you know how it works?
This article explains how syntax highlighting in [Qutepart](https://github.com/andreikop/qutepart) (and [katepart](http://kate-editor.org/about-katepart/)) works. The article is not about UI, but about the architecture. If you are interested, lets go..

### Motivation
I'm developing [Enki](http://enki-editor.org) - a universal, cross platform, extensible text editor inspired by Vim and Emacs. But, with a bit more intuitive and modern GUI. The editor is coded in Python. Initially I used the QScintilla text editor component, but it has some limitations which are not compatible with my goals.
katepart is really cool, but depends on KDE libraries. It is not convenient, especially for Windows and MacOS.
So, I decided to create my own component.

### Code parsing
Enki is not designed for some concrete languages and technologies. I'd like to highlight as many languages as possible. So I decided to use the existing syntax base from katepart.
For every highlighting language katepart supports there is [Highlight Definition](http://kate-editor.org/2005/03/24/writing-a-syntax-highlighting-file/) - an XML file which describes syntax and highlighting rules.
Highlight Definition describes something similar to a finite state machine. The machine moves over the code and changes its state - "Context". All contexts are saved in the stack, so the machine may return to previous state.
Example: C++. A context *"code"* includes a rule *if symbol " was found - switch to context "string"*. The context *"string"* highlights symbols in red and contains a rule *if " symbol found - return to previous context*.
The highlighting system is universal and powerful. The Highlight Definition XML file format is very well documented. This is probably why katepart supports more than 2 hundred languages and formats. The only disadvantage is the performance. An interpreter which parses any code using Highlight Definition in the majority of cases works slower than a parser for a concrete programming language.

### Performance optimisation

<img src="http://habrastorage.org/storage2/df8/65f/0cd/df865f0cd239e5ff19036f148f50abe7.png"/>

When finished writing the parser, my joy knew no bounds. All 59 files in various languages from the katepart collection looked pretty and opened quickly.
Then I tried to open a big file. A really big file. And my joy was over. I discovered that my parser was really slow.
After few hours of profiling, the parser became ten times quicker. But it was still too slow. Further code optimisation would have made the parser just a bit quicker but much more complicated.
I started googling how to write Python extensions in C. It appeared to be quite easy. Python is very extension friendly.
When the accelerated parser was ready, I measured the performance and discovered that it was just a little bit faster than pure Python code. katepart highlighting algorithms use regular expressions. Standard C library doesn't support them, so I tried to call the Python re module from the C extension. These calls took 90% of the parsing time.
I had to add the first (and only one) external Qutepart dependency - the [pcre](http://pcre.org/) regular expression library.
With the parser in C and pcre the performance has became much better. (The numbers are below).

### Asynchronous highlighting

The majority of source files are quite small. But I've edited 300K LOC sources. It doesn't matter how cool the parsing algorithm developer is or how quick the CPU is. 300K LOC file is parsed slower than the user would like to wait, so the parsing should be asynchronous.
**katepart** parses code in the main GUI thread. **The parsing is lazy** - a file is parsed from the beginning to the last line visible on the screen. This approach works fine if the file is opened in the beginning. But if I try to jump to the end of huge file - the interface just freezes. Not the best behaviour.
When **vim** and **emacs** need to draw the end of a big file, they start parsing the text a few lines behind first visible line, but **not from the beginning**. This approach never blocks the UI for a long time.
But one problem exists - it is only possible to parse a source file from the beginning. I.e. to understand if " is a string start or a string end, a parser needs to know if string was opened before.
For the majority of cases, parsing from the middle of the file works, but sometimes incorrect highlighting appears (as on this screenshot from vim)

<img src="http://habrastorage.org/storage2/6d1/fc0/af3/6d1fc0af37cd85eea7b28c7f8f044ff8.png"/>

Nowadays chip vendors tend to increase CPU core count instead of core frequency. So developers tend to write parallel code.
I tried to create a thread which parses a code and sends results to the GUI thread. But Qt wasn't designed for multithreading, so thread synchronization and interaction appeared to be really complicated. I dropped the idea of using threads.
After the research and experiments I found the next solution: a file is parsed from the beginning by the GUI thread, but not for longer than 20 milliseconds. Then control is returned to the main loop, which processes user actions and draws GUI. When the main loop is idle, parsing is resumed again for next 20 millisecond chunk.
If a user jumps to the end of a file which is not highlighted - the file is drawn without highlighting, and redrawn later when visible lines have been parsed.
Sometimes a user sees a code without highlighting, but the GUI is never blocked and the highlighting is always correct.

### Incremental highlighting

When a file is opened, it should be parsed from the beginning to the end. But when code is edited, the file shall be parsed from the first modified symbol. Usually only a few lines should be rehighlighted.
To achieve this, every line has a block of attached data which stores a parser state.
The parser takes its state from the first modified line, and parses the file down until it finds a line whose state has not changed during parsing.

### Performance comparison

It is very difficult to compare the highlighting  speed of various editors. Their performance depends on hardware, software versions, programming languages, source file contents, the Moon phase and many other factors ...
But this article would not be finished if I didn't make some comparisons. So I will.
*Disclaimer: the performance depends on many factors and may vary. The measurements are not precise, the facts are not proven and might be incorrect. Editors might have improved since August 2013.
The information below can't be used as evidence that one text editor is better than another.*

I tried to open a big C++ file (364,121 lines) with a few text editors. The results are below:

| Component or editor    | Whole file highlighting time      | When UI is blocked                                   | Problems                      |
| ---------------------- | --------------------------------- | ---------------------------------------------------- | ----------------------------- |
| Qutepart               | 44 seconds                        | Never                                                | File opening takes 3 seconds  |
| katepart               | 3 seconds                         | Until parsing of last visible line is completed      | None                          |
| QScintilla             | 3 seconds                         | Never                                                | Lags when typing              |
| Scintilla              | 3 seconds                         | Never                                                | Lags when typing              |
| Sublime Text           | 23 seconds                        | Freezes when typing until rehighlighting is finished | None                          |
| gedit                  | 8 seconds                         | Never                                                | Lags when typing              |
| Qt Creator             | 20 seconds                        | Freezes when typing until rehighlighting is finished | None                          |
| Ninja IDE              | 14 seconds                        | When opening a file                                  | Only the first 51 lines were highlighted. Terrible lags during typing. |
| vim                    | Immediately                       | Never                                                | Does not parse a code  from the beginning. In some cases highlighting is incorrect. |
| emacs                  | Immediately                       | Never                                                | Does not parse a code  from the beginning. In some cases highlighting is incorrect. When scrolling up hangs for about a minute |

The table shows that Qutepart is the slowest of the tested editors. This is predictable because an interpreted dynamically typed language is used and the syntax definitions are interpreted XML files. But Qutepart supports very many languages, it never blocks the GUI, it never shows incorrect highlighting. These features are more important for real cases.
For the overwhelming majority of real files a user always sees a highlighted file and doesn't feel any lags. So, the current state is quite good and it isn't worth it to continue Qutepart optimisation.

### The result
<img src="http://habrastorage.org/storage2/d25/87a/120/d2587a1206357246e4172df4fb99121a.png"/>

One year ago I released the code editor component [Qutepart](https://github.com/andreikop/qutepart) and the code editor [Enki](http://enki-editor.org) based on it.
The component depends on PyQt and pcre and contains extension in C. The Syntax Definition files and the indentation algorithms were taken from katepart. Like katepart, the code was released under LGPL.

This article explains how Qutepart (and partially katepart) syntax highlighting works. I would be happy to read in your comments how highlighting is implemented in other editors.
