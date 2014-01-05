"""Ctags execution and output parsing functionality
"""

import os
import subprocess
import tempfile
from contextlib import contextmanager

from enki.core.core import core


class Tag:
    def __init__(self, name, lineNumber, parent):
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
    else:
        type_ = items[-3]
        lineText = items[-2]
        scopeText = items[-1]

    # -1 to convert from human readable to machine numeration
    lineNumber = int(lineText.split(':')[-1]) - 1

    scope = scopeText.split(':')[-1].split('.')[-1] if scopeText else None
    return name, lineNumber, type_, scope

def _findScope(tag, scopeName):
    """Check tag and its parents, it theirs name is scopeName.
    Return tag or None
    """
    if tag is None:
        return None
    if tag.name == scopeName:
        return tag
    elif tag.parent is not None:
        return _findScope(tag.parent, scopeName)
    else:
        return None

def _parseTags(text):
    ignoredTypes = ('variable')

    tags = []
    lastTag = None
    for line in text.splitlines():
        name, lineNumber, type_, scope = _parseTag(line)
        if type_ not in ignoredTypes:
            parent = _findScope(lastTag, scope)
            tag = Tag(name, lineNumber, parent)
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


def processText(ctagsLang, text):
    ctagsPath = core.config()['Navigator']['CtagsPath']
    langArg = '--language-force={}'.format(ctagsLang)

    # \t is used as separator in ctags output. Avoid \t in tags text to simplify parsing
    # encode to utf8
    data = text.encode('utf8').replace('\t', '    ')

    with _namedTemp() as tempFile:
        tempFile.write(data)
        tempFile.close() # Windows compatibility

        try:
            popen = subprocess.Popen(
                    [ctagsPath, '-f', '-', '-u', '--fields=nKs', langArg, tempFile.name],
                    stdout=subprocess.PIPE)
        except OSError as ex:
            return 'Failed to execute ctags console utility "{}": {}\n'\
                        .format(ctagsPath, str(ex)) + \
                   'Go to Settings -> Settings -> Navigator to set path to ctags'

        stdout, stderr = popen.communicate()

    return _parseTags(stdout)
