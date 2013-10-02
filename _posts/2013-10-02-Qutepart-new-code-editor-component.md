---
layout: post
title: New code editor component release
baseurl: ../../../
---

# Qutepart - new code editor component for Enki

What is the most important part of a car? I guess an engine. And what is the most important part of text editor or IDE?
I guess a text editor component.

For many years Monkey Studio had been using QScintilla. Enki, derived from MkS, also used to use QScintilla in the first release. And we never have been happy with it. In fact, we have been hating it, but, there are no alternatives for Qt.

Now this problem is resolved for Enki. I created own code editor component - [Qutepart](https://github.com/hlamer/qutepart)
<img src="../../../blog-screens/qutepart.png"/>

QScintilla has binary parsers, implemented in C++. It is quite difficult to create new parsers (who likes coding in C++?). I counted 30 parsers in current MkS version.
But Qutepart uses syntax definition files, created for Kate, to parse and highlight the code. **More than 200 languages are supported!**

QScintilla does not inherit QPlainTextEdit, but draws all text with own code. And, drawing algorithm sometimes sucks. Especially on long text lines, which does not fit in one row.
But Qutepart uses Qt functionality, and Qutepart works fine.

QScintilla does not grow. Whould you like to to add new feature? OK, you should add the feature to Scintilla at first and get your patch applied. Than wait while your feature is released and included to QScintilla. After it, wait while new QScintilla is included to distributions. And remember, that new version will never be included to already released versions of distribution.
But Qutepart is our own component, and we can develop and release it synchronously with the editor.
In first release I included **Bash-like Tab code completion**, which I was missing in QScintilla. And, I think **many other features will come** in the future. I.e. VIM mode.

QScintilla allows to configure colors for parsers. But, there are no common settings. If you want to create color theme, you should configure all 30 parsers one by one.
But Qutepart (Kate Syntax Definition Files) allows to configure classes of code. I.e. all strings, or all keywords. So, it is **much easier to create a color theme** now.

I released first version of Enki, based on Qutepart, more than month ago. After this few bugs have been found and fixed, many improvements have been done. Except this, I finally got time to make quick but useful improvements, not related to code editor component.
I hope you will enjoy Qutepart and new Enki!
