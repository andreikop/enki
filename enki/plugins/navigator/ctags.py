"""Ctags execution and output parsing functionality
"""

import os
import sys
import tempfile
from contextlib import contextmanager

from enki.core.core import core
import enki.lib.get_console_output as gco


class FailedException(UserWarning):
    """Tags generation failed.

    Module API exception
    """
    pass


class _ParseFailed(UserWarning):
    """Exception for internal usage"""
    pass


class Tag:
    def __init__(self, type_, name, lineNumber, parent):
        self.type = type_
        self.name = name
        self.lineNumber = lineNumber
        self.parent = parent
        self.children = []

    def format(self, indentLevel=0):
        indent = '\t' * indentLevel
        formattedChildren = [child.format(indentLevel + 1) \
                                for child in self.children]
        result = '{}{} {}'.format(indent, self.lineNumber, self.name)
        if formattedChildren:
            result += '\n'
            result += '\n'.join(formattedChildren)

        return result


def _parseTag(line):
    items = line.split('\t')
    name = items[0]
    if len(items) == 5:
        type_ = items[-2]
        lineText = items[-1]
        scopeText = None
    elif len(items) == 6:
        type_ = items[-3]
        lineText = items[-2]
        scopeText = items[-1]
    else:
        raise _ParseFailed()

    # -1 to convert from human readable to machine numeration
    lineNumber = int(lineText.split(':')[-1]) - 1

    if scopeText:
        scopeParts = scopeText.split(':')
        scopeType = scopeParts[0]
        scopeName = scopeParts[-1].split('.')[-1]
    else:
        scopeType = None
        scopeName = None

    return name, lineNumber, type_, scopeType, scopeName

def _findScope(tag, scopeType, scopeName):
    """Check tag and its parents, if theirs name is scopeName.
    Return tag or None
    """
    if tag is None:
        return None
    elif tag.name == scopeName and \
       tag.type == scopeType:
        return tag
    elif tag.parent is not None:
        return _findScope(tag.parent, scopeType, scopeName)
    else:
        return None

def _parseTags(ctagsLang, text):
    if "Try `ctags --help' for a complete list of options." in text:
        raise FailedException("ctags from Emacs package is used. Use Exuberant Ctags")

    ignoredTypes = ['variable']

    if ctagsLang in ('C', 'C++',):
        ignoredTypes.append('member')

    tags = []
    lastTag = None
    for line in text.splitlines():
        if line.startswith('ctags:'):  # warnings from the utility
            continue

        try:
            name, lineNumber, type_, scopeType, scopeName = _parseTag(line)
        except _ParseFailed:
            print >> sys.stderr, 'navigator: failed to parse ctags output line "{}"'.format(line)
            continue

        if type_ not in ignoredTypes:
            if type_ == 'member':
                """ctags returns parent scope type 'function' for members'.
                Workaround this issue - use one term for functions and members
                """
                type_ = 'function'

            parent = _findScope(lastTag, scopeType, scopeName)

            # For C++ automaticaly create class tag.
            # TODO now class is created as top-level item. Find scope for class
            if parent is None and \
               scopeName and \
               ctagsLang == 'C++':
                parent = Tag(scopeType, scopeName, lineNumber, None)
                tags.append(parent)

            tag = Tag(type_, name, lineNumber, parent)
            if parent is not None:
                parent.children.append(tag)
            else:
                tags.append(tag)
            lastTag = tag

    return tags


# Workaround for tempfile.NamedTemporaryFile's behavior, which prevents Windows processes from accessing the file until it's deleted. Adapted from http://bugs.python.org/issue14243.
@contextmanager
def _namedTemp():
    f = tempfile.NamedTemporaryFile(delete=False)
    try:
        yield f
    finally:
        try:
            os.unlink(f.name)
        except OSError:
            pass


def _sortTagsAlphabetically(tags):
    for tag in tags:
        tag.children = _sortTagsAlphabetically(tag.children)

    return sorted(tags, key = lambda tag: tag.name)


def processText(ctagsLang, text, sortAlphabetically):
    ctagsPath = core.config()['Navigator']['CtagsPath']
    langArg = '--language-force={}'.format(ctagsLang)

    # \t is used as separator in ctags output. Avoid \t in tags text to simplify parsing
    # encode to utf8
    data = text.encode('utf8').replace('\t', '    ')


    with _namedTemp() as tempFile:
        tempFile.write(data)
        tempFile.close() # Windows compatibility

        try:
            stdout = gco.get_console_output([ctagsPath,
                                             '-f', '-', '-u', '--fields=nKs', langArg, tempFile.name])[0]
        except OSError as ex:
            raise FailedException('Failed to execute ctags console utility "{}": {}\n'\
                                        .format(ctagsPath, str(ex)) + \
                                  'Go to Settings -> Settings -> Navigator to set path to ctags')

    tags = _parseTags(ctagsLang, stdout)

    if sortAlphabetically:
        return _sortTagsAlphabetically(tags)
    else:
        return tags
